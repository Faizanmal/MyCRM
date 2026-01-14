'use client';

import { useState, useEffect, useCallback } from 'react';
import { 
  TrendingUp, 
  Search,
  MoreVertical,
  DollarSign,
  Calendar,
  Building2,
  User,
  Target,
  CheckCircle2,
  RefreshCw,
  AlertCircle,
  Plus,
  ChevronLeft,
  ChevronRight,
  Trash2,
  Edit
} from 'lucide-react';
import { toast } from 'sonner';

import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { opportunitiesAPI } from '@/lib/api';


interface Opportunity {
  id: number;
  name: string;
  company_name?: string;
  account_name?: string;
  value: number;
  amount?: number;
  stage: string;
  probability: number;
  expected_close_date: string;
  close_date?: string;
  owner_name?: string;
  contact_name?: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

interface PaginatedResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Opportunity[];
}

const stages = [
  { id: 'prospecting', name: 'Prospecting', color: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300' },
  { id: 'qualification', name: 'Qualification', color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300' },
  { id: 'proposal', name: 'Proposal', color: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300' },
  { id: 'negotiation', name: 'Negotiation', color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300' },
  { id: 'closed_won', name: 'Closed Won', color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' },
  { id: 'closed_lost', name: 'Closed Lost', color: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300' },
];

export default function OpportunitiesPage() {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStage, setSelectedStage] = useState<string>('all');
  const [error, setError] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(20);

  // Dialog states
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [selectedOpportunity, setSelectedOpportunity] = useState<Opportunity | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    value: '',
    stage: 'prospecting',
    probability: '20',
    expected_close_date: '',
    description: '',
  });

  const fetchOpportunities = useCallback(async (showRefreshing = false) => {
    try {
      if (showRefreshing) setIsRefreshing(true);
      setError(null);

      const params: Record<string, unknown> = {
        page: currentPage,
        page_size: pageSize,
      };

      if (searchQuery) {
        params.search = searchQuery;
      }

      if (selectedStage !== 'all') {
        params.stage = selectedStage;
      }

      const response: PaginatedResponse = await opportunitiesAPI.getOpportunities(params);
      
      setOpportunities(response.results || []);
      setTotalCount(response.count || 0);
    } catch (err) {
      console.error('Error fetching opportunities:', err);
      setError('Failed to load opportunities');
      toast.error('Failed to load opportunities');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, [currentPage, pageSize, searchQuery, selectedStage]);

  useEffect(() => {
    fetchOpportunities();
  }, [fetchOpportunities]);

  useEffect(() => {
    const timer = setTimeout(() => {
      setCurrentPage(1);
      fetchOpportunities();
    }, 300);
    return () => clearTimeout(timer);

  }, [searchQuery, selectedStage, fetchOpportunities]);

  const handleRefresh = () => {
    fetchOpportunities(true);
  };

  const handleCreateOpportunity = async () => {
    try {
      setIsSubmitting(true);
      await opportunitiesAPI.createOpportunity({
        ...formData,
        value: parseFloat(formData.value) || 0,
        probability: parseInt(formData.probability) || 0,
      });
      toast.success('Opportunity created successfully');
      setIsCreateDialogOpen(false);
      resetForm();
      fetchOpportunities();
    } catch (err) {
      console.error('Error creating opportunity:', err);
      toast.error('Failed to create opportunity');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteOpportunity = async () => {
    if (!selectedOpportunity) return;
    
    try {
      setIsSubmitting(true);
      await opportunitiesAPI.deleteOpportunity(selectedOpportunity.id);
      toast.success('Opportunity deleted successfully');
      setIsDeleteDialogOpen(false);
      setSelectedOpportunity(null);
      fetchOpportunities();
    } catch (err) {
      console.error('Error deleting opportunity:', err);
      toast.error('Failed to delete opportunity');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleStageChange = async (opportunity: Opportunity, newStage: string) => {
    try {
      await opportunitiesAPI.updateStage(opportunity.id, newStage);
      toast.success('Stage updated successfully');
      fetchOpportunities();
    } catch (err) {
      console.error('Error updating stage:', err);
      toast.error('Failed to update stage');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      value: '',
      stage: 'prospecting',
      probability: '20',
      expected_close_date: '',
      description: '',
    });
  };

  const getOpportunityValue = (opp: Opportunity) => opp.value || opp.amount || 0;
  const getOpportunityCloseDate = (opp: Opportunity) => opp.expected_close_date || opp.close_date || '';
  const getCompanyName = (opp: Opportunity) => opp.company_name || opp.account_name || 'N/A';

  const formatCurrency = (value: number) => {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    } else if (value >= 1000) {
      return `$${(value / 1000).toFixed(0)}K`;
    }
    return `$${value.toLocaleString()}`;
  };

  const totalValue = opportunities.reduce((sum, opp) => sum + getOpportunityValue(opp), 0);
  const weightedValue = opportunities.reduce(
    (sum, opp) => sum + (getOpportunityValue(opp) * (opp.probability || 0) / 100),
    0
  );
  const wonDeals = opportunities.filter(o => o.stage === 'closed_won' || o.stage === 'closed-won');
  const wonValue = wonDeals.reduce((sum, opp) => sum + getOpportunityValue(opp), 0);
  const totalPages = Math.ceil(totalCount / pageSize);

  if (error && opportunities.length === 0) {
    return (
      <ProtectedRoute>
        <MainLayout>
          <div className="p-6">
            <Card className="p-8 text-center">
              <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <h2 className="text-xl font-semibold mb-2">Failed to Load Opportunities</h2>
              <p className="text-muted-foreground mb-4">{error}</p>
              <Button onClick={handleRefresh}>
                <RefreshCw className="w-4 h-4 mr-2" />
                Try Again
              </Button>
            </Card>
          </div>
        </MainLayout>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-4 lg:p-6 space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-2xl lg:text-3xl font-bold">Opportunities</h1>
              <p className="text-muted-foreground mt-1">Manage your sales opportunities and deals</p>
            </div>
            <div className="flex items-center gap-2">
              <Button 
                variant="outline" 
                size="sm"
                onClick={handleRefresh}
                disabled={isRefreshing}
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
              <Button 
                size="sm" 
                className="bg-blue-600 hover:bg-blue-700"
                onClick={() => setIsCreateDialogOpen(true)}
              >
                <Plus className="w-4 h-4 mr-2" />
                New Opportunity
              </Button>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Pipeline Value</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <Skeleton className="h-8 w-24" />
                ) : (
                  <div className="text-2xl font-bold">{formatCurrency(totalValue)}</div>
                )}
                <p className="text-xs text-muted-foreground">
                  {totalCount} opportunities
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Weighted Value</CardTitle>
                <Target className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <Skeleton className="h-8 w-24" />
                ) : (
                  <div className="text-2xl font-bold">{formatCurrency(weightedValue)}</div>
                )}
                <p className="text-xs text-muted-foreground">Based on probability</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Won Deals</CardTitle>
                <CheckCircle2 className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <Skeleton className="h-8 w-24" />
                ) : (
                  <div className="text-2xl font-bold text-green-600">{formatCurrency(wonValue)}</div>
                )}
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
                {isLoading ? (
                  <Skeleton className="h-8 w-16" />
                ) : (
                  <div className="text-2xl font-bold">
                    {opportunities.length > 0 
                      ? Math.round((wonDeals.length / opportunities.length) * 100)
                      : 0}%
                  </div>
                )}
                <p className="text-xs text-muted-foreground">Current period</p>
              </CardContent>
            </Card>
          </div>

          {/* Filters */}
          <Card>
            <CardContent className="p-4">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
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
                      Stage: {selectedStage === 'all' ? 'All' : stages.find(s => s.id === selectedStage)?.name || selectedStage}
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
          {isLoading ? (
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <Card key={i}>
                  <CardContent className="p-6">
                    <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                      <div className="flex-1 space-y-3">
                        <Skeleton className="h-6 w-3/4" />
                        <Skeleton className="h-4 w-1/2" />
                        <Skeleton className="h-4 w-2/3" />
                      </div>
                      <Skeleton className="h-10 w-24" />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : opportunities.length > 0 ? (
            <>
              <div className="space-y-4">
                {opportunities.map((opp) => {
                  const stage = stages.find(s => s.id === opp.stage || s.id === opp.stage?.replace('-', '_'));
                  const closeDate = getOpportunityCloseDate(opp);
                  const today = new Date();
                  const parsedCloseDate = closeDate ? new Date(closeDate) : null;
                  const sevenDaysFromNow = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
                  const isClosingSoon = parsedCloseDate && parsedCloseDate < sevenDaysFromNow && opp.stage !== 'closed_won' && opp.stage !== 'closed_lost';
                  const oppValue = getOpportunityValue(opp);
                  
                  return (
                    <Card key={opp.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-6">
                        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                          <div className="flex-1 space-y-3">
                            <div className="flex items-start justify-between">
                              <div>
                                <h3 className="font-semibold text-lg">{opp.name}</h3>
                                <div className="flex items-center gap-2 mt-1">
                                  <Building2 className="w-4 h-4 text-muted-foreground" />
                                  <span className="text-sm text-muted-foreground">{getCompanyName(opp)}</span>
                                </div>
                              </div>
                              <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                                    <MoreVertical className="w-4 h-4" />
                                  </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end">
                                  <DropdownMenuItem>
                                    <Edit className="w-4 h-4 mr-2" />
                                    Edit
                                  </DropdownMenuItem>
                                  <DropdownMenuSeparator />
                                  <DropdownMenuItem className="p-0">
                                    <DropdownMenu>
                                      <DropdownMenuTrigger className="flex items-center w-full px-2 py-1.5">
                                        Move to Stage
                                      </DropdownMenuTrigger>
                                      <DropdownMenuContent side="right">
                                        {stages.map((s) => (
                                          <DropdownMenuItem 
                                            key={s.id} 
                                            onClick={() => handleStageChange(opp, s.id)}
                                          >
                                            {s.name}
                                          </DropdownMenuItem>
                                        ))}
                                      </DropdownMenuContent>
                                    </DropdownMenu>
                                  </DropdownMenuItem>
                                  <DropdownMenuSeparator />
                                  <DropdownMenuItem 
                                    className="text-red-600"
                                    onClick={() => {
                                      setSelectedOpportunity(opp);
                                      setIsDeleteDialogOpen(true);
                                    }}
                                  >
                                    <Trash2 className="w-4 h-4 mr-2" />
                                    Delete
                                  </DropdownMenuItem>
                                </DropdownMenuContent>
                              </DropdownMenu>
                            </div>

                            <div className="flex flex-wrap items-center gap-4 text-sm">
                              <div className="flex items-center gap-1">
                                <DollarSign className="w-4 h-4 text-muted-foreground" />
                                <span className="font-semibold">{formatCurrency(oppValue)}</span>
                              </div>
                              <div className="flex items-center gap-1">
                                <Target className="w-4 h-4 text-muted-foreground" />
                                <span>{opp.probability || 0}% probability</span>
                              </div>
                              {closeDate && (
                                <div className="flex items-center gap-1">
                                  <Calendar className={`w-4 h-4 ${isClosingSoon ? 'text-orange-500' : 'text-muted-foreground'}`} />
                                  <span className={isClosingSoon ? 'text-orange-600 font-medium' : ''}>
                                    {new Date(closeDate).toLocaleDateString()}
                                  </span>
                                </div>
                              )}
                              {opp.owner_name && (
                                <div className="flex items-center gap-1">
                                  <User className="w-4 h-4 text-muted-foreground" />
                                  <span>{opp.owner_name}</span>
                                </div>
                              )}
                            </div>
                          </div>

                          <div className="flex flex-row lg:flex-col items-center lg:items-end gap-3 lg:gap-2">
                            <Badge className={stage?.color || 'bg-gray-100 text-gray-800'}>
                              {stage?.name || opp.stage}
                            </Badge>
                            <div className="text-right">
                              <div className="text-sm font-medium text-muted-foreground">Expected</div>
                              <div className="text-lg font-bold text-blue-600">
                                {formatCurrency((oppValue * (opp.probability || 0)) / 100)}
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* Progress Bar */}
                        <div className="mt-4">
                          <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
                            <span>Pipeline Progress</span>
                            <span>{opp.probability || 0}%</span>
                          </div>
                          <div className="w-full bg-secondary rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full ${
                                opp.stage === 'closed_won' || opp.stage === 'closed-won' ? 'bg-green-600' :
                                opp.stage === 'closed_lost' || opp.stage === 'closed-lost' ? 'bg-red-600' :
                                'bg-blue-600'
                              }`}
                              style={{ width: `${opp.probability || 0}%` }}
                            ></div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between">
                  <p className="text-sm text-muted-foreground">
                    Showing {(currentPage - 1) * pageSize + 1} to {Math.min(currentPage * pageSize, totalCount)} of {totalCount} opportunities
                  </p>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                    >
                      <ChevronLeft className="w-4 h-4" />
                    </Button>
                    <span className="text-sm">
                      Page {currentPage} of {totalPages}
                    </span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                      disabled={currentPage === totalPages}
                    >
                      <ChevronRight className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              )}
            </>
          ) : (
            <Card>
              <CardContent className="p-12 text-center">
                <TrendingUp className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No opportunities found</h3>
                <p className="text-muted-foreground mb-4">
                  {searchQuery || selectedStage !== 'all' 
                    ? 'Try adjusting your search or filters'
                    : 'Get started by creating your first opportunity'}
                </p>
                <Button onClick={() => setIsCreateDialogOpen(true)}>
                  <Plus className="w-4 h-4 mr-2" />
                  New Opportunity
                </Button>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Create Opportunity Dialog */}
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogContent className="sm:max-w-[500px]">
            <DialogHeader>
              <DialogTitle>Create New Opportunity</DialogTitle>
              <DialogDescription>
                Add a new sales opportunity to your pipeline.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="name">Opportunity Name</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g., Enterprise License - Q4"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="value">Value ($)</Label>
                  <Input
                    id="value"
                    type="number"
                    value={formData.value}
                    onChange={(e) => setFormData({ ...formData, value: e.target.value })}
                    placeholder="50000"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="probability">Probability (%)</Label>
                  <Input
                    id="probability"
                    type="number"
                    min="0"
                    max="100"
                    value={formData.probability}
                    onChange={(e) => setFormData({ ...formData, probability: e.target.value })}
                    placeholder="50"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="stage">Stage</Label>
                  <Select value={formData.stage} onValueChange={(v) => setFormData({ ...formData, stage: v })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select stage" />
                    </SelectTrigger>
                    <SelectContent>
                      {stages.map((stage) => (
                        <SelectItem key={stage.id} value={stage.id}>
                          {stage.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="expected_close_date">Expected Close Date</Label>
                  <Input
                    id="expected_close_date"
                    type="date"
                    value={formData.expected_close_date}
                    onChange={(e) => setFormData({ ...formData, expected_close_date: e.target.value })}
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Additional details about this opportunity..."
                  rows={3}
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleCreateOpportunity} disabled={isSubmitting || !formData.name}>
                {isSubmitting ? 'Creating...' : 'Create Opportunity'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Delete Confirmation Dialog */}
        <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Delete Opportunity</DialogTitle>
              <DialogDescription>
                Are you sure you want to delete &quot;{selectedOpportunity?.name}&quot;? 
                This action cannot be undone.
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsDeleteDialogOpen(false)}>
                Cancel
              </Button>
              <Button variant="destructive" onClick={handleDeleteOpportunity} disabled={isSubmitting}>
                {isSubmitting ? 'Deleting...' : 'Delete'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </MainLayout>
    </ProtectedRoute>
  );
}

