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
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { 
  TrendingUp, 
  Search,
  MoreVertical,
  DollarSign,
  Calendar,
  Building2,
  User,
  Target,
  CheckCircle2
} from 'lucide-react';

interface Opportunity {
  id: string;
  name: string;
  company: string;
  value: number;
  stage: 'prospecting' | 'qualification' | 'proposal' | 'negotiation' | 'closed-won' | 'closed-lost';
  probability: number;
  closeDate: string;
  owner: string;
  contactName: string;
}

const mockOpportunities: Opportunity[] = [
  {
    id: '1',
    name: 'Enterprise License - Q4',
    company: 'TechCorp Inc',
    value: 125000,
    stage: 'negotiation',
    probability: 80,
    closeDate: '2025-11-30',
    owner: 'Sarah Johnson',
    contactName: 'John Doe',
  },
  {
    id: '2',
    name: 'Annual Subscription',
    company: 'StartupXYZ',
    value: 45000,
    stage: 'proposal',
    probability: 60,
    closeDate: '2025-11-25',
    owner: 'Mike Smith',
    contactName: 'Jane Smith',
  },
  {
    id: '3',
    name: 'Premium Support Package',
    company: 'GlobalTech',
    value: 75000,
    stage: 'qualification',
    probability: 40,
    closeDate: '2025-12-15',
    owner: 'Sarah Johnson',
    contactName: 'Bob Johnson',
  },
  {
    id: '4',
    name: 'Multi-Year Deal',
    company: 'MegaCorp Ltd',
    value: 250000,
    stage: 'prospecting',
    probability: 20,
    closeDate: '2026-01-31',
    owner: 'John Davis',
    contactName: 'Alice Williams',
  },
  {
    id: '5',
    name: 'Professional Services',
    company: 'Innovation Inc',
    value: 95000,
    stage: 'closed-won',
    probability: 100,
    closeDate: '2025-11-05',
    owner: 'Mike Smith',
    contactName: 'Charlie Brown',
  },
];

const stages = [
  { id: 'prospecting', name: 'Prospecting', color: 'bg-gray-100 text-gray-800' },
  { id: 'qualification', name: 'Qualification', color: 'bg-blue-100 text-blue-800' },
  { id: 'proposal', name: 'Proposal', color: 'bg-purple-100 text-purple-800' },
  { id: 'negotiation', name: 'Negotiation', color: 'bg-yellow-100 text-yellow-800' },
  { id: 'closed-won', name: 'Closed Won', color: 'bg-green-100 text-green-800' },
  { id: 'closed-lost', name: 'Closed Lost', color: 'bg-red-100 text-red-800' },
];

