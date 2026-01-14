'use client';

import React, { useState } from 'react';
// import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Activity,
  Server,
  Database,
  HardDrive,
  Cpu,
  MemoryStick,
  Wifi,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  RefreshCw,
  Settings,
  Shield,
  FileText,
  Download,
  Upload,
  Trash2,
  GitMerge,
  Calendar,
  Bell,
  Flag,
  Play,
  Pause,
  Eye,
} from 'lucide-react';

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Switch } from '@/components/ui/switch';

// Types
interface HealthMetric {
  name: string;
  category: string;
  value: number;
  unit: string;
  status: 'healthy' | 'warning' | 'critical';
  thresholdWarning: number;
  thresholdCritical: number;
}

interface SystemAlert {
  id: string;
  title: string;
  message: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  category: string;
  source: string;
  status: 'active' | 'acknowledged' | 'resolved';
  createdAt: string;
}

interface BulkOperation {
  id: string;
  operationType: string;
  entityType: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  totalRecords: number;
  processedRecords: number;
  successfulRecords: number;
  failedRecords: number;
  progressPercent: number;
  startedAt?: string;
  completedAt?: string;
}

interface ScheduledTask {
  id: string;
  name: string;
  description: string;
  scheduleType: string;
  cronExpression?: string;
  isActive: boolean;
  lastRunAt?: string;
  lastRunStatus?: string;
  nextRunAt?: string;
}

interface FeatureFlag {
  id: string;
  name: string;
  description: string;
  isEnabled: boolean;
  targetType: string;
  rolloutPercentage: number;
}

// Mock data
const mockHealthMetrics: HealthMetric[] = [
  { name: 'CPU Usage', category: 'performance', value: 45, unit: '%', status: 'healthy', thresholdWarning: 70, thresholdCritical: 90 },
  { name: 'Memory Usage', category: 'performance', value: 62, unit: '%', status: 'healthy', thresholdWarning: 80, thresholdCritical: 95 },
  { name: 'Disk Usage', category: 'storage', value: 78, unit: '%', status: 'warning', thresholdWarning: 75, thresholdCritical: 90 },
  { name: 'API Response Time', category: 'api', value: 145, unit: 'ms', status: 'healthy', thresholdWarning: 500, thresholdCritical: 1000 },
  { name: 'Database Connections', category: 'database', value: 85, unit: 'connections', status: 'healthy', thresholdWarning: 150, thresholdCritical: 200 },
  { name: 'Cache Hit Rate', category: 'cache', value: 94, unit: '%', status: 'healthy', thresholdWarning: 80, thresholdCritical: 60 },
  { name: 'Queue Size', category: 'queue', value: 1250, unit: 'jobs', status: 'healthy', thresholdWarning: 5000, thresholdCritical: 10000 },
  { name: 'Error Rate', category: 'api', value: 0.3, unit: '%', status: 'healthy', thresholdWarning: 1, thresholdCritical: 5 },
];

const mockAlerts: SystemAlert[] = [
  {
    id: '1',
    title: 'Disk Usage Warning',
    message: 'Primary storage disk is at 78% capacity. Consider cleaning up or expanding storage.',
    severity: 'warning',
    category: 'storage',
    source: 'monitoring-service',
    status: 'active',
    createdAt: '2024-03-15T10:30:00',
  },
  {
    id: '2',
    title: 'Failed Login Attempts',
    message: '15 failed login attempts detected from IP 192.168.1.100 in the last hour.',
    severity: 'warning',
    category: 'security',
    source: 'auth-service',
    status: 'active',
    createdAt: '2024-03-15T09:45:00',
  },
  {
    id: '3',
    title: 'Email Service Degraded',
    message: 'Email delivery delays detected. Some emails may be delayed by up to 10 minutes.',
    severity: 'info',
    category: 'external',
    source: 'email-service',
    status: 'acknowledged',
    createdAt: '2024-03-15T08:20:00',
  },
];

