from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from wagtail.models import Site, Page
from pages.models import HomePage, BlogIndexPage, ProjectIndexPage, ContactPage, LegalPage, SiteSettings


class Command(BaseCommand):
    help = 'Set up the initial site structure for Aquiles Personal Website'

    def handle(self, *args, **options):
        self.stdout.write('Setting up site structure...')
        
        # Get the root page
        root_page = Page.objects.get(id=1)
        
        # Create or replace home page
        existing_home = Page.objects.filter(slug='home').first()
        if existing_home and not isinstance(existing_home, HomePage):
            # Delete the default Wagtail home page
            existing_home.delete()
            self.stdout.write('✓ Removed default Wagtail home page')
        
        if not HomePage.objects.exists():
            home_page = HomePage(
                title="Home",
                slug="home",
                hero_title="Welcome to Aquiles' Personal Website",
                hero_subtitle="Exploring technology, sharing knowledge, and building the future",
                about_title="About Me",
                about_content="<p>I'm passionate about technology and constantly learning new things. This website serves as my digital garden where I share insights, projects, and thoughts on various topics.</p><p>From web development to machine learning, I explore different areas of technology and document my journey here.</p>",
                contact_email="aquiles@example.com",
            )
            root_page.add_child(instance=home_page)
            home_page.save_revision().publish()
            self.stdout.write(self.style.SUCCESS('✓ Created Home page'))
        else:
            home_page = HomePage.objects.first()
            self.stdout.write('✓ Home page already exists')
        
        # Create blog index page
        if not BlogIndexPage.objects.exists():
            blog_index = BlogIndexPage(
                title="Blog",
                slug="blog",
                intro="<p>Thoughts, tutorials, and insights about technology and development.</p>",
                posts_per_page=10,
            )
            home_page.add_child(instance=blog_index)
            self.stdout.write(self.style.SUCCESS('✓ Created Blog Index page'))
        else:
            self.stdout.write('✓ Blog Index page already exists')
        
        # Create project index page
        if not ProjectIndexPage.objects.exists():
            project_index = ProjectIndexPage(
                title="Projects",
                slug="projects",
                intro="<p>A collection of my projects and work.</p>",
                projects_per_page=12,
            )
            home_page.add_child(instance=project_index)
            self.stdout.write(self.style.SUCCESS('✓ Created Project Index page'))
        else:
            self.stdout.write('✓ Project Index page already exists')
        
        # Create contact page
        if not ContactPage.objects.exists():
            contact_page = ContactPage(
                title="Contact",
                slug="contact",
                intro="<p>Get in touch with me for collaborations, questions, or just to say hello.</p>",
                contact_form_title="Get in Touch",
                email="aquiles@example.com",
            )
            home_page.add_child(instance=contact_page)
            self.stdout.write(self.style.SUCCESS('✓ Created Contact page'))
        else:
            self.stdout.write('✓ Contact page already exists')
        
        # Create legal pages
        if not LegalPage.objects.filter(slug="privacy-policy").exists():
            privacy_page = LegalPage(
                title="Privacy Policy",
                slug="privacy-policy",
                content="<h2>Privacy Policy</h2><p>This is a placeholder privacy policy. Please update with your actual privacy policy content.</p>",
            )
            home_page.add_child(instance=privacy_page)
            self.stdout.write(self.style.SUCCESS('✓ Created Privacy Policy page'))
        else:
            self.stdout.write('✓ Privacy Policy page already exists')
        
        if not LegalPage.objects.filter(slug="cookie-policy").exists():
            cookie_page = LegalPage(
                title="Cookie Policy",
                slug="cookie-policy",
                content="<h2>Cookie Policy</h2><p>This is a placeholder cookie policy. Please update with your actual cookie policy content.</p>",
            )
            home_page.add_child(instance=cookie_page)
            self.stdout.write(self.style.SUCCESS('✓ Created Cookie Policy page'))
        else:
            self.stdout.write('✓ Cookie Policy page already exists')
        
        # Create or update site settings
        site_settings, created = SiteSettings.objects.get_or_create(
            defaults={
                'site_name': "Aquiles Personal Website",
                'site_description': "Personal website showcasing projects, blog posts, and insights about technology",
                'site_keywords': "technology, web development, programming, projects, blog",
                'twitter_handle': "",
                'github_username': "",
                'linkedin_url': "",
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created Site Settings'))
        else:
            self.stdout.write('✓ Site Settings already exists')
        
        # Create or update Wagtail site
        site, created = Site.objects.get_or_create(
            defaults={
                'hostname': 'localhost',
                'port': 80,
                'root_page': home_page,
                'site_name': 'Aquiles Personal Website',
                'is_default_site': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created Wagtail Site'))
        else:
            self.stdout.write('✓ Wagtail Site already exists')
        
        self.stdout.write(self.style.SUCCESS('Site structure setup completed successfully!'))
