'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
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
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Map,
  Users,
  Building2,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  RefreshCw,
  Plus,
  Settings,
  BarChart3,
  ArrowRightLeft,
  Zap,
  ChevronRight,
  ChevronDown,
  Globe,
  Factory,
  CircleDot,
} from 'lucide-react';

// Types
interface Territory {
  id: string;
  name: string;
  code: string;
  type: 'global' | 'region' | 'country' | 'state' | 'city' | 'custom';
  owner: string | null;
  current_accounts: number;
  max_accounts: number;
  total_revenue: number;
  total_pipeline: number;
  children: Territory[];
}

interface TerritoryMetrics {
  territory_id: string;
  territory_name: string;
  current_accounts: number;
  accounts_variance: number;
  pipeline: number;
  pipeline_variance: number;
  capacity_utilization: number;
  is_overloaded: boolean;
  is_underutilized: boolean;
}

interface BalanceAnalysis {
  territories: TerritoryMetrics[];
  analysis: {
    total_territories: number;
    total_accounts: number;
    avg_accounts_per_territory: number;
    total_pipeline: number;
    overloaded_count: number;
    underutilized_count: number;
    balance_score: number;
  };
}

interface Recommendation {
  type: string;
  priority: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  impact: string;
}

// Mock API functions
const fetchTerritoryHierarchy = async (): Promise<Territory[]> => {
  // Simulated API call
  return [
    {
      id: '1',
      name: 'Americas',
      code: 'AMER',
      type: 'region',
      owner: 'John Smith',
      current_accounts: 450,
      max_accounts: 600,
      total_revenue: 12500000,
      total_pipeline: 28000000,
      children: [
        {
          id: '2',
          name: 'United States',
          code: 'US',
          type: 'country',
          owner: 'Sarah Johnson',
          current_accounts: 320,
          max_accounts: 400,
          total_revenue: 8500000,
          total_pipeline: 18000000,
          children: [
            {
              id: '3',
              name: 'West Coast',
              code: 'US-WEST',
              type: 'custom',
              owner: 'Mike Chen',
              current_accounts: 150,
              max_accounts: 180,
              total_revenue: 4200000,
              total_pipeline: 9500000,
              children: [],
            },
            {
              id: '4',
              name: 'East Coast',
              code: 'US-EAST',
              type: 'custom',
              owner: 'Emily Davis',
              current_accounts: 170,
              max_accounts: 200,
              total_revenue: 4300000,
              total_pipeline: 8500000,
              children: [],
            },
          ],
        },
        {
          id: '5',
          name: 'Canada',
          code: 'CA',
          type: 'country',
          owner: 'David Wilson',
          current_accounts: 80,
          max_accounts: 120,
          total_revenue: 2500000,
          total_pipeline: 5500000,
          children: [],
        },
      ],
    },
    {
      id: '6',
      name: 'EMEA',
      code: 'EMEA',
      type: 'region',
      owner: 'Lisa Brown',
      current_accounts: 280,
      max_accounts: 350,
      total_revenue: 8200000,
      total_pipeline: 16000000,
      children: [],
    },
  ];
};

const fetchBalanceAnalysis = async (): Promise<BalanceAnalysis> => {
  return {
    territories: [
      {
        territory_id: '3',
        territory_name: 'West Coast',
        current_accounts: 150,
        accounts_variance: 12.5,
        pipeline: 9500000,
        pipeline_variance: 8.2,
        capacity_utilization: 83.3,
        is_overloaded: false,
        is_underutilized: false,
      },
      {
        territory_id: '4',
        territory_name: 'East Coast',
        current_accounts: 170,
        accounts_variance: 25.0,
        pipeline: 8500000,
        pipeline_variance: -3.2,
        capacity_utilization: 85.0,
        is_overloaded: false,
        is_underutilized: false,
      },
      {
        territory_id: '5',
        territory_name: 'Canada',
        current_accounts: 80,
        accounts_variance: -42.0,
        pipeline: 5500000,
        pipeline_variance: -35.0,
        capacity_utilization: 66.7,
        is_overloaded: false,
        is_underutilized: false,
      },
    ],
    analysis: {
      total_territories: 6,
      total_accounts: 730,
      avg_accounts_per_territory: 121.7,
      total_pipeline: 44000000,
      overloaded_count: 1,
      underutilized_count: 2,
      balance_score: 72,
    },
  };
};

