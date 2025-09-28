from __future__ import annotations

from django.urls import path

from . import views
from .webhooks import MailgunTrackingWebhookView

app_name = "newsletter"

urlpatterns = [
    path("admin/", views.NewsletterDashboardView.as_view(), name="admin-dashboard"),
    path("admin/campaigns/", views.CampaignListView.as_view(), name="admin-campaigns"),
    path("admin/subscribers/", views.SubscriberListView.as_view(), name="admin-subscribers"),
    path("admin/drip-campaigns/", views.DripCampaignListView.as_view(), name="admin-drips"),
    path("admin/editor/", views.TemplateEditorView.as_view(), name="admin-editor"),
    path("subscribe/", views.SubscribeView.as_view(), name="subscribe"),
    path("confirm/<uuid:token>/", views.confirm_subscription, name="confirm"),
    path("unsubscribe/<uuid:token>/", views.unsubscribe, name="unsubscribe"),
    path("webhooks/mailgun/", MailgunTrackingWebhookView.as_view(), name="mailgun-webhook"),
]
