from django.contrib import admin

from .models import (
    AIGeneratedContent,
    AIModelMetrics,
    ChurnPrediction,
    NextBestAction,
    SentimentAnalysis,
)


@admin.register(ChurnPrediction)
class ChurnPredictionAdmin(admin.ModelAdmin):
    list_display = ['contact', 'risk_level', 'churn_probability', 'confidence_score', 'predicted_at', 'is_expired']
    list_filter = ['risk_level', 'predicted_at']
    search_fields = ['contact__first_name', 'contact__last_name', 'contact__email']
    readonly_fields = ['predicted_at', 'expires_at']


@admin.register(NextBestAction)
class NextBestActionAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_type', 'title', 'priority_score', 'status', 'created_at']
    list_filter = ['action_type', 'status', 'expected_impact', 'entity_type']
    search_fields = ['user__username', 'title', 'description']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']


@admin.register(AIGeneratedContent)
class AIGeneratedContentAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_type', 'subject', 'tone', 'was_used', 'user_rating', 'created_at']
    list_filter = ['content_type', 'tone', 'was_used', 'model_used']
    search_fields = ['user__username', 'subject', 'body']
    readonly_fields = ['created_at']


@admin.register(SentimentAnalysis)
class SentimentAnalysisAdmin(admin.ModelAdmin):
    list_display = ['entity_type', 'entity_id', 'sentiment', 'sentiment_score', 'requires_attention', 'analyzed_at']
    list_filter = ['sentiment', 'entity_type', 'requires_attention']
    search_fields = ['text_content']
    readonly_fields = ['analyzed_at']


@admin.register(AIModelMetrics)
class AIModelMetricsAdmin(admin.ModelAdmin):
    list_display = ['model_name', 'model_version', 'metric_type', 'metric_value', 'sample_size', 'measured_at']
    list_filter = ['model_name', 'metric_type']
    readonly_fields = ['measured_at']
