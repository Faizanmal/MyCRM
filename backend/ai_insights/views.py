from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from contact_management.models import Contact

from .churn_predictor import ChurnPredictionEngine
from .content_generator import AIContentGenerator
from .models import (
    AIGeneratedContent,
    AIModelMetrics,
    ChurnPrediction,
    NextBestAction,
    SentimentAnalysis,
)
from .next_best_action import NextBestActionEngine
from .serializers import (
    AIContentGenerationRequestSerializer,
    AIGeneratedContentSerializer,
    AIModelMetricsSerializer,
    ChurnPredictionSerializer,
    NextBestActionSerializer,
    SentimentAnalysisSerializer,
)


class ChurnPredictionViewSet(viewsets.ReadOnlyModelViewSet):
    """View churn predictions"""
    serializer_class = ChurnPredictionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['risk_level', 'contact']
    ordering_fields = ['-churn_probability', '-predicted_at']

    def get_queryset(self):
        return ChurnPrediction.objects.filter(
            contact__assigned_to=self.request.user
        )

    @action(detail=False, methods=['post'])
    def predict(self, request):
        """Predict churn for a specific contact"""
        contact_id = request.data.get('contact_id')
        if not contact_id:
            return Response(
                {'error': 'contact_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        contact = get_object_or_404(Contact, id=contact_id)

        # Check permission
        if contact.assigned_to != request.user and contact.created_by != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )

        engine = ChurnPredictionEngine()
        prediction = engine.predict_churn(contact)

        serializer = self.get_serializer(prediction)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def bulk_predict(self, request):
        """Predict churn for all contacts"""
        engine = ChurnPredictionEngine()

        # Get user's contacts
        contacts = Contact.objects.filter(
            assigned_to=request.user,
            contact_type='customer'
        )

        predictions = engine.bulk_predict(contacts)
        serializer = self.get_serializer(predictions, many=True)

        return Response({
            'count': len(predictions),
            'predictions': serializer.data
        })

    @action(detail=False, methods=['get'])
    def high_risk(self, request):
        """Get high-risk contacts"""
        predictions = self.get_queryset().filter(
            risk_level__in=['high', 'critical']
        ).order_by('-churn_probability')

        serializer = self.get_serializer(predictions, many=True)
        return Response(serializer.data)


class NextBestActionViewSet(viewsets.ModelViewSet):
    """Manage next best action recommendations"""
    serializer_class = NextBestActionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['entity_type', 'action_type', 'status', 'expected_impact']
    ordering_fields = ['-priority_score', '-created_at']

    def get_queryset(self):
        return NextBestAction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate new recommendations"""
        limit = request.data.get('limit', 10)

        engine = NextBestActionEngine()
        recommendations = engine.generate_recommendations(request.user, limit=limit)

        serializer = self.get_serializer(recommendations, many=True)
        return Response({
            'count': len(recommendations),
            'recommendations': serializer.data
        })

    @action(detail=True, methods=['post'])
    def accept(self, request, _pk=None):
        """Accept a recommendation"""
        action_obj = self.get_object()
        engine = NextBestActionEngine()
        updated = engine.accept_recommendation(action_obj.id)

        serializer = self.get_serializer(updated)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete(self, request, _pk=None):
        """Mark recommendation as completed"""
        action_obj = self.get_object()
        engine = NextBestActionEngine()
        updated = engine.complete_recommendation(action_obj.id)

        serializer = self.get_serializer(updated)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def dismiss(self, request, _pk=None):
        """Dismiss a recommendation"""
        action_obj = self.get_object()
        engine = NextBestActionEngine()
        updated = engine.dismiss_recommendation(action_obj.id)

        serializer = self.get_serializer(updated)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending recommendations"""
        actions = self.get_queryset().filter(status='pending').order_by('-priority_score')
        serializer = self.get_serializer(actions, many=True)
        return Response(serializer.data)


class AIGeneratedContentViewSet(viewsets.ModelViewSet):
    """Manage AI-generated content"""
    serializer_class = AIGeneratedContentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['content_type', 'was_used', 'tone']
    ordering_fields = ['-created_at']

    def get_queryset(self):
        return AIGeneratedContent.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate content using AI"""
        request_serializer = AIContentGenerationRequestSerializer(data=request.data)
        if not request_serializer.is_valid():
            return Response(
                request_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        data = request_serializer.validated_data
        generator = AIContentGenerator()

        # Generate based on content type
        if data['content_type'] == 'email':
            content = generator.generate_email(
                user=request.user,
                context=data['context'],
                tone=data['tone'],
                custom_prompt=data.get('custom_prompt')
            )
        elif data['content_type'] == 'sms':
            content = generator.generate_sms(
                user=request.user,
                context=data['context']
            )
        elif data['content_type'] == 'social':
            content = generator.generate_social_post(
                user=request.user,
                context=data['context']
            )
        else:
            return Response(
                {'error': 'Unsupported content type'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(content)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_used(self, request, _pk=None):
        """Mark content as used"""
        content = self.get_object()
        content.was_used = True
        content.save()

        serializer = self.get_serializer(content)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def rate(self, request, _pk=None):
        """Rate generated content"""
        content = self.get_object()
        rating = request.data.get('rating')

        if rating and 1 <= rating <= 5:
            content.user_rating = rating
            content.save()
            serializer = self.get_serializer(content)
            return Response(serializer.data)

        return Response(
            {'error': 'Rating must be between 1 and 5'},
            status=status.HTTP_400_BAD_REQUEST
        )


class SentimentAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """View sentiment analysis results"""
    queryset = SentimentAnalysis.objects.all()
    serializer_class = SentimentAnalysisSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['entity_type', 'sentiment', 'requires_attention']
    ordering_fields = ['-analyzed_at']


class AIModelMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """View AI model performance metrics"""
    queryset = AIModelMetrics.objects.all()
    serializer_class = AIModelMetricsSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['model_name', 'metric_type']
    ordering_fields = ['-measured_at']
