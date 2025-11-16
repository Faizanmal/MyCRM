"""
Lead Scoring API Views
"""
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import models

from lead_management.models import Lead
from core.lead_scoring import LeadScoringEngine, RuleBasedScoring
from core.tasks import score_lead, bulk_score_leads, retrain_lead_scoring_model


class LeadScoringView(views.APIView):
    """
    API endpoint for lead scoring operations
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Score a single lead or multiple leads"""
        action = request.data.get('action', 'score')
        lead_id = request.data.get('lead_id')
        lead_ids = request.data.get('lead_ids', [])
        
        if action == 'score' and lead_id:
            # Score single lead
            try:
                lead = Lead.objects.get(id=lead_id)
                engine = LeadScoringEngine()
                engine.load_model('lead_scoring_model.pkl')
                
                score, factors = engine.score_lead(lead)
                
                # Update lead score
                lead.lead_score = score
                lead.save(update_fields=['lead_score', 'updated_at'])
                
                return Response({
                    'success': True,
                    'lead_id': lead_id,
                    'score': score,
                    'factors': factors
                })
                
            except Lead.DoesNotExist:
                return Response(
                    {'error': 'Lead not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        elif action == 'bulk_score':
            # Score multiple leads in background
            task = bulk_score_leads.delay(lead_ids if lead_ids else None)
            
            return Response({
                'success': True,
                'task_id': task.id,
                'message': 'Bulk scoring started in background'
            })
        
        elif action == 'retrain':
            # Retrain model
            if not request.user.is_staff:
                return Response(
                    {'error': 'Only staff can retrain the model'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            task = retrain_lead_scoring_model.delay()
            
            return Response({
                'success': True,
                'task_id': task.id,
                'message': 'Model retraining started'
            })
        
        return Response(
            {'error': 'Invalid action'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def get(self, request):
        """Get lead scoring statistics"""
        leads = Lead.objects.filter(status__in=['new', 'contacted', 'qualified'])
        
        stats = {
            'total_leads': leads.count(),
            'high_score': leads.filter(lead_score__gte=75).count(),
            'medium_score': leads.filter(lead_score__gte=50, lead_score__lt=75).count(),
            'low_score': leads.filter(lead_score__lt=50).count(),
            'average_score': leads.aggregate(avg_score=models.Avg('lead_score'))['avg_score'] or 0
        }
        
        return Response(stats)