const fetchRecommendations = async (territoryId: string): Promise<Recommendation[]> => {
  return [
    {
      type: 'capacity',
      priority: 'high',
      title: 'Consider Splitting Territory',
      description: 'East Coast territory is approaching capacity. Consider splitting into Northeast and Southeast.',
      impact: 'Better account coverage and reduced rep workload',
    },
    {
      type: 'pipeline',
      priority: 'medium',
      title: 'Pipeline Building Needed',
      description: 'Canada territory has low pipeline coverage (2.2x). Focus on prospecting activities.',
      impact: 'Reduce risk of missing quota',
    },
  ];
};

// Components
const TerritoryTypeIcon: React.FC<{ type: Territory['type'] }> = ({ type }) => {
  switch (type) {
    case 'global':
      return <Globe className="h-4 w-4" />;
    case 'region':
      return <Map className="h-4 w-4" />;
    case 'country':
      return <Building2 className="h-4 w-4" />;
    case 'state':
    case 'city':
      return <CircleDot className="h-4 w-4" />;
    default:
      return <Factory className="h-4 w-4" />;
  }
};

const CapacityBadge: React.FC<{ utilization: number }> = ({ utilization }) => {
  if (utilization >= 90) {
    return <Badge variant="destructive">Overloaded</Badge>;
  } else if (utilization >= 70) {
    return <Badge className="bg-yellow-500">High Load</Badge>;
  } else if (utilization < 40) {
    return <Badge variant="outline">Underutilized</Badge>;
  }
  return <Badge className="bg-green-500">Healthy</Badge>;
};

