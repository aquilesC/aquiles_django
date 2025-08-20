from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from blog.models import BlogPage
from pages.models import HomePage
from wagtail.models import Site, Page


class CoreViewsTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create members group
        self.members_group = Group.objects.create(name='members')
        
        # Create test client
        self.client = Client()
        
        # Set up Wagtail site structure
        self.root_page = Page.objects.get(id=1)
        
        # Create home page
        self.home_page = HomePage(
            title="Test Home",
            slug="test-home",
            about_content="<p>Test about content</p>"
        )
        self.root_page.add_child(instance=self.home_page)
        self.home_page.save_revision().publish()
        
        # Create test blog posts
        self.blog_post1 = BlogPage(
            title="Test Blog Post 1",
            slug="test-blog-1",
            intro="Test intro 1",
            body="<p>Test body 1</p>",
            is_members_only=False
        )
        self.home_page.add_child(instance=self.blog_post1)
        self.blog_post1.save_revision().publish()
        
        self.blog_post2 = BlogPage(
            title="Test Blog Post 2",
            slug="test-blog-2",
            intro="Test intro 2",
            body="<p>Test body 2</p>",
            is_members_only=True
        )
        self.home_page.add_child(instance=self.blog_post2)
        self.blog_post2.save_revision().publish()

    def test_home_view_anonymous_user(self):
        """Test home view for anonymous users"""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')
        self.assertContains(response, 'Welcome to Aquiles')
        self.assertContains(response, 'Join the Community')
        self.assertNotContains(response, 'Welcome back')

    def test_home_view_authenticated_user(self):
        """Test home view for authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome back, testuser')
        self.assertContains(response, 'You\'re logged in!')

    def test_home_view_member_user(self):
        """Test home view for member users"""
        self.user.groups.add(self.members_group)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You have access to exclusive member content')
        self.assertContains(response, 'View Exclusive Content')

    def test_home_view_recent_posts(self):
        """Test that recent blog posts are displayed on home page"""
        response = self.client.get(reverse('core:home'))
        self.assertContains(response, 'Test Blog Post 1')
        self.assertContains(response, 'Test Blog Post 2')

    def test_members_only_view_anonymous_user(self):
        """Test members-only view access for anonymous users"""
        response = self.client.get(reverse('core:members_only'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('core:members_only')}")

    def test_members_only_view_authenticated_user(self):
        """Test members-only view access for authenticated non-member users"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:members_only'))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_members_only_view_member_user(self):
        """Test members-only view access for member users"""
        self.user.groups.add(self.members_group)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:members_only'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This is exclusive content for members only!')


class CoreModelsTestCase(TestCase):
    def test_home_page_creation(self):
        """Test HomePage model creation"""
        root_page = Page.objects.get(id=1)
        home_page = HomePage(
            title="Test Home",
            slug="test-home",
            about_content="<p>Test about content</p>"
        )
        root_page.add_child(instance=home_page)
        home_page.save_revision().publish()
        
        self.assertEqual(home_page.title, "Test Home")
        self.assertEqual(home_page.slug, "test-home")
        self.assertEqual(home_page.about_content, "<p>Test about content</p>")
        self.assertTrue(home_page.live)
