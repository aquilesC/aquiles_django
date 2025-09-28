from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.generic import FormView, TemplateView

from .forms import SubscriptionForm, UnsubscribeForm
from .models import Subscriber, Subscription, SubscriptionList
from .tasks import process_drip_queue, send_confirmation


class SubscribeView(FormView):
    template_name = "newsletter/public/subscribe_form.html"
    form_class = SubscriptionForm

    def _boolean(self, key: str, default: bool = False) -> bool:
        value = self.request.POST.get(key)
        if value is None:
            value = self.request.GET.get(key)
        if value is None:
            return default
        return value in {"1", "true", "True", "yes", "on"}

    def get_initial(self):
        initial = super().get_initial()
        initial.setdefault("next", self.request.get_full_path())
        initial.setdefault("source", "newsletter-page")
        return initial

    def get_available_lists(self):
        list_ids = self.request.POST.getlist("lists") or self.request.GET.getlist("list")
        if list_ids:
            return SubscriptionList.objects.filter(pk__in=list_ids)
        return SubscriptionList.objects.filter(is_public=True)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        available = list(self.get_available_lists())
        kwargs["available_lists"] = available
        kwargs["allow_multiple"] = self._boolean("allow_multiple", default=len(available) > 1)
        kwargs["show_name_fields"] = self._boolean("show_name", default=True)
        return kwargs

    def form_valid(self, form: SubscriptionForm):
        data = form.cleaned_data
        subscriber, created = Subscriber.objects.get_or_create(email=data["email"], defaults={
            "first_name": data.get("first_name", ""),
            "last_name": data.get("last_name", ""),
        })
        if not created:
            updated = False
            if data.get("first_name") and data["first_name"] != subscriber.first_name:
                subscriber.first_name = data["first_name"]
                updated = True
            if data.get("last_name") and data["last_name"] != subscriber.last_name:
                subscriber.last_name = data["last_name"]
                updated = True
            if updated:
                subscriber.save(update_fields=["first_name", "last_name", "updated_at"])
        confirmations_sent = []
        activations = []
        for subscription_list in data["lists"]:
            subscription, _ = Subscription.objects.get_or_create(
                subscriber=subscriber,
                subscription_list=subscription_list,
                defaults={
                    "opt_in_source": data.get("source", "form"),
                    "referrer": self.request.META.get("HTTP_REFERER", ""),
                    "extra_data": {"user_agent": self.request.META.get("HTTP_USER_AGENT", "")},
                },
            )
            if subscription.status == Subscription.Status.UNSUBSCRIBED:
                subscription.unsubscribed_at = None
            if subscription.status == Subscription.Status.BOUNCED:
                subscription.status = Subscription.Status.PENDING
            if subscription.status == Subscription.Status.ACTIVE:
                activations.append(subscription_list)
                continue
            if subscription_list.double_opt_in:
                subscription.mark_pending()
                send_confirmation.delay(subscription.pk)
                confirmations_sent.append(subscription_list)
            else:
                subscription.mark_active(request=self.request)
                activations.append(subscription_list)
        if confirmations_sent:
            lists_string = ", ".join(lst.name for lst in confirmations_sent)
            messages.success(
                self.request,
                _("Almost there! Please confirm your subscription to {lists}.").format(lists=lists_string),
            )
        if activations:
            lists_string = ", ".join(lst.name for lst in activations)
            custom_success = data.get("success_message")
            if custom_success:
                messages.success(self.request, custom_success)
            else:
                messages.success(
                    self.request,
                    _("You're now subscribed to {lists}.").format(lists=lists_string),
                )
        next_url = data.get("next") or self.request.META.get("HTTP_REFERER") or reverse("core:home")
        process_drip_queue.delay()
        return redirect(next_url)

    def form_invalid(self, form):
        next_url = form.data.get("next") or self.request.META.get("HTTP_REFERER") or reverse("core:home")
        if next_url == self.request.path:
            return self.render_to_response(self.get_context_data(form=form))
        messages.error(self.request, _("Please check the form and try again."))
        return redirect(next_url)


