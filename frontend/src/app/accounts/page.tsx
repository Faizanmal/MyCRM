'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  Building2,
  Plus,
  Search,
  Filter,
  MoreVertical,
  Edit,
  Trash2,
  Globe,
  Phone,
  Users,
  ShieldCheck,
  TrendingUp,
  RefreshCw,
  GitMerge,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
  AlertCircle
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
  DropdownMenuLabel,
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
import { accountsAPI } from '@/lib/api';

interface Account {
  id: number;
  name: string;
  domain?: string;
  industry?: string;
  tier?: string;
  account_type?: string;
  phone?: string;
  website?: string;
  city?: string;
  country?: string;
  annual_revenue?: number;
  health_score?: number;
  contacts_count?: number;
  is_merged?: boolean;
  created_at: string;
}

interface Stats {
  total: number;
  customers: number;
  prospects: number;
  avg_health: number;
}

export default function AccountsPage() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [stats, setStats] = useState<Stats>({ total: 0, customers: 0, prospects: 0, avg_health: 0 });
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [tierFilter, setTierFilter] = useState('all');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Create / Edit modal state
  const [isAccountDialogOpen, setIsAccountDialogOpen] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState<Account | null>(null);
  const [accountFormData, setAccountFormData] = useState({
    name: '',
    domain: '',
    industry: '',
    tier: 'smb',
    account_type: 'prospect',
    phone: '',
    website: '',
    city: '',
    country: '',
  });

  // Merge modal state
  const [isMergeDialogOpen, setIsMergeDialogOpen] = useState(false);
  const [primaryAccount, setPrimaryAccount] = useState<Account | null>(null);
  const [secondaryAccountId, setSecondaryAccountId] = useState<string>('');

  const fetchAccounts = useCallback(async () => {
    setIsLoading(true);
    try {
      const params: Record<string, unknown> = {
        page,
        search: searchQuery || undefined,
      };
      if (tierFilter !== 'all') {
        params.tier = tierFilter;
      }
      const data = await accountsAPI.getAccounts(params);
      const results: Account[] = data.results || data;
      setAccounts(results.filter((a) => !a.is_merged));
      if (data.count) {
        setTotalPages(Math.ceil(data.count / 20));
      }

      // Calculate stats locally or fetch
      const total = data.count || results.length;
      const customers = results.filter((a) => a.account_type === 'customer').length;
      const prospects = results.filter((a) => a.account_type === 'prospect').length;
      const avg_health =
        results.length > 0
          ? Math.round(results.reduce((acc, a) => acc + (a.health_score || 50), 0) / results.length)
          : 0;
      setStats({ total, customers, prospects, avg_health });
    } catch (err: unknown) {
      console.error('Failed to load accounts:', err);
      toast.error('Failed to load accounts. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [page, searchQuery, tierFilter]);

  useEffect(() => {
    fetchAccounts();
  }, [fetchAccounts]);

  const handleOpenCreateModal = () => {
    setSelectedAccount(null);
    setAccountFormData({
      name: '',
      domain: '',
      industry: '',
      tier: 'smb',
      account_type: 'prospect',
      phone: '',
      website: '',
      city: '',
      country: '',
    });
    setIsAccountDialogOpen(true);
  };

  const handleOpenEditModal = (account: Account) => {
    setSelectedAccount(account);
    setAccountFormData({
      name: account.name,
      domain: account.domain || '',
      industry: account.industry || '',
      tier: account.tier || 'smb',
      account_type: account.account_type || 'prospect',
      phone: account.phone || '',
      website: account.website || '',
      city: account.city || '',
      country: account.country || '',
    });
    setIsAccountDialogOpen(true);
  };

  const handleSaveAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!accountFormData.name.trim()) {
      toast.error('Account name is required.');
      return;
    }

    setIsSubmitting(true);
    try {
      if (selectedAccount) {
        await accountsAPI.updateAccount(selectedAccount.id, accountFormData);
        toast.success(`Account "${accountFormData.name}" updated successfully.`);
      } else {
        await accountsAPI.createAccount(accountFormData);
        toast.success(`Account "${accountFormData.name}" created successfully.`);
      }
      setIsAccountDialogOpen(false);
      fetchAccounts();
    } catch (err: unknown) {
      console.error('Error saving account:', err);
      toast.error('Failed to save account. Ensure tenant credentials are valid.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteAccount = async (id: number, name: string) => {
    if (!confirm(`Are you sure you want to delete "${name}"?`)) return;
    try {
      await accountsAPI.deleteAccount(id);
      toast.success(`Account "${name}" deleted successfully.`);
      fetchAccounts();
    } catch (err: unknown) {
      console.error('Error deleting account:', err);
      toast.error('Failed to delete account.');
    }
  };

  const handleOpenMergeModal = (account: Account) => {
    setPrimaryAccount(account);
    setSecondaryAccountId('');
    setIsMergeDialogOpen(true);
  };

  const handleExecuteMerge = async () => {
    if (!primaryAccount || !secondaryAccountId) {
      toast.error('Please select an account to merge into this one.');
      return;
    }
    const secId = parseInt(secondaryAccountId, 10);
    if (isNaN(secId) || secId === primaryAccount.id) {
      toast.error('Cannot merge an account into itself.');
      return;
    }

    setIsSubmitting(true);
    try {
      const res = await accountsAPI.mergeAccounts(primaryAccount.id, secId);
      toast.success(res.message || 'Accounts merged successfully.');
      setIsMergeDialogOpen(false);
      fetchAccounts();
    } catch (err: unknown) {
      console.error('Merge failed:', err);
      toast.error('Failed to merge accounts. Verify both accounts belong to this tenant.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getHealthBadge = (score?: number) => {
    const val = score || 50;
    if (val >= 80) return <Badge className="bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/20">{val}% High</Badge>;
    if (val >= 50) return <Badge className="bg-amber-500/15 text-amber-600 dark:text-amber-400 border-amber-500/20">{val}% Medium</Badge>;
    return <Badge className="bg-rose-500/15 text-rose-600 dark:text-rose-400 border-rose-500/20">{val}% At Risk</Badge>;
  };

  const getTierBadge = (tier?: string) => {
    switch (tier) {
      case 'enterprise':
        return <Badge variant="secondary" className="bg-purple-500/15 text-purple-600 border-purple-500/20">Enterprise</Badge>;
      case 'mid_market':
        return <Badge variant="secondary" className="bg-blue-500/15 text-blue-600 border-blue-500/20">Mid Market</Badge>;
      case 'key_account':
        return <Badge variant="secondary" className="bg-indigo-500/15 text-indigo-600 border-indigo-500/20">Key Account</Badge>;
      default:
        return <Badge variant="outline">SMB</Badge>;
    }
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="space-y-6 p-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Accounts</h1>
              <p className="text-muted-foreground">
                Manage business accounts, corporate hierarchies, and customer health
              </p>
            </div>
            <div className="flex items-center gap-3">
              <Button variant="outline" size="sm" onClick={() => fetchAccounts()} disabled={isLoading}>
                <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
              <Button onClick={handleOpenCreateModal} size="sm">
                <Plus className="h-4 w-4 mr-2" />
                Add Account
              </Button>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Total Accounts</CardTitle>
                <Building2 className="h-4 w-4 text-primary" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.total}</div>
                <p className="text-xs text-muted-foreground mt-1">Active in current tenant</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Customers</CardTitle>
                <ShieldCheck className="h-4 w-4 text-emerald-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.customers}</div>
                <p className="text-xs text-muted-foreground mt-1">Contract signed</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Prospects</CardTitle>
                <TrendingUp className="h-4 w-4 text-blue-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.prospects}</div>
                <p className="text-xs text-muted-foreground mt-1">Pipeline opportunities</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Avg Health Score</CardTitle>
                <Users className="h-4 w-4 text-purple-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.avg_health}%</div>
                <p className="text-xs text-muted-foreground mt-1">Engagement index</p>
              </CardContent>
            </Card>
          </div>

          {/* Search & Filter Bar */}
          <div className="flex flex-col sm:flex-row gap-4 justify-between items-center bg-card p-4 rounded-lg border shadow-sm">
            <div className="relative w-full sm:w-96">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by account name, domain, industry..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setPage(1);
                }}
                className="pl-9"
              />
            </div>
            <div className="flex items-center gap-3 w-full sm:w-auto">
              <Filter className="h-4 w-4 text-muted-foreground" />
              <select
                className="text-sm bg-background border rounded-md px-3 py-2"
                value={tierFilter}
                onChange={(e) => {
                  setTierFilter(e.target.value);
                  setPage(1);
                }}
              >
                <option value="all">All Tiers</option>
                <option value="smb">SMB</option>
                <option value="mid_market">Mid Market</option>
                <option value="enterprise">Enterprise</option>
                <option value="key_account">Key Account</option>
              </select>
            </div>
          </div>

          {/* Accounts Table */}
          <Card>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                  <thead className="bg-muted/50 border-b text-muted-foreground uppercase text-xs font-semibold">
                    <tr>
                      <th className="px-6 py-4">Account Name</th>
                      <th className="px-6 py-4">Domain / Web</th>
                      <th className="px-6 py-4">Tier</th>
                      <th className="px-6 py-4">Type</th>
                      <th className="px-6 py-4">Health</th>
                      <th className="px-6 py-4">Location</th>
                      <th className="px-6 py-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {isLoading ? (
                      Array.from({ length: 5 }).map((_, i) => (
                        <tr key={i}>
                          <td colSpan={7} className="px-6 py-4">
                            <Skeleton className="h-6 w-full" />
                          </td>
                        </tr>
                      ))
                    ) : accounts.length === 0 ? (
                      <tr>
                        <td colSpan={7} className="px-6 py-12 text-center text-muted-foreground">
                          <Building2 className="h-10 w-10 mx-auto mb-3 opacity-30" />
                          <p className="font-medium">No accounts found</p>
                          <p className="text-xs mt-1">Get started by creating your first business account.</p>
                        </td>
                      </tr>
                    ) : (
                      accounts.map((account) => (
                        <tr key={account.id} className="hover:bg-muted/40 transition-colors">
                          <td className="px-6 py-4 font-medium text-foreground">
                            <div className="flex items-center gap-2">
                              <Building2 className="h-4 w-4 text-muted-foreground" />
                              <span>{account.name}</span>
                            </div>
                            {account.industry && (
                              <span className="text-xs text-muted-foreground block ml-6">
                                {account.industry}
                              </span>
                            )}
                          </td>
                          <td className="px-6 py-4 text-muted-foreground">
                            {account.domain ? (
                              <div className="flex items-center gap-1.5 text-xs">
                                <Globe className="h-3.5 w-3.5" />
                                <span>{account.domain}</span>
                              </div>
                            ) : (
                              '—'
                            )}
                          </td>
                          <td className="px-6 py-4">{getTierBadge(account.tier)}</td>
                          <td className="px-6 py-4 capitalize text-xs">
                            <Badge variant="outline">{account.account_type || 'Prospect'}</Badge>
                          </td>
                          <td className="px-6 py-4">{getHealthBadge(account.health_score)}</td>
                          <td className="px-6 py-4 text-xs text-muted-foreground">
                            {[account.city, account.country].filter(Boolean).join(', ') || '—'}
                          </td>
                          <td className="px-6 py-4 text-right">
                            <DropdownMenu>
                              <DropdownMenuTrigger asChild>
                                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                                  <MoreVertical className="h-4 w-4" />
                                </Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent align="end">
                                <DropdownMenuLabel>Actions</DropdownMenuLabel>
                                <DropdownMenuItem onClick={() => handleOpenEditModal(account)}>
                                  <Edit className="h-4 w-4 mr-2" /> Edit Details
                                </DropdownMenuItem>
                                <DropdownMenuItem onClick={() => handleOpenMergeModal(account)}>
                                  <GitMerge className="h-4 w-4 mr-2" /> Merge Account
                                </DropdownMenuItem>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem
                                  className="text-rose-600 focus:text-rose-600"
                                  onClick={() => handleDeleteAccount(account.id, account.name)}
                                >
                                  <Trash2 className="h-4 w-4 mr-2" /> Delete
                                </DropdownMenuItem>
                              </DropdownMenuContent>
                            </DropdownMenu>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-end items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
              >
                <ChevronLeft className="h-4 w-4" /> Previous
              </Button>
              <span className="text-xs text-muted-foreground">
                Page {page} of {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
              >
                Next <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          )}

          {/* Create / Edit Dialog */}
          <Dialog open={isAccountDialogOpen} onOpenChange={setIsAccountDialogOpen}>
            <DialogContent className="sm:max-w-lg">
              <DialogHeader>
                <DialogTitle>{selectedAccount ? 'Edit Account' : 'Create Business Account'}</DialogTitle>
                <DialogDescription>
                  Enter company credentials and corporate details for this account.
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleSaveAccount} className="space-y-4 py-2">
                <div className="grid grid-cols-2 gap-4">
                  <div className="col-span-2 space-y-1">
                    <Label htmlFor="account-name">Company Name *</Label>
                    <Input
                      id="account-name"
                      required
                      placeholder="e.g. Acme Corporation"
                      value={accountFormData.name}
                      onChange={(e) => setAccountFormData({ ...accountFormData, name: e.target.value })}
                    />
                  </div>
                  <div className="space-y-1">
                    <Label htmlFor="account-domain">Domain</Label>
                    <Input
                      id="account-domain"
                      placeholder="acme.com"
                      value={accountFormData.domain}
                      onChange={(e) => setAccountFormData({ ...accountFormData, domain: e.target.value })}
                    />
                  </div>
                  <div className="space-y-1">
                    <Label htmlFor="account-industry">Industry</Label>
                    <Input
                      id="account-industry"
                      placeholder="Technology / SaaS"
                      value={accountFormData.industry}
                      onChange={(e) => setAccountFormData({ ...accountFormData, industry: e.target.value })}
                    />
                  </div>
                  <div className="space-y-1">
                    <Label htmlFor="account-tier">Tier</Label>
                    <select
                      id="account-tier"
                      className="w-full text-sm bg-background border rounded-md px-3 py-2"
                      value={accountFormData.tier}
                      onChange={(e) => setAccountFormData({ ...accountFormData, tier: e.target.value })}
                    >
                      <option value="smb">SMB</option>
                      <option value="mid_market">Mid Market</option>
                      <option value="enterprise">Enterprise</option>
                      <option value="key_account">Key Account</option>
                    </select>
                  </div>
                  <div className="space-y-1">
                    <Label htmlFor="account-type">Account Type</Label>
                    <select
                      id="account-type"
                      className="w-full text-sm bg-background border rounded-md px-3 py-2"
                      value={accountFormData.account_type}
                      onChange={(e) => setAccountFormData({ ...accountFormData, account_type: e.target.value })}
                    >
                      <option value="prospect">Prospect</option>
                      <option value="customer">Customer</option>
                      <option value="partner">Partner</option>
                      <option value="vendor">Vendor</option>
                    </select>
                  </div>
                  <div className="space-y-1">
                    <Label htmlFor="account-city">City</Label>
                    <Input
                      id="account-city"
                      placeholder="San Francisco"
                      value={accountFormData.city}
                      onChange={(e) => setAccountFormData({ ...accountFormData, city: e.target.value })}
                    />
                  </div>
                  <div className="space-y-1">
                    <Label htmlFor="account-country">Country</Label>
                    <Input
                      id="account-country"
                      placeholder="United States"
                      value={accountFormData.country}
                      onChange={(e) => setAccountFormData({ ...accountFormData, country: e.target.value })}
                    />
                  </div>
                </div>
                <DialogFooter className="mt-4">
                  <Button type="button" variant="outline" onClick={() => setIsAccountDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button type="submit" disabled={isSubmitting}>
                    {isSubmitting ? 'Saving...' : selectedAccount ? 'Update Account' : 'Create Account'}
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>

          {/* Merge Accounts Dialog */}
          <Dialog open={isMergeDialogOpen} onOpenChange={setIsMergeDialogOpen}>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  <GitMerge className="h-5 w-5 text-purple-500" />
                  Merge Account
                </DialogTitle>
                <DialogDescription>
                  Merge a secondary account into{' '}
                  <span className="font-semibold text-foreground">{primaryAccount?.name}</span>.
                  All contacts and activities will be repointed to this primary account.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-3">
                <div className="space-y-1">
                  <Label htmlFor="secondary-account">Select Secondary Account to Merge</Label>
                  <select
                    id="secondary-account"
                    className="w-full text-sm bg-background border rounded-md px-3 py-2"
                    value={secondaryAccountId}
                    onChange={(e) => setSecondaryAccountId(e.target.value)}
                  >
                    <option value="">-- Choose Account --</option>
                    {accounts
                      .filter((a) => a.id !== primaryAccount?.id)
                      .map((a) => (
                        <option key={a.id} value={a.id}>
                          {a.name} ({a.domain || 'no domain'})
                        </option>
                      ))}
                  </select>
                </div>
                <div className="bg-amber-500/10 border border-amber-500/20 text-amber-700 dark:text-amber-300 text-xs p-3 rounded-md flex items-start gap-2">
                  <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
                  <span>
                    This action marks the secondary account as merged and archives it. All relations
                    are atomically repointed and audited.
                  </span>
                </div>
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setIsMergeDialogOpen(false)}>
                  Cancel
                </Button>
                <Button
                  type="button"
                  onClick={handleExecuteMerge}
                  disabled={!secondaryAccountId || isSubmitting}
                  className="bg-purple-600 hover:bg-purple-700"
                >
                  {isSubmitting ? 'Merging...' : 'Confirm Merge'}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
