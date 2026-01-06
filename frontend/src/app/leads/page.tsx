'use client';

import { useState, useEffect, useCallback } from 'react';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent } from '@/components/ui/card';
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { 
  UserPlus, 
  Search,
  MoreVertical,
  Edit,
  Trash2,
  TrendingUp,
  DollarSign,
  Star,
  Flame,
  RefreshCw,
  AlertCircle,
  ArrowRight,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { leadsAPI } from '@/lib/api';
import { toast } from 'sonner';

interface Lead {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  company: string;
  source: string;
  status: 'new' | 'contacted' | 'qualified' | 'proposal' | 'negotiation' | 'converted' | 'lost';
  estimated_value: number;
  score: number;
  city?: string;
  country?: string;
  assigned_to_name?: string;
  created_at: string;
  updated_at: string;
}

interface PaginatedResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Lead[];
}

const stages = [
  { id: 'new', name: 'New', color: 'bg-blue-50 border-blue-200 dark:bg-blue-950 dark:border-blue-800' },
  { id: 'contacted', name: 'Contacted', color: 'bg-purple-50 border-purple-200 dark:bg-purple-950 dark:border-purple-800' },
  { id: 'qualified', name: 'Qualified', color: 'bg-yellow-50 border-yellow-200 dark:bg-yellow-950 dark:border-yellow-800' },
  { id: 'proposal', name: 'Proposal', color: 'bg-orange-50 border-orange-200 dark:bg-orange-950 dark:border-orange-800' },
  { id: 'negotiation', name: 'Negotiation', color: 'bg-green-50 border-green-200 dark:bg-green-950 dark:border-green-800' },
];

