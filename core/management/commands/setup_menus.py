from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from wagtail.models import Page
from core.models import MenuItem, MainMenu, FooterMenu


class Command(BaseCommand):
    help = 'Set up initial menu items for the website'

    def handle(self, *args, **options):
        self.stdout.write('Setting up initial menus...')
        
        # Create main menu items
        main_menu_items = [
            {'title': 'Blog', 'sort_order': 1, 'menu_type': 'main'},
            {'title': 'Projects', 'sort_order': 2, 'menu_type': 'main'},
            {'title': 'About', 'sort_order': 3, 'menu_type': 'main'},
            {'title': 'Contact', 'sort_order': 4, 'menu_type': 'main'},
        ]
        
        # Create footer menu items
        footer_menu_items = [
            {'title': 'Privacy Policy', 'sort_order': 1, 'menu_type': 'footer', 'link_url': '/privacy/'},
            {'title': 'Terms of Service', 'sort_order': 2, 'menu_type': 'footer', 'link_url': '/terms/'},
            {'title': 'Disclaimer', 'sort_order': 3, 'menu_type': 'footer', 'link_url': '/disclaimer/'},
            {'title': 'Sitemap', 'sort_order': 4, 'menu_type': 'footer', 'link_url': '/sitemap.xml'},
        ]
        
        # Create menu items
        created_items = []
        
        for item_data in main_menu_items + footer_menu_items:
            item, created = MenuItem.objects.get_or_create(
                title=item_data['title'],
                menu_type=item_data['menu_type'],
                defaults={
                    'sort_order': item_data['sort_order'],
                    'link_url': item_data.get('link_url', ''),
                    'is_active': True,
                }
            )
            if created:
                created_items.append(item)
                self.stdout.write(f'Created menu item: {item.title}')
        
        # Create or get main menu
        main_menu, created = MainMenu.objects.get_or_create(
            title='Main Navigation',
            defaults={}
        )
        if created:
            self.stdout.write('Created main menu')
        
        # Add main menu items to main menu
        main_menu_items_objs = MenuItem.objects.filter(menu_type='main')
        main_menu.items.set(main_menu_items_objs)
        self.stdout.write(f'Added {main_menu_items_objs.count()} items to main menu')
        
        # Create or get footer menu
        footer_menu, created = FooterMenu.objects.get_or_create(
            title='Footer Links',
            defaults={}
        )
        if created:
            self.stdout.write('Created footer menu')
        
        # Add footer menu items to footer menu
        footer_menu_items_objs = MenuItem.objects.filter(menu_type='footer')
        footer_menu.items.set(footer_menu_items_objs)
        self.stdout.write(f'Added {footer_menu_items_objs.count()} items to footer menu')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully set up menus with {len(created_items)} new menu items'
            )
        )
