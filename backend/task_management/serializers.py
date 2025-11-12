from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Task, CalendarEvent, Reminder, TaskTemplate

User = get_user_model()


class TaskTemplateSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = TaskTemplate
        fields = [
            'id', 'name', 'description', 'task_type', 'priority',
            'default_due_days', 'notes_template', 'is_active',
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    contact_name = serializers.CharField(source='contact.full_name', read_only=True)
    lead_name = serializers.CharField(source='lead.full_name', read_only=True)
    opportunity_name = serializers.CharField(source='opportunity.name', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'task_type', 'assigned_to', 'assigned_to_name',
            'created_by', 'created_by_name', 'status', 'priority', 'due_date',
            'completed_at', 'reminder_date', 'contact', 'contact_name',
            'lead', 'lead_name', 'opportunity', 'opportunity_name',
            'notes', 'tags', 'custom_fields', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'task_type', 'assigned_to', 'status',
            'priority', 'due_date', 'reminder_date', 'contact', 'lead',
            'opportunity', 'notes', 'tags', 'custom_fields'
        ]
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class CalendarEventSerializer(serializers.ModelSerializer):
    organizer_name = serializers.CharField(source='organizer.get_full_name', read_only=True)
    attendees_names = serializers.SerializerMethodField()
    contact_name = serializers.CharField(source='contact.full_name', read_only=True)
    lead_name = serializers.CharField(source='lead.full_name', read_only=True)
    opportunity_name = serializers.CharField(source='opportunity.name', read_only=True)
    
    class Meta:
        model = CalendarEvent
        fields = [
            'id', 'title', 'description', 'event_type', 'start_time', 'end_time',
            'is_all_day', 'timezone', 'organizer', 'organizer_name', 'attendees',
            'attendees_names', 'location', 'meeting_link', 'contact', 'contact_name',
            'lead', 'lead_name', 'opportunity', 'opportunity_name',
            'notes', 'tags', 'custom_fields', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'organizer', 'created_at', 'updated_at']
    
    def get_attendees_names(self, obj):
        return [attendee.get_full_name() for attendee in obj.attendees.all()]


class CalendarEventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEvent
        fields = [
            'title', 'description', 'event_type', 'start_time', 'end_time',
            'is_all_day', 'timezone', 'attendees', 'location', 'meeting_link',
            'contact', 'lead', 'opportunity', 'notes', 'tags', 'custom_fields'
        ]
    
    def create(self, validated_data):
        validated_data['organizer'] = self.context['request'].user
        return super().create(validated_data)


class ReminderSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)
    contact_name = serializers.CharField(source='contact.full_name', read_only=True)
    lead_name = serializers.CharField(source='lead.full_name', read_only=True)
    opportunity_name = serializers.CharField(source='opportunity.name', read_only=True)
    
    class Meta:
        model = Reminder
        fields = [
            'id', 'title', 'description', 'reminder_type', 'reminder_time',
            'is_sent', 'sent_at', 'user', 'user_name', 'task', 'task_title',
            'event', 'event_title', 'contact', 'contact_name',
            'lead', 'lead_name', 'opportunity', 'opportunity_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class ReminderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = [
            'title', 'description', 'reminder_type', 'reminder_time',
            'task', 'event', 'contact', 'lead', 'opportunity'
        ]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TaskBulkUpdateSerializer(serializers.Serializer):
    task_ids = serializers.ListField(child=serializers.IntegerField())
    updates = serializers.DictField()
    
    def validate_task_ids(self, value):
        if not value:
            raise serializers.ValidationError("At least one task ID is required.")
        return value
