"""
App Marketplace Views
"""

from django.db.models import Q, Avg
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    AppCategory, AppDeveloper, MarketplaceApp, AppVersion,
    AppInstallation, AppReview
)
from .serializers import (
    AppCategorySerializer, AppDeveloperSerializer,
    MarketplaceAppListSerializer, MarketplaceAppDetailSerializer,
    AppVersionSerializer, AppInstallationSerializer, AppInstallSerializer,
    AppReviewSerializer, CreateReviewSerializer
)


class AppCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """List app categories"""
    queryset = AppCategory.objects.all()
    serializer_class = AppCategorySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'


class MarketplaceAppViewSet(viewsets.ReadOnlyModelViewSet):
    """Browse and view marketplace apps"""
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = MarketplaceApp.objects.filter(status='approved')
        
        # Filters
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        app_type = self.request.query_params.get('type')
        if app_type:
            queryset = queryset.filter(app_type=app_type)
        
        pricing = self.request.query_params.get('pricing')
        if pricing:
            queryset = queryset.filter(pricing_type=pricing)
        
        featured = self.request.query_params.get('featured')
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(tags__contains=[search])
            )
        
        # Sort
        sort = self.request.query_params.get('sort', 'popular')
        if sort == 'popular':
            queryset = queryset.order_by('-install_count')
        elif sort == 'rating':
            queryset = queryset.order_by('-rating_average')
        elif sort == 'newest':
            queryset = queryset.order_by('-published_at')
        elif sort == 'name':
            queryset = queryset.order_by('name')
        
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return MarketplaceAppListSerializer
        return MarketplaceAppDetailSerializer

    @action(detail=True, methods=['get'])
    def versions(self, request, slug=None):
        """Get version history for an app"""
        app = self.get_object()
        versions = AppVersion.objects.filter(app=app, is_approved=True)
        return Response(AppVersionSerializer(versions, many=True).data)

    @action(detail=True, methods=['get'])
    def reviews(self, request, slug=None):
        """Get reviews for an app"""
        app = self.get_object()
        reviews = AppReview.objects.filter(app=app, is_approved=True)
        
        sort = request.query_params.get('sort', 'recent')
        if sort == 'helpful':
            reviews = reviews.order_by('-helpful_count')
        elif sort == 'rating_high':
            reviews = reviews.order_by('-rating')
        elif sort == 'rating_low':
            reviews = reviews.order_by('rating')
        
        return Response(AppReviewSerializer(reviews, many=True).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def install(self, request, slug=None):
        """Install an app"""
        app = self.get_object()
        serializer = AppInstallSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check if already installed
        existing = AppInstallation.objects.filter(
            app=app,
            installed_by=request.user
        ).first()
        
        if existing and existing.status == 'active':
            return Response(
                {"error": "App is already installed"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create or update installation
        installation, created = AppInstallation.objects.update_or_create(
            app=app,
            installed_by=request.user,
            defaults={
                'installed_version': app.current_version,
                'config': serializer.validated_data.get('config', {}),
                'status': 'active'
            }
        )
        
        # Update app install count
        app.install_count = AppInstallation.objects.filter(
            app=app, status='active'
        ).count()
        app.save()
        
        return Response(AppInstallationSerializer(installation).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def uninstall(self, request, slug=None):
        """Uninstall an app"""
        app = self.get_object()
        
        try:
            installation = AppInstallation.objects.get(
                app=app,
                installed_by=request.user
            )
            installation.status = 'inactive'
            installation.save()
            
            # Update app install count
            app.install_count = AppInstallation.objects.filter(
                app=app, status='active'
            ).count()
            app.save()
            
            return Response({"message": "App uninstalled successfully"})
        except AppInstallation.DoesNotExist:
            return Response(
                {"error": "App is not installed"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def review(self, request, slug=None):
        """Submit a review for an app"""
        app = self.get_object()
        
        # Check if user has installed the app
        installation = AppInstallation.objects.filter(
            app=app,
            installed_by=request.user
        ).first()
        
        if not installation:
            return Response(
                {"error": "You must install the app before reviewing"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check for existing review
        existing = AppReview.objects.filter(app=app, user=request.user).first()
        if existing:
            return Response(
                {"error": "You have already reviewed this app"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CreateReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        review = AppReview.objects.create(
            app=app,
            user=request.user,
            installation=installation,
            **serializer.validated_data
        )
        
        # Update app rating
        ratings = AppReview.objects.filter(app=app, is_approved=True)
        app.rating_count = ratings.count()
        app.rating_average = ratings.aggregate(avg=Avg('rating'))['avg'] or 0
        app.save()
        
        return Response(AppReviewSerializer(review).data)


class MyAppsViewSet(viewsets.ModelViewSet):
    """Manage installed apps"""
    serializer_class = AppInstallationSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch', 'delete']

    def get_queryset(self):
        return AppInstallation.objects.filter(
            installed_by=self.request.user,
            status='active'
        ).select_related('app', 'app__developer')

    @action(detail=True, methods=['patch'])
    def configure(self, request, pk=None):
        """Update app configuration"""
        installation = self.get_object()
        installation.config = request.data.get('config', installation.config)
        installation.save()
        return Response(AppInstallationSerializer(installation).data)

    @action(detail=True, methods=['post'])
    def refresh_token(self, request, pk=None):
        """Refresh OAuth token for app"""
        installation = self.get_object()
        # Implement OAuth refresh logic
        return Response({"message": "Token refreshed"})


class DeveloperPortalViewSet(viewsets.ModelViewSet):
    """Developer portal for managing apps"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MarketplaceApp.objects.filter(developer__user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return MarketplaceAppListSerializer
        return MarketplaceAppDetailSerializer

    @action(detail=True, methods=['post'])
    def submit_for_review(self, request, pk=None):
        """Submit app for review"""
        app = self.get_object()
        if app.status not in ['draft', 'rejected']:
            return Response(
                {"error": "App cannot be submitted in current status"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        app.status = 'pending_review'
        app.save()
        return Response({"message": "App submitted for review"})

    @action(detail=True, methods=['post'])
    def publish_version(self, request, pk=None):
        """Publish a new version"""
        app = self.get_object()
        
        version = request.data.get('version')
        changelog = request.data.get('changelog', '')
        
        if not version:
            return Response(
                {"error": "Version is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        app_version = AppVersion.objects.create(
            app=app,
            version=version,
            changelog=changelog
        )
        
        return Response(AppVersionSerializer(app_version).data)


class MarketplaceDashboardView(APIView):
    """Marketplace dashboard and stats"""
    permission_classes = [AllowAny]

    def get(self, request):
        """Get marketplace overview"""
        apps = MarketplaceApp.objects.filter(status='approved')
        
        return Response({
            'total_apps': apps.count(),
            'categories': AppCategorySerializer(
                AppCategory.objects.all()[:10],
                many=True
            ).data,
            'featured': MarketplaceAppListSerializer(
                apps.filter(is_featured=True)[:6],
                many=True
            ).data,
            'popular': MarketplaceAppListSerializer(
                apps.order_by('-install_count')[:6],
                many=True
            ).data,
            'newest': MarketplaceAppListSerializer(
                apps.order_by('-published_at')[:6],
                many=True
            ).data,
            'top_rated': MarketplaceAppListSerializer(
                apps.filter(rating_count__gte=5).order_by('-rating_average')[:6],
                many=True
            ).data
        })
