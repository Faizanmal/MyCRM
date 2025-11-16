"""
Custom Fields API Views
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.contenttypes.models import ContentType

from core.custom_fields import CustomField, CustomFieldValue, CustomFieldGroup
from rest_framework import serializers


class CustomFieldSerializer(serializers.ModelSerializer):
    model_name = serializers.CharField(source='content_type.model', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = CustomField
        fields = [
            'id', 'name', 'label', 'field_type', 'help_text', 'placeholder',
            'content_type', 'model_name', 'is_required', 'min_length', 'max_length',
            'min_value', 'max_value', 'regex_pattern', 'regex_error_message',
            'options', 'default_value', 'order', 'is_visible', 'is_searchable',
            'is_filterable', 'is_public', 'visible_to_roles', 'editable_by_roles',
            'created_by', 'created_by_name', 'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class CustomFieldValueSerializer(serializers.ModelSerializer):
    field_label = serializers.CharField(source='custom_field.label', read_only=True)
    field_type = serializers.CharField(source='custom_field.field_type', read_only=True)
    display_value = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomFieldValue
        fields = [
            'id', 'custom_field', 'field_label', 'field_type', 'content_type',
            'object_id', 'value_text', 'value_number', 'value_boolean',
            'value_date', 'value_datetime', 'value_json', 'display_value',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_display_value(self, obj):
        return obj.get_value()


class CustomFieldViewSet(viewsets.ModelViewSet):
    """
    Custom field definition management
    """
    queryset = CustomField.objects.select_related('content_type', 'created_by').all()
    serializer_class = CustomFieldSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['content_type', 'field_type', 'is_active', 'is_visible']
    search_fields = ['name', 'label', 'help_text']
    ordering_fields = ['order', 'name', 'created_at']
    ordering = ['order', 'name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by model
        model_name = self.request.query_params.get('model')
        if model_name:
            try:
                ct = ContentType.objects.get(model=model_name.lower())
                queryset = queryset.filter(content_type=ct)
            except ContentType.DoesNotExist:
                pass
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def validate_value(self, request, pk=None):
        """Validate a value against field rules"""
        field = self.get_object()
        value = request.data.get('value')
        
        try:
            field.validate_value(value)
            return Response({'valid': True})
        except Exception as e:
            return Response({
                'valid': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class CustomFieldValueViewSet(viewsets.ModelViewSet):
    """
    Custom field value management
    """
    queryset = CustomFieldValue.objects.select_related('custom_field').all()
    serializer_class = CustomFieldValueSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['custom_field', 'content_type', 'object_id']
    
    @action(detail=False, methods=['get'])
    def for_object(self, request):
        """Get all custom field values for an object"""
        model_name = request.query_params.get('model')
        object_id = request.query_params.get('object_id')
        
        if not model_name or not object_id:
            return Response(
                {'error': 'model and object_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            ct = ContentType.objects.get(model=model_name.lower())
        except ContentType.DoesNotExist:
            return Response(
                {'error': 'Invalid model'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        values = self.queryset.filter(
            content_type=ct,
            object_id=object_id
        )
        
        serializer = self.get_serializer(values, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update custom field values for an object"""
        model_name = request.data.get('model')
        object_id = request.data.get('object_id')
        values = request.data.get('values', {})
        
        if not model_name or not object_id:
            return Response(
                {'error': 'model and object_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            ct = ContentType.objects.get(model=model_name.lower())
        except ContentType.DoesNotExist:
            return Response(
                {'error': 'Invalid model'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        updated = []
        errors = []
        
        for field_id, value in values.items():
            try:
                field = CustomField.objects.get(id=field_id, content_type=ct)
                
                # Get or create value
                field_value, created = CustomFieldValue.objects.get_or_create(
                    custom_field=field,
                    content_type=ct,
                    object_id=object_id
                )
                
                # Set value
                field_value.set_value(value)
                field_value.save()
                
                updated.append({
                    'field_id': field_id,
                    'field_name': field.name,
                    'value': field_value.get_value()
                })
                
            except CustomField.DoesNotExist:
                errors.append({
                    'field_id': field_id,
                    'error': 'Field not found'
                })
            except Exception as e:
                errors.append({
                    'field_id': field_id,
                    'error': str(e)
                })
        
        return Response({
            'updated': updated,
            'errors': errors
        })
