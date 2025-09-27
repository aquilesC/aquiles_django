from __future__ import annotations

from wagtail import blocks
from wagtail.snippets.blocks import SnippetChooserBlock


class NewsletterSignupBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False, help_text="Optional heading displayed above the form.")
    subheading = blocks.TextBlock(required=False, help_text="Short supporting text.")
    lists = blocks.ListBlock(
        SnippetChooserBlock(target_model="newsletter.SubscriptionList"),
        help_text="Choose the subscription lists that this form should submit to.",
        min_num=1,
    )
    allow_multiple = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Allow visitors to choose multiple lists",
    )
    show_name_fields = blocks.BooleanBlock(
        required=False,
        default=True,
        help_text="Collect first and last name fields",
    )
    button_text = blocks.CharBlock(default="Subscribe", help_text="Submit button label")
    success_message = blocks.CharBlock(
        required=False,
        default="Thanks for subscribing! Check your inbox for a confirmation email.",
        help_text="Message shown after a successful submission (uses Django messages).",
    )
    layout = blocks.ChoiceBlock(
        choices=[
            ("stacked", "Stacked"),
            ("inline", "Inline"),
        ],
        default="stacked",
        help_text="Form layout style",
    )
    background = blocks.ChoiceBlock(
        choices=[
            ("default", "Default"),
            ("muted", "Muted"),
            ("primary", "Primary"),
        ],
        default="default",
    )

    class Meta:
        template = "blocks/newsletter_signup_block.html"
        icon = "mail"
        label = "Newsletter sign-up"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        list_ids = [str(list_item.pk) for list_item in value["lists"]]
        context.update(
            {
                "list_ids": list_ids,
                "allow_multiple": value["allow_multiple"],
                "show_name_fields": value["show_name_fields"],
                "button_text": value["button_text"],
                "success_message": value["success_message"],
                "layout": value["layout"],
                "background": value["background"],
                "subheading": value.get("subheading"),
                "form_id": f"newsletter-{id(value)}",
            }
        )
        return context
