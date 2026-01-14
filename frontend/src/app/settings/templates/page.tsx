'use client';

import { useState } from 'react';
import { toast } from 'sonner';
import { FileText, Copy, Edit2, Trash2, Plus, Save, Loader2 } from 'lucide-react';

import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';

interface Template {
  id: string;
  name: string;
  type: 'email' | 'document';
  preview: string;
  createdAt: string;
  updatedAt: string;
  usage: number;
}

export default function TemplatesSettingsPage() {
  const [isSaving, setIsSaving] = useState(false);
  const [templates, setTemplates] = useState<Template[]>([
    {
      id: '1',
      name: 'Welcome Email',
      type: 'email',
      preview: 'Welcome to our platform...',
      createdAt: 'Jan 1, 2024',
      updatedAt: 'Jan 15, 2025',
      usage: 42,
    },
    {
      id: '2',
      name: 'Follow-up Email',
      type: 'email',
      preview: 'Just checking in on your interest...',
      createdAt: 'Jan 5, 2024',
      updatedAt: 'Jan 10, 2025',
      usage: 18,
    },
  ]);

  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newTemplate, setNewTemplate] = useState({
    name: '',
    type: 'email' as 'email' | 'document',
    content: '',
  });

  const handleCreateTemplate = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSaving(true);

    try {
      const response = await fetch('/api/v1/templates/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTemplate),
      });

      if (!response.ok) throw new Error('Failed to create template');

      const data = await response.json();
      setTemplates(prev => [...prev, {
        id: data.id,
        name: data.name,
        type: data.type,
        preview: data.content.substring(0, 100),
        createdAt: new Date().toLocaleDateString(),
        updatedAt: new Date().toLocaleDateString(),
        usage: 0,
      }]);

      toast.success('Template created successfully');
      setShowCreateForm(false);
      setNewTemplate({ name: '', type: 'email', content: '' });
    } catch (error) {
      console.warn(error);
      toast.error('Failed to create template');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteTemplate = async (templateId: string) => {
    if (!window.confirm('Are you sure you want to delete this template?')) return;

    try {
      const response = await fetch(`/api/v1/templates/${templateId}/`, {
        method: 'DELETE',
      });

      if (!response.ok) throw new Error('Failed to delete template');

      setTemplates(prev => prev.filter(t => t.id !== templateId));
      toast.success('Template deleted');
    } catch (error) {
      console.warn("Failed to delete template",error);
      toast.error('Failed to delete template');
    }
  };

  const handleCopyTemplate = (template: Template) => {
    navigator.clipboard.writeText(template.preview);
    toast.success(`Copied ${template.name}`);
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-4 lg:p-6 space-y-6 max-w-4xl">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl lg:text-3xl font-bold text-gray-900 dark:text-white">Templates</h1>
              <p className="text-gray-500 mt-1">Create and manage reusable email and document templates</p>
            </div>
            <Button
              onClick={() => setShowCreateForm(!showCreateForm)}
              className="gap-2"
            >
              <Plus className="w-4 h-4" />
              New Template
            </Button>
          </div>

          {/* Create Template Form */}
          {showCreateForm && (
            <Card>
              <CardHeader>
                <CardTitle>Create New Template</CardTitle>
                <CardDescription>Create a reusable template for your emails or documents</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleCreateTemplate} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Template Name</Label>
                    <Input
                      id="name"
                      value={newTemplate.name}
                      onChange={(e) => setNewTemplate(prev => ({ ...prev, name: e.target.value }))}
                      placeholder="e.g., Welcome Email"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="type">Template Type</Label>
                    <select
                      id="type"
                      value={newTemplate.type}
                      onChange={(e) => setNewTemplate(prev => ({ ...prev, type: e.target.value as 'email' | 'document' }))}
                      className="w-full p-2 border rounded-lg dark:bg-gray-900"
                    >
                      <option value="email">Email</option>
                      <option value="document">Document</option>
                    </select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="content">Template Content</Label>
                    <Textarea
                      id="content"
                      value={newTemplate.content}
                      onChange={(e) => setNewTemplate(prev => ({ ...prev, content: e.target.value }))}
                      placeholder="Enter your template content..."
                      className="min-h-32 font-mono text-sm"
                      required
                    />
                  </div>

                  <div className="flex gap-2">
                    <Button
                      type="submit"
                      disabled={isSaving}
                      className="gap-2"
                    >
                      {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                      Create Template
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => setShowCreateForm(false)}
                    >
                      Cancel
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          )}

          {/* Templates List */}
          <div className="space-y-3">
            {templates.length > 0 ? (
              templates.map((template) => (
                <Card key={template.id}>
                  <CardContent className="pt-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <FileText className="w-5 h-5 text-gray-400" />
                          <h3 className="font-semibold text-gray-900 dark:text-white">{template.name}</h3>
                          <Badge className={template.type === 'email' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' : 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'}>
                            {template.type}
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">{template.preview}</p>
                        <div className="flex items-center gap-4 text-xs text-gray-500">
                          <span>Created: {template.createdAt}</span>
                          <span>Updated: {template.updatedAt}</span>
                          <span>Used {template.usage} times</span>
                        </div>
                      </div>

                      <div className="flex gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleCopyTemplate(template)}
                        >
                          <Copy className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                        >
                          <Edit2 className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          onClick={() => handleDeleteTemplate(template.id)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            ) : (
              <Card>
                <CardContent className="pt-6">
                  <p className="text-center text-gray-500">No templates yet. Create one to get started.</p>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Template Variables */}
          <Card>
            <CardHeader>
              <CardTitle>Template Variables</CardTitle>
              <CardDescription>Use these variables in your templates for dynamic content</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div className="p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
                  <code className="text-blue-600 dark:text-blue-400">{'{{first_name}}'}</code>
                  <p className="text-gray-600 dark:text-gray-400">Contact&apos;s first name</p>
                </div>
                <div className="p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
                  <code className="text-blue-600 dark:text-blue-400">{'{{last_name}}'}</code>
                  <p className="text-gray-600 dark:text-gray-400">Contact&apos;s last name</p>
                </div>
                <div className="p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
                  <code className="text-blue-600 dark:text-blue-400">{'{{email}}'}</code>
                  <p className="text-gray-600 dark:text-gray-400">Contact&apos;s email address</p>
                </div>
                <div className="p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
                  <code className="text-blue-600 dark:text-blue-400">{'{{company}}'}</code>
                  <p className="text-gray-600 dark:text-gray-400">Contact&apos;s company name</p>
                </div>
                <div className="p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
                  <code className="text-blue-600 dark:text-blue-400">{'{{date}}'}</code>
                  <p className="text-gray-600 dark:text-gray-400">Current date</p>
                </div>
                <div className="p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
                  <code className="text-blue-600 dark:text-blue-400">{'{{user_name}}'}</code>
                  <p className="text-gray-600 dark:text-gray-400">Your name</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}

