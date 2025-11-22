'use client';

import React, { useState } from 'react';
import { 
  Building2, MessageSquare, FileText, CheckCircle2, 
  Plus, Lock, Users, Calendar, Clock, Send, 
  Upload, Download, ThumbsUp, MessageCircle, Eye,
  Search, Filter, ArrowRight, Settings, MoreVertical,
  UserPlus, Shield, Unlock, Reply, Heart
} from 'lucide-react';

// Deal Room Types
interface DealRoom {
  id: number;
  name: string;
  opportunity: string;
  status: 'active' | 'archived' | 'closed';
  privacy_level: 'public' | 'private' | 'restricted';
  participant_count: number;
  message_count: number;
  document_count: number;
  created_at: string;
}

interface Channel {
  id: number;
  name: string;
  channel_type: 'public' | 'private' | 'direct' | 'group';
  member_count: number;
  unread_count: number;
  last_message?: string;
  last_message_at?: string;
  is_archived: boolean;
}

interface Message {
  id: number;
  sender: string;
  content: string;
  created_at: string;
  reactions?: { [emoji: string]: number };
  reply_count: number;
  attachments?: string[];
}

interface Document {
  id: number;
  title: string;
  document_type: 'contract' | 'proposal' | 'presentation' | 'spreadsheet' | 'other';
  version: number;
  is_locked: boolean;
  locked_by?: string;
  comment_count: number;
  updated_at: string;
  file_url: string;
}

interface Approval {
  id: number;
  workflow: string;
  status: 'pending' | 'approved' | 'rejected';
  initiated_by: string;
  created_at: string;
  pending_approvers: string[];
  steps_completed: number;
  total_steps: number;
}

