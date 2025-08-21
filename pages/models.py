from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail import blocks
from wagtail.search import index
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.models import TaggedItemBase
from wagtail.snippets.models import register_snippet
from .blocks import STREAMFIELD_BLOCKS


class HomePage(Page):
    """Home page model with flexible content blocks"""
    
    # StreamField for flexible content
    content = StreamField(STREAMFIELD_BLOCKS, blank=True, use_json_field=True)
    
    search_fields = Page.search_fields + [
        index.SearchField('content'),
    ]
    
    content_panels = Page.content_panels + [
        FieldPanel('content'),
    ]
    
    class Meta:
        verbose_name = "Home Page"


class AboutPage(Page):
    """About page with flexible content blocks"""
    
    # StreamField for flexible content
    content = StreamField(STREAMFIELD_BLOCKS, blank=True, use_json_field=True)
    
    search_fields = Page.search_fields + [
        index.SearchField('content'),
    ]
    
    content_panels = Page.content_panels + [
        FieldPanel('content'),
    ]
    
    class Meta:
        verbose_name = "About Page"


class ServicesPage(Page):
    """Services/Offers page with flexible content blocks"""
    
    # StreamField for flexible content
    content = StreamField(STREAMFIELD_BLOCKS, blank=True, use_json_field=True)
    
    search_fields = Page.search_fields + [
        index.SearchField('content'),
    ]
    
    content_panels = Page.content_panels + [
        FieldPanel('content'),
    ]
    
    class Meta:
        verbose_name = "Services Page"


class BlogIndexPage(Page):
    """Blog listing page"""
    
    intro = RichTextField(blank=True, help_text="Introduction text for the blog")
    posts_per_page = models.IntegerField(default=10, help_text="Number of posts per page")
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('posts_per_page'),
    ]
    
    def get_context(self, request):
        context = super().get_context(request)
        from blog.models import BlogPage
        blog_posts = BlogPage.objects.live().descendant_of(self).order_by('-first_published_at')
        context['blog_posts'] = blog_posts
        return context
    
    class Meta:
        verbose_name = "Blog Index Page"





class ProjectIndexPage(Page):
    """Project listing page"""
    
    intro = RichTextField(blank=True, help_text="Introduction text for the projects section")
    projects_per_page = models.IntegerField(default=12, help_text="Number of projects per page")
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('projects_per_page'),
    ]
    
    def get_context(self, request):
        context = super().get_context(request)
        projects = ProjectPage.objects.live().descendant_of(self).order_by('-first_published_at')
        context['projects'] = projects
        return context
    
    class Meta:
        verbose_name = "Project Index Page"


class ProjectPage(Page):
    """Individual project page with flexible content"""
    
    # Essential project info
    summary = models.CharField(max_length=500, help_text="Brief summary of the project")
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Featured image for the project"
    )
    
    # Project details
    tech_stack = StreamField([
        ('tech_item', blocks.CharBlock(max_length=100)),
    ], blank=True, use_json_field=True, help_text="Technologies used in the project")
    
    project_url = models.URLField(blank=True, help_text="Link to the live project")
    github_url = models.URLField(blank=True, help_text="Link to the GitHub repository")
    
    # Project status
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    
    # Flexible content using StreamField
    content = StreamField(STREAMFIELD_BLOCKS, blank=True, use_json_field=True, help_text="Main project content")
    
    # Access control
    is_members_only = models.BooleanField(default=False, help_text="Make this project members-only")
    
    search_fields = Page.search_fields + [
        index.SearchField('summary'),
        index.SearchField('content'),
    ]
    
    content_panels = Page.content_panels + [
        FieldPanel('summary'),
        FieldPanel('featured_image'),
        FieldPanel('tech_stack'),
        FieldPanel('project_url'),
        FieldPanel('github_url'),
        FieldPanel('status'),
        FieldPanel('content'),
        FieldPanel('is_members_only'),
    ]
    
    class Meta:
        verbose_name = "Project"


class ContactPage(Page):
    """Contact page with form and contact information"""
    
    intro = RichTextField(blank=True, help_text="Introduction text for the contact page")
    contact_form_title = models.CharField(max_length=200, default="Get in Touch")
    
    # Contact information
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    # Social links
    social_links = StreamField([
        ('social_link', blocks.StructBlock([
            ('platform', blocks.CharBlock(max_length=50)),
            ('url', blocks.URLBlock()),
            ('icon', blocks.CharBlock(max_length=50, help_text="Icon class or name")),
        ])),
    ], blank=True, use_json_field=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('contact_form_title'),
        MultiFieldPanel([
            FieldPanel('email'),
            FieldPanel('phone'),
            FieldPanel('address'),
        ], heading="Contact Information"),
        FieldPanel('social_links'),
    ]
    
    class Meta:
        verbose_name = "Contact Page"


class LegalPage(Page):
    """Legal pages like Privacy Policy and Cookie Policy"""
    
    content = RichTextField(help_text="Legal content")
    last_updated = models.DateField(auto_now=True, editable=False)
    
    content_panels = Page.content_panels + [
        FieldPanel('content'),
    ]
    
    class Meta:
        verbose_name = "Legal Page"


# Register snippets for admin interface
@register_snippet
class SiteSettings(ClusterableModel):
    """Site-wide settings"""
    
    site_name = models.CharField(max_length=100, default="Aquiles Personal Website")
    site_description = models.TextField(blank=True)
    site_keywords = models.CharField(max_length=500, blank=True)
    
    # Social media
    twitter_handle = models.CharField(max_length=50, blank=True)
    github_username = models.CharField(max_length=50, blank=True)
    linkedin_url = models.URLField(blank=True)
    
    # Analytics
    google_analytics_id = models.CharField(max_length=50, blank=True)
    
    panels = [
        MultiFieldPanel([
            FieldPanel('site_name'),
            FieldPanel('site_description'),
            FieldPanel('site_keywords'),
        ], heading="Site Information"),
        MultiFieldPanel([
            FieldPanel('twitter_handle'),
            FieldPanel('github_username'),
            FieldPanel('linkedin_url'),
        ], heading="Social Media"),
        MultiFieldPanel([
            FieldPanel('google_analytics_id'),
        ], heading="Analytics"),
    ]
    
    class Meta:
        verbose_name = "Site Settings"
    
    def __str__(self):
        return self.site_name
