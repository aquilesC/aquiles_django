#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aquiles_site.settings')
django.setup()

from wagtail.models import Site, Page
from pages.models import HomePage, BlogIndexPage, ProjectIndexPage, ContactPage, LegalPage, SiteSettings

def setup_pages():
    print("Setting up pages...")
    
    # Get the root page
    root_page = Page.objects.get(id=1)
    
    # Create home page
    if not HomePage.objects.exists():
        home_page = HomePage(
            title="Home",
            slug="home",
            path="00010001",
            depth=2,
            hero_title="Welcome to Aquiles' Personal Website",
            hero_subtitle="Exploring technology, sharing knowledge, and building the future",
            about_title="About Me",
            about_content="<p>I'm passionate about technology and constantly learning new things. This website serves as my digital garden where I share insights, projects, and thoughts on various topics.</p><p>From web development to machine learning, I explore different areas of technology and document my journey here.</p>",
            contact_email="aquiles@example.com",
        )
        home_page.save()
        print("✓ Created Home page")
    else:
        home_page = HomePage.objects.first()
        print("✓ Home page already exists")
    
    # Create blog index page
    if not BlogIndexPage.objects.exists():
        blog_index = BlogIndexPage(
            title="Blog",
            slug="blog",
            path="00010002",
            depth=2,
            intro="<p>Thoughts, tutorials, and insights about technology and development.</p>",
            posts_per_page=10,
        )
        blog_index.save()
        print("✓ Created Blog Index page")
    else:
        print("✓ Blog Index page already exists")
    
    # Create project index page
    if not ProjectIndexPage.objects.exists():
        project_index = ProjectIndexPage(
            title="Projects",
            slug="projects",
            path="00010003",
            depth=2,
            intro="<p>A collection of my projects and work.</p>",
            projects_per_page=12,
        )
        project_index.save()
        print("✓ Created Project Index page")
    else:
        print("✓ Project Index page already exists")
    
    # Create contact page
    if not ContactPage.objects.exists():
        contact_page = ContactPage(
            title="Contact",
            slug="contact",
            path="00010004",
            depth=2,
            intro="<p>Get in touch with me for collaborations, questions, or just to say hello.</p>",
            contact_form_title="Get in Touch",
            email="aquiles@example.com",
        )
        contact_page.save()
        print("✓ Created Contact page")
    else:
        print("✓ Contact page already exists")
    
    # Create legal pages
    if not LegalPage.objects.filter(slug="privacy-policy").exists():
        privacy_page = LegalPage(
            title="Privacy Policy",
            slug="privacy-policy",
            path="00010005",
            depth=2,
            content="<h2>Privacy Policy</h2><p>This is a placeholder privacy policy. Please update with your actual privacy policy content.</p>",
        )
        privacy_page.save()
        print("✓ Created Privacy Policy page")
    else:
        print("✓ Privacy Policy page already exists")
    
    if not LegalPage.objects.filter(slug="cookie-policy").exists():
        cookie_page = LegalPage(
            title="Cookie Policy",
            slug="cookie-policy",
            path="00010006",
            depth=2,
            content="<h2>Cookie Policy</h2><p>This is a placeholder cookie policy. Please update with your actual cookie policy content.</p>",
        )
        cookie_page.save()
        print("✓ Created Cookie Policy page")
    else:
        print("✓ Cookie Policy page already exists")
    
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
        print("✓ Created Site Settings")
    else:
        print("✓ Site Settings already exists")
    
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
        print("✓ Created Wagtail Site")
    else:
        print("✓ Wagtail Site already exists")
    
    print("Site structure setup completed successfully!")

if __name__ == "__main__":
    setup_pages()
