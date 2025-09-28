from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from types import SimpleNamespace
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.generic import FormView, TemplateView

from .forms import CampaignForm, EmailTemplateForm, SubscriptionForm, UnsubscribeForm
from .models import (
    Campaign,
    DripCampaign,
    EmailMessageLog,
    EmailTemplate,
    Subscriber,
    Subscription,
    SubscriptionList,
)
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


class NewsletterAdminMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Common behaviour for the standalone newsletter admin interface."""

    section: str = ""
    page_title: str = "Newsletter admin"

    def test_func(self):
        user = self.request.user
        return user.is_active and user.is_staff

    def get_page_title(self) -> str:
        return self.page_title

    def get_admin_navigation(self) -> list[dict[str, str]]:
        return [
            {"slug": "dashboard", "label": "Dashboard", "url": reverse("newsletter:admin-dashboard")},
            {"slug": "campaigns", "label": "Campaigns", "url": reverse("newsletter:admin-campaigns")},
            {"slug": "subscribers", "label": "Subscribers", "url": reverse("newsletter:admin-subscribers")},
            {"slug": "drips", "label": "Drip campaigns", "url": reverse("newsletter:admin-drips")},
            {"slug": "editor", "label": "Newsletter editor", "url": reverse("newsletter:admin-editor")},
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.get_page_title()
        context["admin_nav"] = self.get_admin_navigation()
        context["active_section"] = self.section
        return context


class NewsletterDashboardView(NewsletterAdminMixin, TemplateView):
    template_name = "newsletter/admin/dashboard.html"
    section = "dashboard"
    page_title = "Newsletter overview"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        lists = SubscriptionList.objects.order_by("name")
        total_subscriptions = Subscription.objects.select_related("subscription_list").count()
        active_subscriptions = Subscription.objects.filter(status=Subscription.Status.ACTIVE).count()
        pending_subscriptions = Subscription.objects.filter(status=Subscription.Status.PENDING).count()
        status_breakdown = {
            item["status"]: item["total"]
            for item in Subscription.objects.values("status").annotate(total=Count("id"))
        }

        campaigns = Campaign.objects.filter(archived=False)
        total_campaigns = campaigns.count()
        recent_campaigns = campaigns.select_related("email_template").prefetch_related("lists").order_by("-created_at")[:5]
        upcoming_campaigns = campaigns.filter(status=Campaign.Status.SCHEDULED).order_by("send_at")[:5]

        email_totals = {
            "sent": EmailMessageLog.objects.filter(status=EmailMessageLog.Status.SENT).count(),
            "delivered": EmailMessageLog.objects.filter(status=EmailMessageLog.Status.DELIVERED).count(),
            "opened": EmailMessageLog.objects.filter(status=EmailMessageLog.Status.OPENED).count(),
            "clicked": EmailMessageLog.objects.filter(status=EmailMessageLog.Status.CLICKED).count(),
            "bounced": EmailMessageLog.objects.filter(status=EmailMessageLog.Status.BOUNCED).count(),
        }

        total_emails_sent = email_totals["sent"] or 1
        delivery_rate = round((email_totals["delivered"] / total_emails_sent) * 100, 2)
        open_rate = round((email_totals["opened"] / total_emails_sent) * 100, 2)
        click_rate = round((email_totals["clicked"] / total_emails_sent) * 100, 2)
        bounce_rate = round((email_totals["bounced"] / total_emails_sent) * 100, 2)

        recent_emails = (
            EmailMessageLog.objects.select_related("subscriber", "campaign", "drip_step")
            .order_by("-sent_at")[:10]
        )

        drips = (
            DripCampaign.objects.filter(archived=False)
            .select_related("subscription_list")
            .prefetch_related("steps")
        )

        thirty_days_ago = timezone.now() - timedelta(days=30)
        new_subscriptions_30d = Subscription.objects.filter(created_at__gte=thirty_days_ago).count()
        active_subscriptions_30d = Subscription.objects.filter(
            status=Subscription.Status.ACTIVE,
            created_at__gte=thirty_days_ago,
        ).count()

        context.update(
            {
                "lists": lists,
                "total_subscriptions": total_subscriptions,
                "active_subscriptions": active_subscriptions,
                "pending_subscriptions": pending_subscriptions,
                "status_breakdown": status_breakdown,
                "campaigns_total": total_campaigns,
                "recent_campaigns": recent_campaigns,
                "upcoming_campaigns": upcoming_campaigns,
                "recent_emails": recent_emails,
                "drips": drips,
                "new_subscriptions_30d": new_subscriptions_30d,
                "active_subscriptions_30d": active_subscriptions_30d,
                "performance_chart": {
                    "labels": ["Delivered", "Opened", "Clicked", "Bounced"],
                    "values": [
                        email_totals["delivered"],
                        email_totals["opened"],
                        email_totals["clicked"],
                        email_totals["bounced"],
                    ],
                },
                "delivery_rate": delivery_rate,
                "open_rate": open_rate,
                "click_rate": click_rate,
                "bounce_rate": bounce_rate,
                "total_emails_sent": email_totals["sent"],
            }
        )
        return context


class CampaignListView(NewsletterAdminMixin, TemplateView):
    template_name = "newsletter/admin/campaigns.html"
    section = "campaigns"
    page_title = "Campaigns"

    def get_current_campaign(self):
        campaign_id = self.request.POST.get("campaign_id") or self.request.GET.get("campaign")
        if campaign_id:
            return get_object_or_404(Campaign, pk=campaign_id)
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_campaign = kwargs.get("current_campaign") or self.get_current_campaign()
        form = kwargs.get("form") or CampaignForm(instance=current_campaign)

        campaigns = (
            Campaign.objects.select_related("email_template")
            .prefetch_related("lists")
            .order_by("-created_at")
        )
        paginator = Paginator(campaigns, 12)
        page_obj = paginator.get_page(self.request.GET.get("page"))

        status_counts = {
            item["status"]: item["total"]
            for item in campaigns.values("status").annotate(total=Count("id"))
        }
        status_summary = [
            {"value": value, "label": label, "count": status_counts.get(value, 0)}
            for value, label in Campaign.Status.choices
        ]

        context.update(
            {
                "campaign_form": form,
                "campaigns_page": page_obj,
                "current_campaign": current_campaign,
                "templates": EmailTemplate.objects.order_by("name"),
                "status_counts": status_counts,
                "status_choices": Campaign.Status.choices,
                "status_summary": status_summary,
            }
        )
        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        campaign = self.get_current_campaign()
        action = request.POST.get("action", "save")

        if action in {"archive", "restore"} and campaign:
            campaign.archived = action == "archive"
            campaign.save(update_fields=["archived", "updated_at"])
            message = _("Campaign archived.") if campaign.archived else _("Campaign restored.")
            messages.success(request, message)
            return redirect(reverse("newsletter:admin-campaigns"))

        form = CampaignForm(request.POST, instance=campaign)
        if form.is_valid():
            saved_campaign = form.save()
            messages.success(
                request,
                _("Campaign '{name}' saved successfully.").format(name=saved_campaign.name),
            )
            return redirect(f"{reverse('newsletter:admin-campaigns')}?campaign={saved_campaign.pk}")

        context = self.get_context_data(form=form, current_campaign=campaign)
        return self.render_to_response(context)


class SubscriberListView(NewsletterAdminMixin, TemplateView):
    template_name = "newsletter/admin/subscribers.html"
    section = "subscribers"
    page_title = "Subscribers"
    paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        query = self.request.GET.get("q", "").strip()
        status_filter = self.request.GET.get("status", "")
        list_filter = self.request.GET.get("list", "")

        subscribers = Subscriber.objects.all().order_by("-created_at")
        if query:
            subscribers = subscribers.filter(
                Q(email__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
            )
        if status_filter:
            subscribers = subscribers.filter(subscriptions__status=status_filter)
        if list_filter:
            subscribers = subscribers.filter(subscriptions__subscription_list_id=list_filter)

        subscribers = subscribers.prefetch_related("subscriptions__subscription_list").distinct()
        paginator = Paginator(subscribers, self.paginate_by)
        page_obj = paginator.get_page(self.request.GET.get("page"))

        status_counts = {
            item["status"]: item["total"]
            for item in Subscription.objects.values("status").annotate(total=Count("id"))
        }
        status_summary = [
            {"value": value, "label": label, "count": status_counts.get(value, 0)}
            for value, label in Subscription.Status.choices
        ]

        context.update(
            {
                "subscribers_page": page_obj,
                "query": query,
                "status_filter": status_filter,
                "list_filter": list_filter,
                "list_filter_value": str(list_filter or ""),
                "status_counts": status_counts,
                "status_choices": Subscription.Status.choices,
                "status_summary": status_summary,
                "subscription_lists": SubscriptionList.objects.order_by("name"),
            }
        )
        return context


class DripCampaignListView(NewsletterAdminMixin, TemplateView):
    template_name = "newsletter/admin/drips.html"
    section = "drips"
    page_title = "Drip campaigns"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        drips = (
            DripCampaign.objects.select_related("subscription_list")
            .prefetch_related("steps")
            .order_by("subscription_list__name", "name")
        )

        context.update(
            {
                "drips": drips,
                "active_drip_count": drips.filter(enabled=True, archived=False).count(),
                "archived_drip_count": drips.filter(archived=True).count(),
            }
        )
        return context


class TemplateEditorView(NewsletterAdminMixin, TemplateView):
    template_name = "newsletter/admin/editor.html"
    section = "editor"
    page_title = "Newsletter editor"

    def get_current_template(self):
        template_id = self.request.POST.get("template_id") or self.request.GET.get("template")
        if template_id:
            return get_object_or_404(EmailTemplate, pk=template_id)
        return None

    def get_preview_context(self):
        subscriber = SimpleNamespace(
            first_name="Jamie",
            last_name="Rivera",
            email="jamie@example.com",
            full_name="Jamie Rivera",
        )
        subscription_list = SimpleNamespace(name="Sample List")

        class DummySubscription:
            def __init__(self, sub, lst):
                self.subscriber = sub
                self.subscription_list = lst

            def build_unsubscribe_url(self):
                return "#"

        subscription = DummySubscription(subscriber, subscription_list)
        return {
            "subscriber": subscriber,
            "subscription": subscription,
            "list": subscription_list,
            "unsubscribe_url": "#",
            "campaign": SimpleNamespace(name="Sample Campaign"),
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_template = kwargs.get("current_template") or self.get_current_template()
        form = kwargs.get("form") or EmailTemplateForm(instance=current_template)

        plain_text_preview = ""
        plain_text_error = ""
        if current_template:
            try:
                plain_text_preview = current_template.render_plain_text(self.get_preview_context())
            except Exception as exc:  # pragma: no cover - render errors reported to UI
                plain_text_error = str(exc)

        context.update(
            {
                "template_form": form,
                "templates": EmailTemplate.objects.order_by("name"),
                "current_template": current_template,
                "plain_text_preview": plain_text_preview,
                "plain_text_error": plain_text_error,
            }
        )
        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        current_template = self.get_current_template()
        form = EmailTemplateForm(request.POST, instance=current_template)

        if form.is_valid():
            saved_template = form.save()
            messages.success(
                request,
                _("Template '{name}' saved successfully.").format(name=saved_template.name),
            )
            return redirect(f"{reverse('newsletter:admin-editor')}?template={saved_template.pk}")

        context = self.get_context_data(form=form, current_template=current_template)
        return self.render_to_response(context)
