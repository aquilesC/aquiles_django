from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.core.paginator import Paginator
from wagtail.models import Page
from pages.models import HomePage
from .models import BlogPage, BlogPageTag
from taggit.models import Tag
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.template import Context, Template
from wagtail.models import Site
from wagtail.test.utils import WagtailTestUtils
from .models import BlogPage
from .blocks import BlogBodyStreamBlock


class BlogModelsTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.root_page = Page.objects.get(id=1)
        
        # Create home page
        self.home_page = HomePage(
            title="Test Home",
            slug="test-home",
            about_content="<p>Test about content</p>"
        )
        self.root_page.add_child(instance=self.home_page)
        self.home_page.save_revision().publish()
        
        # Create test tags
        self.tag1 = Tag.objects.create(name="python")
        self.tag2 = Tag.objects.create(name="django")

    def test_blog_page_creation(self):
        """Test BlogPage model creation"""
        blog_post = BlogPage(
            title="Test Blog Post",
            slug="test-blog",
            intro="Test introduction",
            body="<p>Test body content</p>",
            is_members_only=False
        )
        self.home_page.add_child(instance=blog_post)
        blog_post.save_revision().publish()
        
        self.assertEqual(blog_post.title, "Test Blog Post")
        self.assertEqual(blog_post.slug, "test-blog")
        self.assertEqual(blog_post.intro, "Test introduction")
        self.assertEqual(blog_post.body, "<p>Test body content</p>")
        self.assertFalse(blog_post.is_members_only)
        self.assertTrue(blog_post.live)

    def test_blog_page_with_tags(self):
        """Test BlogPage with tags"""
        blog_post = BlogPage(
            title="Test Blog Post",
            slug="test-blog",
            intro="Test introduction",
            body="<p>Test body content</p>",
            is_members_only=False
        )
        self.home_page.add_child(instance=blog_post)
        blog_post.save_revision().publish()
        
        # Add tags
        blog_post.tags.add(self.tag1, self.tag2)
        
        self.assertEqual(blog_post.tags.count(), 2)
        self.assertTrue(blog_post.tags.filter(name="python").exists())
        self.assertTrue(blog_post.tags.filter(name="django").exists())

    def test_blog_page_members_only(self):
        """Test BlogPage members-only functionality"""
        blog_post = BlogPage(
            title="Members Only Post",
            slug="members-post",
            intro="Members only introduction",
            body="<p>Members only content</p>",
            is_members_only=True
        )
        self.home_page.add_child(instance=blog_post)
        blog_post.save_revision().publish()
        
        self.assertTrue(blog_post.is_members_only)


class BlogViewsTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()
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
            is_members_only=False
        )
        self.home_page.add_child(instance=self.blog_post2)
        self.blog_post2.save_revision().publish()
        
        # Create test tags
        self.tag1 = Tag.objects.create(name="python")
        self.tag2 = Tag.objects.create(name="django")
        self.blog_post1.tags.add(self.tag1)
        self.blog_post2.tags.add(self.tag2)

    def test_blog_list_view(self):
        """Test blog listing view"""
        response = self.client.get(reverse('blog:blog_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blog_list.html')
        self.assertContains(response, 'Test Blog Post 1')
        self.assertContains(response, 'Test Blog Post 2')
        self.assertContains(response, 'python')
        self.assertContains(response, 'django')

    def test_blog_list_view_pagination(self):
        """Test blog listing pagination"""
        # Create more posts to test pagination
        for i in range(15):
            post = BlogPage(
                title=f"Test Post {i+3}",
                slug=f"test-post-{i+3}",
                intro=f"Intro {i+3}",
                body=f"<p>Body {i+3}</p>",
                is_members_only=False
            )
            self.home_page.add_child(instance=post)
            post.save_revision().publish()
        
        response = self.client.get(reverse('blog:blog_list'))
        self.assertEqual(response.status_code, 200)
        
        # Check pagination context
        self.assertIn('blog_posts', response.context)
        self.assertEqual(len(response.context['blog_posts']), 10)  # First page

    def test_blog_list_view_tag_filtering(self):
        """Test blog listing with tag filtering"""
        response = self.client.get(f"{reverse('blog:blog_list')}?tag=python")
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Blog Post 1')
        self.assertNotContains(response, 'Test Blog Post 2')

    def test_blog_list_view_search(self):
        """Test blog listing with search"""
        response = self.client.get(f"{reverse('blog:blog_list')}?search=Post 1")
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Blog Post 1')
        self.assertNotContains(response, 'Test Blog Post 2')

    def test_blog_detail_view(self):
        """Test blog detail view"""
        response = self.client.get(reverse('blog:blog_detail', args=['test-blog-1']))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blog_detail.html')
        self.assertContains(response, 'Test Blog Post 1')
        self.assertContains(response, 'Test intro 1')
        self.assertContains(response, 'Test body 1')

    def test_blog_detail_view_nonexistent(self):
        """Test blog detail view with nonexistent slug"""
        response = self.client.get(reverse('blog:blog_detail', args=['nonexistent']))
        
        self.assertEqual(response.status_code, 404)

    def test_blog_tag_view(self):
        """Test blog tag view"""
        response = self.client.get(reverse('blog:blog_tag', args=['python']))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blog_tag.html')
        self.assertContains(response, 'Posts tagged with "python"')
        self.assertContains(response, 'Test Blog Post 1')
        self.assertNotContains(response, 'Test Blog Post 2')

    def test_blog_tag_view_empty(self):
        """Test blog tag view with no posts"""
        response = self.client.get(reverse('blog:blog_tag', args=['nonexistent']))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No posts found with tag "nonexistent"')


class BlogURLsTestCase(TestCase):
    def test_blog_list_url(self):
        """Test blog list URL pattern"""
        url = reverse('blog:blog_list')
        self.assertEqual(url, '/blog/')

    def test_blog_detail_url(self):
        """Test blog detail URL pattern"""
        url = reverse('blog:blog_detail', args=['test-slug'])
        self.assertEqual(url, '/blog/test-slug/')

    def test_blog_tag_url(self):
        """Test blog tag URL pattern"""
        url = reverse('blog:blog_tag', args=['python'])
        self.assertEqual(url, '/blog/tag/python/')

    def test_blog_feed_url(self):
        """Test blog RSS feed URL pattern"""
        url = reverse('blog:blog_feed')
        self.assertEqual(url, '/blog/feed/')


class BlogTemplateTagsTest(TestCase, WagtailTestUtils):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Get or create a test site
        self.site, created = Site.objects.get_or_create(
            hostname='localhost',
            port=80,
            defaults={
                'is_default_site': True,
                'root_page_id': 1
            }
        )
        
        # Create a test blog page
        self.blog_page = BlogPage(
            title="Test Blog Post",
            slug="test-blog-post",
            intro="This is a test blog post",
            body=BlogBodyStreamBlock().to_python([
                {
                    'type': 'heading',
                    'value': {
                        'text': 'First Heading',
                        'level': 'h2',
                        'anchor': 'first-heading'
                    }
                },
                {
                    'type': 'paragraph',
                    'value': '<p>This is a test paragraph.</p>'
                },
                {
                    'type': 'heading',
                    'value': {
                        'text': 'Second Heading',
                        'level': 'h3',
                        'anchor': 'second-heading'
                    }
                }
            ])
        )
        self.blog_page.save()

    def test_extract_headings_filter(self):
        """Test that headings are correctly extracted from StreamField content"""
        template = Template('{% load blog_tags %}{{ page.body|extract_headings|length }}')
        context = Context({'page': self.blog_page})
        result = template.render(context)
        self.assertEqual(result, '2')

    def test_render_toc_filter(self):
        """Test that table of contents is correctly rendered"""
        headings = self.blog_page.body|extract_headings
        template = Template('{% load blog_tags %}{{ headings|render_toc }}')
        context = Context({'headings': headings})
        result = template.render(context)
        
        # Check that the TOC contains the expected headings
        self.assertIn('First Heading', result)
        self.assertIn('Second Heading', result)
        self.assertIn('first-heading', result)
        self.assertIn('second-heading', result)

    def test_blog_body_template_rendering(self):
        """Test that the blog body template renders correctly"""
        template = Template('{% load wagtailimages_tags wagtailcore_tags %}{% include "blog/blog_body.html" with value=page.body %}')
        context = Context({'page': self.blog_page})
        result = template.render(context)
        
        # Check that the content is rendered
        self.assertIn('First Heading', result)
        self.assertIn('This is a test paragraph', result)
        self.assertIn('Second Heading', result)
