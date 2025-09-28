from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.generic import TemplateView, View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .forms import CampaignForm, DripCampaignArchiveForm, EmailTemplateForm
from .models import Campaign, DripCampaign, EmailTemplate


class AdminAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Require access to the Wagtail admin for the view."""

    raise_exception = True

    def test_func(self):
        user = self.request.user
        return user.is_active and user.has_perm("wagtailadmin.access_admin")


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


class NewsletterWorkspaceView(AdminAccessMixin, TemplateView):
    """Centralised workspace for newsletter management."""

    template_name = "newsletter/admin/workspace.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        templates = EmailTemplate.objects.order_by("name")
        campaigns = (
            Campaign.objects.select_related("email_template")
            .prefetch_related("lists")
            .order_by("-created_at")
        )
        drips = DripCampaign.objects.prefetch_related("steps").order_by("subscription_list__name", "name")

        context.update(
            {
                "template_form": EmailTemplateForm(prefix="template"),
                "campaign_form": CampaignForm(prefix="campaign"),
                "templates": templates,
                "campaigns": campaigns,
                "drip_campaigns": drips,
                "template_payload": [
                    {
                        "id": template.pk,
                        "name": template.name,
                        "subject_template": template.subject_template,
                        "preview_text": template.preview_text,
                        "html_body": str(template.html_body),
                        "text_body": template.text_body,
                        "archived": template.archived,
                    }
                    for template in templates
                ],
                "campaign_payload": [
                    {
                        "id": campaign.pk,
                        "name": campaign.name,
                        "email_template": campaign.email_template_id,
                        "lists": [lst.pk for lst in campaign.lists.all()],
                        "send_at": campaign.send_at.isoformat() if campaign.send_at else "",
                        "send_timezone": campaign.send_timezone,
                        "notes": campaign.notes,
                        "archived": campaign.archived,
                    }
                    for campaign in campaigns
                ],
                "drip_payload": [
                    {
                        "id": drip.pk,
                        "name": drip.name,
                        "archived": drip.archived,
                        "enabled": drip.enabled,
                        "subscription_list": drip.subscription_list.name,
                        "description": drip.description,
                        "steps": [
                            {
                                "id": step.pk,
                                "title": step.title,
                                "order": step.order,
                                "offset_days": step.offset_days,
                                "offset_weeks": step.offset_weeks,
                                "send_weekday": step.get_send_weekday_display() if step.send_weekday is not None else "",
                            }
                            for step in drip.steps.order_by("order")
                        ],
                    }
                    for drip in drips
                ],
            }
        )
        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        action = request.POST.get("action")
        if action in {"save_template", "archive_template", "restore_template"}:
            return self._handle_template(request)
        if action in {"save_campaign", "archive_campaign", "restore_campaign"}:
            return self._handle_campaign(request)
        if action in {"archive_drip", "restore_drip"}:
            return self._handle_drip(request)
        messages.error(request, _("Unknown action"))
        return redirect("newsletter_workspace")

    def _handle_template(self, request: HttpRequest) -> HttpResponse:
        template_id = request.POST.get("template_id")
        action = request.POST.get("action")
        instance = None
        if template_id:
            instance = get_object_or_404(EmailTemplate, pk=template_id)

        if action == "save_template":
            form = EmailTemplateForm(request.POST, prefix="template", instance=instance)
            if form.is_valid():
                template = form.save()
                messages.success(
                    request,
                    _("Template '{name}' saved successfully.").format(name=template.name),
                )
                return redirect("newsletter_workspace")
            return self._render_with_forms(request, template_form=form)

        if instance is None:
            messages.error(request, _("Template not found."))
            return redirect("newsletter_workspace")

        instance.archived = action == "archive_template"
        instance.save(update_fields=["archived", "updated_at"])
        if instance.archived:
            messages.info(request, _("Template archived."))
        else:
            messages.success(request, _("Template restored."))
        return redirect("newsletter_workspace")

    def _handle_campaign(self, request: HttpRequest) -> HttpResponse:
        campaign_id = request.POST.get("campaign_id")
        action = request.POST.get("action")
        instance = None
        if campaign_id:
            instance = get_object_or_404(Campaign, pk=campaign_id)

        if action == "save_campaign":
            form = CampaignForm(request.POST, prefix="campaign", instance=instance)
            if form.is_valid():
                campaign = form.save()
                auto_schedule = form.cleaned_data.get("auto_schedule")
                if auto_schedule:
                    try:
                        campaign.schedule()
                        messages.success(
                            request,
                            _("Campaign '{name}' scheduled successfully.").format(name=campaign.name),
                        )
                    except Exception as exc:
                        messages.warning(
                            request,
                            _("Campaign saved but scheduling failed: {error}").format(error=str(exc)),
                        )
                else:
                    # When not auto-scheduling, only set status to SCHEDULED if we actually schedule the task
                    # Otherwise, keep the existing status or set to DRAFT for new campaigns
                    if campaign.send_at and campaign.send_at > timezone.now():
                        # Only set to SCHEDULED if we're actually scheduling the task
                        # Since auto_schedule is False, we don't schedule, so keep as DRAFT
                        if campaign.status == Campaign.Status.DRAFT:
                            # Only update if it's a new campaign (DRAFT status)
                            campaign.save(update_fields=["updated_at"])
                    else:
                        # For campaigns without future send_at, only set to DRAFT if it's a new campaign
                        if campaign.status == Campaign.Status.DRAFT:
                            campaign.save(update_fields=["updated_at"])
                    
                    messages.success(
                        request,
                        _("Campaign '{name}' saved.").format(name=campaign.name),
                    )
                return redirect("newsletter_workspace")
            return self._render_with_forms(request, campaign_form=form)

        if instance is None:
            messages.error(request, _("Campaign not found."))
            return redirect("newsletter_workspace")

        instance.archived = action == "archive_campaign"
        instance.save(update_fields=["archived", "updated_at"])
        if instance.archived:
            messages.info(request, _("Campaign archived."))
        else:
            messages.success(request, _("Campaign restored."))
        return redirect("newsletter_workspace")

    def _handle_drip(self, request: HttpRequest) -> HttpResponse:
        drip_id = request.POST.get("drip_id")
        instance = get_object_or_404(DripCampaign, pk=drip_id)
        form = DripCampaignArchiveForm(request.POST, instance=instance)
        if form.is_valid():
            drip = form.save()
            if drip.archived:
                messages.info(request, _("Drip campaign archived."))
            else:
                messages.success(request, _("Drip campaign restored."))
        else:
            messages.error(request, _("Unable to update drip campaign."))
        return redirect("newsletter_workspace")

    def _render_with_forms(self, request: HttpRequest, **forms) -> HttpResponse:
        context = self.get_context_data()
        context.update(forms)
        return self.render_to_response(context)
