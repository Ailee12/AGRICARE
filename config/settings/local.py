import os
from .base import * # This imports everything from base.py

# Read the local .env file explicitly
import environ
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Override settings specifically for local development
DEBUG = env.bool('DEBUG', default=True)
SECRET_KEY = env('SECRET_KEY')

# For now, let's fall back to standard SQLite so we don't break the server 
# until we configure PostgreSQL in Step 4.
DATABASES = {
    'default': env.db('DATABASE_URL')
}