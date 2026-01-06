'use client';

import { useState } from 'react';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
// import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { toast } from 'sonner';
import { Plug, Settings, Link, Unlink, Loader2 } from 'lucide-react';

interface Integration {
  id: string;
  name: string;
  description: string;
  icon: React.ElementType;
  enabled: boolean;
  connected: boolean;
}

export default function IntegrationsSettingsPage() {
  const [isSaving, setIsSaving] = useState(false);
  const [integrations, setIntegrations] = useState<Integration[]>([
    {
      id: 'salesforce',
      name: 'Salesforce',
      description: 'Sync contacts and deals with Salesforce',
      icon: Plug,
      enabled: true,
      connected: true,
    },
    {
      id: 'hubspot',
      name: 'HubSpot',
      description: 'Two-way sync with HubSpot CRM',
      icon: Plug,
      enabled: false,
      connected: false,
    },
    {
      id: 'slack',
      name: 'Slack',
      description: 'Get notifications and updates in Slack',
      icon: Plug,
      enabled: true,
      connected: true,
    },
    {
      id: 'gmail',
      name: 'Gmail',
      description: 'Track emails and manage inbox',
      icon: Plug,
      enabled: true,
      connected: true,
    },
    {
      id: 'microsoft',
      name: 'Microsoft Outlook',
      description: 'Sync with your Microsoft calendar',
      icon: Plug,
      enabled: false,
      connected: false,
    },
    {
      id: 'zapier',
      name: 'Zapier',
      description: 'Automate workflows with Zapier',
      icon: Plug,
      enabled: false,
      connected: false,
    },
  ]);

  const handleToggleIntegration = async (integrationId: string) => {
    const integration = integrations.find(i => i.id === integrationId);
    if (!integration) return;

    setIsSaving(true);
    try {
      const response = await fetch(`/api/v1/integrations/${integrationId}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: !integration.enabled }),
      });

      if (!response.ok) throw new Error('Failed to update integration');

      setIntegrations(prev =>
        prev.map(i => i.id === integrationId ? { ...i, enabled: !i.enabled } : i)
      );

      toast.success(
        `${integration.name} ${!integration.enabled ? 'enabled' : 'disabled'}`
      );
    } catch (error) {
      console.log("Failed to update integration",error);
      toast.error('Failed to update integration');
    } finally {
      setIsSaving(false);
    }
  };

  const handleConnectIntegration = async (integrationId: string) => {
    setIsSaving(true);
    try {
      const response = await fetch(`/api/v1/integrations/${integrationId}/connect/`, {
        method: 'POST',
      });

      if (!response.ok) throw new Error('Failed to connect integration');

      const data = await response.json();
      if (data.auth_url) {
        window.location.href = data.auth_url;
      }

      toast.success('Integration connected successfully');
    } catch (error) {
      console.log("Failed to connect integration",error);
      toast.error('Failed to connect integration');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDisconnectIntegration = async (integrationId: string) => {
    if (!window.confirm('Are you sure you want to disconnect this integration?')) return;

    setIsSaving(true);
    try {
      const response = await fetch(`/api/v1/integrations/${integrationId}/disconnect/`, {
        method: 'POST',
      });

      if (!response.ok) throw new Error('Failed to disconnect integration');

      setIntegrations(prev =>
        prev.map(i => i.id === integrationId ? { ...i, connected: false } : i)
      );

      toast.success('Integration disconnected');
    } catch (error) {
      console.log("Failed to disconnect integration",error);
      toast.error('Failed to disconnect integration');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-4 lg:p-6 space-y-6 max-w-4xl">
          <div>
            <h1 className="text-2xl lg:text-3xl font-bold text-gray-900 dark:text-white">Integrations</h1>
            <p className="text-gray-500 mt-1">Connect and manage third-party integrations</p>
          </div>

          {/* Integrations Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {integrations.map((integration) => (
              <Card key={integration.id}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <Plug className="w-6 h-6 text-gray-400" />
                      <div>
                        <CardTitle>{integration.name}</CardTitle>
                        <CardDescription>{integration.description}</CardDescription>
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Status Badges */}
                  <div className="flex gap-2">
                    {integration.enabled ? (
                      <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                        Enabled
                      </Badge>
                    ) : (
                      <Badge className="bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200">
                        Disabled
                      </Badge>
                    )}
                    {integration.connected ? (
                      <Badge className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                        Connected
                      </Badge>
                    ) : (
                      <Badge className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
                        Not Connected
                      </Badge>
                    )}
                  </div>

                  {/* Controls */}
                  <div className="space-y-2">
                    {!integration.connected ? (
                      <Button
                        onClick={() => handleConnectIntegration(integration.id)}
                        disabled={isSaving}
                        className="w-full gap-2"
                      >
                        {isSaving ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <Link className="w-4 h-4" />
                        )}
                        Connect
                      </Button>
                    ) : (
                      <>
                        <Button
                          type="button"
                          variant="outline"
                          className="w-full gap-2"
                        >
                          <Settings className="w-4 h-4" />
                          Settings
                        </Button>
                        <Button
                          onClick={() => handleDisconnectIntegration(integration.id)}
                          disabled={isSaving}
                          variant="destructive"
                          className="w-full gap-2"
                        >
                          {isSaving ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <Unlink className="w-4 h-4" />
                          )}
                          Disconnect
                        </Button>
                      </>
                    )}
                  </div>

                  {/* Toggle Enable/Disable */}
                  {integration.connected && (
                    <div className="flex items-center justify-between pt-2 border-t">
                      <Label className="text-sm">Enable Integration</Label>
                      <Switch
                        checked={integration.enabled}
                        onCheckedChange={() => handleToggleIntegration(integration.id)}
                      />
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Available Integrations */}
          <Card>
            <CardHeader>
              <CardTitle>Explore More Integrations</CardTitle>
              <CardDescription>Discover more apps and services to connect</CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="outline" className="gap-2">
                <Plug className="w-4 h-4" />
                Browse Integration Marketplace
              </Button>
            </CardContent>
          </Card>

          {/* Integration Support */}
          <Card>
            <CardHeader>
              <CardTitle>Integration Support</CardTitle>
              <CardDescription>Need help with integrations?</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Check our documentation for setup guides and troubleshooting.
              </p>
              <Button variant="outline">View Integration Docs</Button>
            </CardContent>
          </Card>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
