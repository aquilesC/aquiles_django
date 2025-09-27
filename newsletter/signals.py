from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Campaign, DripSequenceProgress
from .tasks import process_drip_queue


@receiver(post_save, sender=Campaign)
def schedule_campaign_send(sender, instance: Campaign, created: bool, **kwargs):
    if kwargs.get("raw"):
        return
    if instance.status in {Campaign.Status.SCHEDULED, Campaign.Status.SENDING} and not instance.scheduled_task_id:
        instance.schedule()


@receiver(post_save, sender=DripSequenceProgress)
def enqueue_due_drip(sender, instance: DripSequenceProgress, created: bool, **kwargs):
    if kwargs.get("raw") or instance.completed:
        return
    if instance.next_send_at and instance.next_send_at <= timezone.now():
        process_drip_queue.delay()
