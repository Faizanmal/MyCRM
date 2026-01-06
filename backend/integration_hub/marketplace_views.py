"""
Integration Marketplace - Views
"""

from django.db.models import Avg, Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .marketplace_models import (
    APIRateLimit,
    APIUsageLog,
    AppInstallation,
    AppReview,
    CustomWebhook,
    MarketplaceApp,
    WebhookDeliveryLog,
)
from .marketplace_serializers import (
    APIRateLimitSerializer,
    APIUsageLogSerializer,
    AppInstallationSerializer,
    AppReviewSerializer,
    CreateRateLimitSerializer,
    CreateReviewSerializer,
    CreateWebhookSerializer,
    CustomWebhookSerializer,
    MarketplaceAppCreateSerializer,
    MarketplaceAppDetailSerializer,
    MarketplaceAppListSerializer,
    WebhookDeliveryLogSerializer,
)
from .marketplace_services import MarketplaceService, RateLimitingService, WebhookBuilderService


class MarketplaceAppViewSet(viewsets.ModelViewSet):
    """Manage marketplace apps"""

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'featured', 'search']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'list':
            return MarketplaceAppListSerializer
        if self.action == 'create':
            return MarketplaceAppCreateSerializer
        return MarketplaceAppDetailSerializer

    def get_queryset(self):
        if self.action in ['list', 'retrieve', 'featured', 'search']:
            return MarketplaceApp.objects.filter(status='published')
        return MarketplaceApp.objects.filter(developer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(developer=self.request.user, status='draft')

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured apps"""
        service = MarketplaceService()
        apps = service.get_featured_apps(limit=12)
        return Response(
            MarketplaceAppListSerializer(apps, many=True).data
        )

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search marketplace apps"""
        query = request.query_params.get('q', '')
        category = request.query_params.get('category', '')
        tags = request.query_params.getlist('tags')

        apps = self.get_queryset()

        if query:
            apps = apps.filter(
                Q(name__icontains=query) |
                Q(tagline__icontains=query) |
                Q(description__icontains=query)
            )

        if category:
            apps = apps.filter(category=category)

        if tags:
            for tag in tags:
                apps = apps.filter(tags__contains=[tag])

        return Response(
            MarketplaceAppListSerializer(apps, many=True).data
        )

    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get app categories"""
        return Response([
            {'value': choice[0], 'label': choice[1]}
            for choice in MarketplaceApp.CATEGORIES
        ])

    @action(detail=True, methods=['post'])
    def install(self, request, pk=None):
        """Install an app"""
        app = self.get_object()
        config = request.data.get('config', {})

        service = MarketplaceService()
        result = service.install_app(app, request.user, config)

        return Response(result)

    @action(detail=True, methods=['post'])
    def uninstall(self, request, pk=None):
        """Uninstall an app"""
        app = self.get_object()

        service = MarketplaceService()
        result = service.uninstall_app(app, request.user)

        return Response(result)

    @action(detail=True, methods=['get'])
    def oauth_url(self, request, pk=None):
        """Get OAuth authorization URL"""
        app = self.get_object()
        redirect_uri = request.query_params.get('redirect_uri', '')

        service = MarketplaceService()
        url = service.get_oauth_url(app, request.user, redirect_uri)

        if url:
            return Response({'oauth_url': url})
        return Response(
            {'error': 'OAuth not configured for this app'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def oauth_callback(self, request, pk=None):
        """Handle OAuth callback"""
        app = self.get_object()
        code = request.data.get('code', '')
        redirect_uri = request.data.get('redirect_uri', '')

        service = MarketplaceService()
        result = service.exchange_oauth_code(app, request.user, code, redirect_uri)

        return Response(result)

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get app reviews"""
        app = self.get_object()
        reviews = app.reviews.all()
        return Response(
            AppReviewSerializer(reviews, many=True).data
        )

    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """Submit a review"""
        app = self.get_object()

        serializer = CreateReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        review, created = AppReview.objects.update_or_create(
            app=app,
            user=request.user,
            defaults=serializer.validated_data
        )

        # Update app rating
        avg_rating = app.reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        app.rating_avg = avg_rating
        app.rating_count = app.reviews.count()
        app.save()

        return Response(AppReviewSerializer(review).data)

    @action(detail=True, methods=['post'])
    def submit_for_review(self, request, pk=None):
        """Submit app for marketplace review"""
        app = self.get_object()

        if app.developer != request.user:
            return Response(
                {'error': 'Only the developer can submit for review'},
                status=status.HTTP_403_FORBIDDEN
            )

        app.status = 'pending_review'
        app.save()

        return Response({'status': 'submitted for review'})


class AppInstallationViewSet(viewsets.ReadOnlyModelViewSet):
    """View installed apps"""

    serializer_class = AppInstallationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AppInstallation.objects.filter(
            user=self.request.user,
            status='active'
        )

    @action(detail=True, methods=['post'])
    def update_config(self, request, pk=None):
        """Update installation configuration"""
        installation = self.get_object()
        config = request.data.get('config', {})

        installation.config = {**installation.config, **config}
        installation.save()

        return Response(AppInstallationSerializer(installation).data)

    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Pause an app installation"""
        installation = self.get_object()
        installation.status = 'paused'
        installation.save()
        return Response({'status': 'paused'})

    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """Resume a paused app installation"""
        installation = self.get_object()
        installation.status = 'active'
        installation.save()
        return Response({'status': 'active'})


class CustomWebhookViewSet(viewsets.ModelViewSet):
    """Manage custom webhooks"""

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateWebhookSerializer
        return CustomWebhookSerializer

    def get_queryset(self):
        return CustomWebhook.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = CreateWebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = WebhookBuilderService()
        result = service.create_webhook(request.user, serializer.validated_data)

        webhook = CustomWebhook.objects.get(id=result['webhook_id'])
        return Response(
            CustomWebhookSerializer(webhook).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get'])
    def events(self, request):
        """Get available webhook events"""
        service = WebhookBuilderService()
        events = service.get_available_events()
        return Response(events)

    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Test a webhook"""
        webhook = self.get_object()

        service = WebhookBuilderService()
        result = service.test_webhook(webhook)

        return Response(result)

    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """Toggle webhook active status"""
        webhook = self.get_object()
        webhook.is_active = not webhook.is_active
        webhook.save()
        return Response({'is_active': webhook.is_active})

    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Get webhook delivery logs"""
        webhook = self.get_object()
        logs = webhook.delivery_logs.all()[:100]
        return Response(
            WebhookDeliveryLogSerializer(logs, many=True).data
        )

    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Retry failed deliveries"""
        webhook = self.get_object()
        log_id = request.data.get('log_id')

        try:
            log = webhook.delivery_logs.get(id=log_id, status='failed')
        except WebhookDeliveryLog.DoesNotExist:
            return Response(
                {'error': 'Log not found or not failed'},
                status=status.HTTP_404_NOT_FOUND
            )

        service = WebhookBuilderService()
        payload = log.request_body

        try:
            import json
            payload_dict = json.loads(payload)
        except Exception:
            payload_dict = {'raw': payload}

        result = service.deliver_webhook(webhook, log.event, payload_dict)

        return Response(result)


class APIRateLimitViewSet(viewsets.ModelViewSet):
    """Manage API rate limits"""

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateRateLimitSerializer
        return APIRateLimitSerializer

    def get_queryset(self):
        # Admin users see all, regular users see their own
        if self.request.user.is_staff:
            return APIRateLimit.objects.all()
        return APIRateLimit.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = CreateRateLimitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = RateLimitingService()

        user = None
        if serializer.validated_data.get('user_id'):
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.get(id=serializer.validated_data['user_id'])
            except User.DoesNotExist:
                return Response(
                    {'error': 'User not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

        result = service.create_rate_limit(
            user=user,
            api_key=serializer.validated_data.get('api_key'),
            limit=serializer.validated_data['requests_limit'],
            period=serializer.validated_data['period']
        )

        return Response(result)

    @action(detail=True, methods=['post'])
    def reset(self, request, pk=None):
        """Reset rate limit counter"""
        rate_limit = self.get_object()
        rate_limit.current_count = 0
        rate_limit.period_start = timezone.now()
        rate_limit.is_exceeded = False
        rate_limit.save()
        return Response({'status': 'reset'})

    @action(detail=False, methods=['get'])
    def check(self, request):
        """Check current rate limit status"""
        service = RateLimitingService()
        result = service.check_rate_limit(user=request.user)
        return Response(result)


class APIUsageViewSet(viewsets.ViewSet):
    """View API usage and metrics"""

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def logs(self, request):
        """Get usage logs"""
        logs = APIUsageLog.objects.filter(
            user=request.user
        ).order_by('-created_at')[:100]

        return Response(
            APIUsageLogSerializer(logs, many=True).data
        )

    @action(detail=False, methods=['get'])
    def metrics(self, request):
        """Get usage metrics"""
        period = request.query_params.get('period', 'daily')

        service = RateLimitingService()
        metrics = service.get_usage_metrics(user=request.user, period=period)

        return Response(metrics)

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get comprehensive usage dashboard"""
        service = RateLimitingService()

        # Get metrics for different periods
        hourly = service.get_usage_metrics(user=request.user, period='hourly')
        daily = service.get_usage_metrics(user=request.user, period='daily')
        weekly = service.get_usage_metrics(user=request.user, period='weekly')

        # Get rate limit status
        rate_limit_status = service.check_rate_limit(user=request.user)

        return Response({
            'rate_limit': rate_limit_status,
            'hourly': hourly,
            'daily': daily,
            'weekly': weekly,
        })


class IntegrationMarketplaceDashboardView(APIView):
    """Dashboard for integration marketplace"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get marketplace dashboard data"""

        user = request.user

        # Installed apps
        installed_apps = AppInstallation.objects.filter(
            user=user,
            status='active'
        ).select_related('app')[:10]

        # Featured apps
        featured_apps = MarketplaceApp.objects.filter(
            status='published'
        ).order_by('-rating_avg', '-install_count')[:6]

        # Custom webhooks
        webhooks = CustomWebhook.objects.filter(user=user)
        active_webhooks = webhooks.filter(is_active=True).count()

        # Recent webhook deliveries
        recent_deliveries = WebhookDeliveryLog.objects.filter(
            webhook__user=user
        ).order_by('-created_at')[:10]

        # API usage
        service = RateLimitingService()
        usage = service.get_usage_metrics(user=user, period='daily')
        rate_limit = service.check_rate_limit(user=user)

        return Response({
            'installed_apps': AppInstallationSerializer(installed_apps, many=True).data,
            'featured_apps': MarketplaceAppListSerializer(featured_apps, many=True).data,
            'webhooks': {
                'total': webhooks.count(),
                'active': active_webhooks,
            },
            'recent_deliveries': WebhookDeliveryLogSerializer(recent_deliveries, many=True).data,
            'api_usage': usage,
            'rate_limit': rate_limit,
        })
