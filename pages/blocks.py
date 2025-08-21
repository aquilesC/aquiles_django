from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock


class HeroBlock(blocks.StructBlock):
    """Hero section with title, subtitle, background image/color, and CTA"""
    title = blocks.CharBlock(max_length=200, help_text="Hero title")
    subtitle = blocks.TextBlock(max_length=500, required=False, help_text="Hero subtitle")
    background_image = ImageChooserBlock(required=False, help_text="Background image")
    background_color = blocks.CharBlock(
        max_length=7, 
        required=False, 
        help_text="Background color (hex code, e.g., #ffffff)"
    )
    cta_text = blocks.CharBlock(max_length=50, required=False, help_text="Call-to-action button text")
    cta_link = blocks.URLBlock(required=False, help_text="Call-to-action link")
    cta_style = blocks.ChoiceBlock(
        choices=[
            ('primary', 'Primary Button'),
            ('secondary', 'Secondary Button'),
            ('outline', 'Outline Button'),
        ],
        default='primary'
    )

    class Meta:
        template = 'blocks/hero_block.html'
        icon = 'image'
        label = 'Hero Section'


class IntroTextBlock(blocks.StructBlock):
    """Rich text with optional image/illustration"""
    heading = blocks.CharBlock(max_length=200, required=False, help_text="Optional heading")
    text = blocks.RichTextBlock(help_text="Main text content")
    image = ImageChooserBlock(required=False, help_text="Optional image or illustration")
    image_position = blocks.ChoiceBlock(
        choices=[
            ('left', 'Left'),
            ('right', 'Right'),
            ('top', 'Top'),
            ('bottom', 'Bottom'),
        ],
        default='right',
        help_text="Image position relative to text"
    )

    class Meta:
        template = 'blocks/intro_text_block.html'
        icon = 'doc-full'
        label = 'Intro Text'


class CardBlock(blocks.StructBlock):
    """Individual card for use in CardGridBlock"""
    title = blocks.CharBlock(max_length=200, help_text="Card title")
    description = blocks.TextBlock(max_length=300, help_text="Card description")
    image = ImageChooserBlock(required=False, help_text="Card image")
    link = blocks.URLBlock(required=False, help_text="Card link")
    link_text = blocks.CharBlock(max_length=50, required=False, default="Learn more")


class CardGridBlock(blocks.StructBlock):
    """Grid of cards for Projects, Services, Writing, etc."""
    heading = blocks.CharBlock(max_length=200, required=False, help_text="Section heading")
    description = blocks.TextBlock(max_length=500, required=False, help_text="Section description")
    cards = blocks.ListBlock(CardBlock(), min_num=1, max_num=12, help_text="Add cards to display")
    columns = blocks.ChoiceBlock(
        choices=[
            ('2', '2 Columns'),
            ('3', '3 Columns'),
            ('4', '4 Columns'),
        ],
        default='3',
        help_text="Number of columns on desktop"
    )

    class Meta:
        template = 'blocks/card_grid_block.html'
        icon = 'grip'
        label = 'Card Grid'


class PostListBlock(blocks.StructBlock):
    """Shows latest or tagged posts"""
    heading = blocks.CharBlock(max_length=200, required=False, help_text="Section heading")
    description = blocks.TextBlock(max_length=500, required=False, help_text="Section description")
    post_count = blocks.IntegerBlock(default=3, min_value=1, max_value=12, help_text="Number of posts to show")
    show_featured_only = blocks.BooleanBlock(required=False, help_text="Show only featured posts")
    tag_filter = blocks.CharBlock(max_length=100, required=False, help_text="Filter by tag (optional)")
    show_images = blocks.BooleanBlock(default=True, help_text="Show post featured images")
    show_excerpts = blocks.BooleanBlock(default=True, help_text="Show post excerpts")

    class Meta:
        template = 'blocks/post_list_block.html'
        icon = 'list-ul'
        label = 'Post List'


class QuoteBlock(blocks.StructBlock):
    """Testimonial or pull quote"""
    quote = blocks.TextBlock(help_text="Quote text")
    author = blocks.CharBlock(max_length=100, required=False, help_text="Quote author")
    author_title = blocks.CharBlock(max_length=200, required=False, help_text="Author title/position")
    author_image = ImageChooserBlock(required=False, help_text="Author photo")
    quote_style = blocks.ChoiceBlock(
        choices=[
            ('testimonial', 'Testimonial Style'),
            ('pullquote', 'Pull Quote Style'),
            ('blockquote', 'Block Quote Style'),
        ],
        default='testimonial'
    )

    class Meta:
        template = 'blocks/quote_block.html'
        icon = 'openquote'
        label = 'Quote'


class StatBlock(blocks.StructBlock):
    """Individual stat for use in StatsBlock"""
    number = blocks.CharBlock(max_length=20, help_text="The number/statistic")
    label = blocks.CharBlock(max_length=100, help_text="Label for the statistic")
    description = blocks.CharBlock(max_length=200, required=False, help_text="Optional description")


