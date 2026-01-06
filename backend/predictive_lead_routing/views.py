from django.utils import timezone
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    EscalationRule,
    LeadAssignment,
    RebalancingEvent,
    RepSkillAssignment,
    RoutingAnalytics,
    RoutingRule,
    SalesRepProfile,
    SkillCertification,
    TerritoryDefinition,
)
from .serializers import (
    EscalationRuleSerializer,
    GetRecommendationsSerializer,
    LeadAssignmentSerializer,
    ReassignLeadSerializer,
    RebalancingEventSerializer,
    RepSkillAssignmentSerializer,
    RouteLeadSerializer,
    RoutingAnalyticsSerializer,
    RoutingRuleSerializer,
    SalesRepProfileCreateSerializer,
    SalesRepProfileSerializer,
    SkillCertificationSerializer,
    TerritoryDefinitionSerializer,
    TriggerRebalancingSerializer,
)
from .services import AnalyticsService, LeadRoutingService, RepPerformanceService


class SalesRepProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for managing sales rep profiles"""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SalesRepProfile.objects.all().select_related('user')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SalesRepProfileCreateSerializer
        return SalesRepProfileSerializer

    @action(detail=True, methods=['post'])
    def toggle_availability(self, request, _pk=None):
        """Toggle rep availability"""
        profile = self.get_object()
        profile.is_available = not profile.is_available
        profile.save(update_fields=['is_available'])
        return Response({'is_available': profile.is_available})

    @action(detail=True, methods=['post'])
    def update_performance(self, request, _pk=None):
        """Recalculate rep performance metrics"""
        profile = self.get_object()
        service = RepPerformanceService()
        updated = service.update_rep_performance(profile)
        return Response(SalesRepProfileSerializer(updated).data)

    @action(detail=True, methods=['get'])
    def performance_report(self, request, _pk=None):
        """Get detailed performance report"""
        profile = self.get_object()
        service = RepPerformanceService()
        report = service.get_performance_report(profile)
        return Response(report)

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get all available reps"""
        reps = SalesRepProfile.objects.filter(is_available=True)
        serializer = self.get_serializer(reps, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Get rep performance leaderboard"""
        reps = SalesRepProfile.objects.all().order_by('-overall_performance_score')[:20]
        return Response([
            {
                'rank': i + 1,
                'name': rep.user.get_full_name(),
                'score': float(rep.overall_performance_score),
                'win_rate': float(rep.win_rate) * 100,
                'leads_converted': rep.total_leads_converted
            }
            for i, rep in enumerate(reps)
        ])


class RoutingRuleViewSet(viewsets.ModelViewSet):
    """ViewSet for managing routing rules"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RoutingRuleSerializer

    def get_queryset(self):
        return RoutingRule.objects.all().prefetch_related('target_reps')

    @action(detail=True, methods=['post'])
    def toggle(self, request, _pk=None):
        """Toggle rule active status"""
        rule = self.get_object()
        rule.is_active = not rule.is_active
        rule.save(update_fields=['is_active'])
        return Response({'is_active': rule.is_active})

    @action(detail=True, methods=['post'])
    def test(self, request, _pk=None):
        """Test rule against sample lead data"""
        rule = self.get_object()
        lead_data = request.data.get('lead_data', {})

        service = LeadRoutingService()
        matches = service._matches_rule_criteria(lead_data, rule)

        return Response({
            'matches': matches,
            'rule_criteria': rule.criteria,
            'lead_data': lead_data
        })

    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """Reorder rule priorities"""
        order = request.data.get('order', [])

        for i, rule_id in enumerate(order, 1):
            RoutingRule.objects.filter(id=rule_id).update(priority=i)

        return Response({'status': 'reordered'})


class LeadAssignmentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing lead assignments"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LeadAssignmentSerializer
    http_method_names = ['get', 'patch']

    def get_queryset(self):
        return LeadAssignment.objects.all().select_related(
            'lead', 'assigned_to', 'assigned_by', 'previous_assignee', 'routing_rule'
        )

    @action(detail=True, methods=['post'])
    def accept(self, request, _pk=None):
        """Accept a lead assignment"""
        assignment = self.get_object()
        assignment.status = 'accepted'
        assignment.accepted_at = timezone.now()
        assignment.save(update_fields=['status', 'accepted_at'])
        return Response({'status': 'accepted'})

    @action(detail=True, methods=['post'])
    def reject(self, request, _pk=None):
        """Reject a lead assignment"""
        assignment = self.get_object()
        reason = request.data.get('reason', '')

        assignment.status = 'rejected'
        assignment.status_reason = reason
        assignment.save(update_fields=['status', 'status_reason'])

        # Re-route the lead
        service = LeadRoutingService()
        new_assignment, details = service.route_lead(
            assignment.lead,
            assigned_by=request.user
        )

        return Response({
            'status': 'rejected',
            'new_assignment': LeadAssignmentSerializer(new_assignment).data if new_assignment else None
        })

    @action(detail=True, methods=['post'])
    def record_response(self, request, _pk=None):
        """Record first response to lead"""
        assignment = self.get_object()

        if not assignment.first_response_at:
            assignment.first_response_at = timezone.now()
            assignment.save(update_fields=['first_response_at'])

        return Response({'first_response_at': assignment.first_response_at})

    @action(detail=True, methods=['post'])
    def record_outcome(self, request, _pk=None):
        """Record assignment outcome"""
        assignment = self.get_object()
        outcome = request.data.get('outcome')

        assignment.outcome = outcome
        assignment.outcome_at = timezone.now()

        if outcome == 'converted':
            assignment.status = 'converted'
        elif outcome == 'lost':
            assignment.status = 'lost'

        assignment.save(update_fields=['outcome', 'outcome_at', 'status'])

        return Response(LeadAssignmentSerializer(assignment).data)


class LeadRoutingViewSet(viewsets.ViewSet):
    """ViewSet for lead routing operations"""
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def route(self, request):
        """Route a lead to best available rep"""
        serializer = RouteLeadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from lead_management.models import Lead

        lead = Lead.objects.get(id=serializer.validated_data['lead_id'])
        force_rule = None

        if serializer.validated_data.get('force_rule_id'):
            force_rule = RoutingRule.objects.get(id=serializer.validated_data['force_rule_id'])

        service = LeadRoutingService()
        assignment, details = service.route_lead(
            lead,
            assigned_by=request.user,
            force_rule=force_rule
        )

        return Response({
            'assignment': LeadAssignmentSerializer(assignment).data if assignment else None,
            'details': details
        })

    @action(detail=False, methods=['post'])
    def reassign(self, request):
        """Manually reassign a lead"""
        serializer = ReassignLeadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from django.contrib.auth import get_user_model

        from lead_management.models import Lead
        User = get_user_model()

        lead = Lead.objects.get(id=serializer.validated_data['lead_id'])
        new_assignee = User.objects.get(id=serializer.validated_data['new_assignee_id'])

        service = LeadRoutingService()
        assignment = service.reassign_lead(
            lead,
            new_assignee,
            request.user,
            serializer.validated_data.get('reason', '')
        )

        return Response(LeadAssignmentSerializer(assignment).data)

    @action(detail=False, methods=['post'])
    def bulk_route(self, request):
        """Route multiple leads"""
        lead_ids = request.data.get('lead_ids', [])

        from lead_management.models import Lead

        service = LeadRoutingService()
        results = {'success': [], 'failed': []}

        for lead_id in lead_ids:
            try:
                lead = Lead.objects.get(id=lead_id)
                assignment, details = service.route_lead(lead, assigned_by=request.user)

                if assignment:
                    results['success'].append(lead_id)
                else:
                    results['failed'].append({'lead_id': lead_id, 'error': details.get('error')})
            except Exception as e:
                results['failed'].append({'lead_id': lead_id, 'error': str(e)})

        return Response(results)

    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """Get rep recommendations for a lead"""
        serializer = GetRecommendationsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        from lead_management.models import Lead

        lead = Lead.objects.get(id=serializer.validated_data['lead_id'])

        service = LeadRoutingService()
        recommendations = service.get_rep_recommendations(lead)

        return Response(recommendations)

    @action(detail=False, methods=['post'])
    def process_queue(self, request):
        """Process unassigned leads queue"""
        service = LeadRoutingService()
        results = service.process_routing_queue()
        return Response(results)


class EscalationRuleViewSet(viewsets.ModelViewSet):
    """ViewSet for managing escalation rules"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EscalationRuleSerializer

    def get_queryset(self):
        return EscalationRule.objects.all()

    @action(detail=True, methods=['post'])
    def toggle(self, request, _pk=None):
        """Toggle rule active status"""
        rule = self.get_object()
        rule.is_active = not rule.is_active
        rule.save(update_fields=['is_active'])
        return Response({'is_active': rule.is_active})

    @action(detail=False, methods=['post'])
    def process(self, request):
        """Process pending escalations"""
        service = LeadRoutingService()
        results = service.check_and_process_escalations()
        return Response(results)


class RebalancingViewSet(viewsets.ViewSet):
    """ViewSet for lead rebalancing operations"""
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def analysis(self, request):
        """Analyze current lead distribution"""
        from .routing_engine import LeadRebalancer

        reps = list(SalesRepProfile.objects.filter(is_available=True))
        rebalancer = LeadRebalancer()
        analysis = rebalancer.analyze_distribution(reps)

        return Response(analysis)

    @action(detail=False, methods=['post'])
    def plan(self, request):
        """Generate rebalancing plan"""
        from lead_management.models import Lead

        from .routing_engine import LeadRebalancer

        reps = list(SalesRepProfile.objects.filter(is_available=True))
        leads = list(Lead.objects.filter(
            status__in=['new', 'contacted', 'qualified'],
            assigned_to__isnull=False
        ))

        rebalancer = LeadRebalancer()
        plan = rebalancer.calculate_rebalancing_plan(reps, leads)

        return Response(plan)

    @action(detail=False, methods=['post'])
    def execute(self, request):
        """Execute rebalancing"""
        serializer = TriggerRebalancingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = LeadRoutingService()
        result = service.trigger_rebalancing(
            triggered_by=request.user,
            reason=serializer.validated_data['reason']
        )

        return Response(result)

    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get rebalancing history"""
        events = RebalancingEvent.objects.all()[:20]
        serializer = RebalancingEventSerializer(events, many=True)
        return Response(serializer.data)


class SkillCertificationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing skills and certifications"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SkillCertificationSerializer

    def get_queryset(self):
        return SkillCertification.objects.filter(is_active=True)


class RepSkillAssignmentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing rep skill assignments"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RepSkillAssignmentSerializer

    def get_queryset(self):
        return RepSkillAssignment.objects.all().select_related('rep', 'skill')

    @action(detail=True, methods=['post'])
    def verify(self, request, _pk=None):
        """Verify a skill assignment"""
        assignment = self.get_object()
        assignment.verified = True
        assignment.verified_by = request.user
        assignment.save(update_fields=['verified', 'verified_by'])
        return Response({'verified': True})


class TerritoryDefinitionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing territories"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TerritoryDefinitionSerializer

    def get_queryset(self):
        return TerritoryDefinition.objects.all()


class RoutingAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing routing analytics"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RoutingAnalyticsSerializer

    def get_queryset(self):
        return RoutingAnalytics.objects.all()

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get routing dashboard"""
        service = AnalyticsService()
        dashboard = service.get_routing_dashboard()
        return Response(dashboard)
