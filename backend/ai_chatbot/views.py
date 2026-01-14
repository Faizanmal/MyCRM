"""
AI Chatbot Views
API endpoints for conversational AI assistant
"""

import time

from django.db import models
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ChatMessage, ChatSession, EmailTemplate, QuickAction
from .serializers import (
    ChatMessageSerializer,
    ChatSessionDetailSerializer,
    ChatSessionListSerializer,
    EmailTemplateSerializer,
    GenerateEmailSerializer,
    MessageFeedbackSerializer,
    QueryDataSerializer,
    QuickActionSerializer,
    SendMessageSerializer,
)
from .services import ChatbotService, DataQueryEngine, EmailGenerator


class ChatSessionViewSet(viewsets.ModelViewSet):
    """Manage chat sessions"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return ChatSessionListSerializer
        return ChatSessionDetailSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message and get AI response"""
        session = self.get_object()
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_message = serializer.validated_data['message']

        # Save user message
        ChatMessage.objects.create(
            session=session,
            role='user',
            content=user_message
        )

        # Update context if provided
        if serializer.validated_data.get('context_type'):
            session.context_type = serializer.validated_data['context_type']
            session.context_id = serializer.validated_data.get('context_id', '')

        # Get AI response
        start_time = time.time()
        chatbot = ChatbotService(request.user)
        response = chatbot.process_message(session, user_message)
        processing_time = int((time.time() - start_time) * 1000)

        # Save assistant message
        assistant_message = ChatMessage.objects.create(
            session=session,
            role='assistant',
            message_type=response.get('type', 'text'),
            content=response.get('content', ''),
            structured_data=response.get('data', {}),
            tokens_used=response.get('tokens', 0),
            model_used=response.get('model', ''),
            processing_time_ms=processing_time
        )

        # Update session
        session.message_count = session.messages.count()
        session.last_message_at = timezone.now()
        if session.message_count == 2:  # First exchange
            session.title = chatbot.generate_title(user_message)
        session.save()

        return Response({
            'message': ChatMessageSerializer(assistant_message).data,
            'session': ChatSessionDetailSerializer(session).data
        })

    @action(detail=True, methods=['post'])
    def clear(self, request, pk=None):
        """Clear session messages"""
        session = self.get_object()
        session.messages.all().delete()
        session.message_count = 0
        session.save()
        return Response({"message": "Session cleared"})


class ChatView(APIView):
    """Quick chat endpoint without session management"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Send a message and get response"""
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = serializer.validated_data['message']
        context_type = serializer.validated_data.get('context_type', '')
        context_id = serializer.validated_data.get('context_id', '')

        # Get or create default session
        session, created = ChatSession.objects.get_or_create(
            user=request.user,
            is_active=True,
            defaults={'title': 'Quick Chat'}
        )

        if context_type:
            session.context_type = context_type
            session.context_id = context_id
            session.save()

        # Process message
        chatbot = ChatbotService(request.user)
        response = chatbot.process_message(session, message)

        # Save messages
        ChatMessage.objects.create(
            session=session,
            role='user',
            content=message
        )

        assistant_message = ChatMessage.objects.create(
            session=session,
            role='assistant',
            message_type=response.get('type', 'text'),
            content=response.get('content', ''),
            structured_data=response.get('data', {})
        )

        session.message_count = session.messages.count()
        session.last_message_at = timezone.now()
        session.save()

        return Response({
            'response': response.get('content', ''),
            'type': response.get('type', 'text'),
            'data': response.get('data', {}),
            'session_id': str(session.id)
        })


class GenerateEmailView(APIView):
    """Generate email drafts using AI"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GenerateEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        generator = EmailGenerator()
        result = generator.generate(
            purpose=serializer.validated_data['purpose'],
            tone=serializer.validated_data['tone'],
            context=serializer.validated_data.get('context', {}),
            recipient_name=serializer.validated_data.get('recipient_name', ''),
            company_name=serializer.validated_data.get('company_name', ''),
            additional_context=serializer.validated_data.get('additional_context', '')
        )

        return Response(result)


class QueryDataView(APIView):
    """Query CRM data using natural language"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = QueryDataSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        engine = DataQueryEngine(request.user)
        result = engine.query(
            query=serializer.validated_data['query'],
            entity_type=serializer.validated_data['entity_type']
        )

        return Response(result)


class QuickActionViewSet(viewsets.ReadOnlyModelViewSet):
    """Get available quick actions"""
    serializer_class = QuickActionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = QuickAction.objects.filter(is_active=True)

        context_type = self.request.query_params.get('context_type')
        if context_type:
            queryset = queryset.filter(
                models.Q(requires_context=False) |
                models.Q(context_types__contains=[context_type])
            )

        return queryset

    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute a quick action"""
        action = self.get_object()

        context = request.data.get('context', {})
        prompt = action.prompt_template

        # Replace variables in template
        for key, value in context.items():
            prompt = prompt.replace(f'{{{{{key}}}}}', str(value))

        # Process with chatbot
        session, _ = ChatSession.objects.get_or_create(
            user=request.user,
            is_active=True,
            defaults={'title': action.name}
        )

        chatbot = ChatbotService(request.user)
        response = chatbot.process_message(session, prompt)

        return Response({
            'response': response.get('content', ''),
            'type': response.get('type', 'text'),
            'data': response.get('data', {})
        })


class EmailTemplateViewSet(viewsets.ModelViewSet):
    """Manage email templates"""
    serializer_class = EmailTemplateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EmailTemplate.objects.filter(
            models.Q(created_by=self.request.user) |
            models.Q(created_by__isnull=True)
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """Generate email from template"""
        template = self.get_object()
        context = request.data.get('context', {})

        subject = template.subject_template
        body = template.body_template

        # Replace variables
        for key, value in context.items():
            subject = subject.replace(f'{{{{{key}}}}}', str(value))
            body = body.replace(f'{{{{{key}}}}}', str(value))

        template.usage_count += 1
        template.save()

        return Response({
            'subject': subject,
            'body': body
        })


class MessageFeedbackView(APIView):
    """Submit feedback on AI messages"""
    permission_classes = [IsAuthenticated]

    def post(self, request, message_id):
        serializer = MessageFeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            message = ChatMessage.objects.get(
                id=message_id,
                session__user=request.user
            )
        except ChatMessage.DoesNotExist:
            return Response(
                {"error": "Message not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        message.is_helpful = serializer.validated_data['is_helpful']
        message.feedback = serializer.validated_data.get('feedback', '')
        message.save()

        return Response({"message": "Feedback recorded"})


class SuggestNextActionsView(APIView):
    """Get AI-suggested next actions for an entity"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        entity_type = request.query_params.get('entity_type')
        entity_id = request.query_params.get('entity_id')

        if not entity_type or not entity_id:
            return Response(
                {"error": "entity_type and entity_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        chatbot = ChatbotService(request.user)
        suggestions = chatbot.suggest_next_actions(entity_type, entity_id)

        return Response({
            'suggestions': suggestions
        })
