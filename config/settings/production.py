import os
from .base import *
import environ

env = environ.Env()

DEBUG = False
ALLOWED_HOSTS = [env('RAILWAY_STATIC_URL', default='*'), '127.0.0.1', 'localhost']

# Static files layout for cloud hosting
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'