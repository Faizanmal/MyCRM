'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Target,
  TrendingUp,
  TrendingDown,
  Users,
  Award,
  AlertTriangle,
  CheckCircle,
  Clock,
  DollarSign,
  Calendar,
  Sparkles,
  ArrowUp,
  ArrowDown,
  Edit,
  History,
  BarChart3,
  Calculator,
} from 'lucide-react';

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
// import { Textarea } from '@/components/ui/textarea';

// Types
interface QuotaSummary {
  period: {
    id: string;
    name: string;
    start_date: string;
    end_date: string;
  };
  summary: {
    total_target: number;
    total_achieved: number;
    total_forecast: number;
    attainment: number;
    forecast_attainment: number;
    quota_count: number;
  };
  by_user: UserQuota[];
  by_territory: TerritoryQuota[];
}

interface UserQuota {
  user_id: string;
  username: string;
  target: number;
  achieved: number;
  attainment: number;
  forecast: number;
}

interface TerritoryQuota {
  territory_id: string;
  territory_name: string;
  target: number;
  achieved: number;
  attainment: number;
  forecast: number;
}

interface QuotaForecast {
  quota_id: string;
  target: number;
  achieved: number;
  attainment: number;
  forecast: {
    projected_total: number;
    projected_attainment: number;
    days_remaining: number;
    daily_run_rate: number;
    required_daily_rate: number;
  };
  gap_analysis: {
    remaining_target: number;
    on_track: boolean;
    variance: number;
  };
}

interface AIRecommendation {
  recommended_target: number;
  confidence: number;
  factors: { factor: string; weight: number }[];
  comparison_to_set: {
    difference: number;
    percentage: number;
  };
}

// Mock API functions
const fetchQuotaSummary = async (): Promise<QuotaSummary> => {
  return {
    period: {
      id: 'q1-2024',
      name: 'Q1 2024',
      start_date: '2024-01-01',
      end_date: '2024-03-31',
    },
    summary: {
      total_target: 5000000,
      total_achieved: 3250000,
      total_forecast: 4800000,
      attainment: 65,
      forecast_attainment: 96,
      quota_count: 15,
    },
    by_user: [
      { user_id: '1', username: 'Sarah Johnson', target: 500000, achieved: 420000, attainment: 84, forecast: 550000 },
      { user_id: '2', username: 'Mike Chen', target: 450000, achieved: 360000, attainment: 80, forecast: 480000 },
      { user_id: '3', username: 'Emily Davis', target: 475000, achieved: 310000, attainment: 65, forecast: 450000 },
      { user_id: '4', username: 'David Wilson', target: 400000, achieved: 240000, attainment: 60, forecast: 380000 },
      { user_id: '5', username: 'Lisa Brown', target: 425000, achieved: 200000, attainment: 47, forecast: 350000 },
    ],
    by_territory: [
      { territory_id: '1', territory_name: 'West Coast', target: 1200000, achieved: 950000, attainment: 79, forecast: 1250000 },
      { territory_id: '2', territory_name: 'East Coast', target: 1100000, achieved: 780000, attainment: 71, forecast: 1050000 },
      { territory_id: '3', territory_name: 'Canada', target: 600000, achieved: 420000, attainment: 70, forecast: 580000 },
      { territory_id: '4', territory_name: 'EMEA', target: 1000000, achieved: 650000, attainment: 65, forecast: 920000 },
    ],
  };
};

const fetchQuotaForecast = async (quotaId: string): Promise<QuotaForecast> => {
  return {
    quota_id: quotaId,
    target: 500000,
    achieved: 420000,
    attainment: 84,
    forecast: {
      projected_total: 550000,
      projected_attainment: 110,
      days_remaining: 25,
      daily_run_rate: 6800,
      required_daily_rate: 3200,
    },
    gap_analysis: {
      remaining_target: 80000,
      on_track: true,
      variance: 50000,
    },
  };
};

const fetchAIRecommendation = async (_quotaId: string): Promise<AIRecommendation> => {
  void _quotaId;
  return {
    recommended_target: 480000,
    confidence: 0.82,
    factors: [
      { factor: 'Historical Performance', weight: 0.4 },
      { factor: 'Market Growth', weight: 0.3 },
      { factor: 'Pipeline Quality', weight: 0.3 },
    ],
    comparison_to_set: {
      difference: 20000,
      percentage: 4.17,
    },
  };
};

