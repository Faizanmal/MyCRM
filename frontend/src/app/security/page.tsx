'use client';

import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import SecurityDashboard from '@/components/enterprise/SecurityDashboard';
import AuditLogViewer from '@/components/enterprise/AuditLogViewer';
import PermissionManagement from '@/components/enterprise/PermissionManagement';
import { Shield, FileText, Lock } from 'lucide-react';

export default function SecurityPage() {
  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-4 lg:p-6 space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-2xl lg:text-3xl font-bold text-gray-900 flex items-center gap-2">
                <Shield className="w-8 h-8 text-blue-600" />
                Security & Compliance
              </h1>
              <p className="text-gray-500 mt-1">Monitor security, manage permissions, and view audit logs</p>
            </div>
          </div>

          {/* Security Tabs */}
          <Tabs defaultValue="dashboard" className="space-y-4">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="dashboard" className="flex items-center gap-2">
                <Shield className="w-4 h-4" />
                Dashboard
              </TabsTrigger>
              <TabsTrigger value="permissions" className="flex items-center gap-2">
                <Lock className="w-4 h-4" />
                Permissions
              </TabsTrigger>
              <TabsTrigger value="audit" className="flex items-center gap-2">
                <FileText className="w-4 h-4" />
                Audit Logs
              </TabsTrigger>
            </TabsList>

            <TabsContent value="dashboard" className="space-y-4">
              <Card>
                <CardContent className="p-6">
                  <SecurityDashboard />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="permissions" className="space-y-4">
              <Card>
                <CardContent className="p-6">
                  <PermissionManagement />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="audit" className="space-y-4">
              <Card>
                <CardContent className="p-6">
                  <AuditLogViewer />
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
