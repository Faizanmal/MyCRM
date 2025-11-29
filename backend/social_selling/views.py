"""
Social Selling Views
"""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Sum, Avg
from datetime import timedelta

from .models import (
    SocialProfile, SocialEngagement, LinkedInIntegration,
    SocialSellingSequence, ProspectInSequence,
    SocialInsight, EngagementAnalytics
)
from .serializers import (
    SocialProfileSerializer, SocialPostSerializer, SocialEngagementSerializer,
    LinkedInIntegrationSerializer, SocialSellingSequenceSerializer,
    SocialSellingStepSerializer, SocialInsightSerializer, EngagementAnalyticsSerializer,
    CreateSocialProfileSerializer, BulkEngagementSerializer
)
from .services import SocialSellingService


class SocialProfileViewSet(viewsets.ModelViewSet):
    """Manage social profiles for contacts"""
    serializer_class = SocialProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SocialProfile.objects.filter(
            contact__created_by=self.request.user
        ).select_related('contact')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateSocialProfileSerializer
        return SocialProfileSerializer
    
    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """Sync profile data from social network"""
        profile = self.get_object()
        service = SocialSellingService()
        
        success, message = service.sync_profile(profile)
        
        if success:
            return Response({'status': 'synced', 'message': message})
        return Response({'status': 'error', 'message': message}, status=400)
    
    @action(detail=True, methods=['get'])
    def recent_posts(self, request, pk=None):
        """Get recent posts from profile"""
        profile = self.get_object()
        posts = profile.posts.order_by('-posted_at')[:20]
        serializer = SocialPostSerializer(posts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def insights(self, request, pk=None):
        """Get AI insights for profile"""
        profile = self.get_object()
        insights = profile.insights.filter(is_actioned=False)[:10]
        serializer = SocialInsightSerializer(insights, many=True)
        return Response(serializer.data)


class SocialEngagementViewSet(viewsets.ModelViewSet):
    """Manage social selling engagements"""
    serializer_class = SocialEngagementSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SocialEngagement.objects.filter(
            user=self.request.user
        ).select_related('profile', 'profile__contact', 'post')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def bulk_schedule(self, request):
        """Bulk schedule engagements"""
        serializer = BulkEngagementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = SocialSellingService()
        engagements = service.bulk_schedule_engagements(
            user=request.user,
            **serializer.validated_data
        )
        
        return Response({
            'scheduled': len(engagements),
            'message': f'Scheduled {len(engagements)} engagements'
        })
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute a pending engagement"""
        engagement = self.get_object()
        service = SocialSellingService()
        
        success, message = service.execute_engagement(engagement)
        
        if success:
            return Response({'status': 'completed', 'message': message})
        return Response({'status': 'error', 'message': message}, status=400)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending engagements"""
        pending = self.get_queryset().filter(
            status='pending',
            scheduled_for__lte=timezone.now()
        )
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's engagements"""
        today = timezone.now().date()
        engagements = self.get_queryset().filter(
            created_at__date=today
        )
        serializer = self.get_serializer(engagements, many=True)
        return Response(serializer.data)


class LinkedInIntegrationViewSet(viewsets.ModelViewSet):
    """Manage LinkedIn integration"""
    serializer_class = LinkedInIntegrationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return LinkedInIntegration.objects.filter(user=self.request.user)
    
    def get_object(self):
        obj, created = LinkedInIntegration.objects.get_or_create(user=self.request.user)
        return obj
    
    @action(detail=False, methods=['get'])
    def auth_url(self, request):
        """Get LinkedIn OAuth URL"""
        service = SocialSellingService()
        auth_url = service.get_linkedin_auth_url(request.user)
        return Response({'auth_url': auth_url})
    
    @action(detail=False, methods=['post'])
    def callback(self, request):
        """Handle OAuth callback"""
        code = request.data.get('code')
        service = SocialSellingService()
        
        success, message = service.handle_linkedin_callback(request.user, code)
        
        if success:
            return Response({'status': 'connected', 'message': message})
        return Response({'status': 'error', 'message': message}, status=400)
    
    @action(detail=False, methods=['post'])
    def disconnect(self, request):
        """Disconnect LinkedIn"""
        integration = self.get_object()
        integration.access_token = ''
        integration.refresh_token = ''
        integration.token_expires_at = None
        integration.is_active = False
        integration.save()
        return Response({'status': 'disconnected'})


class SocialSellingSequenceViewSet(viewsets.ModelViewSet):
    """Manage social selling sequences"""
    serializer_class = SocialSellingSequenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SocialSellingSequence.objects.filter(
            user=self.request.user
        ).prefetch_related('steps', 'prospects')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_step(self, request, pk=None):
        """Add step to sequence"""
        sequence = self.get_object()
        serializer = SocialSellingStepSerializer(data={
            **request.data,
            'sequence': sequence.id,
            'order': sequence.steps.count()
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)
    
    @action(detail=True, methods=['post'])
    def enroll(self, request, pk=None):
        """Enroll prospects in sequence"""
        sequence = self.get_object()
        profile_ids = request.data.get('profile_ids', [])
        
        enrolled = 0
        for profile_id in profile_ids:
            try:
                profile = SocialProfile.objects.get(id=profile_id)
                ProspectInSequence.objects.get_or_create(
                    sequence=sequence,
                    profile=profile,
                    defaults={'next_action_at': timezone.now()}
                )
                enrolled += 1
            except SocialProfile.DoesNotExist:
                pass
        
        return Response({
            'enrolled': enrolled,
            'message': f'Enrolled {enrolled} prospects'
        })
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Pause sequence"""
        sequence = self.get_object()
        sequence.is_active = False
        sequence.save()
        return Response({'status': 'paused'})
    
    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """Resume sequence"""
        sequence = self.get_object()
        sequence.is_active = True
        sequence.save()
        return Response({'status': 'resumed'})
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get sequence analytics"""
        sequence = self.get_object()
        prospects = sequence.prospects.all()
        
        return Response({
            'total_enrolled': prospects.count(),
            'active': prospects.filter(status='active').count(),
            'completed': prospects.filter(status='completed').count(),
            'responded': prospects.filter(status='responded').count(),
            'response_rate': self._calc_response_rate(prospects),
        })
    
    def _calc_response_rate(self, prospects):
        total = prospects.count()
        if total == 0:
            return 0
        responded = prospects.filter(status='responded').count()
        return round((responded / total) * 100, 1)


class SocialInsightViewSet(viewsets.ModelViewSet):
    """Manage social insights"""
    serializer_class = SocialInsightSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SocialInsight.objects.filter(
            profile__contact__created_by=self.request.user
        ).select_related('profile', 'profile__contact', 'related_post')
    
    @action(detail=False, methods=['get'])
    def unactioned(self, request):
        """Get unactioned insights"""
        insights = self.get_queryset().filter(is_actioned=False)
        serializer = self.get_serializer(insights, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def buying_signals(self, request):
        """Get buying signal insights"""
        signals = self.get_queryset().filter(
            insight_type='buying_signal',
            is_actioned=False
        )
        serializer = self.get_serializer(signals, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_actioned(self, request, pk=None):
        """Mark insight as actioned"""
        insight = self.get_object()
        insight.is_actioned = True
        insight.actioned_at = timezone.now()
        insight.save()
        return Response({'status': 'actioned'})


class EngagementAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """View engagement analytics"""
    serializer_class = EngagementAnalyticsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return EngagementAnalytics.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get analytics dashboard"""
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        
        analytics = self.get_queryset().filter(date__gte=start_date)
        
        # Aggregate stats
        totals = analytics.aggregate(
            total_profiles_viewed=Sum('profiles_viewed'),
            total_connections_sent=Sum('connections_sent'),
            total_connections_accepted=Sum('connections_accepted'),
            total_messages_sent=Sum('messages_sent'),
            total_messages_replied=Sum('messages_replied'),
            total_contacts_created=Sum('contacts_created'),
            total_opportunities_created=Sum('opportunities_created'),
            total_meetings_booked=Sum('meetings_booked'),
            avg_engagement_score=Avg('engagement_score'),
        )
        
        # Daily breakdown
        daily = list(analytics.values('date').annotate(
            connections=Sum('connections_accepted'),
            messages=Sum('messages_replied'),
            meetings=Sum('meetings_booked'),
            score=Avg('engagement_score'),
        ).order_by('date'))
        
        return Response({
            'summary': totals,
            'daily': daily,
            'period_days': days,
        })
    
    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Get team leaderboard"""
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        
        leaderboard = EngagementAnalytics.objects.filter(
            date__gte=start_date
        ).values('user__email', 'user__first_name', 'user__last_name').annotate(
            total_score=Sum('engagement_score'),
            total_connections=Sum('connections_accepted'),
            total_meetings=Sum('meetings_booked'),
        ).order_by('-total_score')[:10]
        
        return Response(list(leaderboard))
