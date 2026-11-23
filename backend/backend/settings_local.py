"""
Local Development Settings
Configured for developer ergonomics, local SQLite/PostgreSQL, and instant hot-reloading.
"""
import os

os.environ.setdefault('ENVIRONMENT', 'local')
os.environ.setdefault('DEBUG', 'True')
os.environ.setdefault('USE_SQLITE', 'True')

from backend.settings import *
