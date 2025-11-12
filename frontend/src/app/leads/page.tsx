'use client';

import { useState } from 'react';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { 
  UserPlus, 
  Search,
  Filter,
  MoreVertical,
  Mail,
  Phone,
  Edit,
  Trash2,
  TrendingUp,
  MapPin,
  DollarSign,
  Star,
  Flame
} from 'lucide-react';

interface Lead {
  id: string;
  name: string;
  email: string;
  phone: string;
  company: string;
  source: string;
  stage: 'new' | 'contacted' | 'qualified' | 'proposal' | 'negotiation';
  value: number;
  score: number;
  location: string;
  assignedTo: string;
}

const mockLeads: Lead[] = [
  {
    id: '1',
    name: 'John Doe',
    email: 'john.doe@example.com',
    phone: '+1 (555) 111-2222',
    company: 'Acme Inc',
    source: 'Website',
    stage: 'new',
    value: 25000,
    score: 85,
    location: 'San Francisco, CA',
    assignedTo: 'Sarah K.',
  },
  {
    id: '2',
    name: 'Jane Smith',
    email: 'jane.smith@techco.com',
    phone: '+1 (555) 222-3333',
    company: 'TechCo',
    source: 'Referral',
    stage: 'contacted',
    value: 45000,
    score: 92,
    location: 'New York, NY',
    assignedTo: 'Mike R.',
  },
  {
    id: '3',
    name: 'Bob Johnson',
    email: 'bob@startup.io',
    phone: '+1 (555) 333-4444',
    company: 'Startup.io',
    source: 'LinkedIn',
    stage: 'qualified',
    value: 35000,
    score: 78,
    location: 'Austin, TX',
    assignedTo: 'Sarah K.',
  },
  {
    id: '4',
    name: 'Alice Williams',
    email: 'alice@megacorp.com',
    phone: '+1 (555) 444-5555',
    company: 'MegaCorp',
    source: 'Cold Call',
    stage: 'proposal',
    value: 75000,
    score: 95,
    location: 'Chicago, IL',
    assignedTo: 'John D.',
  },
  {
    id: '5',
    name: 'Charlie Brown',
    email: 'charlie@innovation.com',
    phone: '+1 (555) 555-6666',
    company: 'Innovation Ltd',
    source: 'Event',
    stage: 'negotiation',
    value: 50000,
    score: 88,
    location: 'Boston, MA',
    assignedTo: 'Mike R.',
  },
  {
    id: '6',
    name: 'Diana Prince',
    email: 'diana@enterprise.com',
    phone: '+1 (555) 666-7777',
    company: 'Enterprise Solutions',
    source: 'Website',
    stage: 'new',
    value: 30000,
    score: 72,
    location: 'Seattle, WA',
    assignedTo: 'Sarah K.',
  },
];

const stages = [
  { id: 'new', name: 'New', color: 'bg-blue-50 border-blue-200' },
  { id: 'contacted', name: 'Contacted', color: 'bg-purple-50 border-purple-200' },
  { id: 'qualified', name: 'Qualified', color: 'bg-yellow-50 border-yellow-200' },
  { id: 'proposal', name: 'Proposal', color: 'bg-orange-50 border-orange-200' },
  { id: 'negotiation', name: 'Negotiation', color: 'bg-green-50 border-green-200' },
];

