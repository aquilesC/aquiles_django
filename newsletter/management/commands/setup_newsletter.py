from django.core.management.base import BaseCommand
from newsletter.models import EmailTemplate, SubscriptionList


class Command(BaseCommand):
    help = 'Set up basic newsletter templates and subscription list'

    def handle(self, *args, **options):
        self.stdout.write('Setting up basic newsletter templates...')
        
        # Create a basic newsletter list if it doesn't exist
        newsletter_list, created = SubscriptionList.objects.get_or_create(
            slug='newsletter',
            defaults={
                'name': 'Main Newsletter',
                'description': 'Our main newsletter with updates and news',
                'is_public': True,
                'double_opt_in': True
            }
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created subscription list: {newsletter_list.name}')
            )
        else:
            self.stdout.write(f'Subscription list already exists: {newsletter_list.name}')

        # Create basic email templates
        templates = [
            {
                'name': 'Welcome Email',
                'subject_template': 'Welcome to {{ list.name }}!',
                'preview_text': 'Thank you for subscribing to our newsletter',
                'html_body': '''<h2>Welcome, {{ subscriber.first_name|default:"there" }}!</h2>
<p>Thank you for subscribing to <strong>{{ list.name }}</strong>.</p>
<p>We're excited to have you on board and look forward to sharing great content with you.</p>
<p>Best regards,<br>The {{ site_name }} Team</p>
<p><a href="{{ unsubscribe_url }}">Unsubscribe</a></p>''',
                'text_body': '''Welcome, {{ subscriber.first_name|default:"there" }}!

Thank you for subscribing to {{ list.name }}.

We're excited to have you on board and look forward to sharing great content with you.

Best regards,
The {{ site_name }} Team

Unsubscribe: {{ unsubscribe_url }}'''
            },
            {
                'name': 'Newsletter Template',
                'subject_template': '{{ list.name }} - Weekly Update',
                'preview_text': 'Your weekly newsletter with the latest news and updates',
                'html_body': '''<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <header style="background-color: #2c3e50; color: white; padding: 20px; text-align: center;">
        <h1>{{ list.name }}</h1>
    </header>
    
    <main style="padding: 20px;">
        <h2>Hello {{ subscriber.first_name|default:"there" }}!</h2>
        
        <p>Here's what's new this week:</p>
        
        <div style="background-color: #f8f9fa; padding: 15px; margin: 20px 0; border-left: 4px solid #3498db;">
            <h3>Featured Content</h3>
            <p>Add your featured content here...</p>
        </div>
        
        <div style="background-color: #f8f9fa; padding: 15px; margin: 20px 0; border-left: 4px solid #e74c3c;">
            <h3>Important Updates</h3>
            <p>Add your important updates here...</p>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="#" style="background-color: #3498db; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px;">Read More</a>
        </div>
    </main>
    
    <footer style="background-color: #95a5a6; color: white; padding: 20px; text-align: center; font-size: 12px;">
        <p>{{ site_name }}</p>
        <p><a href="{{ unsubscribe_url }}" style="color: white;">Unsubscribe</a> | <a href="#" style="color: white;">Contact Us</a></p>
    </footer>
</div>''',
                'text_body': '''{{ list.name }} - Weekly Update

Hello {{ subscriber.first_name|default:"there" }}!

Here's what's new this week:

FEATURED CONTENT
Add your featured content here...

IMPORTANT UPDATES  
Add your important updates here...

Read More: [Link to your content]

---
{{ site_name }}
Unsubscribe: {{ unsubscribe_url }}
Contact Us: [Your contact info]'''
            },
            {
                'name': 'Confirmation Email',
                'subject_template': 'Please confirm your subscription to {{ list.name }}',
                'preview_text': 'Click the link to confirm your newsletter subscription',
                'html_body': '''<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <h2>Confirm Your Subscription</h2>
    
    <p>Hello!</p>
    
    <p>Thank you for subscribing to <strong>{{ list.name }}</strong>.</p>
    
    <p>To complete your subscription and start receiving our newsletter, please click the confirmation link below:</p>
    
    <div style="text-align: center; margin: 30px 0;">
        <a href="{{ confirm_url }}" style="background-color: #27ae60; color: white; padding: 15px 30px; text-decoration: none; border-radius: 4px; display: inline-block;">Confirm Subscription</a>
    </div>
    
    <p>If you didn't subscribe to this newsletter, you can safely ignore this email.</p>
    
    <p>Best regards,<br>The {{ site_name }} Team</p>
    
    <hr>
    <p style="font-size: 12px; color: #666;">
        <a href="{{ unsubscribe_url }}">Unsubscribe</a>
    </p>
</div>''',
                'text_body': '''Confirm Your Subscription

Hello!

Thank you for subscribing to {{ list.name }}.

To complete your subscription and start receiving our newsletter, please click the confirmation link below:

{{ confirm_url }}

If you didn't subscribe to this newsletter, you can safely ignore this email.

Best regards,
The {{ site_name }} Team

Unsubscribe: {{ unsubscribe_url }}'''
            }
        ]

        created_count = 0
        for template_data in templates:
            template, created = EmailTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created template: {template.name}')
                )
            else:
                self.stdout.write(f'Template already exists: {template.name}')

        self.stdout.write(
            self.style.SUCCESS(f'\nCreated {created_count} new templates.')
        )
        self.stdout.write(
            self.style.SUCCESS('Basic newsletter setup complete!')
        )
        self.stdout.write('\nYou can now:')
        self.stdout.write('1. Go to /admin/ and look for the Newsletter section')
        self.stdout.write('2. Create campaigns using the templates')
        self.stdout.write('3. Add subscribers to your lists')
        self.stdout.write('4. Start sending newsletters!')
