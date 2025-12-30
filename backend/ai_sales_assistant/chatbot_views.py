"""
AI Sales Assistant - Chatbot Views
Conversational AI endpoints for the CRM assistant
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Q

from .chatbot_models import (
    ConversationSession, ChatMessage, QuickAction,
    PredictiveDealIntelligence, SmartContent
)
from .chatbot_serializers import (
    ConversationSessionSerializer, ConversationSessionListSerializer,
    ChatMessageSerializer, SendMessageSerializer, QuickActionSerializer,
    PredictiveDealIntelligenceSerializer, SmartContentSerializer,
    GenerateSmartContentSerializer, AnalyzeDealSerializer,
    MessageFeedbackSerializer, ActionCompleteSerializer
)
from .chatbot_engine import ChatbotEngine, PredictiveDealEngine, SmartContentGenerator


class ConversationSessionViewSet(viewsets.ModelViewSet):
    """Manage AI chat sessions"""
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ConversationSession.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ConversationSessionListSerializer
        return ConversationSessionSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def send_message(self, request):
        """Send a message to the AI assistant"""
        
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        # Get or create session
        session_id = data.get('session_id')
        if session_id:
            try:
                session = ConversationSession.objects.get(
                    id=session_id,
                    user=request.user
                )
            except ConversationSession.DoesNotExist:
                return Response(
                    {'error': 'Session not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Create new session
            session = ConversationSession.objects.create(
                user=request.user,
                title=data['message'][:50] + '...' if len(data['message']) > 50 else data['message'],
            )
        
        # Save user message
        user_message = ChatMessage.objects.create(
            session=session,
            role='user',
            message_type='text',
            content=data['message'],
            metadata=data.get('context', {}),
        )
        
        # Process with chatbot engine
        engine = ChatbotEngine()
        response = engine.process_message(session, data['message'], request.user)
        
        # Save assistant message
        assistant_message = ChatMessage.objects.create(
            session=session,
            role='assistant',
            message_type=response.get('message_type', 'text'),
            content=response['content'],
            metadata=response.get('metadata', {}),
            attachments=response.get('attachments', []),
        )
        
        # Update session
        session.message_count = session.messages.count()
        session.save()
        
        return Response({
            'session': ConversationSessionSerializer(session).data,
            'user_message': ChatMessageSerializer(user_message).data,
            'assistant_message': ChatMessageSerializer(assistant_message).data,
        })
    
    @action(detail=True, methods=['post'])
    def star(self, request, pk=None):
        """Star/unstar a session"""
        session = self.get_object()
        session.is_starred = not session.is_starred
        session.save()
        return Response({'is_starred': session.is_starred})
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close a session"""
        session = self.get_object()
        session.status = 'closed'
        session.save()
        return Response({'status': 'closed'})
    
    @action(detail=True, methods=['post'])
    def clear(self, request, pk=None):
        """Clear session messages"""
        session = self.get_object()
        session.messages.all().delete()
        session.message_count = 0
        session.save()
        return Response({'status': 'cleared'})
    
    @action(detail=False, methods=['get'])
    def starred(self, request):
        """Get starred sessions"""
        sessions = self.get_queryset().filter(is_starred=True)
        return Response(
            ConversationSessionListSerializer(sessions, many=True).data
        )


