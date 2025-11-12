/* eslint-disable @typescript-eslint/no-explicit-any */
'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Shield, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Database,
  Server,
  Mail,
  HardDrive,
  Zap,
  Activity
} from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { enterpriseAPI } from '@/lib/enterprise-api';

const SecurityDashboard = () => {
  const { data: securityData, isLoading: securityLoading } = useQuery({
    queryKey: ['security-dashboard'],
    queryFn: enterpriseAPI.core.getSecurityDashboard,
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const { data: healthData, isLoading: healthLoading } = useQuery({
    queryKey: ['system-health'],
    queryFn: enterpriseAPI.core.getHealthDashboard,
    refetchInterval: 60000, // Refresh every minute
  });

  const { data: auditSummary, isLoading: auditLoading } = useQuery({
    queryKey: ['audit-summary'],
    queryFn: enterpriseAPI.core.getSecuritySummary,
    refetchInterval: 300000, // Refresh every 5 minutes
  });

  const getHealthIcon = (component: string) => {
    const icons: { [key: string]: React.ReactNode } = {
      database: <Database className="h-4 w-4" />,
      cache: <Zap className="h-4 w-4" />,
      email: <Mail className="h-4 w-4" />,
      storage: <HardDrive className="h-4 w-4" />,
      api: <Server className="h-4 w-4" />,
      queue: <Activity className="h-4 w-4" />,
    };
    return icons[component] || <Server className="h-4 w-4" />;
  };

  const getStatusColor = (status: string) => {
    const colors: { [key: string]: string } = {
      healthy: 'text-green-600 bg-green-100',
      warning: 'text-yellow-600 bg-yellow-100',
      critical: 'text-orange-600 bg-orange-100',
      down: 'text-red-600 bg-red-100',
    };
    return colors[status] || 'text-gray-600 bg-gray-100';
  };

  const getRiskLevelColor = (level: string) => {
    const colors: { [key: string]: string } = {
      low: 'text-green-600 bg-green-100',
      medium: 'text-yellow-600 bg-yellow-100',
      high: 'text-orange-600 bg-orange-100',
      critical: 'text-red-600 bg-red-100',
    };
    return colors[level] || 'text-gray-600 bg-gray-100';
  };

  if (securityLoading || healthLoading || auditLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Security Dashboard</h1>
          <p className="text-muted-foreground">
            Monitor system security, health, and compliance status
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="outline" className="bg-green-50 text-green-700">
            <CheckCircle className="h-3 w-3 mr-1" />
            System Secure
          </Badge>
        </div>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="health">System Health</TabsTrigger>
          <TabsTrigger value="audit">Audit Logs</TabsTrigger>
          <TabsTrigger value="api-keys">API Keys</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Security Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Security Events Today
                </CardTitle>
                <Shield className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {securityData?.total_audit_logs || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  {securityData?.high_risk_events_today || 0} high risk
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Failed Logins
                </CardTitle>
                <AlertTriangle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {securityData?.failed_logins_today || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  Last 24 hours
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Active API Keys
                </CardTitle>
                <Database className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {securityData?.active_api_keys || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  External integrations
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  System Health
                </CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {Math.round(healthData?.overall_health_score || 0)}%
                </div>
                <p className="text-xs text-muted-foreground">
                  All components
                </p>
              </CardContent>
            </Card>
          </div>

          {/* System Health Overview */}
          <Card>
            <CardHeader>
              <CardTitle>System Health Overview</CardTitle>
              <CardDescription>
                Current status of all system components
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Overall Health Score</span>
                  <span className="text-sm text-muted-foreground">
                    {healthData?.healthy_components || 0}/{healthData?.total_components || 0} healthy
                  </span>
                </div>
                <Progress 
                  value={healthData?.overall_health_score || 0} 
                  className="w-full"
                />
                
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 pt-4">
                  {healthData?.components && Object.entries(healthData.components).map(([component, data]: [string, any]) => (
                    <div key={component} className="flex items-center space-x-2">
                      {getHealthIcon(component)}
                      <span className="text-sm font-medium capitalize">{component}</span>
                      <Badge 
                        variant="secondary" 
                        className={getStatusColor(data.status)}
                      >
                        {data.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="health" className="space-y-6">
          <SystemHealthDetails healthData={healthData} />
        </TabsContent>

        <TabsContent value="audit" className="space-y-6">
          <AuditLogsView auditSummary={auditSummary} />
        </TabsContent>

        <TabsContent value="api-keys" className="space-y-6">
          <APIKeysManagement />
        </TabsContent>
      </Tabs>
    </div>
  );
};

const SystemHealthDetails = ({ healthData }: { healthData: any }) => (
  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
    {healthData?.components && Object.entries(healthData.components).map(([component, data]: [string, any]) => (
      <Card key={component}>
        <CardHeader>
          <div className="flex items-center space-x-2">
            {getHealthIcon(component)}
            <CardTitle className="capitalize">{component}</CardTitle>
            <Badge 
              variant="secondary" 
              className={getStatusColor(data.status)}
            >
              {data.status}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {data.response_time && (
              <div className="flex justify-between">
                <span className="text-sm">Response Time:</span>
                <span className="text-sm font-medium">{data.response_time}ms</span>
              </div>
            )}
            {data.last_check && (
              <div className="flex justify-between">
                <span className="text-sm">Last Check:</span>
                <span className="text-sm font-medium">
                  {new Date(data.last_check).toLocaleTimeString()}
                </span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    ))}
  </div>
);

const AuditLogsView = ({ auditSummary }: { auditSummary: any }) => (
  <div className="space-y-6">
    <Card>
      <CardHeader>
        <CardTitle>Security Events Summary</CardTitle>
        <CardDescription>Today&apos;s security-related activities</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold">{auditSummary?.total_events_today || 0}</div>
            <div className="text-sm text-muted-foreground">Total Events</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">
              {auditSummary?.high_risk_events_today || 0}
            </div>
            <div className="text-sm text-muted-foreground">High Risk</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{auditSummary?.failed_logins_today || 0}</div>
            <div className="text-sm text-muted-foreground">Failed Logins</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{auditSummary?.unique_users_today || 0}</div>
            <div className="text-sm text-muted-foreground">Active Users</div>
          </div>
        </div>
      </CardContent>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle>Top Actions Today</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {auditSummary?.top_actions?.map((action: any, index: number) => (
            <div key={index} className="flex justify-between items-center">
              <span className="text-sm">{action.action}</span>
              <Badge variant="outline">{action.count}</Badge>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  </div>
);

const APIKeysManagement = () => {
  const { data: apiKeys, isLoading } = useQuery({
    queryKey: ['api-keys'],
    queryFn: enterpriseAPI.core.getAPIKeys,
  });

  if (isLoading) {
    return <div>Loading API keys...</div>;
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>API Keys</CardTitle>
          <CardDescription>Manage external integration API keys</CardDescription>
        </div>
        <Button>Create New Key</Button>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {apiKeys?.results?.map((key: any) => (
            <div key={key.id} className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <div className="font-medium">{key.name}</div>
                <div className="text-sm text-muted-foreground">
                  Created by {key.user_name} • Rate limit: {key.rate_limit}/hour
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Badge 
                  variant={key.status === 'active' ? 'default' : 'secondary'}
                >
                  {key.status}
                </Badge>
                <Button variant="destructive" size="sm">
                  Revoke
                </Button>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

// Helper function to get health icon (defined outside component to avoid recreation)
function getHealthIcon(component: string) {
  const icons: { [key: string]: React.ReactNode } = {
    database: <Database className="h-4 w-4" />,
    cache: <Zap className="h-4 w-4" />,
    email: <Mail className="h-4 w-4" />,
    storage: <HardDrive className="h-4 w-4" />,
    api: <Server className="h-4 w-4" />,
    queue: <Activity className="h-4 w-4" />,
  };
  return icons[component] || <Server className="h-4 w-4" />;
}

// Helper function to get status color
function getStatusColor(status: string) {
  const colors: { [key: string]: string } = {
    healthy: 'text-green-600 bg-green-100',
    warning: 'text-yellow-600 bg-yellow-100',
    critical: 'text-orange-600 bg-orange-100',
    down: 'text-red-600 bg-red-100',
  };
  return colors[status] || 'text-gray-600 bg-gray-100';
}

export default SecurityDashboard;