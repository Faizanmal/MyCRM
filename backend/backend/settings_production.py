"""
Production Settings
Strict, fail-closed production settings enforcing HTTPS, secure cookies, and mandatory secrets.
"""
import os

os.environ.setdefault('ENVIRONMENT', 'production')
os.environ.setdefault('DEBUG', 'False')

from backend.settings import *
