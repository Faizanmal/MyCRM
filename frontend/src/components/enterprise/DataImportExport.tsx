// Data Import/Export Component
/* eslint-disable @typescript-eslint/no-explicit-any */
'use client';

import React, { useState, useCallback, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  Upload, Download, FileSpreadsheet,
  CheckCircle, ArrowRight, Table
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import axios from 'axios';

interface FieldMapping {
  [key: string]: string;
}

interface ImportLog {
  id: string;
  model_name: string;
  file_format: string;
  total_records: number;
  imported_records: number;
  skipped_records: number;
  errors: any[];
  status: string;
  created_at: string;
}

export default function DataImportExport() {
  const [activeTab, setActiveTab] = useState('import');

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <FileSpreadsheet className="h-8 w-8" />
            Data Import/Export
          </h1>
          <p className="text-muted-foreground mt-1">Import and export your CRM data</p>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="import">
            <Upload className="h-4 w-4 mr-2" />
            Import
          </TabsTrigger>
          <TabsTrigger value="export">
            <Download className="h-4 w-4 mr-2" />
            Export
          </TabsTrigger>
          <TabsTrigger value="history">
            <Table className="h-4 w-4 mr-2" />
            History
          </TabsTrigger>
        </TabsList>

        <TabsContent value="import" className="space-y-4">
          <ImportWizard />
        </TabsContent>

        <TabsContent value="export" className="space-y-4">
          <ExportWizard />
        </TabsContent>

        <TabsContent value="history" className="space-y-4">
          <ImportHistory />
        </TabsContent>
      </Tabs>
    </div>
  );
}

