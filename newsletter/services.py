from __future__ import annotations

from typing import Optional

from anymail.message import AnymailMessage
from django.conf import settings
from django.template import Context, Engine
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from .models import (
    Campaign,
    DripCampaign,
    DripSequenceProgress,
    DripStep,
    EmailMessageLog,
    EmailTemplate,
    Subscription,
)

_django_engine: Optional[Engine] = None


def _get_engine() -> Engine:
    global _django_engine
    if _django_engine is None:
        _django_engine = Engine.get_default()
    return _django_engine


def render_email_parts(template: EmailTemplate, context: dict) -> tuple[str, str, str]:
    engine = _get_engine()
    subject = engine.from_string(template.subject_template).render(Context(context)).strip()
    html_body = engine.from_string(template.html_body).render(Context(context))
    if template.text_body:
        text_body = engine.from_string(template.text_body).render(Context(context))
    else:
        text_body = strip_tags(html_body)
    return subject, html_body, text_body


def send_subscription_email(
    subscription: Subscription,
    template: EmailTemplate,
    *,
    campaign: Optional[Campaign] = None,
    drip_step: Optional[DripStep] = None,
    extra_context: Optional[dict] = None,
    tags: Optional[list[str]] = None,
) -> EmailMessageLog:
    context = {
        "subscription": subscription,
        "subscriber": subscription.subscriber,
        "list": subscription.subscription_list,
        "unsubscribe_url": subscription.build_unsubscribe_url(),
    }
    if extra_context:
        context.update(extra_context)
    subject, html_body, text_body = render_email_parts(template, context)
    from_email = campaign.get_from_email() if campaign else subscription.subscription_list.get_from_email()
    log = EmailMessageLog.objects.create(
        subscription=subscription,
        subscriber=subscription.subscriber,
        campaign=campaign,
        drip_step=drip_step,
        subject=subject,
        metadata={
            "list_id": subscription.subscription_list_id,
            "subscriber_id": subscription.subscriber_id,
            "campaign_id": campaign.pk if campaign else None,
            "drip_step_id": drip_step.pk if drip_step else None,
        },
    )
    message = AnymailMessage(
        subject=subject,
        from_email=from_email,
        to=[subscription.subscriber.email],
    )
    message.body = text_body
    message.attach_alternative(html_body, "text/html")
    message.metadata = {
        "subscription_id": str(subscription.pk),
        "subscriber_id": str(subscription.subscriber_id),
        "log_id": str(log.pk),
        "campaign_id": str(campaign.pk) if campaign else "",
        "drip_step_id": str(drip_step.pk) if drip_step else "",
    }
    message.track_clicks = True
    message.track_opens = True
    if tags:
        message.tags = tags
    elif campaign:
        message.tags = [f"campaign:{campaign.pk}"]
    else:
        message.tags = [f"list:{subscription.subscription_list_id}"]
    message.send()
    status = getattr(message, "anymail_status", None)
    now = timezone.now()
    update_fields = ["status", "sent_at", "message_id", "provider_message_id", "updated_at"]
    log.status = EmailMessageLog.Status.SENT
    log.sent_at = now
    if status:
        log.message_id = status.message_id or ""
        log.provider_message_id = status.message_id or ""
    log.save(update_fields=update_fields)
    return log


def send_confirmation_email(subscription: Subscription, *, confirm_url: Optional[str] = None) -> EmailMessageLog:
    if confirm_url is None:
        confirm_url = subscription.build_confirm_url()
    context = {
        "subscription": subscription,
        "list": subscription.subscription_list,
        "confirm_url": confirm_url,
        "unsubscribe_url": subscription.build_unsubscribe_url(),
        "site_name": getattr(settings, "WAGTAIL_SITE_NAME", "Newsletter"),
    }
    html_body = render_to_string("newsletter/emails/confirmation_email.html", context)
    text_body = render_to_string("newsletter/emails/confirmation_email.txt", context)
    from_email = subscription.subscription_list.get_from_email()
    log = EmailMessageLog.objects.create(
        subscription=subscription,
        subscriber=subscription.subscriber,
        subject="Confirm your subscription",
        metadata={
            "list_id": subscription.subscription_list_id,
            "subscriber_id": subscription.subscriber_id,
            "type": "confirmation",
        },
    )
    message = AnymailMessage(
        subject=f"Confirm your subscription to {subscription.subscription_list.name}",
        from_email=from_email,
        to=[subscription.subscriber.email],
    )
    message.body = text_body
    message.attach_alternative(html_body, "text/html")
    message.metadata = {
        "subscription_id": str(subscription.pk),
        "log_id": str(log.pk),
        "type": "confirmation",
    }
    message.tags = ["double-opt-in"]
    message.track_opens = True
    message.send()
    status = getattr(message, "anymail_status", None)
    now = timezone.now()
    log.status = EmailMessageLog.Status.SENT
    log.sent_at = now
    if status:
        log.message_id = status.message_id or ""
        log.provider_message_id = status.message_id or ""
    log.save(update_fields=["status", "sent_at", "message_id", "provider_message_id", "updated_at"])
    return log


def schedule_welcome_email(subscription: Subscription):
    if not subscription.subscription_list.welcome_template:
        return
    from .tasks import send_welcome_email

    send_welcome_email.delay(subscription.pk)


def enroll_in_drip_sequences(subscription: Subscription):
    drips = DripCampaign.objects.filter(subscription_list=subscription.subscription_list, enabled=True)
    for drip in drips:
        progress, _ = DripSequenceProgress.objects.get_or_create(
            drip_campaign=drip,
            subscription=subscription,
        )
        if progress.completed:
            continue
        progress.schedule_next()


def cancel_drip_sequences(subscription: Subscription):
    DripSequenceProgress.objects.filter(subscription=subscription, completed=False).update(
        completed=True,
        next_step=None,
        next_send_at=None,
    )


def get_active_subscriptions_for_campaign(campaign: Campaign):
    return Subscription.objects.filter(
        subscription_list__in=campaign.lists.all(),
        status=Subscription.Status.ACTIVE,
    ).select_related("subscriber", "subscription_list")


def send_drip_step_email(progress_id: int):
    progress = DripSequenceProgress.objects.select_related(
        "subscription",
        "subscription__subscriber",
        "subscription__subscription_list",
        "next_step",
    ).get(pk=progress_id)
    subscription = progress.subscription
    step = progress.next_step
    if not step:
        progress.completed = True
        progress.next_send_at = None
        progress.save(update_fields=["completed", "next_send_at", "updated_at"])
        return
    send_subscription_email(subscription, step.email_template, drip_step=step, tags=["drip"])
    progress.mark_sent(step)


def send_welcome(subscription_id: int):
    subscription = Subscription.objects.select_related("subscriber", "subscription_list").get(pk=subscription_id)
    template = subscription.subscription_list.welcome_template
    if template:
        send_subscription_email(subscription, template, tags=["welcome"])