export default function CollaborationPage() {
  const [activeTab, setActiveTab] = useState<'deal-rooms' | 'channels' | 'documents' | 'approvals'>('deal-rooms');
  const [selectedRoom, setSelectedRoom] = useState<number | null>(null);
  const [selectedChannel, setSelectedChannel] = useState<number | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Mock data
  const dealRooms: DealRoom[] = [
    {
      id: 1,
      name: 'Enterprise Cloud Migration',
      opportunity: 'Acme Corp - Cloud Services',
      status: 'active',
      privacy_level: 'private',
      participant_count: 8,
      message_count: 142,
      document_count: 23,
      created_at: '2024-01-15'
    },
    {
      id: 2,
      name: 'Q1 Product Launch',
      opportunity: 'TechStart Inc - Product Suite',
      status: 'active',
      privacy_level: 'restricted',
      participant_count: 12,
      message_count: 287,
      document_count: 45,
      created_at: '2024-02-01'
    },
    {
      id: 3,
      name: 'Global Expansion Strategy',
      opportunity: 'GlobalCorp - Consulting Services',
      status: 'active',
      privacy_level: 'public',
      participant_count: 5,
      message_count: 89,
      document_count: 15,
      created_at: '2024-02-10'
    }
  ];

  const channels: Channel[] = [
    {
      id: 1,
      name: 'General Discussion',
      channel_type: 'public',
      member_count: 45,
      unread_count: 3,
      last_message: 'Let\'s schedule a meeting for tomorrow',
      last_message_at: '5 minutes ago',
      is_archived: false
    },
    {
      id: 2,
      name: 'Sales Team',
      channel_type: 'private',
      member_count: 12,
      unread_count: 0,
      last_message: 'Q1 numbers looking great!',
      last_message_at: '1 hour ago',
      is_archived: false
    },
    {
      id: 3,
      name: 'Product Updates',
      channel_type: 'public',
      member_count: 67,
      unread_count: 8,
      last_message: 'New feature released today',
      last_message_at: '10 minutes ago',
      is_archived: false
    }
  ];

  const messages: Message[] = [
    {
      id: 1,
      sender: 'John Doe',
      content: 'Has everyone reviewed the latest proposal draft?',
      created_at: '10:30 AM',
      reactions: { '👍': 5, '❤️': 2 },
      reply_count: 3
    },
    {
      id: 2,
      sender: 'Jane Smith',
      content: 'Yes, I left some comments on section 3. Overall looks good!',
      created_at: '10:35 AM',
      reactions: { '👍': 3 },
      reply_count: 1
    },
    {
      id: 3,
      sender: 'Mike Johnson',
      content: 'I\'ll update the pricing section based on the feedback',
      created_at: '10:42 AM',
      reactions: {},
      reply_count: 0,
      attachments: ['pricing_update_v2.xlsx']
    }
  ];

  const documents: Document[] = [
    {
      id: 1,
      title: 'Enterprise Agreement - Final Draft',
      document_type: 'contract',
      version: 3,
      is_locked: true,
      locked_by: 'Sarah Wilson',
      comment_count: 12,
      updated_at: '2 hours ago',
      file_url: '#'
    },
    {
      id: 2,
      title: 'Q1 Sales Presentation',
      document_type: 'presentation',
      version: 5,
      is_locked: false,
      comment_count: 8,
      updated_at: '1 day ago',
      file_url: '#'
    },
    {
      id: 3,
      title: 'Technical Proposal',
      document_type: 'proposal',
      version: 2,
      is_locked: false,
      comment_count: 15,
      updated_at: '3 hours ago',
      file_url: '#'
    }
  ];

  const approvals: Approval[] = [
    {
      id: 1,
      workflow: 'Contract Approval - Acme Corp',
      status: 'pending',
      initiated_by: 'John Doe',
      created_at: '2024-03-15',
      pending_approvers: ['Legal Team', 'CFO'],
      steps_completed: 2,
      total_steps: 4
    },
    {
      id: 2,
      workflow: 'Discount Request - 25% Off',
      status: 'approved',
      initiated_by: 'Jane Smith',
      created_at: '2024-03-14',
      pending_approvers: [],
      steps_completed: 3,
      total_steps: 3
    },
    {
      id: 3,
      workflow: 'Budget Increase - Q2 2024',
      status: 'pending',
      initiated_by: 'Mike Johnson',
      created_at: '2024-03-13',
      pending_approvers: ['VP Sales', 'CFO', 'CEO'],
      steps_completed: 0,
      total_steps: 3
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'approved': return 'bg-green-100 text-green-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      case 'archived': return 'bg-gray-100 text-gray-800';
      case 'closed': return 'bg-gray-100 text-gray-800';
      default: return 'bg-blue-100 text-blue-800';
    }
  };

  const getPrivacyIcon = (privacy: string) => {
    switch (privacy) {
      case 'private': return <Lock className="w-4 h-4" />;
      case 'restricted': return <Shield className="w-4 h-4" />;
      default: return <Eye className="w-4 h-4" />;
    }
  };

  const getDocumentIcon = (type: string) => {
    return <FileText className="w-5 h-5" />;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Advanced Collaboration
        </h1>
        <p className="text-gray-600">
          Collaborate with your team in real-time with deal rooms, messaging, documents, and approvals
        </p>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-sm mb-6">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6" aria-label="Tabs">
            <button
              onClick={() => setActiveTab('deal-rooms')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'deal-rooms'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Building2 className="w-5 h-5 inline-block mr-2" />
              Deal Rooms
            </button>
            <button
              onClick={() => setActiveTab('channels')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'channels'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <MessageSquare className="w-5 h-5 inline-block mr-2" />
              Channels
              {channels.reduce((sum, ch) => sum + ch.unread_count, 0) > 0 && (
                <span className="ml-2 bg-red-500 text-white text-xs rounded-full px-2 py-0.5">
                  {channels.reduce((sum, ch) => sum + ch.unread_count, 0)}
                </span>
              )}
            </button>
            <button
              onClick={() => setActiveTab('documents')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'documents'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <FileText className="w-5 h-5 inline-block mr-2" />
              Documents
            </button>
            <button
              onClick={() => setActiveTab('approvals')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'approvals'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <CheckCircle2 className="w-5 h-5 inline-block mr-2" />
              Approvals
              {approvals.filter(a => a.status === 'pending').length > 0 && (
                <span className="ml-2 bg-yellow-500 text-white text-xs rounded-full px-2 py-0.5">
                  {approvals.filter(a => a.status === 'pending').length}
                </span>
              )}
            </button>
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {/* Deal Rooms Tab */}
          {activeTab === 'deal-rooms' && (
            <div>
              <div className="flex justify-between items-center mb-6">
                <div className="flex-1 max-w-md">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                      type="text"
                      placeholder="Search deal rooms..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>
                <button className="ml-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center">
                  <Plus className="w-5 h-5 mr-2" />
                  Create Deal Room
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {dealRooms.map((room) => (
                  <div
                    key={room.id}
                    className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow cursor-pointer"
                    onClick={() => setSelectedRoom(room.id)}
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 mb-1">{room.name}</h3>
                        <p className="text-sm text-gray-600">{room.opportunity}</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        {getPrivacyIcon(room.privacy_level)}
                        <button className="text-gray-400 hover:text-gray-600">
                          <MoreVertical className="w-5 h-5" />
                        </button>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2 mb-4">
                      <span className={`text-xs font-medium px-2.5 py-0.5 rounded-full ${getStatusColor(room.status)}`}>
                        {room.status.charAt(0).toUpperCase() + room.status.slice(1)}
                      </span>
                      <span className="text-xs text-gray-500">{room.privacy_level}</span>
                    </div>

                    <div className="grid grid-cols-3 gap-4 mb-4">
                      <div className="text-center">
                        <div className="flex items-center justify-center text-blue-600 mb-1">
                          <Users className="w-4 h-4 mr-1" />
                          <span className="text-sm font-semibold">{room.participant_count}</span>
                        </div>
                        <p className="text-xs text-gray-500">Members</p>
                      </div>
                      <div className="text-center">
                        <div className="flex items-center justify-center text-green-600 mb-1">
                          <MessageSquare className="w-4 h-4 mr-1" />
                          <span className="text-sm font-semibold">{room.message_count}</span>
                        </div>
                        <p className="text-xs text-gray-500">Messages</p>
                      </div>
                      <div className="text-center">
                        <div className="flex items-center justify-center text-purple-600 mb-1">
                          <FileText className="w-4 h-4 mr-1" />
                          <span className="text-sm font-semibold">{room.document_count}</span>
                        </div>
                        <p className="text-xs text-gray-500">Docs</p>
                      </div>
                    </div>

                    <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                      <span className="text-xs text-gray-500 flex items-center">
                        <Calendar className="w-3 h-3 mr-1" />
                        {new Date(room.created_at).toLocaleDateString()}
                      </span>
                      <button className="text-blue-600 text-sm font-medium hover:text-blue-700 flex items-center">
                        Open
                        <ArrowRight className="w-4 h-4 ml-1" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Channels Tab */}
          {activeTab === 'channels' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Channel List */}
              <div className="lg:col-span-1 space-y-2">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">Channels</h3>
                  <button className="text-blue-600 hover:text-blue-700">
                    <Plus className="w-5 h-5" />
                  </button>
                </div>
                {channels.map((channel) => (
                  <div
                    key={channel.id}
                    className={`p-4 rounded-lg cursor-pointer transition-colors ${
                      selectedChannel === channel.id
                        ? 'bg-blue-50 border border-blue-200'
                        : 'bg-gray-50 border border-gray-200 hover:bg-gray-100'
                    }`}
                    onClick={() => setSelectedChannel(channel.id)}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center">
                        <MessageSquare className="w-5 h-5 text-gray-600 mr-2" />
                        <span className="font-medium text-gray-900">{channel.name}</span>
                      </div>
                      {channel.unread_count > 0 && (
                        <span className="bg-red-500 text-white text-xs rounded-full px-2 py-0.5">
                          {channel.unread_count}
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 truncate">{channel.last_message}</p>
                    <p className="text-xs text-gray-400 mt-1">{channel.last_message_at}</p>
                  </div>
                ))}
              </div>

              {/* Message View */}
              <div className="lg:col-span-2 bg-white border border-gray-200 rounded-lg">
                {selectedChannel ? (
                  <>
                    {/* Channel Header */}
                    <div className="border-b border-gray-200 p-4 flex items-center justify-between">
                      <div className="flex items-center">
                        <MessageSquare className="w-5 h-5 text-gray-600 mr-2" />
                        <div>
                          <h3 className="font-semibold text-gray-900">
                            {channels.find(c => c.id === selectedChannel)?.name}
                          </h3>
                          <p className="text-sm text-gray-500">
                            {channels.find(c => c.id === selectedChannel)?.member_count} members
                          </p>
                        </div>
                      </div>
                      <button className="text-gray-400 hover:text-gray-600">
                        <Settings className="w-5 h-5" />
                      </button>
                    </div>

                    {/* Messages */}
                    <div className="p-4 space-y-4 max-h-96 overflow-y-auto">
                      {messages.map((message) => (
                        <div key={message.id} className="flex space-x-3">
                          <div className="flex-shrink-0">
                            <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-semibold">
                              {message.sender.split(' ').map(n => n[0]).join('')}
                            </div>
                          </div>
                          <div className="flex-1">
                            <div className="flex items-baseline space-x-2 mb-1">
                              <span className="font-semibold text-gray-900">{message.sender}</span>
                              <span className="text-xs text-gray-500">{message.created_at}</span>
                            </div>
                            <p className="text-gray-700 mb-2">{message.content}</p>
                            {message.attachments && message.attachments.length > 0 && (
                              <div className="flex items-center space-x-2 mb-2">
                                {message.attachments.map((attachment, idx) => (
                                  <div key={idx} className="flex items-center bg-gray-100 rounded px-2 py-1 text-sm">
                                    <FileText className="w-4 h-4 mr-1 text-gray-600" />
                                    {attachment}
                                  </div>
                                ))}
                              </div>
                            )}
                            <div className="flex items-center space-x-4 text-sm">
                              {Object.entries(message.reactions || {}).map(([emoji, count]) => (
                                <button key={emoji} className="flex items-center text-gray-600 hover:text-gray-900">
                                  <span className="mr-1">{emoji}</span>
                                  <span>{count}</span>
                                </button>
                              ))}
                              {message.reply_count > 0 && (
                                <button className="flex items-center text-blue-600 hover:text-blue-700">
                                  <Reply className="w-4 h-4 mr-1" />
                                  {message.reply_count} {message.reply_count === 1 ? 'reply' : 'replies'}
                                </button>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Message Input */}
                    <div className="border-t border-gray-200 p-4">
                      <div className="flex items-center space-x-2">
                        <input
                          type="text"
                          placeholder="Type a message..."
                          className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                        <button className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 transition-colors">
                          <Send className="w-5 h-5" />
                        </button>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="flex items-center justify-center h-full min-h-[400px]">
                    <div className="text-center text-gray-500">
                      <MessageSquare className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                      <p>Select a channel to view messages</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Documents Tab */}
          {activeTab === 'documents' && (
            <div>
              <div className="flex justify-between items-center mb-6">
                <div className="flex-1 max-w-md">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                      type="text"
                      placeholder="Search documents..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>
                <button className="ml-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center">
                  <Upload className="w-5 h-5 mr-2" />
                  Upload Document
                </button>
              </div>

              <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Document
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Version
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Comments
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Last Updated
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {documents.map((doc) => (
                      <tr key={doc.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            {getDocumentIcon(doc.document_type)}
                            <div className="ml-3">
                              <p className="text-sm font-medium text-gray-900">{doc.title}</p>
                              <p className="text-sm text-gray-500 capitalize">{doc.document_type}</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="text-sm text-gray-900">v{doc.version}</span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {doc.is_locked ? (
                            <div className="flex items-center text-sm">
                              <Lock className="w-4 h-4 text-yellow-600 mr-1" />
                              <span className="text-yellow-600">Locked by {doc.locked_by}</span>
                            </div>
                          ) : (
                            <div className="flex items-center text-sm">
                              <Unlock className="w-4 h-4 text-green-600 mr-1" />
                              <span className="text-green-600">Available</span>
                            </div>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center text-sm text-gray-900">
                            <MessageCircle className="w-4 h-4 mr-1 text-gray-400" />
                            {doc.comment_count}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {doc.updated_at}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button className="text-blue-600 hover:text-blue-900 mr-3">
                            <Download className="w-5 h-5" />
                          </button>
                          <button className="text-gray-400 hover:text-gray-600">
                            <MoreVertical className="w-5 h-5" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Approvals Tab */}
          {activeTab === 'approvals' && (
            <div>
              <div className="flex justify-between items-center mb-6">
                <div className="flex space-x-2">
                  <button className="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg font-medium">
                    Pending ({approvals.filter(a => a.status === 'pending').length})
                  </button>
                  <button className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg font-medium">
                    All Approvals
                  </button>
                </div>
                <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center">
                  <Plus className="w-5 h-5 mr-2" />
                  Request Approval
                </button>
              </div>

              <div className="space-y-4">
                {approvals.map((approval) => (
                  <div key={approval.id} className="bg-white border border-gray-200 rounded-lg p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 mb-1">{approval.workflow}</h3>
                        <p className="text-sm text-gray-600">
                          Initiated by {approval.initiated_by} on {new Date(approval.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <span className={`text-sm font-medium px-3 py-1 rounded-full ${getStatusColor(approval.status)}`}>
                        {approval.status.charAt(0).toUpperCase() + approval.status.slice(1)}
                      </span>
                    </div>

                    {/* Progress Bar */}
                    <div className="mb-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-600">
                          Step {approval.steps_completed} of {approval.total_steps}
                        </span>
                        <span className="text-sm font-medium text-gray-900">
                          {Math.round((approval.steps_completed / approval.total_steps) * 100)}% Complete
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all"
                          style={{ width: `${(approval.steps_completed / approval.total_steps) * 100}%` }}
                        />
                      </div>
                    </div>

                    {/* Pending Approvers */}
                    {approval.pending_approvers.length > 0 && (
                      <div className="mb-4">
                        <p className="text-sm font-medium text-gray-700 mb-2">Pending Approvers:</p>
                        <div className="flex flex-wrap gap-2">
                          {approval.pending_approvers.map((approver, idx) => (
                            <span key={idx} className="bg-yellow-100 text-yellow-800 text-sm px-3 py-1 rounded-full">
                              {approver}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Actions */}
                    {approval.status === 'pending' && (
                      <div className="flex space-x-3 pt-4 border-t border-gray-100">
                        <button className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center">
                          <CheckCircle2 className="w-5 h-5 mr-2" />
                          Approve
                        </button>
                        <button className="flex-1 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors">
                          Reject
                        </button>
                        <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
                          View Details
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
