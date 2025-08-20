from django.test import TestCase
from wagtail.models import Page, Site
from .models import HomePage, BlogIndexPage, ProjectIndexPage, ContactPage, LegalPage, SiteSettings


class PagesModelsTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.root_page = Page.objects.get(id=1)

    def test_home_page_creation(self):
        """Test HomePage model creation"""
        home_page = HomePage(
            title="Test Home",
            slug="test-home",
            about_content="<p>Test about content</p>"
        )
        self.root_page.add_child(instance=home_page)
        home_page.save_revision().publish()
        
        self.assertEqual(home_page.title, "Test Home")
        self.assertEqual(home_page.slug, "test-home")
        self.assertEqual(home_page.intro, "Test introduction")
        self.assertEqual(home_page.about_content, "<p>Test about content</p>")
        self.assertTrue(home_page.live)

    def test_blog_index_page_creation(self):
        """Test BlogIndexPage model creation"""
        blog_index = BlogIndexPage(
            title="Blog",
            slug="blog",
            intro="<p>Welcome to our blog</p>"
        )
        self.root_page.add_child(instance=blog_index)
        blog_index.save_revision().publish()
        
        self.assertEqual(blog_index.title, "Blog")
        self.assertEqual(blog_index.slug, "blog")
        self.assertEqual(blog_index.intro, "<p>Welcome to our blog</p>")
        self.assertTrue(blog_index.live)

    def test_project_index_page_creation(self):
        """Test ProjectIndexPage model creation"""
        project_index = ProjectIndexPage(
            title="Projects",
            slug="projects",
            intro="<p>Check out our projects</p>"
        )
        self.root_page.add_child(instance=project_index)
        project_index.save_revision().publish()
        
        self.assertEqual(project_index.title, "Projects")
        self.assertEqual(project_index.slug, "projects")
        self.assertEqual(project_index.intro, "<p>Check out our projects</p>")
        self.assertTrue(project_index.live)

    def test_contact_page_creation(self):
        """Test ContactPage model creation"""
        contact_page = ContactPage(
            title="Contact",
            slug="contact",
            intro="<p>Get in touch</p>"
        )
        self.root_page.add_child(instance=contact_page)
        contact_page.save_revision().publish()
        
        self.assertEqual(contact_page.title, "Contact")
        self.assertEqual(contact_page.slug, "contact")
        self.assertEqual(contact_page.intro, "<p>Get in touch</p>")
        self.assertEqual(contact_page.contact_info, "<p>Email: test@example.com</p>")
        self.assertTrue(contact_page.live)

    def test_legal_page_creation(self):
        """Test LegalPage model creation"""
        legal_page = LegalPage(
            title="Privacy Policy",
            slug="privacy-policy",
            content="<p>This is our privacy policy</p>"
        )
        self.root_page.add_child(instance=legal_page)
        legal_page.save_revision().publish()
        
        self.assertEqual(legal_page.title, "Privacy Policy")
        self.assertEqual(legal_page.slug, "privacy-policy")
        self.assertEqual(legal_page.content, "<p>This is our privacy policy</p>")
        self.assertTrue(legal_page.live)
        # last_updated should be auto-set
        self.assertIsNotNone(legal_page.last_updated)

    def test_site_settings_creation(self):
        """Test SiteSettings snippet creation"""
        site_settings = SiteSettings.objects.create(
            site_name="Test Site",
            site_description="A test website"
        )
        
        self.assertEqual(site_settings.site_name, "Test Site")
        self.assertEqual(site_settings.site_description, "A test website")


class PagesAdminTestCase(TestCase):
    def test_home_page_admin_panels(self):
        """Test HomePage admin panel configuration"""
        home_page = HomePage()
        
        # Check that content_panels exist
        self.assertTrue(len(home_page.content_panels) > 0)

    def test_blog_index_page_admin_panels(self):
        """Test BlogIndexPage admin panel configuration"""
        blog_index = BlogIndexPage()
        
        self.assertTrue(len(blog_index.content_panels) > 0)

    def test_project_index_page_admin_panels(self):
        """Test ProjectIndexPage admin panel configuration"""
        project_index = ProjectIndexPage()
        
        self.assertTrue(len(project_index.content_panels) > 0)

    def test_contact_page_admin_panels(self):
        """Test ContactPage admin panel configuration"""
        contact_page = ContactPage()
        
        self.assertTrue(len(contact_page.content_panels) > 0)

    def test_legal_page_admin_panels(self):
        """Test LegalPage admin panel configuration"""
        legal_page = LegalPage()
        
        self.assertTrue(len(legal_page.content_panels) > 0)


class PagesURLsTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.root_page = Page.objects.get(id=1)
    
    def test_home_page_url(self):
        """Test HomePage URL generation"""
        home_page = HomePage(
            title="Test Home",
            slug="test-home"
        )
        self.root_page.add_child(instance=home_page)
        home_page.save_revision().publish()
        
        # Test that the page has a proper URL
        self.assertIsNotNone(home_page.url)

    def test_blog_index_page_url(self):
        """Test BlogIndexPage URL generation"""
        blog_index = BlogIndexPage(
            title="Blog",
            slug="blog"
        )
        self.root_page.add_child(instance=blog_index)
        blog_index.save_revision().publish()
        
        self.assertIsNotNone(blog_index.url)

    def test_project_index_page_url(self):
        """Test ProjectIndexPage URL generation"""
        project_index = ProjectIndexPage(
            title="Projects",
            slug="projects"
        )
        self.root_page.add_child(instance=project_index)
        project_index.save_revision().publish()
        
        self.assertIsNotNone(project_index.url)
