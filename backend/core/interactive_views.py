"""
Interactive Features Views
API endpoints for interactive UI components
"""

from django.db.models import Q
from django.utils import timezone
from rest_framework import status, views, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .interactive_models import (
    AIRecommendation,
    OnboardingProgress,
    QuickAction,
    SearchQuery,
    SmartFilter,
    UserPreferences,
)
from .interactive_serializers import (
    AIRecommendationSerializer,
    CompleteStepSerializer,
    GlobalSearchSerializer,
    OnboardingProgressSerializer,
    QuickActionSerializer,
    SaveDashboardLayoutSerializer,
    SmartFilterSerializer,
    UserPreferencesSerializer,
)


class UserPreferencesViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user preferences management
    """
    serializer_class = UserPreferencesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserPreferences.objects.filter(user=self.request.user)

    def get_object(self):
        """Get or create user preferences"""
        obj, created = UserPreferences.objects.get_or_create(
            user=self.request.user
        )
        return obj

    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """Get or update current user's preferences"""
        obj = self.get_object()

        if request.method == 'GET':
            serializer = self.get_serializer(obj)
            return Response(serializer.data)

        serializer = self.get_serializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def save_dashboard_layout(self, request):
        """Save dashboard widget layout"""
        serializer = SaveDashboardLayoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        obj = self.get_object()
        obj.dashboard_layout = {
            'widgets': serializer.validated_data['widgets'],
            'updated_at': timezone.now().isoformat()
        }
        obj.save(update_fields=['dashboard_layout', 'updated_at'])

        return Response({'status': 'saved', 'layout': obj.dashboard_layout})

    @action(detail=False, methods=['post'])
    def add_recent_item(self, request):
        """Add an item to recent items"""
        entity_type = request.data.get('type')
        entity_id = request.data.get('id')
        title = request.data.get('title')

        if not all([entity_type, entity_id, title]):
            return Response(
                {'error': 'type, id, and title are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        obj = self.get_object()
        obj.add_recent_item(entity_type, str(entity_id), title)

        return Response({'status': 'added', 'recent_items': obj.recent_items})


class OnboardingProgressViewSet(viewsets.GenericViewSet):
    """
    ViewSet for onboarding progress tracking
    """
    serializer_class = OnboardingProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Get or create onboarding progress"""
        obj, created = OnboardingProgress.objects.get_or_create(
            user=self.request.user
        )
        return obj

    @action(detail=False, methods=['get'])
    def status(self, request):
        """Get current onboarding status"""
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def complete_step(self, request):
        """Mark an onboarding step as complete"""
        serializer = CompleteStepSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        obj = self.get_object()
        completed_steps = obj.complete_step(
            serializer.validated_data['step_id'],
            serializer.validated_data.get('xp_reward', 50)
        )

        return Response({
            'status': 'completed',
            'step_id': serializer.validated_data['step_id'],
            'completed_steps': completed_steps,
            'total_xp': obj.onboarding_xp
        })

    @action(detail=False, methods=['post'])
    def complete_tour(self, request):
        """Mark the product tour as complete"""
        obj = self.get_object()
        obj.tour_completed = True
        obj.tour_completed_at = timezone.now()
        obj.save(update_fields=['tour_completed', 'tour_completed_at'])

        return Response({
            'status': 'tour_completed',
            'completed_at': obj.tour_completed_at.isoformat()
        })

    @action(detail=False, methods=['post'])
    def dismiss_tour(self, request):
        """Dismiss the product tour"""
        obj = self.get_object()
        obj.tour_dismissed = True
        obj.save(update_fields=['tour_dismissed'])

        return Response({'status': 'tour_dismissed'})

    @action(detail=False, methods=['post'])
    def reset(self, request):
        """Reset onboarding progress (for testing)"""
        obj = self.get_object()
        obj.completed_steps = []
        obj.tour_completed = False
        obj.tour_dismissed = False
        obj.tour_completed_at = None
        obj.onboarding_xp = 0
        obj.completed_at = None
        obj.save()

        return Response({'status': 'reset'})


class AIRecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for AI recommendations
    """
    serializer_class = AIRecommendationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AIRecommendation.objects.filter(
            user=self.request.user,
            status='active'
        ).exclude(
            expires_at__lt=timezone.now()
        )

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active recommendations"""
        queryset = self.get_queryset()

        # Optional filtering
        rec_type = request.query_params.get('type')
        impact = request.query_params.get('impact')
        limit = request.query_params.get('limit', 10)

        if rec_type:
            queryset = queryset.filter(recommendation_type=rec_type)
        if impact:
            queryset = queryset.filter(impact=impact)

        queryset = queryset[:int(limit)]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """Dismiss a recommendation"""
        recommendation = self.get_object()

        if not recommendation.dismissable:
            return Response(
                {'error': 'This recommendation cannot be dismissed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        recommendation.dismiss()
        return Response({'status': 'dismissed'})

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark a recommendation as completed"""
        recommendation = self.get_object()
        recommendation.complete()
        return Response({'status': 'completed'})

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Generate new AI recommendations for the user
        This would typically call an AI service
        """
        # Import here to avoid circular imports
        from .ai_recommendation_service import generate_recommendations

        try:
            recommendations = generate_recommendations(request.user)
            return Response({
                'status': 'generated',
                'count': len(recommendations),
                'recommendations': AIRecommendationSerializer(
                    recommendations, many=True
                ).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GlobalSearchView(views.APIView):
    """
    Global search across all CRM entities
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Perform global search"""
        serializer = GlobalSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        query = serializer.validated_data['query']
        types = serializer.validated_data['types']
        limit = serializer.validated_data['limit']

        results = []

        # Search contacts
        if 'contact' in types:
            results.extend(self._search_contacts(query, limit))

        # Search companies/organizations
        if 'company' in types:
            results.extend(self._search_companies(query, limit))

        # Search leads
        if 'lead' in types:
            results.extend(self._search_leads(query, limit))

        # Search opportunities
        if 'opportunity' in types:
            results.extend(self._search_opportunities(query, limit))

        # Search tasks
        if 'task' in types:
            results.extend(self._search_tasks(query, limit))

        # Sort by score and limit
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        results = results[:limit]

        # Save search query for analytics
        SearchQuery.objects.create(
            user=request.user,
            query=query,
            results_count=len(results)
        )

        return Response({
            'query': query,
            'results': results,
            'total': len(results)
        })

    def _search_contacts(self, query, limit):
        """Search contacts"""
        try:
            from contact_management.models import Contact

            contacts = Contact.objects.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query) |
                Q(company__icontains=query)
            )[:limit]

            return [{
                'id': str(c.id),
                'type': 'contact',
                'title': f"{c.first_name} {c.last_name}",
                'subtitle': c.company or c.email,
                'metadata': c.job_title or '',
                'score': 0.9,
                'starred': getattr(c, 'is_starred', False),
                'url': f'/contacts/{c.id}'
            } for c in contacts]
        except Exception:
            return []

    def _search_companies(self, query, limit):
        """Search companies/organizations"""
        try:
            from contact_management.models import Organization

            orgs = Organization.objects.filter(
                Q(name__icontains=query) |
                Q(industry__icontains=query)
            )[:limit]

            return [{
                'id': str(o.id),
                'type': 'company',
                'title': o.name,
                'subtitle': o.industry or '',
                'metadata': f'{o.contacts.count()} contacts',
                'score': 0.85,
                'starred': False,
                'url': f'/organizations/{o.id}'
            } for o in orgs]
        except Exception:
            return []

    def _search_leads(self, query, limit):
        """Search leads"""
        try:
            from lead_management.models import Lead

            leads = Lead.objects.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(company__icontains=query) |
                Q(email__icontains=query)
            )[:limit]

            return [{
                'id': str(l.id),
                'type': 'lead',
                'title': f"{l.first_name} {l.last_name}",
                'subtitle': l.company or l.email,
                'metadata': f'Score: {getattr(l, "score", 0)}',
                'score': 0.8,
                'starred': False,
                'url': f'/leads/{l.id}'
            } for l in leads]
        except Exception:
            return []

    def _search_opportunities(self, query, limit):
        """Search opportunities"""
        try:
            from opportunity_management.models import Opportunity

            opps = Opportunity.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )[:limit]

            return [{
                'id': str(o.id),
                'type': 'opportunity',
                'title': o.name,
                'subtitle': f'${o.amount:,.0f} • {o.stage}' if o.amount else o.stage,
                'metadata': getattr(o, 'company_name', ''),
                'score': 0.85,
                'starred': False,
                'url': f'/opportunities/{o.id}'
            } for o in opps]
        except Exception:
            return []

    def _search_tasks(self, query, limit):
        """Search tasks"""
        try:
            from task_management.models import Task

            tasks = Task.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )[:limit]

            return [{
                'id': str(t.id),
                'type': 'task',
                'title': t.title,
                'subtitle': f'Due: {t.due_date}' if t.due_date else 'No due date',
                'metadata': t.priority or '',
                'score': 0.7,
                'starred': False,
                'url': f'/tasks/{t.id}'
            } for t in tasks]
        except Exception:
            return []


class SmartFilterViewSet(viewsets.ModelViewSet):
    """
    ViewSet for smart/saved filters
    """
    serializer_class = SmartFilterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SmartFilter.objects.filter(
            Q(user=self.request.user) | Q(is_shared=True)
        )

    @action(detail=True, methods=['post'])
    def use(self, request, pk=None):
        """Record filter usage"""
        filter_obj = self.get_object()
        filter_obj.record_use()
        return Response({
            'status': 'recorded',
            'use_count': filter_obj.use_count
        })


class QuickActionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for quick actions
    """
    serializer_class = QuickActionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return QuickAction.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def pinned(self, request):
        """Get pinned quick actions"""
        actions = self.get_queryset().filter(is_pinned=True)
        serializer = self.get_serializer(actions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def toggle_pin(self, request, pk=None):
        """Toggle pin status"""
        action = self.get_object()
        action.is_pinned = not action.is_pinned
        action.save(update_fields=['is_pinned', 'updated_at'])
        return Response({
            'status': 'toggled',
            'is_pinned': action.is_pinned
        })

    @action(detail=True, methods=['post'])
    def record_use(self, request, pk=None):
        """Record action usage"""
        action = self.get_object()
        action.use_count += 1
        action.save(update_fields=['use_count'])
        return Response({
            'status': 'recorded',
            'use_count': action.use_count
        })


class RecentSearchesView(views.APIView):
    """
    Get recent searches for the current user
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get recent search queries"""
        limit = int(request.query_params.get('limit', 10))

        queries = SearchQuery.objects.filter(
            user=request.user
        ).values('query').distinct()[:limit]

        return Response({
            'recent_searches': [q['query'] for q in queries]
        })

    def delete(self, request):
        """Clear search history"""
        SearchQuery.objects.filter(user=request.user).delete()
        return Response({'status': 'cleared'})
