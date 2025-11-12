// Workflow Builder Component
/* eslint-disable @typescript-eslint/no-explicit-any */
'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  Workflow, Play, Pause, Plus, Trash2, Settings, Copy, 
  Mail, CheckSquare, Edit, Bell, Webhook, Clock, Zap 
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import axios from 'axios';

interface WorkflowAction {
  type: string;
  params: Record<string, any>;
}

interface WorkflowData {
  id?: string;
  name: string;
  description: string;
  trigger_type: string;
  trigger_conditions: any;
  actions: WorkflowAction[];
  status: 'active' | 'inactive' | 'draft';
}

const TRIGGER_TYPES = [
  { value: 'record_created', label: 'Record Created', icon: Plus },
  { value: 'record_updated', label: 'Record Updated', icon: Edit },
  { value: 'field_changed', label: 'Field Changed', icon: Edit },
  { value: 'time_based', label: 'Time Based', icon: Clock },
  { value: 'email_received', label: 'Email Received', icon: Mail },
];

const ACTION_TYPES = [
  { value: 'send_email', label: 'Send Email', icon: Mail, color: 'blue' },
  { value: 'create_task', label: 'Create Task', icon: CheckSquare, color: 'green' },
  { value: 'update_field', label: 'Update Field', icon: Edit, color: 'purple' },
  { value: 'send_notification', label: 'Send Notification', icon: Bell, color: 'yellow' },
  { value: 'webhook', label: 'Call Webhook', icon: Webhook, color: 'orange' },
  { value: 'wait', label: 'Wait/Delay', icon: Clock, color: 'gray' },
];

