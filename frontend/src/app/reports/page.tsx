'use client';

import { useState } from 'react';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import DashboardAndReports from '@/components/enterprise/DashboardAndReports';
import { 
  FileText, 
  Plus, 
  Download, 
  Calendar,
  BarChart3,
  TrendingUp,
  Users,
  DollarSign,
  Target
} from 'lucide-react';

interface Report {
  id: string;
  name: string;
  type: 'sales' | 'leads' | 'contacts' | 'activities';
  description: string;
  lastRun?: string;
  schedule?: string;
}

const mockReports: Report[] = [
  {
    id: '1',
    name: 'Sales Performance',
    type: 'sales',
    description: 'Monthly sales metrics and trends',
    lastRun: '2025-11-10T08:00:00',
    schedule: 'Daily at 8:00 AM',
  },
  {
    id: '2',
    name: 'Lead Conversion Report',
    type: 'leads',
    description: 'Lead to customer conversion analysis',
    lastRun: '2025-11-09T09:00:00',
    schedule: 'Weekly on Monday',
  },
  {
    id: '3',
    name: 'Contact Activity Summary',
    type: 'contacts',
    description: 'Recent contact interactions and engagement',
    lastRun: '2025-11-10T07:30:00',
  },
  {
    id: '4',
    name: 'Pipeline Forecast',
    type: 'sales',
    description: 'Revenue forecast based on pipeline',
    lastRun: '2025-11-08T10:00:00',
    schedule: 'Weekly on Friday',
  },
];

export default function ReportsPage() {
  const [showBuilder, setShowBuilder] = useState(false);

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'sales': return 'bg-green-100 text-green-800';
      case 'leads': return 'bg-blue-100 text-blue-800';
      case 'contacts': return 'bg-purple-100 text-purple-800';
      case 'activities': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (showBuilder) {
    return (
      <ProtectedRoute>
        <MainLayout>
          <div className="p-4 lg:p-6">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-2xl font-bold">Custom Report Builder</h2>
              <Button variant="outline" onClick={() => setShowBuilder(false)}>
                Back to Reports
              </Button>
            </div>
            <DashboardAndReports />
          </div>
        </MainLayout>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-4 lg:p-6 space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-2xl lg:text-3xl font-bold text-gray-900">Reports & Analytics</h1>
              <p className="text-gray-500 mt-1">Generate insights from your CRM data</p>
            </div>
            <Button
              size="sm"
              className="bg-blue-600 hover:bg-blue-700"
              onClick={() => setShowBuilder(true)}
            >
              <Plus className="w-4 h-4 mr-2" />
              Create Report
            </Button>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card className="cursor-pointer hover:shadow-md transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Sales Reports</CardTitle>
                <BarChart3 className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">12</div>
                <p className="text-xs text-muted-foreground">Available reports</p>
              </CardContent>
            </Card>

            <Card className="cursor-pointer hover:shadow-md transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Lead Analytics</CardTitle>
                <TrendingUp className="h-4 w-4 text-blue-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">8</div>
                <p className="text-xs text-muted-foreground">Available reports</p>
              </CardContent>
            </Card>

            <Card className="cursor-pointer hover:shadow-md transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Contact Reports</CardTitle>
                <Users className="h-4 w-4 text-purple-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">6</div>
                <p className="text-xs text-muted-foreground">Available reports</p>
              </CardContent>
            </Card>

            <Card className="cursor-pointer hover:shadow-md transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Custom Reports</CardTitle>
                <FileText className="h-4 w-4 text-orange-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">4</div>
                <p className="text-xs text-muted-foreground">Your reports</p>
              </CardContent>
            </Card>
          </div>

          {/* Recent Reports */}
          <div>
            <h2 className="text-lg font-semibold mb-4">Recent Reports</h2>
            <div className="space-y-4">
              {mockReports.map((report) => (
                <Card key={report.id} className="hover:shadow-md transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <CardTitle className="text-lg">{report.name}</CardTitle>
                          <Badge className={getTypeColor(report.type)}>
                            {report.type}
                          </Badge>
                        </div>
                        <CardDescription>{report.description}</CardDescription>
                      </div>
                      <Button variant="outline" size="sm">
                        <Download className="w-4 h-4 mr-2" />
                        Export
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                      <div className="flex items-center gap-6 text-sm">
                        {report.lastRun && (
                          <div className="flex items-center gap-2 text-gray-600">
                            <Calendar className="w-4 h-4" />
                            <span>Last run: {new Date(report.lastRun).toLocaleString()}</span>
                          </div>
                        )}
                        {report.schedule && (
                          <div className="flex items-center gap-2 text-gray-600">
                            <Calendar className="w-4 h-4" />
                            <span>Schedule: {report.schedule}</span>
                          </div>
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        <Button variant="outline" size="sm">
                          View
                        </Button>
                        <Button variant="outline" size="sm">
                          Run Now
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Report Templates */}
          <div>
            <h2 className="text-lg font-semibold mb-4">Report Templates</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <Card className="cursor-pointer hover:shadow-md transition-shadow">
                <CardHeader>
                  <DollarSign className="w-8 h-8 text-green-600 mb-2" />
                  <CardTitle className="text-base">Revenue Analysis</CardTitle>
                  <CardDescription className="text-sm">
                    Track revenue trends and forecasts
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button variant="outline" size="sm" className="w-full">
                    Use Template
                  </Button>
                </CardContent>
              </Card>

              <Card className="cursor-pointer hover:shadow-md transition-shadow">
                <CardHeader>
                  <Target className="w-8 h-8 text-blue-600 mb-2" />
                  <CardTitle className="text-base">Pipeline Health</CardTitle>
                  <CardDescription className="text-sm">
                    Monitor pipeline metrics and velocity
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button variant="outline" size="sm" className="w-full">
                    Use Template
                  </Button>
                </CardContent>
              </Card>

              <Card className="cursor-pointer hover:shadow-md transition-shadow">
                <CardHeader>
                  <Users className="w-8 h-8 text-purple-600 mb-2" />
                  <CardTitle className="text-base">Team Performance</CardTitle>
                  <CardDescription className="text-sm">
                    Analyze individual and team metrics
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button variant="outline" size="sm" className="w-full">
                    Use Template
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
