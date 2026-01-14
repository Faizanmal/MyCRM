'use client';

import { useState } from 'react';
import { toast } from 'sonner';
import { Lock, Copy, Eye, EyeOff, Plus, Trash2, RefreshCw, Loader2 } from 'lucide-react';

import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';

interface ApiKey {
  id: string;
  name: string;
  key: string;
  createdAt: string;
  lastUsedAt: string;
  isActive: boolean;
}

export default function ApiSettingsPage() {
  const [isSaving, setIsSaving] = useState(false);
  const [showKeyForm, setShowKeyForm] = useState(false);
  const [keyName, setKeyName] = useState('');
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([
    {
      id: '1',
      name: 'Production API Key',
      key: 'sk_live_***************************',
      createdAt: 'Jan 1, 2024',
      lastUsedAt: 'Jan 15, 2025',
      isActive: true,
    },
    {
      id: '2',
      name: 'Development API Key',
      key: 'sk_test_***************************',
      createdAt: 'Dec 15, 2024',
      lastUsedAt: 'Jan 14, 2025',
      isActive: true,
    },
  ]);

  const [visibleKeys, setVisibleKeys] = useState<Set<string>>(new Set());

  const handleToggleKeyVisibility = (keyId: string) => {
    const newVisible = new Set(visibleKeys);
    if (newVisible.has(keyId)) {
      newVisible.delete(keyId);
    } else {
      newVisible.add(keyId);
    }
    setVisibleKeys(newVisible);
  };

  const handleCreateApiKey = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSaving(true);

    try {
      const response = await fetch('/api/v1/api-keys/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: keyName }),
      });

      if (!response.ok) throw new Error('Failed to create API key');

      const data = await response.json();
      setApiKeys(prev => [...prev, {
        id: data.id,
        name: data.name,
        key: data.key,
        createdAt: new Date().toLocaleDateString(),
        lastUsedAt: 'Never',
        isActive: true,
      }]);

      toast.success('API key created successfully');
      setKeyName('');
      setShowKeyForm(false);
    } catch (error) {
      console.warn("Failed to create API key",error);
      toast.error('Failed to create API key');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCopyKey = (key: string) => {
    navigator.clipboard.writeText(key);
    toast.success('API key copied to clipboard');
  };

  const handleDeleteKey = async (keyId: string) => {
    if (!window.confirm('Are you sure you want to delete this API key?')) return;

    try {
      const response = await fetch(`/api/v1/api-keys/${keyId}/`, {
        method: 'DELETE',
      });

      if (!response.ok) throw new Error('Failed to delete API key');

      setApiKeys(prev => prev.filter(k => k.id !== keyId));
      toast.success('API key deleted');
    } catch (error) {
      console.warn("Failed to delete API key",error);
      toast.error('Failed to delete API key');
    }
  };

  const handleRotateKey = async (keyId: string) => {
    if (!window.confirm('Rotate this API key? Any applications using it will need to be updated.')) return;

    try {
      const response = await fetch(`/api/v1/api-keys/${keyId}/rotate/`, {
        method: 'POST',
      });

      if (!response.ok) throw new Error('Failed to rotate API key');

      toast.success('API key rotated successfully');
    } catch (error) {
      console.warn("Failed to rotate API key",error);
      toast.error('Failed to rotate API key');
    }
  };

  // let newVisibleKeys: Set<string>;

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-4 lg:p-6 space-y-6 max-w-4xl">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl lg:text-3xl font-bold text-gray-900 dark:text-white">API Keys</h1>
              <p className="text-gray-500 mt-1">Manage your API keys for integrations and third-party applications</p>
            </div>
            <Button
              onClick={() => setShowKeyForm(!showKeyForm)}
              className="gap-2"
            >
              <Plus className="w-4 h-4" />
              Create API Key
            </Button>
          </div>

          {/* Create API Key Form */}
          {showKeyForm && (
            <Card>
              <CardHeader>
                <CardTitle>Create New API Key</CardTitle>
                <CardDescription>Create a new API key for your application</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleCreateApiKey} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="key-name">Key Name</Label>
                    <Input
                      id="key-name"
                      value={keyName}
                      onChange={(e) => setKeyName(e.target.value)}
                      placeholder="e.g., My App Integration"
                      required
                    />
                    <p className="text-xs text-gray-500">Give your API key a descriptive name</p>
                  </div>

                  <div className="flex gap-2">
                    <Button type="submit" disabled={isSaving} className="gap-2">
                      {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
                      Create Key
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => setShowKeyForm(false)}
                    >
                      Cancel
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          )}

          {/* API Keys List */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lock className="w-5 h-5" />
                Your API Keys ({apiKeys.length})
              </CardTitle>
              <CardDescription>Manage your active API keys</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {apiKeys.length > 0 ? (
                apiKeys.map((apiKey) => (
                  <div key={apiKey.id} className="p-4 border rounded-lg space-y-3">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900 dark:text-white">{apiKey.name}</h3>
                        <div className="flex items-center gap-3 mt-1 text-sm text-gray-500">
                          <span>Created: {apiKey.createdAt}</span>
                          <span>Last used: {apiKey.lastUsedAt}</span>
                        </div>
                      </div>
                      {apiKey.isActive && (
                        <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                          Active
                        </Badge>
                      )}
                    </div>

                    {/* Key Display */}
                    <div className="flex items-center gap-2 bg-gray-50 dark:bg-gray-900 p-3 rounded border font-mono text-sm">
                      {visibleKeys.has(apiKey.id) ? apiKey.key : apiKey.key}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleToggleKeyVisibility(apiKey.id)}
                      >
                        {visibleKeys.has(apiKey.id) ? (
                          <EyeOff className="w-4 h-4" />
                        ) : (
                          <Eye className="w-4 h-4" />
                        )}
                      </Button>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        className="gap-2"
                        onClick={() => handleCopyKey(apiKey.key)}
                      >
                        <Copy className="w-4 h-4" />
                        Copy
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        className="gap-2"
                        onClick={() => handleRotateKey(apiKey.id)}
                      >
                        <RefreshCw className="w-4 h-4" />
                        Rotate
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        className="gap-2 ml-auto"
                        onClick={() => handleDeleteKey(apiKey.id)}
                      >
                        <Trash2 className="w-4 h-4" />
                        Delete
                      </Button>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-gray-500">No API keys yet. Create one to get started.</p>
              )}
            </CardContent>
          </Card>

          {/* API Documentation */}
          <Card>
            <CardHeader>
              <CardTitle>API Documentation</CardTitle>
              <CardDescription>Learn how to use our API</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Getting Started</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                  Use your API key in the Authorization header of your requests:
                </p>
                <div className="bg-gray-900 text-gray-100 p-4 rounded-lg font-mono text-sm overflow-x-auto">
                  <code>{`Authorization: Bearer your_api_key_here`}</code>
                </div>
              </div>

              <div className="pt-3">
                <Button variant="outline" className="gap-2">
                  View Full API Documentation
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Security Warning */}
          <Card className="border-yellow-200 dark:border-yellow-900">
            <CardHeader>
              <CardTitle className="text-yellow-600 dark:text-yellow-400 flex items-center gap-2">
                <Lock className="w-5 h-5" />
                Security Tips
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-yellow-800 dark:text-yellow-200">
              <p>• Never share your API keys publicly</p>
              <p>• Use different keys for development and production</p>
              <p>• Rotate your keys regularly</p>
              <p>• Delete keys you no longer use</p>
              <p>• Store keys securely in environment variables</p>
            </CardContent>
          </Card>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}

