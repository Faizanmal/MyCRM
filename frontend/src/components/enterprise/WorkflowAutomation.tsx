/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { 
  Workflow, 
  Play, 
  Pause, 
  Settings, 
  Plus,
  Clock,
  CheckCircle,
  AlertCircle,
  Zap,
  Mail,
  Phone,
  Calendar,
  Users,
  Target,
  BarChart3
} from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { enterpriseAPI } from '@/lib/enterprise-api';

interface WorkflowAction {
  type: string;
  parameters: { [key: string]: any };
  delay?: number;
}

interface WorkflowData {
  name: string;
  description: string;
  trigger_type: string;
  trigger_conditions: { [key: string]: any };
  actions: WorkflowAction[];
  status: string;
}

const WorkflowAutomation = () => {
  const [selectedWorkflow, setSelectedWorkflow] = useState<any>(null);
  const [isCreating, setIsCreating] = useState(false);
  const queryClient = useQueryClient();

  const { data: workflows, isLoading } = useQuery({
    queryKey: ['workflows'],
    queryFn: enterpriseAPI.core.getWorkflows,
  });

  const { data: executions } = useQuery({
    queryKey: ['workflow-executions'],
    queryFn: () => enterpriseAPI.core.getWorkflows(), // This would be a separate endpoint
  });

  const executeWorkflow = useMutation({
    mutationFn: ({ id, triggerData }: { id: string; triggerData?: any }) =>
      enterpriseAPI.core.executeWorkflow(id, triggerData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflow-executions'] });
    },
  });

  const createWorkflow = useMutation({
    mutationFn: (data: WorkflowData) => enterpriseAPI.core.createWorkflow(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflows'] });
      setIsCreating(false);
    },
  });

  const getActionIcon = (actionType: string) => {
    const icons: { [key: string]: React.ReactNode } = {
      email: <Mail className="h-4 w-4" />,
      sms: <Phone className="h-4 w-4" />,
      task: <CheckCircle className="h-4 w-4" />,
      meeting: <Calendar className="h-4 w-4" />,
      assignment: <Users className="h-4 w-4" />,
      notification: <AlertCircle className="h-4 w-4" />,
    };
    return icons[actionType] || <Zap className="h-4 w-4" />;
  };

  const getStatusColor = (status: string) => {
    const colors: { [key: string]: string } = {
      active: 'text-green-600 bg-green-100',
      inactive: 'text-gray-600 bg-gray-100',
      draft: 'text-yellow-600 bg-yellow-100',
    };
    return colors[status] || 'text-gray-600 bg-gray-100';
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-48 bg-gray-200 rounded"></div>
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
          <h1 className="text-3xl font-bold tracking-tight">Workflow Automation</h1>
          <p className="text-muted-foreground">
            Automate repetitive tasks and streamline your business processes
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Dialog open={isCreating} onOpenChange={setIsCreating}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Create Workflow
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <WorkflowCreator onSubmit={createWorkflow.mutate} isLoading={createWorkflow.isPending} />
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <Tabs defaultValue="workflows" className="space-y-6">
        <TabsList>
          <TabsTrigger value="workflows">Workflows</TabsTrigger>
          <TabsTrigger value="executions">Execution History</TabsTrigger>
          <TabsTrigger value="templates">Templates</TabsTrigger>
        </TabsList>

        <TabsContent value="workflows" className="space-y-6">
          <WorkflowsList 
            workflows={workflows?.results || []}
            onSelect={setSelectedWorkflow}
            onExecute={(id, data) => executeWorkflow.mutate({ id, triggerData: data })}
          />
        </TabsContent>

        <TabsContent value="executions" className="space-y-6">
          <ExecutionHistory executions={executions?.results || []} />
        </TabsContent>

        <TabsContent value="templates" className="space-y-6">
          <WorkflowTemplates onUseTemplate={(template) => setIsCreating(true)} />
        </TabsContent>
      </Tabs>

      {selectedWorkflow && (
        <WorkflowDetails 
          workflow={selectedWorkflow} 
          onClose={() => setSelectedWorkflow(null)}
        />
      )}
    </div>
  );
};

const WorkflowsList = ({ 
  workflows, 
  onSelect, 
  onExecute 
}: { 
  workflows: any[];
  onSelect: (workflow: any) => void;
  onExecute: (id: string, data?: any) => void;
}) => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    {workflows.map((workflow) => (
      <Card key={workflow.id} className="cursor-pointer hover:shadow-md transition-shadow">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Workflow className="h-5 w-5" />
              <CardTitle className="text-lg">{workflow.name}</CardTitle>
            </div>
            <Badge className={getStatusColor(workflow.status)}>
              {workflow.status}
            </Badge>
          </div>
          <CardDescription className="line-clamp-2">
            {workflow.description}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Trigger:</span>
              <span className="capitalize">{workflow.trigger_type.replace('_', ' ')}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Actions:</span>
              <span>{workflow.actions?.length || 0}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Executions:</span>
              <span>{workflow.execution_count || 0}</span>
            </div>
            
            <div className="flex space-x-2 pt-2">
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => onSelect(workflow)}
                className="flex-1"
              >
                <Settings className="h-3 w-3 mr-1" />
                Details
              </Button>
              {workflow.status === 'active' && (
                <Button 
                  size="sm" 
                  onClick={() => onExecute(workflow.id)}
                  className="flex-1"
                >
                  <Play className="h-3 w-3 mr-1" />
                  Execute
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    ))}
  </div>
);

