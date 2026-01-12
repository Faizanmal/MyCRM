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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

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

    # Premium Revenue Features
    path('api/v1/revenue-intelligence/', include('revenue_intelligence.urls')),
    path('api/v1/email-tracking/', include('email_tracking.urls')),
    path('api/v1/scheduling/', include('smart_scheduling.urls')),
    path('api/v1/ai-assistant/', include('ai_sales_assistant.urls')),
    path('api/v1/social-selling/', include('social_selling.urls')),
    path('api/v1/documents/', include('document_esign.urls')),
    path('api/v1/conversation-intelligence/', include('conversation_intelligence.urls')),
    path('api/v1/white-label/', include('white_label.urls')),
    path('api/v1/customer-success/', include('customer_success.urls')),

    # AI Workflow Automation Features
    path('api/v1/email-sequences/', include('email_sequence_automation.urls')),
    path('api/v1/lead-routing/', include('predictive_lead_routing.urls')),
    path('api/v1/data-enrichment/', include('data_enrichment.urls')),
    path('api/v1/voice-intelligence/', include('voice_intelligence.urls')),
    path('api/v1/scheduling/ai/', include('smart_scheduling.ai_urls')),
    
    # Enterprise Features (New)
    path('api/v1/ai-chatbot/', include('ai_chatbot.urls')),
    path('api/v1/marketplace/', include('app_marketplace.urls')),
    path('api/v1/esg/', include('esg_reporting.urls')),
    path('api/v1/realtime-collab/', include('realtime_collaboration.urls')),
    path('api/v1/security/', include('enterprise.urls')),
    path('api/v1/customer-portal/', include('customer_portal.urls')),
    path('api/v1/social-inbox/', include('social_inbox.urls')),
    
    # Futuristic Next-Gen Features
    path('api/v1/quantum/', include('quantum_modeling.urls')),
    path('api/v1/web3/', include('web3_integration.urls')),
    path('api/v1/metaverse/', include('metaverse_experiences.urls')),
    path('api/v1/ethical-ai/', include('ethical_ai_oversight.urls')),
    path('api/v1/carbon/', include('carbon_tracking.urls')),
    path('api/v1/neurological/', include('neurological_feedback.urls')),
    path('api/v1/holographic/', include('holographic_collab.urls')),
    path('api/v1/autonomous-workflow/', include('autonomous_workflow.urls')),
    path('api/v1/interplanetary/', include('interplanetary_sync.urls')),
    path('api/v1/biofeedback/', include('biofeedback_personalization.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
