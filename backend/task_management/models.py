from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Task(models.Model):
    """Task model for managing tasks and activities"""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    TASK_TYPE_CHOICES = [
        ('call', 'Call'),
        ('email', 'Email'),
        ('meeting', 'Meeting'),
        ('follow_up', 'Follow Up'),
        ('proposal', 'Proposal'),
        ('demo', 'Demo'),
        ('other', 'Other'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES, default='other')
    
    # Assignment
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    
    # Status and Priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Dates
    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    reminder_date = models.DateTimeField(null=True, blank=True)
    
    # Related Objects
    contact = models.ForeignKey('contact_management.Contact', on_delete=models.CASCADE, null=True, blank=True, related_name='tasks')
    lead = models.ForeignKey('lead_management.Lead', on_delete=models.CASCADE, null=True, blank=True, related_name='tasks')
    opportunity = models.ForeignKey('opportunity_management.Opportunity', on_delete=models.CASCADE, null=True, blank=True, related_name='tasks')
    
    # Additional Information
    notes = models.TextField(blank=True, null=True)
    tags = models.JSONField(default=list, blank=True)
    custom_fields = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_tasks'
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.assigned_to.get_full_name()}"


class CalendarEvent(models.Model):
    """Calendar events for meetings and appointments"""
    EVENT_TYPE_CHOICES = [
        ('meeting', 'Meeting'),
        ('call', 'Call'),
        ('appointment', 'Appointment'),
        ('demo', 'Demo'),
        ('presentation', 'Presentation'),
        ('other', 'Other'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default='meeting')
    
    # Scheduling
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_all_day = models.BooleanField(default=False)
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Participants
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    attendees = models.ManyToManyField(User, blank=True, related_name='attended_events')
    
    # Location
    location = models.CharField(max_length=200, blank=True, null=True)
    meeting_link = models.URLField(blank=True, null=True)
    
    # Related Objects
    contact = models.ForeignKey('contact_management.Contact', on_delete=models.CASCADE, null=True, blank=True, related_name='events')
    lead = models.ForeignKey('lead_management.Lead', on_delete=models.CASCADE, null=True, blank=True, related_name='events')
    opportunity = models.ForeignKey('opportunity_management.Opportunity', on_delete=models.CASCADE, null=True, blank=True, related_name='events')
    
    # Additional Information
    notes = models.TextField(blank=True, null=True)
    tags = models.JSONField(default=list, blank=True)
    custom_fields = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_calendar_events'
        verbose_name = 'Calendar Event'
        verbose_name_plural = 'Calendar Events'
        ordering = ['start_time']
    
    def __str__(self):
        return f"{self.title} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"


class Reminder(models.Model):
    """Reminders for tasks and events"""
    REMINDER_TYPE_CHOICES = [
        ('task', 'Task'),
        ('event', 'Event'),
        ('follow_up', 'Follow Up'),
        ('custom', 'Custom'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPE_CHOICES, default='custom')
    
    # Scheduling
    reminder_time = models.DateTimeField()
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Assignment
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminders')
    
    # Related Objects
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name='reminders')
    event = models.ForeignKey(CalendarEvent, on_delete=models.CASCADE, null=True, blank=True, related_name='reminders')
    contact = models.ForeignKey('contact_management.Contact', on_delete=models.CASCADE, null=True, blank=True, related_name='reminders')
    lead = models.ForeignKey('lead_management.Lead', on_delete=models.CASCADE, null=True, blank=True, related_name='reminders')
    opportunity = models.ForeignKey('opportunity_management.Opportunity', on_delete=models.CASCADE, null=True, blank=True, related_name='reminders')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crm_reminders'
        verbose_name = 'Reminder'
        verbose_name_plural = 'Reminders'
        ordering = ['reminder_time']
    
    def __str__(self):
        return f"{self.title} - {self.reminder_time.strftime('%Y-%m-%d %H:%M')}"


class TaskTemplate(models.Model):
    """Templates for common tasks"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    task_type = models.CharField(max_length=20, choices=Task.TASK_TYPE_CHOICES, default='other')
    priority = models.CharField(max_length=20, choices=Task.PRIORITY_CHOICES, default='medium')
    default_due_days = models.IntegerField(default=7)  # Days from creation
    notes_template = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'crm_task_templates'
        verbose_name = 'Task Template'
        verbose_name_plural = 'Task Templates'
    
    def __str__(self):
        return self.name
