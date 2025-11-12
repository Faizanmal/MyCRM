'use client';

import { useState } from 'react';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
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
  Clock
} from 'lucide-react';

interface WorkflowData {
  id: string;
  name: string;
  description: string;
  trigger: string;
  status: 'active' | 'inactive' | 'draft';
  executions: number;
  successRate: number;
  lastRun?: string;
}

const mockWorkflows: WorkflowData[] = [
  {
    id: '1',
    name: 'Lead Follow-up Sequence',
    description: 'Automatically send follow-up emails to new leads',
    trigger: 'New Lead Created',
    status: 'active',
    executions: 142,
    successRate: 95,
    lastRun: '2025-11-10T10:30:00',
  },
  {
    id: '2',
    name: 'Opportunity Stage Update',
    description: 'Send notifications when opportunity stage changes',
    trigger: 'Opportunity Updated',
    status: 'active',
    executions: 87,
    successRate: 98,
    lastRun: '2025-11-10T09:15:00',
  },
  {
    id: '3',
    name: 'Task Assignment Automation',
    description: 'Auto-assign tasks based on team availability',
    trigger: 'Task Created',
    status: 'active',
    executions: 234,
    successRate: 92,
    lastRun: '2025-11-10T11:00:00',
  },
  {
    id: '4',
    name: 'Customer Onboarding',
    description: 'Welcome email series for new customers',
    trigger: 'Deal Closed Won',
    status: 'inactive',
    executions: 45,
    successRate: 89,
    lastRun: '2025-11-08T14:20:00',
  },
  {
    id: '5',
    name: 'Lead Scoring Update',
    description: 'Recalculate lead scores based on activities',
    trigger: 'Activity Logged',
    status: 'draft',
    executions: 0,
    successRate: 0,
  },
];

export default function WorkflowsPage() {
  const [showBuilder, setShowBuilder] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowData | null>(null);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'inactive': return 'bg-gray-100 text-gray-800';
      case 'draft': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
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

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-4 lg:p-6 space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-2xl lg:text-3xl font-bold text-gray-900">Workflows</h1>
              <p className="text-gray-500 mt-1">Automate your business processes</p>
            </div>
            <Button
              size="sm"
              className="bg-blue-600 hover:bg-blue-700"
              onClick={() => setShowBuilder(true)}
            >
              <Plus className="w-4 h-4 mr-2" />
              Create Workflow
            </Button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Workflows</CardTitle>
                <Workflow className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{mockWorkflows.length}</div>
                <p className="text-xs text-muted-foreground">
                  {mockWorkflows.filter(w => w.status === 'active').length} active
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Executions</CardTitle>
                <Play className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {mockWorkflows.reduce((sum, w) => sum + w.executions, 0)}
                </div>
                <p className="text-xs text-muted-foreground">
                  Last 30 days
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
                <CheckCircle2 className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">
                  {Math.round(
                    mockWorkflows.reduce((sum, w) => sum + w.successRate * w.executions, 0) /
                    mockWorkflows.reduce((sum, w) => sum + w.executions, 0)
                  )}%
                </div>
                <p className="text-xs text-muted-foreground">
                  Average across all workflows
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Workflows</CardTitle>
                <Play className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {mockWorkflows.filter(w => w.status === 'active').length}
                </div>
                <p className="text-xs text-muted-foreground">
                  Running automation
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Workflows List */}
          <div className="space-y-4">
            {mockWorkflows.map((workflow) => (
              <Card key={workflow.id} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <CardTitle className="text-lg">{workflow.name}</CardTitle>
                        <Badge className={getStatusColor(workflow.status)}>
                          {getStatusIcon(workflow.status)}
                          <span className="ml-1">{workflow.status}</span>
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
                      <Button variant="outline" size="sm">
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div>
                      <p className="text-sm text-gray-500 mb-1">Trigger</p>
                      <p className="text-sm font-medium">{workflow.trigger}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500 mb-1">Executions</p>
                      <p className="text-sm font-medium">{workflow.executions}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500 mb-1">Success Rate</p>
                      <p className="text-sm font-medium text-green-600">
                        {workflow.successRate}%
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500 mb-1">Last Run</p>
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
                        <span className="text-sm text-gray-600">Running</span>
                      </div>
                      <Button variant="outline" size="sm">
                        <Pause className="w-4 h-4 mr-2" />
                        Pause
                      </Button>
                    </div>
                  )}

                  {workflow.status === 'inactive' && (
                    <div className="mt-4 pt-4 border-t flex items-center justify-between">
                      <span className="text-sm text-gray-500">This workflow is paused</span>
                      <Button variant="outline" size="sm">
                        <Play className="w-4 h-4 mr-2" />
                        Activate
                      </Button>
                    </div>
                  )}

                  {workflow.status === 'draft' && (
                    <div className="mt-4 pt-4 border-t flex items-center justify-between">
                      <span className="text-sm text-gray-500">This workflow is in draft mode</span>
                      <Button variant="outline" size="sm">
                        <Play className="w-4 h-4 mr-2" />
                        Publish
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
