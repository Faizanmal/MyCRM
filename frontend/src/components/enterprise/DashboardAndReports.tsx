// Dashboard Builder and Report Builder Components
/* eslint-disable @typescript-eslint/no-explicit-any */
'use client';

import React, { useState, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { LayoutDashboard, Plus, BarChart3, PieChart, TrendingUp, Users, Download } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import axios from 'axios';

interface Dashboard {
  id: string;
  name: string;
  description: string;
  layout: any;
  is_shared: boolean;
}

interface Widget {
  id: string;
  type: 'chart' | 'metric' | 'table' | 'list';
  title: string;
  config: any;
}

interface Report {
  id: string;
  name: string;
  model_name: string;
  columns: string[];
  filters: any;
  is_scheduled: boolean;
}

export function DashboardBuilder() {
  const [dashboards, setDashboards] = useState<Dashboard[]>([]);
  const [selectedDashboard, setSelectedDashboard] = useState<Dashboard | null>(null);
  const [widgets, setWidgets] = useState<Widget[]>([]);
  const { toast } = useToast();

  const loadDashboards = useCallback(async () => {
    try {
      const response = await axios.get('/api/core/dashboards/');
      setDashboards(response.data);
    } catch (error) {
      console.error('Error loading dashboards:', error);
      toast({
        title: 'Error',
        description: 'Failed to load dashboards',
        variant: 'destructive',
      });
    }
  }, [toast]);

  const createDashboard = async (name: string, description: string) => {
    try {
      const response = await axios.post('/api/core/dashboards/', {
        name,
        description,
        layout: { widgets: [] },
        is_shared: false,
      });
      setDashboards([...dashboards, response.data]);
      toast({
        title: 'Success',
        description: 'Dashboard created successfully',
      });
    } catch (error) {
      console.error('Error creating dashboard:', error);
      toast({
        title: 'Error',
        description: 'Failed to create dashboard',
        variant: 'destructive',
      });
    }
  };

  const addWidget = (widget: Widget) => {
    setWidgets([...widgets, widget]);
  };

  React.useEffect(() => {
    loadDashboards();
  }, [loadDashboards]);

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <LayoutDashboard className="h-8 w-8" />
            Dashboard Builder
          </h1>
          <p className="text-muted-foreground mt-1">Create and customize your dashboards</p>
        </div>
        <CreateDashboardDialog onCreate={createDashboard} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Dashboard List */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>My Dashboards</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {dashboards.map(dashboard => (
                <Button
                  key={dashboard.id}
                  variant={selectedDashboard?.id === dashboard.id ? 'default' : 'outline'}
                  className="w-full justify-start"
                  onClick={() => setSelectedDashboard(dashboard)}
                >
                  {dashboard.name}
                </Button>
              ))}
              {dashboards.length === 0 && (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No dashboards yet
                </p>
              )}
            </CardContent>
          </Card>

          <Card className="mt-4">
            <CardHeader>
              <CardTitle className="text-sm">Add Widgets</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <WidgetPalette onAddWidget={addWidget} />
            </CardContent>
          </Card>
        </div>

        {/* Dashboard Canvas */}
        <div className="lg:col-span-3">
          {selectedDashboard ? (
            <DashboardCanvas
              dashboard={selectedDashboard}
              widgets={widgets}
              onRemoveWidget={(id) => setWidgets(widgets.filter(w => w.id !== id))}
            />
          ) : (
            <Card>
              <CardContent className="py-12 text-center text-muted-foreground">
                <LayoutDashboard className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Select or create a dashboard to start building</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

// Dashboard Canvas Component
function DashboardCanvas({ dashboard, widgets, onRemoveWidget }: { dashboard: Dashboard; widgets: Widget[]; onRemoveWidget: (id: string) => void }) {
  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle>{dashboard.name}</CardTitle>
            <CardDescription>{dashboard.description}</CardDescription>
          </div>
          <Badge>{dashboard.is_shared ? 'Shared' : 'Private'}</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {widgets.map(widget => (
            <WidgetRenderer key={widget.id} widget={widget} onRemove={() => onRemoveWidget(widget.id)} />
          ))}
          {widgets.length === 0 && (
            <div className="col-span-2 text-center py-12 text-muted-foreground">
              <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>Add widgets from the sidebar to build your dashboard</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

// Widget Palette Component
function WidgetPalette({ onAddWidget }: { onAddWidget: (widget: Widget) => void }) {
  const widgetTypes = [
    { type: 'metric', icon: TrendingUp, label: 'Metric', color: 'blue' },
    { type: 'chart', icon: BarChart3, label: 'Chart', color: 'green' },
    { type: 'pie', icon: PieChart, label: 'Pie Chart', color: 'purple' },
    { type: 'list', icon: Users, label: 'List', color: 'orange' },
  ];

  return (
    <div className="space-y-2">
      {widgetTypes.map(({ type, icon: Icon, label, color }) => (
        <Button
          key={type}
          variant="outline"
          className="w-full justify-start"
          onClick={() => onAddWidget({
            id: `widget-${Date.now()}`,
            type: type as any,
            title: `New ${label}`,
            config: {},
          })}
        >
          <Icon className="h-4 w-4 mr-2" />
          {label}
        </Button>
      ))}
    </div>
  );
}

// Widget Renderer Component
function WidgetRenderer({ widget, onRemove }: { widget: Widget; onRemove: () => void }) {
  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-start">
          <CardTitle className="text-lg">{widget.title}</CardTitle>
          <Button variant="ghost" size="sm" onClick={onRemove}>×</Button>
        </div>
      </CardHeader>
      <CardContent>
        {widget.type === 'metric' && (
          <div className="text-center py-8">
            <p className="text-4xl font-bold">1,234</p>
            <p className="text-sm text-muted-foreground mt-2">Sample Metric</p>
          </div>
        )}
        {widget.type === 'chart' && (
          <div className="h-48 flex items-center justify-center bg-muted rounded">
            <BarChart3 className="h-12 w-12 text-muted-foreground" />
          </div>
        )}
        {widget.type === 'list' && (
          <div className="space-y-2">
            {[1, 2, 3].map(i => (
              <div key={i} className="p-2 bg-muted rounded">
                <p className="text-sm">List Item {i}</p>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Create Dashboard Dialog
function CreateDashboardDialog({ onCreate }: { onCreate: (name: string, description: string) => void }) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');

  const handleCreate = () => {
    if (name.trim()) {
      onCreate(name, description);
      setName('');
      setDescription('');
      setOpen(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Create Dashboard
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create Dashboard</DialogTitle>
          <DialogDescription>Create a new custom dashboard</DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <div>
            <Label htmlFor="name">Dashboard Name</Label>
            <Input
              id="name"
              placeholder="e.g., Sales Overview"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="description">Description</Label>
            <Input
              id="description"
              placeholder="Describe your dashboard"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreate}>Create</Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

// Report Builder Component
export function ReportBuilder() {
  const [reports, setReports] = useState<Report[]>([]);
  const { toast } = useToast();

  const loadReports = async () => {
    try {
      const response = await axios.get('/api/core/reports/');
      setReports(response.data);
    } catch (error) {
      console.error('Error loading reports:', error);
      toast({
        title: 'Error',
        description: 'Failed to load reports',
        variant: 'destructive',
      });
    }
  };

  React.useEffect(() => {
    loadReports();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const generateReport = async (reportId: string) => {
    try {
      const response = await axios.post(`/api/core/reports/${reportId}/generate/`, {}, {
        responseType: 'blob',
      });
      
      // Download the file
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `report-${reportId}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast({
        title: 'Success',
        description: 'Report generated successfully',
      });
    } catch (error) {
      console.error('Error generating report:', error);
      toast({
        title: 'Error',
        description: 'Failed to generate report',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <BarChart3 className="h-8 w-8" />
            Report Builder
          </h1>
          <p className="text-muted-foreground mt-1">Create and manage custom reports</p>
        </div>
        <CreateReportDialog onCreated={loadReports} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {reports.map(report => (
          <ReportCard key={report.id} report={report} onGenerate={() => generateReport(report.id)} />
        ))}
      </div>

      {reports.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No reports yet. Create your first report to get started.</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

// Report Card Component
function ReportCard({ report, onGenerate }: { report: Report; onGenerate: () => void }) {
  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-start">
          <CardTitle className="text-lg">{report.name}</CardTitle>
          {report.is_scheduled && <Badge>Scheduled</Badge>}
        </div>
        <CardDescription>
          {report.model_name} - {report.columns.length} columns
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-2">
        <Button className="w-full" onClick={onGenerate}>
          <Download className="h-4 w-4 mr-2" />
          Generate Report
        </Button>
        <Button className="w-full" variant="outline">
          Edit Report
        </Button>
      </CardContent>
    </Card>
  );
}

// Create Report Dialog
function CreateReportDialog({ onCreated }: { onCreated: () => void }) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState('');
  const [modelName, setModelName] = useState('contact_management.Contact');
  const [columns, setColumns] = useState<string[]>([]);
  const { toast } = useToast();

  const MODELS = [
    { value: 'contact_management.Contact', label: 'Contacts' },
    { value: 'lead_management.Lead', label: 'Leads' },
    { value: 'opportunity_management.Opportunity', label: 'Opportunities' },
  ];

  const handleCreate = async () => {
    try {
      await axios.post('/api/core/reports/', {
        name,
        model_name: modelName,
        columns,
        filters: {},
        is_scheduled: false,
      });
      toast({
        title: 'Success',
        description: 'Report created successfully',
      });
      setOpen(false);
      setName('');
      onCreated();
    } catch (error) {
      console.error('Error creating report:', error);
      toast({
        title: 'Error',
        description: 'Failed to create report',
        variant: 'destructive',
      });
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Create Report
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create Report</DialogTitle>
          <DialogDescription>Configure a new custom report</DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <div>
            <Label htmlFor="report-name">Report Name</Label>
            <Input
              id="report-name"
              placeholder="e.g., Monthly Sales Report"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="model">Data Source</Label>
            <Select value={modelName} onValueChange={setModelName}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {MODELS.map(model => (
                  <SelectItem key={model.value} value={model.value}>
                    {model.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreate}>Create Report</Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

export default function DashboardAndReports() {
  return (
    <Tabs defaultValue="dashboard" className="w-full">
      <TabsList className="grid w-full grid-cols-2">
        <TabsTrigger value="dashboard">Dashboard Builder</TabsTrigger>
        <TabsTrigger value="reports">Report Builder</TabsTrigger>
      </TabsList>
      <TabsContent value="dashboard">
        <DashboardBuilder />
      </TabsContent>
      <TabsContent value="reports">
        <ReportBuilder />
      </TabsContent>
    </Tabs>
  );
}
