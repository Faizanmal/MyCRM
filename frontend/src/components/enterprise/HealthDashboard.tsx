/**
 * Enterprise Health Dashboard Component
 * ======================================
 * 
 * Real-time system health monitoring dashboard
 */

'use client';

import React, { useEffect, useState } from 'react';
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Database,
  HardDrive,
  MemoryStick,
  RefreshCw,
  Server,
  XCircle,
} from 'lucide-react';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

// =============================================================================
// Types
// =============================================================================

interface HealthCheck {
  name: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  latencyMs: number;
  message?: string;
  details?: Record<string, unknown>;
  timestamp: string;
}

interface AggregatedHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  totalLatencyMs: number;
  checks: HealthCheck[];
  timestamp: string;
  hostname?: string;
}

// =============================================================================
// Health Dashboard Component
// =============================================================================

export function HealthDashboard() {
  const [health, setHealth] = useState<AggregatedHealth | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchHealth = async (fresh = false) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const url = fresh 
        ? '/api/health?fresh=true'
        : '/api/health';
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`);
      }
      
      const data = await response.json();
      setHealth(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch health status');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
    
    if (autoRefresh) {
      const interval = setInterval(() => fetchHealth(), 30000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'degraded':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case 'unhealthy':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Activity className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
      healthy: 'default',
      degraded: 'secondary',
      unhealthy: 'destructive',
    };
    
    return (
      <Badge variant={variants[status] || 'outline'} className="capitalize">
        {status}
      </Badge>
    );
  };

  if (error) {
    return (
      <Card className="border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-red-700 dark:text-red-400">
            <XCircle className="h-5 w-5" />
            Health Check Failed
          </CardTitle>
          <CardDescription className="text-red-600 dark:text-red-400">
            {error}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={() => fetchHealth(true)} variant="outline">
            <RefreshCw className="mr-2 h-4 w-4" />
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">System Health</h2>
          <p className="text-muted-foreground">
            Real-time monitoring of system components
          </p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="auto-refresh"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded border-gray-300"
            />
            <label htmlFor="auto-refresh" className="text-sm text-muted-foreground">
              Auto-refresh (30s)
            </label>
          </div>
          <Button
            onClick={() => fetchHealth(true)}
            disabled={isLoading}
            variant="outline"
            size="sm"
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Overall Status */}
      {health && (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                {getStatusIcon(health.status)}
                <div>
                  <h3 className="font-semibold">Overall System Status</h3>
                  <p className="text-sm text-muted-foreground">
                    {health.hostname && `Host: ${health.hostname} · `}
                    Last checked: {new Date(health.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                {getStatusBadge(health.status)}
                <div className="text-right">
                  <p className="text-sm font-medium">
                    {health.totalLatencyMs.toFixed(0)}ms
                  </p>
                  <p className="text-xs text-muted-foreground">Total Latency</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Component Health */}
      <Tabs defaultValue="all" className="space-y-4">
        <TabsList>
          <TabsTrigger value="all">All Components</TabsTrigger>
          <TabsTrigger value="critical">Critical</TabsTrigger>
          <TabsTrigger value="issues">Issues</TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {health?.checks.map((check) => (
              <HealthCheckCard key={check.name} check={check} />
            ))}
          </div>
        </TabsContent>

        <TabsContent value="critical" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {health?.checks
              .filter((c) => c.name.includes('database') || c.name.includes('redis'))
              .map((check) => (
                <HealthCheckCard key={check.name} check={check} />
              ))}
          </div>
        </TabsContent>

        <TabsContent value="issues" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {health?.checks
              .filter((c) => c.status !== 'healthy')
              .map((check) => (
                <HealthCheckCard key={check.name} check={check} />
              ))}
            {health?.checks.every((c) => c.status === 'healthy') && (
              <Card className="col-span-full">
                <CardContent className="pt-6 text-center">
                  <CheckCircle2 className="mx-auto h-12 w-12 text-green-500" />
                  <h3 className="mt-4 font-semibold">All Systems Operational</h3>
                  <p className="text-sm text-muted-foreground">
                    No issues detected
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>
      </Tabs>

      {/* System Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          title="Response Time"
          value={`${health?.totalLatencyMs.toFixed(0) || '—'}ms`}
          description="Average health check latency"
          icon={<Clock className="h-4 w-4" />}
        />
        <MetricCard
          title="Components"
          value={`${health?.checks.length || 0}`}
          description="Total monitored components"
          icon={<Server className="h-4 w-4" />}
        />
        <MetricCard
          title="Healthy"
          value={`${health?.checks.filter((c) => c.status === 'healthy').length || 0}`}
          description="Components operating normally"
          icon={<CheckCircle2 className="h-4 w-4 text-green-500" />}
        />
        <MetricCard
          title="Issues"
          value={`${health?.checks.filter((c) => c.status !== 'healthy').length || 0}`}
          description="Components with issues"
          icon={<AlertTriangle className="h-4 w-4 text-yellow-500" />}
        />
      </div>
    </div>
  );
}

// =============================================================================
// Health Check Card
// =============================================================================

function HealthCheckCard({ check }: { check: HealthCheck }) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'border-green-200 bg-green-50 dark:border-green-900 dark:bg-green-950';
      case 'degraded':
        return 'border-yellow-200 bg-yellow-50 dark:border-yellow-900 dark:bg-yellow-950';
      case 'unhealthy':
        return 'border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950';
      default:
        return '';
    }
  };

  const getComponentIcon = (name: string) => {
    if (name.includes('database') || name.includes('postgres')) {
      return <Database className="h-5 w-5" />;
    }
    if (name.includes('redis') || name.includes('cache')) {
      return <Server className="h-5 w-5" />;
    }
    if (name.includes('celery') || name.includes('worker')) {
      return <Activity className="h-5 w-5" />;
    }
    if (name.includes('disk') || name.includes('storage')) {
      return <HardDrive className="h-5 w-5" />;
    }
    if (name.includes('memory') || name.includes('ram')) {
      return <MemoryStick className="h-5 w-5" />;
    }
    return <Server className="h-5 w-5" />;
  };

  return (
    <Card className={getStatusColor(check.status)}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {getComponentIcon(check.name)}
            <CardTitle className="text-base capitalize">
              {check.name.replace(/_/g, ' ')}
            </CardTitle>
          </div>
          <Badge
            variant={
              check.status === 'healthy'
                ? 'default'
                : check.status === 'degraded'
                ? 'secondary'
                : 'destructive'
            }
            className="capitalize"
          >
            {check.status}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground mb-3">{check.message}</p>
        
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Latency</span>
          <span className="font-mono">{check.latencyMs.toFixed(2)}ms</span>
        </div>

        {check.details && Object.keys(check.details).length > 0 && (
          <div className="mt-3 pt-3 border-t space-y-2">
            {Object.entries(check.details).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground capitalize">
                  {key.replace(/_/g, ' ')}
                </span>
                <span className="font-mono">
                  {typeof value === 'number'
                    ? value.toLocaleString()
                    : String(value)}
                </span>
              </div>
            ))}
            
            {check.details.utilization_percent !== undefined && (
              <Progress
                value={check.details.utilization_percent as number}
                className="mt-2"
              />
            )}
            
            {check.details.used_percent !== undefined && (
              <Progress
                value={check.details.used_percent as number}
                className="mt-2"
              />
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// =============================================================================
// Metric Card
// =============================================================================

function MetricCard({
  title,
  value,
  description,
  icon,
}: {
  title: string;
  value: string;
  description: string;
  icon: React.ReactNode;
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {icon}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className="text-xs text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  );
}

export default HealthDashboard;

