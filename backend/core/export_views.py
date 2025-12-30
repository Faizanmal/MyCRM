"""
Data Export API Views
Handles export of CRM data in various formats
"""

import csv
import json
import io
import zipfile
from datetime import datetime, timedelta

from django.conf import settings
from django.http import HttpResponse, StreamingHttpResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser

import logging

logger = logging.getLogger(__name__)


class ExportJobViewSet(viewsets.ViewSet):
    """
    ViewSet for managing data export jobs
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def create_export(self, request):
        """
        Create a new export job
        
        Request body:
        {
            "format": "csv" | "json" | "xlsx",
            "entities": ["contacts", "companies", "deals", ...],
            "date_range": "all" | "year" | "quarter" | "month",
            "include_archived": false,
            "include_deleted": false
        }
        """
        data = request.data
        
        export_format = data.get('format', 'csv')
        entities = data.get('entities', [])
        date_range = data.get('date_range', 'all')
        include_archived = data.get('include_archived', False)
        include_deleted = data.get('include_deleted', False)
        
        if not entities:
            return Response(
                {'error': 'At least one entity type must be selected'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create export job record (would be in database in production)
        export_job = {
            'id': str(int(timezone.now().timestamp() * 1000)),
            'user_id': request.user.id,
            'format': export_format,
            'entities': entities,
            'date_range': date_range,
            'include_archived': include_archived,
            'include_deleted': include_deleted,
            'status': 'pending',
            'progress': 0,
            'created_at': timezone.now().isoformat(),
        }
        
        # In production, this would queue a Celery task
        # For now, we process synchronously for smaller exports
        # or return the job ID for async processing
        
        return Response({
            'job_id': export_job['id'],
            'status': 'processing',
            'message': 'Export job created successfully',
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=['get'])
    def job_status(self, request):
        """
        Get status of an export job
        """
        job_id = request.query_params.get('job_id')
        
        if not job_id:
            return Response(
                {'error': 'job_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # In production, fetch from database
        # Mock response for now
        return Response({
            'job_id': job_id,
            'status': 'completed',
            'progress': 100,
            'download_url': f'/api/v1/export/download/{job_id}/',
            'file_size': '2.4 MB',
            'expires_at': (timezone.now() + timedelta(days=7)).isoformat(),
        })
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """
        Get export history for the current user
        """
        # In production, fetch from database
        # Mock response for now
        return Response({
            'exports': [
                {
                    'id': '1',
                    'format': 'csv',
                    'entities': ['contacts', 'companies'],
                    'status': 'completed',
                    'created_at': (timezone.now() - timedelta(days=2)).isoformat(),
                    'file_size': '2.4 MB',
                    'download_url': '/api/v1/export/download/1/',
                },
                {
                    'id': '2',
                    'format': 'json',
                    'entities': ['deals', 'activities'],
                    'status': 'completed',
                    'created_at': (timezone.now() - timedelta(days=7)).isoformat(),
                    'file_size': '5.1 MB',
                    'download_url': '/api/v1/export/download/2/',
                },
            ]
        })
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """
        Download an export file
        """
        # In production, fetch from storage and stream the file
        # For now, generate a sample export based on format
        
        export_format = request.query_params.get('format', 'csv')
        
        if export_format == 'json':
            return self._generate_json_export(request)
        else:
            return self._generate_csv_export(request)
    
    def _generate_csv_export(self, request):
        """Generate CSV export"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['id', 'name', 'email', 'company', 'created_at'])
        
        # Write sample data
        for i in range(100):
            writer.writerow([
                i + 1,
                f'Contact {i + 1}',
                f'contact{i + 1}@example.com',
                f'Company {i % 10 + 1}',
                timezone.now().isoformat(),
            ])
        
        output.seek(0)
        
        response = HttpResponse(output, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="crm_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        return response
    
    def _generate_json_export(self, request):
        """Generate JSON export"""
        data = {
            'exported_at': timezone.now().isoformat(),
            'exported_by': request.user.username,
            'contacts': [
                {
                    'id': i + 1,
                    'name': f'Contact {i + 1}',
                    'email': f'contact{i + 1}@example.com',
                    'company': f'Company {i % 10 + 1}',
                    'created_at': timezone.now().isoformat(),
                }
                for i in range(100)
            ]
        }
        
        response = HttpResponse(
            json.dumps(data, indent=2),
            content_type='application/json'
        )
        response['Content-Disposition'] = f'attachment; filename="crm_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json"'
        
        return response


class DataExportService:
    """
    Service class for handling data exports
    """
    
    def __init__(self, user, config):
        self.user = user
        self.config = config
        self.date_filter = self._get_date_filter()
    
    def _get_date_filter(self):
        """Get date filter based on config"""
        date_range = self.config.get('date_range', 'all')
        now = timezone.now()
        
        if date_range == 'year':
            return Q(created_at__gte=now - timedelta(days=365))
        elif date_range == 'quarter':
            return Q(created_at__gte=now - timedelta(days=90))
        elif date_range == 'month':
            return Q(created_at__gte=now - timedelta(days=30))
        else:
            return Q()  # No filter
    
    def export_contacts(self):
        """Export contacts"""
        try:
            from contact_management.models import Contact
            
            queryset = Contact.objects.filter(
                Q(owner=self.user) | Q(organization__owner=self.user)
            ).filter(self.date_filter)
            
            if not self.config.get('include_archived'):
                queryset = queryset.filter(is_archived=False)
            
            if not self.config.get('include_deleted'):
                queryset = queryset.filter(is_deleted=False)
            
            return list(queryset.values(
                'id', 'first_name', 'last_name', 'email', 'phone',
                'job_title', 'organization__name', 'created_at', 'updated_at'
            ))
        except ImportError:
            return []
    
    def export_companies(self):
        """Export companies/organizations"""
        try:
            from contact_management.models import Organization
            
            queryset = Organization.objects.filter(
                owner=self.user
            ).filter(self.date_filter)
            
            return list(queryset.values(
                'id', 'name', 'website', 'industry', 'size',
                'address', 'created_at', 'updated_at'
            ))
        except ImportError:
            return []
    
    def export_deals(self):
        """Export deals/opportunities"""
        try:
            from opportunity_management.models import Opportunity
            
            queryset = Opportunity.objects.filter(
                Q(owner=self.user) | Q(assigned_to=self.user)
            ).filter(self.date_filter)
            
            return list(queryset.values(
                'id', 'name', 'amount', 'stage', 'status',
                'probability', 'expected_close', 'organization__name',
                'created_at', 'updated_at', 'closed_at'
            ))
        except ImportError:
            return []
    
    def export_tasks(self):
        """Export tasks"""
        try:
            from task_management.models import Task
            
            queryset = Task.objects.filter(
                assigned_to=self.user
            ).filter(self.date_filter)
            
            return list(queryset.values(
                'id', 'title', 'description', 'status', 'priority',
                'due_date', 'completed_at', 'created_at', 'updated_at'
            ))
        except ImportError:
            return []
    
    def export_activities(self):
        """Export activities"""
        try:
            from activity_feed.models import Activity
            
            queryset = Activity.objects.filter(
                actor=self.user
            ).filter(self.date_filter)
            
            return list(queryset.values(
                'id', 'action', 'subject', 'subject_type',
                'created_at'
            ))
        except ImportError:
            return []
    
    def export_all(self):
        """Export all requested entities"""
        entities = self.config.get('entities', [])
        data = {}
        
        entity_methods = {
            'contacts': self.export_contacts,
            'companies': self.export_companies,
            'deals': self.export_deals,
            'tasks': self.export_tasks,
            'activities': self.export_activities,
        }
        
        for entity in entities:
            if entity in entity_methods:
                data[entity] = entity_methods[entity]()
        
        return data
    
    def to_csv(self, data):
        """Convert data to CSV format"""
        output = io.StringIO()
        
        for entity_name, records in data.items():
            if records:
                writer = csv.DictWriter(output, fieldnames=records[0].keys())
                output.write(f"# {entity_name.upper()}\n")
                writer.writeheader()
                writer.writerows(records)
                output.write("\n")
        
        return output.getvalue()
    
    def to_json(self, data):
        """Convert data to JSON format"""
        export_data = {
            'exported_at': timezone.now().isoformat(),
            'exported_by': self.user.username,
            'config': self.config,
            'data': data,
        }
        return json.dumps(export_data, indent=2, default=str)
    
    def to_zip(self, data):
        """Create a ZIP file with separate files for each entity"""
        output = io.BytesIO()
        
        with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zf:
            for entity_name, records in data.items():
                if records:
                    # Add CSV file
                    csv_output = io.StringIO()
                    writer = csv.DictWriter(csv_output, fieldnames=records[0].keys())
                    writer.writeheader()
                    writer.writerows(records)
                    zf.writestr(f'{entity_name}.csv', csv_output.getvalue())
                    
                    # Add JSON file
                    json_output = json.dumps(records, indent=2, default=str)
                    zf.writestr(f'{entity_name}.json', json_output)
        
        output.seek(0)
        return output.getvalue()


# URL patterns for this view (add to urls.py)
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .export_views import ExportJobViewSet

router = DefaultRouter()
router.register(r'export', ExportJobViewSet, basename='export')

urlpatterns = [
    path('api/v1/', include(router.urls)),
]
"""