const mockBulkOperations: BulkOperation[] = [
  {
    id: '1',
    operationType: 'import',
    entityType: 'contacts',
    status: 'processing',
    totalRecords: 5000,
    processedRecords: 3250,
    successfulRecords: 3200,
    failedRecords: 50,
    progressPercent: 65,
    startedAt: '2024-03-15T10:00:00',
  },
  {
    id: '2',
    operationType: 'export',
    entityType: 'deals',
    status: 'completed',
    totalRecords: 1200,
    processedRecords: 1200,
    successfulRecords: 1200,
    failedRecords: 0,
    progressPercent: 100,
    startedAt: '2024-03-15T09:00:00',
    completedAt: '2024-03-15T09:15:00',
  },
];

const mockScheduledTasks: ScheduledTask[] = [
  {
    id: '1',
    name: 'Daily Report Generation',
    description: 'Generate and email daily sales reports',
    scheduleType: 'cron',
    cronExpression: '0 6 * * *',
    isActive: true,
    lastRunAt: '2024-03-15T06:00:00',
    lastRunStatus: 'completed',
    nextRunAt: '2024-03-16T06:00:00',
  },
  {
    id: '2',
    name: 'Database Backup',
    description: 'Automated database backup to cloud storage',
    scheduleType: 'cron',
    cronExpression: '0 2 * * *',
    isActive: true,
    lastRunAt: '2024-03-15T02:00:00',
    lastRunStatus: 'completed',
    nextRunAt: '2024-03-16T02:00:00',
  },
  {
    id: '3',
    name: 'Cache Cleanup',
    description: 'Clear expired cache entries',
    scheduleType: 'interval',
    isActive: true,
    lastRunAt: '2024-03-15T10:00:00',
    lastRunStatus: 'completed',
    nextRunAt: '2024-03-15T11:00:00',
  },
];

const mockFeatureFlags: FeatureFlag[] = [
  { id: '1', name: 'new_dashboard', description: 'New redesigned dashboard', isEnabled: true, targetType: 'percentage', rolloutPercentage: 50 },
  { id: '2', name: 'ai_insights', description: 'AI-powered insights feature', isEnabled: true, targetType: 'roles', rolloutPercentage: 100 },
  { id: '3', name: 'dark_mode_v2', description: 'Enhanced dark mode theme', isEnabled: false, targetType: 'all', rolloutPercentage: 0 },
  { id: '4', name: 'beta_features', description: 'Access to beta features', isEnabled: true, targetType: 'users', rolloutPercentage: 100 },
];

// Utility Components
const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const colors: Record<string, string> = {
    healthy: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    critical: 'bg-red-100 text-red-800',
    active: 'bg-red-100 text-red-800',
    acknowledged: 'bg-yellow-100 text-yellow-800',
    resolved: 'bg-green-100 text-green-800',
    pending: 'bg-gray-100 text-gray-800',
    processing: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
  };

  return (
    <Badge className={colors[status] || 'bg-gray-100 text-gray-800'}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </Badge>
  );
};

const MetricIcon: React.FC<{ category: string }> = ({ category }) => {
  const icons: Record<string, React.ReactNode> = {
    performance: <Cpu className="h-5 w-5" />,
    database: <Database className="h-5 w-5" />,
    storage: <HardDrive className="h-5 w-5" />,
    cache: <MemoryStick className="h-5 w-5" />,
    queue: <Activity className="h-5 w-5" />,
    api: <Wifi className="h-5 w-5" />,
  };
  return <>{icons[category] || <Server className="h-5 w-5" />}</>;
};

