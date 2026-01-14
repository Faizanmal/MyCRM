'use client';

import { Upload, Download } from 'lucide-react';

import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent } from '@/components/ui/card';
import DataImportExport from '@/components/enterprise/DataImportExport';

export default function DataPage() {
  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-4 lg:p-6 space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-2xl lg:text-3xl font-bold text-gray-900 flex items-center gap-2">
                <Upload className="w-8 h-8 text-blue-600" />
                <Download className="w-8 h-8 text-green-600" />
                Data Import/Export
              </h1>
              <p className="text-gray-500 mt-1">Import or export your CRM data in various formats</p>
            </div>
          </div>

          {/* Data Tools */}
          <Card>
            <CardContent className="p-6">
              <DataImportExport />
            </CardContent>
          </Card>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}

