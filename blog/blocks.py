from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.contrib.table_block.blocks import TableBlock

# RichText feature set you’ll enable in settings/editor:
RICH_FEATURES = ["bold", "italic", "link", "ol", "ul", "code", "h2", "h3", "h4"]

class LeadBlock(blocks.TextBlock):
    class Meta:
        icon = "openquote"
        label = "Lead (Summary)"
        help_text = "1–2 sentence intro (also used as excerpt)."

class HeadingBlock(blocks.StructBlock):
    text = blocks.CharBlock()
    level = blocks.ChoiceBlock(choices=[("h2", "H2"), ("h3", "H3")], default="h2")
    anchor = blocks.CharBlock(required=False, help_text="Optional custom id")
    class Meta:
        icon = "title"
        label = "Heading"

class ImageWithCaption(blocks.StructBlock):
    image = ImageChooserBlock()
    alt = blocks.CharBlock(required=False, help_text="Alt text override")
    caption = blocks.RichTextBlock(required=False, features=["bold", "italic", "link"])
    align = blocks.ChoiceBlock(choices=[("full", "Full"), ("wide", "Wide"), ("left", "Left"), ("right", "Right")], default="full")
    class Meta:
        icon = "image"
        label = "Image"

class PullQuote(blocks.StructBlock):
    quote = blocks.TextBlock()
    attribution = blocks.CharBlock(required=False)
    class Meta:
        icon = "openquote"
        label = "Pull quote"

class Callout(blocks.StructBlock):
    variant = blocks.ChoiceBlock(choices=[("note", "Note"), ("tip", "Tip"), ("warning", "Warning")], default="note")
    body = blocks.RichTextBlock(features=RICH_FEATURES)
    class Meta:
        icon = "placeholder"
        label = "Callout"

class CodeBlock(blocks.StructBlock):
    language = blocks.ChoiceBlock(choices=[
        ("text", "Plain text"), ("python", "Python"), ("bash", "Bash"),
        ("html", "HTML"), ("css", "CSS"), ("js", "JavaScript"),
        ("json", "JSON"), ("sql", "SQL"),
    ], default="python")
    code = blocks.TextBlock()
    caption = blocks.CharBlock(required=False)
    class Meta:
        icon = "code"
        label = "Code"

class EmbedBlock(blocks.URLBlock):
    class Meta:
        icon = "media"
        label = "Embed (URL)"

class Divider(blocks.StaticBlock):
    class Meta:
        icon = "horizontalrule"
        label = "Divider"
        admin_text = "Thematic break"

class BlogBodyStreamBlock(blocks.StreamBlock):
    lead = LeadBlock()
    paragraph = blocks.RichTextBlock(features=RICH_FEATURES)
    heading = HeadingBlock()
    image = ImageWithCaption()
    pullquote = PullQuote()
    callout = Callout()
    code = CodeBlock()
    embed = EmbedBlock()
    table = TableBlock()
    divider = Divider()

    class Meta:
        block_counts = {
            "lead": {"max_num": 1},
        }
        label = "Blog content"
