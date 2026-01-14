'use client';

import React, { useState } from 'react';
import {
  Shield, Download, Trash2, AlertTriangle,
  X, Clock, Eye, Lock, Settings, UserCheck,
  Bell, Plus, ExternalLink,
  Info, CheckCircle2, XCircle
} from 'lucide-react';

// Types
interface Consent {
  id: number;
  type: string;
  category: string;
  granted: boolean;
  date: string;
  can_withdraw: boolean;
}

interface ExportRequest {
  id: number;
  type: string;
  format: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  requested_at: string;
  completed_at?: string;
  file_url?: string;
}

interface DeletionRequest {
  id: number;
  type: string;
  status: 'pending' | 'approved' | 'rejected' | 'processing' | 'completed';
  requested_at: string;
  reviewed_at?: string;
  reason?: string;
}

interface BreachIncident {
  id: number;
  incident_id: string;
  title: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'identified' | 'investigating' | 'contained' | 'remediated' | 'closed';
  discovered_at: string;
  affected_users: number;
  authority_notified: boolean;
  users_notified: boolean;
}

interface PrivacySettings {
  allow_data_processing: boolean;
  allow_marketing_emails: boolean;
  allow_analytics: boolean;
  allow_third_party_sharing: boolean;
  allow_profiling: boolean;
  data_retention_preference: 'minimum' | 'standard' | 'extended';
}

