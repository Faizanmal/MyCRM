"""
AI Sales Assistant Views
"""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.utils import timezone
from django.db import models

from .models import (
    AIEmailDraft, SalesCoachAdvice, ObjectionResponse,
    CallScript, DealInsight, PersonaProfile, ContactPersonaMatch
)
from .serializers import (
    AIEmailDraftSerializer, GenerateEmailSerializer, SalesCoachAdviceSerializer,
    ObjectionResponseSerializer, HandleObjectionSerializer, CallScriptSerializer,
    DealInsightSerializer, PersonaProfileSerializer,
    ContactPersonaMatchSerializer
)
from .engine import AIEmailGenerator, SalesCoachEngine, PersonaMatchingEngine


class AIEmailDraftViewSet(viewsets.ModelViewSet):
    """Manage AI-generated email drafts"""
    serializer_class = AIEmailDraftSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['email_type', 'tone', 'was_used']
    ordering_fields = ['-created_at']
    
    def get_queryset(self):
        return AIEmailDraft.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate a new email draft"""
        serializer = GenerateEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        from contact_management.models import Contact
        from opportunity_management.models import Opportunity
        
        try:
            contact = Contact.objects.get(id=data['contact_id'])
        except Contact.DoesNotExist:
            return Response({'error': 'Contact not found'}, status=404)
        
        opportunity = None
        if data.get('opportunity_id'):
            try:
                opportunity = Opportunity.objects.get(id=data['opportunity_id'])
            except Opportunity.DoesNotExist:
                pass
        
        generator = AIEmailGenerator()
        draft = generator.generate_email(
            email_type=data['email_type'],
            contact=contact,
            opportunity=opportunity,
            context=data.get('context', ''),
            key_points=data.get('key_points', []),
            tone=data.get('tone', 'professional')
        )
        
        # Set the user
        draft.user = request.user
        draft.save()
        
        return Response(AIEmailDraftSerializer(draft).data, status=201)
    
    @action(detail=True, methods=['post'])
    def use(self, request, pk=None):
        """Mark a draft as used"""
        draft = self.get_object()
        draft.was_used = True
        draft.save()
        return Response({'status': 'marked as used'})
    
    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        """Rate a draft"""
        draft = self.get_object()
        rating = request.data.get('rating')
        feedback = request.data.get('feedback', '')
        
        if not rating or not (1 <= rating <= 5):
            return Response({'error': 'Rating must be 1-5'}, status=400)
        
        draft.user_rating = rating
        draft.user_feedback = feedback
        draft.save()
        
        return Response({'status': 'rated'})
    
    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """Regenerate with different parameters"""
        draft = self.get_object()
        
        generator = AIEmailGenerator()
        new_draft = generator.generate_email(
            email_type=draft.email_type,
            contact=draft.contact,
            opportunity=draft.opportunity,
            context=request.data.get('context', draft.context),
            key_points=request.data.get('key_points', draft.key_points),
            tone=request.data.get('tone', draft.tone)
        )
        
        new_draft.user = request.user
        new_draft.save()
        
        return Response(AIEmailDraftSerializer(new_draft).data, status=201)


class SalesCoachAdviceViewSet(viewsets.ModelViewSet):
    """Manage sales coaching advice"""
    serializer_class = SalesCoachAdviceSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['advice_type', 'priority', 'is_dismissed', 'is_completed']
    ordering_fields = ['-created_at', 'priority']
    
    def get_queryset(self):
        return SalesCoachAdvice.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def analyze_deal(self, request):
        """Get coaching advice for a specific deal"""
        opportunity_id = request.data.get('opportunity_id')
        
        if not opportunity_id:
            return Response({'error': 'opportunity_id required'}, status=400)
        
        from opportunity_management.models import Opportunity
        
        try:
            opportunity = Opportunity.objects.get(id=opportunity_id)
        except Opportunity.DoesNotExist:
            return Response({'error': 'Opportunity not found'}, status=404)
        
        engine = SalesCoachEngine()
        advice_items = engine.analyze_deal(opportunity)
        
        return Response({
            'advice_count': len(advice_items),
            'advice': advice_items
        })
    
    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """Dismiss advice"""
        advice = self.get_object()
        advice.is_dismissed = True
        advice.save()
        return Response({'status': 'dismissed'})
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark advice as completed"""
        advice = self.get_object()
        advice.is_completed = True
        advice.completed_at = timezone.now()
        advice.outcome = request.data.get('outcome', '')
        advice.save()
        return Response({'status': 'completed'})
    
    @action(detail=True, methods=['post'])
    def feedback(self, request, pk=None):
        """Provide feedback on advice"""
        advice = self.get_object()
        was_helpful = request.data.get('was_helpful')
        
        if was_helpful is not None:
            advice.was_helpful = was_helpful
            advice.save()
        
        return Response({'status': 'feedback recorded'})
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending advice"""
        advice = self.get_queryset().filter(
            is_dismissed=False,
            is_completed=False
        ).order_by('priority', '-created_at')
        
        serializer = self.get_serializer(advice, many=True)
        return Response(serializer.data)


class ObjectionResponseViewSet(viewsets.ModelViewSet):
    """Manage objection responses"""
    serializer_class = ObjectionResponseSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['category', 'is_system']
    search_fields = ['objection', 'keywords']
    ordering_fields = ['-times_used', 'category']
    
    def get_queryset(self):
        # Show system responses and user's custom ones
        return ObjectionResponse.objects.filter(
            models.Q(is_system=True) | models.Q(created_by=self.request.user)
        )
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, is_system=False)
    
    @action(detail=False, methods=['post'])
    def handle(self, request):
        """Get response for an objection"""
        serializer = HandleObjectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        engine = SalesCoachEngine()
        response = engine.get_objection_response(
            serializer.validated_data['objection']
        )
        
        return Response(response)


class CallScriptViewSet(viewsets.ModelViewSet):
    """Manage call scripts"""
    serializer_class = CallScriptSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['script_type', 'is_template', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['-times_used', 'name']
    
    def get_queryset(self):
        return CallScript.objects.filter(
            models.Q(user=self.request.user) | models.Q(is_template=True)
        )
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def use(self, request, pk=None):
        """Mark script as used"""
        script = self.get_object()
        script.times_used += 1
        script.save()
        return Response({'status': 'recorded'})
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a script"""
        original = self.get_object()
        
        new_script = CallScript.objects.create(
            user=request.user,
            name=f"{original.name} (Copy)",
            script_type=original.script_type,
            description=original.description,
            opening=original.opening,
            discovery_questions=original.discovery_questions,
            value_propositions=original.value_propositions,
            objection_handlers=original.objection_handlers,
            closing_techniques=original.closing_techniques,
            next_steps=original.next_steps,
        )
        
        return Response(CallScriptSerializer(new_script).data, status=201)


