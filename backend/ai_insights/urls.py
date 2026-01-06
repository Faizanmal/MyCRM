from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AIGeneratedContentViewSet,
    AIModelMetricsViewSet,
    ChurnPredictionViewSet,
    NextBestActionViewSet,
    SentimentAnalysisViewSet,
)

router = DefaultRouter()
router.register(r'churn-predictions', ChurnPredictionViewSet, basename='churn-prediction')
router.register(r'next-best-actions', NextBestActionViewSet, basename='next-best-action')
router.register(r'generated-content', AIGeneratedContentViewSet, basename='ai-content')
router.register(r'sentiment', SentimentAnalysisViewSet, basename='sentiment')
router.register(r'model-metrics', AIModelMetricsViewSet, basename='model-metrics')

urlpatterns = [
    path('', include(router.urls)),
]
