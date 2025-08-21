# Performance Optimization

## Database Performance

### Query Optimization
**Django ORM Best Practices:**
```python
# Use select_related for foreign key relationships
blog_posts = BlogPage.objects.select_related('author').all()

# Use prefetch_related for many-to-many and reverse foreign keys
posts = BlogPage.objects.prefetch_related('tags', 'comments').all()

# Combine both for complex relationships
posts = BlogPage.objects.select_related('author').prefetch_related('tags').all()

# Use only() to fetch specific fields
posts = BlogPage.objects.only('title', 'slug', 'published_date').all()

# Use defer() to exclude heavy fields
posts = BlogPage.objects.defer('body', 'content').all()
```

### Database Indexing
**Strategic Index Creation:**
```python
# Model-level indexing
class BlogPage(Page):
    published_date = models.DateTimeField(db_index=True)
    slug = models.SlugField(unique=True, db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['published_date', 'live']),
            models.Index(fields=['title', 'published_date']),
        ]
```

**Common Index Patterns:**
- Single-column indexes for frequently filtered fields
- Composite indexes for multi-field queries
- Unique indexes for slug fields and identifiers
- Partial indexes for conditional queries

### Query Analysis
**Performance Monitoring:**
```python
# Django Debug Toolbar for development
INSTALLED_APPS = [
    'debug_toolbar',
]

# Log slow queries
LOGGING = {
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    }
}

# Use explain() to analyze query plans
queryset = BlogPage.objects.filter(live=True)
print(queryset.explain())
```

## Caching Strategy

### Page Caching
**Full-Page Caching:**
```python
# Cache entire views
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # Cache for 15 minutes
def blog_list(request):
    return render(request, 'blog/list.html', context)
```

### Template Fragment Caching
**Selective Caching:**
```html
<!-- Cache expensive template fragments -->
{% load cache %}
{% cache 300 sidebar request.user.username %}
    <!-- Expensive sidebar content -->
{% endcache %}

{% cache 600 blog_list page.number %}
    <!-- Blog post list -->
{% endcache %}
```

### Low-Level Caching
**Data Caching:**
```python
from django.core.cache import cache

# Cache database queries
def get_popular_posts():
    popular_posts = cache.get('popular_posts')
    if popular_posts is None:
        popular_posts = BlogPage.objects.filter(
            featured=True
        ).select_related('author')[:5]
        cache.set('popular_posts', popular_posts, 300)  # 5 minutes
    return popular_posts

# Cache computed values
def get_post_count():
    count = cache.get('total_post_count')
    if count is None:
        count = BlogPage.objects.filter(live=True).count()
        cache.set('total_post_count', count, 600)  # 10 minutes
    return count
```

### Cache Configuration
**Redis Cache Setup:**
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Cache key versioning
CACHE_MIDDLEWARE_KEY_PREFIX = 'aquiles'
CACHE_MIDDLEWARE_SECONDS = 600
```

## Static File Optimization

### CSS Optimization
**Tailwind CSS Build Process:**
```bash
# Production build with optimization
npm run build:css

# Purge unused CSS
npx tailwindcss -i ./static/src/styles.css -o ./static/css/tailwind.css --minify
```

**PostCSS Configuration:**
```javascript
// postcss.config.mjs
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
    ...(process.env.NODE_ENV === 'production' ? { cssnano: {} } : {})
  }
}
```

### Image Optimization
**Wagtail Image Optimization:**
```python
# Custom image renditions
from wagtail.images.models import Image

# Optimize images on upload
def optimize_image(image_file):
    from PIL import Image as PILImage
    img = PILImage.open(image_file)
    
    # Resize if too large
    if img.width > 2048 or img.height > 2048:
        img.thumbnail((2048, 2048), PILImage.Resampling.LANCZOS)
    
    # Convert to WebP for better compression
    if img.format != 'WebP':
        img = img.convert('RGB')
        img.save(image_file, 'WebP', quality=85, optimize=True)
```

**Responsive Images:**
```html
<!-- Use Wagtail's responsive image tags -->
{% load wagtailimages_tags %}

{% image page.hero_image width-400 as hero_small %}
{% image page.hero_image width-800 as hero_medium %}
{% image page.hero_image width-1200 as hero_large %}

