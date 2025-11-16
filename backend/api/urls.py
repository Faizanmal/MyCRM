"""
API URLs - Main entry point for versioned API
"""
from django.urls import path, include

urlpatterns = [
    path('v1/', include('api.v1.urls')),
]