export default function WorkflowBuilder() {
  const [workflows, setWorkflows] = useState<WorkflowData[]>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowData | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const fetchWorkflows = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/core/workflows/');
      setWorkflows(response.data.results || response.data);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load workflows',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const createWorkflow = () => {
    setSelectedWorkflow({
      name: '',
      description: '',
      trigger_type: 'record_created',
      trigger_conditions: { rules: [] },
      actions: [],
      status: 'draft',
    });
    setIsCreating(true);
  };

  const saveWorkflow = async (workflow: WorkflowData) => {
    try {
      if (workflow.id) {
        await axios.put(`/api/core/workflows/${workflow.id}/`, workflow);
        toast({ title: 'Success', description: 'Workflow updated successfully' });
      } else {
        await axios.post('/api/core/workflows/', workflow);
        toast({ title: 'Success', description: 'Workflow created successfully' });
      }
      fetchWorkflows();
      setIsCreating(false);
      setSelectedWorkflow(null);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to save workflow',
        variant: 'destructive',
      });
    }
  };

  const toggleWorkflowStatus = async (workflowId: string, currentStatus: string) => {
    try {
      const newStatus = currentStatus === 'active' ? 'inactive' : 'active';
      await axios.patch(`/api/core/workflows/${workflowId}/`, { status: newStatus });
      toast({
        title: 'Success',
        description: `Workflow ${newStatus === 'active' ? 'activated' : 'deactivated'}`,
      });
      fetchWorkflows();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to update workflow status',
        variant: 'destructive',
      });
    }
  };

  const executeWorkflow = async (workflowId: string) => {
    try {
      await axios.post(`/api/core/workflows/${workflowId}/execute/`, {
        trigger_data: { manual_trigger: true },
      });
      toast({
        title: 'Success',
        description: 'Workflow execution started',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to execute workflow',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Workflow className="h-8 w-8" />
            Workflow Automation
          </h1>
          <p className="text-muted-foreground mt-1">Automate your business processes</p>
        </div>
        <Button onClick={createWorkflow}>
          <Plus className="h-4 w-4 mr-2" />
          Create Workflow
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Workflows List */}
        <div className="lg:col-span-1 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Workflows</CardTitle>
              <CardDescription>{workflows.length} total workflows</CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[600px]">
                <div className="space-y-2">
                  {workflows.map((workflow) => (
                    <Card
                      key={workflow.id}
                      className={`cursor-pointer hover:bg-accent ${
                        selectedWorkflow?.id === workflow.id ? 'border-primary' : ''
                      }`}
                      onClick={() => {
                        setSelectedWorkflow(workflow);
                        setIsCreating(false);
                      }}
                    >
                      <CardContent className="p-4">
                        <div className="space-y-2">
                          <div className="flex justify-between items-start">
                            <h3 className="font-semibold">{workflow.name}</h3>
                            <Badge
                              variant={
                                workflow.status === 'active'
                                  ? 'default'
                                  : workflow.status === 'draft'
                                  ? 'secondary'
                                  : 'outline'
                              }
                            >
                              {workflow.status}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground line-clamp-2">
                            {workflow.description}
                          </p>
                          <div className="flex items-center gap-2 text-xs text-muted-foreground">
                            <Badge variant="outline" className="text-xs">
                              {TRIGGER_TYPES.find((t) => t.value === workflow.trigger_type)?.label}
                            </Badge>
                            <span>{workflow.actions.length} actions</span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>

        {/* Workflow Editor */}
        <div className="lg:col-span-2">
          {(selectedWorkflow || isCreating) ? (
            <WorkflowEditor
              workflow={selectedWorkflow!}
              onSave={saveWorkflow}
              onCancel={() => {
                setSelectedWorkflow(null);
                setIsCreating(false);
              }}
              onExecute={selectedWorkflow?.id ? () => executeWorkflow(selectedWorkflow.id!) : undefined}
              onToggleStatus={
                selectedWorkflow?.id
                  ? () => toggleWorkflowStatus(selectedWorkflow.id!, selectedWorkflow.status)
                  : undefined
              }
            />
          ) : (
            <Card className="h-full flex items-center justify-center">
              <CardContent>
                <div className="text-center text-muted-foreground">
                  <Workflow className="h-16 w-16 mx-auto mb-4 opacity-50" />
                  <p>Select a workflow or create a new one</p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

// Workflow Editor Component
function WorkflowEditor({
  workflow,
  onSave,
  onCancel,
  onExecute,
  onToggleStatus,
}: {
  workflow: WorkflowData;
  onSave: (workflow: WorkflowData) => void;
  onCancel: () => void;
  onExecute?: () => void;
  onToggleStatus?: () => void;
}) {
  const [editedWorkflow, setEditedWorkflow] = useState<WorkflowData>(workflow);

  const addAction = (type: string) => {
    const defaultParams: Record<string, any> = {
      send_email: { recipient: '', subject: '', message: '' },
      create_task: { title: '', assigned_to: null, priority: 'medium' },
      update_field: { model: '', field: '', value: '' },
      send_notification: { user_id: null, title: '', message: '' },
      webhook: { url: '', method: 'POST', payload: {} },
      wait: { seconds: 60 },
    };

    setEditedWorkflow({
      ...editedWorkflow,
      actions: [...editedWorkflow.actions, { type, params: defaultParams[type] || {} }],
    });
  };

  const removeAction = (index: number) => {
    setEditedWorkflow({
      ...editedWorkflow,
      actions: editedWorkflow.actions.filter((_, i) => i !== index),
    });
  };

  const updateAction = (index: number, params: Record<string, any>) => {
    const newActions = [...editedWorkflow.actions];
    newActions[index].params = params;
    setEditedWorkflow({ ...editedWorkflow, actions: newActions });
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle>
              {workflow.id ? 'Edit Workflow' : 'Create New Workflow'}
            </CardTitle>
            <CardDescription>Configure triggers and actions</CardDescription>
          </div>
          <div className="flex gap-2">
            {onExecute && (
              <Button variant="outline" size="sm" onClick={onExecute}>
                <Play className="h-4 w-4 mr-2" />
                Test Run
              </Button>
            )}
            {onToggleStatus && (
              <Button variant="outline" size="sm" onClick={onToggleStatus}>
                {workflow.status === 'active' ? (
                  <>
                    <Pause className="h-4 w-4 mr-2" />
                    Deactivate
                  </>
                ) : (
                  <>
                    <Zap className="h-4 w-4 mr-2" />
                    Activate
                  </>
                )}
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="basic" className="space-y-4">
          <TabsList>
            <TabsTrigger value="basic">Basic Info</TabsTrigger>
            <TabsTrigger value="trigger">Trigger</TabsTrigger>
            <TabsTrigger value="actions">Actions ({editedWorkflow.actions.length})</TabsTrigger>
          </TabsList>

          {/* Basic Info Tab */}
          <TabsContent value="basic" className="space-y-4">
            <div>
              <Label htmlFor="name">Workflow Name</Label>
              <Input
                id="name"
                value={editedWorkflow.name}
                onChange={(e) => setEditedWorkflow({ ...editedWorkflow, name: e.target.value })}
                placeholder="e.g., New Lead Follow-up"
              />
            </div>
            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={editedWorkflow.description}
                onChange={(e) => setEditedWorkflow({ ...editedWorkflow, description: e.target.value })}
                placeholder="What does this workflow do?"
                rows={3}
              />
            </div>
          </TabsContent>

          {/* Trigger Tab */}
          <TabsContent value="trigger" className="space-y-4">
            <div>
              <Label htmlFor="trigger">Trigger Type</Label>
              <Select
                value={editedWorkflow.trigger_type}
                onValueChange={(value) =>
                  setEditedWorkflow({ ...editedWorkflow, trigger_type: value })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {TRIGGER_TYPES.map((trigger) => (
                    <SelectItem key={trigger.value} value={trigger.value}>
                      {trigger.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="p-4 border rounded-lg bg-muted/50">
              <p className="text-sm text-muted-foreground">
                This workflow will run when: <strong>{TRIGGER_TYPES.find(t => t.value === editedWorkflow.trigger_type)?.label}</strong>
              </p>
            </div>
          </TabsContent>

          {/* Actions Tab */}
          <TabsContent value="actions" className="space-y-4">
            <div className="flex justify-between items-center">
              <Label>Workflow Actions</Label>
              <ActionSelector onSelect={addAction} />
            </div>

            <div className="space-y-3">
              {editedWorkflow.actions.map((action, index) => (
                <ActionEditor
                  key={index}
                  action={action}
                  index={index}
                  onUpdate={(params) => updateAction(index, params)}
                  onRemove={() => removeAction(index)}
                />
              ))}

              {editedWorkflow.actions.length === 0 && (
                <div className="text-center py-12 border-2 border-dashed rounded-lg">
                  <p className="text-muted-foreground">No actions yet. Add your first action above.</p>
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>

        <div className="flex justify-end gap-2 mt-6 pt-6 border-t">
          <Button variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button onClick={() => onSave(editedWorkflow)}>
            {workflow.id ? 'Update Workflow' : 'Create Workflow'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

// Action Selector Component
function ActionSelector({ onSelect }: { onSelect: (type: string) => void }) {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button size="sm">
          <Plus className="h-4 w-4 mr-2" />
          Add Action
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add Action</DialogTitle>
          <DialogDescription>Choose an action to add to your workflow</DialogDescription>
        </DialogHeader>
        <div className="grid grid-cols-2 gap-3">
          {ACTION_TYPES.map((actionType) => {
            const Icon = actionType.icon;
            return (
              <Button
                key={actionType.value}
                variant="outline"
                className="h-auto py-4 flex-col gap-2"
                onClick={() => onSelect(actionType.value)}
              >
                <Icon className="h-6 w-6" />
                <span className="text-sm">{actionType.label}</span>
              </Button>
            );
          })}
        </div>
      </DialogContent>
    </Dialog>
  );
}

// Action Editor Component
function ActionEditor({
  action,
  index,
  onUpdate,
  onRemove,
}: {
  action: WorkflowAction;
  index: number;
  onUpdate: (params: Record<string, any>) => void;
  onRemove: () => void;
}) {
  const actionType = ACTION_TYPES.find((t) => t.value === action.type);
  const Icon = actionType?.icon || Settings;

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10">
              <span className="text-xs font-bold">{index + 1}</span>
            </div>
            <Icon className="h-4 w-4" />
            <CardTitle className="text-base">{actionType?.label}</CardTitle>
          </div>
          <Button variant="ghost" size="sm" onClick={onRemove}>
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {action.type === 'send_email' && (
          <>
            <Input
              placeholder="Recipient email"
              value={action.params.recipient || ''}
              onChange={(e) => onUpdate({ ...action.params, recipient: e.target.value })}
            />
            <Input
              placeholder="Subject"
              value={action.params.subject || ''}
              onChange={(e) => onUpdate({ ...action.params, subject: e.target.value })}
            />
            <Textarea
              placeholder="Message (use {{variable}} for dynamic content)"
              value={action.params.message || ''}
              onChange={(e) => onUpdate({ ...action.params, message: e.target.value })}
              rows={3}
            />
          </>
        )}

        {action.type === 'create_task' && (
          <>
            <Input
              placeholder="Task title"
              value={action.params.title || ''}
              onChange={(e) => onUpdate({ ...action.params, title: e.target.value })}
            />
            <Select
              value={action.params.priority}
              onValueChange={(value) => onUpdate({ ...action.params, priority: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Priority" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="low">Low</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="high">High</SelectItem>
              </SelectContent>
            </Select>
          </>
        )}

        {action.type === 'webhook' && (
          <>
            <Input
              placeholder="Webhook URL"
              value={action.params.url || ''}
              onChange={(e) => onUpdate({ ...action.params, url: e.target.value })}
            />
            <Select
              value={action.params.method}
              onValueChange={(value) => onUpdate({ ...action.params, method: value })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="GET">GET</SelectItem>
                <SelectItem value="POST">POST</SelectItem>
                <SelectItem value="PUT">PUT</SelectItem>
              </SelectContent>
            </Select>
          </>
        )}
      </CardContent>
    </Card>
  );
}
