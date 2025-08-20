from django.urls import path
from . import views, feeds

app_name = 'blog'

urlpatterns = [
    path('', views.blog_list_view, name='blog_list'),
    path('<slug:slug>/', views.blog_detail_view, name='blog_detail'),
    path('tag/<str:tag_name>/', views.blog_tag_view, name='blog_tag'),
    path('feed/', feeds.BlogFeed(), name='blog_feed'),
]
