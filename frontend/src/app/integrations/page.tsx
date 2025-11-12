'use client';

import { useState, useEffect } from 'react';
import { integrationAPI } from '@/lib/api';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import {
  PuzzlePieceIcon,
  BoltIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ArrowPathIcon,
  PlusIcon,
  LinkIcon,
} from '@heroicons/react/24/outline';

// Integration Platform Icons/Logos
const integrationLogos: any = {
  slack: '💬',
  teams: '👥',
  salesforce: '☁️',
  hubspot: '🎯',
  mailchimp: '📧',
  zapier: '⚡',
  custom: '🔧',
};

export default function IntegrationsPage() {
  const [integrations, setIntegrations] = useState<any[]>([]);
  const [webhooks, setWebhooks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'integrations' | 'webhooks'>('integrations');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [integrationsRes, webhooksRes] = await Promise.all([
        integrationAPI.getIntegrations(),
        integrationAPI.getWebhooks(),
      ]);
      setIntegrations(integrationsRes.data.results || integrationsRes.data);
      setWebhooks(webhooksRes.data.results || webhooksRes.data);
    } catch (error) {
      console.error('Failed to load integrations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTestIntegration = async (id: string) => {
    try {
      await integrationAPI.testIntegration(id);
      alert('Integration test successful!');
    } catch (error) {
      alert('Integration test failed. Check the logs for details.');
    }
  };

  const handleSyncIntegration = async (id: string) => {
    try {
      await integrationAPI.syncIntegration(id);
      alert('Sync started successfully!');
      await loadData();
    } catch (error) {
      alert('Failed to start sync.');
    }
  };

  const handleTestWebhook = async (id: string) => {
    try {
      await integrationAPI.testWebhook(id);
      alert('Test webhook sent successfully!');
    } catch (error) {
      alert('Failed to send test webhook.');
    }
  };

  const toggleWebhook = async (webhook: any) => {
    try {
      if (webhook.is_active) {
        await integrationAPI.deactivateWebhook(webhook.id);
      } else {
        await integrationAPI.activateWebhook(webhook.id);
      }
      await loadData();
    } catch (error) {
      alert('Failed to toggle webhook.');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'text-green-600 bg-green-50';
      case 'error': return 'text-red-600 bg-red-50';
      case 'syncing': return 'text-blue-600 bg-blue-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected': return <CheckCircleIcon className="w-4 h-4" />;
      case 'error': return <XCircleIcon className="w-4 h-4" />;
      case 'syncing': return <ArrowPathIcon className="w-4 h-4 animate-spin" />;
      default: return <ClockIcon className="w-4 h-4" />;
    }
  };

  if (loading) {
    return (
      <ProtectedRoute>
        <MainLayout>
          <div className="flex items-center justify-center h-96">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        </MainLayout>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                <PuzzlePieceIcon className="w-8 h-8 mr-3 text-blue-600" />
                Integrations & Webhooks
              </h1>
              <p className="text-gray-600 mt-1">Connect your CRM with external services</p>
            </div>
            <button className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              <PlusIcon className="w-5 h-5 mr-2" />
              Add Integration
            </button>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200 mb-6">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('integrations')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'integrations'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <PuzzlePieceIcon className="w-5 h-5 inline-block mr-2" />
                Integrations ({integrations.length})
              </button>
              <button
                onClick={() => setActiveTab('webhooks')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'webhooks'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <BoltIcon className="w-5 h-5 inline-block mr-2" />
                Webhooks ({webhooks.length})
              </button>
            </nav>
          </div>

          {/* Integrations Tab */}
          {activeTab === 'integrations' && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {integrations.length === 0 ? (
                <div className="col-span-full bg-white rounded-lg shadow p-12 text-center">
                  <PuzzlePieceIcon className="mx-auto h-16 w-16 text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No integrations yet</h3>
                  <p className="text-gray-500">Connect with external services to enhance your CRM</p>
                </div>
              ) : (
                integrations.map((integration) => (
                  <div key={integration.id} className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow">
                    {/* Integration Header */}
                    <div className="p-6 border-b border-gray-200">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center">
                          <div className="text-4xl mr-3">
                            {integrationLogos[integration.platform] || '🔧'}
                          </div>
                          <div>
                            <h3 className="font-semibold text-gray-900 capitalize">
                              {integration.name}
                            </h3>
                            <p className="text-sm text-gray-500 capitalize">{integration.platform}</p>
                          </div>
                        </div>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(integration.status)}`}>
                          {getStatusIcon(integration.status)}
                          <span className="ml-1 capitalize">{integration.status}</span>
                        </span>
                      </div>
                      
                      {integration.description && (
                        <p className="text-sm text-gray-600">{integration.description}</p>
                      )}
                    </div>

                    {/* Integration Stats */}
                    <div className="p-6 bg-gray-50">
                      <div className="grid grid-cols-2 gap-4 mb-4">
                        <div>
                          <p className="text-xs text-gray-600">Last Sync</p>
                          <p className="text-sm font-medium text-gray-900">
                            {integration.last_sync_at
                              ? new Date(integration.last_sync_at).toLocaleDateString()
                              : 'Never'}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-600">Auth Type</p>
                          <p className="text-sm font-medium text-gray-900 capitalize">
                            {integration.auth_type || 'API Key'}
                          </p>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleTestIntegration(integration.id)}
                          className="flex-1 px-3 py-2 bg-white border border-gray-300 text-gray-700 rounded hover:bg-gray-50 text-sm font-medium"
                        >
                          Test
                        </button>
                        <button
                          onClick={() => handleSyncIntegration(integration.id)}
                          disabled={integration.status === 'syncing'}
                          className="flex-1 px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {integration.status === 'syncing' ? 'Syncing...' : 'Sync Now'}
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {/* Webhooks Tab */}
          {activeTab === 'webhooks' && (
            <div className="bg-white rounded-lg shadow overflow-hidden">
              {webhooks.length === 0 ? (
                <div className="p-12 text-center">
                  <BoltIcon className="mx-auto h-16 w-16 text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No webhooks configured</h3>
                  <p className="text-gray-500">Set up webhooks to receive real-time updates</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Webhook
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Events
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          URL
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Last Delivery
                        </th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {webhooks.map((webhook) => (
                        <tr key={webhook.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4">
                            <div className="flex items-center">
                              <LinkIcon className="w-5 h-5 text-gray-400 mr-2" />
                              <div>
                                <div className="text-sm font-medium text-gray-900">
                                  {webhook.name}
                                </div>
                                {webhook.description && (
                                  <div className="text-sm text-gray-500">{webhook.description}</div>
                                )}
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <div className="flex flex-wrap gap-1">
                              {webhook.events?.map((event: string) => (
                                <span
                                  key={event}
                                  className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                                >
                                  {event}
                                </span>
                              ))}
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <div className="text-sm text-gray-900 truncate max-w-xs" title={webhook.url}>
                              {webhook.url}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              webhook.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                            }`}>
                              {webhook.is_active ? 'Active' : 'Inactive'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {webhook.last_triggered_at
                              ? new Date(webhook.last_triggered_at).toLocaleString()
                              : 'Never'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <button
                              onClick={() => handleTestWebhook(webhook.id)}
                              className="text-blue-600 hover:text-blue-900 mr-4"
                            >
                              Test
                            </button>
                            <button
                              onClick={() => toggleWebhook(webhook)}
                              className={webhook.is_active ? 'text-red-600 hover:text-red-900' : 'text-green-600 hover:text-green-900'}
                            >
                              {webhook.is_active ? 'Disable' : 'Enable'}
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
