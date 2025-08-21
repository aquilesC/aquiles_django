# Development Guidelines

## Code Quality Standards

### Python/Django Standards
- **PEP 8 Compliance** - Follow Python's official style guide
- **Descriptive Naming** - Use clear, meaningful variable and function names
- **Type Hints** - Use Python type annotations where beneficial
- **Docstrings** - Document classes and complex functions
- **Import Organization** - Group imports: standard library, third-party, local

### Django Best Practices
- **Class-Based Views (CBVs)** - For complex views with multiple HTTP methods
- **Function-Based Views (FBVs)** - For simple, single-purpose views
- **Django ORM** - Use `select_related` and `prefetch_related` for optimization
- **Model Methods** - Keep business logic in models when appropriate
- **Form Classes** - Use Django forms for data validation and rendering

### Wagtail Guidelines
- **Page Models** - Inherit from appropriate Wagtail page types
- **StreamField** - Use for flexible, editor-friendly content blocks
- **Search Indexing** - Implement proper search functionality
- **Admin Interface** - Customize panels for better editor experience
- **Content Types** - Create specific page types: HomePage, BlogPage, ProjectPage

## Frontend Standards

### Tailwind CSS
- **Utility-First** - Use utility classes over custom CSS
- **Responsive Design** - Mobile-first approach with responsive utilities
- **Component Classes** - Use `@apply` for reusable component styles
- **Design System** - Follow `visual_style.md` for consistency

### CSS Organization
```css
/* Source: static/src/styles.css */
@import 'tailwindcss/base';
@import 'tailwindcss/components';
@import 'tailwindcss/utilities';

/* Custom components using @apply */
.btn-primary {
  @apply px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600;
}
```

### Build Process
```bash
npm run build:css    # Production build
npm run watch:css    # Development watch mode
```

## Project Organization

### Modular Architecture
- **Separation of Concerns** - Each Django app has a single responsibility
- **Reusability** - Design components for reuse across the project
- **Clear Boundaries** - Well-defined interfaces between apps

### File Naming Conventions
- **Python Files** - `snake_case.py`
- **Templates** - `snake_case.html`
- **Static Files** - `kebab-case.css`, `camelCase.js`
- **Media Files** - Descriptive names with proper extensions

## Testing Standards

### Unit Testing
- **Model Tests** - Test model methods and validation
- **View Tests** - Test HTTP responses and business logic
- **Form Tests** - Test form validation and processing
- **Template Tests** - Test template rendering and context

### Integration Testing
- **Wagtail Pages** - Test page functionality and admin interface
- **User Authentication** - Test login/logout and permissions
- **Content Management** - Test CRUD operations

## Error Handling

### User-Friendly Errors
- **Custom Error Pages** - 404, 500, 403 templates
- **Form Validation** - Clear, actionable error messages
- **Logging** - Appropriate log levels for debugging

### Exception Handling
```python
try:
    # Risky operation
    result = perform_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    # Handle gracefully
```

## Performance Guidelines

### Database Optimization
- **Query Optimization** - Use `select_related()` and `prefetch_related()`
- **Database Indexing** - Add indexes for frequently queried fields
- **Lazy Loading** - Avoid N+1 queries

### Caching Strategy
- **Template Caching** - Cache expensive template fragments
- **Database Caching** - Cache frequent database queries
- **Static Files** - Use browser caching headers

## Accessibility Standards

### WCAG Compliance
- **Semantic HTML** - Use proper HTML5 semantic elements
- **Alt Text** - Descriptive alt attributes for images
- **Keyboard Navigation** - Ensure all interactive elements are keyboard accessible
- **Color Contrast** - Meet WCAG AA contrast requirements

### Screen Reader Support
- **ARIA Labels** - Use appropriate ARIA attributes
- **Focus Management** - Proper focus indicators and management
- **Skip Links** - Provide skip navigation links