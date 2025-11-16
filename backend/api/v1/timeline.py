"""
Unified Activity Timeline API
Consolidated view of all activities across entities
"""
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, timedelta

from activity_feed.models import Activity
from core.audit_models import AuditTrail
from task_management.models import Task
from opportunity_management.models import Opportunity
from lead_management.models import Lead
from contact_management.models import Contact


class ActivityTimelineView(views.APIView):
    """
    Unified activity timeline combining multiple sources
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get unified activity timeline
        
        Query params:
        - start_date: Filter activities after this date
        - end_date: Filter activities before this date
        - entity_type: Filter by entity type (lead, contact, opportunity, task)
        - entity_id: Filter by specific entity ID
        - activity_types: Comma-separated list of activity types
        - user_id: Filter by user who performed action
        - limit: Number of results (default 50, max 500)
        """
        # Parse parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        entity_type = request.query_params.get('entity_type')
        entity_id = request.query_params.get('entity_id')
        activity_types = request.query_params.get('activity_types', '').split(',') if request.query_params.get('activity_types') else []
        user_id = request.query_params.get('user_id')
        limit = min(int(request.query_params.get('limit', 50)), 500)
        
        timeline = []
        
        # 1. Activity Feed
        activities = Activity.objects.select_related('user', 'content_type').all()
        
        if start_date:
            activities = activities.filter(timestamp__gte=start_date)
        if end_date:
            activities = activities.filter(timestamp__lte=end_date)
        if entity_type and entity_id:
            try:
                ct = ContentType.objects.get(model=entity_type.lower())
                activities = activities.filter(content_type=ct, object_id=entity_id)
            except ContentType.DoesNotExist:
                pass
        if user_id:
            activities = activities.filter(user_id=user_id)
        
        for activity in activities[:limit]:
            timeline.append({
                'id': f'activity_{activity.id}',
                'type': 'activity',
                'action': activity.action,
                'description': activity.description,
                'entity_type': activity.content_type.model if activity.content_type else None,
                'entity_id': activity.object_id,
                'entity_name': activity.object_repr,
                'user': {
                    'id': activity.user.id if activity.user else None,
                    'name': activity.user.get_full_name() if activity.user else 'System',
                    'email': activity.user.email if activity.user else None
                },
                'metadata': activity.metadata,
                'timestamp': activity.timestamp.isoformat()
            })
        
        # 2. Audit Trail
        audit_entries = AuditTrail.objects.select_related('user', 'content_type').all()
        
        if start_date:
            audit_entries = audit_entries.filter(timestamp__gte=start_date)
        if end_date:
            audit_entries = audit_entries.filter(timestamp__lte=end_date)
        if entity_type and entity_id:
            try:
                ct = ContentType.objects.get(model=entity_type.lower())
                audit_entries = audit_entries.filter(content_type=ct, object_id=entity_id)
            except ContentType.DoesNotExist:
                pass
        if user_id:
            audit_entries = audit_entries.filter(user_id=user_id)
        
        for audit in audit_entries[:limit]:
            timeline.append({
                'id': f'audit_{audit.id}',
                'type': 'audit',
                'action': audit.action,
                'description': audit.description,
                'entity_type': audit.content_type.model if audit.content_type else None,
                'entity_id': audit.object_id,
                'entity_name': audit.object_repr,
                'user': {
                    'id': audit.user.id if audit.user else None,
                    'name': audit.user.get_full_name() if audit.user else 'System',
                    'email': audit.user_email
                },
                'changes': audit.changes,
                'old_values': audit.old_values,
                'new_values': audit.new_values,
                'timestamp': audit.timestamp.isoformat()
            })
        
        # 3. Task updates
        tasks = Task.objects.select_related('assigned_to', 'created_by').all()
        
        if start_date:
            tasks = tasks.filter(updated_at__gte=start_date)
        if end_date:
            tasks = tasks.filter(updated_at__lte=end_date)
        if user_id:
            tasks = tasks.filter(Q(assigned_to_id=user_id) | Q(created_by_id=user_id))
        
        for task in tasks[:limit]:
            timeline.append({
                'id': f'task_{task.id}',
                'type': 'task',
                'action': 'task_update',
                'description': f"Task: {task.title}",
                'entity_type': 'task',
                'entity_id': task.id,
                'entity_name': task.title,
                'user': {
                    'id': task.assigned_to.id if task.assigned_to else None,
                    'name': task.assigned_to.get_full_name() if task.assigned_to else None,
                    'email': task.assigned_to.email if task.assigned_to else None
                },
                'metadata': {
                    'status': task.status,
                    'priority': task.priority,
                    'due_date': task.due_date.isoformat() if task.due_date else None
                },
                'timestamp': task.updated_at.isoformat()
            })
        
        # 4. Opportunity stage changes
        if not entity_type or entity_type == 'opportunity':
            opportunities = Opportunity.objects.select_related('owner').all()
            
            if start_date:
                opportunities = opportunities.filter(updated_at__gte=start_date)
            if end_date:
                opportunities = opportunities.filter(updated_at__lte=end_date)
            if entity_id:
                opportunities = opportunities.filter(id=entity_id)
            if user_id:
                opportunities = opportunities.filter(owner_id=user_id)
            
            for opp in opportunities[:limit]:
                timeline.append({
                    'id': f'opportunity_{opp.id}',
                    'type': 'opportunity',
                    'action': 'stage_change',
                    'description': f"Opportunity: {opp.name}",
                    'entity_type': 'opportunity',
                    'entity_id': opp.id,
                    'entity_name': opp.name,
                    'user': {
                        'id': opp.owner.id if opp.owner else None,
                        'name': opp.owner.get_full_name() if opp.owner else None,
                        'email': opp.owner.email if opp.owner else None
                    },
                    'metadata': {
                        'stage': opp.stage,
                        'amount': float(opp.amount) if opp.amount else None,
                        'close_date': opp.close_date.isoformat() if opp.close_date else None
                    },
                    'timestamp': opp.updated_at.isoformat()
                })
        
        # Sort by timestamp (descending)
        timeline.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Apply limit
        timeline = timeline[:limit]
        
        return Response({
            'count': len(timeline),
            'results': timeline
        })


