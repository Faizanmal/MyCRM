'use client';

import { useState, useEffect, useCallback } from 'react';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { 
  BuildingOfficeIcon, 
  UserGroupIcon, 
  EnvelopeIcon,
  CheckCircleIcon,
  XCircleIcon,
  ArrowPathIcon,
  ChartBarIcon,
  CogIcon,
  UserPlusIcon
} from '@heroicons/react/24/outline';

// Types
interface Organization {
  id: string;
  name: string;
  description?: string;
  plan: string;
  member_count: number;
  domain?: string;
}

interface Member {
  id: string;
  user_name: string;
  user_email: string;
  role: string;
  is_active: boolean;
  joined_at: string;
}

interface Invitation {
  id: string;
  email: string;
  role: string;
  status: string;
  sent_at: string;
  expires_at: string;
}

interface Statistics {
  total_members: number;
  active_members: number;
  pending_invitations: number;
  admin_count: number;
  role_distribution: Record<string, number>;
}

interface CreateOrganizationData {
  name: string;
  description?: string;
  domain?: string;
}

interface UpdateOrganizationData {
  name?: string;
  description?: string;
  domain?: string;
}

interface CreateInvitationData {
  organization: string;
  email: string;
  role: string;
}

// API Service
const multiTenantAPI = {
  // Organizations
  getOrganizations: (): Promise<Organization[]> => fetch('/api/v1/multi-tenant/organizations/').then(r => r.json()),
  getOrganization: (id: string): Promise<Organization> => fetch(`/api/v1/multi-tenant/organizations/${id}/`).then(r => r.json()),
  createOrganization: (data: CreateOrganizationData): Promise<Organization> => fetch('/api/v1/multi-tenant/organizations/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(r => r.json()),
  updateOrganization: (id: string, data: UpdateOrganizationData): Promise<Organization> => fetch(`/api/v1/multi-tenant/organizations/${id}/`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(r => r.json()),
  switchOrganization: (id: string): Promise<void> => fetch(`/api/v1/multi-tenant/organizations/${id}/switch/`, {
    method: 'POST'
  }).then(r => r.json()),
  getStatistics: (id: string): Promise<Statistics> => fetch(`/api/v1/multi-tenant/organizations/${id}/statistics/`).then(r => r.json()),
  upgradePlan: (id: string, plan: string): Promise<void> => fetch(`/api/v1/multi-tenant/organizations/${id}/upgrade_plan/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ plan })
  }).then(r => r.json()),

  // Members
  getMembers: (orgId?: string): Promise<Member[]> => {
    const url = orgId 
      ? `/api/v1/multi-tenant/members/?organization=${orgId}`
      : '/api/v1/multi-tenant/members/';
    return fetch(url).then(r => r.json());
  },
  updateMemberRole: (id: string, role: string): Promise<void> => fetch(`/api/v1/multi-tenant/members/${id}/update_role/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ role })
  }).then(r => r.json()),
  deactivateMember: (id: string): Promise<void> => fetch(`/api/v1/multi-tenant/members/${id}/deactivate/`, {
    method: 'POST'
  }).then(r => r.json()),

  // Invitations
  getInvitations: (orgId?: string): Promise<Invitation[]> => {
    const url = orgId 
      ? `/api/v1/multi-tenant/invitations/?organization=${orgId}`
      : '/api/v1/multi-tenant/invitations/';
    return fetch(url).then(r => r.json());
  },
  createInvitation: (data: CreateInvitationData): Promise<Invitation> => fetch('/api/v1/multi-tenant/invitations/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(r => r.json()),
  acceptInvitation: (id: string): Promise<void> => fetch(`/api/v1/multi-tenant/invitations/${id}/accept/`, {
    method: 'POST'
  }).then(r => r.json()),
  resendInvitation: (id: string): Promise<void> => fetch(`/api/v1/multi-tenant/invitations/${id}/resend/`, {
    method: 'POST'
  }).then(r => r.json()),
};