export default function LeadsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'kanban' | 'list'>('kanban');

  const filteredLeads = mockLeads.filter(lead =>
    lead.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    lead.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
    lead.company.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getLeadsByStage = (stage: string) => {
    return filteredLeads.filter(lead => lead.stage === stage);
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 75) return 'text-yellow-600';
    return 'text-gray-600';
  };

  const getScoreBadge = (score: number) => {
    if (score >= 90) return <span title="Hot Lead"><Flame className="w-4 h-4 text-red-500" /></span>;
    if (score >= 75) return <span title="Warm Lead"><Star className="w-4 h-4 text-yellow-500" /></span>;
    return null;
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-4 lg:p-6 space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-2xl lg:text-3xl font-bold text-gray-900">Leads</h1>
              <p className="text-gray-500 mt-1">Track and manage your sales pipeline</p>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant={viewMode === 'kanban' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('kanban')}
              >
                Kanban
              </Button>
              <Button
                variant={viewMode === 'list' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('list')}
              >
                List
              </Button>
              <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                <UserPlus className="w-4 h-4 mr-2" />
                Add Lead
              </Button>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold">{mockLeads.length}</div>
                <p className="text-xs text-muted-foreground">Total Leads</p>
              </CardContent>
            </Card>
            {stages.map((stage) => (
              <Card key={stage.id}>
                <CardContent className="p-4">
                  <div className="text-2xl font-bold">
                    {getLeadsByStage(stage.id).length}
                  </div>
                  <p className="text-xs text-muted-foreground">{stage.name}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Search */}
          <Card>
            <CardContent className="p-4">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    type="text"
                    placeholder="Search leads..."
                    className="pl-10"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
                <Button variant="outline" size="sm">
                  <Filter className="w-4 h-4 mr-2" />
                  Filter
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Kanban View */}
          {viewMode === 'kanban' && (
            <div className="overflow-x-auto pb-4">
              <div className="flex gap-4 min-w-max">
                {stages.map((stage) => {
                  const stageLeads = getLeadsByStage(stage.id);
                  const stageValue = stageLeads.reduce((sum, lead) => sum + lead.value, 0);

                  return (
                    <div key={stage.id} className="w-80 shrink-0">
                      <Card className={`border-2 ${stage.color}`}>
                        <CardHeader className="pb-3">
                          <div className="flex items-center justify-between">
                            <CardTitle className="text-sm font-semibold">
                              {stage.name}
                            </CardTitle>
                            <Badge variant="secondary">{stageLeads.length}</Badge>
                          </div>
                          <p className="text-xs text-muted-foreground">
                            ${(stageValue / 1000).toFixed(0)}K total value
                          </p>
                        </CardHeader>
                        <CardContent className="space-y-3 max-h-[calc(100vh-24rem)] overflow-y-auto">
                          {stageLeads.map((lead) => (
                            <Card key={lead.id} className="hover:shadow-md transition-shadow cursor-pointer">
                              <CardContent className="p-4">
                                <div className="flex items-start justify-between mb-3">
                                  <div>
                                    <h4 className="font-semibold text-sm">{lead.name}</h4>
                                    <p className="text-xs text-gray-500">{lead.company}</p>
                                  </div>
                                  <div className="flex items-center gap-1">
                                    {getScoreBadge(lead.score)}
                                    <DropdownMenu>
                                      <DropdownMenuTrigger asChild>
                                        <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                                          <MoreVertical className="w-3 h-3" />
                                        </Button>
                                      </DropdownMenuTrigger>
                                      <DropdownMenuContent align="end">
                                        <DropdownMenuItem>
                                          <Edit className="w-4 h-4 mr-2" />
                                          Edit
                                        </DropdownMenuItem>
                                        <DropdownMenuItem>
                                          <Mail className="w-4 h-4 mr-2" />
                                          Send Email
                                        </DropdownMenuItem>
                                        <DropdownMenuItem>
                                          <Phone className="w-4 h-4 mr-2" />
                                          Call
                                        </DropdownMenuItem>
                                        <DropdownMenuSeparator />
                                        <DropdownMenuItem className="text-red-600">
                                          <Trash2 className="w-4 h-4 mr-2" />
                                          Delete
                                        </DropdownMenuItem>
                                      </DropdownMenuContent>
                                    </DropdownMenu>
                                  </div>
                                </div>

                                <div className="space-y-1.5 mb-3">
                                  <div className="flex items-center text-xs text-gray-600">
                                    <DollarSign className="w-3 h-3 mr-1" />
                                    <span>${(lead.value / 1000).toFixed(0)}K</span>
                                  </div>
                                  <div className="flex items-center text-xs text-gray-600">
                                    <TrendingUp className="w-3 h-3 mr-1" />
                                    <span className={getScoreColor(lead.score)}>
                                      Score: {lead.score}
                                    </span>
                                  </div>
                                  <div className="flex items-center text-xs text-gray-600">
                                    <MapPin className="w-3 h-3 mr-1" />
                                    <span className="truncate">{lead.location}</span>
                                  </div>
                                </div>

                                <div className="flex items-center justify-between pt-3 border-t">
                                  <Badge variant="outline" className="text-xs">
                                    {lead.source}
                                  </Badge>
                                  <span className="text-xs text-gray-500">{lead.assignedTo}</span>
                                </div>
                              </CardContent>
                            </Card>
                          ))}
                          {stageLeads.length === 0 && (
                            <div className="text-center py-8 text-sm text-gray-400">
                              No leads in this stage
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* List View */}
          {viewMode === 'list' && (
            <Card>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Lead
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Company
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Stage
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Value
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Score
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Assigned To
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {filteredLeads.map((lead) => (
                        <tr key={lead.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div>
                              <div className="text-sm font-medium text-gray-900">{lead.name}</div>
                              <div className="text-sm text-gray-500">{lead.email}</div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-900">{lead.company}</div>
                            <div className="text-sm text-gray-500">{lead.source}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <Badge variant="outline">
                              {stages.find(s => s.id === lead.stage)?.name}
                            </Badge>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            ${lead.value.toLocaleString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center gap-2">
                              {getScoreBadge(lead.score)}
                              <span className={`text-sm font-medium ${getScoreColor(lead.score)}`}>
                                {lead.score}
                              </span>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {lead.assignedTo}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">
                            <div className="flex gap-2">
                              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                                <Mail className="w-4 h-4" />
                              </Button>
                              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                                <Phone className="w-4 h-4" />
                              </Button>
                              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                                <Edit className="w-4 h-4" />
                              </Button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {filteredLeads.length === 0 && (
            <Card>
              <CardContent className="p-12 text-center">
                <p className="text-gray-500">No leads found matching your search.</p>
              </CardContent>
            </Card>
          )}
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
