from __future__ import annotations

from anymail.webhooks.mailgun import MailgunTrackingWebhookView as BaseMailgunWebhook
from django.http import HttpResponse
from django.utils import timezone

from .models import EmailEvent, EmailMessageLog, Subscription


class MailgunTrackingWebhookView(BaseMailgunWebhook):
    def handle_tracking_event(self, event):
        metadata = event.metadata or {}
        log = None
        log_id = metadata.get("log_id")
        if log_id:
            try:
                log = EmailMessageLog.objects.select_related("subscription").get(pk=log_id)
            except EmailMessageLog.DoesNotExist:
                log = None
        if log is None and event.message_id:
            log = EmailMessageLog.objects.filter(message_id=event.message_id).select_related("subscription").first()
        if log is None:
            return HttpResponse(status=200)
        timestamp = event.timestamp or timezone.now()
        event_type = event.event_type
        EmailEvent.objects.create(
            log=log,
            event_type=event_type,
            recipient=event.recipient,
            occurred_at=timestamp,
            payload=event.payload,
        )
        updates = {"updated_at": timezone.now()}
        if event_type == "delivered":
            updates.update({"status": EmailMessageLog.Status.DELIVERED, "delivered_at": timestamp})
        elif event_type == "opened":
            updates.update({"status": EmailMessageLog.Status.OPENED, "opened_at": timestamp})
        elif event_type == "clicked":
            updates.update({"status": EmailMessageLog.Status.CLICKED, "clicked_at": timestamp})
        elif event_type in {"bounced", "failed"}:
            updates.update({"status": EmailMessageLog.Status.BOUNCED, "bounced_at": timestamp})
            subscription = log.subscription
            subscription.status = Subscription.Status.BOUNCED
            subscription.save(update_fields=["status", "updated_at"])
        elif event_type in {"complained", "unsubscribed"}:
            updates.update({"status": EmailMessageLog.Status.BOUNCED})
            subscription = log.subscription
            subscription.status = Subscription.Status.COMPLAINED if event_type == "complained" else Subscription.Status.UNSUBSCRIBED
            subscription.unsubscribed_at = timestamp if event_type == "unsubscribed" else subscription.unsubscribed_at
            subscription.save(update_fields=["status", "unsubscribed_at", "updated_at"])
        if len(updates) > 1:
            for field, value in updates.items():
                setattr(log, field, value)
            log.save(update_fields=list(updates.keys()))
        return HttpResponse(status=200)