<img src="{{ hero_medium.url }}"
     srcset="{{ hero_small.url }} 400w,
             {{ hero_medium.url }} 800w,
             {{ hero_large.url }} 1200w"
     sizes="(max-width: 768px) 400px,
            (max-width: 1024px) 800px,
            1200px"
     alt="{{ page.hero_image.title }}">
```

### Static File Serving
**WhiteNoise Configuration:**
```python
# Efficient static file serving
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Compression and caching
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True  # Development only
```

## Frontend Performance

### JavaScript Optimization
**Code Splitting and Lazy Loading:**
```javascript
// Lazy load non-critical JavaScript
const loadContactForm = async () => {
    const module = await import('./contact-form.js');
    return module.default;
};

// Load on user interaction
document.getElementById('contact-button').addEventListener('click', async () => {
    const ContactForm = await loadContactForm();
    new ContactForm();
});
```

### Critical CSS
**Above-the-fold Optimization:**
```html
<!-- Inline critical CSS -->
<style>
    /* Critical styles for above-the-fold content */
    .hero { /* styles */ }
    .navigation { /* styles */ }
</style>

<!-- Load full CSS asynchronously -->
<link rel="preload" href="{% static 'css/tailwind.css' %}" as="style" onload="this.onload=null;this.rel='stylesheet'">
```

### Resource Hints
**Browser Optimization:**
```html
<!-- DNS prefetch for external resources -->
<link rel="dns-prefetch" href="//fonts.googleapis.com">
<link rel="dns-prefetch" href="//www.google-analytics.com">

<!-- Preload critical resources -->
<link rel="preload" href="{% static 'fonts/inter.woff2' %}" as="font" type="font/woff2" crossorigin>

<!-- Prefetch likely next pages -->
<link rel="prefetch" href="{% url 'blog:list' %}">
```

## Server Performance

### Application Server Optimization
**Gunicorn Configuration:**
```python
# gunicorn_config.py
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 5
```

### Web Server Configuration
**Nginx Optimization:**
```nginx
# nginx.conf
server {
    listen 80;
    server_name example.com;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json;
    
    # Static file caching
    location /static/ {
        alias /path/to/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Media file caching
    location /media/ {
        alias /path/to/media/;
        expires 30d;
        add_header Cache-Control "public";
    }
    
    # Application proxy
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Wagtail-Specific Optimizations

### Page Query Optimization
**Wagtail Performance Patterns:**
```python
# Optimize page queries
def get_blog_posts(self):
    return self.get_children().live().public().select_related('owner').prefetch_related('tags')

# Use specific() for page querysets
posts = BlogPage.objects.live().specific().select_related('owner')

# Optimize StreamField queries
class BlogPage(Page):
    def get_context(self, request):
        context = super().get_context(request)
        # Prefetch related objects for StreamField blocks
        context['related_posts'] = BlogPage.objects.live().select_related('owner')[:3]
        return context
```

### Search Performance
**Wagtail Search Optimization:**
```python
# Use database search backend for better performance
WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.database',
    }
}

# Optimize search indexing
class BlogPage(Page):
    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.FilterField('published_date'),
        index.FilterField('live'),
    ]
```

## Monitoring & Profiling

### Performance Monitoring
**Application Monitoring:**
```python
# Django performance monitoring
INSTALLED_APPS = [
    'django_extensions',  # For profiling
]

# Custom middleware for timing
class PerformanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time
        
        if duration > 1.0:  # Log slow requests
            logger.warning(f"Slow request: {request.path} took {duration:.2f}s")
        
        return response
```

### Database Monitoring
**Query Performance Tracking:**
```python
# Log slow queries
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'OPTIONS': '-c log_min_duration_statement=1000'  # Log queries > 1s
        }
    }
}
```

### Performance Metrics
**Key Performance Indicators:**
- **Page Load Time** - Target: < 2 seconds
- **Time to First Byte (TTFB)** - Target: < 500ms
- **Database Query Count** - Target: < 20 queries per page
- **Memory Usage** - Monitor and optimize
- **Cache Hit Rate** - Target: > 80%

### Performance Testing
**Load Testing Strategy:**
```bash
# Use locust for load testing
pip install locust

# Create locustfile.py
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def view_homepage(self):
        self.client.get("/")
    
    @task(2)
    def view_blog(self):
        self.client.get("/blog/")
    
    @task(1)
    def search(self):
        self.client.get("/search/?q=django")

# Run load test
locust -f locustfile.py --host=http://localhost:8000
```