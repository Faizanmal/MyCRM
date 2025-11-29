'use client';

import { useState, useEffect } from 'react';
import { integrationHubAPI, Integration, IntegrationProvider } from '@/lib/new-features-api';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import {
  PuzzlePieceIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ArrowPathIcon,
  PlusIcon,
  LinkIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export default function IntegrationHubPage() {
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [providers, setProviders] = useState<IntegrationProvider[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'active' | 'available'>('active');
  const [syncing, setSyncing] = useState<Record<string, boolean>>({});

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [integrationsRes, providersRes] = await Promise.all([
        integrationHubAPI.getIntegrations(),
        integrationHubAPI.getProviders(),
      ]);
      setIntegrations(integrationsRes.data.results || integrationsRes.data);
      setProviders(providersRes.data.results || providersRes.data);
    } catch (error) {
      console.error('Failed to load integrations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async (providerId: string) => {
    try {
      const response = await integrationHubAPI.createIntegration({
        provider: providerId,
        name: `${providers.find(p => p.id === providerId)?.name} Integration`,
      });
      
      if (response.data.auth_url) {
        window.location.href = response.data.auth_url;
      } else {
        await loadData();
      }
    } catch (error) {
      console.error('Failed to connect integration:', error);
      alert('Failed to connect integration. Please try again.');
    }
  };

  const handleSync = async (id: string) => {
    setSyncing({ ...syncing, [id]: true });
    try {
      await integrationHubAPI.syncNow(id);
      alert('Sync started successfully!');
      await loadData();
    } catch (error) {
      console.error('Failed to sync:', error);
      alert('Failed to start sync.');
    } finally {
      setSyncing({ ...syncing, [id]: false });
    }
  };

  const handleTest = async (id: string) => {
    try {
      const response = await integrationHubAPI.testConnection(id);
      if (response.data.success) {
        alert('Connection test successful!');
      } else {
        alert('Connection test failed: ' + (response.data.message || 'Unknown error'));
      }
    } catch (error) {
      console.error('Failed to test connection:', error);
      alert('Connection test failed.');
    }
  };

  const handleDisconnect = async (id: string) => {
    if (!confirm('Are you sure you want to disconnect this integration?')) {
      return;
    }
    
    try {
      await integrationHubAPI.deleteIntegration(id);
      alert('Integration disconnected successfully!');
      await loadData();
    } catch (error) {
      console.error('Failed to disconnect:', error);
      alert('Failed to disconnect integration.');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected':
        return <CheckCircleIcon className="w-5 h-5 text-green-500" />;
      case 'error':
        return <XCircleIcon className="w-5 h-5 text-red-500" />;
      case 'pending':
        return <ClockIcon className="w-5 h-5 text-yellow-500" />;
      default:
        return <ExclamationTriangleIcon className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected':
        return 'bg-green-100 text-green-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <ProtectedRoute>
        <MainLayout>
          <div className="flex items-center justify-center h-96">
            <ArrowPathIcon className="w-12 h-12 text-blue-600 animate-spin" />
          </div>
        </MainLayout>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-6 max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                  <PuzzlePieceIcon className="w-10 h-10 text-blue-600" />
                  Integration Hub
                </h1>
                <p className="text-gray-600 mt-2">
                  Connect your CRM with external services and automate workflows
                </p>
              </div>
              <div className="flex items-center gap-3">
                <Card className="px-4 py-2">
                  <div className="flex items-center gap-2">
                    <LinkIcon className="w-5 h-5 text-blue-600" />
                    <div>
                      <div className="text-2xl font-bold">{integrations.filter(i => i.is_active).length}</div>
                      <div className="text-xs text-gray-600">Active</div>
                    </div>
                  </div>
                </Card>
                <Card className="px-4 py-2">
                  <div className="flex items-center gap-2">
                    <ChartBarIcon className="w-5 h-5 text-green-600" />
                    <div>
                      <div className="text-2xl font-bold">{providers.length}</div>
                      <div className="text-xs text-gray-600">Available</div>
                    </div>
                  </div>
                </Card>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200 mb-6">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('active')}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'active'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Active Integrations ({integrations.length})
              </button>
              <button
                onClick={() => setActiveTab('available')}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'available'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Available Integrations ({providers.length})
              </button>
            </nav>
          </div>

          {/* Active Integrations Tab */}
          {activeTab === 'active' && (
            <div>
              {integrations.length === 0 ? (
                <Card className="p-12 text-center">
                  <PuzzlePieceIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">No active integrations</h3>
                  <p className="text-gray-600 mb-6">
                    Connect with external services to enhance your CRM capabilities
                  </p>
                  <Button onClick={() => setActiveTab('available')}>
                    Browse Available Integrations
                  </Button>
                </Card>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {integrations.map((integration) => (
                    <Card key={integration.id} className="hover:shadow-lg transition-shadow">
                      <CardHeader>
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-3">
                            <div className="w-12 h-12 bg-linear-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-white text-xl font-bold">
                              {integration.provider.name.charAt(0)}
                            </div>
                            <div>
                              <CardTitle className="text-lg">{integration.name}</CardTitle>
                              <CardDescription className="text-sm">
                                {integration.provider.name}
                              </CardDescription>
                            </div>
                          </div>
                          {getStatusIcon(integration.status)}
                        </div>
                        <Badge className={getStatusColor(integration.status)}>
                          {integration.status}
                        </Badge>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Last Sync:</span>
                            <span className="font-medium">
                              {integration.last_sync_at
                                ? new Date(integration.last_sync_at).toLocaleDateString()
                                : 'Never'}
                            </span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Next Sync:</span>
                            <span className="font-medium">
                              {integration.next_sync_at
                                ? new Date(integration.next_sync_at).toLocaleDateString()
                                : 'Manual'}
                            </span>
                          </div>
                          {integration.error_message && (
                            <div className="text-xs text-red-600 bg-red-50 p-2 rounded">
                              {integration.error_message}
                            </div>
                          )}
                          <div className="flex gap-2 pt-2">
                            <Button
                              variant="outline"
                              size="sm"
                              className="flex-1"
                              onClick={() => handleTest(integration.id)}
                            >
                              Test
                            </Button>
                            <Button
                              size="sm"
                              className="flex-1"
                              onClick={() => handleSync(integration.id)}
                              disabled={syncing[integration.id]}
                            >
                              {syncing[integration.id] ? (
                                <ArrowPathIcon className="w-4 h-4 animate-spin" />
                              ) : (
                                'Sync'
                              )}
                            </Button>
                          </div>
                          <Button
                            variant="destructive"
                            size="sm"
                            className="w-full"
                            onClick={() => handleDisconnect(integration.id)}
                          >
                            Disconnect
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Available Integrations Tab */}
          {activeTab === 'available' && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {providers.filter(p => p.is_active).map((provider) => {
                const isConnected = integrations.some(i => i.provider.id === provider.id);
                return (
                  <Card key={provider.id} className="hover:shadow-lg transition-shadow">
                    <CardHeader>
                      <div className="flex items-center gap-3 mb-2">
                        <div className="w-12 h-12 bg-linear-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-white text-xl font-bold">
                          {provider.name.charAt(0)}
                        </div>
                        <div>
                          <CardTitle className="text-lg">{provider.name}</CardTitle>
                          <CardDescription className="text-xs">
                            {provider.auth_type.replace('_', ' ').toUpperCase()}
                          </CardDescription>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                        {provider.description}
                      </p>
                      <div className="mb-4">
                        <p className="text-xs font-semibold text-gray-700 mb-2">Features:</p>
                        <div className="flex flex-wrap gap-1">
                          {provider.supported_features.slice(0, 3).map((feature) => (
                            <Badge key={feature} variant="secondary" className="text-xs">
                              {feature}
                            </Badge>
                          ))}
                          {provider.supported_features.length > 3 && (
                            <Badge variant="secondary" className="text-xs">
                              +{provider.supported_features.length - 3} more
                            </Badge>
                          )}
                        </div>
                      </div>
                      <Button
                        className="w-full"
                        onClick={() => handleConnect(provider.id)}
                        disabled={isConnected}
                      >
                        {isConnected ? (
                          <>
                            <CheckCircleIcon className="w-4 h-4 mr-2" />
                            Connected
                          </>
                        ) : (
                          <>
                            <PlusIcon className="w-4 h-4 mr-2" />
                            Connect
                          </>
                        )}
                      </Button>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
