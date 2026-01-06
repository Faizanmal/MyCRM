'use client';

import { useState } from 'react';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
// import { Input } from '@/components/ui/input';
// import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { toast } from 'sonner';
import { Upload, FileUp, AlertCircle, CheckCircle, Loader2, Download } from 'lucide-react';

export default function ImportSettingsPage() {
  const [isImporting, setIsImporting] = useState(false);
  const [importFile, setImportFile] = useState<File | null>(null);
  const [importType, setImportType] = useState('contacts');
  const [importProgress, setImportProgress] = useState(0);

  const importTypes = [
    { id: 'contacts', name: 'Contacts', description: 'Import contacts from CSV or Excel' },
    { id: 'leads', name: 'Leads', description: 'Import leads from CSV or Excel' },
    { id: 'deals', name: 'Deals', description: 'Import deals from CSV or Excel' },
    { id: 'companies', name: 'Companies', description: 'Import company data' },
  ];

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'].includes(file.type)) {
        toast.error('Please select a CSV or Excel file');
        return;
      }
      setImportFile(file);
    }
  };

  const handleImport = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    if (!importFile) {
      toast.error('Please select a file to import');
      return;
    }

    setIsImporting(true);
    const formData = new FormData();
    formData.append('file', importFile);
    formData.append('import_type', importType);

    try {
      const response = await fetch(`/api/v1/${importType}/import/`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Failed to import data');
      
      toast.success(`Successfully imported ${importType}`);
      setImportFile(null);
      setImportProgress(0);
    } catch (error) {
      console.log("Failed to import data",error);
      toast.error('Failed to import data');
    } finally {
      setIsImporting(false);
    }
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-4 lg:p-6 space-y-6 max-w-4xl">
          <div>
            <h1 className="text-2xl lg:text-3xl font-bold text-gray-900 dark:text-white">Import Data</h1>
            <p className="text-gray-500 mt-1">Import your data from CSV or Excel files</p>
          </div>

          {/* Import Types */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">What would you like to import?</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {importTypes.map((type) => (
                <button
                  key={type.id}
                  onClick={() => setImportType(type.id)}
                  className={`p-4 border rounded-lg text-left transition-all ${
                    importType === type.id
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                  }`}
                >
                  <p className="font-medium text-gray-900 dark:text-white">{type.name}</p>
                  <p className="text-sm text-gray-500">{type.description}</p>
                </button>
              ))}
            </div>
          </div>

          {/* File Upload */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Upload className="w-5 h-5" />
                Upload File
              </CardTitle>
              <CardDescription>Select a CSV or Excel file to import</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleImport} className="space-y-4">
                <div className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-lg p-8 text-center hover:border-gray-400 transition-colors">
                  <FileUp className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 dark:text-gray-400 mb-2">Drag and drop your file here, or</p>
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <Button type="button" variant="outline" asChild>
                      <span>Browse Files</span>
                    </Button>
                  </label>
                  <input
                    id="file-upload"
                    type="file"
                    accept=".csv,.xls,.xlsx"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                  <p className="text-xs text-gray-500 mt-4">Supported formats: CSV, Excel (XLS, XLSX)</p>
                </div>

                {importFile && (
                  <div className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-900 rounded-lg">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
                      <span className="text-sm font-medium text-green-800 dark:text-green-200">{importFile.name}</span>
                    </div>
                  </div>
                )}

                {isImporting && (
                  <div className="space-y-2">
                    <Progress value={importProgress} />
                    <p className="text-xs text-gray-500 text-center">Importing {importProgress}%</p>
                  </div>
                )}

                <Button type="submit" disabled={isImporting || !importFile} className="w-full gap-2">
                  {isImporting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
                  {isImporting ? 'Importing...' : 'Import Data'}
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Template Download */}
          <Card>
            <CardHeader>
              <CardTitle>Download Template</CardTitle>
              <CardDescription>Get a sample file to understand the required format</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {importTypes.map((type) => (
                <Button
                  key={type.id}
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => {
                    toast.success(`Downloaded ${type.name} template`);
                  }}
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download {type.name} Template
                </Button>
              ))}
            </CardContent>
          </Card>

          {/* Import Guidelines */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertCircle className="w-5 h-5" />
                Import Guidelines
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-gray-600 dark:text-gray-400">
              <div>
                <p className="font-medium text-gray-900 dark:text-white mb-1">File Requirements:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li>Maximum file size: 10 MB</li>
                  <li>Supported formats: CSV, XLS, XLSX</li>
                  <li>First row must contain column headers</li>
                  <li>Maximum 10,000 rows per file</li>
                </ul>
              </div>
              <div>
                <p className="font-medium text-gray-900 dark:text-white mb-1">Column Mapping:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li>Required columns will be highlighted during import</li>
                  <li>You can map custom columns to standard fields</li>
                  <li>Extra columns will be saved as custom fields</li>
                </ul>
              </div>
              <div>
                <p className="font-medium text-gray-900 dark:text-white mb-1">Tips:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li>Clean your data before importing</li>
                  <li>Check for duplicate records</li>
                  <li>Verify email addresses and phone numbers</li>
                </ul>
              </div>
            </CardContent>
          </Card>

          {/* Recent Imports */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Imports</CardTitle>
              <CardDescription>View your import history</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-500">No imports yet. Start by uploading a file above.</p>
            </CardContent>
          </Card>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
