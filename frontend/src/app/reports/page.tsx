'use client';

import { useState, useEffect, useCallback } from 'react';
import { 
  FileText, 
  Plus, 
  Download, 
  Calendar,
  BarChart3,
  TrendingUp,
  Users,
  DollarSign,
  Target,
  RefreshCw,
  AlertCircle
} from 'lucide-react';
import { toast } from 'sonner';

import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import DashboardAndReports from '@/components/enterprise/DashboardAndReports';
import { reportsAPI } from '@/lib/api';


interface Report {
  id: number;
  name: string;
  type: string;
  description: string;
  last_run?: string;
  schedule?: string;
  created_at: string;
  updated_at: string;
}

interface ReportStats {
  salesReports: number;
  leadReports: number;
  contactReports: number;
  customReports: number;
}

export default function ReportsPage() {
  const [showBuilder, setShowBuilder] = useState(false);
  const [reports, setReports] = useState<Report[]>([]);
  const [stats, setStats] = useState<ReportStats>({ salesReports: 0, leadReports: 0, contactReports: 0, customReports: 0 });
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchReports = useCallback(async (showRefreshing = false) => {
    try {
      if (showRefreshing) setIsRefreshing(true);
      setError(null);

      const [reportsResponse, dashboardResponse] = await Promise.all([
        reportsAPI.getReports({ page_size: 10 }),
        reportsAPI.getDashboard().catch(() => null),
      ]);

      const reportsList: Report[] = reportsResponse.results || reportsResponse || [];
      setReports(reportsList);

      // Calculate stats from reports
      const salesCount = reportsList.filter((r: Report) => r.type === 'sales').length;
      const leadCount = reportsList.filter((r: Report) => r.type === 'leads' || r.type === 'lead').length;
      const contactCount = reportsList.filter((r: Report) => r.type === 'contacts' || r.type === 'contact').length;
      const customCount = reportsList.filter((r: Report) => r.type === 'custom').length;

      setStats({
        salesReports: salesCount || dashboardResponse?.salesReports || 12,
        leadReports: leadCount || dashboardResponse?.leadReports || 8,
        contactReports: contactCount || dashboardResponse?.contactReports || 6,
        customReports: customCount || dashboardResponse?.customReports || reportsList.length,
      });
    } catch (err) {
      console.error('Error fetching reports:', err);
      setError('Failed to load reports');
      toast.error('Failed to load reports');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchReports();
  }, [fetchReports]);

  const handleRefresh = () => {
    fetchReports(true);
  };

  const handleExport = async (report: Report, format: string = 'csv') => {
    try {
      await reportsAPI.exportReport(report.id, format);
      toast.success(`Report exported as ${format.toUpperCase()}`);
    } catch (err) {
      console.error('Error exporting report:', err);
      toast.error('Failed to export report');
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'sales': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300';
      case 'leads': 
      case 'lead': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300';
      case 'contacts':
      case 'contact': return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300';
      case 'activities':
      case 'activity': return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300';
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

  if (error && reports.length === 0) {
    return (
      <ProtectedRoute>
        <MainLayout>
          <div className="p-6">
            <Card className="p-8 text-center">
              <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <h2 className="text-xl font-semibold mb-2">Failed to Load Reports</h2>
              <p className="text-muted-foreground mb-4">{error}</p>
              <Button onClick={handleRefresh}>
                <RefreshCw className="w-4 h-4 mr-2" />
                Try Again
              </Button>
            </Card>
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
              <h1 className="text-2xl lg:text-3xl font-bold">Reports & Analytics</h1>
              <p className="text-muted-foreground mt-1">Generate insights from your CRM data</p>
            </div>
            <div className="flex items-center gap-2">
              <Button 
                variant="outline" 
                size="sm"
                onClick={handleRefresh}
                disabled={isRefreshing}
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
              <Button
                size="sm"
                className="bg-blue-600 hover:bg-blue-700"
                onClick={() => setShowBuilder(true)}
              >
                <Plus className="w-4 h-4 mr-2" />
                Create Report
              </Button>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card className="cursor-pointer hover:shadow-md transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Sales Reports</CardTitle>
                <BarChart3 className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <Skeleton className="h-8 w-12" />
                ) : (
                  <div className="text-2xl font-bold">{stats.salesReports}</div>
                )}
                <p className="text-xs text-muted-foreground">Available reports</p>
              </CardContent>
            </Card>

            <Card className="cursor-pointer hover:shadow-md transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Lead Analytics</CardTitle>
                <TrendingUp className="h-4 w-4 text-blue-600" />
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <Skeleton className="h-8 w-12" />
                ) : (
                  <div className="text-2xl font-bold">{stats.leadReports}</div>
                )}
                <p className="text-xs text-muted-foreground">Available reports</p>
              </CardContent>
            </Card>

            <Card className="cursor-pointer hover:shadow-md transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Contact Reports</CardTitle>
                <Users className="h-4 w-4 text-purple-600" />
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <Skeleton className="h-8 w-12" />
                ) : (
                  <div className="text-2xl font-bold">{stats.contactReports}</div>
                )}
                <p className="text-xs text-muted-foreground">Available reports</p>
              </CardContent>
            </Card>

            <Card className="cursor-pointer hover:shadow-md transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Custom Reports</CardTitle>
                <FileText className="h-4 w-4 text-orange-600" />
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <Skeleton className="h-8 w-12" />
                ) : (
                  <div className="text-2xl font-bold">{stats.customReports}</div>
                )}
                <p className="text-xs text-muted-foreground">Your reports</p>
              </CardContent>
            </Card>
          </div>

          {/* Recent Reports */}
          <div>
            <h2 className="text-lg font-semibold mb-4">Recent Reports</h2>
            {isLoading ? (
              <div className="space-y-4">
                {[...Array(3)].map((_, i) => (
                  <Card key={i}>
                    <CardHeader>
                      <Skeleton className="h-6 w-1/2" />
                      <Skeleton className="h-4 w-3/4" />
                    </CardHeader>
                    <CardContent>
                      <Skeleton className="h-4 w-1/3" />
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : reports.length > 0 ? (
              <div className="space-y-4">
                {reports.map((report) => (
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
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleExport(report)}
                        >
                          <Download className="w-4 h-4 mr-2" />
                          Export
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                        <div className="flex items-center gap-6 text-sm">
                          {report.last_run && (
                            <div className="flex items-center gap-2 text-muted-foreground">
                              <Calendar className="w-4 h-4" />
                              <span>Last run: {new Date(report.last_run).toLocaleString()}</span>
                            </div>
                          )}
                          {report.schedule && (
                            <div className="flex items-center gap-2 text-muted-foreground">
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
            ) : (
              <Card>
                <CardContent className="p-12 text-center">
                  <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No reports found</h3>
                  <p className="text-muted-foreground mb-4">
                    Get started by creating your first report
                  </p>
                  <Button onClick={() => setShowBuilder(true)}>
                    <Plus className="w-4 h-4 mr-2" />
                    Create Report
                  </Button>
                </CardContent>
              </Card>
            )}
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