// Components
const AttainmentBadge: React.FC<{ attainment: number }> = ({ attainment }) => {
  if (attainment >= 100) {
    return <Badge className="bg-green-500">Achieved</Badge>;
  } else if (attainment >= 80) {
    return <Badge className="bg-blue-500">On Track</Badge>;
  } else if (attainment >= 60) {
    return <Badge className="bg-yellow-500">At Risk</Badge>;
  }
  return <Badge variant="destructive">Behind</Badge>;
};

const AttainmentProgress: React.FC<{
  achieved: number;
  target: number;
  forecast?: number;
}> = ({ achieved, target, forecast }) => {
  const attainment = target > 0 ? (achieved / target) * 100 : 0;
  const forecastPct = forecast && target > 0 ? (forecast / target) * 100 : 0;

  return (
    <div className="space-y-2">
      <div className="relative h-3 w-full bg-muted rounded-full overflow-hidden">
        {/* Forecast bar (lighter) */}
        {forecast && forecastPct > attainment && (
          <div
            className="absolute inset-y-0 left-0 bg-blue-200"
            style={{ width: `${Math.min(forecastPct, 100)}%` }}
          />
        )}
        {/* Achieved bar */}
        <div
          className={`absolute inset-y-0 left-0 ${
            attainment >= 100 ? 'bg-green-500' : attainment >= 80 ? 'bg-blue-500' : 'bg-yellow-500'
          }`}
          style={{ width: `${Math.min(attainment, 100)}%` }}
        />
        {/* 100% marker */}
        <div
          className="absolute inset-y-0 w-0.5 bg-gray-400"
          style={{ left: '100%' }}
        />
      </div>
      <div className="flex justify-between text-xs text-muted-foreground">
        <span>${(achieved / 1000).toFixed(0)}K achieved</span>
        <span>${(target / 1000).toFixed(0)}K target</span>
      </div>
    </div>
  );
};

