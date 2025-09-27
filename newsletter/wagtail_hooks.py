from __future__ import annotations

from django.urls import path, reverse
from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.admin.viewsets.model import ModelViewSet

from .models import (
    Campaign,
    DripCampaign,
    DripStep,
    EmailTemplate,
    Subscriber,
    Subscription,
    SubscriptionList,
)
from .views import NewsletterDashboardView


class SubscriptionListViewSet(ModelViewSet):
    model = SubscriptionList
    menu_label = "Lists"
    menu_icon = "mail"
    menu_order = 200
    list_display = ("name", "slug", "double_opt_in", "is_public")
    search_fields = ("name", "slug")


class EmailTemplateViewSet(ModelViewSet):
    model = EmailTemplate
    menu_label = "Templates"
    menu_icon = "doc-full"
    menu_order = 210
    list_display = ("name", "subject_template", "updated_at")
    search_fields = ("name", "subject_template")


class SubscriberViewSet(ModelViewSet):
    model = Subscriber
    menu_label = "Subscribers"
    menu_icon = "user"
    menu_order = 220
    list_display = ("email", "first_name", "last_name", "created_at")
    search_fields = ("email", "first_name", "last_name")


class SubscriptionViewSet(ModelViewSet):
    model = Subscription
    menu_label = "Subscriptions"
    menu_icon = "pick"
    menu_order = 230
    list_display = ("subscriber", "subscription_list", "status", "confirmed_at")
    list_filter = ("status", "subscription_list")
    search_fields = ("subscriber__email",)


class CampaignViewSet(ModelViewSet):
    model = Campaign
    menu_label = "Campaigns"
    menu_icon = "mail"
    menu_order = 240
    list_display = ("name", "status", "send_at", "sent_at")
    list_filter = ("status",)
    search_fields = ("name",)


class DripCampaignViewSet(ModelViewSet):
    model = DripCampaign
    menu_label = "Drip campaigns"
    menu_icon = "repeat"
    menu_order = 250
    list_display = ("name", "subscription_list", "enabled")
    list_filter = ("enabled", "subscription_list")
    search_fields = ("name",)


class DripStepViewSet(ModelViewSet):
    model = DripStep
    menu_label = "Drip steps"
    menu_icon = "arrow-right"
    menu_order = 260
    list_display = ("drip_campaign", "order", "title", "offset_days", "offset_weeks", "send_weekday")
    list_filter = ("drip_campaign",)
    search_fields = ("title",)


subscription_list_viewset = SubscriptionListViewSet("newsletter_subscription_list")
email_template_viewset = EmailTemplateViewSet("newsletter_email_template")
subscriber_viewset = SubscriberViewSet("newsletter_subscriber")
subscription_viewset = SubscriptionViewSet("newsletter_subscription")
campaign_viewset = CampaignViewSet("newsletter_campaign")
drip_campaign_viewset = DripCampaignViewSet("newsletter_drip_campaign")
drip_step_viewset = DripStepViewSet("newsletter_drip_step")


@hooks.register("register_admin_viewset")
def register_subscription_list_viewset():
    return subscription_list_viewset


@hooks.register("register_admin_viewset")
def register_email_template_viewset():
    return email_template_viewset


@hooks.register("register_admin_viewset")
def register_subscriber_viewset():
    return subscriber_viewset


@hooks.register("register_admin_viewset")
def register_subscription_viewset():
    return subscription_viewset


@hooks.register("register_admin_viewset")
def register_campaign_viewset():
    return campaign_viewset


@hooks.register("register_admin_viewset")
def register_drip_campaign_viewset():
    return drip_campaign_viewset


@hooks.register("register_admin_viewset")
def register_drip_step_viewset():
    return drip_step_viewset


@hooks.register("register_admin_urls")
def register_newsletter_admin_urls():
    return [
        path("newsletter/dashboard/", NewsletterDashboardView.as_view(), name="newsletter_dashboard"),
    ]


@hooks.register("register_admin_menu_item")
def register_newsletter_menu_item():
    return MenuItem("Newsletter stats", reverse("newsletter_dashboard"), icon_name="bar-chart", order=270)
