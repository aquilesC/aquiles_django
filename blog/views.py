from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from wagtail.models import Page
from .models import BlogPage


def blog_list_view(request):
    """Blog listing view with pagination and filtering"""
    # Get all live blog posts
    blog_posts = BlogPage.objects.live().order_by('-first_published_at')
    
    # Tag filtering
    tag = request.GET.get('tag')
    if tag:
        blog_posts = blog_posts.filter(tags__name=tag)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        blog_posts = blog_posts.filter(
            Q(title__icontains=search_query) |
            Q(intro__icontains=search_query) |
            Q(body__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(blog_posts, 10)  # 10 posts per page
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    # Get all tags for filtering
    all_tags = BlogPage.objects.live().values_list('tags__name', flat=True).distinct()
    
    context = {
        'blog_posts': posts,
        'all_tags': all_tags,
        'current_tag': tag,
        'search_query': search_query,
    }
    
    return render(request, 'blog/blog_list.html', context)


def blog_detail_view(request, slug):
    """Individual blog post detail view"""
    post = get_object_or_404(BlogPage, slug=slug, live=True)
    
    # Get related posts (same tags)
    related_posts = BlogPage.objects.live().filter(
        tags__in=post.tags.all()
    ).exclude(id=post.id).distinct()[:3]
    
    context = {
        'post': post,
        'related_posts': related_posts,
    }
    
    return render(request, 'blog/blog_detail.html', context)


def blog_tag_view(request, tag_name):
    """Blog posts filtered by tag"""
    blog_posts = BlogPage.objects.live().filter(
        tags__name=tag_name
    ).order_by('-first_published_at')
    
    # Pagination
    paginator = Paginator(blog_posts, 10)
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    context = {
        'blog_posts': posts,
        'tag_name': tag_name,
    }
    
    return render(request, 'blog/blog_tag.html', context)
