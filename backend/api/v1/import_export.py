"""
CSV Import/Export Views
Handles bulk data import and export operations
"""
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import HttpResponse
from django.utils import timezone
import csv
import io
import json

from lead_management.models import Lead
from contact_management.models import Contact
from opportunity_management.models import Opportunity
from task_management.models import Task

from .serializers import ImportMappingSerializer


class CSVImportView(views.APIView):
    """
    CSV Import API endpoint
    Supports field mapping, validation, and error reporting
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    SUPPORTED_MODELS = {
        'leads': Lead,
        'contacts': Contact,
        'opportunities': Opportunity,
        'tasks': Task
    }
    
    def post(self, request, resource_type):
        """Import CSV data for a specific resource"""
        if resource_type not in self.SUPPORTED_MODELS:
            return Response(
                {'error': f'Invalid resource type: {resource_type}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate request
        serializer = ImportMappingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        file_obj = serializer.validated_data['file']
        mapping = serializer.validated_data['mapping']
        update_existing = serializer.validated_data.get('update_existing', False)
        skip_errors = serializer.validated_data.get('skip_errors', True)
        
        # Read CSV file
        try:
            decoded_file = file_obj.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(decoded_file))
            
            success_count = 0
            error_count = 0
            errors = []
            
            model_class = self.SUPPORTED_MODELS[resource_type]
            
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (header is row 1)
                try:
                    # Map CSV columns to model fields
                    data = {}
                    for csv_field, model_field in mapping.items():
                        if csv_field in row and row[csv_field]:
                            data[model_field] = row[csv_field]
                    
                    # Add current user as owner/creator
                    if resource_type == 'leads':
                        data['owner'] = request.user
                    elif resource_type == 'contacts':
                        data['created_by'] = request.user
                    elif resource_type == 'opportunities':
                        data['owner'] = request.user
                    elif resource_type == 'tasks':
                        data['created_by'] = request.user
                        data['assigned_to'] = request.user
                    
                    # Create or update record
                    if update_existing and 'email' in data:
                        # Try to update existing record by email
                        existing = model_class.objects.filter(email=data['email']).first()
                        if existing:
                            for key, value in data.items():
                                if key not in ['owner', 'created_by']:
                                    setattr(existing, key, value)
                            existing.save()
                            success_count += 1
                            continue
                    
                    # Create new record
                    model_class.objects.create(**data)
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    errors.append({
                        'row': row_num,
                        'error': str(e),
                        'data': row
                    })
                    
                    if not skip_errors:
                        # Stop on first error
                        break
            
            return Response({
                'success': True,
                'imported': success_count,
                'errors': error_count,
                'error_details': errors[:100]  # Limit to first 100 errors
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to process CSV: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def get(self, request, resource_type):
        """Get sample CSV template"""
        if resource_type not in self.SUPPORTED_MODELS:
            return Response(
                {'error': f'Invalid resource type: {resource_type}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Define sample fields for each resource
        templates = {
            'leads': ['first_name', 'last_name', 'email', 'phone', 'company_name', 
                     'job_title', 'lead_source', 'status', 'priority'],
            'contacts': ['first_name', 'last_name', 'email', 'phone', 'mobile',
                        'company_name', 'job_title', 'contact_type'],
            'opportunities': ['name', 'company_name', 'amount', 'stage', 
                            'probability', 'expected_close_date'],
            'tasks': ['title', 'description', 'task_type', 'priority', 
                     'status', 'due_date']
        }
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{resource_type}_template.csv"'
        
        writer = csv.writer(response)
        writer.writerow(templates[resource_type])
        
        return response


class CSVExportView(views.APIView):
    """
    CSV Export API endpoint
    Exports filtered data to CSV format
    """
    permission_classes = [IsAuthenticated]
    
    SUPPORTED_MODELS = {
        'leads': Lead,
        'contacts': Contact,
        'opportunities': Opportunity,
        'tasks': Task
    }
    
    def get(self, request, resource_type):
        """Export CSV data for a specific resource"""
        if resource_type not in self.SUPPORTED_MODELS:
            return Response(
                {'error': f'Invalid resource type: {resource_type}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        model_class = self.SUPPORTED_MODELS[resource_type]
        queryset = model_class.objects.all()
        
        # Apply filters from query params
        filters = {}
        for key, value in request.query_params.items():
            if key not in ['format', 'fields']:
                filters[key] = value
        
        if filters:
            queryset = queryset.filter(**filters)
        
        # Define export fields
        export_fields = {
            'leads': ['id', 'first_name', 'last_name', 'email', 'phone', 'company_name',
                     'job_title', 'lead_source', 'status', 'priority', 'lead_score',
                     'created_at', 'updated_at'],
            'contacts': ['id', 'first_name', 'last_name', 'email', 'phone', 'mobile',
                        'company_name', 'job_title', 'contact_type', 'status',
                        'created_at', 'updated_at'],
            'opportunities': ['id', 'name', 'company_name', 'amount', 'stage',
                            'probability', 'expected_close_date', 'created_at'],
            'tasks': ['id', 'title', 'task_type', 'priority', 'status', 'due_date',
                     'created_at', 'updated_at']
        }
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{resource_type}_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        fields = export_fields[resource_type]
        writer.writerow(fields)
        
        # Write data rows
        for obj in queryset:
            row = []
            for field in fields:
                value = getattr(obj, field, '')
                if value is None:
                    value = ''
                row.append(str(value))
            writer.writerow(row)
        
        return response