class StatsBlock(blocks.StructBlock):
    """Numbers with labels"""
    heading = blocks.CharBlock(max_length=200, required=False, help_text="Section heading")
    description = blocks.TextBlock(max_length=500, required=False, help_text="Section description")
    stats = blocks.ListBlock(StatBlock(), min_num=1, max_num=8, help_text="Add statistics")

    class Meta:
        template = 'blocks/stats_block.html'
        icon = 'snippet'
        label = 'Statistics'


class LogoBlock(blocks.StructBlock):
    """Individual logo for use in LogosBlock"""
    logo = ImageChooserBlock(help_text="Company logo")
    company_name = blocks.CharBlock(max_length=100, help_text="Company name (for alt text)")
    link = blocks.URLBlock(required=False, help_text="Company website")


class LogosBlock(blocks.StructBlock):
    """Grid of company logos"""
    heading = blocks.CharBlock(max_length=200, required=False, help_text="Section heading")
    description = blocks.TextBlock(max_length=500, required=False, help_text="Section description")
    logos = blocks.ListBlock(LogoBlock(), min_num=1, max_num=20, help_text="Add company logos")
    grayscale = blocks.BooleanBlock(default=True, help_text="Display logos in grayscale")

    class Meta:
        template = 'blocks/logos_block.html'
        icon = 'image'
        label = 'Logos Grid'


class CTASectionBlock(blocks.StructBlock):
    """Call-to-action section with headline, subheadline, and button"""
    headline = blocks.CharBlock(max_length=200, help_text="Main headline")
    subheadline = blocks.TextBlock(max_length=500, required=False, help_text="Supporting text")
    button_text = blocks.CharBlock(max_length=50, help_text="Button text")
    button_link = blocks.URLBlock(help_text="Button link")
    button_style = blocks.ChoiceBlock(
        choices=[
            ('primary', 'Primary Button'),
            ('secondary', 'Secondary Button'),
            ('outline', 'Outline Button'),
        ],
        default='primary'
    )
    background_color = blocks.ChoiceBlock(
        choices=[
            ('white', 'White'),
            ('gray', 'Light Gray'),
            ('primary', 'Primary Color'),
            ('dark', 'Dark'),
        ],
        default='gray'
    )

    class Meta:
        template = 'blocks/cta_section_block.html'
        icon = 'plus'
        label = 'CTA Section'


class FAQItemBlock(blocks.StructBlock):
    """Individual FAQ item"""
    question = blocks.CharBlock(max_length=300, help_text="FAQ question")
    answer = blocks.RichTextBlock(help_text="FAQ answer")


class FAQBlock(blocks.StructBlock):
    """Accordion of question+answer"""
    heading = blocks.CharBlock(max_length=200, required=False, help_text="Section heading")
    description = blocks.TextBlock(max_length=500, required=False, help_text="Section description")
    faqs = blocks.ListBlock(FAQItemBlock(), min_num=1, help_text="Add FAQ items")

    class Meta:
        template = 'blocks/faq_block.html'
        icon = 'help'
        label = 'FAQ'


class ContactBlock(blocks.StructBlock):
    """Contact form embed or contact information"""
    heading = blocks.CharBlock(max_length=200, required=False, help_text="Section heading")
    description = blocks.TextBlock(max_length=500, required=False, help_text="Section description")
    contact_type = blocks.ChoiceBlock(
        choices=[
            ('form', 'Contact Form'),
            ('info', 'Contact Information'),
            ('both', 'Form and Information'),
        ],
        default='both'
    )
    email = blocks.EmailBlock(required=False, help_text="Contact email")
    phone = blocks.CharBlock(max_length=20, required=False, help_text="Contact phone")
    address = blocks.TextBlock(required=False, help_text="Contact address")
    form_title = blocks.CharBlock(max_length=100, required=False, default="Get in Touch")

    class Meta:
        template = 'blocks/contact_block.html'
        icon = 'mail'
        label = 'Contact'


class DividerBlock(blocks.StructBlock):
    """Spacer / visual break"""
    divider_style = blocks.ChoiceBlock(
        choices=[
            ('line', 'Simple Line'),
            ('dots', 'Dots'),
            ('wave', 'Wave'),
            ('space', 'Just Space'),
        ],
        default='line'
    )
    spacing = blocks.ChoiceBlock(
        choices=[
            ('small', 'Small (2rem)'),
            ('medium', 'Medium (4rem)'),
            ('large', 'Large (6rem)'),
        ],
        default='medium'
    )

    class Meta:
        template = 'blocks/divider_block.html'
        icon = 'horizontalrule'
        label = 'Divider'


# Main StreamField block choices
STREAMFIELD_BLOCKS = [
    ('hero', HeroBlock()),
    ('intro_text', IntroTextBlock()),
    ('card_grid', CardGridBlock()),
    ('post_list', PostListBlock()),
    ('quote', QuoteBlock()),
    ('stats', StatsBlock()),
    ('logos', LogosBlock()),
    ('cta_section', CTASectionBlock()),
    ('faq', FAQBlock()),
    ('contact', ContactBlock()),
    ('divider', DividerBlock()),
]