// Tab Components
const SystemHealthTab: React.FC = () => (
  <div className="space-y-6">
    {/* Overall Status */}
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="h-16 w-16 rounded-full bg-green-100 flex items-center justify-center">
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
            <div>
              <h3 className="text-2xl font-bold">System Healthy</h3>
              <p className="text-muted-foreground">All critical services operational</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-muted-foreground">Last checked</p>
            <p className="font-medium">2 minutes ago</p>
          </div>
          <Button variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </CardContent>
    </Card>

    {/* Metrics Grid */}
    <div className="grid grid-cols-4 gap-4">
      {mockHealthMetrics.map((metric) => (
        <Card key={metric.name}>
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <MetricIcon category={metric.category} />
                <span className="text-sm font-medium">{metric.name}</span>
              </div>
              <StatusBadge status={metric.status} />
            </div>
            <p className="text-2xl font-bold">
              {metric.value}
              <span className="text-sm font-normal text-muted-foreground ml-1">
                {metric.unit}
              </span>
            </p>
            <Progress
              value={(metric.value / metric.thresholdCritical) * 100}
              className={`h-1.5 mt-2 ${
                metric.status === 'critical'
                  ? 'bg-red-200'
                  : metric.status === 'warning'
                  ? 'bg-yellow-200'
                  : ''
              }`}
            />
          </CardContent>
        </Card>
      ))}
    </div>

    {/* Active Alerts */}
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-yellow-500" />
          Active Alerts
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {mockAlerts
            .filter((a) => a.status !== 'resolved')
            .map((alert) => (
              <div
                key={alert.id}
                className={`p-4 rounded-lg border-l-4 ${
                  alert.severity === 'critical'
                    ? 'border-red-500 bg-red-50'
                    : alert.severity === 'error'
                    ? 'border-red-400 bg-red-50'
                    : alert.severity === 'warning'
                    ? 'border-yellow-500 bg-yellow-50'
                    : 'border-blue-500 bg-blue-50'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-medium">{alert.title}</h4>
                      <StatusBadge status={alert.status} />
                    </div>
                    <p className="text-sm text-muted-foreground">{alert.message}</p>
                    <p className="text-xs text-muted-foreground mt-2">
                      Source: {alert.source} • {new Date(alert.createdAt).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline">
                      Acknowledge
                    </Button>
                    <Button size="sm" variant="outline">
                      Resolve
                    </Button>
                  </div>
                </div>
              </div>
            ))}
        </div>
      </CardContent>
    </Card>
  </div>
);

const BulkOperationsTab: React.FC = () => (
  <div className="space-y-6">
    <div className="flex justify-between items-center">
      <h3 className="text-lg font-semibold">Bulk Operations</h3>
      <div className="flex gap-2">
        <Button>
          <Upload className="h-4 w-4 mr-2" />
          Import Data
        </Button>
        <Button variant="outline">
          <Download className="h-4 w-4 mr-2" />
          Export Data
        </Button>
      </div>
    </div>

    {/* Active Operations */}
    <Card>
      <CardHeader>
        <CardTitle>Active Operations</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {mockBulkOperations.map((op) => (
          <div key={op.id} className="p-4 border rounded-lg">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                {op.operationType === 'import' ? (
                  <Upload className="h-5 w-5 text-blue-500" />
                ) : op.operationType === 'export' ? (
                  <Download className="h-5 w-5 text-green-500" />
                ) : (
                  <GitMerge className="h-5 w-5 text-purple-500" />
                )}
                <div>
                  <h4 className="font-medium capitalize">
                    {op.operationType} {op.entityType}
                  </h4>
                  <p className="text-sm text-muted-foreground">
                    Started {new Date(op.startedAt!).toLocaleTimeString()}
                  </p>
                </div>
              </div>
              <StatusBadge status={op.status} />
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>
                  {op.processedRecords.toLocaleString()} / {op.totalRecords.toLocaleString()} records
                </span>
                <span>{op.progressPercent}%</span>
              </div>
              <Progress value={op.progressPercent} />
              <div className="flex gap-4 text-sm text-muted-foreground">
                <span className="text-green-600">✓ {op.successfulRecords.toLocaleString()} successful</span>
                {op.failedRecords > 0 && (
                  <span className="text-red-600">✗ {op.failedRecords.toLocaleString()} failed</span>
                )}
              </div>
            </div>

            {op.status === 'processing' && (
              <div className="flex gap-2 mt-3">
                <Button size="sm" variant="outline">
                  <Pause className="h-4 w-4 mr-1" />
                  Pause
                </Button>
                <Button size="sm" variant="outline" className="text-red-600">
                  <XCircle className="h-4 w-4 mr-1" />
                  Cancel
                </Button>
              </div>
            )}
          </div>
        ))}
      </CardContent>
    </Card>

    {/* Quick Actions */}
    <div className="grid grid-cols-4 gap-4">
      <Card className="cursor-pointer hover:bg-muted/50">
        <CardContent className="p-4 text-center">
          <Upload className="h-8 w-8 mx-auto mb-2 text-blue-500" />
          <p className="font-medium">Import Contacts</p>
        </CardContent>
      </Card>
      <Card className="cursor-pointer hover:bg-muted/50">
        <CardContent className="p-4 text-center">
          <Download className="h-8 w-8 mx-auto mb-2 text-green-500" />
          <p className="font-medium">Export All Data</p>
        </CardContent>
      </Card>
      <Card className="cursor-pointer hover:bg-muted/50">
        <CardContent className="p-4 text-center">
          <GitMerge className="h-8 w-8 mx-auto mb-2 text-purple-500" />
          <p className="font-medium">Merge Duplicates</p>
        </CardContent>
      </Card>
      <Card className="cursor-pointer hover:bg-muted/50">
        <CardContent className="p-4 text-center">
          <Trash2 className="h-8 w-8 mx-auto mb-2 text-red-500" />
          <p className="font-medium">Mass Delete</p>
        </CardContent>
      </Card>
    </div>
  </div>
);

const ScheduledTasksTab: React.FC = () => (
  <div className="space-y-6">
    <div className="flex justify-between items-center">
      <h3 className="text-lg font-semibold">Scheduled Tasks</h3>
      <Button>
        <Calendar className="h-4 w-4 mr-2" />
        Create Task
      </Button>
    </div>

    <Card>
      <CardContent className="p-0">
        <div className="divide-y">
          {mockScheduledTasks.map((task) => (
            <div key={task.id} className="p-4 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div
                  className={`h-10 w-10 rounded-full flex items-center justify-center ${
                    task.isActive ? 'bg-green-100' : 'bg-gray-100'
                  }`}
                >
                  <Clock className={`h-5 w-5 ${task.isActive ? 'text-green-600' : 'text-gray-400'}`} />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="font-medium">{task.name}</h4>
                    <Badge variant="outline">
                      {task.scheduleType === 'cron' ? task.cronExpression : 'Interval'}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">{task.description}</p>
                </div>
              </div>
              <div className="flex items-center gap-6">
                <div className="text-right">
                  <p className="text-sm text-muted-foreground">Last Run</p>
                  <p className="text-sm font-medium flex items-center gap-1">
                    {task.lastRunStatus === 'completed' ? (
                      <CheckCircle className="h-3 w-3 text-green-500" />
                    ) : (
                      <XCircle className="h-3 w-3 text-red-500" />
                    )}
                    {new Date(task.lastRunAt!).toLocaleString()}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-muted-foreground">Next Run</p>
                  <p className="text-sm font-medium">
                    {new Date(task.nextRunAt!).toLocaleString()}
                  </p>
                </div>
                <Switch checked={task.isActive} />
                <Button variant="ghost" size="sm">
                  <Play className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  </div>
);

const FeatureFlagsTab: React.FC = () => {
  const [flags, setFlags] = useState(mockFeatureFlags);

  const toggleFlag = (flagId: string) => {
    setFlags(flags.map(f => 
      f.id === flagId ? { ...f, isEnabled: !f.isEnabled } : f
    ));
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Feature Flags</h3>
        <Button>
          <Flag className="h-4 w-4 mr-2" />
          Create Flag
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          <div className="divide-y">
            {flags.map((flag) => (
              <div key={flag.id} className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div
                    className={`h-10 w-10 rounded-full flex items-center justify-center ${
                      flag.isEnabled ? 'bg-green-100' : 'bg-gray-100'
                    }`}
                  >
                    <Flag className={`h-5 w-5 ${flag.isEnabled ? 'text-green-600' : 'text-gray-400'}`} />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium font-mono">{flag.name}</h4>
                      <Badge variant="outline" className="capitalize">
                        {flag.targetType}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{flag.description}</p>
                  </div>
                </div>
                <div className="flex items-center gap-6">
                  {flag.targetType === 'percentage' && (
                    <div className="text-right">
                      <p className="text-sm text-muted-foreground">Rollout</p>
                      <p className="text-sm font-medium">{flag.rolloutPercentage}%</p>
                    </div>
                  )}
                  <Switch
                    checked={flag.isEnabled}
                    onCheckedChange={() => toggleFlag(flag.id)}
                  />
                  <Button variant="ghost" size="sm">
                    <Settings className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

const AuditLogTab: React.FC = () => (
  <div className="space-y-6">
    <div className="flex justify-between items-center">
      <h3 className="text-lg font-semibold">Audit Log</h3>
      <div className="flex gap-2">
        <Button variant="outline">
          <Download className="h-4 w-4 mr-2" />
          Export Logs
        </Button>
      </div>
    </div>

    <Card>
      <CardContent className="p-0">
        <div className="divide-y">
          {[
            { action: 'Updated system configuration', user: 'admin@company.com', category: 'settings', time: '5 min ago' },
            { action: 'Created feature flag: new_dashboard', user: 'dev@company.com', category: 'feature_flags', time: '1 hour ago' },
            { action: 'Started bulk import: contacts', user: 'ops@company.com', category: 'bulk_operations', time: '2 hours ago' },
            { action: 'Acknowledged alert: Disk Usage Warning', user: 'admin@company.com', category: 'alerts', time: '3 hours ago' },
            { action: 'Modified user permissions', user: 'admin@company.com', category: 'security', time: '4 hours ago' },
          ].map((log, i) => (
            <div key={i} className="p-4 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="h-10 w-10 rounded-full bg-muted flex items-center justify-center">
                  <FileText className="h-5 w-5 text-muted-foreground" />
                </div>
                <div>
                  <p className="font-medium">{log.action}</p>
                  <p className="text-sm text-muted-foreground">
                    by {log.user}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <Badge variant="outline">{log.category}</Badge>
                <span className="text-sm text-muted-foreground">{log.time}</span>
                <Button variant="ghost" size="sm">
                  <Eye className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  </div>
);

// Main Component
export default function AdminControlCenter() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Shield className="h-8 w-8 text-blue-600" />
            Admin Control Center
          </h1>
          <p className="text-muted-foreground mt-1">
            System administration, monitoring, and configuration
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Bell className="h-4 w-4 mr-2" />
            Notifications
          </Button>
          <Button variant="outline">
            <Settings className="h-4 w-4 mr-2" />
            Settings
          </Button>
        </div>
      </div>

      <Tabs defaultValue="health">
        <TabsList>
          <TabsTrigger value="health" className="flex items-center gap-2">
            <Activity className="h-4 w-4" />
            System Health
          </TabsTrigger>
          <TabsTrigger value="operations" className="flex items-center gap-2">
            <RefreshCw className="h-4 w-4" />
            Bulk Operations
          </TabsTrigger>
          <TabsTrigger value="tasks" className="flex items-center gap-2">
            <Clock className="h-4 w-4" />
            Scheduled Tasks
          </TabsTrigger>
          <TabsTrigger value="flags" className="flex items-center gap-2">
            <Flag className="h-4 w-4" />
            Feature Flags
          </TabsTrigger>
          <TabsTrigger value="audit" className="flex items-center gap-2">
            <FileText className="h-4 w-4" />
            Audit Log
          </TabsTrigger>
        </TabsList>

        <TabsContent value="health" className="mt-4">
          <SystemHealthTab />
        </TabsContent>

        <TabsContent value="operations" className="mt-4">
          <BulkOperationsTab />
        </TabsContent>

        <TabsContent value="tasks" className="mt-4">
          <ScheduledTasksTab />
        </TabsContent>

        <TabsContent value="flags" className="mt-4">
          <FeatureFlagsTab />
        </TabsContent>

        <TabsContent value="audit" className="mt-4">
          <AuditLogTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}

