from __future__ import annotations

from celery import shared_task
from django.utils import timezone

from .models import Campaign, DripSequenceProgress, Subscription
from .services import (
    get_active_subscriptions_for_campaign,
    send_confirmation_email,
    send_drip_step_email,
    send_subscription_email,
    send_welcome,
)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=60, retry_kwargs={"max_retries": 3})
def send_campaign(self, campaign_id: int) -> int:
    campaign = Campaign.objects.select_related("email_template").prefetch_related("lists").get(pk=campaign_id)
    campaign.status = Campaign.Status.SENDING
    campaign.save(update_fields=["status", "updated_at"])
    subscriptions = get_active_subscriptions_for_campaign(campaign)
    sent_count = 0
    seen = set()
    for subscription in subscriptions:
        if subscription.subscriber_id in seen:
            continue
        seen.add(subscription.subscriber_id)
        send_subscription_email(subscription, campaign.email_template, campaign=campaign)
        sent_count += 1
    campaign.status = Campaign.Status.SENT
    campaign.sent_at = timezone.now()
    campaign.save(update_fields=["status", "sent_at", "updated_at"])
    return sent_count


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=30, retry_kwargs={"max_retries": 5})
def send_welcome_email(self, subscription_id: int) -> None:
    send_welcome(subscription_id)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=30, retry_kwargs={"max_retries": 5})
def send_drip_email(self, progress_id: int) -> None:
    send_drip_step_email(progress_id)


@shared_task
def process_drip_queue() -> int:
    now = timezone.now()
    progress_ids = list(
        DripSequenceProgress.objects.filter(completed=False, next_send_at__lte=now)
        .values_list("id", flat=True)
    )
    for progress_id in progress_ids:
        send_drip_email.delay(progress_id)
    return len(progress_ids)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=60, retry_kwargs={"max_retries": 3})
def send_confirmation(self, subscription_id: int) -> None:
    subscription = Subscription.objects.select_related("subscriber", "subscription_list").get(pk=subscription_id)
    send_confirmation_email(subscription)
