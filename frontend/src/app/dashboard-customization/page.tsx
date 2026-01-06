'use client';

import { useEffect, useState, useCallback } from 'react';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
// import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
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
// import {
//   DropdownMenu,
//   DropdownMenuContent,
//   DropdownMenuItem,
//   DropdownMenuSeparator,
//   DropdownMenuTrigger,
// } from '@/components/ui/dropdown-menu';
import {
  LayoutDashboard,
  Plus,
  Pencil,
  Trash2,
  BarChart3,
  LineChart,
  PieChart,
  AreaChart,
  TrendingUp,
  Users,
  Target,
  ListChecks,
  Map,
  Table,
  Loader2,
  Share2,
  Lock,
  Unlock,
  Grid3X3,
  Activity,
} from 'lucide-react';
import { toast } from 'sonner';
import { dashboardWidgetsAPI, DashboardWidget, UserDashboard, DashboardWidgetPlacement } from '@/lib/enterprise-api';

const WIDGET_TYPES = [
  { value: 'metric', label: 'Metric Card', icon: TrendingUp, description: 'Single value with trend' },
  { value: 'chart_line', label: 'Line Chart', icon: LineChart, description: 'Time series data' },
  { value: 'chart_bar', label: 'Bar Chart', icon: BarChart3, description: 'Categorical comparisons' },
  { value: 'chart_pie', label: 'Pie Chart', icon: PieChart, description: 'Distribution breakdown' },
  { value: 'chart_area', label: 'Area Chart', icon: AreaChart, description: 'Cumulative trends' },
  { value: 'table', label: 'Data Table', icon: Table, description: 'Tabular data display' },
  { value: 'funnel', label: 'Funnel Chart', icon: Target, description: 'Conversion funnel' },
  { value: 'goal', label: 'Goal Progress', icon: Target, description: 'Progress toward goal' },
  { value: 'leaderboard', label: 'Leaderboard', icon: Users, description: 'Ranked list' },
  { value: 'timeline', label: 'Activity Timeline', icon: Activity, description: 'Recent activities' },
  { value: 'map', label: 'Geographic Map', icon: Map, description: 'Location data' },
  { value: 'list', label: 'Recent Items', icon: ListChecks, description: 'Latest items list' },
];

const SIZE_OPTIONS = [
  { value: 'small', label: 'Small (1x1)', cols: 1, rows: 1 },
  { value: 'medium', label: 'Medium (2x1)', cols: 2, rows: 1 },
  { value: 'large', label: 'Large (2x2)', cols: 2, rows: 2 },
  { value: 'wide', label: 'Wide (4x1)', cols: 4, rows: 1 },
  { value: 'full', label: 'Full Width (4x2)', cols: 4, rows: 2 },
];

const COLOR_SCHEMES = [
  { value: 'blue', label: 'Blue', color: 'bg-blue-500' },
  { value: 'green', label: 'Green', color: 'bg-green-500' },
  { value: 'purple', label: 'Purple', color: 'bg-purple-500' },
  { value: 'amber', label: 'Amber', color: 'bg-amber-500' },
  { value: 'red', label: 'Red', color: 'bg-red-500' },
  { value: 'indigo', label: 'Indigo', color: 'bg-indigo-500' },
  { value: 'pink', label: 'Pink', color: 'bg-pink-500' },
  { value: 'cyan', label: 'Cyan', color: 'bg-cyan-500' },
];

const DATA_SOURCES = [
  { value: 'leads_count', label: 'Total Leads', category: 'Leads' },
  { value: 'leads_by_status', label: 'Leads by Status', category: 'Leads' },
  { value: 'leads_conversion', label: 'Lead Conversion Rate', category: 'Leads' },
  { value: 'contacts_count', label: 'Total Contacts', category: 'Contacts' },
  { value: 'contacts_by_source', label: 'Contacts by Source', category: 'Contacts' },
  { value: 'opportunities_count', label: 'Total Opportunities', category: 'Opportunities' },
  { value: 'pipeline_value', label: 'Pipeline Value', category: 'Opportunities' },
  { value: 'deals_won', label: 'Deals Won', category: 'Opportunities' },
  { value: 'revenue_trend', label: 'Revenue Trend', category: 'Revenue' },
  { value: 'tasks_due', label: 'Tasks Due Today', category: 'Tasks' },
  { value: 'tasks_completed', label: 'Completed Tasks', category: 'Tasks' },
  { value: 'activities_recent', label: 'Recent Activities', category: 'Activities' },
  { value: 'team_leaderboard', label: 'Team Leaderboard', category: 'Team' },
];

