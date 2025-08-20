from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import BlogPage


class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    
    def items(self):
        return BlogPage.objects.live()
    
    def lastmod(self, obj):
        return obj.last_published_at
    
    def location(self, obj):
        return reverse('blog:blog_detail', args=[obj.slug])


class BlogListSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9
    
    def items(self):
        return ['blog:blog_list']
    
    def location(self, obj):
        return reverse(obj)
