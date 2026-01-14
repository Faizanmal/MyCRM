from django.urls import include, path
from rest_framework.routers import DefaultRouter

# Views are defined in views.py

router = DefaultRouter()
# Register viewsets here

urlpatterns = [
    path('', include(router.urls)),
]