class EntityTimelineView(views.APIView):
    """
    Get timeline for a specific entity
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, entity_type, entity_id):
        """
        Get all activities related to a specific entity
        """
        try:
            ct = ContentType.objects.get(model=entity_type.lower())
        except ContentType.DoesNotExist:
            return Response(
                {'error': 'Invalid entity type'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        timeline = []
        
        # Activity Feed
        activities = Activity.objects.filter(
            content_type=ct,
            object_id=entity_id
        ).select_related('user').order_by('-timestamp')
        
        for activity in activities:
            timeline.append({
                'id': f'activity_{activity.id}',
                'type': 'activity',
                'action': activity.action,
                'description': activity.description,
                'user': activity.user.get_full_name() if activity.user else 'System',
                'metadata': activity.metadata,
                'timestamp': activity.timestamp.isoformat()
            })
        
        # Audit Trail
        audit_entries = AuditTrail.objects.filter(
            content_type=ct,
            object_id=entity_id
        ).select_related('user').order_by('-timestamp')
        
        for audit in audit_entries:
            timeline.append({
                'id': f'audit_{audit.id}',
                'type': 'audit',
                'action': audit.action,
                'description': audit.description,
                'user': audit.user.get_full_name() if audit.user else 'System',
                'changes': audit.changes,
                'timestamp': audit.timestamp.isoformat()
            })
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return Response({
            'entity_type': entity_type,
            'entity_id': entity_id,
            'count': len(timeline),
            'timeline': timeline
        })


class UserActivityView(views.APIView):
    """
    Get activity timeline for a specific user
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id=None):
        """
        Get all activities performed by a user
        """
        if not user_id:
            user_id = request.user.id
        
        timeline = []
        
        # User's activities
        activities = Activity.objects.filter(
            user_id=user_id
        ).select_related('content_type').order_by('-timestamp')[:100]
        
        for activity in activities:
            timeline.append({
                'id': f'activity_{activity.id}',
                'type': 'activity',
                'action': activity.action,
                'description': activity.description,
                'entity_type': activity.content_type.model if activity.content_type else None,
                'entity_id': activity.object_id,
                'entity_name': activity.object_repr,
                'timestamp': activity.timestamp.isoformat()
            })
        
        # User's audit trail
        audit_entries = AuditTrail.objects.filter(
            user_id=user_id
        ).select_related('content_type').order_by('-timestamp')[:100]
        
        for audit in audit_entries:
            timeline.append({
                'id': f'audit_{audit.id}',
                'type': 'audit',
                'action': audit.action,
                'description': audit.description,
                'entity_type': audit.content_type.model if audit.content_type else None,
                'entity_id': audit.object_id,
                'entity_name': audit.object_repr,
                'timestamp': audit.timestamp.isoformat()
            })
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return Response({
            'user_id': user_id,
            'count': len(timeline),
            'timeline': timeline
        })
