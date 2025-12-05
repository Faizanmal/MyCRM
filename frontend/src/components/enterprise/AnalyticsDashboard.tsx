/**
 * Analytics Dashboard Component
 * ===============================
 * 
 * Real-time analytics and sales intelligence dashboard
 */

'use client';

import React, { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  ArrowDown,
  ArrowRight,
  ArrowUp,
  BarChart3,
  Calendar,
  DollarSign,
  Download,
  Filter,
  Loader2,
  PieChart,
  RefreshCw,
  Target,
  TrendingDown,
  TrendingUp,
  Users,
  Zap,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// =============================================================================
// Types
// =============================================================================

interface SalesMetrics {
  revenue: {
    current: number;
    previous: number;
    target: number;
    trend: number;
  };
  deals: {
    won: number;
    lost: number;
    in_progress: number;
    avg_deal_size: number;
    win_rate: number;
  };
  pipeline: {
    value: number;
    weighted_value: number;
    stages: PipelineStage[];
  };
  activities: {
    calls: number;
    emails: number;
    meetings: number;
    tasks_completed: number;
  };
}

interface PipelineStage {
  name: string;
  value: number;
  count: number;
  conversion_rate: number;
}

interface SalesForecast {
  period: string;
  predicted: number;
  lower_bound: number;
  upper_bound: number;
  confidence: number;
}

interface TeamPerformance {
  user_id: string;
  name: string;
  avatar?: string;
  revenue: number;
  deals_won: number;
  deals_lost: number;
  win_rate: number;
  quota_attainment: number;
  activities: number;
  rank: number;
}

interface ConversionFunnel {
  stage: string;
  count: number;
  conversion_rate: number;
  avg_time_in_stage: number;
}

interface AIInsight {
  id: string;
  type: 'opportunity' | 'risk' | 'trend' | 'recommendation';
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  action?: string;
  related_entity?: {
    type: string;
    id: string;
    name: string;
  };
}

// =============================================================================
// API Hooks
// =============================================================================

function useSalesMetrics(period: string) {
  return useQuery<SalesMetrics>({
    queryKey: ['analytics', 'sales-metrics', period],
    queryFn: async () => {
      const res = await fetch(`/api/analytics/sales-metrics?period=${period}`);
      if (!res.ok) throw new Error('Failed to fetch sales metrics');
      return res.json();
    },
    refetchInterval: 30000,
  });
}

function useSalesForecast() {
  return useQuery<SalesForecast[]>({
    queryKey: ['analytics', 'forecast'],
    queryFn: async () => {
      const res = await fetch('/api/analytics/forecast');
      if (!res.ok) throw new Error('Failed to fetch forecast');
      return res.json();
    },
  });
}

function useTeamPerformance(period: string) {
  return useQuery<TeamPerformance[]>({
    queryKey: ['analytics', 'team-performance', period],
    queryFn: async () => {
      const res = await fetch(`/api/analytics/team-performance?period=${period}`);
      if (!res.ok) throw new Error('Failed to fetch team performance');
      return res.json();
    },
  });
}

function useConversionFunnel() {
  return useQuery<ConversionFunnel[]>({
    queryKey: ['analytics', 'conversion-funnel'],
    queryFn: async () => {
      const res = await fetch('/api/analytics/conversion-funnel');
      if (!res.ok) throw new Error('Failed to fetch conversion funnel');
      return res.json();
    },
  });
}

function useAIInsights() {
  return useQuery<AIInsight[]>({
    queryKey: ['analytics', 'ai-insights'],
    queryFn: async () => {
      const res = await fetch('/api/analytics/ai-insights');
      if (!res.ok) throw new Error('Failed to fetch AI insights');
      return res.json();
    },
    refetchInterval: 60000,
  });
}

// =============================================================================
// Main Component
// =============================================================================

export function AnalyticsDashboard({ className }: { className?: string }) {
  const [period, setPeriod] = useState('month');
  const { data: metrics, isLoading, refetch } = useSalesMetrics(period);

  if (isLoading || !metrics) {
    return (
      <div className={cn('space-y-6', className)}>
        <div className="animate-pulse space-y-4">
          <div className="h-10 w-48 bg-muted rounded" />
          <div className="grid grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-muted rounded-lg" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={cn('space-y-6', className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Analytics Dashboard</h2>
          <p className="text-muted-foreground">
            Real-time sales intelligence and performance metrics
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Select value={period} onValueChange={setPeriod}>
            <SelectTrigger className="w-[150px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="week">This Week</SelectItem>
              <SelectItem value="month">This Month</SelectItem>
              <SelectItem value="quarter">This Quarter</SelectItem>
              <SelectItem value="year">This Year</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" onClick={() => refetch()}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Revenue"
          value={formatCurrency(metrics.revenue.current)}
          previousValue={formatCurrency(metrics.revenue.previous)}
          trend={metrics.revenue.trend}
          target={metrics.revenue.target}
          icon={<DollarSign className="h-4 w-4" />}
        />
        <KPICard
          title="Deals Won"
          value={metrics.deals.won.toString()}
          subtext={`Win Rate: ${metrics.deals.win_rate.toFixed(1)}%`}
          trend={5}
          icon={<Target className="h-4 w-4" />}
        />
        <KPICard
          title="Pipeline Value"
          value={formatCurrency(metrics.pipeline.value)}
          subtext={`Weighted: ${formatCurrency(metrics.pipeline.weighted_value)}`}
          icon={<BarChart3 className="h-4 w-4" />}
        />
        <KPICard
          title="Avg Deal Size"
          value={formatCurrency(metrics.deals.avg_deal_size)}
          trend={8}
          icon={<TrendingUp className="h-4 w-4" />}
        />
      </div>

      {/* Tabs */}
      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="pipeline">Pipeline</TabsTrigger>
          <TabsTrigger value="team">Team Performance</TabsTrigger>
          <TabsTrigger value="forecast">Forecast</TabsTrigger>
          <TabsTrigger value="insights">AI Insights</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="mt-6">
          <OverviewTab metrics={metrics} />
        </TabsContent>

        <TabsContent value="pipeline" className="mt-6">
          <PipelineTab stages={metrics.pipeline.stages} />
        </TabsContent>

        <TabsContent value="team" className="mt-6">
          <TeamPerformanceTab period={period} />
        </TabsContent>

        <TabsContent value="forecast" className="mt-6">
          <ForecastTab />
        </TabsContent>

        <TabsContent value="insights" className="mt-6">
          <AIInsightsTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}

// =============================================================================
// KPI Card
// =============================================================================

function KPICard({
  title,
  value,
  previousValue,
  subtext,
  trend,
  target,
  icon,
}: {
  title: string;
  value: string;
  previousValue?: string;
  subtext?: string;
  trend?: number;
  target?: number;
  icon: React.ReactNode;
}) {
  const progress = target ? (parseFloat(value.replace(/[^0-9.]/g, '')) / target) * 100 : null;

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between mb-2">
          <div className="p-2 rounded-lg bg-primary/10">
            {icon}
          </div>
          {trend !== undefined && (
            <Badge
              variant={trend >= 0 ? 'default' : 'destructive'}
              className={cn(
                'text-xs',
                trend >= 0 ? 'bg-green-500' : 'bg-red-500'
              )}
            >
              {trend >= 0 ? <ArrowUp className="h-3 w-3 mr-1" /> : <ArrowDown className="h-3 w-3 mr-1" />}
              {Math.abs(trend)}%
            </Badge>
          )}
        </div>
        <p className="text-sm text-muted-foreground">{title}</p>
        <p className="text-2xl font-bold mt-1">{value}</p>
        {subtext && (
          <p className="text-xs text-muted-foreground mt-1">{subtext}</p>
        )}
        {previousValue && (
          <p className="text-xs text-muted-foreground mt-1">
            vs {previousValue} last period
          </p>
        )}
        {progress !== null && (
          <div className="mt-4">
            <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
              <span>Target</span>
              <span>{progress.toFixed(0)}%</span>
            </div>
            <Progress value={Math.min(progress, 100)} className="h-1.5" />
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// =============================================================================
// Overview Tab
// =============================================================================

function OverviewTab({ metrics }: { metrics: SalesMetrics }) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Activity Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Activity Summary</CardTitle>
          <CardDescription>Your team's activities this period</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <ActivityBar
              label="Calls"
              value={metrics.activities.calls}
              max={200}
              color="bg-blue-500"
            />
            <ActivityBar
              label="Emails"
              value={metrics.activities.emails}
              max={500}
              color="bg-green-500"
            />
            <ActivityBar
              label="Meetings"
              value={metrics.activities.meetings}
              max={100}
              color="bg-purple-500"
            />
            <ActivityBar
              label="Tasks Completed"
              value={metrics.activities.tasks_completed}
              max={300}
              color="bg-orange-500"
            />
          </div>
        </CardContent>
      </Card>

      {/* Deal Status */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Deal Status</CardTitle>
          <CardDescription>Win/Loss breakdown</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center gap-8">
            <div className="text-center">
              <div className="w-20 h-20 rounded-full bg-green-500/20 flex items-center justify-center mb-2">
                <span className="text-2xl font-bold text-green-500">
                  {metrics.deals.won}
                </span>
              </div>
              <p className="text-sm text-muted-foreground">Won</p>
            </div>
            <div className="text-center">
              <div className="w-20 h-20 rounded-full bg-blue-500/20 flex items-center justify-center mb-2">
                <span className="text-2xl font-bold text-blue-500">
                  {metrics.deals.in_progress}
                </span>
              </div>
              <p className="text-sm text-muted-foreground">In Progress</p>
            </div>
            <div className="text-center">
              <div className="w-20 h-20 rounded-full bg-red-500/20 flex items-center justify-center mb-2">
                <span className="text-2xl font-bold text-red-500">
                  {metrics.deals.lost}
                </span>
              </div>
              <p className="text-sm text-muted-foreground">Lost</p>
            </div>
          </div>
          <div className="mt-6 pt-4 border-t">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Win Rate</span>
              <span className="text-lg font-semibold">
                {metrics.deals.win_rate.toFixed(1)}%
              </span>
            </div>
            <Progress value={metrics.deals.win_rate} className="h-2 mt-2" />
          </div>
        </CardContent>
      </Card>

      {/* Conversion Funnel */}
      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle className="text-base">Sales Funnel</CardTitle>
          <CardDescription>Lead to customer conversion</CardDescription>
        </CardHeader>
        <CardContent>
          <ConversionFunnelChart />
        </CardContent>
      </Card>
    </div>
  );
}

// =============================================================================
// Pipeline Tab
// =============================================================================

function PipelineTab({ stages }: { stages: PipelineStage[] }) {
  const totalValue = useMemo(
    () => stages.reduce((acc, stage) => acc + stage.value, 0),
    [stages]
  );

  return (
    <div className="space-y-6">
      {/* Pipeline Stages */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stages.map((stage, index) => (
          <Card key={stage.name}>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between mb-4">
                <Badge variant="outline">{stage.name}</Badge>
                <span className="text-xs text-muted-foreground">
                  {stage.count} deals
                </span>
              </div>
              <p className="text-2xl font-bold">{formatCurrency(stage.value)}</p>
              <p className="text-xs text-muted-foreground mt-1">
                {((stage.value / totalValue) * 100).toFixed(1)}% of pipeline
              </p>
              <div className="mt-4">
                <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
                  <span>Conversion Rate</span>
                  <span>{stage.conversion_rate.toFixed(1)}%</span>
                </div>
                <Progress value={stage.conversion_rate} className="h-1.5" />
              </div>
              {index < stages.length - 1 && (
                <div className="absolute right-0 top-1/2 transform translate-x-1/2 -translate-y-1/2 hidden lg:block">
                  <ArrowRight className="h-4 w-4 text-muted-foreground" />
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Pipeline Details Table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Pipeline Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {stages.map((stage) => (
              <div key={stage.name} className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-medium">{stage.name}</span>
                  <div className="flex items-center gap-4">
                    <span className="text-sm text-muted-foreground">
                      {stage.count} deals
                    </span>
                    <span className="font-semibold">
                      {formatCurrency(stage.value)}
                    </span>
                  </div>
                </div>
                <div className="relative">
                  <Progress
                    value={(stage.value / totalValue) * 100}
                    className="h-3"
                  />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// =============================================================================
// Team Performance Tab
// =============================================================================

function TeamPerformanceTab({ period }: { period: string }) {
  const { data: team = [], isLoading } = useTeamPerformance(period);

  if (isLoading) {
    return <div className="animate-pulse h-64 bg-muted rounded-lg" />;
  }

  return (
    <div className="space-y-6">
      {/* Leaderboard */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Sales Leaderboard</CardTitle>
          <CardDescription>Top performers this period</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {team.slice(0, 10).map((member, index) => (
              <div
                key={member.user_id}
                className={cn(
                  'flex items-center gap-4 p-3 rounded-lg',
                  index < 3 && 'bg-muted'
                )}
              >
                <div
                  className={cn(
                    'w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm',
                    index === 0 && 'bg-yellow-500 text-white',
                    index === 1 && 'bg-gray-400 text-white',
                    index === 2 && 'bg-amber-600 text-white',
                    index > 2 && 'bg-muted-foreground/20'
                  )}
                >
                  {index + 1}
                </div>
                <div className="flex-1">
                  <p className="font-medium">{member.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {member.deals_won} deals · {member.win_rate.toFixed(0)}% win rate
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-bold">{formatCurrency(member.revenue)}</p>
                  <div className="flex items-center gap-1 text-sm">
                    <span className="text-muted-foreground">Quota:</span>
                    <Badge
                      variant={member.quota_attainment >= 100 ? 'default' : 'secondary'}
                      className={cn(
                        member.quota_attainment >= 100 && 'bg-green-500'
                      )}
                    >
                      {member.quota_attainment.toFixed(0)}%
                    </Badge>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// =============================================================================
// Forecast Tab
// =============================================================================

function ForecastTab() {
  const { data: forecast = [], isLoading } = useSalesForecast();

  if (isLoading) {
    return <div className="animate-pulse h-64 bg-muted rounded-lg" />;
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-base">Revenue Forecast</CardTitle>
              <CardDescription>AI-powered revenue predictions</CardDescription>
            </div>
            <Badge variant="outline" className="gap-1">
              <Zap className="h-3 w-3" />
              AI Powered
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {forecast.map((item) => (
              <div key={item.period} className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-medium">{item.period}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-lg font-bold">
                      {formatCurrency(item.predicted)}
                    </span>
                    <Badge variant="outline">
                      {item.confidence.toFixed(0)}% confidence
                    </Badge>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground">
                    {formatCurrency(item.lower_bound)}
                  </span>
                  <div className="flex-1 relative h-2">
                    <div className="absolute inset-0 bg-muted rounded-full" />
                    <div
                      className="absolute inset-y-0 bg-primary/30 rounded-full"
                      style={{
                        left: `${((item.lower_bound - item.lower_bound) / (item.upper_bound - item.lower_bound)) * 100}%`,
                        right: `${100 - ((item.upper_bound - item.lower_bound) / (item.upper_bound - item.lower_bound)) * 100}%`,
                      }}
                    />
                    <div
                      className="absolute top-1/2 w-3 h-3 bg-primary rounded-full -translate-y-1/2"
                      style={{
                        left: `${((item.predicted - item.lower_bound) / (item.upper_bound - item.lower_bound)) * 100}%`,
                      }}
                    />
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {formatCurrency(item.upper_bound)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// =============================================================================
// AI Insights Tab
// =============================================================================

function AIInsightsTab() {
  const { data: insights = [], isLoading } = useAIInsights();

  if (isLoading) {
    return <div className="animate-pulse h-64 bg-muted rounded-lg" />;
  }

  const insightIcons: Record<string, React.ReactNode> = {
    opportunity: <TrendingUp className="h-4 w-4 text-green-500" />,
    risk: <TrendingDown className="h-4 w-4 text-red-500" />,
    trend: <BarChart3 className="h-4 w-4 text-blue-500" />,
    recommendation: <Zap className="h-4 w-4 text-purple-500" />,
  };

  const impactColors: Record<string, string> = {
    high: 'bg-red-500',
    medium: 'bg-yellow-500',
    low: 'bg-blue-500',
  };

  return (
    <div className="space-y-4">
      {insights.map((insight) => (
        <Card key={insight.id}>
          <CardContent className="pt-6">
            <div className="flex items-start gap-4">
              <div className="p-2 rounded-lg bg-muted">
                {insightIcons[insight.type]}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h4 className="font-semibold">{insight.title}</h4>
                  <Badge className={cn('text-white', impactColors[insight.impact])}>
                    {insight.impact} impact
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground mb-3">
                  {insight.description}
                </p>
                {insight.action && (
                  <Button size="sm" variant="outline">
                    {insight.action}
                    <ArrowRight className="h-3 w-3 ml-2" />
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
      {insights.length === 0 && (
        <Card>
          <CardContent className="py-8 text-center">
            <Zap className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
            <p className="text-muted-foreground">No insights available yet</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

// =============================================================================
// Helper Components
// =============================================================================

function ActivityBar({
  label,
  value,
  max,
  color,
}: {
  label: string;
  value: number;
  max: number;
  color: string;
}) {
  const percentage = Math.min((value / max) * 100, 100);

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-sm">
        <span>{label}</span>
        <span className="font-medium">{value}</span>
      </div>
      <div className="h-2 bg-muted rounded-full overflow-hidden">
        <div
          className={cn('h-full rounded-full transition-all', color)}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

function ConversionFunnelChart() {
  const { data: funnel = [], isLoading } = useConversionFunnel();

  if (isLoading) {
    return <div className="animate-pulse h-32 bg-muted rounded-lg" />;
  }

  const maxCount = Math.max(...funnel.map((f) => f.count));

  return (
    <div className="space-y-4">
      {funnel.map((stage, index) => (
        <div key={stage.stage} className="flex items-center gap-4">
          <div className="w-24 text-sm font-medium">{stage.stage}</div>
          <div className="flex-1 relative">
            <div
              className="h-8 rounded bg-primary/20 flex items-center justify-end pr-3"
              style={{ width: `${(stage.count / maxCount) * 100}%` }}
            >
              <span className="text-sm font-medium">{stage.count}</span>
            </div>
          </div>
          <div className="w-24 text-right">
            {index > 0 && (
              <span className="text-sm text-muted-foreground">
                {stage.conversion_rate.toFixed(1)}%
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

// =============================================================================
// Utilities
// =============================================================================

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    notation: value >= 1000000 ? 'compact' : 'standard',
    maximumFractionDigits: value >= 1000000 ? 1 : 0,
  }).format(value);
}

export default AnalyticsDashboard;
