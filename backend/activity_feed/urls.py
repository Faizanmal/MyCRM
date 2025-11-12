"""
Activity Feed URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ActivityViewSet, CommentViewSet, MentionViewSet,
    NotificationViewSet, FollowViewSet
)

router = DefaultRouter()
router.register(r'activities', ActivityViewSet, basename='activity')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'mentions', MentionViewSet, basename='mention')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'follows', FollowViewSet, basename='follow')

urlpatterns = [
    path('', include(router.urls)),
]