const WorkflowCreator = ({ 
  onSubmit, 
  isLoading 
}: { 
  onSubmit: (data: WorkflowData) => void;
  isLoading: boolean;
}) => {
  const [formData, setFormData] = useState<WorkflowData>({
    name: '',
    description: '',
    trigger_type: 'record_created',
    trigger_conditions: {},
    actions: [],
    status: 'draft'
  });

  const [currentAction, setCurrentAction] = useState<WorkflowAction>({
    type: 'email',
    parameters: {}
  });

  const addAction = () => {
    setFormData(prev => ({
      ...prev,
      actions: [...prev.actions, currentAction]
    }));
    setCurrentAction({ type: 'email', parameters: {} });
  };

  const removeAction = (index: number) => {
    setFormData(prev => ({
      ...prev,
      actions: prev.actions.filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div>
      <DialogHeader>
        <DialogTitle>Create New Workflow</DialogTitle>
        <DialogDescription>
          Set up automated processes to streamline your business operations
        </DialogDescription>
      </DialogHeader>
      
      <form onSubmit={handleSubmit} className="space-y-6 mt-6">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="name">Workflow Name</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              placeholder="e.g., Welcome New Customers"
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="trigger">Trigger Type</Label>
            <Select 
              value={formData.trigger_type}
              onValueChange={(value) => setFormData(prev => ({ ...prev, trigger_type: value }))}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="record_created">Record Created</SelectItem>
                <SelectItem value="record_updated">Record Updated</SelectItem>
                <SelectItem value="field_changed">Field Changed</SelectItem>
                <SelectItem value="time_based">Time Based</SelectItem>
                <SelectItem value="email_received">Email Received</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="description">Description</Label>
          <Textarea
            id="description"
            value={formData.description}
            onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
            placeholder="Describe what this workflow does..."
            rows={3}
          />
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <Label>Actions</Label>
            <span className="text-sm text-muted-foreground">
              {formData.actions.length} action(s) configured
            </span>
          </div>
          
          {formData.actions.map((action, index) => (
            <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
              <div className="flex items-center space-x-2">
                {getActionIcon(action.type)}
                <span className="font-medium capitalize">{action.type}</span>
                {action.delay && (
                  <Badge variant="outline">
                    <Clock className="h-3 w-3 mr-1" />
                    {action.delay}min delay
                  </Badge>
                )}
              </div>
              <Button 
                variant="destructive" 
                size="sm"
                onClick={() => removeAction(index)}
              >
                Remove
              </Button>
            </div>
          ))}

          <div className="p-4 border-2 border-dashed rounded-lg space-y-4">
            <h4 className="font-medium">Add New Action</h4>
            <div className="grid grid-cols-2 gap-4">
              <Select 
                value={currentAction.type}
                onValueChange={(value) => setCurrentAction(prev => ({ ...prev, type: value }))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="email">Send Email</SelectItem>
                  <SelectItem value="sms">Send SMS</SelectItem>
                  <SelectItem value="task">Create Task</SelectItem>
                  <SelectItem value="meeting">Schedule Meeting</SelectItem>
                  <SelectItem value="assignment">Assign Record</SelectItem>
                  <SelectItem value="notification">Send Notification</SelectItem>
                </SelectContent>
              </Select>
              <Input
                placeholder="Delay (minutes)"
                type="number"
                value={currentAction.delay || ''}
                onChange={(e) => setCurrentAction(prev => ({ 
                  ...prev, 
                  delay: e.target.value ? parseInt(e.target.value) : undefined 
                }))}
              />
            </div>
            <Button type="button" onClick={addAction} variant="outline" className="w-full">
              <Plus className="h-4 w-4 mr-2" />
              Add Action
            </Button>
          </div>
        </div>

        <div className="flex justify-end space-x-2 pt-4">
          <Button type="button" variant="outline">Cancel</Button>
          <Button type="submit" disabled={isLoading}>
            {isLoading ? 'Creating...' : 'Create Workflow'}
          </Button>
        </div>
      </form>
    </div>
  );
};

const ExecutionHistory = ({ executions }: { executions: any[] }) => (
  <div className="space-y-4">
    {executions.length === 0 ? (
      <Card>
        <CardContent className="py-8 text-center">
          <BarChart3 className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium mb-2">No Executions Yet</h3>
          <p className="text-muted-foreground">
            Workflow executions will appear here once your workflows start running.
          </p>
        </CardContent>
      </Card>
    ) : (
      executions.map((execution) => (
        <Card key={execution.id}>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">{execution.workflow_name}</CardTitle>
              <Badge className={getStatusColor(execution.status)}>
                {execution.status}
              </Badge>
            </div>
            <CardDescription>
              Started {new Date(execution.started_at).toLocaleString()}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span>Progress:</span>
                <span>{execution.steps_completed}/{execution.total_steps} steps</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full" 
                  style={{ width: `${execution.progress_percentage || 0}%` }}
                ></div>
              </div>
              {execution.duration_minutes && (
                <div className="flex justify-between text-sm">
                  <span>Duration:</span>
                  <span>{execution.duration_minutes} minutes</span>
                </div>
              )}
              {execution.error_message && (
                <div className="p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                  {execution.error_message}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      ))
    )}
  </div>
);

const WorkflowTemplates = ({ onUseTemplate }: { onUseTemplate: (template: any) => void }) => {
  const templates = [
    {
      name: "Lead Nurturing Sequence",
      description: "Automatically nurture new leads with a series of emails",
      trigger: "Lead Created",
      actions: ["Send welcome email", "Schedule follow-up", "Assign to sales rep"]
    },
    {
      name: "Customer Onboarding",
      description: "Guide new customers through the onboarding process",
      trigger: "Opportunity Won",
      actions: ["Send welcome package", "Schedule kickoff call", "Create onboarding tasks"]
    },
    {
      name: "Support Ticket Escalation",
      description: "Escalate overdue support tickets automatically",
      trigger: "Time Based",
      actions: ["Check ticket age", "Notify manager", "Update priority"]
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {templates.map((template, index) => (
        <Card key={index}>
          <CardHeader>
            <CardTitle className="text-lg">{template.name}</CardTitle>
            <CardDescription>{template.description}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Trigger:</span>
                <span>{template.trigger}</span>
              </div>
              <div className="text-sm">
                <span className="text-muted-foreground">Actions:</span>
                <ul className="mt-1 space-y-1">
                  {template.actions.map((action, i) => (
                    <li key={i} className="flex items-center space-x-2">
                      <CheckCircle className="h-3 w-3 text-green-600" />
                      <span>{action}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <Button 
                className="w-full mt-4" 
                variant="outline"
                onClick={() => onUseTemplate(template)}
              >
                Use Template
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

const WorkflowDetails = ({ 
  workflow, 
  onClose 
}: { 
  workflow: any;
  onClose: () => void;
}) => (
  <Dialog open={!!workflow} onOpenChange={onClose}>
    <DialogContent className="max-w-4xl">
      <DialogHeader>
        <DialogTitle>{workflow.name}</DialogTitle>
        <DialogDescription>{workflow.description}</DialogDescription>
      </DialogHeader>
      
      <div className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label>Status</Label>
            <div className="mt-1">
              <Badge className={getStatusColor(workflow.status)}>
                {workflow.status}
              </Badge>
            </div>
          </div>
          <div>
            <Label>Trigger Type</Label>
            <div className="mt-1 capitalize">
              {workflow.trigger_type.replace('_', ' ')}
            </div>
          </div>
        </div>

        <div>
          <Label>Actions ({workflow.actions?.length || 0})</Label>
          <div className="mt-2 space-y-2">
            {workflow.actions?.map((action: any, index: number) => (
              <div key={index} className="flex items-center space-x-3 p-3 border rounded-lg">
                {getActionIcon(action.type)}
                <span className="font-medium capitalize">{action.type}</span>
                {action.delay && (
                  <Badge variant="outline">
                    <Clock className="h-3 w-3 mr-1" />
                    {action.delay}min delay
                  </Badge>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </DialogContent>
  </Dialog>
);

// Helper functions
function getActionIcon(actionType: string) {
  const icons: { [key: string]: React.ReactNode } = {
    email: <Mail className="h-4 w-4" />,
    sms: <Phone className="h-4 w-4" />,
    task: <CheckCircle className="h-4 w-4" />,
    meeting: <Calendar className="h-4 w-4" />,
    assignment: <Users className="h-4 w-4" />,
    notification: <AlertCircle className="h-4 w-4" />,
  };
  return icons[actionType] || <Zap className="h-4 w-4" />;
}

function getStatusColor(status: string) {
  const colors: { [key: string]: string } = {
    active: 'text-green-600 bg-green-100',
    inactive: 'text-gray-600 bg-gray-100',
    draft: 'text-yellow-600 bg-yellow-100',
    running: 'text-blue-600 bg-blue-100',
    completed: 'text-green-600 bg-green-100',
    failed: 'text-red-600 bg-red-100',
  };
  return colors[status] || 'text-gray-600 bg-gray-100';
}

export default WorkflowAutomation;