class DealInsightViewSet(viewsets.ReadOnlyModelViewSet):
    """View deal insights"""
    serializer_class = DealInsightSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['insight_type', 'is_acknowledged', 'is_actioned']
    ordering_fields = ['-created_at', 'impact_score']
    
    def get_queryset(self):
        return DealInsight.objects.filter(
            opportunity__owner=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge an insight"""
        insight = self.get_object()
        insight.is_acknowledged = True
        insight.save()
        return Response({'status': 'acknowledged'})
    
    @action(detail=True, methods=['post'])
    def action(self, request, pk=None):
        """Mark insight as actioned"""
        insight = self.get_object()
        insight.is_actioned = True
        insight.save()
        return Response({'status': 'actioned'})


class PersonaProfileViewSet(viewsets.ModelViewSet):
    """Manage buyer personas"""
    serializer_class = PersonaProfileSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_system']
    search_fields = ['name', 'description']
    ordering_fields = ['name', '-contacts_matched', '-deals_won']
    
    def get_queryset(self):
        return PersonaProfile.objects.filter(
            models.Q(is_system=True) | models.Q(created_by=self.request.user)
        )
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['post'])
    def match_contact(self, request):
        """Match a contact to personas"""
        contact_id = request.data.get('contact_id')
        
        if not contact_id:
            return Response({'error': 'contact_id required'}, status=400)
        
        from contact_management.models import Contact
        
        try:
            contact = Contact.objects.get(id=contact_id)
        except Contact.DoesNotExist:
            return Response({'error': 'Contact not found'}, status=404)
        
        engine = PersonaMatchingEngine()
        matches = engine.match_contact_to_personas(contact)
        
        return Response({
            'matches': [
                {
                    'persona_id': str(m['persona'].id),
                    'persona_name': m['persona'].name,
                    'score': m['score'],
                    'factors': m['factors']
                }
                for m in matches
            ]
        })


class ContactPersonaMatchViewSet(viewsets.ReadOnlyModelViewSet):
    """View contact-persona matches"""
    serializer_class = ContactPersonaMatchSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['contact', 'persona']
    ordering_fields = ['-confidence_score']
    
    def get_queryset(self):
        return ContactPersonaMatch.objects.filter(
            contact__assigned_to=self.request.user
        )


class AICoachDashboardView(APIView):
    """AI Sales Coach Dashboard"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get AI coaching dashboard"""
        user = request.user
        today = timezone.now().date()
        
        # Pending advice
        pending_advice = SalesCoachAdvice.objects.filter(
            user=user,
            is_dismissed=False,
            is_completed=False
        )
        
        high_priority = pending_advice.filter(
            priority__in=['high', 'critical']
        ).order_by('priority')[:5]
        
        # Emails generated today
        emails_today = AIEmailDraft.objects.filter(
            user=user,
            created_at__date=today
        ).count()
        
        # Deals needing attention
        from revenue_intelligence.models import DealRiskAlert
        
        deals_needing_attention = DealRiskAlert.objects.filter(
            opportunity__owner=user,
            is_active=True,
            is_resolved=False
        ).values('opportunity').distinct().count()
        
        # Top insights
        top_insights = DealInsight.objects.filter(
            opportunity__owner=user,
            is_acknowledged=False
        ).order_by('-impact_score')[:5]
        
        return Response({
            'pending_advice_count': pending_advice.count(),
            'high_priority_advice': SalesCoachAdviceSerializer(high_priority, many=True).data,
            'emails_generated_today': emails_today,
            'deals_needing_attention': deals_needing_attention,
            'top_insights': DealInsightSerializer(top_insights, many=True).data,
        })