const TerritoryTreeItem: React.FC<{
  territory: Territory;
  level: number;
  onSelect: (territory: Territory) => void;
}> = ({ territory, level, onSelect }) => {
  const [expanded, setExpanded] = useState(level < 2);
  const hasChildren = territory.children.length > 0;
  const capacityUtil = territory.max_accounts
    ? (territory.current_accounts / territory.max_accounts) * 100
    : 0;

  return (
    <div>
      <div
        className={`flex items-center justify-between p-3 hover:bg-muted/50 cursor-pointer border-l-2 ${
          level === 0 ? 'border-l-primary' : 'border-l-transparent'
        }`}
        style={{ paddingLeft: `${level * 24 + 12}px` }}
        onClick={() => onSelect(territory)}
      >
        <div className="flex items-center gap-3">
          {hasChildren ? (
            <button
              onClick={(e) => {
                e.stopPropagation();
                setExpanded(!expanded);
              }}
              className="p-0.5 hover:bg-muted rounded"
            >
              {expanded ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
            </button>
          ) : (
            <div className="w-5" />
          )}
          <TerritoryTypeIcon type={territory.type} />
          <div>
            <div className="font-medium">{territory.name}</div>
            <div className="text-xs text-muted-foreground">
              {territory.code} • {territory.owner || 'Unassigned'}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right text-sm">
            <div className="font-medium">
              {territory.current_accounts}/{territory.max_accounts}
            </div>
            <div className="text-muted-foreground text-xs">accounts</div>
          </div>
          <div className="text-right text-sm min-w-[100px]">
            <div className="font-medium">
              ${(territory.total_pipeline / 1000000).toFixed(1)}M
            </div>
            <div className="text-muted-foreground text-xs">pipeline</div>
          </div>
          <CapacityBadge utilization={capacityUtil} />
        </div>
      </div>
      {expanded &&
        territory.children.map((child) => (
          <TerritoryTreeItem
            key={child.id}
            territory={child}
            level={level + 1}
            onSelect={onSelect}
          />
        ))}
    </div>
  );
};

const TerritoryHierarchyTab: React.FC<{
  onTerritorySelect: (territory: Territory) => void;
}> = ({ onTerritorySelect }) => {
  const { data: hierarchy, isLoading } = useQuery({
    queryKey: ['territory-hierarchy'],
    queryFn: fetchTerritoryHierarchy,
  });

  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-muted-foreground" />
          <p>Loading territory hierarchy...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <Input placeholder="Search territories..." className="max-w-sm" />
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Create Territory
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Map className="h-5 w-5" />
            Territory Hierarchy
          </CardTitle>
          <CardDescription>
            Manage your sales territories and assignments
          </CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <div className="divide-y">
            {hierarchy?.map((territory) => (
              <TerritoryTreeItem
                key={territory.id}
                territory={territory}
                level={0}
                onSelect={onTerritorySelect}
              />
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

const BalanceAnalysisTab: React.FC = () => {
  const { data: analysis, isLoading } = useQuery({
    queryKey: ['territory-balance'],
    queryFn: fetchBalanceAnalysis,
  });

  const getVarianceColor = (variance: number) => {
    if (Math.abs(variance) < 10) return 'text-green-600';
    if (Math.abs(variance) < 25) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Balance Score</p>
                <p className="text-3xl font-bold">{analysis?.analysis.balance_score}</p>
              </div>
              <div
                className={`h-12 w-12 rounded-full flex items-center justify-center ${
                  (analysis?.analysis.balance_score || 0) >= 80
                    ? 'bg-green-100 text-green-600'
                    : (analysis?.analysis.balance_score || 0) >= 60
                    ? 'bg-yellow-100 text-yellow-600'
                    : 'bg-red-100 text-red-600'
                }`}
              >
                <BarChart3 className="h-6 w-6" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground">Total Accounts</p>
            <p className="text-2xl font-bold">{analysis?.analysis.total_accounts}</p>
            <p className="text-xs text-muted-foreground mt-1">
              Avg: {analysis?.analysis.avg_accounts_per_territory.toFixed(0)} per territory
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground">Overloaded</p>
            <p className="text-2xl font-bold text-red-600">
              {analysis?.analysis.overloaded_count}
            </p>
            <p className="text-xs text-muted-foreground mt-1">territories</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground">Underutilized</p>
            <p className="text-2xl font-bold text-yellow-600">
              {analysis?.analysis.underutilized_count}
            </p>
            <p className="text-xs text-muted-foreground mt-1">territories</p>
          </CardContent>
        </Card>
      </div>

      {/* Territory Comparison */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Territory Comparison</CardTitle>
              <CardDescription>
                Account and pipeline distribution analysis
              </CardDescription>
            </div>
            <Button variant="outline">
              <ArrowRightLeft className="h-4 w-4 mr-2" />
              Request Rebalance
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {analysis?.territories.map((t) => (
              <div key={t.territory_id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h4 className="font-medium">{t.territory_name}</h4>
                    <div className="flex items-center gap-4 mt-1">
                      <span className="text-sm text-muted-foreground">
                        {t.current_accounts} accounts
                      </span>
                      <span className="text-sm text-muted-foreground">
                        ${(t.pipeline / 1000000).toFixed(1)}M pipeline
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {t.is_overloaded && (
                      <Badge variant="destructive">Overloaded</Badge>
                    )}
                    {t.is_underutilized && (
                      <Badge variant="outline">Underutilized</Badge>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span>Capacity Utilization</span>
                      <span className="font-medium">
                        {t.capacity_utilization.toFixed(0)}%
                      </span>
                    </div>
                    <Progress value={t.capacity_utilization} />
                  </div>
                  <div className="flex gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Account Variance:</span>
                      <span
                        className={`ml-2 font-medium ${getVarianceColor(
                          t.accounts_variance
                        )}`}
                      >
                        {t.accounts_variance > 0 ? '+' : ''}
                        {t.accounts_variance.toFixed(1)}%
                      </span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Pipeline Variance:</span>
                      <span
                        className={`ml-2 font-medium ${getVarianceColor(
                          t.pipeline_variance
                        )}`}
                      >
                        {t.pipeline_variance > 0 ? '+' : ''}
                        {t.pipeline_variance.toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

const RecommendationsTab: React.FC = () => {
  const { data: recommendations, isLoading } = useQuery({
    queryKey: ['territory-recommendations'],
    queryFn: () => fetchRecommendations('all'),
  });

  const getPriorityColor = (priority: Recommendation['priority']) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  if (isLoading) {
    return <div>Loading recommendations...</div>;
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            AI Optimization Recommendations
          </CardTitle>
          <CardDescription>
            Intelligent suggestions to optimize your territory structure
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recommendations?.map((rec, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {rec.priority === 'high' ? (
                      <AlertTriangle className="h-5 w-5 text-red-500" />
                    ) : (
                      <TrendingUp className="h-5 w-5 text-yellow-500" />
                    )}
                    <h4 className="font-medium">{rec.title}</h4>
                  </div>
                  <Badge className={getPriorityColor(rec.priority)}>
                    {rec.priority}
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground mb-3">
                  {rec.description}
                </p>
                <div className="flex items-center justify-between">
                  <div className="text-sm">
                    <span className="text-muted-foreground">Impact: </span>
                    <span>{rec.impact}</span>
                  </div>
                  <Button size="sm">Apply Recommendation</Button>
                </div>
              </div>
            ))}

            {(!recommendations || recommendations.length === 0) && (
              <div className="text-center py-8 text-muted-foreground">
                <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-500" />
                <p>All territories are optimally configured!</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

const TerritoryDetailDialog: React.FC<{
  territory: Territory | null;
  onClose: () => void;
}> = ({ territory, onClose }) => {
  if (!territory) return null;

  const capacityUtil = territory.max_accounts
    ? (territory.current_accounts / territory.max_accounts) * 100
    : 0;

  return (
    <Dialog open={!!territory} onOpenChange={() => onClose()}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <TerritoryTypeIcon type={territory.type} />
            {territory.name}
          </DialogTitle>
          <DialogDescription>
            Territory code: {territory.code}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Owner</label>
              <Input value={territory.owner || 'Unassigned'} readOnly />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Type</label>
              <Input value={territory.type} readOnly />
            </div>
          </div>

          <div>
            <label className="text-sm font-medium mb-2 block">
              Capacity Utilization
            </label>
            <div className="flex items-center gap-4">
              <Progress value={capacityUtil} className="flex-1" />
              <span className="text-sm font-medium">
                {capacityUtil.toFixed(0)}%
              </span>
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {territory.current_accounts} of {territory.max_accounts} accounts
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Card>
              <CardContent className="p-4">
                <p className="text-sm text-muted-foreground">Total Revenue</p>
                <p className="text-2xl font-bold">
                  ${(territory.total_revenue / 1000000).toFixed(2)}M
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <p className="text-sm text-muted-foreground">Total Pipeline</p>
                <p className="text-2xl font-bold">
                  ${(territory.total_pipeline / 1000000).toFixed(2)}M
                </p>
              </CardContent>
            </Card>
          </div>

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={onClose}>
              Close
            </Button>
            <Button>
              <Settings className="h-4 w-4 mr-2" />
              Edit Territory
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

// Main Component
export default function TerritoryDashboard() {
  const [selectedTerritory, setSelectedTerritory] = useState<Territory | null>(
    null
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Map className="h-8 w-8" />
            Territory Management
          </h1>
          <p className="text-muted-foreground mt-1">
            Manage sales territories, assignments, and capacity planning
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Select defaultValue="all">
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Filter by region" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Regions</SelectItem>
              <SelectItem value="americas">Americas</SelectItem>
              <SelectItem value="emea">EMEA</SelectItem>
              <SelectItem value="apac">APAC</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Sync Data
          </Button>
        </div>
      </div>

      <Tabs defaultValue="hierarchy">
        <TabsList>
          <TabsTrigger value="hierarchy" className="flex items-center gap-2">
            <Map className="h-4 w-4" />
            Hierarchy
          </TabsTrigger>
          <TabsTrigger value="balance" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Balance Analysis
          </TabsTrigger>
          <TabsTrigger value="recommendations" className="flex items-center gap-2">
            <Zap className="h-4 w-4" />
            AI Recommendations
          </TabsTrigger>
        </TabsList>

        <TabsContent value="hierarchy" className="mt-4">
          <TerritoryHierarchyTab onTerritorySelect={setSelectedTerritory} />
        </TabsContent>

        <TabsContent value="balance" className="mt-4">
          <BalanceAnalysisTab />
        </TabsContent>

        <TabsContent value="recommendations" className="mt-4">
          <RecommendationsTab />
        </TabsContent>
      </Tabs>

      <TerritoryDetailDialog
        territory={selectedTerritory}
        onClose={() => setSelectedTerritory(null)}
      />
    </div>
  );
}
