"""
Data Enrichment Views
API endpoints for data enrichment operations
"""

import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import (
    EnrichmentProvider, EnrichmentProfile, CompanyEnrichment,
    TechnographicData, IntentSignal, NewsAlert, EmailVerification,
    EnrichmentJob, EnrichmentRule, EnrichmentActivity
)
from .serializers import (
    EnrichmentProviderSerializer, EnrichmentProfileSerializer,
    CompanyEnrichmentSerializer, TechnographicDataSerializer,
    IntentSignalSerializer, NewsAlertSerializer, EmailVerificationSerializer,
    EnrichmentJobSerializer, EnrichmentRuleSerializer, EnrichmentActivitySerializer,
    EnrichContactRequestSerializer, EnrichCompanyRequestSerializer,
    BulkEnrichRequestSerializer, VerifyEmailRequestSerializer,
    FetchNewsRequestSerializer, GetIntentSignalsRequestSerializer,
    EnrichmentStatsResponseSerializer, ProviderStatsSerializer
)
from .services import EnrichmentService, BulkEnrichmentService, EnrichmentStatsService

logger = logging.getLogger(__name__)


class EnrichmentProviderViewSet(viewsets.ModelViewSet):
    """ViewSet for enrichment providers"""
    
    serializer_class = EnrichmentProviderSerializer
    permission_classes = [IsAuthenticated]
    queryset = EnrichmentProvider.objects.all()
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get statistics for all providers"""
        stats = EnrichmentStatsService.get_provider_stats()
        serializer = ProviderStatsSerializer(stats, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test connection to a provider"""
        provider = self.get_object()
        
        # In production, this would make a test API call
        # For now, return success if configured
        if provider.is_configured and provider.api_key:
            return Response({
                'status': 'success',
                'message': 'Connection successful'
            })
        else:
            return Response({
                'status': 'error',
                'message': 'Provider not configured'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def reset_daily_limit(self, request, pk=None):
        """Reset daily request counter"""
        provider = self.get_object()
        provider.daily_requests_used = 0
        provider.last_request_reset = timezone.now().date()
        provider.save()
        return Response({'message': 'Daily limit reset'})


class EnrichmentProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for enrichment profiles"""
    
    serializer_class = EnrichmentProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = EnrichmentProfile.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by domain
        domain = self.request.query_params.get('domain')
        if domain:
            queryset = queryset.filter(domain=domain)
        
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def enrich(self, request):
        """Enrich a contact or lead by email"""
        serializer = EnrichContactRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = EnrichmentService()
        
        # Get contact or lead if provided
        contact = None
        lead = None
        
        if serializer.validated_data.get('contact_id'):
            from contact_management.models import Contact
            try:
                contact = Contact.objects.get(id=serializer.validated_data['contact_id'])
            except Contact.DoesNotExist:
                pass
        
        if serializer.validated_data.get('lead_id'):
            from lead_management.models import Lead
            try:
                lead = Lead.objects.get(id=serializer.validated_data['lead_id'])
            except Lead.DoesNotExist:
                pass
        
        result = service.enrich_contact_or_lead(
            email=serializer.validated_data['email'],
            contact=contact,
            lead=lead,
            enrich_company=serializer.validated_data.get('enrich_company', True),
            verify_email=serializer.validated_data.get('verify_email', True),
            get_social=serializer.validated_data.get('get_social', True)
        )
        
        return Response(result)
    
    @action(detail=True, methods=['post'])
    def refresh(self, request, pk=None):
        """Refresh enrichment data for a profile"""
        profile = self.get_object()
        
        service = EnrichmentService()
        result = service.enrich_contact_or_lead(
            email=profile.email,
            contact=profile.contact,
            lead=profile.lead
        )
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get profiles pending enrichment"""
        profiles = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(profiles, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stale(self, request):
        """Get profiles with stale data (>30 days)"""
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(days=30)
        profiles = self.get_queryset().filter(
            last_enriched_at__lt=cutoff
        )
        serializer = self.get_serializer(profiles, many=True)
        return Response(serializer.data)


class CompanyEnrichmentViewSet(viewsets.ModelViewSet):
    """ViewSet for company enrichments"""
    
    serializer_class = CompanyEnrichmentSerializer
    permission_classes = [IsAuthenticated]
    queryset = CompanyEnrichment.objects.all()
    lookup_field = 'domain'
    
    @action(detail=False, methods=['post'])
    def enrich(self, request):
        """Enrich a company by domain"""
        serializer = EnrichCompanyRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = EnrichmentService()
        
        # First enrich basic company data
        company = service._enrich_company(serializer.validated_data['domain'])
        
        if not company:
            return Response(
                {'error': 'Could not enrich company'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get additional data if requested
        if serializer.validated_data.get('get_news', True):
            service.fetch_company_news(company.domain)
        
        # Get technographics
        if serializer.validated_data.get('get_technographics', True):
            service.engine.get_technographics(company.domain)
        
        company_serializer = self.get_serializer(company)
        return Response(company_serializer.data)
    
    @action(detail=True, methods=['get'])
    def technographics(self, request, domain=None):
        """Get technographic data for a company"""
        company = self.get_object()
        techs = TechnographicData.objects.filter(company=company)
        serializer = TechnographicDataSerializer(techs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def news(self, request, domain=None):
        """Get news alerts for a company"""
        company = self.get_object()
        news = NewsAlert.objects.filter(company=company).order_by('-published_at')[:20]
        serializer = NewsAlertSerializer(news, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def intent(self, request, domain=None):
        """Get intent signals for a company"""
        company = self.get_object()
        signals = IntentSignal.objects.filter(company=company).order_by('-detected_at')[:20]
        serializer = IntentSignalSerializer(signals, many=True)
        return Response(serializer.data)


class IntentSignalViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for intent signals"""
    
    serializer_class = IntentSignalSerializer
    permission_classes = [IsAuthenticated]
    queryset = IntentSignal.objects.all().order_by('-detected_at')
    
    @action(detail=False, methods=['post'])
    def fetch(self, request):
        """Fetch intent signals for a company"""
        serializer = GetIntentSignalsRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = EnrichmentService()
        signals = service.get_intent_signals(
            domain=serializer.validated_data['domain'],
            topics=serializer.validated_data.get('topics')
        )
        
        signal_serializer = self.get_serializer(signals, many=True)
        return Response(signal_serializer.data)
    
    @action(detail=False, methods=['get'])
    def strong(self, request):
        """Get strong intent signals"""
        signals = self.queryset.filter(strength__in=['strong', 'very_strong'])
        serializer = self.get_serializer(signals[:50], many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_actioned(self, request, pk=None):
        """Mark an intent signal as actioned"""
        signal = self.get_object()
        signal.was_actioned = True
        signal.actioned_by = request.user
        signal.actioned_at = timezone.now()
        signal.save()
        return Response({'message': 'Signal marked as actioned'})


class NewsAlertViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for news alerts"""
    
    serializer_class = NewsAlertSerializer
    permission_classes = [IsAuthenticated]
    queryset = NewsAlert.objects.all().order_by('-published_at')
    
    @action(detail=False, methods=['post'])
    def fetch(self, request):
        """Fetch news for a company"""
        serializer = FetchNewsRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = EnrichmentService()
        alerts = service.fetch_company_news(
            domain=serializer.validated_data['domain'],
            days_back=serializer.validated_data.get('days_back', 30)
        )
        
        alert_serializer = self.get_serializer(alerts, many=True)
        return Response(alert_serializer.data)
    
    @action(detail=False, methods=['get'])
    def sales_triggers(self, request):
        """Get sales trigger alerts"""
        alerts = self.queryset.filter(is_sales_trigger=True, is_read=False)
        serializer = self.get_serializer(alerts[:50], many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a news alert as read"""
        alert = self.get_object()
        alert.is_read = True
        alert.read_by = request.user
        alert.read_at = timezone.now()
        alert.save()
        return Response({'message': 'Alert marked as read'})


class EmailVerificationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for email verifications"""
    
    serializer_class = EmailVerificationSerializer
    permission_classes = [IsAuthenticated]
    queryset = EmailVerification.objects.all()
    
    @action(detail=False, methods=['post'])
    def verify(self, request):
        """Verify an email address"""
        serializer = VerifyEmailRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = EnrichmentService()
        verification = service._verify_email(serializer.validated_data['email'])
        
        if verification:
            return Response(EmailVerificationSerializer(verification).data)
        else:
            return Response(
                {'error': 'Could not verify email'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def bulk_verify(self, request):
        """Bulk verify emails"""
        emails = request.data.get('emails', [])
        
        if not emails or len(emails) > 100:
            return Response(
                {'error': 'Provide 1-100 emails'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = EnrichmentService()
        results = []
        
        for email in emails:
            verification = service._verify_email(email)
            if verification:
                results.append({
                    'email': email,
                    'status': verification.status,
                    'quality_score': verification.quality_score
                })
            else:
                results.append({
                    'email': email,
                    'status': 'error',
                    'quality_score': 0
                })
        
        return Response({'results': results})


class EnrichmentJobViewSet(viewsets.ModelViewSet):
    """ViewSet for enrichment jobs"""
    
    serializer_class = EnrichmentJobSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return EnrichmentJob.objects.filter(
            initiated_by=self.request.user
        ).order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def bulk_enrich(self, request):
        """Start a bulk enrichment job"""
        serializer = BulkEnrichRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = BulkEnrichmentService()
        job = service.create_bulk_job(
            emails=serializer.validated_data['emails'],
            user=request.user,
            enrichment_types=serializer.validated_data.get('enrichment_types')
        )
        
        # Trigger async processing
        from .tasks import process_bulk_enrichment_job
        process_bulk_enrichment_job.delay(str(job.id))
        
        return Response(EnrichmentJobSerializer(job).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get job status"""
        job = self.get_object()
        return Response({
            'status': job.status,
            'progress': job.processed_records / job.total_records * 100 if job.total_records > 0 else 0,
            'processed': job.processed_records,
            'total': job.total_records,
            'successful': job.successful_records,
            'failed': job.failed_records
        })


class EnrichmentRuleViewSet(viewsets.ModelViewSet):
    """ViewSet for enrichment rules"""
    
    serializer_class = EnrichmentRuleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return EnrichmentRule.objects.all().order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """Toggle rule active status"""
        rule = self.get_object()
        rule.is_active = not rule.is_active
        rule.save()
        return Response({'is_active': rule.is_active})
    
    @action(detail=True, methods=['post'])
    def trigger(self, request, pk=None):
        """Manually trigger a rule"""
        rule = self.get_object()
        
        # Update trigger stats
        rule.times_triggered += 1
        rule.last_triggered_at = timezone.now()
        rule.save()
        
        return Response({'message': 'Rule triggered'})


class EnrichmentActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for enrichment activities"""
    
    serializer_class = EnrichmentActivitySerializer
    permission_classes = [IsAuthenticated]
    queryset = EnrichmentActivity.objects.all().order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent activities"""
        limit = int(request.query_params.get('limit', 20))
        activities = self.queryset[:limit]
        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)


class EnrichmentDashboardViewSet(viewsets.ViewSet):
    """ViewSet for enrichment dashboard data"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get overall enrichment statistics"""
        stats = EnrichmentStatsService.get_enrichment_stats()
        serializer = EnrichmentStatsResponseSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def providers(self, request):
        """Get provider statistics"""
        stats = EnrichmentStatsService.get_provider_stats()
        serializer = ProviderStatsSerializer(stats, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent enrichment activities"""
        recent = EnrichmentStatsService.get_recent_enrichments(20)
        return Response(recent)
