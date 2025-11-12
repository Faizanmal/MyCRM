'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  LayoutDashboard, FileText, BarChart3, TrendingUp, Plus, Edit,
  Trash2, Play, Calendar, Download, Users, Settings
} from 'lucide-react';

interface Dashboard {
  id: number;
  name: string;
  description: string;
  dashboard_type: string;
  is_default: boolean;
  is_public: boolean;
  widgets: any[];
  created_at: string;
}

interface Report {
  id: number;
  name: string;
  description: string;
  report_type: string;
  export_format: string;
  is_public: boolean;
  last_generated_at?: string;
  created_at: string;
}

interface KPI {
  id: number;
  name: string;
  kpi_type: string;
  current_value?: number;
  target_value?: number;
  unit: string;
  trend?: 'up' | 'down' | 'stable';
  is_active: boolean;
}

export default function AdvancedReportingPage() {
  const [activeTab, setActiveTab] = useState<'dashboards' | 'reports' | 'kpis'>('dashboards');
  const [dashboards, setDashboards] = useState<Dashboard[]>([]);
  const [reports, setReports] = useState<Report[]>([]);
  const [kpis, setKPIs] = useState<KPI[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'dashboards') {
        const res = await fetch('/api/advanced-reporting/dashboards/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        if (res.ok) {
          const data = await res.json();
          setDashboards(data.results || data);
        }
      } else if (activeTab === 'reports') {
        const res = await fetch('/api/advanced-reporting/reports/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        if (res.ok) {
          const data = await res.json();
          setReports(data.results || data);
        }
      } else if (activeTab === 'kpis') {
        const res = await fetch('/api/advanced-reporting/kpis/summary/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        if (res.ok) {
          const data = await res.json();
          setKPIs(data);
        }
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTrendIcon = (trend?: string) => {
    if (trend === 'up') return <TrendingUp className="w-4 h-4 text-green-500" />;
    if (trend === 'down') return <TrendingUp className="w-4 h-4 text-red-500 transform rotate-180" />;
    return <div className="w-4 h-4" />;
  };

  const renderDashboards = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Custom Dashboards</h2>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Create Dashboard
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {dashboards.map((dashboard) => (
          <Card key={dashboard.id} className="p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <LayoutDashboard className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold">{dashboard.name}</h3>
                  <p className="text-sm text-gray-600 capitalize">{dashboard.dashboard_type.replace('_', ' ')}</p>
                </div>
              </div>
              {dashboard.is_default && (
                <Badge variant="secondary">Default</Badge>
              )}
            </div>

            <p className="text-sm text-gray-600 mb-4 line-clamp-2">
              {dashboard.description || 'No description'}
            </p>

            <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
              <span>{dashboard.widgets.length} widgets</span>
              <span>{dashboard.is_public ? 'Public' : 'Private'}</span>
            </div>

            <div className="flex gap-2">
              <Button size="sm" variant="outline" className="flex-1">
                <BarChart3 className="w-4 h-4 mr-2" />
                View
              </Button>
              <Button size="sm" variant="ghost">
                <Edit className="w-4 h-4" />
              </Button>
              <Button size="sm" variant="ghost">
                <Settings className="w-4 h-4" />
              </Button>
            </div>
          </Card>
        ))}

        {/* Empty State */}
        {dashboards.length === 0 && !loading && (
          <div className="col-span-full text-center py-12 text-gray-500">
            <LayoutDashboard className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <p className="text-lg font-semibold">No Dashboards Yet</p>
            <p className="text-sm mt-2">Create your first custom dashboard to visualize your CRM data</p>
            <Button className="mt-4">
              <Plus className="w-4 h-4 mr-2" />
              Create Dashboard
            </Button>
          </div>
        )}
      </div>
    </div>
  );

  const renderReports = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Reports</h2>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Create Report
        </Button>
      </div>

      <Card className="p-6">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left p-3">Report Name</th>
                <th className="text-left p-3">Type</th>
                <th className="text-left p-3">Format</th>
                <th className="text-left p-3">Last Generated</th>
                <th className="text-left p-3">Status</th>
                <th className="text-left p-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {reports.map((report) => (
                <tr key={report.id} className="border-b hover:bg-gray-50">
                  <td className="p-3">
                    <div>
                      <div className="font-semibold">{report.name}</div>
                      <div className="text-sm text-gray-500 line-clamp-1">
                        {report.description || 'No description'}
                      </div>
                    </div>
                  </td>
                  <td className="p-3">
                    <Badge variant="secondary" className="capitalize">
                      {report.report_type.replace('_', ' ')}
                    </Badge>
                  </td>
                  <td className="p-3">
                    <span className="uppercase font-mono text-sm">{report.export_format}</span>
                  </td>
                  <td className="p-3 text-sm text-gray-600">
                    {report.last_generated_at
                      ? new Date(report.last_generated_at).toLocaleDateString()
                      : 'Never'}
                  </td>
                  <td className="p-3">
                    {report.is_public ? (
                      <Badge className="bg-green-500">
                        <Users className="w-3 h-3 mr-1" />
                        Public
                      </Badge>
                    ) : (
                      <Badge variant="secondary">Private</Badge>
                    )}
                  </td>
                  <td className="p-3">
                    <div className="flex items-center gap-2">
                      <Button size="sm" variant="outline">
                        <Play className="w-4 h-4 mr-1" />
                        Run
                      </Button>
                      <Button size="sm" variant="outline">
                        <Download className="w-4 h-4 mr-1" />
                        Download
                      </Button>
                      <Button size="sm" variant="ghost">
                        <Calendar className="w-4 h-4" />
                      </Button>
                      <Button size="sm" variant="ghost">
                        <Edit className="w-4 h-4" />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {reports.length === 0 && !loading && (
            <div className="text-center py-12 text-gray-500">
              <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p className="text-lg font-semibold">No Reports Yet</p>
              <p className="text-sm mt-2">Create custom reports to analyze your CRM data</p>
            </div>
          )}
        </div>
      </Card>
    </div>
  );

  const renderKPIs = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Key Performance Indicators</h2>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Create KPI
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {kpis.map((kpi) => (
          <Card key={kpi.id} className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h3 className="font-semibold text-sm text-gray-600 mb-1">{kpi.name}</h3>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold">
                    {kpi.current_value !== undefined && kpi.current_value !== null
                      ? kpi.current_value.toLocaleString()
                      : '-'}
                  </span>
                  <span className="text-sm text-gray-500">{kpi.unit}</span>
                </div>
              </div>
              {getTrendIcon(kpi.trend)}
            </div>

            {kpi.target_value && (
              <div className="mb-3">
                <div className="flex justify-between text-xs text-gray-600 mb-1">
                  <span>Progress</span>
                  <span>Target: {kpi.target_value}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full"
                    style={{
                      width: `${Math.min(
                        ((kpi.current_value || 0) / kpi.target_value) * 100,
                        100
                      )}%`
                    }}
                  />
                </div>
              </div>
            )}

            <div className="flex items-center gap-2 mt-4">
              <Button size="sm" variant="outline" className="flex-1">
                <BarChart3 className="w-4 h-4 mr-2" />
                View History
              </Button>
              <Button size="sm" variant="ghost">
                <Edit className="w-4 h-4" />
              </Button>
            </div>
          </Card>
        ))}

        {kpis.length === 0 && !loading && (
          <div className="col-span-full text-center py-12 text-gray-500">
            <TrendingUp className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <p className="text-lg font-semibold">No KPIs Configured</p>
            <p className="text-sm mt-2">Track key metrics to measure your business performance</p>
            <Button className="mt-4">
              <Plus className="w-4 h-4 mr-2" />
              Create KPI
            </Button>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Advanced Reporting & Analytics</h1>
        <p className="text-gray-600">
          Create custom dashboards, reports, and track key performance indicators
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b mb-6">
        <div className="flex space-x-6">
          <button
            className={`pb-3 px-1 ${
              activeTab === 'dashboards'
                ? 'border-b-2 border-blue-600 text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
            onClick={() => setActiveTab('dashboards')}
          >
            <LayoutDashboard className="w-4 h-4 inline mr-2" />
            Dashboards
          </button>
          <button
            className={`pb-3 px-1 ${
              activeTab === 'reports'
                ? 'border-b-2 border-blue-600 text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
            onClick={() => setActiveTab('reports')}
          >
            <FileText className="w-4 h-4 inline mr-2" />
            Reports
          </button>
          <button
            className={`pb-3 px-1 ${
              activeTab === 'kpis'
                ? 'border-b-2 border-blue-600 text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
            onClick={() => setActiveTab('kpis')}
          >
            <TrendingUp className="w-4 h-4 inline mr-2" />
            KPIs
          </button>
        </div>
      </div>

      {/* Content */}
      {loading ? (
        <div className="text-center py-12">Loading...</div>
      ) : (
        <>
          {activeTab === 'dashboards' && renderDashboards()}
          {activeTab === 'reports' && renderReports()}
          {activeTab === 'kpis' && renderKPIs()}
        </>
      )}
    </div>
  );
}
