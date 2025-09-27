from __future__ import annotations

import uuid
from datetime import date, datetime, time, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.snippets.models import register_snippet


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


@register_snippet
class EmailTemplate(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    subject_template = models.CharField(max_length=255, help_text=_("Supports Django template syntax."))
    preview_text = models.CharField(max_length=150, blank=True, help_text=_("Shown in some email clients under the subject."))
    html_body = RichTextField(
        features=["bold", "italic", "ol", "ul", "hr", "link", "h2", "h3", "h4"],
        help_text=_("Supports Django template syntax."),
    )
    text_body = models.TextField(blank=True, help_text=_("Optional plain text version. Leave blank to auto-generate."))

    panels = [
        FieldPanel("name"),
        MultiFieldPanel(
            [FieldPanel("subject_template"), FieldPanel("preview_text")],
            heading="Header",
        ),
        FieldPanel("html_body"),
        FieldPanel("text_body"),
    ]

    class Meta:
        ordering = ["name"]
        verbose_name = _("Email template")
        verbose_name_plural = _("Email templates")

    def __str__(self) -> str:
        return self.name


@register_snippet
class SubscriptionList(TimeStampedModel):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=True, help_text=_("Display in public subscription forms."))
    double_opt_in = models.BooleanField(default=True, help_text=_("Require confirmation before sending newsletters."))
    welcome_template = models.ForeignKey(
        EmailTemplate,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="welcome_lists",
        help_text=_("Optional template sent immediately after confirmation."),
    )
    default_from_name = models.CharField(max_length=150, blank=True)
    default_from_email = models.EmailField(blank=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("description"),
        FieldPanel("is_public"),
        FieldPanel("double_opt_in"),
        FieldPanel("welcome_template"),
        MultiFieldPanel(
            [FieldPanel("default_from_name"), FieldPanel("default_from_email")],
            heading="Sender overrides",
        ),
    ]

    class Meta:
        ordering = ["name"]
        verbose_name = _("Subscription list")
        verbose_name_plural = _("Subscription lists")

    def __str__(self) -> str:
        return self.name

    def get_from_email(self) -> str:
        if self.default_from_email:
            if self.default_from_name:
                return f"{self.default_from_name} <{self.default_from_email}>"
            return self.default_from_email
        return settings.DEFAULT_FROM_EMAIL