export default function LeadsPage() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'kanban' | 'list'>('kanban');
  const [selectedStage] = useState<string>('all');
  const [error, setError] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(50);

  // Dialog states
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isConvertDialogOpen, setIsConvertDialogOpen] = useState(false);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    company: '',
    source: 'website',
    status: 'new',
    estimated_value: '',
    city: '',
    country: '',
  });

  const fetchLeads = useCallback(async (showRefreshing = false) => {
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
        params.status = selectedStage;
      }

      const response: PaginatedResponse = await leadsAPI.getLeads(params);
      
      setLeads(response.results || []);
      setTotalCount(response.count || 0);
    } catch (err) {
      console.error('Error fetching leads:', err);
      setError('Failed to load leads');
      toast.error('Failed to load leads');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, [currentPage, pageSize, searchQuery, selectedStage]);

  useEffect(() => {
    fetchLeads();
  }, [currentPage, pageSize, searchQuery, selectedStage, fetchLeads]);

  useEffect(() => {
    const timer = setTimeout(() => {
      setCurrentPage(1);
      fetchLeads();
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery, selectedStage, fetchLeads]);

  const handleRefresh = () => {
    fetchLeads(true);
  };

  const handleCreateLead = async () => {
    try {
      setIsSubmitting(true);
      await leadsAPI.createLead({
        ...formData,
        estimated_value: formData.estimated_value ? parseFloat(formData.estimated_value) : 0,
      });
      toast.success('Lead created successfully');
      setIsCreateDialogOpen(false);
      resetForm();
      fetchLeads();
    } catch (err) {
      console.error('Error creating lead:', err);
      toast.error('Failed to create lead');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteLead = async () => {
    if (!selectedLead) return;
    
    try {
      setIsSubmitting(true);
      await leadsAPI.deleteLead(selectedLead.id);
      toast.success('Lead deleted successfully');
      setIsDeleteDialogOpen(false);
      setSelectedLead(null);
      fetchLeads();
    } catch (err) {
      console.error('Error deleting lead:', err);
      toast.error('Failed to delete lead');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleConvertLead = async () => {
    if (!selectedLead) return;
    
    try {
      setIsSubmitting(true);
      await leadsAPI.convertLead(selectedLead.id);
      toast.success('Lead converted to opportunity successfully');
      setIsConvertDialogOpen(false);
      setSelectedLead(null);
      fetchLeads();
    } catch (err) {
      console.error('Error converting lead:', err);
      toast.error('Failed to convert lead');
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setFormData({
      first_name: '',
      last_name: '',
      email: '',
      phone: '',
      company: '',
      source: 'website',
      status: 'new',
      estimated_value: '',
      city: '',
      country: '',
    });
  };

  const getLeadsByStage = (stage: string) => {
    return leads.filter(lead => lead.status === stage);
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-400';
    if (score >= 75) return 'text-yellow-400';
    return 'text-gray-400';
  };

  const getScoreBadge = (score: number) => {
    if (score >= 90) return <span title="Hot Lead"><Flame className="w-4 h-4 text-red-500" /></span>;
    if (score >= 75) return <span title="Warm Lead"><Star className="w-4 h-4 text-yellow-500" /></span>;
    return null;
  };

  const getFullName = (lead: Lead) => {
    return `${lead.first_name || ''} ${lead.last_name || ''}`.trim() || 'Unknown';
  };

  const formatCurrency = (value: number) => {
    if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `$${(value / 1000).toFixed(0)}K`;
    return `$${value}`;
  };

  const totalPipelineValue = leads.reduce((sum, lead) => sum + (lead.estimated_value || 0), 0);
  const avgScore = leads.length > 0 
    ? Math.round(leads.reduce((sum, lead) => sum + (lead.score || 0), 0) / leads.length)
    : 0;
  const totalPages = Math.ceil(totalCount / pageSize);

  if (error && leads.length === 0) {
    return (
      <ProtectedRoute>
        <MainLayout>
          <div className="p-6">
            <Card className="p-8 text-center">
              <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <h2 className="text-xl font-semibold mb-2">Failed to Load Leads</h2>
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
              <h1 className="text-2xl lg:text-3xl font-bold">Leads</h1>
              <p className="text-muted-foreground mt-1">Track and manage your sales pipeline</p>
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
              <Button 
                size="sm" 
                className="bg-blue-600 hover:bg-blue-700"
                onClick={() => setIsCreateDialogOpen(true)}
              >
                <UserPlus className="w-4 h-4 mr-2" />
                Add Lead
              </Button>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <Card>
              <CardContent className="p-4">
                {isLoading ? (
                  <Skeleton className="h-8 w-16" />
                ) : (
                  <div className="text-2xl font-bold">{totalCount}</div>
                )}
                <p className="text-xs text-muted-foreground">Total Leads</p>
              </CardContent>
            </Card>
            {stages.slice(0, 4).map((stage) => (
              <Card key={stage.id}>
                <CardContent className="p-4">
                  {isLoading ? (
                    <Skeleton className="h-8 w-16" />
                  ) : (
                    <div className="text-2xl font-bold">{getLeadsByStage(stage.id).length}</div>
                  )}
                  <p className="text-xs text-muted-foreground">{stage.name}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Search and Pipeline Value */}
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <Input
                type="text"
                placeholder="Search leads..."
                className="pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <Card className="p-3 flex items-center gap-4 sm:min-w-[200px]">
              <DollarSign className="w-5 h-5 text-green-600" />
              <div>
                <div className="text-lg font-bold">{formatCurrency(totalPipelineValue)}</div>
                <p className="text-xs text-muted-foreground">Pipeline Value</p>
              </div>
            </Card>
            <Card className="p-3 flex items-center gap-4 sm:min-w-[150px]">
              <TrendingUp className="w-5 h-5 text-blue-600" />
              <div>
                <div className="text-lg font-bold">{avgScore}</div>
                <p className="text-xs text-muted-foreground">Avg Score</p>
              </div>
            </Card>
          </div>

          {/* Kanban View */}
          {viewMode === 'kanban' && (
            isLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                {stages.map((stage) => (
                  <div key={stage.id} className="space-y-4">
                    <Skeleton className="h-10 w-full" />
                    <Skeleton className="h-32 w-full" />
                    <Skeleton className="h-32 w-full" />
                  </div>
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                {stages.map((stage) => (
                  <div key={stage.id} className={`rounded-lg border-2 ${stage.color} p-4`}>
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold">{stage.name}</h3>
                      <Badge variant="secondary">{getLeadsByStage(stage.id).length}</Badge>
                    </div>
                    <div className="space-y-3">
                      {getLeadsByStage(stage.id).map((lead) => (
                        <Card key={lead.id} className="cursor-pointer hover:shadow-md transition-shadow">
                          <CardContent className="p-4">
                            <div className="flex items-start justify-between mb-2">
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2">
                                  <h4 className="font-medium text-sm truncate">{getFullName(lead)}</h4>
                                  {getScoreBadge(lead.score || 0)}
                                </div>
                                <p className="text-xs text-muted-foreground truncate">{lead.company || 'No company'}</p>
                              </div>
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
                                  <DropdownMenuItem onClick={() => {
                                    setSelectedLead(lead);
                                    setIsConvertDialogOpen(true);
                                  }}>
                                    <ArrowRight className="w-4 h-4 mr-2" />
                                    Convert
                                  </DropdownMenuItem>
                                  <DropdownMenuSeparator />
                                  <DropdownMenuItem 
                                    className="text-red-600"
                                    onClick={() => {
                                      setSelectedLead(lead);
                                      setIsDeleteDialogOpen(true);
                                    }}
                                  >
                                    <Trash2 className="w-4 h-4 mr-2" />
                                    Delete
                                  </DropdownMenuItem>
                                </DropdownMenuContent>
                              </DropdownMenu>
                            </div>
                            <div className="flex items-center justify-between text-xs">
                              <span className={`font-semibold ${getScoreColor(lead.score || 0)}`}>
                                Score: {lead.score || 0}
                              </span>
                              <span className="text-green-600 font-semibold">
                                {formatCurrency(lead.estimated_value || 0)}
                              </span>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                      {getLeadsByStage(stage.id).length === 0 && (
                        <p className="text-center text-sm text-muted-foreground py-4">
                          No leads in this stage
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )
          )}

          {/* List View */}
          {viewMode === 'list' && (
            isLoading ? (
              <Card>
                <CardContent className="p-6">
                  {[...Array(5)].map((_, i) => (
                    <div key={i} className="flex items-center gap-4 py-4 border-b last:border-0">
                      <Skeleton className="h-10 w-10 rounded-full" />
                      <div className="flex-1">
                        <Skeleton className="h-4 w-32 mb-2" />
                        <Skeleton className="h-3 w-48" />
                      </div>
                      <Skeleton className="h-6 w-20" />
                      <Skeleton className="h-6 w-16" />
                    </div>
                  ))}
                </CardContent>
              </Card>
            ) : leads.length > 0 ? (
              <>
                <Card>
                  <CardContent className="p-0">
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead className="bg-muted/50">
                          <tr>
                            <th className="text-left p-4 font-medium">Name</th>
                            <th className="text-left p-4 font-medium">Company</th>
                            <th className="text-left p-4 font-medium">Email</th>
                            <th className="text-left p-4 font-medium">Stage</th>
                            <th className="text-left p-4 font-medium">Score</th>
                            <th className="text-left p-4 font-medium">Value</th>
                            <th className="text-left p-4 font-medium">Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {leads.map((lead) => (
                            <tr key={lead.id} className="border-t hover:bg-muted/50">
                              <td className="p-4">
                                <div className="flex items-center gap-2">
                                  <span className="font-medium">{getFullName(lead)}</span>
                                  {getScoreBadge(lead.score || 0)}
                                </div>
                              </td>
                              <td className="p-4 text-muted-foreground">{lead.company || '-'}</td>
                              <td className="p-4 text-muted-foreground">{lead.email || '-'}</td>
                              <td className="p-4">
                                <Badge variant="outline" className="capitalize">{lead.status}</Badge>
                              </td>
                              <td className="p-4">
                                <span className={`font-semibold ${getScoreColor(lead.score || 0)}`}>
                                  {lead.score || 0}
                                </span>
                              </td>
                              <td className="p-4 font-semibold text-green-600">
                                {formatCurrency(lead.estimated_value || 0)}
                              </td>
                              <td className="p-4">
                                <DropdownMenu>
                                  <DropdownMenuTrigger asChild>
                                    <Button variant="ghost" size="sm">
                                      <MoreVertical className="w-4 h-4" />
                                    </Button>
                                  </DropdownMenuTrigger>
                                  <DropdownMenuContent align="end">
                                    <DropdownMenuItem>
                                      <Edit className="w-4 h-4 mr-2" />
                                      Edit
                                    </DropdownMenuItem>
                                    <DropdownMenuItem onClick={() => {
                                      setSelectedLead(lead);
                                      setIsConvertDialogOpen(true);
                                    }}>
                                      <ArrowRight className="w-4 h-4 mr-2" />
                                      Convert to Opportunity
                                    </DropdownMenuItem>
                                    <DropdownMenuSeparator />
                                    <DropdownMenuItem 
                                      className="text-red-600"
                                      onClick={() => {
                                        setSelectedLead(lead);
                                        setIsDeleteDialogOpen(true);
                                      }}
                                    >
                                      <Trash2 className="w-4 h-4 mr-2" />
                                      Delete
                                    </DropdownMenuItem>
                                  </DropdownMenuContent>
                                </DropdownMenu>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="flex items-center justify-between">
                    <p className="text-sm text-muted-foreground">
                      Showing {(currentPage - 1) * pageSize + 1} to {Math.min(currentPage * pageSize, totalCount)} of {totalCount} leads
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
                  <UserPlus className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No leads found</h3>
                  <p className="text-muted-foreground mb-4">
                    Get started by adding your first lead
                  </p>
                  <Button onClick={() => setIsCreateDialogOpen(true)}>
                    <UserPlus className="w-4 h-4 mr-2" />
                    Add Lead
                  </Button>
                </CardContent>
              </Card>
            )
          )}
        </div>

        {/* Create Lead Dialog */}
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogContent className="sm:max-w-[500px]">
            <DialogHeader>
              <DialogTitle>Add New Lead</DialogTitle>
              <DialogDescription>
                Enter the details for your new lead.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="first_name">First Name</Label>
                  <Input
                    id="first_name"
                    value={formData.first_name}
                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                    placeholder="John"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="last_name">Last Name</Label>
                  <Input
                    id="last_name"
                    value={formData.last_name}
                    onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                    placeholder="Doe"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="john@example.com"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="phone">Phone</Label>
                  <Input
                    id="phone"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    placeholder="+1 (555) 123-4567"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="company">Company</Label>
                  <Input
                    id="company"
                    value={formData.company}
                    onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                    placeholder="Acme Inc"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="source">Source</Label>
                  <Select value={formData.source} onValueChange={(v) => setFormData({ ...formData, source: v })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select source" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="website">Website</SelectItem>
                      <SelectItem value="referral">Referral</SelectItem>
                      <SelectItem value="linkedin">LinkedIn</SelectItem>
                      <SelectItem value="cold_call">Cold Call</SelectItem>
                      <SelectItem value="event">Event</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="estimated_value">Estimated Value ($)</Label>
                  <Input
                    id="estimated_value"
                    type="number"
                    value={formData.estimated_value}
                    onChange={(e) => setFormData({ ...formData, estimated_value: e.target.value })}
                    placeholder="10000"
                  />
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleCreateLead} disabled={isSubmitting}>
                {isSubmitting ? 'Creating...' : 'Create Lead'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Delete Confirmation Dialog */}
        <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Delete Lead</DialogTitle>
              <DialogDescription>
                Are you sure you want to delete {selectedLead ? getFullName(selectedLead) : 'this lead'}? 
                This action cannot be undone.
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsDeleteDialogOpen(false)}>
                Cancel
              </Button>
              <Button variant="destructive" onClick={handleDeleteLead} disabled={isSubmitting}>
                {isSubmitting ? 'Deleting...' : 'Delete'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Convert Lead Dialog */}
        <Dialog open={isConvertDialogOpen} onOpenChange={setIsConvertDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Convert Lead to Opportunity</DialogTitle>
              <DialogDescription>
                This will convert {selectedLead ? getFullName(selectedLead) : 'this lead'} to an opportunity 
                and create a contact record. Continue?
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsConvertDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleConvertLead} disabled={isSubmitting}>
                {isSubmitting ? 'Converting...' : 'Convert Lead'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </MainLayout>
    </ProtectedRoute>
  );
}
