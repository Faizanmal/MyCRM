from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    OpportunityActivityViewSet,
    OpportunityProductViewSet,
    OpportunityStageViewSet,
    OpportunityViewSet,
    ProductViewSet,
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