// Import Wizard Component
function ImportWizard() {
  const [step, setStep] = useState(1);
  const [file, setFile] = useState<File | null>(null);
  const [modelName, setModelName] = useState('');
  const [fileFormat, setFileFormat] = useState('csv');
  const [fieldMapping, setFieldMapping] = useState<FieldMapping>({});
  const [fileHeaders, setFileHeaders] = useState<string[]>([]);
  const [modelFields, setModelFields] = useState<string[]>([]);
  const [uploading, setUploading] = useState(false);
  const [importResult, setImportResult] = useState<any>(null);
  const [filePreview, setFilePreview] = useState<string | null>(null);
  const { toast } = useToast();

  const MODELS = [
    { value: 'contact_management.Contact', label: 'Contacts' },
    { value: 'lead_management.Lead', label: 'Leads' },
    { value: 'opportunity_management.Opportunity', label: 'Opportunities' },
    { value: 'task_management.Task', label: 'Tasks' },
  ];

  const getAvailableFields = (modelValue: string): string[] => {
    const fieldMap: Record<string, string[]> = {
      'contact_management.Contact': ['name', 'email', 'phone', 'company', 'title', 'status'],
      'lead_management.Lead': ['first_name', 'last_name', 'email', 'phone', 'company_name', 'lead_source'],
      'opportunity_management.Opportunity': ['name', 'amount', 'stage', 'close_date', 'description'],
      'task_management.Task': ['title', 'description', 'due_date', 'priority', 'status'],
    };
    return fieldMap[modelValue] || [];
  };

  const parseFileHeaders = useCallback((file: File) => {
    // This would parse the first row of the file
    // For demo purposes, using mock data
    setFileHeaders(['Name', 'Email', 'Phone', 'Company', 'Title', 'Status']);
    
    // Show file preview info in toast notification
    toast({
      title: 'File Preview',
      description: `File: ${file.name} (${(file.size / 1024).toFixed(2)} KB)`,
    });
    
    // Update model fields when file is selected
    if (modelName) {
      const fields = getAvailableFields(modelName);
      setModelFields(fields);
    }
  }, [modelName, toast]);

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      // Parse headers from CSV/Excel
      parseFileHeaders(selectedFile);
      // Show file preview info
      setFilePreview(`${selectedFile.name} - ${(selectedFile.size / 1024).toFixed(2)} KB`);
    }
  }, [parseFileHeaders]);

  const handleModelChange = (value: string) => {
    setModelName(value);
    const fields = getAvailableFields(value);
    setModelFields(fields);
  };

  const handleImport = async () => {
    if (!file || !modelFields.length) {
      toast({
        title: 'Error',
        description: 'Please select a file and data type',
        variant: 'destructive',
      });
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('model_name', modelName);
    formData.append('file_format', fileFormat);
    formData.append('field_mapping', JSON.stringify(fieldMapping));
    formData.append('validate_only', 'false');

    try {
      const response = await axios.post('/api/core/data/import/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setImportResult(response.data);
      setStep(4);
      toast({
        title: 'Success',
        description: `Imported ${response.data.imported} records successfully`,
      });
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.error || 'Failed to import data',
        variant: 'destructive',
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <CardTitle>Import Data</CardTitle>
            <CardDescription>Step {step} of 4</CardDescription>
          </div>
          <div className="flex gap-1">
            {[1, 2, 3, 4].map((s) => (
              <div
                key={s}
                className={`h-2 w-12 rounded-full ${
                  s <= step ? 'bg-primary' : 'bg-muted'
                }`}
              />
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {step === 1 && (
          <div className="space-y-4">
            <div>
              <Label htmlFor="model">Select Data Type</Label>
              <Select value={modelName} onValueChange={handleModelChange}>
                <SelectTrigger>
                  <SelectValue placeholder="Choose what to import" />
                </SelectTrigger>
                <SelectContent>
                  {MODELS.map((model) => (
                    <SelectItem key={model.value} value={model.value}>
                      {model.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="format">File Format</Label>
              <Select value={fileFormat} onValueChange={setFileFormat}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="csv">CSV</SelectItem>
                  <SelectItem value="xlsx">Excel (XLSX)</SelectItem>
                  <SelectItem value="json">JSON</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="file">Upload File</Label>
              <Input
                id="file"
                type="file"
                accept=".csv,.xlsx,.xls,.json"
                onChange={handleFileChange}
                className="cursor-pointer"
              />
              {filePreview && (
                <p className="text-sm text-muted-foreground mt-2">
                  Selected: {filePreview}
                </p>
              )}
            </div>

            <Button
              onClick={() => setStep(2)}
              disabled={!file || !modelName}
              className="w-full"
            >
              Next: Map Fields
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-4">
            <div>
              <h3 className="font-semibold mb-4">Field Mapping</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Map your file columns to CRM fields. Available fields: {modelFields.join(', ')}
              </p>
            </div>

            <div className="space-y-3">
              {fileHeaders.map((header) => (
                <div key={header} className="flex items-center gap-3">
                  <div className="flex-1">
                    <Label className="text-sm font-normal">{header}</Label>
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground" />
                  <div className="flex-1">
                    <Select
                      value={fieldMapping[header] || ''}
                      onValueChange={(value) =>
                        setFieldMapping({ ...fieldMapping, [header]: value })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select field" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="name">Name</SelectItem>
                        <SelectItem value="email">Email</SelectItem>
                        <SelectItem value="phone">Phone</SelectItem>
                        <SelectItem value="company">Company</SelectItem>
                        <SelectItem value="title">Title</SelectItem>
                        <SelectItem value="status">Status</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setStep(1)} className="flex-1">
                Back
              </Button>
              <Button onClick={() => setStep(3)} className="flex-1">
                Next: Review
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-4">
            <div>
              <h3 className="font-semibold mb-4">Review & Confirm</h3>
            </div>

            <div className="space-y-3 p-4 bg-muted rounded-lg">
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Data Type:</span>
                <span className="text-sm font-medium">
                  {MODELS.find((m) => m.value === modelName)?.label}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">File:</span>
                <span className="text-sm font-medium">{file?.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Format:</span>
                <span className="text-sm font-medium">{fileFormat.toUpperCase()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Mapped Fields:</span>
                <span className="text-sm font-medium">
                  {Object.keys(fieldMapping).length} / {fileHeaders.length}
                </span>
              </div>
            </div>

            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setStep(2)} className="flex-1">
                Back
              </Button>
              <Button onClick={handleImport} disabled={uploading} className="flex-1">
                {uploading ? 'Importing...' : 'Start Import'}
              </Button>
            </div>
          </div>
        )}

        {step === 4 && importResult && (
          <div className="space-y-4">
            <div className="text-center py-6">
              <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Import Complete</h3>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <Card>
                <CardContent className="pt-6">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-green-600">
                      {importResult.imported}
                    </p>
                    <p className="text-sm text-muted-foreground">Imported</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-yellow-600">
                      {importResult.skipped}
                    </p>
                    <p className="text-sm text-muted-foreground">Skipped</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="text-center">
                    <p className="text-3xl font-bold">{importResult.total}</p>
                    <p className="text-sm text-muted-foreground">Total</p>
                  </div>
                </CardContent>
              </Card>
            </div>

            {importResult.errors && importResult.errors.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Errors</CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-40">
                    <div className="space-y-2">
                      {importResult.errors.map((error: any, index: number) => (
                        <div
                          key={index}
                          className="text-sm p-2 bg-destructive/10 rounded"
                        >
                          Row {error.row}: {error.errors.join(', ')}
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            )}

            <Button
              onClick={() => {
                setStep(1);
                setFile(null);
                setImportResult(null);
                setFieldMapping({});
              }}
              className="w-full"
            >
              Import Another File
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Export Wizard Component
function ExportWizard() {
  const [modelName, setModelName] = useState('');
  const [fileFormat, setFileFormat] = useState('csv');
  const [selectedFields, setSelectedFields] = useState<string[]>([]);
  const [exporting, setExporting] = useState(false);
  const { toast } = useToast();

  const MODELS = [
    { value: 'contact_management.Contact', label: 'Contacts' },
    { value: 'lead_management.Lead', label: 'Leads' },
    { value: 'opportunity_management.Opportunity', label: 'Opportunities' },
  ];

  const AVAILABLE_FIELDS = [
    'id',
    'name',
    'email',
    'phone',
    'company',
    'title',
    'status',
    'created_at',
    'updated_at',
  ];

  const handleExport = async () => {
    setExporting(true);
    try {
      const response = await axios.post(
        '/api/core/data/export/',
        {
          model_name: modelName,
          file_format: fileFormat,
          fields: selectedFields.length > 0 ? selectedFields : AVAILABLE_FIELDS,
        },
        { responseType: 'blob' }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `export.${fileFormat}`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast({
        title: 'Success',
        description: 'Data exported successfully',
      });
    } catch (error: any) {
      console.error('Export failed:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.error || 'Failed to export data',
        variant: 'destructive',
      });
    } finally {
      setExporting(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Export Data</CardTitle>
        <CardDescription>Download your CRM data in various formats</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Label>Data Type</Label>
          <Select value={modelName} onValueChange={setModelName}>
            <SelectTrigger>
              <SelectValue placeholder="Choose what to export" />
            </SelectTrigger>
            <SelectContent>
              {MODELS.map((model) => (
                <SelectItem key={model.value} value={model.value}>
                  {model.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label>Export Format</Label>
          <Select value={fileFormat} onValueChange={setFileFormat}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="csv">CSV</SelectItem>
              <SelectItem value="xlsx">Excel (XLSX)</SelectItem>
              <SelectItem value="json">JSON</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label>Fields to Export</Label>
          <p className="text-sm text-muted-foreground mb-2">
            Leave empty to export all fields
          </p>
          <div className="grid grid-cols-2 gap-2">
            {AVAILABLE_FIELDS.map((field) => (
              <div key={field} className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id={field}
                  checked={selectedFields.includes(field)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedFields([...selectedFields, field]);
                    } else {
                      setSelectedFields(selectedFields.filter((f) => f !== field));
                    }
                  }}
                  className="h-4 w-4"
                />
                <label htmlFor={field} className="text-sm">
                  {field}
                </label>
              </div>
            ))}
          </div>
        </div>

        <Button
          onClick={handleExport}
          disabled={!modelName || exporting}
          className="w-full"
        >
          <Download className="h-4 w-4 mr-2" />
          {exporting ? 'Exporting...' : 'Export Data'}
        </Button>
      </CardContent>
    </Card>
  );
}

// Import History Component
function ImportHistory() {
  const [logs, setLogs] = useState<ImportLog[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/core/data-import-logs/');
      setLogs(response.data.results || response.data);
    } catch (error: any) {
      console.error('Failed to fetch import logs:', error.response?.data?.error || error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Import History</CardTitle>
        <CardDescription>View past import operations ({loading ? 'Loading...' : logs.length} records)</CardDescription>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[500px]">
          <div className="space-y-3">
            {logs.map((log) => (
              <Card key={log.id}>
                <CardContent className="pt-6">
                  <div className="flex justify-between items-start">
                    <div className="space-y-1">
                      <p className="font-medium">{log.model_name}</p>
                      <p className="text-sm text-muted-foreground">
                        {new Date(log.created_at).toLocaleString()}
                      </p>
                    </div>
                    <Badge
                      variant={
                        log.status === 'completed'
                          ? 'default'
                          : log.status === 'completed_with_errors'
                          ? 'secondary'
                          : 'destructive'
                      }
                    >
                      {log.status}
                    </Badge>
                  </div>
                  <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Total</p>
                      <p className="font-semibold">{log.total_records}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Imported</p>
                      <p className="font-semibold text-green-600">
                        {log.imported_records}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Skipped</p>
                      <p className="font-semibold text-yellow-600">
                        {log.skipped_records}
                      </p>
                    </div>
                  </div>
                  {log.errors.length > 0 && (
                    <div className="mt-3">
                      <p className="text-sm text-destructive">
                        {log.errors.length} errors occurred
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
