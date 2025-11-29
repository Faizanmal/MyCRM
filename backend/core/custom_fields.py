"""
Custom Field Builder System
Allows dynamic custom fields on any CRM entity
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

User = get_user_model()


class CustomField(models.Model):
    """
    Define custom fields for any model
    """
    FIELD_TYPES = [
        ('text', 'Text'),
        ('textarea', 'Text Area'),
        ('number', 'Number'),
        ('decimal', 'Decimal'),
        ('boolean', 'Boolean'),
        ('date', 'Date'),
        ('datetime', 'Date & Time'),
        ('email', 'Email'),
        ('url', 'URL'),
        ('phone', 'Phone'),
        ('select', 'Dropdown'),
        ('multiselect', 'Multi-Select'),
        ('radio', 'Radio Buttons'),
        ('checkbox', 'Checkboxes'),
        ('file', 'File Upload'),
    ]
    
    # Field definition
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=200)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    help_text = models.TextField(blank=True)
    placeholder = models.CharField(max_length=200, blank=True)
    
    # Target model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    
    # Validation rules
    is_required = models.BooleanField(default=False)
    min_length = models.IntegerField(null=True, blank=True)
    max_length = models.IntegerField(null=True, blank=True)
    min_value = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    max_value = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    regex_pattern = models.CharField(max_length=500, blank=True)
    regex_error_message = models.CharField(max_length=200, blank=True)
    
    # Options for select/multiselect/radio/checkbox
    options = models.JSONField(
        default=list,
        help_text="List of options for select fields: [{'value': 'opt1', 'label': 'Option 1'}, ...]"
    )
    
    # Default value
    default_value = models.TextField(blank=True)
    
    # Display settings
    order = models.IntegerField(default=0)
    is_visible = models.BooleanField(default=True)
    is_searchable = models.BooleanField(default=False)
    is_filterable = models.BooleanField(default=False)
    
    # Permissions
    is_public = models.BooleanField(default=True)
    visible_to_roles = models.JSONField(default=list, blank=True)
    editable_by_roles = models.JSONField(default=list, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_custom_fields')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['content_type', 'order', 'name']
        unique_together = ['content_type', 'name']
        indexes = [
            models.Index(fields=['content_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.label} ({self.content_type.model})"
    
    def clean(self):
        """Validate field configuration"""
        super().clean()
        
        # Validate options for select fields
        if self.field_type in ['select', 'multiselect', 'radio', 'checkbox']:
            if not self.options:
                raise ValidationError("Options are required for select fields")
            
            # Ensure options is a list of dicts with value and label
            if not isinstance(self.options, list):
                raise ValidationError("Options must be a list")
            
            for opt in self.options:
                if not isinstance(opt, dict) or 'value' not in opt or 'label' not in opt:
                    raise ValidationError("Each option must have 'value' and 'label'")
    
    def validate_value(self, value):
        """Validate a value against this field's rules"""
        if self.is_required and not value:
            raise ValidationError(f"{self.label} is required")
        
        if value:
            # Type-specific validation
            if self.field_type == 'number':
                try:
                    int_value = int(value)
                    if self.min_value and int_value < self.min_value:
                        raise ValidationError(f"{self.label} must be at least {self.min_value}")
                    if self.max_value and int_value > self.max_value:
                        raise ValidationError(f"{self.label} must be at most {self.max_value}")
                except ValueError:
                    raise ValidationError(f"{self.label} must be a number")
            
            elif self.field_type == 'email':
                from django.core.validators import validate_email
                try:
                    validate_email(value)
                except ValidationError:
                    raise ValidationError(f"{self.label} must be a valid email")
            
            elif self.field_type in ['text', 'textarea']:
                if self.min_length and len(value) < self.min_length:
                    raise ValidationError(f"{self.label} must be at least {self.min_length} characters")
                if self.max_length and len(value) > self.max_length:
                    raise ValidationError(f"{self.label} must be at most {self.max_length} characters")
            
            # Regex validation
            if self.regex_pattern:
                import re
                if not re.match(self.regex_pattern, str(value)):
                    error_msg = self.regex_error_message or f"{self.label} format is invalid"
                    raise ValidationError(error_msg)


class CustomFieldValue(models.Model):
    """
    Store custom field values for any object
    """
    custom_field = models.ForeignKey(CustomField, on_delete=models.CASCADE, related_name='values')
    
    # Target object
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    
    # Value storage
    value_text = models.TextField(blank=True)
    value_number = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    value_boolean = models.BooleanField(null=True, blank=True)
    value_date = models.DateField(null=True, blank=True)
    value_datetime = models.DateTimeField(null=True, blank=True)
    value_json = models.JSONField(null=True, blank=True)  # For multiselect, file info, etc.
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['custom_field', 'content_type', 'object_id']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['custom_field']),
        ]
    
    def __str__(self):
        return f"{self.custom_field.label}: {self.get_value()}"
    
    def get_value(self):
        """Get the appropriate value based on field type"""
        field_type = self.custom_field.field_type
        
        if field_type in ['text', 'textarea', 'email', 'url', 'phone']:
            return self.value_text
        elif field_type in ['number', 'decimal']:
            return self.value_number
        elif field_type == 'boolean':
            return self.value_boolean
        elif field_type == 'date':
            return self.value_date
        elif field_type == 'datetime':
            return self.value_datetime
        elif field_type in ['select', 'radio']:
            return self.value_text
        elif field_type in ['multiselect', 'checkbox', 'file']:
            return self.value_json
        
        return None
    
    def set_value(self, value):
        """Set the appropriate value based on field type"""
        field_type = self.custom_field.field_type
        
        # Validate first
        self.custom_field.validate_value(value)
        
        # Clear all value fields
        self.value_text = ''
        self.value_number = None
        self.value_boolean = None
        self.value_date = None
        self.value_datetime = None
        self.value_json = None
        
        # Set appropriate field
        if field_type in ['text', 'textarea', 'email', 'url', 'phone', 'select', 'radio']:
            self.value_text = str(value)
        elif field_type == 'number':
            self.value_number = int(value)
        elif field_type == 'decimal':
            self.value_number = float(value)
        elif field_type == 'boolean':
            self.value_boolean = bool(value)
        elif field_type == 'date':
            self.value_date = value
        elif field_type == 'datetime':
            self.value_datetime = value
        elif field_type in ['multiselect', 'checkbox', 'file']:
            self.value_json = value


class CustomFieldGroup(models.Model):
    """
    Group custom fields for better organization
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    
    order = models.IntegerField(default=0)
    is_collapsible = models.BooleanField(default=True)
    is_collapsed_by_default = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['content_type', 'order', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.content_type.model})"


class CustomFieldGroupMembership(models.Model):
    """
    Assign custom fields to groups
    """
    group = models.ForeignKey(CustomFieldGroup, on_delete=models.CASCADE, related_name='field_memberships')
    custom_field = models.ForeignKey(CustomField, on_delete=models.CASCADE, related_name='group_memberships')
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        unique_together = ['group', 'custom_field']
    
    def __str__(self):
        return f"{self.custom_field.label} in {self.group.name}"