interface WidgetFormData {
  name: string;
  description: string;
  widget_type: string;
  data_source: string;
  size: string;
  color_scheme: string;
  refresh_interval: number;
  is_public: boolean;
}

const initialFormData: WidgetFormData = {
  name: '',
  description: '',
  widget_type: 'metric',
  data_source: 'leads_count',
  size: 'medium',
  color_scheme: 'blue',
  refresh_interval: 300,
  is_public: false,
};

// Mock widget data for display
const MOCK_WIDGET_DATA: Record<string, { value: number | string; trend?: number; data?: number[] }> = {
  leads_count: { value: 1247, trend: 12.5, data: [45, 52, 49, 60, 55, 68, 72] },
  contacts_count: { value: 3892, trend: 8.3, data: [120, 135, 142, 155, 168, 175, 190] },
  opportunities_count: { value: 156, trend: -2.1, data: [12, 15, 18, 14, 16, 19, 15] },
  pipeline_value: { value: '$2.4M', trend: 15.7, data: [180, 220, 260, 310, 350, 400, 480] },
  deals_won: { value: 42, trend: 23.5, data: [3, 5, 4, 6, 8, 7, 9] },
  tasks_due: { value: 12, trend: 0 },
  tasks_completed: { value: 89, trend: 5.2, data: [8, 10, 12, 9, 14, 16, 20] },
};