class Subscriber(TimeStampedModel):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    timezone = models.CharField(
        max_length=64,
        blank=True,
        help_text=_("Used to personalize send times for drip sequences."),
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["email"]
        verbose_name = _("Subscriber")
        verbose_name_plural = _("Subscribers")

    def __str__(self) -> str:
        return self.email

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


class Subscription(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending confirmation")
        ACTIVE = "active", _("Active")
        UNSUBSCRIBED = "unsubscribed", _("Unsubscribed")
        BOUNCED = "bounced", _("Bounced")
        COMPLAINED = "complained", _("Complaint")

    subscriber = models.ForeignKey(Subscriber, related_name="subscriptions", on_delete=models.CASCADE)
    subscription_list = models.ForeignKey(SubscriptionList, related_name="subscriptions", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    confirmation_token = models.UUIDField(default=uuid.uuid4, editable=False)
    unsubscribe_token = models.UUIDField(default=uuid.uuid4, editable=False)
    confirmation_sent_at = models.DateTimeField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    opt_in_source = models.CharField(max_length=150, blank=True)
    referrer = models.URLField(blank=True)
    extra_data = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ("subscriber", "subscription_list")
        verbose_name = _("Subscription")
        verbose_name_plural = _("Subscriptions")

    def __str__(self) -> str:
        return f"{self.subscriber.email} → {self.subscription_list.name}"

    def is_confirmed(self) -> bool:
        return self.status == self.Status.ACTIVE

    def build_confirm_url(self, request=None) -> str:
        path = reverse("newsletter:confirm", args=[str(self.confirmation_token)])
        return _absolute_url(path, request)

    def build_unsubscribe_url(self, request=None) -> str:
        path = reverse("newsletter:unsubscribe", args=[str(self.unsubscribe_token)])
        return _absolute_url(path, request)

    def mark_pending(self):
        self.status = self.Status.PENDING
        self.confirmation_token = uuid.uuid4()
        self.confirmation_sent_at = timezone.now()
        self.unsubscribed_at = None
        self.save(update_fields=["status", "confirmation_token", "confirmation_sent_at", "unsubscribed_at", "updated_at"])

    def mark_active(self, request=None):
        if self.status == self.Status.ACTIVE:
            return
        now = timezone.now()
        self.status = self.Status.ACTIVE
        self.confirmed_at = now
        self.unsubscribe_token = uuid.uuid4()
        self.unsubscribed_at = None
        self.save(update_fields=["status", "confirmed_at", "unsubscribe_token", "unsubscribed_at", "updated_at"])
        from .services import enroll_in_drip_sequences, schedule_welcome_email

        schedule_welcome_email(self)
        enroll_in_drip_sequences(self)

    def mark_unsubscribed(self):
        if self.status == self.Status.UNSUBSCRIBED:
            return
        self.status = self.Status.UNSUBSCRIBED
        self.unsubscribed_at = timezone.now()
        self.save(update_fields=["status", "unsubscribed_at", "updated_at"])
        from .services import cancel_drip_sequences

        cancel_drip_sequences(self)


class Campaign(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        SCHEDULED = "scheduled", _("Scheduled")
        SENDING = "sending", _("Sending")
        SENT = "sent", _("Sent")
        CANCELLED = "cancelled", _("Cancelled")

    name = models.CharField(max_length=255)
    email_template = models.ForeignKey(EmailTemplate, on_delete=models.PROTECT, related_name="campaigns")
    lists = models.ManyToManyField(SubscriptionList, related_name="campaigns")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    send_at = models.DateTimeField(null=True, blank=True, help_text=_("Leave blank to send immediately."))
    sent_at = models.DateTimeField(null=True, blank=True)
    send_timezone = models.CharField(
        max_length=64,
        blank=True,
        help_text=_("Optional override for scheduling timezone."),
    )
    scheduled_task_id = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("email_template"),
        FieldPanel("lists"),
        FieldPanel("status"),
        FieldPanel("send_at"),
        FieldPanel("send_timezone"),
        FieldPanel("notes"),
    ]

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Campaign")
        verbose_name_plural = _("Campaigns")

    def __str__(self) -> str:
        return self.name

    def get_from_email(self) -> str:
        custom = next(
            (
                subscription_list.get_from_email()
                for subscription_list in self.lists.all()
                if subscription_list.default_from_email
            ),
            None,
        )
        return custom or settings.DEFAULT_FROM_EMAIL

    def schedule(self):
        from .tasks import send_campaign

        if self.status == self.Status.CANCELLED:
            return
        if self.send_at:
            result = send_campaign.apply_async(args=[self.pk], eta=self.send_at)
            new_status = self.Status.SCHEDULED
        else:
            result = send_campaign.delay(self.pk)
            new_status = self.Status.SENDING
        self.scheduled_task_id = result.id
        self.status = new_status
        self.save(update_fields=["scheduled_task_id", "status", "updated_at"])


class DripCampaign(TimeStampedModel):
    class StartStrategy(models.TextChoices):
        IMMEDIATE = "immediate", _("Immediately after confirmation")
        DELAYED = "delayed", _("Start after a delay")

    name = models.CharField(max_length=255)
    subscription_list = models.ForeignKey(SubscriptionList, related_name="drip_campaigns", on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)
    start_strategy = models.CharField(max_length=20, choices=StartStrategy.choices, default=StartStrategy.IMMEDIATE)
    start_delay_days = models.PositiveIntegerField(default=0)
    send_time = models.TimeField(default=time(9, 0))
    timezone = models.CharField(max_length=64, default="UTC")
    description = models.TextField(blank=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("subscription_list"),
        FieldPanel("enabled"),
        FieldPanel("start_strategy"),
        FieldPanel("start_delay_days"),
        FieldPanel("send_time"),
        FieldPanel("timezone"),
        FieldPanel("description"),
    ]

    class Meta:
        ordering = ["subscription_list__name", "name"]
        verbose_name = _("Drip campaign")
        verbose_name_plural = _("Drip campaigns")

    def __str__(self) -> str:
        return self.name

    def get_first_step(self) -> Optional["DripStep"]:
        return self.steps.order_by("order").first()


class DripStep(TimeStampedModel):
    WEEKDAY_CHOICES = [
        (0, _("Monday")),
        (1, _("Tuesday")),
        (2, _("Wednesday")),
        (3, _("Thursday")),
        (4, _("Friday")),
        (5, _("Saturday")),
        (6, _("Sunday")),
    ]

    drip_campaign = models.ForeignKey(DripCampaign, related_name="steps", on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=1)
    title = models.CharField(max_length=255)
    email_template = models.ForeignKey(EmailTemplate, related_name="drip_steps", on_delete=models.PROTECT)
    offset_days = models.PositiveIntegerField(default=0, help_text=_("Days after start to send this step."))
    offset_weeks = models.PositiveIntegerField(default=0, help_text=_("Additional weeks after start."))
    send_weekday = models.IntegerField(
        choices=WEEKDAY_CHOICES,
        null=True,
        blank=True,
        help_text=_("Align send to this weekday after offsets."),
    )

    panels = [
        FieldPanel("drip_campaign"),
        FieldPanel("order"),
        FieldPanel("title"),
        FieldPanel("email_template"),
        FieldPanel("offset_days"),
        FieldPanel("offset_weeks"),
        FieldPanel("send_weekday"),
    ]

    class Meta:
        ordering = ["drip_campaign", "order"]
        unique_together = ("drip_campaign", "order")
        verbose_name = _("Drip step")
        verbose_name_plural = _("Drip steps")

    def __str__(self) -> str:
        return f"{self.drip_campaign.name}: {self.title}"

    def compute_send_datetime(self, base: datetime) -> datetime:
        scheduled_date = base.date() + timedelta(days=self.offset_days) + timedelta(weeks=self.offset_weeks)
        if self.send_weekday is not None:
            scheduled_date = _next_weekday(scheduled_date, self.send_weekday)
        send_time = self.drip_campaign.send_time or time(9, 0)
        try:
            tz = ZoneInfo(self.drip_campaign.timezone or "UTC")
        except Exception:
            tz = ZoneInfo("UTC")
        send_dt = datetime.combine(scheduled_date, send_time, tzinfo=tz)
        return send_dt.astimezone(timezone.utc)


class DripSequenceProgress(TimeStampedModel):
    drip_campaign = models.ForeignKey(DripCampaign, related_name="progress_records", on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, related_name="drip_progress", on_delete=models.CASCADE)
    next_step = models.ForeignKey(DripStep, null=True, blank=True, related_name="next_for", on_delete=models.SET_NULL)
    last_step = models.ForeignKey(DripStep, null=True, blank=True, related_name="completed_for", on_delete=models.SET_NULL)
    next_send_at = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("drip_campaign", "subscription")
        verbose_name = _("Drip progress")
        verbose_name_plural = _("Drip progress records")

    def __str__(self) -> str:
        return f"{self.subscription} – {self.drip_campaign.name}"

    def schedule_next(self, base: Optional[datetime] = None):
        if self.completed:
            return
        if base is None:
            base = self.subscription.confirmed_at or timezone.now()
        if self.drip_campaign.start_strategy == DripCampaign.StartStrategy.DELAYED and not self.last_step:
            base += timedelta(days=self.drip_campaign.start_delay_days)
        next_step = self.drip_campaign.steps.filter(
            order__gt=self.last_step.order if self.last_step else 0
        ).order_by("order").first()
        if not next_step:
            self.completed = True
            self.next_step = None
            self.next_send_at = None
            self.save(update_fields=["completed", "next_step", "next_send_at", "updated_at"])
            return
        send_at = next_step.compute_send_datetime(base)
        self.next_step = next_step
        self.next_send_at = send_at
        self.save(update_fields=["next_step", "next_send_at", "updated_at"])

    def mark_sent(self, step: DripStep):
        self.last_step = step
        self.save(update_fields=["last_step", "updated_at"])
        self.schedule_next(base=self.subscription.confirmed_at)


class EmailMessageLog(TimeStampedModel):
    class Status(models.TextChoices):
        QUEUED = "queued", _("Queued")
        SENT = "sent", _("Sent")
        DELIVERED = "delivered", _("Delivered")
        OPENED = "opened", _("Opened")
        CLICKED = "clicked", _("Clicked")
        BOUNCED = "bounced", _("Bounced")
        FAILED = "failed", _("Failed")

    subscription = models.ForeignKey(Subscription, related_name="email_logs", on_delete=models.CASCADE)
    subscriber = models.ForeignKey(Subscriber, related_name="email_logs", on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, null=True, blank=True, related_name="email_logs", on_delete=models.SET_NULL)
    drip_step = models.ForeignKey(DripStep, null=True, blank=True, related_name="email_logs", on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)
    subject = models.CharField(max_length=255)
    message_id = models.CharField(max_length=255, blank=True)
    provider_message_id = models.CharField(max_length=255, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    bounced_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Email log")
        verbose_name_plural = _("Email logs")

    def __str__(self) -> str:
        return f"{self.subject} → {self.subscriber.email}"


class EmailEvent(TimeStampedModel):
    log = models.ForeignKey(EmailMessageLog, related_name="events", on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50)
    recipient = models.EmailField()
    occurred_at = models.DateTimeField()
    payload = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-occurred_at"]
        verbose_name = _("Email event")
        verbose_name_plural = _("Email events")

    def __str__(self) -> str:
        return f"{self.event_type} @ {self.occurred_at:%Y-%m-%d %H:%M}"


def _next_weekday(current: date, weekday: int) -> date:
    if weekday < 0 or weekday > 6:
        raise ValidationError("Weekday must be between 0 (Monday) and 6 (Sunday)")
    days_ahead = (weekday - current.weekday()) % 7
    return current + timedelta(days=days_ahead)


def _absolute_url(path: str, request=None) -> str:
    if request is not None:
        return request.build_absolute_uri(path)
    base_url = getattr(settings, "NEWSLETTER_BASE_URL", "")
    if base_url:
        return f"{base_url.rstrip('/')}{path}"
    return path
