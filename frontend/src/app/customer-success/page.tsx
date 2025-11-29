'use client';

import { useEffect, useState, useCallback } from 'react';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import {
  Heart,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  DollarSign,
  RefreshCw,
  Search,
  Plus,
  Calendar,
  Target,
  Activity,
  ThumbsUp,
  Sparkles,
  ArrowUpRight,
  CheckCircle2,
  XCircle,
  MessageSquare,
  Zap
} from 'lucide-react';
import { toast } from 'sonner';
import { customerSuccessAPI } from '@/lib/premium-features-api';

interface CustomerAccount {
  id: string;
  name: string;
  tier: string;
  arr: number;
  health_score: number;
  health_status: string;
  days_until_renewal: number | null;
  csm_name: string;
  onboarding_complete: boolean;
}

interface HealthScore {
  id: string;
  account_name: string;
  score: number;
  status: string;
  usage_score: number;
  engagement_score: number;
  support_score: number;
  payment_score: number;
  trend: string;
  calculated_at: string;
}

interface ChurnRisk {
  id: string;
  account_name: string;
  risk_level: string;
  risk_score: number;
  risk_factors: string[];
  recommended_actions: string[];
}

interface ExpansionOpportunity {
  id: string;
  account_name: string;
  opportunity_type: string;
  potential_arr: number;
  probability: number;
  triggers: string[];
}

interface SuccessMetrics {
  total_accounts: number;
  total_arr: number;
  healthy_accounts: number;
  at_risk_accounts: number;
  avg_health_score: number;
  nps_score: number;
  churn_rate: number;
  expansion_revenue: number;
}

