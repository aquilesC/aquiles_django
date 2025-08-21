# Technical Architecture

## Tech Stack

### Backend
- **Django 5.2+** - Web framework with modern Python practices
- **Wagtail 7.1+** - Content management system
- **Python 3.11+** - Programming language
- **PostgreSQL** - Production database
- **SQLite** - Development database
- **WhiteNoise** - Static file serving

### Frontend
- **Tailwind CSS v4** - Utility-first CSS framework
- **PostCSS** - CSS processing
- **JavaScript (ES6+)** - Client-side scripting
- **HTML5** - Semantic markup

### Development Tools
- **npm** - Package management for frontend dependencies
- **pip** - Python package management
- **Git** - Version control

### Deployment
- **DigitalOcean** - Cloud hosting platform
- **Gunicorn** - WSGI HTTP Server
- **Nginx** - Reverse proxy and static file serving
- **Certbot** - SSL certificate management

## System Architecture

### MVT Pattern (Model-View-Template)
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Models    │◄───┤    Views    │◄───┤  Templates  │
│ (Database)  │    │ (Business   │    │    (UI)     │
│             │    │  Logic)     │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Application Structure
```
┌─────────────────┐
│   Django Apps   │
├─────────────────┤
│ core/           │ ◄── Home views and core functionality
│ blog/           │ ◄── Blog functionality with Wagtail
│ pages/          │ ◄── Wagtail page models and templates
│ accounts/       │ ◄── User authentication and management
└─────────────────┘
```

### Data Flow
```
User Request → URL Router → View → Model → Database
                    ↓
            Template ← Context Data ← View Response
```

## Database Design

### User Management
- Django's built-in User model
- Custom user groups for access control
- Member-only content gating

### Content Management (Wagtail)
- Page hierarchy with Wagtail's Page model
- StreamField for flexible content blocks
- Search indexing for content discovery
- Tagging system for organization

## Static Files Architecture

### Development
```
static/src/styles.css → PostCSS → static/css/tailwind.css
```

### Production
```
Static Files → collectstatic → STATIC_ROOT → WhiteNoise → CDN
```

## Security Architecture

- **Authentication**: Django's built-in system
- **Authorization**: Group-based permissions
- **CSRF Protection**: Django middleware
- **HTTPS**: SSL/TLS encryption in production
- **Environment Variables**: Sensitive configuration
- **Input Validation**: Django forms and models