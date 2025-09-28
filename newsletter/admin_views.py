from __future__ import annotations

from django.contrib import messages
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import Campaign


class CampaignActionView(View):
    """Handle campaign actions like send, cancel, duplicate."""
    
    def post(self, request: HttpRequest, campaign_id: int, action: str) -> HttpResponse:
        campaign = get_object_or_404(Campaign, pk=campaign_id)
        
        if action == "send":
            return self._send_campaign(request, campaign)
        elif action == "cancel":
            return self._cancel_campaign(request, campaign)
        elif action == "duplicate":
            return self._duplicate_campaign(request, campaign)
        elif action == "preview":
            return self._preview_campaign(request, campaign)
        else:
            messages.error(request, _("Invalid action."))
            return redirect("wagtailadmin_pages:edit", campaign.pk)
    
    def _send_campaign(self, request: HttpRequest, campaign: Campaign) -> HttpResponse:
        """Send or schedule a campaign."""
        if campaign.status == Campaign.Status.SENT:
            messages.warning(request, _("Campaign has already been sent."))
            return redirect("wagtailadmin_pages:edit", campaign.pk)
        
        if campaign.status == Campaign.Status.SENDING:
            messages.warning(request, _("Campaign is currently being sent."))
            return redirect("wagtailadmin_pages:edit", campaign.pk)
        
        if not campaign.email_template:
            messages.error(request, _("Campaign must have an email template."))
            return redirect("wagtailadmin_pages:edit", campaign.pk)
        
        if not campaign.lists.exists():
            messages.error(request, _("Campaign must have at least one subscription list."))
            return redirect("wagtailadmin_pages:edit", campaign.pk)
        
        try:
            campaign.schedule()
            if campaign.send_at:
                messages.success(
                    request, 
                    _("Campaign '{name}' scheduled for {date}.").format(
                        name=campaign.name,
                        date=campaign.send_at.strftime("%Y-%m-%d %H:%M")
                    )
                )
            else:
                messages.success(
                    request, 
                    _("Campaign '{name}' is being sent now.").format(name=campaign.name)
                )
        except Exception as e:
            messages.error(request, _("Failed to send campaign: {error}").format(error=str(e)))
        
        return redirect("wagtailadmin_pages:edit", campaign.pk)
    
    def _cancel_campaign(self, request: HttpRequest, campaign: Campaign) -> HttpResponse:
        """Cancel a scheduled campaign."""
        if campaign.status not in [Campaign.Status.SCHEDULED, Campaign.Status.DRAFT]:
            messages.warning(request, _("Only scheduled or draft campaigns can be cancelled."))
            return redirect("wagtailadmin_pages:edit", campaign.pk)
        
        try:
            # Cancel the Celery task if it exists
            if campaign.scheduled_task_id:
                from celery import current_app
                current_app.control.revoke(campaign.scheduled_task_id, terminate=True)
            
            campaign.status = Campaign.Status.CANCELLED
            campaign.scheduled_task_id = ""
            campaign.save(update_fields=["status", "scheduled_task_id", "updated_at"])
            
            messages.success(request, _("Campaign '{name}' has been cancelled.").format(name=campaign.name))
        except Exception as e:
            messages.error(request, _("Failed to cancel campaign: {error}").format(error=str(e)))
        
        return redirect("wagtailadmin_pages:edit", campaign.pk)
    
    def _duplicate_campaign(self, request: HttpRequest, campaign: Campaign) -> HttpResponse:
        """Duplicate a campaign."""
        try:
            # Create a new campaign based on the existing one
            new_campaign = Campaign.objects.create(
                name=f"{campaign.name} (Copy)",
                email_template=campaign.email_template,
                status=Campaign.Status.DRAFT,
                notes=campaign.notes,
            )
            new_campaign.lists.set(campaign.lists.all())
            
            messages.success(
                request, 
                _("Campaign '{name}' has been duplicated as '{new_name}'.").format(
                    name=campaign.name,
                    new_name=new_campaign.name
                )
            )
            return redirect("wagtailadmin_pages:edit", new_campaign.pk)
        except Exception as e:
            messages.error(request, _("Failed to duplicate campaign: {error}").format(error=str(e)))
            return redirect("wagtailadmin_pages:edit", campaign.pk)
    
    def _preview_campaign(self, request: HttpRequest, campaign: Campaign) -> JsonResponse:
        """Preview campaign content."""
        if not campaign.email_template:
            return JsonResponse({"error": _("No email template selected")}, status=400)
        
        # Create a sample subscription for preview
        from .models import Subscriber, Subscription, SubscriptionList
        
        # Get or create a sample subscriber
        sample_subscriber, _ = Subscriber.objects.get_or_create(
            email="preview@example.com",
            defaults={"first_name": "John", "last_name": "Doe"}
        )
        
        # Get the first subscription list for preview context
        first_list = campaign.lists.first()
        if not first_list:
            return JsonResponse({"error": _("No subscription lists selected")}, status=400)
        
        # Create a temporary subscription for preview
        sample_subscription = Subscription(
            subscriber=sample_subscriber,
            subscription_list=first_list,
            status=Subscription.Status.ACTIVE
        )
        
        # Render the email template
        from .services import render_email_parts
        context = {
            "subscription": sample_subscription,
            "subscriber": sample_subscriber,
            "list": first_list,
            "unsubscribe_url": sample_subscription.build_unsubscribe_url(),
        }
        
        try:
            subject, html_body, text_body = render_email_parts(campaign.email_template, context)
            return JsonResponse({
                "subject": subject,
                "html_body": html_body,
                "text_body": text_body,
                "from_email": campaign.get_from_email()
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class SubscriberImportView(View):
    """Handle bulk subscriber import."""
    
    def get(self, request: HttpRequest) -> HttpResponse:
        """Show import form."""
        from .import_forms import SubscriberImportForm
        
        form = SubscriberImportForm()
        return self._render_form(request, form)
    
    def post(self, request: HttpRequest) -> HttpResponse:
        """Process CSV import."""
        from .import_forms import SubscriberImportForm, process_subscriber_import
        
        form = SubscriberImportForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                stats = process_subscriber_import(
                    csv_file=form.cleaned_data['csv_file'],
                    subscription_list=form.cleaned_data.get('subscription_list'),
                    skip_existing=form.cleaned_data['skip_existing'],
                    send_confirmation=form.cleaned_data['send_confirmation']
                )
                
                # Show success message with statistics
                success_msg = _(
                    "Import completed! "
                    "Imported: {imported}, "
                    "Skipped: {skipped}, "
                    "Errors: {errors}"
                ).format(**stats)
                messages.success(request, success_msg)
                
                # Show error details if any
                if stats['error_details']:
                    error_msg = _("Errors encountered:\n") + "\n".join(stats['error_details'][:10])
                    if len(stats['error_details']) > 10:
                        error_msg += _("\n... and {} more errors").format(len(stats['error_details']) - 10)
                    messages.warning(request, error_msg)
                
                # Redirect to subscribers list
                return redirect("wagtailadmin_pages:index")
                
            except Exception as e:
                messages.error(request, _("Import failed: {error}").format(error=str(e)))
        
        return self._render_form(request, form)
    
    def _render_form(self, request: HttpRequest, form) -> HttpResponse:
        """Render the import form."""
        from django.template.loader import render_to_string
        from django.http import HttpResponse
        
        template = """
        {% extends "wagtailadmin/base.html" %}
        {% load i18n wagtailadmin_tags %}
        
        {% block content %}
        <div class="nice-padding">
            <h1 class="wagtail-admin-title">{% trans "Import Subscribers" %}</h1>
            
            <div class="w-panel__container">
                <div class="w-panel">
                    <div class="w-panel__header">
                        <h2 class="w-panel__heading">{% trans "CSV Import" %}</h2>
                    </div>
                    <div class="w-panel__content">
                        <form method="post" enctype="multipart/form-data">
                            {% csrf_token %}
                            {{ form.as_p }}
                            <div class="submit-row">
                                <button type="submit" class="button button-primary">
                                    {% trans "Import Subscribers" %}
                                </button>
                                <a href="{% url 'wagtailadmin_pages:index' %}" class="button">
                                    {% trans "Cancel" %}
                                </a>
                            </div>
                        </form>
                        
                        <div style="margin-top: 2rem; padding: 1rem; background: #f8f9fa; border-radius: 8px;">
                            <h3>{% trans "CSV Format" %}</h3>
                            <p>{% trans "Your CSV file should have the following columns:" %}</p>
                            <ul>
                                <li><strong>email</strong> - {% trans "Required. Subscriber's email address" %}</li>
                                <li><strong>first_name</strong> - {% trans "Optional. Subscriber's first name" %}</li>
                                <li><strong>last_name</strong> - {% trans "Optional. Subscriber's last name" %}</li>
                                <li><strong>list_slug</strong> - {% trans "Optional. Slug of subscription list to add subscriber to" %}</li>
                            </ul>
                            
                            <h4>{% trans "Example CSV:" %}</h4>
                            <pre style="background: white; padding: 1rem; border: 1px solid #ddd; border-radius: 4px;">
email,first_name,last_name,list_slug
john@example.com,John,Doe,newsletter
jane@example.com,Jane,Smith,newsletter
bob@example.com,Bob,Johnson,updates
                            </pre>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        {% endblock %}
        """
        
        from django.template import Context, Template
        from django.utils.translation import gettext
        
        t = Template(template)
        c = Context({
            'form': form,
            'messages': messages.get_messages(request),
        })
        
        return HttpResponse(t.render(c))


@method_decorator(csrf_exempt, name='dispatch')
class TemplatePreviewView(View):
    """Preview email templates with sample data."""
    
    def post(self, request: HttpRequest, template_id: int) -> JsonResponse:
        """Generate a preview of the email template."""
        from .models import EmailTemplate
        
        template = get_object_or_404(EmailTemplate, pk=template_id)
        
        # Create sample context
        from .models import Subscriber, Subscription, SubscriptionList
        
        sample_subscriber, _ = Subscriber.objects.get_or_create(
            email="preview@example.com",
            defaults={"first_name": "John", "last_name": "Doe"}
        )
        
        # Get first available subscription list or create a sample one
        first_list = SubscriptionList.objects.first()
        if not first_list:
            first_list = SubscriptionList.objects.create(
                name="Sample List",
                slug="sample-list",
                description="Sample list for previews"
            )
        
        sample_subscription = Subscription(
            subscriber=sample_subscriber,
            subscription_list=first_list,
            status=Subscription.Status.ACTIVE
        )
        
        context = {
            "subscription": sample_subscription,
            "subscriber": sample_subscriber,
            "list": first_list,
            "unsubscribe_url": sample_subscription.build_unsubscribe_url(),
        }
        
        try:
            from .services import render_email_parts
            subject, html_body, text_body = render_email_parts(template, context)
            return JsonResponse({
                "subject": subject,
                "html_body": html_body,
                "text_body": text_body
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