export default function OrganizationsPage() {
  const [activeTab, setActiveTab] = useState<'overview' | 'members' | 'invitations' | 'settings'>('overview');
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [currentOrg, setCurrentOrg] = useState<Organization | null>(null);
  const [members, setMembers] = useState<Member[]>([]);
  const [invitations, setInvitations] = useState<Invitation[]>([]);
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('member');

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const orgsData = await multiTenantAPI.getOrganizations();
      setOrganizations(orgsData);
      
      // Set first org as current
      if (orgsData.length > 0 && !currentOrg) {
        setCurrentOrg(orgsData[0]);
      }
    } catch (error) {
      console.error('Failed to load organizations:', error);
    } finally {
      setLoading(false);
    }
  }, [currentOrg]);

  const loadOrgData = useCallback(async () => {
    if (!currentOrg) return;
    
    try {
      const [membersData, invitationsData, statsData] = await Promise.all([
        multiTenantAPI.getMembers(currentOrg.id),
        multiTenantAPI.getInvitations(currentOrg.id),
        multiTenantAPI.getStatistics(currentOrg.id)
      ]);
      
      setMembers(membersData);
      setInvitations(invitationsData);
      setStatistics(statsData);
    } catch (error) {
      console.error('Failed to load organization data:', error);
    }
  }, [currentOrg]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    if (currentOrg) {
      loadOrgData();
    }
  }, [currentOrg, loadOrgData]);

  const handleSwitchOrg = async (orgId: string) => {
    try {
      await multiTenantAPI.switchOrganization(orgId);
      const org = organizations.find(o => o.id === orgId);
      if (org) {
        setCurrentOrg(org);
      }
    } catch (error) {
      console.error('Failed to switch organization:', error);
    }
  };

  const handleInviteMember = async () => {
    if (!inviteEmail || !currentOrg) return;
    
    try {
      await multiTenantAPI.createInvitation({
        organization: currentOrg.id,
        email: inviteEmail,
        role: inviteRole
      });
      
      setShowInviteModal(false);
      setInviteEmail('');
      setInviteRole('member');
      loadOrgData();
    } catch (error) {
      console.error('Failed to send invitation:', error);
    }
  };

  const handleUpdateRole = async (memberId: string, newRole: string) => {
    try {
      await multiTenantAPI.updateMemberRole(memberId, newRole);
      loadOrgData();
    } catch (error) {
      console.error('Failed to update role:', error);
    }
  };

  const handleDeactivateMember = async (memberId: string) => {
    if (!confirm('Are you sure you want to deactivate this member?')) return;
    
    try {
      await multiTenantAPI.deactivateMember(memberId);
      loadOrgData();
    } catch (error) {
      console.error('Failed to deactivate member:', error);
    }
  };

  const handleUpgradePlan = async (plan: string) => {
    if (!currentOrg) return;
    
    try {
      await multiTenantAPI.upgradePlan(currentOrg.id, plan);
      loadData();
    } catch (error) {
      console.error('Failed to upgrade plan:', error);
    }
  };

  const getRoleBadgeColor = (role: string): string => {
    const colors: Record<string, string> = {
      owner: 'bg-purple-100 text-purple-800',
      admin: 'bg-blue-100 text-blue-800',
      manager: 'bg-green-100 text-green-800',
      member: 'bg-gray-100 text-gray-800',
      viewer: 'bg-yellow-100 text-yellow-800'
    };
    return colors[role] || 'bg-gray-100 text-gray-800';
  };

  const getPlanBadgeColor = (plan: string): string => {
    const colors: Record<string, string> = {
      enterprise: 'bg-purple-100 text-purple-800',
      professional: 'bg-blue-100 text-blue-800',
      starter: 'bg-green-100 text-green-800',
      trial: 'bg-yellow-100 text-yellow-800'
    };
    return colors[plan] || 'bg-gray-100 text-gray-800';
  };

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
            <h1 className="text-3xl font-bold text-gray-900">Organization Management</h1>
            <p className="mt-2 text-gray-600">
              Manage your organizations, members, and access control
            </p>
          </div>

          {/* Organization Switcher */}
          {organizations.length > 1 && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Current Organization
              </label>
              <select
                value={currentOrg?.id || ''}
                onChange={(e) => handleSwitchOrg(e.target.value)}
                className="block w-full max-w-md px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {organizations.map(org => (
                  <option key={org.id} value={org.id}>
                    {org.name} ({org.plan})
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Current Organization Card */}
          {currentOrg && (
            <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl p-6 text-white mb-8">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-4">
                  <BuildingOfficeIcon className="h-12 w-12" />
                  <div>
                    <h2 className="text-2xl font-bold">{currentOrg.name}</h2>
                    <p className="text-blue-100 mt-1">{currentOrg.description || 'No description'}</p>
                    <div className="flex items-center space-x-3 mt-3">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getPlanBadgeColor(currentOrg.plan).replace('text', 'bg-white text')}`}>
                        {currentOrg.plan.toUpperCase()}
                      </span>
                      <span className="text-blue-100">•</span>
                      <span className="text-blue-100">{currentOrg.member_count} members</span>
                    </div>
                  </div>
                </div>
                <button className="px-4 py-2 bg-white text-blue-600 rounded-lg hover:bg-blue-50 transition-colors">
                  <CogIcon className="h-5 w-5 inline mr-2" />
                  Settings
                </button>
              </div>
            </div>
          )}

          {/* Tabs */}
          <div className="border-b border-gray-200 mb-6">
            <nav className="-mb-px flex space-x-8">
              {[
                { id: 'overview', name: 'Overview', icon: ChartBarIcon },
                { id: 'members', name: 'Members', icon: UserGroupIcon },
                { id: 'invitations', name: 'Invitations', icon: EnvelopeIcon },
                { id: 'settings', name: 'Settings', icon: CogIcon }
              ].map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as 'overview' | 'members' | 'invitations' | 'settings')}
                  className={`
                    flex items-center py-4 px-1 border-b-2 font-medium text-sm
                    ${activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}
                  `}
                >
                  <tab.icon className="h-5 w-5 mr-2" />
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          {activeTab === 'overview' && statistics && (
            <div className="space-y-6">
              {/* Statistics Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Total Members</p>
                      <p className="text-3xl font-bold text-gray-900 mt-2">{statistics.total_members}</p>
                    </div>
                    <UserGroupIcon className="h-12 w-12 text-blue-600 opacity-50" />
                  </div>
                </div>
                
                <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Active Members</p>
                      <p className="text-3xl font-bold text-green-600 mt-2">{statistics.active_members}</p>
                    </div>
                    <CheckCircleIcon className="h-12 w-12 text-green-600 opacity-50" />
                  </div>
                </div>
                
                <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Pending Invites</p>
                      <p className="text-3xl font-bold text-yellow-600 mt-2">{statistics.pending_invitations}</p>
                    </div>
                    <EnvelopeIcon className="h-12 w-12 text-yellow-600 opacity-50" />
                  </div>
                </div>
                
                <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Admin Users</p>
                      <p className="text-3xl font-bold text-purple-600 mt-2">{statistics.admin_count}</p>
                    </div>
                    <UserGroupIcon className="h-12 w-12 text-purple-600 opacity-50" />
                  </div>
                </div>
              </div>

              {/* Role Distribution */}
              <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Role Distribution</h3>
                <div className="space-y-3">
                  {statistics.role_distribution && Object.entries(statistics.role_distribution).map(([role, count]) => (
                    <div key={role} className="flex items-center justify-between">
                      <span className="text-sm text-gray-600 capitalize">{role}</span>
                      <div className="flex items-center space-x-3">
                        <div className="w-48 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full"
                            style={{ width: `${(count / statistics.total_members) * 100}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium text-gray-900 w-8">{count}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Plan Upgrade */}
              {currentOrg && currentOrg.plan !== 'enterprise' && (
                <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-6 border border-purple-200">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Upgrade Your Plan</h3>
                  <p className="text-gray-600 mb-4">
                    Unlock more features and increase your team size with a higher plan.
                  </p>
                  <div className="flex space-x-4">
                    {['starter', 'professional', 'enterprise'].map(plan => {
                      if (plan <= currentOrg.plan) return null;
                      return (
                        <button
                          key={plan}
                          onClick={() => handleUpgradePlan(plan)}
                          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors capitalize"
                        >
                          Upgrade to {plan}
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'members' && (
            <div>
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-semibold text-gray-900">Team Members</h3>
                <button
                  onClick={() => setShowInviteModal(true)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <UserPlusIcon className="h-5 w-5 inline mr-2" />
                  Invite Member
                </button>
              </div>

              <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Member</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Joined</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {members.map(member => (
                      <tr key={member.id}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900">{member.user_name}</div>
                            <div className="text-sm text-gray-500">{member.user_email}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <select
                            value={member.role}
                            onChange={(e) => handleUpdateRole(member.id, e.target.value)}
                            className={`px-3 py-1 rounded-full text-xs font-medium ${getRoleBadgeColor(member.role)}`}
                          >
                            <option value="owner">Owner</option>
                            <option value="admin">Admin</option>
                            <option value="manager">Manager</option>
                            <option value="member">Member</option>
                            <option value="viewer">Viewer</option>
                          </select>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                            member.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                          }`}>
                            {member.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(member.joined_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                          {member.is_active && member.role !== 'owner' && (
                            <button
                              onClick={() => handleDeactivateMember(member.id)}
                              className="text-red-600 hover:text-red-800"
                            >
                              Deactivate
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'invitations' && (
            <div>
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-semibold text-gray-900">Pending Invitations</h3>
              </div>

              <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sent</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Expires</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {invitations.map(invite => (
                      <tr key={invite.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {invite.email}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${getRoleBadgeColor(invite.role)}`}>
                            {invite.role}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                            invite.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                            invite.status === 'accepted' ? 'bg-green-100 text-green-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {invite.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(invite.sent_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(invite.expires_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                          {invite.status === 'pending' && (
                            <button
                              onClick={() => multiTenantAPI.resendInvitation(invite.id)}
                              className="text-blue-600 hover:text-blue-800"
                            >
                              Resend
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'settings' && currentOrg && (
            <div className="space-y-6">
              <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Organization Settings</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Organization Name
                    </label>
                    <input
                      type="text"
                      defaultValue={currentOrg.name}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Description
                    </label>
                    <textarea
                      defaultValue={currentOrg.description}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Domain
                    </label>
                    <input
                      type="text"
                      defaultValue={currentOrg.domain}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                    Save Changes
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Invite Modal */}
          {showInviteModal && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Invite Team Member</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email Address
                    </label>
                    <input
                      type="email"
                      value={inviteEmail}
                      onChange={(e) => setInviteEmail(e.target.value)}
                      placeholder="colleague@company.com"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Role
                    </label>
                    <select
                      value={inviteRole}
                      onChange={(e) => setInviteRole(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="member">Member</option>
                      <option value="manager">Manager</option>
                      <option value="admin">Admin</option>
                      <option value="viewer">Viewer</option>
                    </select>
                  </div>
                  <div className="flex space-x-3">
                    <button
                      onClick={handleInviteMember}
                      className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      Send Invitation
                    </button>
                    <button
                      onClick={() => setShowInviteModal(false)}
                      className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </ProtectedRoute>
    </MainLayout>
  );
}