export default function CustomerSuccessPage() {
  const [loading, setLoading] = useState(true);
  const [accounts, setAccounts] = useState<CustomerAccount[]>([]);
  const [healthScores, setHealthScores] = useState<HealthScore[]>([]);
  const [churnRisks, setChurnRisks] = useState<ChurnRisk[]>([]);
  const [expansions, setExpansions] = useState<ExpansionOpportunity[]>([]);
  const [metrics, setMetrics] = useState<SuccessMetrics | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      
      const [accountsRes, healthRes, churnRes, expansionRes, dashboardRes] = await Promise.all([
        customerSuccessAPI.getAccounts({ limit: 10 }),
        customerSuccessAPI.getHealthScores({ limit: 10 }),
        customerSuccessAPI.getChurnRisks({ is_resolved: false }),
        customerSuccessAPI.getExpansionOpportunities({ status: 'open' }),
        customerSuccessAPI.getDashboard()
      ]);

      setAccounts(accountsRes.data.results || []);
      setHealthScores(healthRes.data.results || []);
      setChurnRisks(churnRes.data.results || []);
      setExpansions(expansionRes.data.results || []);
      setMetrics(dashboardRes.data || null);
    } catch (error) {
      console.error('Failed to fetch customer success data:', error);
      // Demo data
      setAccounts([
        { id: '1', name: 'Acme Corporation', tier: 'enterprise', arr: 120000, health_score: 85, health_status: 'healthy', days_until_renewal: 90, csm_name: 'Sarah Wilson', onboarding_complete: true },
        { id: '2', name: 'TechStart Inc', tier: 'business', arr: 48000, health_score: 62, health_status: 'at_risk', days_until_renewal: 30, csm_name: 'Mike Chen', onboarding_complete: true },
        { id: '3', name: 'GlobalTech Ltd', tier: 'enterprise', arr: 180000, health_score: 92, health_status: 'healthy', days_until_renewal: 180, csm_name: 'Sarah Wilson', onboarding_complete: true },
        { id: '4', name: 'StartupXYZ', tier: 'professional', arr: 24000, health_score: 45, health_status: 'critical', days_until_renewal: 15, csm_name: 'John Davis', onboarding_complete: false },
      ]);
      setHealthScores([
        { id: '1', account_name: 'Acme Corporation', score: 85, status: 'healthy', usage_score: 90, engagement_score: 82, support_score: 88, payment_score: 100, trend: 'up', calculated_at: new Date().toISOString() },
        { id: '2', account_name: 'TechStart Inc', score: 62, status: 'at_risk', usage_score: 55, engagement_score: 70, support_score: 60, payment_score: 85, trend: 'down', calculated_at: new Date().toISOString() },
        { id: '3', account_name: 'GlobalTech Ltd', score: 92, status: 'healthy', usage_score: 95, engagement_score: 88, support_score: 92, payment_score: 100, trend: 'stable', calculated_at: new Date().toISOString() },
      ]);
      setChurnRisks([
        { id: '1', account_name: 'TechStart Inc', risk_level: 'high', risk_score: 78, risk_factors: ['Usage dropped 40%', 'No login in 14 days', 'Support tickets increased'], recommended_actions: ['Schedule check-in call', 'Offer training session', 'Review account plan'] },
        { id: '2', account_name: 'StartupXYZ', risk_level: 'critical', risk_score: 92, risk_factors: ['Renewal in 15 days', 'Onboarding incomplete', 'No champion identified'], recommended_actions: ['Urgent exec outreach', 'Complete onboarding', 'Discuss renewal terms'] },
      ]);
      setExpansions([
        { id: '1', account_name: 'Acme Corporation', opportunity_type: 'upsell', potential_arr: 36000, probability: 75, triggers: ['High feature usage', 'Approaching seat limit', 'Request for enterprise features'] },
        { id: '2', account_name: 'GlobalTech Ltd', opportunity_type: 'cross_sell', potential_arr: 24000, probability: 60, triggers: ['Interest in new module', 'Expanding to new region'] },
      ]);
      setMetrics({
        total_accounts: 156,
        total_arr: 2340000,
        healthy_accounts: 124,
        at_risk_accounts: 18,
        avg_health_score: 78,
        nps_score: 52,
        churn_rate: 3.2,
        expansion_revenue: 180000
      });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleRecalculateHealth = async (accountId: string) => {
    try {
      await customerSuccessAPI.recalculateHealth(accountId);
      toast.success('Health score recalculated');
      fetchData();
    } catch {
      toast.error('Failed to recalculate health score');
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const getHealthColor = (score: number) => {
    if (score >= 80) return 'text-green-600 dark:text-green-400';
    if (score >= 60) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  const getHealthBadge = (status: string) => {
    const styles: Record<string, string> = {
      healthy: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
      at_risk: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
      critical: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
    };
    return styles[status] || styles.at_risk;
  };

  const getTierBadge = (tier: string) => {
    const styles: Record<string, string> = {
      enterprise: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400',
      business: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
      professional: 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400',
      starter: 'bg-gray-100 text-gray-600 dark:bg-gray-900/30 dark:text-gray-500',
    };
    return styles[tier] || styles.professional;
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-6 space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h1 className="text-3xl font-bold gradient-text flex items-center gap-2">
                <Heart className="w-8 h-8" />
                Customer Success
              </h1>
              <p className="text-muted-foreground mt-1">
                Monitor health, prevent churn, and drive expansion
              </p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => fetchData()}>
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </Button>
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Add Account
              </Button>
            </div>
          </div>

          {/* Metrics Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card className="modern-card">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Total ARR
                </CardTitle>
                <DollarSign className="w-5 h-5 text-green-500" />
              </CardHeader>
              <CardContent>
                {loading ? (
                  <Skeleton className="h-8 w-28" />
                ) : (
                  <>
                    <div className="text-2xl font-bold">{formatCurrency(metrics?.total_arr || 0)}</div>
                    <p className="text-xs text-muted-foreground">{metrics?.total_accounts} accounts</p>
                  </>
                )}
              </CardContent>
            </Card>

            <Card className="modern-card">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Avg Health Score
                </CardTitle>
                <Activity className="w-5 h-5 text-blue-500" />
              </CardHeader>
              <CardContent>
                {loading ? (
                  <Skeleton className="h-8 w-20" />
                ) : (
                  <>
                    <div className={`text-2xl font-bold ${getHealthColor(metrics?.avg_health_score || 0)}`}>
                      {metrics?.avg_health_score}
                    </div>
                    <Progress value={metrics?.avg_health_score || 0} className="mt-2" />
                  </>
                )}
              </CardContent>
            </Card>

            <Card className="modern-card">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  At Risk Accounts
                </CardTitle>
                <AlertTriangle className="w-5 h-5 text-yellow-500" />
              </CardHeader>
              <CardContent>
                {loading ? (
                  <Skeleton className="h-8 w-20" />
                ) : (
                  <>
                    <div className="text-2xl font-bold text-yellow-600">{metrics?.at_risk_accounts}</div>
                    <p className="text-xs text-muted-foreground">
                      of {metrics?.total_accounts} total
                    </p>
                  </>
                )}
              </CardContent>
            </Card>

            <Card className="modern-card">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  NPS Score
                </CardTitle>
                <ThumbsUp className="w-5 h-5 text-purple-500" />
              </CardHeader>
              <CardContent>
                {loading ? (
                  <Skeleton className="h-8 w-20" />
                ) : (
                  <>
                    <div className="text-2xl font-bold">{metrics?.nps_score}</div>
                    <p className="text-xs text-muted-foreground">
                      {metrics?.churn_rate}% churn rate
                    </p>
                  </>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Main Content Tabs */}
          <Tabs defaultValue="accounts" className="space-y-4">
            <TabsList className="grid w-full grid-cols-4 lg:w-auto lg:inline-grid">
              <TabsTrigger value="accounts">Accounts</TabsTrigger>
              <TabsTrigger value="health">Health Scores</TabsTrigger>
              <TabsTrigger value="churn">Churn Risks</TabsTrigger>
              <TabsTrigger value="expansion">Expansion</TabsTrigger>
            </TabsList>

            {/* Accounts Tab */}
            <TabsContent value="accounts" className="space-y-4">
              <Card>
                <CardHeader>
                  <div className="flex flex-col sm:flex-row justify-between gap-4">
                    <div>
                      <CardTitle>Customer Accounts</CardTitle>
                      <CardDescription>Manage and monitor your customer portfolio</CardDescription>
                    </div>
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                      <Input
                        placeholder="Search accounts..."
                        className="pl-10 w-64"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                      />
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <div className="space-y-3">
                      {[1, 2, 3].map((i) => (
                        <Skeleton key={i} className="h-20 w-full" />
                      ))}
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {accounts.map((account) => (
                        <div
                          key={account.id}
                          className="flex items-center justify-between p-4 rounded-lg border hover:bg-accent/50 transition-colors"
                        >
                          <div className="flex-1">
                            <div className="flex items-center gap-3">
                              <h4 className="font-semibold">{account.name}</h4>
                              <Badge className={getTierBadge(account.tier)}>{account.tier}</Badge>
                              <Badge className={getHealthBadge(account.health_status)}>
                                {account.health_status.replace('_', ' ')}
                              </Badge>
                              {!account.onboarding_complete && (
                                <Badge variant="outline" className="text-orange-600">
                                  Onboarding
                                </Badge>
                              )}
                            </div>
                            <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                              <span>{formatCurrency(account.arr)} ARR</span>
                              <span>CSM: {account.csm_name}</span>
                              {account.days_until_renewal && (
                                <span className={account.days_until_renewal < 30 ? 'text-orange-600' : ''}>
                                  <Calendar className="w-3 h-3 inline mr-1" />
                                  {account.days_until_renewal} days to renewal
                                </span>
                              )}
                            </div>
                          </div>
                          <div className="flex items-center gap-4">
                            <div className="text-right">
                              <div className={`text-2xl font-bold ${getHealthColor(account.health_score)}`}>
                                {account.health_score}
                              </div>
                              <div className="text-xs text-muted-foreground">Health Score</div>
                            </div>
                            <div className="flex gap-2">
                              <Button 
                                variant="outline" 
                                size="sm"
                                onClick={() => handleRecalculateHealth(account.id.toString())}
                              >
                                Recalculate
                              </Button>
                              <Button variant="outline" size="sm">View</Button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* Health Scores Tab */}
            <TabsContent value="health" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="w-5 h-5" />
                    Health Score Breakdown
                  </CardTitle>
                  <CardDescription>Detailed health metrics for each account</CardDescription>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <div className="space-y-4">
                      {[1, 2, 3].map((i) => (
                        <Skeleton key={i} className="h-32 w-full" />
                      ))}
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {healthScores.map((health) => (
                        <div key={health.id} className="p-4 rounded-lg border">
                          <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-3">
                              <h4 className="font-semibold">{health.account_name}</h4>
                              <Badge className={getHealthBadge(health.status)}>
                                {health.status.replace('_', ' ')}
                              </Badge>
                              {health.trend === 'up' && (
                                <TrendingUp className="w-4 h-4 text-green-500" />
                              )}
                              {health.trend === 'down' && (
                                <TrendingDown className="w-4 h-4 text-red-500" />
                              )}
                            </div>
                            <div className={`text-3xl font-bold ${getHealthColor(health.score)}`}>
                              {health.score}
                            </div>
                          </div>
                          <div className="grid grid-cols-4 gap-4">
                            <div>
                              <div className="flex justify-between text-sm mb-1">
                                <span className="text-muted-foreground">Usage</span>
                                <span>{health.usage_score}</span>
                              </div>
                              <Progress value={health.usage_score} className="h-2" />
                            </div>
                            <div>
                              <div className="flex justify-between text-sm mb-1">
                                <span className="text-muted-foreground">Engagement</span>
                                <span>{health.engagement_score}</span>
                              </div>
                              <Progress value={health.engagement_score} className="h-2" />
                            </div>
                            <div>
                              <div className="flex justify-between text-sm mb-1">
                                <span className="text-muted-foreground">Support</span>
                                <span>{health.support_score}</span>
                              </div>
                              <Progress value={health.support_score} className="h-2" />
                            </div>
                            <div>
                              <div className="flex justify-between text-sm mb-1">
                                <span className="text-muted-foreground">Payment</span>
                                <span>{health.payment_score}</span>
                              </div>
                              <Progress value={health.payment_score} className="h-2" />
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* Churn Risks Tab */}
            <TabsContent value="churn" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-yellow-500" />
                    Churn Risk Alerts
                  </CardTitle>
                  <CardDescription>Accounts requiring immediate attention</CardDescription>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <div className="space-y-4">
                      {[1, 2].map((i) => (
                        <Skeleton key={i} className="h-40 w-full" />
                      ))}
                    </div>
                  ) : churnRisks.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      <CheckCircle2 className="w-12 h-12 mx-auto mb-4 text-green-500" />
                      <p>No high-risk accounts at the moment!</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {churnRisks.map((risk) => (
                        <div
                          key={risk.id}
                          className={`p-4 rounded-lg border ${
                            risk.risk_level === 'critical'
                              ? 'border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950/30'
                              : 'border-yellow-200 bg-yellow-50 dark:border-yellow-900 dark:bg-yellow-950/30'
                          }`}
                        >
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex items-center gap-3">
                              <AlertTriangle
                                className={`w-5 h-5 ${
                                  risk.risk_level === 'critical' ? 'text-red-500' : 'text-yellow-500'
                                }`}
                              />
                              <h4 className="font-semibold">{risk.account_name}</h4>
                              <Badge
                                className={
                                  risk.risk_level === 'critical'
                                    ? 'bg-red-100 text-red-800 dark:bg-red-900/50'
                                    : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/50'
                                }
                              >
                                {risk.risk_level} risk
                              </Badge>
                            </div>
                            <div className="text-2xl font-bold text-red-600">{risk.risk_score}%</div>
                          </div>
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <h5 className="text-sm font-semibold mb-2">Risk Factors:</h5>
                              <ul className="space-y-1">
                                {risk.risk_factors.map((factor, i) => (
                                  <li key={i} className="flex items-center gap-2 text-sm">
                                    <XCircle className="w-3 h-3 text-red-500" />
                                    {factor}
                                  </li>
                                ))}
                              </ul>
                            </div>
                            <div>
                              <h5 className="text-sm font-semibold mb-2">Recommended Actions:</h5>
                              <ul className="space-y-1">
                                {risk.recommended_actions.map((action, i) => (
                                  <li key={i} className="flex items-center gap-2 text-sm">
                                    <Zap className="w-3 h-3 text-blue-500" />
                                    {action}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          </div>
                          <div className="flex gap-2 mt-4">
                            <Button size="sm">
                              <MessageSquare className="w-4 h-4 mr-2" />
                              Contact Customer
                            </Button>
                            <Button size="sm" variant="outline">
                              View Account
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* Expansion Tab */}
            <TabsContent value="expansion" className="space-y-4">
              <Card>
                <CardHeader>
                  <div className="flex justify-between items-center">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-green-500" />
                        Expansion Opportunities
                      </CardTitle>
                      <CardDescription>Identified upsell and cross-sell opportunities</CardDescription>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-green-600">
                        {formatCurrency(metrics?.expansion_revenue || 0)}
                      </div>
                      <div className="text-xs text-muted-foreground">Pipeline Value</div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <div className="space-y-4">
                      {[1, 2].map((i) => (
                        <Skeleton key={i} className="h-32 w-full" />
                      ))}
                    </div>
                  ) : expansions.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      <Target className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p>No expansion opportunities identified yet.</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {expansions.map((expansion) => (
                        <div
                          key={expansion.id}
                          className="p-4 rounded-lg border border-green-200 bg-green-50 dark:border-green-900 dark:bg-green-950/30"
                        >
                          <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center gap-3">
                              <h4 className="font-semibold">{expansion.account_name}</h4>
                              <Badge className="bg-green-100 text-green-800 dark:bg-green-900/50">
                                {expansion.opportunity_type}
                              </Badge>
                            </div>
                            <div className="text-right">
                              <div className="text-xl font-bold text-green-600">
                                {formatCurrency(expansion.potential_arr)}
                              </div>
                              <div className="text-xs text-muted-foreground">
                                {expansion.probability}% probability
                              </div>
                            </div>
                          </div>
                          <div>
                            <h5 className="text-sm font-semibold mb-2">Expansion Triggers:</h5>
                            <div className="flex flex-wrap gap-2">
                              {expansion.triggers.map((trigger, i) => (
                                <Badge key={i} variant="secondary" className="text-xs">
                                  <Sparkles className="w-3 h-3 mr-1" />
                                  {trigger}
                                </Badge>
                              ))}
                            </div>
                          </div>
                          <div className="flex gap-2 mt-4">
                            <Button size="sm">
                              <ArrowUpRight className="w-4 h-4 mr-2" />
                              Create Opportunity
                            </Button>
                            <Button size="sm" variant="outline">
                              View Details
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
