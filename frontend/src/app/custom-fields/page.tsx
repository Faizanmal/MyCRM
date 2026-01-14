'use client';

import { useEffect, useState, useCallback } from 'react';
import {
  Type,
  Hash,
  Calendar,
  Mail,
  Link,
  Phone,
  List,
  CheckSquare,
  ToggleLeft,
  FileText,
  Upload,
  Plus,
  MoreVertical,
  Pencil,
  Trash2,
  GripVertical,
  Settings2,
  Eye,
  EyeOff,
  Search,
  Filter,
  Users,
  Building,
  Target,
  Briefcase,
  ListChecks,
  Loader2,
  AlertCircle,
} from 'lucide-react';
import { toast } from 'sonner';

import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { customFieldsAPI, CustomField } from '@/lib/enterprise-api';

const FIELD_TYPES = [
  { value: 'text', label: 'Text', icon: Type, description: 'Single line text input' },
  { value: 'textarea', label: 'Text Area', icon: FileText, description: 'Multi-line text input' },
  { value: 'number', label: 'Number', icon: Hash, description: 'Numeric values' },
  { value: 'decimal', label: 'Decimal', icon: Hash, description: 'Decimal numbers' },
  { value: 'boolean', label: 'Yes/No', icon: ToggleLeft, description: 'True/false toggle' },
  { value: 'date', label: 'Date', icon: Calendar, description: 'Date picker' },
  { value: 'datetime', label: 'Date & Time', icon: Calendar, description: 'Date and time picker' },
  { value: 'email', label: 'Email', icon: Mail, description: 'Email address with validation' },
  { value: 'url', label: 'URL', icon: Link, description: 'Web address' },
  { value: 'phone', label: 'Phone', icon: Phone, description: 'Phone number' },
  { value: 'select', label: 'Dropdown', icon: List, description: 'Single selection from options' },
  { value: 'multiselect', label: 'Multi-Select', icon: ListChecks, description: 'Multiple selections' },
  { value: 'radio', label: 'Radio Buttons', icon: CheckSquare, description: 'Radio button group' },
  { value: 'checkbox', label: 'Checkboxes', icon: CheckSquare, description: 'Checkbox group' },
  { value: 'file', label: 'File Upload', icon: Upload, description: 'File attachment' },
];

const ENTITY_TYPES = [
  { value: 'contact', label: 'Contacts', icon: Users },
  { value: 'lead', label: 'Leads', icon: Target },
  { value: 'opportunity', label: 'Opportunities', icon: Briefcase },
  { value: 'task', label: 'Tasks', icon: ListChecks },
  { value: 'organization', label: 'Organizations', icon: Building },
];

interface FieldFormData {
  name: string;
  label: string;
  field_type: string;
  content_type: number;
  help_text: string;
  placeholder: string;
  is_required: boolean;
  is_visible: boolean;
  is_searchable: boolean;
  is_filterable: boolean;
  default_value: string;
  options: { value: string; label: string }[];
  min_length?: number;
  max_length?: number;
  min_value?: number;
  max_value?: number;
  regex_pattern?: string;
  regex_error_message?: string;
}

const initialFormData: FieldFormData = {
  name: '',
  label: '',
  field_type: 'text',
  content_type: 0,
  help_text: '',
  placeholder: '',
  is_required: false,
  is_visible: true,
  is_searchable: false,
  is_filterable: false,
  default_value: '',
  options: [],
};

