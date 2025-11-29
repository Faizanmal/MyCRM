"""
Gamification Views
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Count, Q

from .models import Achievement, UserAchievement, Leaderboard, UserPoints, PointTransaction, Challenge, ChallengeProgress
from .serializers import (
    AchievementSerializer, UserAchievementSerializer, LeaderboardSerializer,
    UserPointsSerializer, PointTransactionSerializer, ChallengeSerializer, ChallengeProgressSerializer
)


class AchievementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing achievements
    """
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'difficulty', 'is_active']
    search_fields = ['name', 'description']
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get available achievements for current user"""
        # Get achievements not yet completed
        completed_ids = UserAchievement.objects.filter(
            user=request.user,
            is_completed=True
        ).values_list('achievement_id', flat=True)
        
        available = Achievement.objects.filter(is_active=True).exclude(
            id__in=completed_ids
        )
        
        serializer = self.get_serializer(available, many=True)
        return Response(serializer.data)


class UserAchievementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user achievements
    """
    queryset = UserAchievement.objects.all()
    serializer_class = UserAchievementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_completed', 'achievement__category']
    
    def get_queryset(self):
        # Users see their own achievements, staff see all
        if self.request.user.is_staff:
            return UserAchievement.objects.all()
        return UserAchievement.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_achievements(self, request):
        """Get current user's achievements"""
        achievements = UserAchievement.objects.filter(user=request.user)
        serializer = self.get_serializer(achievements, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get achievement statistics"""
        total = Achievement.objects.filter(is_active=True).count()
        earned = UserAchievement.objects.filter(
            user=request.user,
            is_completed=True
        ).count()
        in_progress = UserAchievement.objects.filter(
            user=request.user,
            is_completed=False
        ).count()
        
        return Response({
            'total_available': total,
            'earned': earned,
            'in_progress': in_progress,
            'completion_rate': (earned / total * 100) if total > 0 else 0
        })


class LeaderboardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for leaderboards
    """
    queryset = Leaderboard.objects.filter(is_active=True)
    serializer_class = LeaderboardSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['period', 'metric']
    
    @action(detail=True, methods=['get'])
    def rankings(self, request, pk=None):
        """Get leaderboard rankings"""
        leaderboard = self.get_object()
        
        # Get rankings based on metric
        if leaderboard.metric == 'total_points':
            rankings = UserPoints.objects.order_by('-total_points')[:leaderboard.display_count]
            data = [{
                'rank': idx + 1,
                'user': {
                    'id': up.user.id,
                    'username': up.user.username,
                    'email': up.user.email
                },
                'score': up.total_points,
                'level': up.level,
                'level_name': up.level_name
            } for idx, up in enumerate(rankings)]
        
        elif leaderboard.metric == 'achievements_earned':
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            users = User.objects.annotate(
                achievement_count=Count('achievements', filter=Q(achievements__is_completed=True))
            ).order_by('-achievement_count')[:leaderboard.display_count]
            
            data = [{
                'rank': idx + 1,
                'user': {
                    'id': u.id,
                    'username': u.username,
                    'email': u.email
                },
                'score': u.achievement_count
            } for idx, u in enumerate(users)]
        
        else:
            data = []
        
        return Response({
            'leaderboard': LeaderboardSerializer(leaderboard).data,
            'rankings': data
        })


class UserPointsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user points
    """
    queryset = UserPoints.objects.all()
    serializer_class = UserPointsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users see their own points, staff see all
        if self.request.user.is_staff:
            return UserPoints.objects.all()
        return UserPoints.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_points(self, request):
        """Get current user's points"""
        points, created = UserPoints.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(points)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add_points(self, request):
        """Add points to current user (for testing)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Staff only'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_id = request.data.get('user_id')
        points = request.data.get('points', 0)
        category = request.data.get('category', 'activity')
        reason = request.data.get('reason', 'Manual addition')
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(id=user_id)
        
        user_points, created = UserPoints.objects.get_or_create(user=user)
        user_points.add_points(points, category)
        
        # Create transaction
        PointTransaction.objects.create(
            user=user,
            transaction_type='earned',
            points=points,
            category=category,
            reason=reason
        )
        
        return Response(UserPointsSerializer(user_points).data)


class PointTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for point transactions (read-only)
    """
    queryset = PointTransaction.objects.all()
    serializer_class = PointTransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['transaction_type', 'category']
    
    def get_queryset(self):
        # Users see their own transactions, staff see all
        if self.request.user.is_staff:
            return PointTransaction.objects.all()
        return PointTransaction.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_transactions(self, request):
        """Get current user's transactions"""
        transactions = PointTransaction.objects.filter(user=request.user).order_by('-created_at')[:50]
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)


class ChallengeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for challenges
    """
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'challenge_type']
    search_fields = ['name', 'description']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active challenges"""
        now = timezone.now()
        active = Challenge.objects.filter(
            status='active',
            start_date__lte=now,
            end_date__gte=now
        )
        serializer = self.get_serializer(active, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a challenge"""
        challenge = self.get_object()
        
        if not challenge.is_active():
            return Response(
                {'error': 'Challenge is not active'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        challenge.participants.add(request.user)
        
        # Create progress tracker
        ChallengeProgress.objects.get_or_create(
            challenge=challenge,
            user=request.user
        )
        
        return Response({'message': 'Joined challenge successfully'})
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a challenge"""
        challenge = self.get_object()
        challenge.participants.remove(request.user)
        return Response({'message': 'Left challenge successfully'})


class ChallengeProgressViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for challenge progress (read-only)
    """
    queryset = ChallengeProgress.objects.all()
    serializer_class = ChallengeProgressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users see their own progress, staff see all
        if self.request.user.is_staff:
            return ChallengeProgress.objects.all()
        return ChallengeProgress.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_progress(self, request):
        """Get current user's challenge progress"""
        progress = ChallengeProgress.objects.filter(user=request.user)
        serializer = self.get_serializer(progress, many=True)
        return Response(serializer.data)
