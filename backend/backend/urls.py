"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Unified API (versioned)
    path('api/', include('api.urls')),
    
    # Enterprise Core APIs
    path('api/core/', include('core.urls')),
    
    # CRM Module APIs (legacy, consider deprecating in favor of unified API)
    path('api/auth/', include('user_management.urls')),
    path('api/contacts/', include('contact_management.urls')),
    path('api/leads/', include('lead_management.urls')),
    path('api/opportunities/', include('opportunity_management.urls')),
    path('api/tasks/', include('task_management.urls')),
    path('api/communications/', include('communication_management.urls')),
    path('api/campaigns/', include('campaign_management.urls')),
    path('api/documents/', include('document_management.urls')),
    path('api/integrations/', include('integration_hub.urls')),
    path('api/activity/', include('activity_feed.urls')),
    path('api/lead-qualification/', include('lead_qualification.urls')),
    path('api/advanced-reporting/', include('advanced_reporting.urls')),
    path('api/reports/', include('reporting.urls')),
    
    # New Advanced Features
    path('api/v1/integration-hub/', include('integration_hub.urls')),
    path('api/v1/ai-insights/', include('ai_insights.urls')),
    path('api/v1/gamification/', include('gamification.urls')),
    path('api/v1/multi-tenant/', include('multi_tenant.urls')),
    path('api/v1/sso/', include('sso_integration.urls')),
    path('api/v1/collaboration/', include('collaboration.urls')),
    path('api/v1/gdpr/', include('gdpr_compliance.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
