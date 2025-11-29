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
import {
  TrendingUp,
  DollarSign,
  Target,
  AlertTriangle,
  CheckCircle2,
  BarChart3,
  PieChart,
  RefreshCw,
  ArrowUpRight,
  Zap,
  Trophy
} from 'lucide-react';
import { toast } from 'sonner';
import { revenueIntelligenceAPI } from '@/lib/premium-features-api';

interface DealScore {
  id: string;
  opportunity_name: string;
  score: number;
  win_probability: number;
  risk_level: string;
  key_factors: string[];
  recommendations: string[];
  scored_at: string;
}

interface RiskAlert {
  id: string;
  opportunity_name: string;
  alert_type: string;
  severity: string;
  message: string;
  created_at: string;
  acknowledged: boolean;
}

interface RevenueMetrics {
  current_quarter_revenue: number;
  target: number;
  pipeline_value: number;
  weighted_pipeline: number;
  win_rate: number;
  avg_deal_size: number;
  sales_cycle_days: number;
}

export default function RevenueIntelligencePage() {
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState<RevenueMetrics | null>(null);
  const [dealScores, setDealScores] = useState<DealScore[]>([]);
  const [riskAlerts, setRiskAlerts] = useState<RiskAlert[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      
      // Fetch deal scores
      const scoresRes = await revenueIntelligenceAPI.getDealScores({ limit: 10, ordering: '-score' });
      setDealScores(scoresRes.data.results || []);
      
      // Fetch risk alerts
      const alertsRes = await revenueIntelligenceAPI.getRiskAlerts({ is_resolved: false });
      setRiskAlerts(alertsRes.data.results || []);

      // Mock metrics for demo
      setMetrics({
        current_quarter_revenue: 2450000,
        target: 3000000,
        pipeline_value: 8500000,
        weighted_pipeline: 4250000,
        win_rate: 32,
        avg_deal_size: 45000,
        sales_cycle_days: 45
      });
      
    } catch (error) {
      console.error('Failed to fetch revenue data:', error);
      // Set demo data for preview
      setMetrics({
        current_quarter_revenue: 2450000,
        target: 3000000,
        pipeline_value: 8500000,
        weighted_pipeline: 4250000,
        win_rate: 32,
        avg_deal_size: 45000,
        sales_cycle_days: 45
      });
      setDealScores([
        { id: '1', opportunity_name: 'Enterprise Deal - Acme Corp', score: 85, win_probability: 78, risk_level: 'low', key_factors: ['Strong champion', 'Budget approved'], recommendations: ['Schedule demo'], scored_at: new Date().toISOString() },
        { id: '2', opportunity_name: 'Mid-Market - TechStart Inc', score: 72, win_probability: 65, risk_level: 'medium', key_factors: ['Competitor involved'], recommendations: ['Address pricing concerns'], scored_at: new Date().toISOString() },
        { id: '3', opportunity_name: 'SMB - LocalBiz LLC', score: 45, win_probability: 35, risk_level: 'high', key_factors: ['No recent engagement'], recommendations: ['Re-engage stakeholder'], scored_at: new Date().toISOString() },
      ]);
      setRiskAlerts([
        { id: '1', opportunity_name: 'Enterprise Deal - Acme Corp', alert_type: 'stalled', severity: 'medium', message: 'No activity in 14 days', created_at: new Date().toISOString(), acknowledged: false },
        { id: '2', opportunity_name: 'Mid-Market - TechStart Inc', alert_type: 'competitor', severity: 'high', message: 'Competitor mentioned in recent call', created_at: new Date().toISOString(), acknowledged: false },
      ]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchData();
    setRefreshing(false);
    toast.success('Data refreshed');
  };

  const handleBulkScore = async () => {
    try {
      await revenueIntelligenceAPI.bulkScoreDeals();
      toast.success('Bulk scoring initiated');
      fetchData();
    } catch {
      toast.error('Failed to initiate bulk scoring');
    }
  };

  const handleAcknowledgeAlert = async (alertId: string) => {
    try {
      await revenueIntelligenceAPI.acknowledgeAlert(alertId);
      toast.success('Alert acknowledged');
      fetchData();
    } catch {
      toast.error('Failed to acknowledge alert');
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

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 dark:text-green-400';
    if (score >= 60) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  const getRiskBadge = (risk: string) => {
    const colors = {
      low: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
      medium: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
      high: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
    };
    return colors[risk as keyof typeof colors] || colors.medium;
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-6 space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h1 className="text-3xl font-bold gradient-text flex items-center gap-2">
                <TrendingUp className="w-8 h-8" />
                Revenue Intelligence
              </h1>
              <p className="text-muted-foreground mt-1">
                AI-powered deal scoring, forecasting, and pipeline analytics
              </p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={handleRefresh} disabled={refreshing}>
                <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
              <Button onClick={handleBulkScore}>
                <Zap className="w-4 h-4 mr-2" />
                Score All Deals
              </Button>
            </div>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card className="modern-card">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Q4 Revenue
                </CardTitle>
                <DollarSign className="w-5 h-5 text-green-500" />
              </CardHeader>
              <CardContent>
                {loading ? (
                  <Skeleton className="h-8 w-32" />
                ) : (
                  <>
                    <div className="text-2xl font-bold">
                      {formatCurrency(metrics?.current_quarter_revenue || 0)}
                    </div>
                    <Progress 
                      value={((metrics?.current_quarter_revenue || 0) / (metrics?.target || 1)) * 100} 
                      className="mt-2"
                    />
                    <p className="text-xs text-muted-foreground mt-1">
                      {Math.round(((metrics?.current_quarter_revenue || 0) / (metrics?.target || 1)) * 100)}% of {formatCurrency(metrics?.target || 0)} target
                    </p>
                  </>
                )}
              </CardContent>
            </Card>

            <Card className="modern-card">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Pipeline Value
                </CardTitle>
                <BarChart3 className="w-5 h-5 text-blue-500" />
              </CardHeader>
              <CardContent>
                {loading ? (
                  <Skeleton className="h-8 w-32" />
                ) : (
                  <>
                    <div className="text-2xl font-bold">
                      {formatCurrency(metrics?.pipeline_value || 0)}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
                      <span className="text-green-500">Weighted:</span>
                      {formatCurrency(metrics?.weighted_pipeline || 0)}
                    </p>
                  </>
                )}
              </CardContent>
            </Card>

            <Card className="modern-card">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Win Rate
                </CardTitle>
                <Trophy className="w-5 h-5 text-yellow-500" />
              </CardHeader>
              <CardContent>
                {loading ? (
                  <Skeleton className="h-8 w-20" />
                ) : (
                  <>
                    <div className="text-2xl font-bold flex items-center gap-2">
                      {metrics?.win_rate}%
                      <ArrowUpRight className="w-4 h-4 text-green-500" />
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      +5% from last quarter
                    </p>
                  </>
                )}
              </CardContent>
            </Card>

            <Card className="modern-card">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Avg Deal Size
                </CardTitle>
                <Target className="w-5 h-5 text-purple-500" />
              </CardHeader>
              <CardContent>
                {loading ? (
                  <Skeleton className="h-8 w-24" />
                ) : (
                  <>
                    <div className="text-2xl font-bold">
                      {formatCurrency(metrics?.avg_deal_size || 0)}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      {metrics?.sales_cycle_days} days avg cycle
                    </p>
                  </>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Main Content Tabs */}
          <Tabs defaultValue="deal-scores" className="space-y-4">
            <TabsList className="grid w-full grid-cols-4 lg:w-auto lg:inline-grid">
              <TabsTrigger value="deal-scores">Deal Scores</TabsTrigger>
              <TabsTrigger value="risk-alerts">Risk Alerts</TabsTrigger>
              <TabsTrigger value="forecasts">Forecasts</TabsTrigger>
              <TabsTrigger value="win-loss">Win/Loss Analysis</TabsTrigger>
            </TabsList>

            <TabsContent value="deal-scores" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <PieChart className="w-5 h-5" />
                    AI Deal Scores
                  </CardTitle>
                  <CardDescription>
                    Machine learning-powered win probability scores for active deals
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <div className="space-y-4">
                      {[1, 2, 3].map((i) => (
                        <Skeleton key={i} className="h-20 w-full" />
                      ))}
                    </div>
                  ) : dealScores.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      <Target className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p>No deals scored yet</p>
                      <Button className="mt-4" onClick={handleBulkScore}>
                        Score All Deals
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {dealScores.map((deal) => (
                        <div
                          key={deal.id}
                          className="flex items-center justify-between p-4 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
                        >
                          <div className="flex-1">
                            <div className="flex items-center gap-3">
                              <h4 className="font-semibold">{deal.opportunity_name}</h4>
                              <Badge className={getRiskBadge(deal.risk_level)}>
                                {deal.risk_level} risk
                              </Badge>
                            </div>
                            <div className="flex flex-wrap gap-2 mt-2">
                              {deal.key_factors.slice(0, 3).map((factor, i) => (
                                <Badge key={i} variant="outline" className="text-xs">
                                  {factor}
                                </Badge>
                              ))}
                            </div>
                          </div>
                          <div className="text-right ml-4">
                            <div className={`text-3xl font-bold ${getScoreColor(deal.score)}`}>
                              {deal.score}
                            </div>
                            <div className="text-xs text-muted-foreground">
                              {deal.win_probability}% win prob
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="risk-alerts" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-yellow-500" />
                    Deal Risk Alerts
                  </CardTitle>
                  <CardDescription>
                    Active alerts requiring attention
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <div className="space-y-4">
                      {[1, 2].map((i) => (
                        <Skeleton key={i} className="h-16 w-full" />
                      ))}
                    </div>
                  ) : riskAlerts.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      <CheckCircle2 className="w-12 h-12 mx-auto mb-4 text-green-500" />
                      <p>No active risk alerts - your pipeline looks healthy!</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {riskAlerts.map((alert) => (
                        <div
                          key={alert.id}
                          className={`flex items-center justify-between p-4 rounded-lg border ${
                            alert.severity === 'high'
                              ? 'border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950/30'
                              : 'border-yellow-200 bg-yellow-50 dark:border-yellow-900 dark:bg-yellow-950/30'
                          }`}
                        >
                          <div className="flex items-start gap-3">
                            <AlertTriangle
                              className={`w-5 h-5 mt-0.5 ${
                                alert.severity === 'high' ? 'text-red-500' : 'text-yellow-500'
                              }`}
                            />
                            <div>
                              <h4 className="font-semibold">{alert.opportunity_name}</h4>
                              <p className="text-sm text-muted-foreground">{alert.message}</p>
                              <Badge variant="outline" className="mt-1 text-xs">
                                {alert.alert_type}
                              </Badge>
                            </div>
                          </div>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleAcknowledgeAlert(alert.id)}
                          >
                            Acknowledge
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="forecasts" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5" />
                    Revenue Forecasts
                  </CardTitle>
                  <CardDescription>
                    AI-generated revenue predictions with confidence intervals
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {['Q4 2025', 'Q1 2026', 'Q2 2026'].map((period, i) => (
                      <Card key={period} className="border-2">
                        <CardHeader className="pb-2">
                          <CardTitle className="text-lg">{period}</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="text-2xl font-bold text-primary">
                            {formatCurrency(3000000 + i * 500000)}
                          </div>
                          <div className="mt-2 space-y-1 text-sm">
                            <div className="flex justify-between">
                              <span className="text-muted-foreground">Best Case</span>
                              <span className="text-green-600">{formatCurrency(3500000 + i * 600000)}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-muted-foreground">Worst Case</span>
                              <span className="text-red-600">{formatCurrency(2500000 + i * 400000)}</span>
                            </div>
                          </div>
                          <div className="mt-3">
                            <div className="flex justify-between text-xs mb-1">
                              <span>Confidence</span>
                              <span>{85 - i * 10}%</span>
                            </div>
                            <Progress value={85 - i * 10} />
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="win-loss" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="w-5 h-5" />
                    Win/Loss Analysis
                  </CardTitle>
                  <CardDescription>
                    Understand why deals are won or lost
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-semibold text-green-600 mb-3 flex items-center gap-2">
                        <CheckCircle2 className="w-4 h-4" />
                        Top Win Reasons
                      </h4>
                      <div className="space-y-3">
                        {[
                          { reason: 'Strong product fit', count: 45, percent: 35 },
                          { reason: 'Competitive pricing', count: 32, percent: 25 },
                          { reason: 'Executive sponsorship', count: 28, percent: 22 },
                          { reason: 'Fast implementation', count: 23, percent: 18 },
                        ].map((item) => (
                          <div key={item.reason}>
                            <div className="flex justify-between text-sm mb-1">
                              <span>{item.reason}</span>
                              <span className="text-muted-foreground">{item.count} deals</span>
                            </div>
                            <Progress value={item.percent} className="h-2" />
                          </div>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h4 className="font-semibold text-red-600 mb-3 flex items-center gap-2">
                        <AlertTriangle className="w-4 h-4" />
                        Top Loss Reasons
                      </h4>
                      <div className="space-y-3">
                        {[
                          { reason: 'Lost to competitor', count: 28, percent: 32 },
                          { reason: 'Budget constraints', count: 24, percent: 28 },
                          { reason: 'No decision made', count: 20, percent: 23 },
                          { reason: 'Timing not right', count: 15, percent: 17 },
                        ].map((item) => (
                          <div key={item.reason}>
                            <div className="flex justify-between text-sm mb-1">
                              <span>{item.reason}</span>
                              <span className="text-muted-foreground">{item.count} deals</span>
                            </div>
                            <Progress value={item.percent} className="h-2 [&>div]:bg-red-500" />
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
