from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CalendarEventViewSet, ReminderViewSet, TaskTemplateViewSet, TaskViewSet

router = DefaultRouter()
router.register(r'tasks', TaskViewSet)
router.register(r'events', CalendarEventViewSet)
router.register(r'reminders', ReminderViewSet)
router.register(r'templates', TaskTemplateViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