export default function GDPRCompliancePage() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'consents' | 'export' | 'deletion' | 'breaches'>('dashboard');

  // Mock data
  const consents: Consent[] = [
    {
      id: 1,
      type: 'Essential Services',
      category: 'essential',
      granted: true,
      date: '2024-01-15',
      can_withdraw: false
    },
    {
      id: 2,
      type: 'Marketing Communications',
      category: 'marketing',
      granted: false,
      date: '2024-01-15',
      can_withdraw: true
    },
    {
      id: 3,
      type: 'Analytics & Performance',
      category: 'analytics',
      granted: true,
      date: '2024-01-15',
      can_withdraw: true
    },
    {
      id: 4,
      type: 'Third-Party Integrations',
      category: 'third_party',
      granted: true,
      date: '2024-02-01',
      can_withdraw: true
    }
  ];

  const exportRequests: ExportRequest[] = [
    {
      id: 1,
      type: 'Full Data Export',
      format: 'JSON',
      status: 'completed',
      requested_at: '2024-03-10',
      completed_at: '2024-03-10',
      file_url: '#'
    },
    {
      id: 2,
      type: 'Contact Data',
      format: 'CSV',
      status: 'processing',
      requested_at: '2024-03-15'
    }
  ];

  const deletionRequests: DeletionRequest[] = [
    {
      id: 1,
      type: 'Specific Data Deletion',
      status: 'completed',
      requested_at: '2024-02-20',
      reviewed_at: '2024-02-21',
      reason: 'No longer using marketing features'
    }
  ];

  const breaches: BreachIncident[] = [
    {
      id: 1,
      incident_id: 'BR-2024-001',
      title: 'Unauthorized API Access Attempt',
      severity: 'medium',
      status: 'remediated',
      discovered_at: '2024-03-01',
      affected_users: 0,
      authority_notified: false,
      users_notified: false
    },
    {
      id: 2,
      incident_id: 'BR-2024-002',
      title: 'Database Configuration Error',
      severity: 'low',
      status: 'closed',
      discovered_at: '2024-02-15',
      affected_users: 5,
      authority_notified: false,
      users_notified: true
    }
  ];

  const [privacySettings, setPrivacySettings] = useState<PrivacySettings>({
    allow_data_processing: true,
    allow_marketing_emails: false,
    allow_analytics: true,
    allow_third_party_sharing: false,
    allow_profiling: false,
    data_retention_preference: 'standard'
  });

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
      case 'remediated':
      case 'closed':
      case 'approved': return 'bg-green-100 text-green-800';
      case 'processing':
      case 'investigating':
      case 'contained': return 'bg-blue-100 text-blue-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'failed':
      case 'rejected': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'essential': return <Lock className="w-4 h-4" />;
      case 'marketing': return <Bell className="w-4 h-4" />;
      case 'analytics': return <Eye className="w-4 h-4" />;
      case 'third_party': return <ExternalLink className="w-4 h-4" />;
      default: return <Settings className="w-4 h-4" />;
    }
  };

  return (
    <div className="min-h-screen bg-linear-to-br from-slate-50 via-purple-50 to-indigo-50 p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center mb-2">
          <Shield className="w-8 h-8 text-purple-600 mr-3" />
          <h1 className="text-4xl font-bold text-gray-900">
            GDPR Compliance Center
          </h1>
        </div>
        <p className="text-gray-600">
          Manage your data privacy, consents, and compliance requirements
        </p>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-sm mb-6">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6" aria-label="Tabs">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'dashboard'
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Shield className="w-5 h-5 inline-block mr-2" />
              Dashboard
            </button>
            <button
              onClick={() => setActiveTab('consents')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'consents'
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <UserCheck className="w-5 h-5 inline-block mr-2" />
              Consent Management
            </button>
            <button
              onClick={() => setActiveTab('export')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'export'
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Download className="w-5 h-5 inline-block mr-2" />
              Data Export
            </button>
            <button
              onClick={() => setActiveTab('deletion')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'deletion'
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Trash2 className="w-5 h-5 inline-block mr-2" />
              Data Deletion
            </button>
            <button
              onClick={() => setActiveTab('breaches')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'breaches'
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <AlertTriangle className="w-5 h-5 inline-block mr-2" />
              Security Incidents
            </button>
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {/* Dashboard Tab */}
          {activeTab === 'dashboard' && (
            <div className="space-y-6">
              {/* Stats Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-linear-to-br from-green-50 to-green-100 rounded-lg p-6 border border-green-200">
                  <div className="flex items-center justify-between mb-2">
                    <CheckCircle2 className="w-8 h-8 text-green-600" />
                    <span className="text-2xl font-bold text-green-900">{consents.filter(c => c.granted).length}/{consents.length}</span>
                  </div>
                  <p className="text-sm font-medium text-green-900">Active Consents</p>
                  <p className="text-xs text-green-700 mt-1">Consents granted</p>
                </div>

                <div className="bg-linear-to-br from-blue-50 to-blue-100 rounded-lg p-6 border border-blue-200">
                  <div className="flex items-center justify-between mb-2">
                    <Download className="w-8 h-8 text-blue-600" />
                    <span className="text-2xl font-bold text-blue-900">{exportRequests.length}</span>
                  </div>
                  <p className="text-sm font-medium text-blue-900">Export Requests</p>
                  <p className="text-xs text-blue-700 mt-1">Data exports made</p>
                </div>

                <div className="bg-linear-to-br from-purple-50 to-purple-100 rounded-lg p-6 border border-purple-200">
                  <div className="flex items-center justify-between mb-2">
                    <Trash2 className="w-8 h-8 text-purple-600" />
                    <span className="text-2xl font-bold text-purple-900">{deletionRequests.length}</span>
                  </div>
                  <p className="text-sm font-medium text-purple-900">Deletion Requests</p>
                  <p className="text-xs text-purple-700 mt-1">Data deletions</p>
                </div>

                <div className="bg-linear-to-br from-orange-50 to-orange-100 rounded-lg p-6 border border-orange-200">
                  <div className="flex items-center justify-between mb-2">
                    <AlertTriangle className="w-8 h-8 text-orange-600" />
                    <span className="text-2xl font-bold text-orange-900">{breaches.length}</span>
                  </div>
                  <p className="text-sm font-medium text-orange-900">Security Incidents</p>
                  <p className="text-xs text-orange-700 mt-1">Tracked incidents</p>
                </div>
              </div>

              {/* Privacy Settings */}
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Settings className="w-5 h-5 mr-2 text-purple-600" />
                  Privacy Preferences
                </h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">Data Processing</p>
                      <p className="text-sm text-gray-600">Allow processing of personal data</p>
                    </div>
                    <button
                      onClick={() => setPrivacySettings({...privacySettings, allow_data_processing: !privacySettings.allow_data_processing})}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        privacySettings.allow_data_processing ? 'bg-purple-600' : 'bg-gray-300'
                      }`}
                    >
                      <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        privacySettings.allow_data_processing ? 'translate-x-6' : 'translate-x-1'
                      }`} />
                    </button>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">Marketing Emails</p>
                      <p className="text-sm text-gray-600">Receive promotional communications</p>
                    </div>
                    <button
                      onClick={() => setPrivacySettings({...privacySettings, allow_marketing_emails: !privacySettings.allow_marketing_emails})}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        privacySettings.allow_marketing_emails ? 'bg-purple-600' : 'bg-gray-300'
                      }`}
                    >
                      <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        privacySettings.allow_marketing_emails ? 'translate-x-6' : 'translate-x-1'
                      }`} />
                    </button>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">Analytics</p>
                      <p className="text-sm text-gray-600">Help improve our services</p>
                    </div>
                    <button
                      onClick={() => setPrivacySettings({...privacySettings, allow_analytics: !privacySettings.allow_analytics})}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        privacySettings.allow_analytics ? 'bg-purple-600' : 'bg-gray-300'
                      }`}
                    >
                      <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        privacySettings.allow_analytics ? 'translate-x-6' : 'translate-x-1'
                      }`} />
                    </button>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">Third-Party Sharing</p>
                      <p className="text-sm text-gray-600">Share data with partners</p>
                    </div>
                    <button
                      onClick={() => setPrivacySettings({...privacySettings, allow_third_party_sharing: !privacySettings.allow_third_party_sharing})}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        privacySettings.allow_third_party_sharing ? 'bg-purple-600' : 'bg-gray-300'
                      }`}
                    >
                      <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        privacySettings.allow_third_party_sharing ? 'translate-x-6' : 'translate-x-1'
                      }`} />
                    </button>
                  </div>

                  <div className="pt-4 border-t border-gray-200">
                    <button className="w-full bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors">
                      Save Privacy Preferences
                    </button>
                  </div>
                </div>
              </div>

              {/* Recent Activity */}
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Clock className="w-5 h-5 mr-2 text-purple-600" />
                  Recent Activity
                </h3>
                <div className="space-y-3">
                  <div className="flex items-start">
                    <div className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-3"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">Consent granted for Analytics</p>
                      <p className="text-xs text-gray-500">2 hours ago</p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">Data export completed</p>
                      <p className="text-xs text-gray-500">1 day ago</p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <div className="w-2 h-2 bg-purple-500 rounded-full mt-2 mr-3"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">Privacy preferences updated</p>
                      <p className="text-xs text-gray-500">3 days ago</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Consent Management Tab */}
          {activeTab === 'consents' && (
            <div>
              <div className="mb-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Your Consents</h3>
                <p className="text-gray-600">Manage your consent preferences for data processing</p>
              </div>

              <div className="space-y-4">
                {consents.map((consent) => (
                  <div key={consent.id} className="bg-white border border-gray-200 rounded-lg p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center mb-2">
                          <div className={`p-2 rounded-lg mr-3 ${
                            consent.category === 'essential' ? 'bg-red-100' :
                            consent.category === 'marketing' ? 'bg-yellow-100' :
                            consent.category === 'analytics' ? 'bg-blue-100' :
                            'bg-purple-100'
                          }`}>
                            {getCategoryIcon(consent.category)}
                          </div>
                          <div>
                            <h4 className="text-lg font-semibold text-gray-900">{consent.type}</h4>
                            <p className="text-sm text-gray-600 capitalize">{consent.category}</p>
                          </div>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">
                          Granted on {new Date(consent.date).toLocaleDateString()}
                        </p>
                        {!consent.can_withdraw && (
                          <div className="flex items-center text-sm text-amber-600 bg-amber-50 rounded px-3 py-2 inline-flex">
                            <Info className="w-4 h-4 mr-2" />
                            Required for essential services
                          </div>
                        )}
                      </div>
                      <div className="flex flex-col items-end space-y-3">
                        <span className={`text-sm font-medium px-3 py-1 rounded-full ${
                          consent.granted ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {consent.granted ? 'Granted' : 'Not Granted'}
                        </span>
                        {consent.can_withdraw && consent.granted && (
                          <button className="text-red-600 hover:text-red-700 text-sm font-medium flex items-center">
                            <X className="w-4 h-4 mr-1" />
                            Withdraw Consent
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Data Export Tab */}
          {activeTab === 'export' && (
            <div>
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Data Export Requests</h3>
                  <p className="text-gray-600">Download your personal data in various formats</p>
                </div>
                <button className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors flex items-center">
                  <Plus className="w-5 h-5 mr-2" />
                  New Export Request
                </button>
              </div>

              <div className="space-y-4">
                {exportRequests.map((request) => (
                  <div key={request.id} className="bg-white border border-gray-200 rounded-lg p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center mb-2">
                          <Download className="w-5 h-5 text-purple-600 mr-3" />
                          <h4 className="text-lg font-semibold text-gray-900">{request.type}</h4>
                        </div>
                        <div className="grid grid-cols-2 gap-4 mb-3">
                          <div>
                            <p className="text-xs text-gray-500">Format</p>
                            <p className="text-sm font-medium text-gray-900">{request.format}</p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-500">Requested</p>
                            <p className="text-sm font-medium text-gray-900">
                              {new Date(request.requested_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        {request.completed_at && (
                          <p className="text-sm text-gray-600">
                            Completed on {new Date(request.completed_at).toLocaleDateString()}
                          </p>
                        )}
                      </div>
                      <div className="flex flex-col items-end space-y-3">
                        <span className={`text-sm font-medium px-3 py-1 rounded-full ${getStatusColor(request.status)}`}>
                          {request.status.charAt(0).toUpperCase() + request.status.slice(1)}
                        </span>
                        {request.status === 'completed' && request.file_url && (
                          <button className="text-purple-600 hover:text-purple-700 text-sm font-medium flex items-center">
                            <Download className="w-4 h-4 mr-1" />
                            Download File
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Export Info */}
              <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex">
                  <Info className="w-5 h-5 text-blue-600 mt-0.5 mr-3 shrink-0" />
                  <div>
                    <p className="text-sm font-medium text-blue-900 mb-1">About Data Exports</p>
                    <p className="text-sm text-blue-700">
                      Your data will be exported in the requested format and made available for download for 30 days.
                      Export requests typically complete within 24-48 hours.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Data Deletion Tab */}
          {activeTab === 'deletion' && (
            <div>
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Data Deletion Requests</h3>
                  <p className="text-gray-600">Request deletion of your personal data (Right to be Forgotten)</p>
                </div>
                <button className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors flex items-center">
                  <Trash2 className="w-5 h-5 mr-2" />
                  Request Data Deletion
                </button>
              </div>

              {deletionRequests.length > 0 ? (
                <div className="space-y-4">
                  {deletionRequests.map((request) => (
                    <div key={request.id} className="bg-white border border-gray-200 rounded-lg p-6">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center mb-2">
                            <Trash2 className="w-5 h-5 text-red-600 mr-3" />
                            <h4 className="text-lg font-semibold text-gray-900">{request.type}</h4>
                          </div>
                          <div className="grid grid-cols-2 gap-4 mb-3">
                            <div>
                              <p className="text-xs text-gray-500">Requested</p>
                              <p className="text-sm font-medium text-gray-900">
                                {new Date(request.requested_at).toLocaleDateString()}
                              </p>
                            </div>
                            {request.reviewed_at && (
                              <div>
                                <p className="text-xs text-gray-500">Reviewed</p>
                                <p className="text-sm font-medium text-gray-900">
                                  {new Date(request.reviewed_at).toLocaleDateString()}
                                </p>
                              </div>
                            )}
                          </div>
                          {request.reason && (
                            <p className="text-sm text-gray-600">Reason: {request.reason}</p>
                          )}
                        </div>
                        <span className={`text-sm font-medium px-3 py-1 rounded-full ${getStatusColor(request.status)}`}>
                          {request.status.charAt(0).toUpperCase() + request.status.slice(1)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 bg-white border border-gray-200 rounded-lg">
                  <Trash2 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">No deletion requests</p>
                </div>
              )}

              {/* Warning */}
              <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex">
                  <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5 mr-3 shrink-0" />
                  <div>
                    <p className="text-sm font-medium text-red-900 mb-1">Warning</p>
                    <p className="text-sm text-red-700">
                      Data deletion is permanent and cannot be undone. We recommend exporting your data before requesting deletion.
                      Some data may be retained for legal or compliance purposes.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Security Breaches Tab */}
          {activeTab === 'breaches' && (
            <div>
              <div className="mb-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Security Incident History</h3>
                <p className="text-gray-600">Transparency report of security incidents and breaches</p>
              </div>

              <div className="space-y-4">
                {breaches.map((breach) => (
                  <div key={breach.id} className="bg-white border border-gray-200 rounded-lg p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <div className="flex items-center mb-2">
                          <span className={`text-xs font-medium px-2 py-1 rounded mr-3 ${getSeverityColor(breach.severity)}`}>
                            {breach.severity.toUpperCase()}
                          </span>
                          <span className="text-sm text-gray-600">{breach.incident_id}</span>
                        </div>
                        <h4 className="text-lg font-semibold text-gray-900 mb-1">{breach.title}</h4>
                        <p className="text-sm text-gray-600">
                          Discovered on {new Date(breach.discovered_at).toLocaleDateString()}
                        </p>
                      </div>
                      <span className={`text-sm font-medium px-3 py-1 rounded-full ${getStatusColor(breach.status)}`}>
                        {breach.status.charAt(0).toUpperCase() + breach.status.slice(1)}
                      </span>
                    </div>

                    <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gray-100">
                      <div className="text-center">
                        <p className="text-2xl font-bold text-gray-900">{breach.affected_users}</p>
                        <p className="text-xs text-gray-500">Affected Users</p>
                      </div>
                      <div className="text-center">
                        <div className="flex items-center justify-center mb-1">
                          {breach.authority_notified ? (
                            <CheckCircle2 className="w-5 h-5 text-green-600" />
                          ) : (
                            <XCircle className="w-5 h-5 text-gray-400" />
                          )}
                        </div>
                        <p className="text-xs text-gray-500">Authority Notified</p>
                      </div>
                      <div className="text-center">
                        <div className="flex items-center justify-center mb-1">
                          {breach.users_notified ? (
                            <CheckCircle2 className="w-5 h-5 text-green-600" />
                          ) : (
                            <XCircle className="w-5 h-5 text-gray-400" />
                          )}
                        </div>
                        <p className="text-xs text-gray-500">Users Notified</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Info */}
              <div className="mt-6 bg-purple-50 border border-purple-200 rounded-lg p-4">
                <div className="flex">
                  <Shield className="w-5 h-5 text-purple-600 mt-0.5 mr-3 shrink-0" />
                  <div>
                    <p className="text-sm font-medium text-purple-900 mb-1">Your Data is Protected</p>
                    <p className="text-sm text-purple-700">
                      We take security seriously and are transparent about any incidents. All breaches are investigated,
                      remediated, and reported according to GDPR requirements.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

