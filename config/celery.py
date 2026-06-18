import os
from celery import Celery

# 1. Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

app = Celery('agricare')

# 2. Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# This tells Celery to look inside your settings files for any keys starting with 'CELERY_'
app.config_from_object('django.conf:settings', namespace='CELERY')

# 3. Load task modules from all registered Django apps.
# Force Celery to explicitly import your temporary config.tasks file
app.conf.imports = ('config.tasks',)