const QuotaOverviewTab: React.FC<{ summary: QuotaSummary | undefined }> = ({
  summary,
}) => {
  if (!summary) return null;

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-5 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-blue-100 flex items-center justify-center">
                <Target className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Target</p>
                <p className="text-xl font-bold">
                  ${(summary.summary.total_target / 1000000).toFixed(1)}M
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-green-100 flex items-center justify-center">
                <DollarSign className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Achieved</p>
                <p className="text-xl font-bold">
                  ${(summary.summary.total_achieved / 1000000).toFixed(2)}M
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-purple-100 flex items-center justify-center">
                <TrendingUp className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Attainment</p>
                <p className="text-xl font-bold">{summary.summary.attainment}%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-yellow-100 flex items-center justify-center">
                <BarChart3 className="h-5 w-5 text-yellow-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Forecast</p>
                <p className="text-xl font-bold">
                  ${(summary.summary.total_forecast / 1000000).toFixed(2)}M
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-gray-100 flex items-center justify-center">
                <Users className="h-5 w-5 text-gray-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Quotas</p>
                <p className="text-xl font-bold">{summary.summary.quota_count}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Overall Progress */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Period Progress</CardTitle>
              <CardDescription>
                {summary.period.name}: {summary.period.start_date} to{' '}
                {summary.period.end_date}
              </CardDescription>
            </div>
            <Badge className="bg-blue-500">
              Forecast: {summary.summary.forecast_attainment}% attainment
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <AttainmentProgress
            achieved={summary.summary.total_achieved}
            target={summary.summary.total_target}
            forecast={summary.summary.total_forecast}
          />
        </CardContent>
      </Card>

      {/* Top Performers */}
      <div className="grid grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Award className="h-5 w-5 text-yellow-500" />
              Top Performers
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {summary.by_user.slice(0, 3).map((user, index) => (
                <div key={user.user_id} className="flex items-center gap-4">
                  <div
                    className={`h-8 w-8 rounded-full flex items-center justify-center font-bold text-white ${
                      index === 0
                        ? 'bg-yellow-500'
                        : index === 1
                        ? 'bg-gray-400'
                        : 'bg-amber-700'
                    }`}
                  >
                    {index + 1}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{user.username}</span>
                      <span className="font-bold">{user.attainment}%</span>
                    </div>
                    <Progress value={user.attainment} className="h-2 mt-1" />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Needs Attention
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {summary.by_user
                .filter((u) => u.attainment < 60)
                .map((user) => (
                  <div key={user.user_id} className="flex items-center gap-4">
                    <div className="h-8 w-8 rounded-full bg-red-100 flex items-center justify-center">
                      <TrendingDown className="h-4 w-4 text-red-600" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <span className="font-medium">{user.username}</span>
                        <span className="font-bold text-red-600">
                          {user.attainment}%
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        Gap: ${((user.target - user.achieved) / 1000).toFixed(0)}K
                      </p>
                    </div>
                  </div>
                ))}
              {summary.by_user.filter((u) => u.attainment < 60).length === 0 && (
                <div className="text-center py-4 text-muted-foreground">
                  <CheckCircle className="h-8 w-8 mx-auto mb-2 text-green-500" />
                  <p>All reps on track!</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

const QuotasByUserTab: React.FC<{ users: UserQuota[] | undefined }> = ({
  users,
}) => {
  const [selectedUser, setSelectedUser] = useState<string | null>(null);

  if (!users) return null;

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <Input placeholder="Search users..." className="max-w-sm" />
        <Button>
          <Edit className="h-4 w-4 mr-2" />
          Bulk Edit Quotas
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          <table className="w-full">
            <thead className="bg-muted/50">
              <tr>
                <th className="text-left p-4 font-medium">User</th>
                <th className="text-right p-4 font-medium">Target</th>
                <th className="text-right p-4 font-medium">Achieved</th>
                <th className="text-right p-4 font-medium">Attainment</th>
                <th className="text-right p-4 font-medium">Forecast</th>
                <th className="text-center p-4 font-medium">Status</th>
                <th className="text-right p-4 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {users.map((user) => (
                <tr key={user.user_id} className="hover:bg-muted/30">
                  <td className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                        {user.username.charAt(0)}
                      </div>
                      <span className="font-medium">{user.username}</span>
                    </div>
                  </td>
                  <td className="p-4 text-right font-medium">
                    ${(user.target / 1000).toFixed(0)}K
                  </td>
                  <td className="p-4 text-right">
                    ${(user.achieved / 1000).toFixed(0)}K
                  </td>
                  <td className="p-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      {user.attainment > 75 ? (
                        <ArrowUp className="h-4 w-4 text-green-500" />
                      ) : (
                        <ArrowDown className="h-4 w-4 text-red-500" />
                      )}
                      {user.attainment}%
                    </div>
                  </td>
                  <td className="p-4 text-right">
                    ${(user.forecast / 1000).toFixed(0)}K
                  </td>
                  <td className="p-4 text-center">
                    <AttainmentBadge attainment={user.attainment} />
                  </td>
                  <td className="p-4 text-right">
                    <div className="flex justify-end gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setSelectedUser(user.user_id)}
                      >
                        <Calculator className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm">
                        <History className="h-4 w-4" />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>

      {selectedUser && (
        <QuotaForecastDialog
          quotaId={selectedUser}
          onClose={() => setSelectedUser(null)}
        />
      )}
    </div>
  );
};

const QuotasByTerritoryTab: React.FC<{
  territories: TerritoryQuota[] | undefined;
}> = ({ territories }) => {
  if (!territories) return null;

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Territory Quota Performance</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {territories.map((territory) => (
              <div key={territory.territory_id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h4 className="font-medium">{territory.territory_name}</h4>
                    <p className="text-sm text-muted-foreground">
                      Target: ${(territory.target / 1000000).toFixed(2)}M
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold">{territory.attainment}%</p>
                    <AttainmentBadge attainment={territory.attainment} />
                  </div>
                </div>
                <AttainmentProgress
                  achieved={territory.achieved}
                  target={territory.target}
                  forecast={territory.forecast}
                />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

const AIQuotaPlannerTab: React.FC = () => {
  const [planning, setPlanning] = useState({
    growthTarget: 15,
    adjustForMarket: true,
    useHistorical: true,
  });

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-yellow-500" />
            AI Quota Planning Assistant
          </CardTitle>
          <CardDescription>
            Let AI help you set optimal quotas based on historical data and
            market conditions
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium">Growth Target (%)</label>
                <Input
                  type="number"
                  value={planning.growthTarget}
                  onChange={(e) =>
                    setPlanning({ ...planning, growthTarget: +e.target.value })
                  }
                  className="mt-1"
                />
              </div>

              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={planning.adjustForMarket}
                  onChange={(e) =>
                    setPlanning({
                      ...planning,
                      adjustForMarket: e.target.checked,
                    })
                  }
                  className="h-4 w-4"
                />
                <label className="text-sm">Adjust for market conditions</label>
              </div>

              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={planning.useHistorical}
                  onChange={(e) =>
                    setPlanning({ ...planning, useHistorical: e.target.checked })
                  }
                  className="h-4 w-4"
                />
                <label className="text-sm">Use historical performance</label>
              </div>

              <Button className="w-full">
                <Sparkles className="h-4 w-4 mr-2" />
                Generate AI Recommendations
              </Button>
            </div>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">AI Factors Considered</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {[
                    { name: 'Historical Performance', weight: 40 },
                    { name: 'Market Growth Rate', weight: 25 },
                    { name: 'Pipeline Quality', weight: 20 },
                    { name: 'Seasonal Patterns', weight: 15 },
                  ].map((factor) => (
                    <div key={factor.name}>
                      <div className="flex justify-between text-sm mb-1">
                        <span>{factor.name}</span>
                        <span className="font-medium">{factor.weight}%</span>
                      </div>
                      <Progress value={factor.weight} className="h-2" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Recommended Quotas</CardTitle>
          <CardDescription>
            AI-generated quota recommendations for next period
          </CardDescription>
        </CardHeader>
        <CardContent>
          <table className="w-full">
            <thead className="bg-muted/50">
              <tr>
                <th className="text-left p-3">User</th>
                <th className="text-right p-3">Current</th>
                <th className="text-right p-3">Recommended</th>
                <th className="text-right p-3">Change</th>
                <th className="text-center p-3">Confidence</th>
                <th className="text-right p-3">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {[
                { name: 'Sarah Johnson', current: 500000, recommended: 550000, confidence: 85 },
                { name: 'Mike Chen', current: 450000, recommended: 480000, confidence: 78 },
                { name: 'Emily Davis', current: 475000, recommended: 460000, confidence: 72 },
              ].map((rec) => (
                <tr key={rec.name}>
                  <td className="p-3 font-medium">{rec.name}</td>
                  <td className="p-3 text-right">${(rec.current / 1000).toFixed(0)}K</td>
                  <td className="p-3 text-right font-medium">
                    ${(rec.recommended / 1000).toFixed(0)}K
                  </td>
                  <td className="p-3 text-right">
                    <span
                      className={
                        rec.recommended > rec.current
                          ? 'text-green-600'
                          : 'text-red-600'
                      }
                    >
                      {rec.recommended > rec.current ? '+' : ''}
                      {(((rec.recommended - rec.current) / rec.current) * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td className="p-3 text-center">
                    <Badge
                      variant={rec.confidence >= 80 ? 'default' : 'secondary'}
                    >
                      {rec.confidence}%
                    </Badge>
                  </td>
                  <td className="p-3 text-right">
                    <Button size="sm" variant="outline">
                      Apply
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
};

const QuotaForecastDialog: React.FC<{
  quotaId: string;
  onClose: () => void;
}> = ({ quotaId, onClose }) => {
  const { data: forecast } = useQuery({
    queryKey: ['quota-forecast', quotaId],
    queryFn: () => fetchQuotaForecast(quotaId),
  });

  const { data: aiRec } = useQuery({
    queryKey: ['quota-ai-recommendation', quotaId],
    queryFn: () => fetchAIRecommendation(quotaId),
  });

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Quota Forecast & Analysis</DialogTitle>
          <DialogDescription>
            Detailed forecast and AI recommendations
          </DialogDescription>
        </DialogHeader>

        {forecast && (
          <div className="space-y-6">
            <div className="grid grid-cols-3 gap-4">
              <Card>
                <CardContent className="p-4 text-center">
                  <p className="text-sm text-muted-foreground">Current Attainment</p>
                  <p className="text-2xl font-bold">{forecast.attainment}%</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 text-center">
                  <p className="text-sm text-muted-foreground">Projected</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {forecast.forecast.projected_attainment}%
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 text-center">
                  <p className="text-sm text-muted-foreground">Days Remaining</p>
                  <p className="text-2xl font-bold">{forecast.forecast.days_remaining}</p>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Run Rate Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Daily Run Rate</p>
                    <p className="text-xl font-bold">
                      ${forecast.forecast.daily_run_rate.toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Required Daily</p>
                    <p className="text-xl font-bold">
                      ${forecast.forecast.required_daily_rate.toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="mt-4 p-3 rounded-lg bg-muted">
                  <div className="flex items-center gap-2">
                    {forecast.gap_analysis.on_track ? (
                      <>
                        <CheckCircle className="h-5 w-5 text-green-500" />
                        <span className="font-medium text-green-600">On Track</span>
                      </>
                    ) : (
                      <>
                        <AlertTriangle className="h-5 w-5 text-yellow-500" />
                        <span className="font-medium text-yellow-600">At Risk</span>
                      </>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">
                    {forecast.gap_analysis.on_track
                      ? `Projected to exceed quota by $${forecast.gap_analysis.variance.toLocaleString()}`
                      : `Gap of $${Math.abs(forecast.gap_analysis.variance).toLocaleString()} to close`}
                  </p>
                </div>
              </CardContent>
            </Card>

            {aiRec && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-yellow-500" />
                    AI Recommendation
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Recommended Target</p>
                      <p className="text-xl font-bold">
                        ${aiRec.recommended_target.toLocaleString()}
                      </p>
                    </div>
                    <Badge>{(aiRec.confidence * 100).toFixed(0)}% confidence</Badge>
                  </div>
                  <div className="mt-4 space-y-2">
                    {aiRec.factors.map((f) => (
                      <div key={f.factor} className="flex justify-between text-sm">
                        <span>{f.factor}</span>
                        <span className="font-medium">{(f.weight * 100).toFixed(0)}%</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={onClose}>
                Close
              </Button>
              <Button>Request Adjustment</Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
};

// Main Component
export default function QuotaManagement() {
  const { data: summary, isLoading } = useQuery({
    queryKey: ['quota-summary'],
    queryFn: fetchQuotaSummary,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <Clock className="h-12 w-12 animate-pulse mx-auto mb-4 text-muted-foreground" />
          <p>Loading quota data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Target className="h-8 w-8" />
            Quota Management
          </h1>
          <p className="text-muted-foreground mt-1">
            Track, plan, and optimize sales quotas across your organization
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Select defaultValue="q1-2024">
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Select period" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="q1-2024">Q1 2024</SelectItem>
              <SelectItem value="q4-2023">Q4 2023</SelectItem>
              <SelectItem value="q3-2023">Q3 2023</SelectItem>
            </SelectContent>
          </Select>
          <Button>
            <Calendar className="h-4 w-4 mr-2" />
            New Period
          </Button>
        </div>
      </div>

      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="by-user" className="flex items-center gap-2">
            <Users className="h-4 w-4" />
            By User
          </TabsTrigger>
          <TabsTrigger value="by-territory" className="flex items-center gap-2">
            <Target className="h-4 w-4" />
            By Territory
          </TabsTrigger>
          <TabsTrigger value="ai-planner" className="flex items-center gap-2">
            <Sparkles className="h-4 w-4" />
            AI Planner
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="mt-4">
          <QuotaOverviewTab summary={summary} />
        </TabsContent>

        <TabsContent value="by-user" className="mt-4">
          <QuotasByUserTab users={summary?.by_user} />
        </TabsContent>

        <TabsContent value="by-territory" className="mt-4">
          <QuotasByTerritoryTab territories={summary?.by_territory} />
        </TabsContent>

        <TabsContent value="ai-planner" className="mt-4">
          <AIQuotaPlannerTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}

