import os
from .base import *
import environ
import dj_database_url

env = environ.Env()

DEBUG = False

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600
    )
}

ALLOWED_HOSTS = [
    'agrocare-production-61a9d.up.railway.app',  # Your current active domain
    '.up.railway.app',                            # Wildcard for any fallback Railway domain
    '127.0.0.1', 
    'localhost'
]

# Static files layout for cloud hosting
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
