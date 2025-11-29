'use client';

import { useState, useEffect, useCallback } from 'react';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import WorkflowBuilder from '@/components/enterprise/WorkflowBuilder';
import {
  Workflow,
  Play,
  Pause,
  Edit,
  Trash2,
  Copy,
  Plus,
  CheckCircle2,
  Clock,
  RefreshCw,
  AlertCircle
} from 'lucide-react';
import { leadQualificationAPI } from '@/lib/api';
import { toast } from 'sonner';

interface WorkflowData {
  id: string;
  name: string;
  description: string;
  trigger?: string;
  status: 'active' | 'inactive' | 'draft';
  is_active?: boolean;
  executions?: number;
  execution_count?: number;
  success_rate?: number;
  successRate?: number;
  last_run?: string;
  lastRun?: string;
  created_at: string;
  updated_at: string;
}

export default function WorkflowsPage() {
  const [showBuilder, setShowBuilder] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowData | null>(null);
  const [workflows, setWorkflows] = useState<WorkflowData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchWorkflows = useCallback(async (showRefreshing = false) => {
    try {
      if (showRefreshing) setIsRefreshing(true);
      setError(null);

      const response = await leadQualificationAPI.getWorkflows();
      const workflowsList: WorkflowData[] = response.data?.results || response.data || [];
      
      // Normalize workflow data
      const normalizedWorkflows = workflowsList.map((w: WorkflowData) => ({
        ...w,
        status: w.status || (w.is_active ? 'active' : 'inactive'),
        executions: w.executions || w.execution_count || 0,
        successRate: w.successRate || w.success_rate || 0,
        lastRun: w.lastRun || w.last_run,
      }));
      
      setWorkflows(normalizedWorkflows);
    } catch (err) {
      console.error('Error fetching workflows:', err);
      setError('Failed to load workflows');
      toast.error('Failed to load workflows');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchWorkflows();
  }, [fetchWorkflows]);

  const handleRefresh = () => {
    fetchWorkflows(true);
  };

  const handleActivate = async (workflow: WorkflowData) => {
    try {
      await leadQualificationAPI.activateWorkflow(workflow.id);
      toast.success('Workflow activated');
      fetchWorkflows();
    } catch (err) {
      console.error('Error activating workflow:', err);
      toast.error('Failed to activate workflow');
    }
  };

  const handleDeactivate = async (workflow: WorkflowData) => {
    try {
      await leadQualificationAPI.deactivateWorkflow(workflow.id);
      toast.success('Workflow deactivated');
      fetchWorkflows();
    } catch (err) {
      console.error('Error deactivating workflow:', err);
      toast.error('Failed to deactivate workflow');
    }
  };

  const handleDelete = async (workflow: WorkflowData) => {
    try {
      await leadQualificationAPI.deleteWorkflow(workflow.id);
      toast.success('Workflow deleted');
      fetchWorkflows();
    } catch (err) {
      console.error('Error deleting workflow:', err);
      toast.error('Failed to delete workflow');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300';
      case 'inactive': return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300';
      case 'draft': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle2 className="w-4 h-4 text-green-600" />;
      case 'inactive': return <Pause className="w-4 h-4 text-gray-600" />;
      case 'draft': return <Clock className="w-4 h-4 text-yellow-600" />;
      default: return null;
    }
  };

  const totalExecutions = workflows.reduce((sum, w) => sum + (w.executions || 0), 0);
  const activeWorkflows = workflows.filter(w => w.status === 'active').length;
  const avgSuccessRate = workflows.length > 0 
    ? Math.round(
        workflows.reduce((sum, w) => sum + (w.successRate || 0) * (w.executions || 0), 0) /
        Math.max(totalExecutions, 1)
      )
    : 0;

  if (showBuilder) {
    return (
      <ProtectedRoute>
        <MainLayout>
          <div className="p-4 lg:p-6">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-2xl font-bold">
                {selectedWorkflow ? `Edit: ${selectedWorkflow.name}` : 'Create New Workflow'}
              </h2>
              <Button
                variant="outline"
                onClick={() => {
                  setShowBuilder(false);
                  setSelectedWorkflow(null);
                }}
              >
                Back to Workflows
              </Button>
            </div>
            <WorkflowBuilder />
          </div>
        </MainLayout>
      </ProtectedRoute>
    );
  }

  if (error && workflows.length === 0) {
    return (
      <ProtectedRoute>
        <MainLayout>
          <div className="p-6">
            <Card className="p-8 text-center">
              <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <h2 className="text-xl font-semibold mb-2">Failed to Load Workflows</h2>
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
              <h1 className="text-2xl lg:text-3xl font-bold">Workflows</h1>
              <p className="text-muted-foreground mt-1">Automate your business processes</p>
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
                Create Workflow
              </Button>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Workflows</CardTitle>
                <Workflow className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <Skeleton className="h-8 w-12" />
                ) : (
                  <div className="text-2xl font-bold">{workflows.length}</div>
                )}
                <p className="text-xs text-muted-foreground">
                  {activeWorkflows} active
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Executions</CardTitle>
                <Play className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <Skeleton className="h-8 w-16" />
                ) : (
                  <div className="text-2xl font-bold">{totalExecutions}</div>
                )}
                <p className="text-xs text-muted-foreground">All time</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
                <CheckCircle2 className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <Skeleton className="h-8 w-12" />
                ) : (
                  <div className="text-2xl font-bold text-green-600">{avgSuccessRate}%</div>
                )}
                <p className="text-xs text-muted-foreground">Average across all workflows</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Workflows</CardTitle>
                <Play className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <Skeleton className="h-8 w-8" />
                ) : (
                  <div className="text-2xl font-bold">{activeWorkflows}</div>
                )}
                <p className="text-xs text-muted-foreground">Running automation</p>
              </CardContent>
            </Card>
          </div>

          {/* Workflows List */}
          {isLoading ? (
            <div className="space-y-4">
              {[...Array(3)].map((_, i) => (
                <Card key={i}>
                  <CardHeader>
                    <Skeleton className="h-6 w-1/2" />
                    <Skeleton className="h-4 w-3/4" />
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-4 gap-4">
                      {[...Array(4)].map((_, j) => (
                        <Skeleton key={j} className="h-12" />
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : workflows.length > 0 ? (
            <div className="space-y-4">
              {workflows.map((workflow) => (
                <Card key={workflow.id} className="hover:shadow-md transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <CardTitle className="text-lg">{workflow.name}</CardTitle>
                          <Badge className={getStatusColor(workflow.status)}>
                            {getStatusIcon(workflow.status)}
                            <span className="ml-1 capitalize">{workflow.status}</span>
                          </Badge>
                        </div>
                        <CardDescription>{workflow.description}</CardDescription>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setSelectedWorkflow(workflow);
                            setShowBuilder(true);
                          }}
                        >
                          <Edit className="w-4 h-4 mr-2" />
                          Edit
                        </Button>
                        <Button variant="outline" size="sm">
                          <Copy className="w-4 h-4 mr-2" />
                          Duplicate
                        </Button>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleDelete(workflow)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">Trigger</p>
                        <p className="text-sm font-medium">{workflow.trigger || 'Manual'}</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">Executions</p>
                        <p className="text-sm font-medium">{workflow.executions || 0}</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">Success Rate</p>
                        <p className="text-sm font-medium text-green-600">
                          {workflow.successRate || 0}%
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">Last Run</p>
                        <p className="text-sm font-medium">
                          {workflow.lastRun
                            ? new Date(workflow.lastRun).toLocaleString()
                            : 'Never'}
                        </p>
                      </div>
                    </div>

                    {workflow.status === 'active' && (
                      <div className="mt-4 pt-4 border-t flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                          <span className="text-sm text-muted-foreground">Running</span>
                        </div>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleDeactivate(workflow)}
                        >
                          <Pause className="w-4 h-4 mr-2" />
                          Pause
                        </Button>
                      </div>
                    )}

                    {workflow.status === 'inactive' && (
                      <div className="mt-4 pt-4 border-t flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">This workflow is paused</span>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleActivate(workflow)}
                        >
                          <Play className="w-4 h-4 mr-2" />
                          Activate
                        </Button>
                      </div>
                    )}

                    {workflow.status === 'draft' && (
                      <div className="mt-4 pt-4 border-t flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">This workflow is in draft mode</span>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleActivate(workflow)}
                        >
                          <Play className="w-4 h-4 mr-2" />
                          Publish
                        </Button>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="p-12 text-center">
                <Workflow className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No workflows found</h3>
                <p className="text-muted-foreground mb-4">
                  Get started by creating your first workflow
                </p>
                <Button onClick={() => setShowBuilder(true)}>
                  <Plus className="w-4 h-4 mr-2" />
                  Create Workflow
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
