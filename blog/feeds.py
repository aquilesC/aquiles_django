from django.contrib.syndication.views import Feed
from django.urls import reverse_lazy
from .models import BlogPage


class BlogFeed(Feed):
    title = "Aquiles' Blog"
    link = reverse_lazy('blog:blog_list')
    description = "Latest blog posts about technology, development, and insights"
    
    def items(self):
        return BlogPage.objects.live().order_by('-first_published_at')[:20]
    
    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        return item.intro
    
    def item_link(self, item):
        return reverse_lazy('blog:blog_detail', args=[item.slug])
    
    def item_pubdate(self, item):
        return item.first_published_at
    
    def item_updateddate(self, item):
        return item.last_published_at
    
    def item_categories(self, item):
        return [tag.name for tag in item.tags.all()]
