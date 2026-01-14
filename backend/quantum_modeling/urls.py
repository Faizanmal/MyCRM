from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    IoTDataFeedViewSet,
    QuantumModelRegistryViewSet,
    QuantumSimulationViewSet,
    WhatIfScenarioViewSet,
)

router = DefaultRouter()
router.register(r'simulations', QuantumSimulationViewSet, basename='quantum-simulation')
router.register(r'whatif-scenarios', WhatIfScenarioViewSet, basename='whatif-scenario')
router.register(r'models', QuantumModelRegistryViewSet, basename='quantum-model')
router.register(r'data-feeds', IoTDataFeedViewSet, basename='iot-data-feed')

urlpatterns = [
    path('', include(router.urls)),
]
