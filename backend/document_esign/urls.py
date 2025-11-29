"""
Document E-Signature URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'templates', views.DocumentTemplateViewSet, basename='document-template')
router.register(r'documents', views.DocumentViewSet, basename='document')
router.register(r'signatures', views.SavedSignatureViewSet, basename='saved-signature')
router.register(r'analytics', views.DocumentAnalyticsViewSet, basename='document-analytics')
router.register(r'sign', views.SigningViewSet, basename='signing')

urlpatterns = [
    path('', include(router.urls)),
]