def confirm_subscription(request: HttpRequest, token: str) -> HttpResponse:
    subscription = get_object_or_404(Subscription, confirmation_token=token)
    expiry_days = getattr(settings, "NEWSLETTER_CONFIRMATION_EXPIRY_DAYS", 7)
    expired = False
    if subscription.confirmation_sent_at and subscription.confirmation_sent_at + timedelta(days=expiry_days) < timezone.now():
        expired = True
    context = {"subscription": subscription, "expired": expired}
    if not expired:
        subscription.mark_active(request=request)
        messages.success(
            request,
            _("Thanks! You're confirmed for {list_name}.").format(list_name=subscription.subscription_list.name),
        )
    else:
        messages.error(
            request,
            _("The confirmation link has expired. Please submit the form again to receive a new email."),
        )
    return render(request, "newsletter/public/confirm.html", context)


def unsubscribe(request: HttpRequest, token: str) -> HttpResponse:
    subscription = get_object_or_404(Subscription, unsubscribe_token=token)
    if request.method == "POST":
        form = UnsubscribeForm(request.POST)
        if form.is_valid():
            subscription.mark_unsubscribed()
            if form.cleaned_data.get("reason"):
                subscription.extra_data.update({"unsubscribe_reason": form.cleaned_data["reason"]})
                subscription.save(update_fields=["extra_data", "updated_at"])
            messages.success(
                request,
                _("You've been unsubscribed from {list_name}.").format(list_name=subscription.subscription_list.name),
            )
            return render(request, "newsletter/public/unsubscribe_success.html", {"subscription": subscription})
    else:
        form = UnsubscribeForm(initial={"confirm": False})
    return render(request, "newsletter/public/unsubscribe.html", {"subscription": subscription, "form": form})


class NewsletterDashboardView(TemplateView):
    template_name = "newsletter/admin/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Basic counts
        context["lists"] = SubscriptionList.objects.all()
        context["subscriptions"] = Subscription.objects.select_related("subscription_list").count()
        context["active_subscriptions"] = Subscription.objects.filter(status=Subscription.Status.ACTIVE).count()
        context["pending_subscriptions"] = Subscription.objects.filter(status=Subscription.Status.PENDING).count()
        
        # Import Campaign and EmailMessageLog for analytics
        from .models import Campaign, EmailMessageLog, EmailEvent
        
        # Campaign analytics
        context["total_campaigns"] = Campaign.objects.count()
        context["draft_campaigns"] = Campaign.objects.filter(status=Campaign.Status.DRAFT).count()
        context["scheduled_campaigns"] = Campaign.objects.filter(status=Campaign.Status.SCHEDULED).count()
        context["recent_campaigns"] = Campaign.objects.order_by('-created_at')[:5]
        
        # Email performance analytics
        context["total_emails_sent"] = EmailMessageLog.objects.filter(status=EmailMessageLog.Status.SENT).count()
        context["emails_delivered"] = EmailMessageLog.objects.filter(status=EmailMessageLog.Status.DELIVERED).count()
        context["emails_opened"] = EmailMessageLog.objects.filter(status=EmailMessageLog.Status.OPENED).count()
        context["emails_clicked"] = EmailMessageLog.objects.filter(status=EmailMessageLog.Status.CLICKED).count()
        context["emails_bounced"] = EmailMessageLog.objects.filter(status=EmailMessageLog.Status.BOUNCED).count()
        
        # Calculate rates
        if context["total_emails_sent"] > 0:
            context["delivery_rate"] = round((context["emails_delivered"] / context["total_emails_sent"]) * 100, 2)
            context["open_rate"] = round((context["emails_opened"] / context["total_emails_sent"]) * 100, 2)
            context["click_rate"] = round((context["emails_clicked"] / context["total_emails_sent"]) * 100, 2)
            context["bounce_rate"] = round((context["emails_bounced"] / context["total_emails_sent"]) * 100, 2)
        else:
            context["delivery_rate"] = 0
            context["open_rate"] = 0
            context["click_rate"] = 0
            context["bounce_rate"] = 0
        
        # Recent activity
        context["recent_emails"] = EmailMessageLog.objects.select_related(
            'subscriber', 'campaign', 'drip_step'
        ).order_by('-sent_at')[:10]
        
        # Subscription growth (last 30 days)
        from datetime import timedelta
        thirty_days_ago = timezone.now() - timedelta(days=30)
        context["new_subscriptions_30d"] = Subscription.objects.filter(
            created_at__gte=thirty_days_ago
        ).count()
        context["active_subscriptions_30d"] = Subscription.objects.filter(
            status=Subscription.Status.ACTIVE,
            created_at__gte=thirty_days_ago
        ).count()
        
        return context
