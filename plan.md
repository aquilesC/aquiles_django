## Plan

### Phase 0 — Project Setup
- [x] Create virtual environment and activate it
- [x] Install Django, Wagtail, and WhiteNoise
- [x] Create Django project (`aquiles_site`)
- [x] Create Django apps: `core`, `blog`, `accounts`, `pages`
- [x] Add Wagtail to `INSTALLED_APPS` in settings
- [x] Configure `STATIC_ROOT` and `MEDIA_ROOT` in settings
- [x] Configure WhiteNoise middleware in settings
- [x] Run initial migrations
- [x] Create superuser account
- [x] Test that Django admin and Wagtail admin are accessible

### Phase 1 — CMS and Content Models
- [x] Create `HomePage` model (hero section, featured content)
- [x] Create `BlogIndexPage` model (listing page for blog posts)
- [x] Create `BlogPage` model (individual blog post with rich content, tags, publish date)
- [x] Create `ProjectIndexPage` model (listing page for projects)
- [x] Create `ProjectPage` model (individual project with title, summary, tech stack, links)
- [x] Create `ContactPage` model (social links, contact form)
- [x] Create `LegalPage` model (privacy policy, cookie policy)
- [x] Set up image and document libraries in Wagtail
- [x] Configure tagging system for blog posts
- [x] Set up search functionality
- [x] Create and run migrations for all page models
- [x] Test page creation in Wagtail admin

### Phase 2 — Authentication and Membership
- [ ] Set up Django's built-in authentication system
- [ ] Create user registration form and view
- [ ] Create login/logout views
- [ ] Create "members" group with appropriate permissions
- [ ] Add permission checks to gated content
- [ ] Create user profile model (optional)
- [ ] Test user registration and login flow
- [ ] Test access control for exclusive content

### Phase 3 — Templates and Tailwind CSS
- [x] Initialize npm project
- [x] Install Tailwind CSS, PostCSS, and Autoprefixer
- [x] Configure Tailwind CSS with PostCSS
- [x] Set up build process for CSS compilation
- [x] Create base template (`base.html`)
- [x] Create navigation partial template
- [x] Create footer partial template
- [x] Create homepage template
- [x] Create blog listing template
- [x] Create blog detail template
- [x] Create project listing template
- [x] Create project detail template
- [x] Create contact page template
- [x] Create legal pages template
- [x] Style templates following `visual_style.md` guidelines
- [x] Test responsive design on different screen sizes

### Phase 4 — Blog and Content Flow
- [ ] Implement blog listing with pagination
- [ ] Implement blog detail page
- [ ] Add tag filtering functionality
- [ ] Create RSS feed for blog posts
- [ ] Add OpenGraph meta tags for social sharing
- [ ] Add Twitter Card meta tags
- [ ] Implement search functionality for blog posts
- [ ] Add "related posts" feature
- [ ] Test blog functionality end-to-end

### Phase 5 — Testing and Quality Assurance
- [ ] Write unit tests for all page models
- [ ] Write unit tests for authentication views
- [ ] Write unit tests for blog functionality
- [ ] Write integration tests for user flows
- [ ] Set up GitHub Actions for CI/CD
- [ ] Configure automated testing in CI
- [ ] Add code linting (flake8, black)
- [ ] Add pre-commit hooks
- [ ] Test all functionality locally
- [ ] Fix any bugs or issues found during testing

### Phase 6 — Performance and Security
- [ ] Optimize database queries with `select_related` and `prefetch_related`
- [ ] Enable WhiteNoise for static file serving
- [ ] Configure security headers
- [ ] Set up production security settings (`SECURE_*` variables)
- [ ] Implement template caching where beneficial
- [ ] Optimize image handling and compression
- [ ] Add database indexing for better performance
- [ ] Configure logging
- [ ] Test performance under load
- [ ] Security audit and penetration testing

### Phase 7 — Deployment to DigitalOcean
- [ ] Choose deployment method (Droplet vs App Platform)
- [ ] Set up production environment variables
- [ ] Configure production database
- [ ] Set up Gunicorn (if using Droplet)
- [ ] Configure Nginx (if using Droplet)
- [ ] Set up SSL/HTTPS certificate
- [ ] Configure domain and DNS settings
- [ ] Run production migrations
- [ ] Create production superuser
- [ ] Collect static files
- [ ] Test production deployment
- [ ] Set up monitoring and logging
- [ ] Configure backups
- [ ] Document deployment process

### Milestones
- [ ] **M1**: Project boots locally with Wagtail admin and Tailwind compiled
- [ ] **M2**: Blog + Projects models and templates live; public pages render
- [ ] **M3**: Auth + members-only content working
- [ ] **M4**: Deployed on DigitalOcean with HTTPS and basic CI

### Commands Reference
```bash
# Phase 0 Setup
python -m venv .venv && source .venv/bin/activate
pip install "Django>=5.0" "wagtail>=6.0" whitenoise
django-admin startproject aquiles_site .
python manage.py startapp core
python manage.py startapp blog
python manage.py startapp accounts
python manage.py startapp pages
python manage.py migrate
python manage.py createsuperuser --username aquiles --email you@example.com

# Phase 3 Tailwind Setup
npm init -y
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```