export default function OpportunitiesPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStage, setSelectedStage] = useState<string>('all');

  const filteredOpportunities = mockOpportunities.filter(opp => {
    const matchesSearch =
      opp.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      opp.company.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStage = selectedStage === 'all' || opp.stage === selectedStage;
    return matchesSearch && matchesStage;
  });

  const totalValue = filteredOpportunities.reduce((sum, opp) => sum + opp.value, 0);
  const weightedValue = filteredOpportunities.reduce(
    (sum, opp) => sum + (opp.value * opp.probability / 100),
    0
  );

  const wonDeals = mockOpportunities.filter(o => o.stage === 'closed-won');
  const wonValue = wonDeals.reduce((sum, opp) => sum + opp.value, 0);

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-4 lg:p-6 space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-2xl lg:text-3xl font-bold text-gray-900">Opportunities</h1>
              <p className="text-gray-500 mt-1">Manage your sales opportunities and deals</p>
            </div>
            <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
              <TrendingUp className="w-4 h-4 mr-2" />
              New Opportunity
            </Button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Pipeline Value</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">${(totalValue / 1000).toFixed(0)}K</div>
                <p className="text-xs text-muted-foreground">
                  {filteredOpportunities.length} opportunities
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Weighted Value</CardTitle>
                <Target className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">${(weightedValue / 1000).toFixed(0)}K</div>
                <p className="text-xs text-muted-foreground">
                  Based on probability
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Won This Month</CardTitle>
                <CheckCircle2 className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">
                  ${(wonValue / 1000).toFixed(0)}K
                </div>
                <p className="text-xs text-muted-foreground">
                  {wonDeals.length} deals closed
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Win Rate</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">65%</div>
                <p className="text-xs text-muted-foreground">
                  Last 90 days
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Filters */}
          <Card>
            <CardContent className="p-4">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    type="text"
                    placeholder="Search opportunities..."
                    className="pl-10"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="outline" size="sm">
                      Stage: {selectedStage === 'all' ? 'All' : stages.find(s => s.id === selectedStage)?.name}
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => setSelectedStage('all')}>
                      All Stages
                    </DropdownMenuItem>
                    {stages.map((stage) => (
                      <DropdownMenuItem key={stage.id} onClick={() => setSelectedStage(stage.id)}>
                        {stage.name}
                      </DropdownMenuItem>
                    ))}
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </CardContent>
          </Card>

          {/* Opportunities List */}
          <div className="space-y-4">
            {filteredOpportunities.map((opp) => {
              const stage = stages.find(s => s.id === opp.stage);
              const today = new Date();
              const closeDate = new Date(opp.closeDate);
              const sevenDaysFromNow = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
              const isClosingSoon = closeDate < sevenDaysFromNow;
              
              return (
                <Card key={opp.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                      <div className="flex-1 space-y-3">
                        <div className="flex items-start justify-between">
                          <div>
                            <h3 className="font-semibold text-lg text-gray-900">{opp.name}</h3>
                            <div className="flex items-center gap-2 mt-1">
                              <Building2 className="w-4 h-4 text-gray-400" />
                              <span className="text-sm text-gray-600">{opp.company}</span>
                            </div>
                          </div>
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                                <MoreVertical className="w-4 h-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuItem>Edit</DropdownMenuItem>
                              <DropdownMenuItem>View Details</DropdownMenuItem>
                              <DropdownMenuItem>Add Activity</DropdownMenuItem>
                              <DropdownMenuItem className="text-red-600">Delete</DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </div>

                        <div className="flex flex-wrap items-center gap-4 text-sm">
                          <div className="flex items-center gap-1">
                            <DollarSign className="w-4 h-4 text-gray-400" />
                            <span className="font-semibold">${opp.value.toLocaleString()}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Target className="w-4 h-4 text-gray-400" />
                            <span>{opp.probability}% probability</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Calendar className={`w-4 h-4 ${isClosingSoon ? 'text-orange-500' : 'text-gray-400'}`} />
                            <span className={isClosingSoon ? 'text-orange-600 font-medium' : ''}>
                              {new Date(opp.closeDate).toLocaleDateString()}
                            </span>
                          </div>
                          <div className="flex items-center gap-1">
                            <User className="w-4 h-4 text-gray-400" />
                            <span>{opp.owner}</span>
                          </div>
                        </div>
                      </div>

                      <div className="flex flex-row lg:flex-col items-center lg:items-end gap-3 lg:gap-2">
                        <Badge className={stage?.color}>
                          {stage?.name}
                        </Badge>
                        <div className="text-right">
                          <div className="text-sm font-medium text-gray-600">Expected</div>
                          <div className="text-lg font-bold text-blue-600">
                            ${((opp.value * opp.probability) / 100 / 1000).toFixed(1)}K
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="mt-4">
                      <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                        <span>Pipeline Progress</span>
                        <span>{opp.probability}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${
                            opp.stage === 'closed-won' ? 'bg-green-600' :
                            opp.stage === 'closed-lost' ? 'bg-red-600' :
                            'bg-blue-600'
                          }`}
                          style={{ width: `${opp.probability}%` }}
                        ></div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {filteredOpportunities.length === 0 && (
            <Card>
              <CardContent className="p-12 text-center">
                <TrendingUp className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No opportunities found matching your criteria.</p>
              </CardContent>
            </Card>
          )}
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
