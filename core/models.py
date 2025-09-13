from django.db import models
from django import forms
from django.core.exceptions import ValidationError
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.snippets.models import register_snippet
from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey
from wagtail.fields import RichTextField


class MenuItem(ClusterableModel):
    """Individual menu item that can be added to menus"""
    
    MENU_TYPES = [
        ('main', 'Main Navigation'),
        ('footer', 'Footer Links'),
    ]
    
    title = models.CharField(max_length=255, help_text="Menu item title")
    link_url = models.URLField(blank=True, help_text="External URL (leave blank for page link)")
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text="Page to link to (overrides external URL)"
    )
    menu_type = models.CharField(max_length=20, choices=MENU_TYPES, default='main')
    sort_order = models.PositiveIntegerField(default=0, help_text="Order in menu (lower numbers first)")
    is_active = models.BooleanField(default=True, help_text="Show this item in the menu")
    
    panels = [
        FieldPanel('title'),
        FieldPanel('menu_type'),
        FieldPanel('link_page'),
        FieldPanel('link_url'),
        FieldPanel('sort_order'),
        FieldPanel('is_active'),
    ]
    
    class Meta:
        ordering = ['sort_order', 'title']
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"
    
    def __str__(self):
        return self.title
    
    def clean(self):
        """Validate that either link_page or link_url is provided"""
        if not self.link_page and not self.link_url:
            raise ValidationError("Either a page or URL must be specified.")
        if self.link_page and self.link_url:
            raise ValidationError("Please specify either a page OR a URL, not both.")
    
    @property
    def url(self):
        """Get the URL for this menu item"""
        if self.link_page:
            return self.link_page.url
        return self.link_url
    
    @property
    def is_external(self):
        """Check if this is an external link"""
        return bool(self.link_url)


class MainMenu(models.Model):
    """Main navigation menu"""
    
    title = models.CharField(max_length=255, default="Main Menu")
    items = models.ManyToManyField(MenuItem, blank=True, related_name='main_menus')
    
    panels = [
        FieldPanel('title'),
        FieldPanel('items', widget=forms.CheckboxSelectMultiple),
    ]
    
    class Meta:
        verbose_name = "Main Menu"
        verbose_name_plural = "Main Menus"
    
    def __str__(self):
        return self.title
    
    def get_menu_items(self):
        """Get active menu items ordered by sort_order"""
        return self.items.filter(is_active=True, menu_type='main').order_by('sort_order')


class FooterMenu(models.Model):
    """Footer links menu"""
    
    title = models.CharField(max_length=255, default="Footer Links")
    items = models.ManyToManyField(MenuItem, blank=True, related_name='footer_menus')
    
    panels = [
        FieldPanel('title'),
        FieldPanel('items', widget=forms.CheckboxSelectMultiple),
    ]
    
    class Meta:
        verbose_name = "Footer Menu"
        verbose_name_plural = "Footer Menus"
    
    def __str__(self):
        return self.title
    
    def get_menu_items(self):
        """Get active menu items ordered by sort_order"""
        return self.items.filter(is_active=True, menu_type='footer').order_by('sort_order')


# Register snippets for admin interface
register_snippet(MenuItem)
register_snippet(MainMenu)
register_snippet(FooterMenu)