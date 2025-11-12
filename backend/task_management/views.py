from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Task, CalendarEvent, Reminder, TaskTemplate
from .serializers import (
    TaskSerializer, TaskCreateSerializer, CalendarEventSerializer,
    CalendarEventCreateSerializer, ReminderSerializer, ReminderCreateSerializer,
    TaskTemplateSerializer, TaskBulkUpdateSerializer
)

User = get_user_model()


class TaskViewSet(viewsets.ModelViewSet):
    """Task management viewset"""
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'notes']
    ordering_fields = ['title', 'due_date', 'priority', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer
        return TaskSerializer
    
    def get_queryset(self):
        queryset = Task.objects.all()
        
        # Filter by assigned user if not admin
        if self.request.user.role != 'admin':
            queryset = queryset.filter(
                Q(assigned_to=self.request.user) | Q(created_by=self.request.user)
            )
        
        # Apply additional filters
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        priority_filter = self.request.query_params.get('priority')
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        assigned_to = self.request.query_params.get('assigned_to')
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)
        
        # Filter by due date
        due_today = self.request.query_params.get('due_today')
        if due_today == 'true':
            today = timezone.now().date()
            queryset = queryset.filter(due_date__date=today)
        
        overdue = self.request.query_params.get('overdue')
        if overdue == 'true':
            today = timezone.now().date()
            queryset = queryset.filter(due_date__date__lt=today, status__in=['pending', 'in_progress'])
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark task as completed"""
        task = self.get_object()
        
        if task.status == 'completed':
            return Response(
                {'error': 'Task is already completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.save()
        
        return Response(TaskSerializer(task).data)
    
    @action(detail=True, methods=['post'])
    def reopen(self, request, pk=None):
        """Reopen completed task"""
        task = self.get_object()
        
        if task.status != 'completed':
            return Response(
                {'error': 'Task is not completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task.status = 'pending'
        task.completed_at = None
        task.save()
        
        return Response(TaskSerializer(task).data)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard data for tasks"""
        queryset = self.get_queryset()
        
        # Get task counts by status
        status_counts = {}
        for status_choice in Task.STATUS_CHOICES:
            status_name = status_choice[0]
            count = queryset.filter(status=status_name).count()
            status_counts[status_name] = {
                'name': status_choice[1],
                'count': count
            }
        
        # Get overdue tasks
        today = timezone.now().date()
        overdue_tasks = queryset.filter(
            due_date__date__lt=today,
            status__in=['pending', 'in_progress']
        ).count()
        
        # Get tasks due today
        due_today_tasks = queryset.filter(due_date__date=today).count()
        
        # Get tasks due this week
        week_end = today + timedelta(days=7)
        due_this_week = queryset.filter(
            due_date__date__range=[today, week_end]
        ).count()
        
        return Response({
            'status_counts': status_counts,
            'overdue_tasks': overdue_tasks,
            'due_today_tasks': due_today_tasks,
            'due_this_week_tasks': due_this_week
        })
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update tasks"""
        serializer = TaskBulkUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        task_ids = serializer.validated_data['task_ids']
        updates = serializer.validated_data['updates']
        
        # Check permissions
        tasks = Task.objects.filter(id__in=task_ids)
        if self.request.user.role != 'admin':
            tasks = tasks.filter(
                Q(assigned_to=self.request.user) | Q(created_by=self.request.user)
            )
        
        updated_count = tasks.update(**updates)
        
        return Response({
            'message': f'{updated_count} tasks updated successfully',
            'updated_count': updated_count
        })


class CalendarEventViewSet(viewsets.ModelViewSet):
    """Calendar event management viewset"""
    queryset = CalendarEvent.objects.all()
    serializer_class = CalendarEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['start_time', 'end_time', 'title']
    ordering = ['start_time']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CalendarEventCreateSerializer
        return CalendarEventSerializer
    
    def get_queryset(self):
        queryset = CalendarEvent.objects.all()
        
        # Filter by user if not admin
        if self.request.user.role != 'admin':
            queryset = queryset.filter(
                Q(organizer=self.request.user) | Q(attendees=self.request.user)
            ).distinct()
        
        # Apply date filters
        start_date = self.request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(start_time__date__gte=start_date)
        
        end_date = self.request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(start_time__date__lte=end_date)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)
    
    @action(detail=False, methods=['get'])
    def calendar_view(self, request):
        """Get events for calendar view"""
        queryset = self.get_queryset()
        
        # Get events for current month by default
        today = timezone.now().date()
        month_start = today.replace(day=1)
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1)
        
        events = queryset.filter(
            start_time__date__range=[month_start, month_end]
        )
        
        return Response(CalendarEventSerializer(events, many=True).data)


class ReminderViewSet(viewsets.ModelViewSet):
    """Reminder management viewset"""
    queryset = Reminder.objects.all()
    serializer_class = ReminderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['reminder_time', 'created_at']
    ordering = ['reminder_time']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReminderCreateSerializer
        return ReminderSerializer
    
    def get_queryset(self):
        return Reminder.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming reminders"""
        queryset = self.get_queryset()
        
        # Get reminders for next 7 days
        now = timezone.now()
        week_end = now + timedelta(days=7)
        
        upcoming_reminders = queryset.filter(
            reminder_time__range=[now, week_end],
            is_sent=False
        )
        
        return Response(ReminderSerializer(upcoming_reminders, many=True).data)


class TaskTemplateViewSet(viewsets.ModelViewSet):
    """Task template management viewset"""
    queryset = TaskTemplate.objects.all()
    serializer_class = TaskTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return TaskTemplate.objects.filter(created_by=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def create_task(self, request, pk=None):
        """Create task from template"""
        template = self.get_object()
        
        # Calculate due date
        due_date = None
        if template.default_due_days:
            due_date = timezone.now() + timedelta(days=template.default_due_days)
        
        # Create task from template
        task_data = {
            'title': template.name,
            'description': template.description,
            'task_type': template.task_type,
            'priority': template.priority,
            'due_date': due_date,
            'notes': template.notes_template,
            'assigned_to': request.data.get('assigned_to'),
            'contact': request.data.get('contact'),
            'lead': request.data.get('lead'),
            'opportunity': request.data.get('opportunity')
        }
        
        serializer = TaskCreateSerializer(data=task_data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        
        return Response(TaskSerializer(task).data)
