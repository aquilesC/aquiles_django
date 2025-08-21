from django import template
from blog.models import BlogPage

register = template.Library()


@register.simple_tag
def get_blog_posts(block_value):
    """Get blog posts based on block configuration"""
    posts = BlogPage.objects.live().public()
    
    # Filter by tag if specified
    if block_value.get('tag_filter'):
        posts = posts.filter(tags__name__icontains=block_value['tag_filter'])
    
    # Filter featured only if specified
    if block_value.get('show_featured_only'):
        # This would require adding a featured field to BlogPage
        # For now, we'll just return all posts
        pass
    
    # Order by publication date
    posts = posts.order_by('-first_published_at')
    
    # Limit the number of posts
    post_count = block_value.get('post_count', 3)
    posts = posts[:post_count]
    
    return posts