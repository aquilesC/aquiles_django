from django.contrib import admin

from .models import (
    Campaign,
    DripCampaign,
    DripSequenceProgress,
    DripStep,
    EmailEvent,
    EmailMessageLog,
    EmailTemplate,
    Subscriber,
    Subscription,
    SubscriptionList,
)


@admin.register(SubscriptionList)
class SubscriptionListAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "double_opt_in", "is_public")
    search_fields = ("name", "slug")


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "created_at")
    search_fields = ("email", "first_name", "last_name")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("subscriber", "subscription_list", "status", "confirmed_at")
    list_filter = ("status", "subscription_list")
    search_fields = ("subscriber__email",)


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "subject_template", "updated_at")
    search_fields = ("name", "subject_template")


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "send_at", "sent_at")
    list_filter = ("status", "lists")
    search_fields = ("name",)
    filter_horizontal = ("lists",)


@admin.register(DripCampaign)
class DripCampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "subscription_list", "enabled")
    list_filter = ("subscription_list", "enabled")


@admin.register(DripStep)
class DripStepAdmin(admin.ModelAdmin):
    list_display = ("drip_campaign", "order", "title", "offset_days", "offset_weeks", "send_weekday")
    list_filter = ("drip_campaign",)


@admin.register(DripSequenceProgress)
class DripSequenceProgressAdmin(admin.ModelAdmin):
    list_display = ("drip_campaign", "subscription", "next_step", "next_send_at", "completed")
    list_filter = ("drip_campaign", "completed")


@admin.register(EmailMessageLog)
class EmailMessageLogAdmin(admin.ModelAdmin):
    list_display = ("subject", "subscriber", "status", "sent_at")
    list_filter = ("status", "campaign")
    search_fields = ("subject", "subscriber__email")


@admin.register(EmailEvent)
class EmailEventAdmin(admin.ModelAdmin):
    list_display = ("event_type", "recipient", "occurred_at")
    list_filter = ("event_type",)
    search_fields = ("recipient", "event_type")
