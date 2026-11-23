"""
CI Test Settings
Optimized for headless, repeatable, hermetic CI test pipelines with fast hashing and in-memory backends.
"""
import os

os.environ['ENVIRONMENT'] = 'ci'
os.environ['DEBUG'] = 'False'
os.environ.setdefault('USE_SQLITE', 'True')
os.environ.setdefault('SECRET_KEY', 'ci-testing-hermetic-secret-key-32-chars-ok')
os.environ.setdefault('ENCRYPTION_KEY', 'ci-testing-encryption-key-sample-ok')

from backend.settings import *

DEBUG = False

# Fast execution overrides
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
CHANNEL_LAYERS = {'default': {'BACKEND': 'channels.layers.InMemoryChannelLayer'}}
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
