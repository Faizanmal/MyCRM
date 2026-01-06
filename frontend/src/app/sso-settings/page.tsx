'use client';

import { useState, useEffect, useCallback } from 'react';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { 
  ShieldCheckIcon, 
  KeyIcon, 
  UserIcon,
  PlusIcon,
  CheckCircleIcon,
  XCircleIcon,
  ArrowPathIcon,
  ChartBarIcon,
  LinkIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';

// Types
interface SSOProvider {
  id: string;
  provider_name: string;
  provider_type: string;
  status: string;
  total_logins: number;
  last_used_at?: string;
  auto_create_users: boolean;
  auto_update_user_info: boolean;
  default_role: string;
}

interface SSOSession {
  id: string;
  user_email: string;
  provider_name: string;
  ip_address?: string;
  created_at: string;
  is_active: boolean;
}

interface SSOAttempt {
  id: string;
  email: string;
  provider_name: string;
  status: string;
  ip_address?: string;
  created_at: string;
  error_message?: string;
}

interface ProviderStatistics {
  total_logins: number;
  successful_logins: number;
  failed_logins: number;
  unique_users: number;
  avg_logins_per_day: number;
}

interface CreateProviderData {
  provider_type: string;
  provider_name: string;
  status?: string;
  client_id?: string;
  client_secret?: string;
  authorization_url?: string;
  token_url?: string;
  user_info_url?: string;
  scope?: string;
  entity_id?: string;
  sso_url?: string;
  x509_cert?: string;
  auto_create_users: boolean;
  auto_update_user_info: boolean;
  default_role: string;
}

interface AvailableType {
  value: string;
  label: string;
  type: string;
}

// API Service
const ssoAPI = {
  // Providers
  getProviders: (): Promise<SSOProvider[]> => fetch('/api/v1/sso/providers/').then(r => r.json()),
  getProvider: (id: string): Promise<SSOProvider> => fetch(`/api/v1/sso/providers/${id}/`).then(r => r.json()),
  createProvider: (data: CreateProviderData): Promise<SSOProvider> => fetch('/api/v1/sso/providers/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(r => r.json()),
  updateProvider: (id: string, data: Partial<CreateProviderData>): Promise<SSOProvider> => fetch(`/api/v1/sso/providers/${id}/`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(r => r.json()),
  testConnection: (id: string): Promise<{ message: string; authorization_url?: string }> => fetch(`/api/v1/sso/providers/${id}/test_connection/`, {
    method: 'POST'
  }).then(r => r.json()),
  activate: (id: string): Promise<void> => fetch(`/api/v1/sso/providers/${id}/activate/`, {
    method: 'POST'
  }).then(r => r.json()),
  deactivate: (id: string): Promise<void> => fetch(`/api/v1/sso/providers/${id}/deactivate/`, {
    method: 'POST'
  }).then(r => r.json()),
  getStatistics: (id: string): Promise<ProviderStatistics> => fetch(`/api/v1/sso/providers/${id}/statistics/`).then(r => r.json()),
  getAvailableTypes: (): Promise<AvailableType[]> => fetch('/api/v1/sso/providers/available_types/').then(r => r.json()),

  // Sessions
  getSessions: (): Promise<SSOSession[]> => fetch('/api/v1/sso/sessions/').then(r => r.json()),
  endSession: (id: string): Promise<void> => fetch(`/api/v1/sso/sessions/${id}/end_session/`, {
    method: 'POST'
  }).then(r => r.json()),

  // Login Attempts
  getAttempts: (providerId?: string): Promise<SSOAttempt[]> => {
    const url = providerId 
      ? `/api/v1/sso/attempts/?provider=${providerId}`
      : '/api/v1/sso/attempts/';
    return fetch(url).then(r => r.json());
  },
};

export default function SSOSettingsPage() {
  const [activeTab, setActiveTab] = useState<'providers' | 'sessions' | 'audit'>('providers');
  const [providers, setProviders] = useState<SSOProvider[]>([]);
  const [sessions, setSessions] = useState<SSOSession[]>([]);
  const [attempts, setAttempts] = useState<SSOAttempt[]>([]);
  const [availableTypes, setAvailableTypes] = useState<AvailableType[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState<SSOProvider | null>(null);
  const [showStatsModal, setShowStatsModal] = useState(false);
  const [providerStats, setProviderStats] = useState<ProviderStatistics | null>(null);
  
  // Form state
  const [formData, setFormData] = useState<CreateProviderData>({
    provider_type: 'oauth2_google',
    provider_name: '',
    client_id: '',
    client_secret: '',
    authorization_url: '',
    token_url: '',
    user_info_url: '',
    scope: 'openid profile email',
    entity_id: '',
    sso_url: '',
    x509_cert: '',
    auto_create_users: true,
    auto_update_user_info: true,
    default_role: 'member',
  });

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const [providersData, sessionsData, attemptsData] = await Promise.all([
        ssoAPI.getProviders(),
        ssoAPI.getSessions(),
        ssoAPI.getAttempts()
      ]);
      
      setProviders(providersData);
      setSessions(sessionsData);
      setAttempts(attemptsData);
    } catch (error) {
      console.error('Failed to load SSO data:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadAvailableTypes = useCallback(async () => {
    try {
      const types = await ssoAPI.getAvailableTypes();
      setAvailableTypes(types);
    } catch (error) {
      console.error('Failed to load available types:', error);
    }
  }, []);

  useEffect(() => {
    loadData();
    loadAvailableTypes();
  }, [loadData, loadAvailableTypes]);

  const handleCreateProvider = async () => {
    try {
      await ssoAPI.createProvider(formData);
      setShowCreateModal(false);
      resetForm();
      loadData();
    } catch (error) {
      console.error('Failed to create provider:', error);
    }
  };

  const handleTestConnection = async (id: string) => {
    try {
      const result = await ssoAPI.testConnection(id);
      if (result.authorization_url) {
        // Open OAuth2 authorization URL in new window
        window.open(result.authorization_url, '_blank');
      }
      alert(result.message);
    } catch (error) {
      console.error('Connection test failed:', error);
      alert('Connection test failed. Check configuration.');
    }
  };

  const handleActivateProvider = async (id: string) => {
    try {
      await ssoAPI.activate(id);
      loadData();
    } catch (error) {
      console.error('Failed to activate provider:', error);
    }
  };

  const handleDeactivateProvider = async (id: string) => {
    if (!confirm('Are you sure? This will end all active SSO sessions.')) return;
    
    try {
      await ssoAPI.deactivate(id);
      loadData();
    } catch (error) {
      console.error('Failed to deactivate provider:', error);
    }
  };

  const handleEndSession = async (id: string) => {
    if (!confirm('End this SSO session?')) return;
    
    try {
      await ssoAPI.endSession(id);
      loadData();
    } catch (error) {
      console.error('Failed to end session:', error);
    }
  };

  const handleViewStatistics = async (provider: SSOProvider) => {
    try {
      const stats = await ssoAPI.getStatistics(provider.id);
      setProviderStats(stats);
      setSelectedProvider(provider);
      setShowStatsModal(true);
    } catch (error) {
      console.error('Failed to load statistics:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      provider_type: 'oauth2_google',
      provider_name: '',
      status: 'testing',
      client_id: '',
      client_secret: '',
      authorization_url: '',
      token_url: '',
      user_info_url: '',
      scope: 'openid profile email',
      entity_id: '',
      sso_url: '',
      x509_cert: '',
      auto_create_users: true,
      auto_update_user_info: true,
      default_role: 'member',
    });
  };
  const getStatusBadge = (status: string): string => {
    const styles: Record<string, string> = {
      active: 'bg-green-100 text-green-800',
      inactive: 'bg-gray-100 text-gray-800',
      testing: 'bg-yellow-100 text-yellow-800',
    };
    return styles[status] || 'bg-gray-100 text-gray-800';
  };

  const getProviderIcon = (type: string) => {
    if (type.includes('google')) return '🔍 Google';
    if (type.includes('microsoft')) return '🪟 Microsoft';
    if (type.includes('github')) return '🐙 GitHub';
    if (type.includes('okta')) return '🔐 Okta';
    if (type.includes('azure')) return '☁️ Azure';
    if (type.includes('onelogin')) return '🔑 OneLogin';
    return '🔒 Custom';
  };

  const isOAuth2 = formData.provider_type.startsWith('oauth2_');
  const isSAML = formData.provider_type.startsWith('saml_');

  if (loading) {
    return (
      <MainLayout>
        <ProtectedRoute>
          <div className="flex items-center justify-center h-64">
            <ArrowPathIcon className="h-8 w-8 animate-spin text-blue-600" />
          </div>
        </ProtectedRoute>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <ProtectedRoute>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">SSO Configuration</h1>
                <p className="mt-2 text-gray-600">
                  Configure Single Sign-On providers for your organization
                </p>
              </div>
              <button
                onClick={() => setShowCreateModal(true)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <PlusIcon className="h-5 w-5 inline mr-2" />
                Add Provider
              </button>
            </div>
          </div>

          {/* Info Banner */}
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
            <div className="flex items-start">
              <ShieldCheckIcon className="h-6 w-6 text-blue-600 mr-3 shrink-0 mt-0.5" />
              <div>
                <h3 className="text-sm font-medium text-blue-900">Secure Authentication</h3>
                <p className="text-sm text-blue-700 mt-1">
                  SSO providers allow your team to sign in securely using existing corporate credentials.
                  Supports OAuth2 (Google, Microsoft, GitHub) and SAML 2.0 (Okta, OneLogin, Azure AD).
                </p>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200 mb-6">
            <nav className="-mb-px flex space-x-8">
              {[
                { id: 'providers', name: 'Providers', icon: KeyIcon, count: providers.length },
                { id: 'sessions', name: 'Active Sessions', icon: UserIcon, count: sessions.filter(s => s.is_active).length },
                { id: 'audit', name: 'Audit Log', icon: DocumentTextIcon, count: attempts.length }
              ].map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as 'providers' | 'sessions' | 'audit')}
                  className={`
                    flex items-center py-4 px-1 border-b-2 font-medium text-sm
                    ${activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 hover:border-gray-300'}
                  `}
                >
                  <tab.icon className="h-5 w-5 mr-2" />
                  {tab.name}
                  <span className="ml-2 px-2 py-0.5 rounded-full bg-gray-200 text-xs">
                    {tab.count}
                  </span>
                </button>
              ))}
            </nav>
          </div>

          {/* Providers Tab */}
          {activeTab === 'providers' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {providers.length === 0 ? (
                <div className="col-span-2 text-center py-12 bg-gray-50 rounded-xl">
                  <KeyIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No SSO Providers</h3>
                  <p className="text-gray-600 mb-4">Get started by adding your first SSO provider</p>
                  <button
                    onClick={() => setShowCreateModal(true)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Add Provider
                  </button>
                </div>
              ) : (
                providers.map(provider => (
                  <div key={provider.id} className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="text-3xl">{getProviderIcon(provider.provider_type).split(' ')[0]}</div>
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">{provider.provider_name}</h3>
                          <p className="text-sm text-gray-500">{getProviderIcon(provider.provider_type).split(' ')[1]}</p>
                        </div>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusBadge(provider.status)}`}>
                        {provider.status}
                      </span>
                    </div>

                    <div className="space-y-2 mb-4">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Total Logins:</span>
                        <span className="font-medium text-gray-900">{provider.total_logins}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Last Used:</span>
                        <span className="font-medium text-gray-900">
                          {provider.last_used_at 
                            ? new Date(provider.last_used_at).toLocaleDateString()
                            : 'Never'}
                        </span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Auto Create Users:</span>
                        <span className="font-medium text-gray-900">
                          {provider.auto_create_users ? 'Yes' : 'No'}
                        </span>
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-2">
                      <button
                        onClick={() => handleTestConnection(provider.id)}
                        className="flex-1 px-3 py-2 bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 text-sm"
                      >
                        <LinkIcon className="h-4 w-4 inline mr-1" />
                        Test
                      </button>
                      <button
                        onClick={() => handleViewStatistics(provider)}
                        className="flex-1 px-3 py-2 bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 text-sm"
                      >
                        <ChartBarIcon className="h-4 w-4 inline mr-1" />
                        Stats
                      </button>
                      {provider.status === 'active' ? (
                        <button
                          onClick={() => handleDeactivateProvider(provider.id)}
                          className="flex-1 px-3 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 text-sm"
                        >
                          <XCircleIcon className="h-4 w-4 inline mr-1" />
                          Deactivate
                        </button>
                      ) : (
                        <button
                          onClick={() => handleActivateProvider(provider.id)}
                          className="flex-1 px-3 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 text-sm"
                        >
                          <CheckCircleIcon className="h-4 w-4 inline mr-1" />
                          Activate
                        </button>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {/* Sessions Tab */}
          {activeTab === 'sessions' && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Provider</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">IP Address</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Started</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {sessions.map(session => (
                    <tr key={session.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {session.user_email}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {session.provider_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {session.ip_address || 'Unknown'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(session.created_at).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                          session.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {session.is_active ? 'Active' : 'Ended'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                        {session.is_active && (
                          <button
                            onClick={() => handleEndSession(session.id)}
                            className="text-red-600 hover:text-red-800"
                          >
                            End Session
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Audit Log Tab */}
          {activeTab === 'audit' && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Provider</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">IP Address</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Timestamp</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Error</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {attempts.map(attempt => (
                    <tr key={attempt.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {attempt.email}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {attempt.provider_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                          attempt.status === 'success' ? 'bg-green-100 text-green-800' :
                          attempt.status === 'failed' ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {attempt.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {attempt.ip_address || 'Unknown'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(attempt.created_at).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 text-sm text-red-600">
                        {attempt.error_message || '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Create Provider Modal */}
          {showCreateModal && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto">
              <div className="bg-white rounded-xl p-6 max-w-2xl w-full mx-4 my-8">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Add SSO Provider</h3>
                
                <div className="space-y-4 max-h-[70vh] overflow-y-auto">
                  {/* Provider Type */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Provider Type
                    </label>
                    <select
                      value={formData.provider_type}
                      onChange={(e) => setFormData({...formData, provider_type: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    >
                      {availableTypes.map(type => (
                        <option key={type.value} value={type.value}>
                          {type.label} ({type.type.toUpperCase()})
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Provider Name */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Provider Name
                    </label>
                    <input
                      type="text"
                      value={formData.provider_name}
                      onChange={(e) => setFormData({...formData, provider_name: e.target.value})}
                      placeholder="My Company SSO"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  {/* OAuth2 Fields */}
                  {isOAuth2 && (
                    <>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Client ID
                        </label>
                        <input
                          type="text"
                          value={formData.client_id}
                          onChange={(e) => setFormData({...formData, client_id: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Client Secret
                        </label>
                        <input
                          type="password"
                          value={formData.client_secret}
                          onChange={(e) => setFormData({...formData, client_secret: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Authorization URL
                        </label>
                        <input
                          type="url"
                          value={formData.authorization_url}
                          onChange={(e) => setFormData({...formData, authorization_url: e.target.value})}
                          placeholder="https://accounts.google.com/o/oauth2/v2/auth"
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Token URL
                        </label>
                        <input
                          type="url"
                          value={formData.token_url}
                          onChange={(e) => setFormData({...formData, token_url: e.target.value})}
                          placeholder="https://oauth2.googleapis.com/token"
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          User Info URL
                        </label>
                        <input
                          type="url"
                          value={formData.user_info_url}
                          onChange={(e) => setFormData({...formData, user_info_url: e.target.value})}
                          placeholder="https://www.googleapis.com/oauth2/v1/userinfo"
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    </>
                  )}

                  {/* SAML Fields */}
                  {isSAML && (
                    <>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Entity ID (SP)
                        </label>
                        <input
                          type="text"
                          value={formData.entity_id}
                          onChange={(e) => setFormData({...formData, entity_id: e.target.value})}
                          placeholder="https://mycrm.com/saml/metadata"
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          SSO URL (IdP)
                        </label>
                        <input
                          type="url"
                          value={formData.sso_url}
                          onChange={(e) => setFormData({...formData, sso_url: e.target.value})}
                          placeholder="https://idp.example.com/sso/saml"
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          X.509 Certificate
                        </label>
                        <textarea
                          value={formData.x509_cert}
                          onChange={(e) => setFormData({...formData, x509_cert: e.target.value})}
                          rows={4}
                          placeholder="-----BEGIN CERTIFICATE-----&#10;...&#10;-----END CERTIFICATE-----"
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                        />
                      </div>
                    </>
                  )}

                  {/* Common Settings */}
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="auto_create"
                      checked={formData.auto_create_users}
                      onChange={(e) => setFormData({...formData, auto_create_users: e.target.checked})}
                      className="rounded border-gray-300"
                    />
                    <label htmlFor="auto_create" className="text-sm text-gray-700">
                      Automatically create users on first login
                    </label>
                  </div>

                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="auto_update"
                      checked={formData.auto_update_user_info}
                      onChange={(e) => setFormData({...formData, auto_update_user_info: e.target.checked})}
                      className="rounded border-gray-300"
                    />
                    <label htmlFor="auto_update" className="text-sm text-gray-700">
                      Update user info from SSO on each login
                    </label>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Default Role for New Users
                    </label>
                    <select
                      value={formData.default_role}
                      onChange={(e) => setFormData({...formData, default_role: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="viewer">Viewer</option>
                      <option value="member">Member</option>
                      <option value="manager">Manager</option>
                      <option value="admin">Admin</option>
                    </select>
                  </div>
                </div>

                <div className="flex space-x-3 mt-6">
                  <button
                    onClick={handleCreateProvider}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Create Provider
                  </button>
                  <button
                    onClick={() => {
                      setShowCreateModal(false);
                      resetForm();
                    }}
                    className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Statistics Modal */}
          {showStatsModal && providerStats && selectedProvider && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white rounded-xl p-6 max-w-2xl w-full mx-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Statistics: {selectedProvider.provider_name}
                </h3>
                
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="bg-blue-50 rounded-lg p-4">
                    <p className="text-sm text-gray-600">Total Logins</p>
                    <p className="text-2xl font-bold text-blue-600">{providerStats.total_logins}</p>
                  </div>
                  <div className="bg-green-50 rounded-lg p-4">
                    <p className="text-sm text-gray-600">Successful</p>
                    <p className="text-2xl font-bold text-green-600">{providerStats.successful_logins}</p>
                  </div>
                  <div className="bg-red-50 rounded-lg p-4">
                    <p className="text-sm text-gray-600">Failed</p>
                    <p className="text-2xl font-bold text-red-600">{providerStats.failed_logins}</p>
                  </div>
                  <div className="bg-purple-50 rounded-lg p-4">
                    <p className="text-sm text-gray-600">Unique Users</p>
                    <p className="text-2xl font-bold text-purple-600">{providerStats.unique_users}</p>
                  </div>
                </div>

                <div className="mb-4">
                  <p className="text-sm text-gray-600">Average Logins/Day</p>
                  <p className="text-lg font-semibold text-gray-900">{providerStats.avg_logins_per_day}</p>
                </div>

                <button
                  onClick={() => setShowStatsModal(false)}
                  className="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                >
                  Close
                </button>
              </div>
            </div>
          )}
        </div>
      </ProtectedRoute>
    </MainLayout>
  );
}
