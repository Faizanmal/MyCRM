"""
Staging Settings
Production-mirroring configuration with staging database and security gates.
"""
import os

os.environ.setdefault('ENVIRONMENT', 'staging')
os.environ.setdefault('DEBUG', 'False')

from backend.settings import *
