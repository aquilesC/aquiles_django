from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel
from wagtail.search import index
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase


class BlogPageTag(TaggedItemBase):
    """Tags for blog posts"""
    content_object = ParentalKey('BlogPage', on_delete=models.CASCADE, related_name='tagged_items')


class BlogPage(Page):
    """Individual blog post page"""
    
    intro = models.CharField(max_length=500, help_text="Brief introduction to the blog post")
    body = RichTextField(help_text="Main content of the blog post")
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Featured image for the blog post"
    )
    tags = models.ManyToManyField('taggit.Tag', through=BlogPageTag, blank=True)
    
    # SEO fields
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO meta description")
    
    # Access control
    is_members_only = models.BooleanField(default=False, help_text="Make this post members-only")
    
    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('body'),
        FieldPanel('featured_image'),
        FieldPanel('tags'),
        FieldPanel('is_members_only'),
    ]
    
    promote_panels = Page.promote_panels + [
        FieldPanel('meta_description'),
    ]
    
    class Meta:
        verbose_name = "Blog Post"
