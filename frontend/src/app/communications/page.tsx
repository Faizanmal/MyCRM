'use client';

import { useState } from 'react';
import { 
  Mail, 
  Phone, 
  MessageSquare, 
  Video,
  Search,
  User,
  Clock
} from 'lucide-react';

import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface Communication {
  id: string;
  type: 'email' | 'call' | 'meeting' | 'sms';
  subject: string;
  contact: string;
  date: string;
  direction: 'inbound' | 'outbound';
  status: 'completed' | 'scheduled' | 'failed';
  notes?: string;
}

const mockCommunications: Communication[] = [
  {
    id: '1',
    type: 'email',
    subject: 'Follow-up on proposal',
    contact: 'John Doe (TechCorp)',
    date: '2025-11-10T10:30:00',
    direction: 'outbound',
    status: 'completed',
    notes: 'Sent proposal document and pricing',
  },
  {
    id: '2',
    type: 'call',
    subject: 'Discovery call',
    contact: 'Jane Smith (StartupXYZ)',
    date: '2025-11-10T14:00:00',
    direction: 'inbound',
    status: 'completed',
    notes: 'Discussed requirements and timeline',
  },
  {
    id: '3',
    type: 'meeting',
    subject: 'Product demo',
    contact: 'Bob Johnson (Innovation Ltd)',
    date: '2025-11-12T15:00:00',
    direction: 'outbound',
    status: 'scheduled',
    notes: 'Prepare demo environment',
  },
  {
    id: '4',
    type: 'email',
    subject: 'Contract questions',
    contact: 'Alice Williams (MegaCorp)',
    date: '2025-11-09T16:20:00',
    direction: 'inbound',
    status: 'completed',
    notes: 'Answered questions about terms',
  },
  {
    id: '5',
    type: 'sms',
    subject: 'Meeting reminder',
    contact: 'Charlie Brown (GlobalTech)',
    date: '2025-11-11T09:00:00',
    direction: 'outbound',
    status: 'scheduled',
  },
];

export default function CommunicationsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState('all');

  const filteredCommunications = mockCommunications.filter(comm => {
    const matchesSearch =
      comm.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
      comm.contact.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesTab = activeTab === 'all' || comm.type === activeTab;
    return matchesSearch && matchesTab;
  });

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'email': return <Mail className="w-5 h-5 text-blue-600" />;
      case 'call': return <Phone className="w-5 h-5 text-green-600" />;
      case 'meeting': return <Video className="w-5 h-5 text-purple-600" />;
      case 'sms': return <MessageSquare className="w-5 h-5 text-orange-600" />;
      default: return <Mail className="w-5 h-5" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'scheduled': return 'bg-blue-100 text-blue-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getDirectionBadge = (direction: string) => {
    return direction === 'inbound' ? (
      <Badge variant="outline" className="text-xs">Received</Badge>
    ) : (
      <Badge variant="outline" className="text-xs">Sent</Badge>
    );
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-4 lg:p-6 space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-2xl lg:text-3xl font-bold text-gray-900">Communications</h1>
              <p className="text-gray-500 mt-1">Track all customer interactions</p>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm">
                <Mail className="w-4 h-4 mr-2" />
                Email
              </Button>
              <Button variant="outline" size="sm">
                <Phone className="w-4 h-4 mr-2" />
                Call
              </Button>
              <Button variant="outline" size="sm">
                <Video className="w-4 h-4 mr-2" />
                Meeting
              </Button>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2 mb-1">
                  <Mail className="w-4 h-4 text-blue-600" />
                  <span className="text-sm font-medium">Emails</span>
                </div>
                <div className="text-2xl font-bold">
                  {mockCommunications.filter(c => c.type === 'email').length}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2 mb-1">
                  <Phone className="w-4 h-4 text-green-600" />
                  <span className="text-sm font-medium">Calls</span>
                </div>
                <div className="text-2xl font-bold">
                  {mockCommunications.filter(c => c.type === 'call').length}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2 mb-1">
                  <Video className="w-4 h-4 text-purple-600" />
                  <span className="text-sm font-medium">Meetings</span>
                </div>
                <div className="text-2xl font-bold">
                  {mockCommunications.filter(c => c.type === 'meeting').length}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2 mb-1">
                  <MessageSquare className="w-4 h-4 text-orange-600" />
                  <span className="text-sm font-medium">Messages</span>
                </div>
                <div className="text-2xl font-bold">
                  {mockCommunications.filter(c => c.type === 'sms').length}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Search */}
          <Card>
            <CardContent className="p-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  type="text"
                  placeholder="Search communications..."
                  className="pl-10"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            </CardContent>
          </Card>

          {/* Communications Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="all">All</TabsTrigger>
              <TabsTrigger value="email">
                <Mail className="w-4 h-4 mr-2" />
                Email
              </TabsTrigger>
              <TabsTrigger value="call">
                <Phone className="w-4 h-4 mr-2" />
                Calls
              </TabsTrigger>
              <TabsTrigger value="meeting">
                <Video className="w-4 h-4 mr-2" />
                Meetings
              </TabsTrigger>
              <TabsTrigger value="sms">
                <MessageSquare className="w-4 h-4 mr-2" />
                SMS
              </TabsTrigger>
            </TabsList>

            <TabsContent value={activeTab} className="space-y-3 mt-6">
              {filteredCommunications.map((comm) => (
                <Card key={comm.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex items-start gap-4">
                      <div className="mt-1">
                        {getTypeIcon(comm.type)}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-4 mb-2">
                          <div>
                            <h3 className="font-semibold text-gray-900">{comm.subject}</h3>
                            <div className="flex items-center gap-2 mt-1 text-sm text-gray-600">
                              <User className="w-4 h-4" />
                              <span>{comm.contact}</span>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            {getDirectionBadge(comm.direction)}
                            <Badge className={getStatusColor(comm.status)}>
                              {comm.status}
                            </Badge>
                          </div>
                        </div>

                        {comm.notes && (
                          <p className="text-sm text-gray-600 mb-2">{comm.notes}</p>
                        )}

                        <div className="flex items-center gap-2 text-sm text-gray-500">
                          <Clock className="w-4 h-4" />
                          <span>{new Date(comm.date).toLocaleString()}</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </TabsContent>
          </Tabs>

          {filteredCommunications.length === 0 && (
            <Card>
              <CardContent className="p-12 text-center">
                <MessageSquare className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No communications found matching your criteria.</p>
              </CardContent>
            </Card>
          )}
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}

