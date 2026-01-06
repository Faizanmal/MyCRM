"""
Customer Success Views
"""

from datetime import timedelta

from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    CustomerAccount,
    CustomerSuccessAnalytics,
    ExpansionOpportunity,
    NPSSurvey,
    PlaybookExecution,
    RenewalOpportunity,
    SuccessPlaybook,
)
from .serializers import (
    CustomerAccountDetailSerializer,
    CustomerAccountListSerializer,
    CustomerMilestoneSerializer,
    CustomerNoteSerializer,
    CustomerSuccessAnalyticsSerializer,
    ExpansionOpportunitySerializer,
    HealthScoreSerializer,
    NPSSurveySerializer,
    PlaybookExecutionSerializer,
    PlaybookStepSerializer,
    RenewalOpportunitySerializer,
    SendNPSSerializer,
    SuccessPlaybookSerializer,
)
from .services import CustomerSuccessService


class CustomerAccountViewSet(viewsets.ModelViewSet):
    """Manage customer accounts"""
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CustomerAccountDetailSerializer
        return CustomerAccountListSerializer

    def get_queryset(self):
        qs = CustomerAccount.objects.all()

        # Filter by CSM
        csm_id = self.request.query_params.get('csm')
        if csm_id:
            qs = qs.filter(customer_success_manager_id=csm_id)

        # Filter by health status
        health_status = self.request.query_params.get('health')
        if health_status:
            qs = qs.filter(health_scores__status=health_status)

        # Filter by tier
        tier = self.request.query_params.get('tier')
        if tier:
            qs = qs.filter(tier=tier)

        return qs.select_related('customer_success_manager').prefetch_related('health_scores')

    @action(detail=True, methods=['get'])
    def health_history(self, request, _pk=None):
        """Get health score history"""
        account = self.get_object()
        scores = account.health_scores.all()[:30]
        serializer = HealthScoreSerializer(scores, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def recalculate_health(self, request, _pk=None):
        """Recalculate health score"""
        account = self.get_object()
        service = CustomerSuccessService()
        score = service.calculate_health_score(account)
        serializer = HealthScoreSerializer(score)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def milestones(self, request, _pk=None):
        """Get customer milestones"""
        account = self.get_object()
        milestones = account.milestones.all()
        serializer = CustomerMilestoneSerializer(milestones, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_milestone(self, request, _pk=None):
        """Add milestone"""
        account = self.get_object()
        serializer = CustomerMilestoneSerializer(data={
            **request.data,
            'account': account.id
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

    @action(detail=True, methods=['get'])
    def notes(self, request, _pk=None):
        """Get customer notes"""
        account = self.get_object()
        notes = account.notes.all()
        serializer = CustomerNoteSerializer(notes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_note(self, request, _pk=None):
        """Add note"""
        account = self.get_object()
        serializer = CustomerNoteSerializer(data={
            **request.data,
            'account': account.id
        })
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=201)

    @action(detail=True, methods=['get'])
    def renewals(self, request, _pk=None):
        """Get renewal opportunities"""
        account = self.get_object()
        renewals = account.renewals.all()
        serializer = RenewalOpportunitySerializer(renewals, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def expansions(self, request, _pk=None):
        """Get expansion opportunities"""
        account = self.get_object()
        expansions = account.expansion_opportunities.all()
        serializer = ExpansionOpportunitySerializer(expansions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def trigger_playbook(self, request, _pk=None):
        """Trigger a playbook for this account"""
        account = self.get_object()
        playbook_id = request.data.get('playbook_id')

        try:
            playbook = SuccessPlaybook.objects.get(id=playbook_id)
        except SuccessPlaybook.DoesNotExist:
            return Response({'error': 'Playbook not found'}, status=404)

        execution = PlaybookExecution.objects.create(
            account=account,
            playbook=playbook,
            triggered_by=request.user,
            next_step_at=timezone.now()
        )

        serializer = PlaybookExecutionSerializer(execution)
        return Response(serializer.data, status=201)

    @action(detail=False, methods=['get'])
    def at_risk(self, request):
        """Get at-risk accounts"""
        accounts = self.get_queryset().filter(
            health_scores__status__in=['at_risk', 'critical']
        ).distinct()
        serializer = CustomerAccountListSerializer(accounts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def renewals_upcoming(self, request):
        """Get accounts with upcoming renewals"""
        days = int(request.query_params.get('days', 90))
        cutoff = timezone.now().date() + timedelta(days=days)

        accounts = self.get_queryset().filter(
            contract_end__lte=cutoff,
            contract_end__gte=timezone.now().date()
        ).order_by('contract_end')

        serializer = CustomerAccountListSerializer(accounts, many=True)
        return Response(serializer.data)


class SuccessPlaybookViewSet(viewsets.ModelViewSet):
    """Manage success playbooks"""
    serializer_class = SuccessPlaybookSerializer
    permission_classes = [IsAuthenticated]
    queryset = SuccessPlaybook.objects.filter(is_active=True).prefetch_related('steps')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def add_step(self, request, _pk=None):
        """Add step to playbook"""
        playbook = self.get_object()
        serializer = PlaybookStepSerializer(data={
            **request.data,
            'playbook': playbook.id,
            'order': playbook.steps.count()
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)


class PlaybookExecutionViewSet(viewsets.ModelViewSet):
    """Track playbook executions"""
    serializer_class = PlaybookExecutionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PlaybookExecution.objects.all().select_related('account', 'playbook')

    @action(detail=True, methods=['post'])
    def advance(self, request, _pk=None):
        """Advance to next step"""
        execution = self.get_object()
        service = CustomerSuccessService()
        service.advance_playbook(execution)

        serializer = self.get_serializer(execution)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def pause(self, request, _pk=None):
        """Pause execution"""
        execution = self.get_object()
        execution.status = 'paused'
        execution.save()
        return Response({'status': 'paused'})

    @action(detail=True, methods=['post'])
    def resume(self, request, _pk=None):
        """Resume execution"""
        execution = self.get_object()
        execution.status = 'active'
        execution.save()
        return Response({'status': 'resumed'})


class RenewalOpportunityViewSet(viewsets.ModelViewSet):
    """Manage renewals"""
    serializer_class = RenewalOpportunitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RenewalOpportunity.objects.all().select_related('account', 'owner')

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming renewals"""
        days = int(request.query_params.get('days', 90))
        cutoff = timezone.now().date() + timedelta(days=days)

        renewals = self.get_queryset().filter(
            status='upcoming',
            renewal_date__lte=cutoff
        ).order_by('renewal_date')

        serializer = self.get_serializer(renewals, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def at_risk(self, request):
        """Get at-risk renewals"""
        renewals = self.get_queryset().filter(
            status__in=['upcoming', 'in_progress'],
            risk_level__in=['medium', 'high']
        ).order_by('renewal_date')

        serializer = self.get_serializer(renewals, many=True)
        return Response(serializer.data)


class ExpansionOpportunityViewSet(viewsets.ModelViewSet):
    """Manage expansion opportunities"""
    serializer_class = ExpansionOpportunitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ExpansionOpportunity.objects.all().select_related('account', 'owner')

    @action(detail=False, methods=['get'])
    def pipeline(self, request):
        """Get expansion pipeline"""
        opportunities = self.get_queryset().exclude(
            status__in=['closed_won', 'closed_lost']
        )

        pipeline = {
            'identified': opportunities.filter(status='identified').aggregate(
                count=Count('id'), value=Sum('potential_arr_increase')
            ),
            'qualified': opportunities.filter(status='qualified').aggregate(
                count=Count('id'), value=Sum('potential_arr_increase')
            ),
            'proposal': opportunities.filter(status='proposal').aggregate(
                count=Count('id'), value=Sum('potential_arr_increase')
            ),
            'negotiation': opportunities.filter(status='negotiation').aggregate(
                count=Count('id'), value=Sum('potential_arr_increase')
            ),
        }

        return Response(pipeline)


class NPSSurveyViewSet(viewsets.ModelViewSet):
    """Manage NPS surveys"""
    serializer_class = NPSSurveySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return NPSSurvey.objects.all().select_related('account', 'contact')

    @action(detail=False, methods=['post'])
    def send_survey(self, request):
        """Send NPS survey"""
        serializer = SendNPSSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = CustomerSuccessService()
        surveys = service.send_nps_surveys(
            serializer.validated_data['account_id'],
            serializer.validated_data['contact_ids']
        )

        return Response({'sent': len(surveys)})

    @action(detail=False, methods=['get'])
    def score(self, request):
        """Get NPS score"""
        days = int(request.query_params.get('days', 90))
        start_date = timezone.now() - timedelta(days=days)

        surveys = self.get_queryset().filter(
            responded_at__gte=start_date,
            score__isnull=False
        )

        promoters = surveys.filter(classification='promoter').count()
        detractors = surveys.filter(classification='detractor').count()
        total = surveys.count()

        nps = (promoters - detractors) / total * 100 if total > 0 else None

        return Response({
            'nps_score': nps,
            'total_responses': total,
            'promoters': promoters,
            'passives': surveys.filter(classification='passive').count(),
            'detractors': detractors,
        })


class CustomerSuccessAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """View CS analytics"""
    serializer_class = CustomerSuccessAnalyticsSerializer
    permission_classes = [IsAuthenticated]
    queryset = CustomerSuccessAnalytics.objects.all()

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get analytics dashboard"""
        # Current portfolio
        accounts = CustomerAccount.objects.filter(is_active=True)

        total_arr = accounts.aggregate(total=Sum('arr'))['total'] or 0

        # Health distribution
        latest_scores = {}
        for account in accounts:
            score = account.health_scores.first()
            if score:
                latest_scores[score.status] = latest_scores.get(score.status, 0) + 1

        # Upcoming renewals
        upcoming_renewals = RenewalOpportunity.objects.filter(
            status='upcoming',
            renewal_date__lte=timezone.now().date() + timedelta(days=90)
        ).aggregate(
            count=Count('id'),
            arr=Sum('current_arr')
        )

        # Expansion pipeline
        expansion_pipeline = ExpansionOpportunity.objects.exclude(
            status__in=['closed_won', 'closed_lost']
        ).aggregate(
            count=Count('id'),
            potential=Sum('potential_arr_increase')
        )

        return Response({
            'total_accounts': accounts.count(),
            'total_arr': total_arr,
            'health_distribution': latest_scores,
            'upcoming_renewals': upcoming_renewals,
            'expansion_pipeline': expansion_pipeline,
        })
