from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
# Register viewsets here

urlpatterns = [
    path('', include(router.urls)),
]
