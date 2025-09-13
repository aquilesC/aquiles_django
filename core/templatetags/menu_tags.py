from django import template
from django.core.cache import cache
from ..models import MainMenu, FooterMenu

register = template.Library()


@register.inclusion_tag('core/menu.html', takes_context=True)
def main_menu(context):
    """Render the main navigation menu"""
    cache_key = 'main_menu_items'
    menu_items = cache.get(cache_key)
    
    if menu_items is None:
        try:
            main_menu = MainMenu.objects.first()
            if main_menu:
                menu_items = main_menu.get_menu_items()
            else:
                menu_items = []
            # Cache for 5 minutes
            cache.set(cache_key, menu_items, 300)
        except Exception:
            menu_items = []
    
    return {
        'menu_items': menu_items,
        'request': context['request'],
    }


@register.inclusion_tag('core/footer_menu.html', takes_context=True)
def footer_menu(context):
    """Render the footer links menu"""
    cache_key = 'footer_menu_items'
    menu_items = cache.get(cache_key)
    
    if menu_items is None:
        try:
            footer_menu = FooterMenu.objects.first()
            if footer_menu:
                menu_items = footer_menu.get_menu_items()
            else:
                menu_items = []
            # Cache for 5 minutes
            cache.set(cache_key, menu_items, 300)
        except Exception:
            menu_items = []
    
    return {
        'menu_items': menu_items,
        'request': context['request'],
    }


@register.simple_tag
def clear_menu_cache():
    """Clear menu cache (useful for admin actions)"""
    cache.delete('main_menu_items')
    cache.delete('footer_menu_items')
    return ""