export default function CustomFieldsPage() {
  const [fields, setFields] = useState<CustomField[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeEntity, setActiveEntity] = useState('contact');
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [editingField, setEditingField] = useState<CustomField | null>(null);
  const [formData, setFormData] = useState<FieldFormData>(initialFormData);
  const [saving, setSaving] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [newOption, setNewOption] = useState({ value: '', label: '' });

  const loadFields = useCallback(async () => {
    try {
      setLoading(true);
      const data = await customFieldsAPI.list(activeEntity);
      setFields(data.results || data || []);
    } catch (error) {
      console.error('Failed to load custom fields:', error);
      // Use mock data for demo
      setFields([
        {
          id: '1',
          name: 'customer_type',
          label: 'Customer Type',
          field_type: 'select',
          content_type: 1,
          content_type_name: 'contact',
          help_text: 'Select the type of customer',
          placeholder: 'Select type...',
          is_required: true,
          is_visible: true,
          is_searchable: true,
          is_filterable: true,
          is_public: true,
          default_value: '',
          options: [
            { value: 'enterprise', label: 'Enterprise' },
            { value: 'smb', label: 'Small/Medium Business' },
            { value: 'startup', label: 'Startup' },
          ],
          order: 0,
          visible_to_roles: [],
          editable_by_roles: [],
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          is_active: true,
        },
        {
          id: '2',
          name: 'linkedin_url',
          label: 'LinkedIn Profile',
          field_type: 'url',
          content_type: 1,
          content_type_name: 'contact',
          help_text: 'Link to LinkedIn profile',
          placeholder: 'https://linkedin.com/in/...',
          is_required: false,
          is_visible: true,
          is_searchable: false,
          is_filterable: false,
          is_public: true,
          default_value: '',
          options: [],
          order: 1,
          visible_to_roles: [],
          editable_by_roles: [],
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          is_active: true,
        },
        {
          id: '3',
          name: 'budget_range',
          label: 'Budget Range',
          field_type: 'select',
          content_type: 3,
          content_type_name: 'opportunity',
          help_text: 'Expected budget for this deal',
          placeholder: 'Select budget range',
          is_required: true,
          is_visible: true,
          is_searchable: false,
          is_filterable: true,
          is_public: true,
          default_value: '',
          options: [
            { value: 'under_10k', label: 'Under $10,000' },
            { value: '10k_50k', label: '$10,000 - $50,000' },
            { value: '50k_100k', label: '$50,000 - $100,000' },
            { value: 'over_100k', label: 'Over $100,000' },
          ],
          order: 0,
          visible_to_roles: [],
          editable_by_roles: [],
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          is_active: true,
        },
      ].filter(f => f.content_type_name === activeEntity));
    } finally {
      setLoading(false);
    }
  }, [activeEntity]);

  useEffect(() => {
    loadFields();
  }, [loadFields]);

  const handleCreateField = async () => {
    if (!formData.name || !formData.label || !formData.field_type) {
      toast.error('Please fill in all required fields');
      return;
    }

    // Validate options for select fields
    if (['select', 'multiselect', 'radio', 'checkbox'].includes(formData.field_type) && formData.options.length === 0) {
      toast.error('Please add at least one option for this field type');
      return;
    }

    try {
      setSaving(true);
      if (editingField) {
        await customFieldsAPI.update(editingField.id, formData);
        toast.success('Field updated successfully');
      } else {
        await customFieldsAPI.create(formData);
        toast.success('Field created successfully');
      }
      setShowCreateDialog(false);
      setEditingField(null);
      setFormData(initialFormData);
      loadFields();
    } catch (error) {
      console.error('Failed to save field:', error);
      toast.error('Failed to save field');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteField = async (fieldId: string) => {
    if (!confirm('Are you sure you want to delete this field? This action cannot be undone.')) {
      return;
    }

    try {
      await customFieldsAPI.delete(fieldId);
      toast.success('Field deleted successfully');
      loadFields();
    } catch (error) {
      console.error('Failed to delete field:', error);
      toast.error('Failed to delete field');
    }
  };

  const handleEditField = (field: CustomField) => {
    setEditingField(field);
    setFormData({
      name: field.name,
      label: field.label,
      field_type: field.field_type,
      content_type: field.content_type,
      help_text: field.help_text,
      placeholder: field.placeholder,
      is_required: field.is_required,
      is_visible: field.is_visible,
      is_searchable: field.is_searchable,
      is_filterable: field.is_filterable,
      default_value: field.default_value,
      options: field.options || [],
      min_length: field.min_length,
      max_length: field.max_length,
      min_value: field.min_value,
      max_value: field.max_value,
      regex_pattern: field.regex_pattern,
      regex_error_message: field.regex_error_message,
    });
    setShowCreateDialog(true);
  };

  const addOption = () => {
    if (!newOption.value || !newOption.label) {
      toast.error('Please enter both value and label for the option');
      return;
    }
    setFormData({
      ...formData,
      options: [...formData.options, { ...newOption }],
    });
    setNewOption({ value: '', label: '' });
  };

  const removeOption = (index: number) => {
    setFormData({
      ...formData,
      options: formData.options.filter((_, i) => i !== index),
    });
  };

  const getFieldTypeIcon = (type: string) => {
    const fieldType = FIELD_TYPES.find(ft => ft.value === type);
    return fieldType ? fieldType.icon : Type;
  };

  const filteredFields = fields.filter(field =>
    field.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
    field.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-4 lg:p-6 space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-2xl lg:text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <Settings2 className="w-8 h-8 text-purple-600" />
                Custom Field Builder
              </h1>
              <p className="text-gray-500 dark:text-gray-400 mt-1">
                Create and manage custom fields for your CRM entities
              </p>
            </div>
            <Button
              onClick={() => {
                setEditingField(null);
                setFormData({ ...initialFormData });
                setShowCreateDialog(true);
              }}
              className="bg-linear-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700"
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Custom Field
            </Button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <Card className="bg-linear-to-br from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20 border-purple-200 dark:border-purple-800">
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-purple-700 dark:text-purple-300">{fields.length}</div>
                <div className="text-sm text-purple-600 dark:text-purple-400">Total Fields</div>
              </CardContent>
            </Card>
            <Card className="bg-linear-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border-green-200 dark:border-green-800">
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-green-700 dark:text-green-300">
                  {fields.filter(f => f.is_visible).length}
                </div>
                <div className="text-sm text-green-600 dark:text-green-400">Visible Fields</div>
              </CardContent>
            </Card>
            <Card className="bg-linear-to-br from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 border-blue-200 dark:border-blue-800">
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-blue-700 dark:text-blue-300">
                  {fields.filter(f => f.is_required).length}
                </div>
                <div className="text-sm text-blue-600 dark:text-blue-400">Required Fields</div>
              </CardContent>
            </Card>
            <Card className="bg-linear-to-br from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 border-amber-200 dark:border-amber-800">
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-amber-700 dark:text-amber-300">
                  {fields.filter(f => f.is_searchable).length}
                </div>
                <div className="text-sm text-amber-600 dark:text-amber-400">Searchable Fields</div>
              </CardContent>
            </Card>
          </div>

          {/* Entity Tabs */}
          <Tabs value={activeEntity} onValueChange={setActiveEntity}>
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
              <TabsList className="grid grid-cols-5 w-full sm:w-auto">
                {ENTITY_TYPES.map(entity => (
                  <TabsTrigger key={entity.value} value={entity.value} className="flex items-center gap-2">
                    <entity.icon className="w-4 h-4" />
                    <span className="hidden sm:inline">{entity.label}</span>
                  </TabsTrigger>
                ))}
              </TabsList>

              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <Input
                  placeholder="Search fields..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 w-full sm:w-64"
                />
              </div>
            </div>

            {ENTITY_TYPES.map(entity => (
              <TabsContent key={entity.value} value={entity.value} className="mt-0">
                {loading ? (
                  <div className="flex items-center justify-center py-12">
                    <Loader2 className="w-8 h-8 animate-spin text-purple-600" />
                  </div>
                ) : filteredFields.length === 0 ? (
                  <Card className="border-dashed">
                    <CardContent className="flex flex-col items-center justify-center py-12">
                      <Settings2 className="w-12 h-12 text-gray-300 dark:text-gray-600 mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                        No custom fields yet
                      </h3>
                      <p className="text-gray-500 dark:text-gray-400 text-center max-w-md mb-4">
                        Create custom fields to capture additional information specific to your business needs.
                      </p>
                      <Button
                        onClick={() => {
                          setEditingField(null);
                          setFormData({ ...initialFormData });
                          setShowCreateDialog(true);
                        }}
                      >
                        <Plus className="w-4 h-4 mr-2" />
                        Create First Field
                      </Button>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="space-y-3">
                    {filteredFields.map((field, index) => {
                      const FieldIcon = getFieldTypeIcon(field.field_type);
                      return (
                        <Card key={field.id} className="hover:shadow-md transition-shadow">
                          <CardContent className="p-4">
                            <div className="flex items-start gap-4">
                              <div className="flex items-center gap-2 text-gray-400 cursor-grab">
                                <GripVertical className="w-5 h-5" />
                                <span className="text-sm font-medium">{index + 1}</span>
                              </div>

                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-3 mb-2">
                                  <div className="p-2 rounded-lg bg-purple-100 dark:bg-purple-900/30">
                                    <FieldIcon className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                                  </div>
                                  <div className="flex-1 min-w-0">
                                    <h3 className="font-semibold text-gray-900 dark:text-white truncate">
                                      {field.label}
                                    </h3>
                                    <p className="text-sm text-gray-500 dark:text-gray-400 font-mono">
                                      {field.name}
                                    </p>
                                  </div>
                                </div>

                                {field.help_text && (
                                  <p className="text-sm text-gray-500 dark:text-gray-400 mb-2 ml-12">
                                    {field.help_text}
                                  </p>
                                )}

                                <div className="flex flex-wrap gap-2 ml-12">
                                  <Badge variant="outline" className="capitalize">
                                    {field.field_type.replace('_', ' ')}
                                  </Badge>
                                  {field.is_required && (
                                    <Badge className="bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400">
                                      Required
                                    </Badge>
                                  )}
                                  {field.is_searchable && (
                                    <Badge className="bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
                                      <Search className="w-3 h-3 mr-1" />
                                      Searchable
                                    </Badge>
                                  )}
                                  {field.is_filterable && (
                                    <Badge className="bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400">
                                      <Filter className="w-3 h-3 mr-1" />
                                      Filterable
                                    </Badge>
                                  )}
                                  {!field.is_visible && (
                                    <Badge variant="secondary">
                                      <EyeOff className="w-3 h-3 mr-1" />
                                      Hidden
                                    </Badge>
                                  )}
                                </div>
                              </div>

                              <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                  <Button variant="ghost" size="icon">
                                    <MoreVertical className="w-4 h-4" />
                                  </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end">
                                  <DropdownMenuItem onClick={() => handleEditField(field)}>
                                    <Pencil className="w-4 h-4 mr-2" />
                                    Edit Field
                                  </DropdownMenuItem>
                                  <DropdownMenuItem
                                    className="text-red-600 focus:text-red-600"
                                    onClick={() => handleDeleteField(field.id)}
                                  >
                                    <Trash2 className="w-4 h-4 mr-2" />
                                    Delete Field
                                  </DropdownMenuItem>
                                </DropdownMenuContent>
                              </DropdownMenu>
                            </div>
                          </CardContent>
                        </Card>
                      );
                    })}
                  </div>
                )}
              </TabsContent>
            ))}
          </Tabs>

          {/* Create/Edit Dialog */}
          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  <Settings2 className="w-5 h-5 text-purple-600" />
                  {editingField ? 'Edit Custom Field' : 'Create Custom Field'}
                </DialogTitle>
                <DialogDescription>
                  Configure the field settings and validation rules.
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-6 py-4">
                {/* Basic Info */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="label">Display Label *</Label>
                    <Input
                      id="label"
                      placeholder="e.g., Customer Type"
                      value={formData.label}
                      onChange={(e) => {
                        setFormData({
                          ...formData,
                          label: e.target.value,
                          name: e.target.value.toLowerCase().replace(/[^a-z0-9]+/g, '_'),
                        });
                      }}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="name">Field Name (API) *</Label>
                    <Input
                      id="name"
                      placeholder="customer_type"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="font-mono"
                    />
                  </div>
                </div>

                {/* Field Type */}
                <div className="space-y-2">
                  <Label>Field Type *</Label>
                  <div className="grid grid-cols-3 sm:grid-cols-5 gap-2">
                    {FIELD_TYPES.map((type) => {
                      const TypeIcon = type.icon;
                      return (
                        <button
                          key={type.value}
                          type="button"
                          onClick={() => setFormData({ ...formData, field_type: type.value })}
                          className={`p-3 rounded-lg border-2 transition-all text-center ${
                            formData.field_type === type.value
                              ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
                              : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                          }`}
                        >
                          <TypeIcon className={`w-5 h-5 mx-auto mb-1 ${
                            formData.field_type === type.value
                              ? 'text-purple-600'
                              : 'text-gray-400'
                          }`} />
                          <span className={`text-xs ${
                            formData.field_type === type.value
                              ? 'text-purple-700 dark:text-purple-300 font-medium'
                              : 'text-gray-500 dark:text-gray-400'
                          }`}>
                            {type.label}
                          </span>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Entity Type */}
                <div className="space-y-2">
                  <Label>Apply to Entity *</Label>
                  <Select
                    value={activeEntity}
                    onValueChange={(value) => setFormData({ ...formData, content_type: ENTITY_TYPES.findIndex(e => e.value === value) + 1 })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select entity type" />
                    </SelectTrigger>
                    <SelectContent>
                      {ENTITY_TYPES.map((entity) => (
                        <SelectItem key={entity.value} value={entity.value}>
                          <div className="flex items-center gap-2">
                            <entity.icon className="w-4 h-4" />
                            {entity.label}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Options for select fields */}
                {['select', 'multiselect', 'radio', 'checkbox'].includes(formData.field_type) && (
                  <div className="space-y-3">
                    <Label>Options *</Label>
                    <div className="space-y-2">
                      {formData.options.map((option, index) => (
                        <div key={index} className="flex items-center gap-2">
                          <Input
                            value={option.label}
                            disabled
                            className="flex-1"
                          />
                          <Input
                            value={option.value}
                            disabled
                            className="flex-1 font-mono text-sm"
                          />
                          <Button
                            type="button"
                            variant="ghost"
                            size="icon"
                            onClick={() => removeOption(index)}
                          >
                            <Trash2 className="w-4 h-4 text-red-500" />
                          </Button>
                        </div>
                      ))}
                      <div className="flex items-center gap-2">
                        <Input
                          placeholder="Option label"
                          value={newOption.label}
                          onChange={(e) => setNewOption({ ...newOption, label: e.target.value })}
                          className="flex-1"
                        />
                        <Input
                          placeholder="value"
                          value={newOption.value}
                          onChange={(e) => setNewOption({ ...newOption, value: e.target.value })}
                          className="flex-1 font-mono text-sm"
                        />
                        <Button type="button" variant="outline" onClick={addOption}>
                          <Plus className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                )}

                {/* Help Text & Placeholder */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="placeholder">Placeholder</Label>
                    <Input
                      id="placeholder"
                      placeholder="Enter placeholder text..."
                      value={formData.placeholder}
                      onChange={(e) => setFormData({ ...formData, placeholder: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="default_value">Default Value</Label>
                    <Input
                      id="default_value"
                      placeholder="Enter default value..."
                      value={formData.default_value}
                      onChange={(e) => setFormData({ ...formData, default_value: e.target.value })}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="help_text">Help Text</Label>
                  <Input
                    id="help_text"
                    placeholder="Explain what this field is for..."
                    value={formData.help_text}
                    onChange={(e) => setFormData({ ...formData, help_text: e.target.value })}
                  />
                </div>

                {/* Validation for text/number fields */}
                {['text', 'textarea', 'number', 'decimal'].includes(formData.field_type) && (
                  <div className="grid grid-cols-2 gap-4">
                    {['text', 'textarea'].includes(formData.field_type) && (
                      <>
                        <div className="space-y-2">
                          <Label htmlFor="min_length">Min Length</Label>
                          <Input
                            id="min_length"
                            type="number"
                            value={formData.min_length || ''}
                            onChange={(e) => setFormData({ ...formData, min_length: parseInt(e.target.value) || undefined })}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="max_length">Max Length</Label>
                          <Input
                            id="max_length"
                            type="number"
                            value={formData.max_length || ''}
                            onChange={(e) => setFormData({ ...formData, max_length: parseInt(e.target.value) || undefined })}
                          />
                        </div>
                      </>
                    )}
                    {['number', 'decimal'].includes(formData.field_type) && (
                      <>
                        <div className="space-y-2">
                          <Label htmlFor="min_value">Min Value</Label>
                          <Input
                            id="min_value"
                            type="number"
                            value={formData.min_value || ''}
                            onChange={(e) => setFormData({ ...formData, min_value: parseFloat(e.target.value) || undefined })}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="max_value">Max Value</Label>
                          <Input
                            id="max_value"
                            type="number"
                            value={formData.max_value || ''}
                            onChange={(e) => setFormData({ ...formData, max_value: parseFloat(e.target.value) || undefined })}
                          />
                        </div>
                      </>
                    )}
                  </div>
                )}

                {/* Switches */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
                    <div className="flex items-center gap-2">
                      <AlertCircle className="w-4 h-4 text-red-500" />
                      <Label htmlFor="is_required" className="cursor-pointer">Required Field</Label>
                    </div>
                    <Switch
                      id="is_required"
                      checked={formData.is_required}
                      onCheckedChange={(checked) => setFormData({ ...formData, is_required: checked })}
                    />
                  </div>
                  <div className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
                    <div className="flex items-center gap-2">
                      <Eye className="w-4 h-4 text-blue-500" />
                      <Label htmlFor="is_visible" className="cursor-pointer">Visible</Label>
                    </div>
                    <Switch
                      id="is_visible"
                      checked={formData.is_visible}
                      onCheckedChange={(checked) => setFormData({ ...formData, is_visible: checked })}
                    />
                  </div>
                  <div className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
                    <div className="flex items-center gap-2">
                      <Search className="w-4 h-4 text-green-500" />
                      <Label htmlFor="is_searchable" className="cursor-pointer">Searchable</Label>
                    </div>
                    <Switch
                      id="is_searchable"
                      checked={formData.is_searchable}
                      onCheckedChange={(checked) => setFormData({ ...formData, is_searchable: checked })}
                    />
                  </div>
                  <div className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
                    <div className="flex items-center gap-2">
                      <Filter className="w-4 h-4 text-amber-500" />
                      <Label htmlFor="is_filterable" className="cursor-pointer">Filterable</Label>
                    </div>
                    <Switch
                      id="is_filterable"
                      checked={formData.is_filterable}
                      onCheckedChange={(checked) => setFormData({ ...formData, is_filterable: checked })}
                    />
                  </div>
                </div>
              </div>

              <DialogFooter>
                <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                  Cancel
                </Button>
                <Button
                  onClick={handleCreateField}
                  disabled={saving}
                  className="bg-linear-to-r from-purple-600 to-indigo-600"
                >
                  {saving && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                  {editingField ? 'Update Field' : 'Create Field'}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}

