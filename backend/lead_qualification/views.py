from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count, Avg, Q

from .models import (
    ScoringRule, QualificationCriteria, LeadScore,
    QualificationWorkflow, WorkflowExecution, LeadEnrichmentData
)
from .serializers import (
    ScoringRuleSerializer, QualificationCriteriaSerializer, LeadScoreSerializer,
    QualificationWorkflowSerializer, WorkflowExecutionSerializer,
    LeadEnrichmentDataSerializer, LeadScoreCalculationSerializer,
    BulkScoreCalculationSerializer
)
from .scoring_engine import LeadScoringEngine, LeadQualificationChecker, recalculate_all_leads
from .tasks import calculate_lead_score_task, enrich_lead_data_task


class ScoringRuleViewSet(viewsets.ModelViewSet):
    """ViewSet for managing scoring rules"""
    queryset = ScoringRule.objects.all()
    serializer_class = ScoringRuleSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get rules grouped by type"""
        rule_type = request.query_params.get('type')
        if rule_type:
            rules = self.queryset.filter(rule_type=rule_type, is_active=True)
        else:
            rules = self.queryset.filter(is_active=True)
        
        serializer = self.get_serializer(rules, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def test_rule(self, request, pk=None):
        """Test a rule against a lead"""
        rule = self.get_object()
        lead_id = request.data.get('lead_id')
        
        if not lead_id:
            return Response(
                {'error': 'lead_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from lead_management.models import Lead
            lead = Lead.objects.get(id=lead_id)
            engine = LeadScoringEngine(lead)
            points = engine._evaluate_rule(rule)
            
            return Response({
                'rule': rule.name,
                'lead': lead.name,
                'points_awarded': points,
                'rule_applied': points != 0
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class QualificationCriteriaViewSet(viewsets.ModelViewSet):
    """ViewSet for managing qualification criteria"""
    queryset = QualificationCriteria.objects.all()
    serializer_class = QualificationCriteriaSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def by_stage(self, request):
        """Get criteria for a specific stage"""
        stage = request.query_params.get('stage')
        if stage:
            criteria = self.queryset.filter(stage=stage, is_active=True)
            serializer = self.get_serializer(criteria, many=True)
            return Response(serializer.data)
        
        return Response({'error': 'stage parameter is required'}, status=400)
    
    @action(detail=True, methods=['post'])
    def check_lead(self, request, pk=None):
        """Check if a lead meets this criteria"""
        criteria = self.get_object()
        lead_id = request.data.get('lead_id')
        
        if not lead_id:
            return Response({'error': 'lead_id is required'}, status=400)
        
        try:
            from lead_management.models import Lead
            lead = Lead.objects.get(id=lead_id)
            meets_criteria, message = LeadQualificationChecker.check_qualification(
                lead, criteria.stage
            )
            
            return Response({
                'lead': lead.name,
                'criteria': criteria.name,
                'meets_criteria': meets_criteria,
                'message': message
            })
        except Exception as e:
            return Response({'error': str(e)}, status=400)


class LeadScoreViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing lead scores (read-only)"""
    queryset = LeadScore.objects.all()
    serializer_class = LeadScoreSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """Calculate score for a lead"""
        serializer = LeadScoreCalculationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        lead_id = serializer.validated_data['lead_id']
        
        try:
            from lead_management.models import Lead
            lead = Lead.objects.get(id=lead_id)
            engine = LeadScoringEngine(lead)
            lead_score = engine.calculate_score()
            
            response_serializer = LeadScoreSerializer(lead_score)
            return Response(response_serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def bulk_calculate(self, request):
        """Calculate scores for multiple leads"""
        serializer = BulkScoreCalculationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if serializer.validated_data.get('recalculate_all'):
            # Trigger background task for all leads
            from .tasks import bulk_recalculate_scores_task
            bulk_recalculate_scores_task.delay()
            return Response({
                'message': 'Bulk recalculation started in background',
                'status': 'queued'
            })
        
        lead_ids = serializer.validated_data.get('lead_ids', [])
        if not lead_ids:
            return Response({'error': 'No lead_ids provided'}, status=400)
        
        # Queue individual calculations
        for lead_id in lead_ids:
            calculate_lead_score_task.delay(lead_id)
        
        return Response({
            'message': f'Score calculation queued for {len(lead_ids)} leads',
            'lead_ids': lead_ids
        })
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get score history for a lead"""
        lead_id = request.query_params.get('lead_id')
        if not lead_id:
            return Response({'error': 'lead_id is required'}, status=400)
        
        scores = self.queryset.filter(lead_id=lead_id).order_by('-calculated_at')[:50]
        serializer = self.get_serializer(scores, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def distribution(self, request):
        """Get score distribution statistics"""
        from django.db.models import Count, Case, When, IntegerField
        
        distribution = LeadScore.objects.filter(
            id__in=LeadScore.objects.values('lead').annotate(
                latest=Count('id')
            ).values('lead')
        ).aggregate(
            score_0_20=Count(Case(When(score__lt=20, then=1))),
            score_20_40=Count(Case(When(score__gte=20, score__lt=40, then=1))),
            score_40_60=Count(Case(When(score__gte=40, score__lt=60, then=1))),
            score_60_80=Count(Case(When(score__gte=60, score__lt=80, then=1))),
            score_80_100=Count(Case(When(score__gte=80, then=1))),
            avg_score=Avg('score')
        )
        
        return Response(distribution)


class QualificationWorkflowViewSet(viewsets.ModelViewSet):
    """ViewSet for managing qualification workflows"""
    queryset = QualificationWorkflow.objects.all()
    serializer_class = QualificationWorkflowSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Manually execute a workflow for a lead"""
        workflow = self.get_object()
        lead_id = request.data.get('lead_id')
        
        if not lead_id:
            return Response({'error': 'lead_id is required'}, status=400)
        
        try:
            from lead_management.models import Lead
            lead = Lead.objects.get(id=lead_id)
            engine = LeadScoringEngine(lead)
            engine._execute_workflow(workflow, {'manual_trigger': True})
            
            return Response({
                'message': 'Workflow executed successfully',
                'workflow': workflow.name,
                'lead': lead.name
            })
        except Exception as e:
            return Response({'error': str(e)}, status=400)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get workflow execution statistics"""
        stats = self.queryset.aggregate(
            total_workflows=Count('id'),
            active_workflows=Count('id', filter=Q(is_active=True)),
            total_executions=Count('executions'),
            successful_executions=Count('executions', filter=Q(executions__status='completed')),
            failed_executions=Count('executions', filter=Q(executions__status='failed'))
        )
        
        return Response(stats)


class WorkflowExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing workflow executions"""
    queryset = WorkflowExecution.objects.all()
    serializer_class = WorkflowExecutionSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent executions"""
        limit = int(request.query_params.get('limit', 50))
        executions = self.queryset.order_by('-started_at')[:limit]
        serializer = self.get_serializer(executions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_workflow(self, request):
        """Get executions for a specific workflow"""
        workflow_id = request.query_params.get('workflow_id')
        if not workflow_id:
            return Response({'error': 'workflow_id is required'}, status=400)
        
        executions = self.queryset.filter(workflow_id=workflow_id).order_by('-started_at')
        serializer = self.get_serializer(executions, many=True)
        return Response(serializer.data)


class LeadEnrichmentDataViewSet(viewsets.ModelViewSet):
    """ViewSet for managing lead enrichment data"""
    queryset = LeadEnrichmentData.objects.all()
    serializer_class = LeadEnrichmentDataSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def enrich(self, request):
        """Trigger enrichment for a lead"""
        lead_id = request.data.get('lead_id')
        source = request.data.get('source', 'api')
        
        if not lead_id:
            return Response({'error': 'lead_id is required'}, status=400)
        
        # Queue enrichment task
        enrich_lead_data_task.delay(lead_id, source)
        
        return Response({
            'message': 'Enrichment queued',
            'lead_id': lead_id,
            'source': source
        })
    
    @action(detail=False, methods=['get'])
    def by_lead(self, request):
        """Get enrichment data for a lead"""
        lead_id = request.query_params.get('lead_id')
        if not lead_id:
            return Response({'error': 'lead_id is required'}, status=400)
        
        enrichment_data = self.queryset.filter(lead_id=lead_id).order_by('-enriched_at')
        serializer = self.get_serializer(enrichment_data, many=True)
        return Response(serializer.data)
