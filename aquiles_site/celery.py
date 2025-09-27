import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aquiles_site.settings')

app = Celery('aquiles_site')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