class ChatMessageViewSet(viewsets.ReadOnlyModelViewSet):
    """Read chat messages"""
    
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ChatMessage.objects.filter(
            session__user=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def feedback(self, request, pk=None):
        """Provide feedback on a message"""
        message = self.get_object()
        
        serializer = MessageFeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        message.was_helpful = serializer.validated_data['was_helpful']
        message.feedback = serializer.validated_data.get('feedback', '')
        message.save()
        
        return Response({'status': 'feedback recorded'})
    
    @action(detail=True, methods=['post'])
    def take_action(self, request, pk=None):
        """Mark that action was taken on a message"""
        message = self.get_object()
        
        serializer = ActionCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        message.action_taken = True
        message.action_result = serializer.validated_data.get('result', '')
        message.save()
        
        return Response({'status': 'action recorded'})


class QuickActionViewSet(viewsets.ModelViewSet):
    """Manage AI-suggested quick actions"""
    
    serializer_class = QuickActionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['action_type', 'priority', 'is_completed', 'is_dismissed']
    ordering_fields = ['priority', 'created_at']
    
    def get_queryset(self):
        return QuickAction.objects.filter(
            user=self.request.user,
            is_dismissed=False
        )
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark an action as completed"""
        action_item = self.get_object()
        action_item.is_completed = True
        action_item.completed_at = timezone.now()
        action_item.save()
        return Response({'status': 'completed'})
    
    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """Dismiss an action"""
        action_item = self.get_object()
        action_item.is_dismissed = True
        action_item.save()
        return Response({'status': 'dismissed'})
    
    @action(detail=False, methods=['get'])
    def urgent(self, request):
        """Get urgent actions"""
        actions = self.get_queryset().filter(
            priority__in=['high', 'urgent'],
            is_completed=False
        )
        return Response(
            QuickActionSerializer(actions, many=True).data
        )
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate new actions based on CRM data"""
        engine = ChatbotEngine()
        context = engine._build_crm_context(request.user, {})
        
        # Generate actions based on context
        actions_generated = []
        
        # Check for overdue tasks
        if context['tasks']['overdue'] > 0:
            action_item, created = QuickAction.objects.get_or_create(
                user=request.user,
                action_type='task',
                title=f"Complete {context['tasks']['overdue']} overdue tasks",
                defaults={
                    'description': 'You have overdue tasks that need attention',
                    'entity_type': 'task',
                    'entity_id': request.user.id,
                    'priority': 'high',
                    'reason': 'Overdue tasks can impact deal momentum',
                    'expected_impact': 'Improved deal velocity',
                    'source_insight': 'task_analysis',
                }
            )
            if created:
                actions_generated.append(action_item)
        
        return Response({
            'generated': len(actions_generated),
            'actions': QuickActionSerializer(actions_generated, many=True).data,
        })


class PredictiveDealIntelligenceViewSet(viewsets.ReadOnlyModelViewSet):
    """View deal predictions and intelligence"""
    
    serializer_class = PredictiveDealIntelligenceSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['risk_level', 'opportunity']
    ordering_fields = ['win_probability', 'deal_health_score', 'analyzed_at']
    
    def get_queryset(self):
        return PredictiveDealIntelligence.objects.filter(
            opportunity__owner=self.request.user
        )
    
    @action(detail=False, methods=['post'])
    def analyze(self, request):
        """Analyze a specific deal"""
        serializer = AnalyzeDealSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        from opportunity_management.models import Opportunity
        
        try:
            opportunity = Opportunity.objects.get(
                id=serializer.validated_data['opportunity_id'],
                owner=request.user
            )
        except Opportunity.DoesNotExist:
            return Response(
                {'error': 'Opportunity not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        engine = PredictiveDealEngine()
        analysis = engine.analyze_deal(opportunity)
        
        # Save the intelligence
        intel, created = PredictiveDealIntelligence.objects.update_or_create(
            opportunity=opportunity,
            defaults={
                'win_probability': analysis['win_probability'],
                'probability_trend': 'stable',
                'probability_factors': analysis['probability_factors'],
                'expected_close_date': opportunity.expected_close_date or timezone.now().date(),
                'velocity_score': analysis['velocity_score'],
                'days_to_close_prediction': 30,
                'risk_level': analysis['risk_level'],
                'risk_factors': analysis['risk_factors'],
                'risk_mitigation_actions': [],
                'deal_health_score': analysis['deal_health_score'],
                'health_breakdown': {},
                'engagement_score': analysis['engagement_score'],
                'recommended_actions': analysis['recommended_actions'],
                'model_version': analysis['model_version'],
                'confidence_score': analysis['confidence_score'],
            }
        )
        
        return Response(PredictiveDealIntelligenceSerializer(intel).data)
    
    @action(detail=False, methods=['post'])
    def analyze_all(self, request):
        """Analyze all active deals"""
        from opportunity_management.models import Opportunity
        
        opportunities = Opportunity.objects.filter(
            owner=request.user,
            is_closed=False
        )
        
        engine = PredictiveDealEngine()
        analyzed = []
        
        for opportunity in opportunities:
            analysis = engine.analyze_deal(opportunity)
            
            intel, created = PredictiveDealIntelligence.objects.update_or_create(
                opportunity=opportunity,
                defaults={
                    'win_probability': analysis['win_probability'],
                    'probability_trend': 'stable',
                    'probability_factors': analysis['probability_factors'],
                    'expected_close_date': opportunity.expected_close_date or timezone.now().date(),
                    'velocity_score': analysis['velocity_score'],
                    'days_to_close_prediction': 30,
                    'risk_level': analysis['risk_level'],
                    'risk_factors': analysis['risk_factors'],
                    'risk_mitigation_actions': [],
                    'deal_health_score': analysis['deal_health_score'],
                    'health_breakdown': {},
                    'engagement_score': analysis['engagement_score'],
                    'recommended_actions': analysis['recommended_actions'],
                    'model_version': analysis['model_version'],
                    'confidence_score': analysis['confidence_score'],
                }
            )
            analyzed.append(intel)
        
        return Response({
            'analyzed': len(analyzed),
            'intelligence': PredictiveDealIntelligenceSerializer(analyzed, many=True).data,
        })
    
    @action(detail=False, methods=['get'])
    def at_risk(self, request):
        """Get deals at risk"""
        intel = self.get_queryset().filter(
            risk_level__in=['high', 'critical']
        ).order_by('-win_probability')
        
        return Response(
            PredictiveDealIntelligenceSerializer(intel, many=True).data
        )
    
    @action(detail=False, methods=['get'])
    def top_opportunities(self, request):
        """Get top opportunities by win probability"""
        intel = self.get_queryset().filter(
            win_probability__gte=70
        ).order_by('-win_probability')[:10]
        
        return Response(
            PredictiveDealIntelligenceSerializer(intel, many=True).data
        )


class SmartContentViewSet(viewsets.ModelViewSet):
    """Manage AI-generated content"""
    
    serializer_class = SmartContentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['content_type', 'tone', 'was_used']
    ordering_fields = ['created_at', 'personalization_score']
    
    def get_queryset(self):
        return SmartContent.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate smart content"""
        serializer = GenerateSmartContentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        # Build context
        context = data.get('context', {})
        
        contact = None
        opportunity = None
        
        if data.get('contact_id'):
            from contact_management.models import Contact
            try:
                contact = Contact.objects.get(id=data['contact_id'])
                context['contact_name'] = f"{contact.first_name} {contact.last_name}"
                context['company'] = contact.company or ''
                context['email'] = contact.email
            except Contact.DoesNotExist:
                pass
        
        if data.get('opportunity_id'):
            from opportunity_management.models import Opportunity
            try:
                opportunity = Opportunity.objects.get(id=data['opportunity_id'])
                context['deal_name'] = opportunity.name
                context['deal_amount'] = float(opportunity.amount)
                context['deal_stage'] = opportunity.stage
            except Opportunity.DoesNotExist:
                pass
        
        if data.get('prompt'):
            context['prompt'] = data['prompt']
        
        # Generate content
        generator = SmartContentGenerator()
        result = generator.generate_content(
            content_type=data['content_type'],
            context=context,
            tone=data['tone']
        )
        
        # Save the content
        smart_content = SmartContent.objects.create(
            user=request.user,
            content_type=data['content_type'],
            tone=data['tone'],
            contact=contact,
            opportunity=opportunity,
            prompt=data.get('prompt', ''),
            context_data=context,
            title=result.get('title', ''),
            content=result['content'],
            variations=result.get('variations', []),
            personalization_score=result.get('personalization_score', 0),
            personalization_elements=result.get('personalization_elements', []),
        )
        
        return Response(
            SmartContentSerializer(smart_content).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def use(self, request, pk=None):
        """Mark content as used"""
        content = self.get_object()
        content.was_used = True
        content.used_at = timezone.now()
        content.save()
        return Response({'status': 'marked as used'})
    
    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        """Rate content"""
        content = self.get_object()
        rating = request.data.get('rating')
        feedback = request.data.get('feedback', '')
        
        if not rating or not (1 <= rating <= 5):
            return Response(
                {'error': 'Rating must be 1-5'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        content.rating = rating
        content.feedback = feedback
        content.save()
        
        return Response({'status': 'rated'})
    
    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """Regenerate content with different parameters"""
        content = self.get_object()
        
        new_tone = request.data.get('tone', content.tone)
        additional_context = request.data.get('context', {})
        
        context = {**content.context_data, **additional_context}
        
        generator = SmartContentGenerator()
        result = generator.generate_content(
            content_type=content.content_type,
            context=context,
            tone=new_tone
        )
        
        # Create new content
        new_content = SmartContent.objects.create(
            user=request.user,
            content_type=content.content_type,
            tone=new_tone,
            contact=content.contact,
            opportunity=content.opportunity,
            prompt=content.prompt,
            context_data=context,
            title=result.get('title', ''),
            content=result['content'],
            variations=result.get('variations', []),
            personalization_score=result.get('personalization_score', 0),
            personalization_elements=result.get('personalization_elements', []),
        )
        
        return Response(SmartContentSerializer(new_content).data)


class AIAssistantDashboardView(APIView):
    """Dashboard view for AI assistant features"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get AI assistant dashboard data"""
        
        user = request.user
        
        # Get recent sessions
        recent_sessions = ConversationSession.objects.filter(
            user=user
        ).order_by('-last_activity')[:5]
        
        # Get pending actions
        pending_actions = QuickAction.objects.filter(
            user=user,
            is_completed=False,
            is_dismissed=False
        ).order_by('-priority', '-created_at')[:5]
        
        # Get at-risk deals
        at_risk = PredictiveDealIntelligence.objects.filter(
            opportunity__owner=user,
            risk_level__in=['high', 'critical']
        )[:5]
        
        # Get recent content
        recent_content = SmartContent.objects.filter(
            user=user
        ).order_by('-created_at')[:5]
        
        # Build CRM context
        engine = ChatbotEngine()
        crm_context = engine._build_crm_context(user, {})
        
        return Response({
            'overview': {
                'pipeline': crm_context['pipeline'],
                'tasks': crm_context['tasks'],
                'activities': crm_context['activities'],
            },
            'recent_sessions': ConversationSessionListSerializer(
                recent_sessions, many=True
            ).data,
            'pending_actions': QuickActionSerializer(
                pending_actions, many=True
            ).data,
            'at_risk_deals': PredictiveDealIntelligenceSerializer(
                at_risk, many=True
            ).data,
            'recent_content': SmartContentSerializer(
                recent_content, many=True
            ).data,
            'suggestions': [
                {
                    'type': 'insight',
                    'title': 'Pipeline Health',
                    'description': f"You have {crm_context['pipeline']['total_deals']} active deals worth ${crm_context['pipeline']['total_value']:,.0f}",
                },
                {
                    'type': 'action',
                    'title': 'Tasks Due Today',
                    'description': f"{crm_context['tasks']['due_today']} tasks are due today",
                },
            ],
        })
