from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OpportunityViewSet, OpportunityStageViewSet, OpportunityActivityViewSet,
    ProductViewSet, OpportunityProductViewSet
)

router = DefaultRouter()
router.register(r'opportunities', OpportunityViewSet)
router.register(r'stages', OpportunityStageViewSet)
router.register(r'activities', OpportunityActivityViewSet)
router.register(r'products', ProductViewSet)
router.register(r'opportunity-products', OpportunityProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
