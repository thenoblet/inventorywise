from __future__ import absolute_import, unicode_literals
import os
from celery import Celery


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventorywise.settings')

app = Celery('inventorywise')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Discover tasks from all registered apps.
app.autodiscover_tasks()

broker_connection_retry_on_startup = True