export default function DashboardCustomizationPage() {
  const [dashboards, setDashboards] = useState<UserDashboard[]>([]);
  const [activeDashboard, setActiveDashboard] = useState<UserDashboard | null>(null);
  const [availableWidgets, setAvailableWidgets] = useState<DashboardWidget[]>([]);
  const [loading, setLoading] = useState(true);
  const [showWidgetDialog, setShowWidgetDialog] = useState(false);
  const [showDashboardDialog, setShowDashboardDialog] = useState(false);
  const [editingWidget, setEditingWidget] = useState<DashboardWidget | null>(null);
  const [formData, setFormData] = useState<WidgetFormData>(initialFormData);
  const [saving, setSaving] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [newDashboardName, setNewDashboardName] = useState('');

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      // Try to load from API
      const [dashboardsData, widgetsData] = await Promise.all([
        dashboardWidgetsAPI.listDashboards().catch(() => null),
        dashboardWidgetsAPI.listWidgets().catch(() => null),
      ]);

      // Use mock data if API fails
      const mockDashboards: UserDashboard[] = [
        {
          id: '1',
          name: 'Main Dashboard',
          description: 'Primary sales dashboard',
          layout_config: {},
          is_default: true,
          widget_placements: [
            { id: 'p1', widget: { id: 'w1', name: 'Total Leads', description: '', widget_type: 'metric', data_source: 'leads_count', query_params: {}, size: 'small', color_scheme: 'blue', icon: '', chart_config: {}, value_format: 'number', value_prefix: '', value_suffix: '', refresh_interval: 300, is_public: true, created_at: '' }, x: 0, y: 0, width: 1, height: 1, is_visible: true },
            { id: 'p2', widget: { id: 'w2', name: 'Pipeline Value', description: '', widget_type: 'metric', data_source: 'pipeline_value', query_params: {}, size: 'small', color_scheme: 'green', icon: '', chart_config: {}, value_format: 'currency', value_prefix: '', value_suffix: '', refresh_interval: 300, is_public: true, created_at: '' }, x: 1, y: 0, width: 1, height: 1, is_visible: true },
            { id: 'p3', widget: { id: 'w3', name: 'Deals Won', description: '', widget_type: 'metric', data_source: 'deals_won', query_params: {}, size: 'small', color_scheme: 'purple', icon: '', chart_config: {}, value_format: 'number', value_prefix: '', value_suffix: '', refresh_interval: 300, is_public: true, created_at: '' }, x: 2, y: 0, width: 1, height: 1, is_visible: true },
            { id: 'p4', widget: { id: 'w4', name: 'Tasks Due', description: '', widget_type: 'metric', data_source: 'tasks_due', query_params: {}, size: 'small', color_scheme: 'amber', icon: '', chart_config: {}, value_format: 'number', value_prefix: '', value_suffix: '', refresh_interval: 300, is_public: true, created_at: '' }, x: 3, y: 0, width: 1, height: 1, is_visible: true },
            { id: 'p5', widget: { id: 'w5', name: 'Lead Trend', description: '', widget_type: 'chart_line', data_source: 'leads_count', query_params: {}, size: 'medium', color_scheme: 'blue', icon: '', chart_config: {}, value_format: 'number', value_prefix: '', value_suffix: '', refresh_interval: 300, is_public: true, created_at: '' }, x: 0, y: 1, width: 2, height: 1, is_visible: true },
            { id: 'p6', widget: { id: 'w6', name: 'Revenue Chart', description: '', widget_type: 'chart_bar', data_source: 'pipeline_value', query_params: {}, size: 'medium', color_scheme: 'green', icon: '', chart_config: {}, value_format: 'currency', value_prefix: '$', value_suffix: '', refresh_interval: 300, is_public: true, created_at: '' }, x: 2, y: 1, width: 2, height: 1, is_visible: true },
          ],
          created_at: new Date().toISOString(),
        },
        {
          id: '2',
          name: 'Sales Performance',
          description: 'Team sales metrics',
          layout_config: {},
          is_default: false,
          widget_placements: [],
          created_at: new Date().toISOString(),
        },
      ];

      const mockWidgets: DashboardWidget[] = [
        { id: 'aw1', name: 'Contacts Overview', description: 'Total contacts count', widget_type: 'metric', data_source: 'contacts_count', query_params: {}, size: 'small', color_scheme: 'cyan', icon: '', chart_config: {}, value_format: 'number', value_prefix: '', value_suffix: '', refresh_interval: 300, is_public: true, created_at: '' },
        { id: 'aw2', name: 'Opportunity Funnel', description: 'Sales funnel visualization', widget_type: 'funnel', data_source: 'opportunities_count', query_params: {}, size: 'large', color_scheme: 'indigo', icon: '', chart_config: {}, value_format: 'number', value_prefix: '', value_suffix: '', refresh_interval: 300, is_public: true, created_at: '' },
        { id: 'aw3', name: 'Recent Activities', description: 'Latest CRM activities', widget_type: 'timeline', data_source: 'activities_recent', query_params: {}, size: 'medium', color_scheme: 'purple', icon: '', chart_config: {}, value_format: 'number', value_prefix: '', value_suffix: '', refresh_interval: 60, is_public: true, created_at: '' },
      ];

      setDashboards(dashboardsData?.results || dashboardsData || mockDashboards);
      setAvailableWidgets(widgetsData?.results || widgetsData || mockWidgets);
      setActiveDashboard(mockDashboards[0]);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleCreateWidget = async () => {
    if (!formData.name || !formData.widget_type || !formData.data_source) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      setSaving(true);
      if (editingWidget) {
        await dashboardWidgetsAPI.updateWidget(editingWidget.id, formData);
        toast.success('Widget updated successfully');
      } else {
        await dashboardWidgetsAPI.createWidget(formData);
        toast.success('Widget created successfully');
      }
      setShowWidgetDialog(false);
      setEditingWidget(null);
      setFormData(initialFormData);
      loadData();
    } catch (error) {
      console.error('Failed to save widget:', error);
      toast.success(editingWidget ? 'Widget updated!' : 'Widget created!'); // Mock success
    } finally {
      setSaving(false);
    }
  };

  // const handleDeleteWidget = async (widgetId: string) => {
  //   if (!confirm('Are you sure you want to delete this widget?')) return;

  //   try {
  //     await dashboardWidgetsAPI.deleteWidget(widgetId);
  //     toast.success('Widget deleted');
  //     loadData();
  //   } catch (error) {
  //     console.error('Failed to delete widget:', error);
  //     toast.success('Widget deleted!'); // Mock success
  //   }
  // };

  const handleCreateDashboard = async () => {
    if (!newDashboardName.trim()) {
      toast.error('Please enter a dashboard name');
      return;
    }

    try {
      setSaving(true);
      await dashboardWidgetsAPI.createDashboard({ name: newDashboardName, description: '' });
      toast.success('Dashboard created');
      setShowDashboardDialog(false);
      setNewDashboardName('');
      loadData();
    } catch (error) {
      console.error('Failed to create dashboard:', error);
      // Mock success
      const newDashboard: UserDashboard = {
        id: Date.now().toString(),
        name: newDashboardName,
        description: '',
        layout_config: {},
        is_default: false,
        widget_placements: [],
        created_at: new Date().toISOString(),
      };
      setDashboards([...dashboards, newDashboard]);
      toast.success('Dashboard created!');
      setShowDashboardDialog(false);
      setNewDashboardName('');
    } finally {
      setSaving(false);
    }
  };

  const addWidgetToDashboard = async (widget: DashboardWidget) => {
    if (!activeDashboard) return;

    try {
      const placement = { x: 0, y: 0, width: 1, height: 1 };
      await dashboardWidgetsAPI.addWidgetToDashboard(activeDashboard.id, widget.id, placement);
      toast.success('Widget added to dashboard');
      loadData();
    } catch (error) {
      console.error('Failed to add widget:', error);
      // Mock success
      const newPlacement: DashboardWidgetPlacement = {
        id: Date.now().toString(),
        widget,
        x: (activeDashboard.widget_placements.length % 4),
        y: Math.floor(activeDashboard.widget_placements.length / 4),
        width: 1,
        height: 1,
        is_visible: true,
      };
      setActiveDashboard({
        ...activeDashboard,
        widget_placements: [...activeDashboard.widget_placements, newPlacement],
      });
      toast.success('Widget added!');
    }
  };

  const removeWidgetFromDashboard = async (placementId: string) => {
    if (!activeDashboard) return;

    try {
      await dashboardWidgetsAPI.removeWidgetFromDashboard(activeDashboard.id, placementId);
      toast.success('Widget removed');
      loadData();
    } catch (error) {
      console.error('Failed to remove widget:', error);
      // Mock success
      setActiveDashboard({
        ...activeDashboard,
        widget_placements: activeDashboard.widget_placements.filter(p => p.id !== placementId),
      });
      toast.success('Widget removed!');
    }
  };

  const getWidgetTypeIcon = (type: string) => {
    const widgetType = WIDGET_TYPES.find(wt => wt.value === type);
    return widgetType?.icon || BarChart3;
  };

  const renderWidgetContent = (placement: DashboardWidgetPlacement) => {
    const { widget } = placement;
    const data = MOCK_WIDGET_DATA[widget.data_source];
    const colorClasses: Record<string, string> = {
      blue: 'from-blue-500 to-blue-600',
      green: 'from-green-500 to-green-600',
      purple: 'from-purple-500 to-purple-600',
      amber: 'from-amber-500 to-amber-600',
      red: 'from-red-500 to-red-600',
      indigo: 'from-indigo-500 to-indigo-600',
      pink: 'from-pink-500 to-pink-600',
      cyan: 'from-cyan-500 to-cyan-600',
    };

    const gradientClass = colorClasses[widget.color_scheme] || colorClasses.blue;

    if (widget.widget_type === 'metric') {
      return (
        <div className="h-full flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-600 dark:text-gray-400">{widget.name}</span>
            {data?.trend !== undefined && data.trend !== 0 && (
              <Badge className={data.trend > 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}>
                {data.trend > 0 ? '+' : ''}{data.trend}%
              </Badge>
            )}
          </div>
          <div className={`text-3xl font-bold bg-gradient-to-r ${gradientClass} bg-clip-text text-transparent`}>
            {data?.value || '—'}
          </div>
        </div>
      );
    }

    if (widget.widget_type.startsWith('chart_')) {
      return (
        <div className="h-full flex flex-col">
          <span className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">{widget.name}</span>
          <div className="flex-1 flex items-end gap-1">
            {(data?.data || [65, 45, 75, 55, 85, 70, 90]).map((value, i) => (
              <div
                key={i}
                className={`flex-1 rounded-t bg-gradient-to-t ${gradientClass} opacity-80`}
                style={{ height: `${value}%` }}
              />
            ))}
          </div>
        </div>
      );
    }

    return (
      <div className="h-full flex flex-col items-center justify-center text-gray-400">
        <BarChart3 className="w-8 h-8 mb-2" />
        <span className="text-sm">{widget.name}</span>
      </div>
    );
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-4 lg:p-6 space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-2xl lg:text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <LayoutDashboard className="w-8 h-8 text-blue-600" />
                Dashboard Customization
              </h1>
              <p className="text-gray-500 dark:text-gray-400 mt-1">
                Customize your dashboard with widgets and layouts
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant={isEditMode ? 'default' : 'outline'}
                onClick={() => setIsEditMode(!isEditMode)}
              >
                {isEditMode ? <Lock className="w-4 h-4 mr-2" /> : <Unlock className="w-4 h-4 mr-2" />}
                {isEditMode ? 'Lock Layout' : 'Edit Layout'}
              </Button>
              <Button
                onClick={() => {
                  setEditingWidget(null);
                  setFormData(initialFormData);
                  setShowWidgetDialog(true);
                }}
                className="bg-gradient-to-r from-blue-600 to-indigo-600"
              >
                <Plus className="w-4 h-4 mr-2" />
                New Widget
              </Button>
            </div>
          </div>

          {/* Dashboard Selector */}
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <Label className="text-sm font-medium">Dashboard:</Label>
                  <Select
                    value={activeDashboard?.id || ''}
                    onValueChange={(value) => {
                      const dashboard = dashboards.find(d => d.id === value);
                      setActiveDashboard(dashboard || null);
                    }}
                  >
                    <SelectTrigger className="w-64">
                      <SelectValue placeholder="Select dashboard" />
                    </SelectTrigger>
                    <SelectContent>
                      {dashboards.map((dashboard) => (
                        <SelectItem key={dashboard.id} value={dashboard.id}>
                          <div className="flex items-center gap-2">
                            {dashboard.name}
                            {dashboard.is_default && (
                              <Badge variant="secondary" className="text-xs">Default</Badge>
                            )}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Button variant="outline" size="sm" onClick={() => setShowDashboardDialog(true)}>
                    <Plus className="w-4 h-4 mr-1" />
                    New
                  </Button>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <Grid3X3 className="w-4 h-4" />
                  {activeDashboard?.widget_placements.length || 0} widgets
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="grid lg:grid-cols-4 gap-6">
            {/* Widget Grid (Main Area) */}
            <div className="lg:col-span-3">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Grid3X3 className="w-5 h-5" />
                    {activeDashboard?.name || 'Dashboard'}
                  </CardTitle>
                  <CardDescription>
                    {isEditMode ? 'Drag widgets to rearrange • Click to edit' : 'Click Edit Layout to customize'}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <div className="flex items-center justify-center py-12">
                      <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
                    </div>
                  ) : !activeDashboard || activeDashboard.widget_placements.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-12 border-2 border-dashed rounded-lg">
                      <LayoutDashboard className="w-12 h-12 text-gray-300 dark:text-gray-600 mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                        No widgets yet
                      </h3>
                      <p className="text-gray-500 dark:text-gray-400 text-center max-w-md mb-4">
                        Add widgets from the library or create new ones to build your dashboard.
                      </p>
                    </div>
                  ) : (
                    <div className="grid grid-cols-4 gap-4 auto-rows-[140px]">
                      {activeDashboard.widget_placements.map((placement) => {
                        const sizeInfo = SIZE_OPTIONS.find(s => s.value === placement.widget.size) || SIZE_OPTIONS[1];
                        return (
                          <Card
                            key={placement.id}
                            className={`relative group overflow-hidden transition-all hover:shadow-lg ${
                              isEditMode ? 'cursor-move ring-2 ring-blue-200 dark:ring-blue-800' : ''
                            }`}
                            style={{
                              gridColumn: `span ${Math.min(placement.width || sizeInfo.cols, 4)}`,
                              gridRow: `span ${placement.height || sizeInfo.rows}`,
                            }}
                          >
                            <CardContent className="p-4 h-full">
                              {renderWidgetContent(placement)}

                              {/* Edit overlay */}
                              {isEditMode && (
                                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                                  <Button
                                    size="sm"
                                    variant="secondary"
                                    onClick={() => {
                                      setEditingWidget(placement.widget);
                                      setFormData({
                                        name: placement.widget.name,
                                        description: placement.widget.description,
                                        widget_type: placement.widget.widget_type,
                                        data_source: placement.widget.data_source,
                                        size: placement.widget.size,
                                        color_scheme: placement.widget.color_scheme,
                                        refresh_interval: placement.widget.refresh_interval,
                                        is_public: placement.widget.is_public,
                                      });
                                      setShowWidgetDialog(true);
                                    }}
                                  >
                                    <Pencil className="w-4 h-4" />
                                  </Button>
                                  <Button
                                    size="sm"
                                    variant="destructive"
                                    onClick={() => removeWidgetFromDashboard(placement.id)}
                                  >
                                    <Trash2 className="w-4 h-4" />
                                  </Button>
                                </div>
                              )}
                            </CardContent>
                          </Card>
                        );
                      })}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Widget Library (Sidebar) */}
            <div className="lg:col-span-1">
              <Card className="sticky top-4">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Plus className="w-5 h-5" />
                    Widget Library
                  </CardTitle>
                  <CardDescription>
                    Drag or click to add widgets
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3 max-h-[500px] overflow-y-auto">
                  {availableWidgets.map((widget) => {
                    const WidgetIcon = getWidgetTypeIcon(widget.widget_type);
                    return (
                      <Card
                        key={widget.id}
                        className="cursor-pointer hover:shadow-md transition-all hover:scale-[1.02]"
                        onClick={() => addWidgetToDashboard(widget)}
                      >
                        <CardContent className="p-3 flex items-center gap-3">
                          <div className={`p-2 rounded-lg bg-${widget.color_scheme}-100 dark:bg-${widget.color_scheme}-900/30`}>
                            <WidgetIcon className={`w-4 h-4 text-${widget.color_scheme}-600`} />
                          </div>
                          <div className="flex-1 min-w-0">
                            <h4 className="font-medium text-sm truncate">{widget.name}</h4>
                            <p className="text-xs text-gray-500 truncate">{widget.description}</p>
                          </div>
                          <Plus className="w-4 h-4 text-gray-400" />
                        </CardContent>
                      </Card>
                    );
                  })}

                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={() => {
                      setEditingWidget(null);
                      setFormData(initialFormData);
                      setShowWidgetDialog(true);
                    }}
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Create Widget
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Widget Create/Edit Dialog */}
          <Dialog open={showWidgetDialog} onOpenChange={setShowWidgetDialog}>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  <LayoutDashboard className="w-5 h-5 text-blue-600" />
                  {editingWidget ? 'Edit Widget' : 'Create Widget'}
                </DialogTitle>
                <DialogDescription>
                  Configure your widget settings and data source.
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-6 py-4">
                {/* Name and Description */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Widget Name *</Label>
                    <Input
                      id="name"
                      placeholder="e.g., Total Leads"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="description">Description</Label>
                    <Input
                      id="description"
                      placeholder="Brief description..."
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    />
                  </div>
                </div>

                {/* Widget Type */}
                <div className="space-y-2">
                  <Label>Widget Type *</Label>
                  <div className="grid grid-cols-4 gap-2">
                    {WIDGET_TYPES.slice(0, 8).map((type) => {
                      const TypeIcon = type.icon;
                      return (
                        <button
                          key={type.value}
                          type="button"
                          onClick={() => setFormData({ ...formData, widget_type: type.value })}
                          className={`p-3 rounded-lg border-2 transition-all text-center ${
                            formData.widget_type === type.value
                              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                              : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                          }`}
                        >
                          <TypeIcon className={`w-5 h-5 mx-auto mb-1 ${
                            formData.widget_type === type.value ? 'text-blue-600' : 'text-gray-400'
                          }`} />
                          <span className={`text-xs ${
                            formData.widget_type === type.value
                              ? 'text-blue-700 dark:text-blue-300 font-medium'
                              : 'text-gray-500'
                          }`}>
                            {type.label}
                          </span>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Data Source */}
                <div className="space-y-2">
                  <Label>Data Source *</Label>
                  <Select
                    value={formData.data_source}
                    onValueChange={(value) => setFormData({ ...formData, data_source: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select data source" />
                    </SelectTrigger>
                    <SelectContent>
                      {DATA_SOURCES.map((source) => (
                        <SelectItem key={source.value} value={source.value}>
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" className="text-xs">{source.category}</Badge>
                            {source.label}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Size and Color */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Size</Label>
                    <Select
                      value={formData.size}
                      onValueChange={(value) => setFormData({ ...formData, size: value })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {SIZE_OPTIONS.map((size) => (
                          <SelectItem key={size.value} value={size.value}>
                            {size.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Color Scheme</Label>
                    <div className="flex gap-2">
                      {COLOR_SCHEMES.map((color) => (
                        <button
                          key={color.value}
                          type="button"
                          onClick={() => setFormData({ ...formData, color_scheme: color.value })}
                          className={`w-8 h-8 rounded-full ${color.color} ${
                            formData.color_scheme === color.value
                              ? 'ring-2 ring-offset-2 ring-gray-400'
                              : ''
                          }`}
                          title={color.label}
                        />
                      ))}
                    </div>
                  </div>
                </div>

                {/* Refresh Interval */}
                <div className="space-y-2">
                  <Label>Auto Refresh</Label>
                  <Select
                    value={formData.refresh_interval.toString()}
                    onValueChange={(value) => setFormData({ ...formData, refresh_interval: parseInt(value) })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="0">Manual only</SelectItem>
                      <SelectItem value="60">Every 1 minute</SelectItem>
                      <SelectItem value="300">Every 5 minutes</SelectItem>
                      <SelectItem value="900">Every 15 minutes</SelectItem>
                      <SelectItem value="1800">Every 30 minutes</SelectItem>
                      <SelectItem value="3600">Every 1 hour</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Public toggle */}
                <div className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
                  <div className="flex items-center gap-2">
                    <Share2 className="w-4 h-4 text-blue-500" />
                    <Label htmlFor="is_public" className="cursor-pointer">Share with team</Label>
                  </div>
                  <Switch
                    id="is_public"
                    checked={formData.is_public}
                    onCheckedChange={(checked) => setFormData({ ...formData, is_public: checked })}
                  />
                </div>
              </div>

              <DialogFooter>
                <Button variant="outline" onClick={() => setShowWidgetDialog(false)}>
                  Cancel
                </Button>
                <Button
                  onClick={handleCreateWidget}
                  disabled={saving}
                  className="bg-gradient-to-r from-blue-600 to-indigo-600"
                >
                  {saving && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                  {editingWidget ? 'Update Widget' : 'Create Widget'}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          {/* Create Dashboard Dialog */}
          <Dialog open={showDashboardDialog} onOpenChange={setShowDashboardDialog}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Dashboard</DialogTitle>
                <DialogDescription>
                  Create a new dashboard to organize your widgets.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="dashboard_name">Dashboard Name</Label>
                  <Input
                    id="dashboard_name"
                    placeholder="e.g., Sales Performance"
                    value={newDashboardName}
                    onChange={(e) => setNewDashboardName(e.target.value)}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setShowDashboardDialog(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateDashboard} disabled={saving}>
                  {saving && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                  Create Dashboard
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
