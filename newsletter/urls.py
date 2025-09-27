from __future__ import annotations

from django.urls import path

from . import views
from .webhooks import MailgunTrackingWebhookView

app_name = "newsletter"

urlpatterns = [
    path("subscribe/", views.SubscribeView.as_view(), name="subscribe"),
    path("confirm/<uuid:token>/", views.confirm_subscription, name="confirm"),
    path("unsubscribe/<uuid:token>/", views.unsubscribe, name="unsubscribe"),
    path("webhooks/mailgun/", MailgunTrackingWebhookView.as_view(), name="mailgun-webhook"),
]
