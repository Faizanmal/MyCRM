"use client";

import React, { useState } from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  Target, 
  Brain,
  AlertCircle,
  CheckCircle,
  Clock,
  Lightbulb,
  BarChart3,
  PieChart
} from 'lucide-react';
import { useQuery } from '@tanstack/react-query';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { enterpriseAPI } from '@/lib/enterprise-api';

interface CustomerSegmentInsight {
  count?: number;
  avg_value?: number;
  churn_risk?: number;
  recommendations?: string[];
  percentage?: number;
}

interface CustomerSegments {
  insights: Record<string, CustomerSegmentInsight>;
  total_segments?: number;
  total_customers?: number;
}

interface ChurnRiskCustomer {
  id: string;
  name?: string;
  contact_name?: string;
  risk_score: number;
  risk_level?: string;
  last_activity: string;
}

interface ChurnRisk {
  high_risk_customers: ChurnRiskCustomer[];
  total_at_risk: number;
  predicted_churn_rate?: number;
  recommendations?: string[];
}

interface AIInsights {
  customer_segments: CustomerSegments;
  churn_risk: ChurnRisk;
  sales_forecast?: Record<string, unknown>;
  predictive_analytics?: Record<string, unknown>;
  insights?: Array<Record<string, unknown>>;
}

interface SalesForecast {
  monthly_forecast?: Array<Record<string, unknown>>;
  confidence_score?: number;
  forecast_amount?: number;
  growth_rate?: number;
  historical_average?: number;
  confidence_interval?: [number, number];
  trend?: string;
  recommendations?: string[];
  forecast?: Record<string, unknown>;
  confidence?: number;
}

interface LeadScore {
  score?: number;
  total_score?: number;
  quality?: string;
  priority?: string;
  score_breakdown: Record<string, number>;
  recommendations?: string[];
}

const AIAnalyticsDashboard = () => {
  const [selectedPeriod, setSelectedPeriod] = useState('3');
  const [selectedLeadId, setSelectedLeadId] = useState('');

  const { data: aiInsights, isLoading: insightsLoading } = useQuery({
    queryKey: ['ai-insights'],
    queryFn: enterpriseAPI.ai.getAIInsightsDashboard,
    refetchInterval: 300000, // Refresh every 5 minutes
  });

  const { data: salesForecast, isLoading: forecastLoading } = useQuery({
    queryKey: ['sales-forecast', selectedPeriod],
    queryFn: () => enterpriseAPI.ai.getSalesForcast(parseInt(selectedPeriod)),
    enabled: !!selectedPeriod,
  });

  const { data: leadScore, isLoading: scoreLoading } = useQuery({
    queryKey: ['lead-score', selectedLeadId],
    queryFn: () => enterpriseAPI.ai.calculateLeadScore(parseInt(selectedLeadId)),
    enabled: !!selectedLeadId,
  });

  if (insightsLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-48 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">AI Analytics Dashboard</h1>
          <p className="text-muted-foreground">
            Intelligent insights and predictions powered by machine learning
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="outline" className="bg-blue-50 text-blue-700">
            <Brain className="h-3 w-3 mr-1" />
            AI Powered
          </Badge>
        </div>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="forecast">Sales Forecast</TabsTrigger>
          <TabsTrigger value="segmentation">Customer Segments</TabsTrigger>
          <TabsTrigger value="scoring">Lead Scoring</TabsTrigger>
          <TabsTrigger value="churn">Churn Prediction</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <AIOverview aiInsights={aiInsights} />
        </TabsContent>

        <TabsContent value="forecast" className="space-y-6">
          <SalesForecastView 
            salesForecast={salesForecast}
            forecastLoading={forecastLoading}
            selectedPeriod={selectedPeriod}
            setSelectedPeriod={setSelectedPeriod}
          />
        </TabsContent>

        <TabsContent value="segmentation" className="space-y-6">
          <CustomerSegmentationView aiInsights={aiInsights} />
        </TabsContent>

        <TabsContent value="scoring" className="space-y-6">
          <LeadScoringView 
            leadScore={leadScore}
            scoreLoading={scoreLoading}
            selectedLeadId={selectedLeadId}
            setSelectedLeadId={setSelectedLeadId}
          />
        </TabsContent>

        <TabsContent value="churn" className="space-y-6">
          <ChurnPredictionView aiInsights={aiInsights} />
        </TabsContent>
      </Tabs>
    </div>
  );
};

const AIOverview = ({ aiInsights }: { aiInsights: AIInsights }) => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {/* Sales Forecast Summary */}
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Revenue Forecast</CardTitle>
        <TrendingUp className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">
          ${aiInsights?.sales_forecast?.forecast_amount?.toLocaleString() || 0}
        </div>
        <p className="text-xs text-muted-foreground">
          Next 3 months • {(aiInsights?.sales_forecast?.growth_rate as number) > 0 ? '+' : ''}{(aiInsights?.sales_forecast?.growth_rate as number) || 0}% growth
        </p>
        <div className="flex items-center pt-2">
          {getTrendIcon((aiInsights?.sales_forecast?.trend as string) || '')}
          <span className="text-xs ml-1 capitalize">{(aiInsights?.sales_forecast?.trend as string) || ''}</span>
        </div>
      </CardContent>
    </Card>

    {/* Customer Segments */}
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Customer Segments</CardTitle>
        <PieChart className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">
          {aiInsights?.customer_segments?.total_customers || 0}
        </div>
        <p className="text-xs text-muted-foreground">Total customers</p>
        <div className="space-y-1 pt-2">
          {Object.entries(aiInsights?.customer_segments?.insights || {}).slice(0, 3).map(([segment, data]: [string, CustomerSegmentInsight]) => (
            <div key={segment} className="flex justify-between text-xs">
              <span className="capitalize">{segment.replace('_', ' ')}</span>
              <span>{data.percentage}%</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>

    {/* Churn Risk */}
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Churn Risk</CardTitle>
        <AlertCircle className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-red-600">
          {aiInsights?.churn_risk?.total_at_risk || 0}
        </div>
        <p className="text-xs text-muted-foreground">High-risk customers</p>
        <div className="flex items-center pt-2">
          <AlertCircle className="h-3 w-3 text-red-600" />
          <span className="text-xs ml-1">Immediate attention needed</span>
        </div>
      </CardContent>
    </Card>

    {/* AI Recommendations */}
    <Card className="md:col-span-2 lg:col-span-3">
      <CardHeader>
        <CardTitle className="flex items-center">
          <Lightbulb className="h-5 w-5 mr-2" />
          AI Recommendations
        </CardTitle>
        <CardDescription>Actionable insights based on your data</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-3">
            <h4 className="font-medium">Sales Forecast</h4>
            {((aiInsights?.sales_forecast?.recommendations as string[]) || [])?.slice(0, 3).map((rec: string, index: number) => (
              <div key={index} className="flex items-start space-x-2">
                <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 shrink-0" />
                <span className="text-sm">{rec}</span>
              </div>
            ))}
          </div>
          <div className="space-y-3">
            <h4 className="font-medium">Customer Retention</h4>
            {aiInsights?.churn_risk?.recommendations?.slice(0, 3).map((rec: string, index: number) => (
              <div key={index} className="flex items-start space-x-2">
                <AlertCircle className="h-4 w-4 text-orange-600 mt-0.5 shrink-0" />
                <span className="text-sm">{rec}</span>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  </div>
);

const SalesForecastView = ({ 
  salesForecast, 
  forecastLoading, 
  selectedPeriod, 
  setSelectedPeriod 
}: { 
  salesForecast: SalesForecast;
  forecastLoading: boolean;
  selectedPeriod: string;
  setSelectedPeriod: (period: string) => void;
}) => (
  <div className="space-y-6">
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Sales Revenue Forecast</CardTitle>
            <CardDescription>AI-powered revenue predictions based on historical data</CardDescription>
          </div>
          <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1">1 Month</SelectItem>
              <SelectItem value="3">3 Months</SelectItem>
              <SelectItem value="6">6 Months</SelectItem>
              <SelectItem value="12">12 Months</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </CardHeader>
      <CardContent>
        {forecastLoading ? (
          <div className="h-64 flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600">
                  ${salesForecast?.forecast_amount?.toLocaleString() || 0}
                </div>
                <div className="text-sm text-muted-foreground">Predicted Revenue</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold">
                  {(salesForecast?.growth_rate as number) > 0 ? '+' : ''}{(salesForecast?.growth_rate as number) || 0}%
                </div>
                <div className="text-sm text-muted-foreground">Growth Rate</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold">
                  ${salesForecast?.historical_average?.toLocaleString() || 0}
                </div>
                <div className="text-sm text-muted-foreground">Historical Average</div>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Confidence Range</span>
                  <span>
                    ${salesForecast?.confidence_interval?.[0]?.toLocaleString()} - 
                    ${salesForecast?.confidence_interval?.[1]?.toLocaleString()}
                  </span>
                </div>
                <Progress 
                  value={75} 
                  className="w-full h-2"
                />
              </div>

              <div className="flex items-center space-x-2">
                {getTrendIcon(salesForecast?.trend || '')}
                <span className="text-sm font-medium capitalize">
                  {salesForecast?.trend || 'stable'} Trend
                </span>
              </div>
            </div>

            <div>
              <h4 className="font-medium mb-3">Recommendations</h4>
              <div className="space-y-2">
                {salesForecast?.recommendations?.map((rec: string, index: number) => (
                  <div key={index} className="flex items-start space-x-2">
                    <Lightbulb className="h-4 w-4 text-yellow-600 mt-0.5 shrink-0" />
                    <span className="text-sm">{rec}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  </div>
);

const CustomerSegmentationView = ({ aiInsights }: { aiInsights: AIInsights }) => (
  <div className="space-y-6">
    <Card>
      <CardHeader>
        <CardTitle>Customer Segmentation Analysis</CardTitle>
        <CardDescription>AI-driven customer categorization for targeted strategies</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(aiInsights?.customer_segments?.insights || {}).map(([segment, data]: [string, CustomerSegmentInsight]) => (
            <Card key={segment}>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base capitalize">
                    {segment.replace('_', ' ')}
                  </CardTitle>
                  <Badge className={getSegmentColor(segment)}>
                    {data.count}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div>
                    <Progress value={data.percentage} className="w-full" />
                    <div className="text-xs text-muted-foreground mt-1">
                      {data.percentage}% of total customers
                    </div>
                  </div>
                  <div>
                    <h5 className="text-sm font-medium mb-2">Recommendations:</h5>
                    <ul className="text-xs space-y-1">
                      {data.recommendations?.slice(0, 2).map((rec: string, index: number) => (
                        <li key={index} className="flex items-start space-x-1">
                          <span>•</span>
                          <span>{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </CardContent>
    </Card>
  </div>
);

const LeadScoringView = ({ 
  leadScore, 
  scoreLoading, 
  selectedLeadId, 
  setSelectedLeadId 
}: { 
  leadScore: LeadScore;
  scoreLoading: boolean;
  selectedLeadId: string;
  setSelectedLeadId: (id: string) => void;
}) => (
  <div className="space-y-6">
    <Card>
      <CardHeader>
        <CardTitle>AI Lead Scoring</CardTitle>
        <CardDescription>Intelligent lead qualification and prioritization</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex space-x-4">
            <Input 
              placeholder="Enter Lead ID" 
              value={selectedLeadId}
              onChange={(e) => setSelectedLeadId(e.target.value)}
              className="max-w-xs"
            />
            <Button 
              onClick={() => {/* Query will auto-refresh */}}
              disabled={!selectedLeadId || scoreLoading}
            >
              Analyze Lead
            </Button>
          </div>

          {scoreLoading && (
            <div className="h-48 flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          )}

          {leadScore && !scoreLoading && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-4xl font-bold text-blue-600">
                    {leadScore.total_score}
                  </div>
                  <div className="text-sm text-muted-foreground">Overall Score</div>
                </div>
                <div className="text-center">
                  <Badge className={getQualityColor(leadScore.quality || '')} variant="secondary">
                    {leadScore.quality?.toUpperCase() || 'UNKNOWN'}
                  </Badge>
                  <div className="text-sm text-muted-foreground mt-1">Quality Rating</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold capitalize">
                    {leadScore.priority}
                  </div>
                  <div className="text-sm text-muted-foreground">Priority Level</div>
                </div>
              </div>

              <div>
                <div className="space-y-3">
                  {Object.entries(leadScore.score_breakdown || {}).map(([component, score]: [string, number]) => (
                    <div key={component}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="capitalize">{component}</span>
                        <span>{score}/100</span>
                      </div>
                      <Progress value={score} className="w-full h-2" />
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="font-medium mb-3">Recommendations</h4>
                <div className="space-y-2">
                  {leadScore.recommendations?.map((rec: string, index: number) => (
                    <div key={index} className="flex items-start space-x-2">
                      <Target className="h-4 w-4 text-blue-600 mt-0.5 shrink-0" />
                      <span className="text-sm">{rec}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  </div>
);

const ChurnPredictionView = ({ aiInsights }: { aiInsights: AIInsights }) => (
  <div className="space-y-6">
    <Card>
      <CardHeader>
        <CardTitle>Customer Churn Prediction</CardTitle>
        <CardDescription>Identify at-risk customers before they leave</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="text-center p-6 border rounded-lg">
              <div className="text-3xl font-bold text-red-600">
                {aiInsights?.churn_risk?.total_at_risk || 0}
              </div>
              <div className="text-sm text-muted-foreground">High-Risk Customers</div>
            </div>
            <div className="text-center p-6 border rounded-lg">
              <div className="text-3xl font-bold text-green-600">
                {((aiInsights?.customer_segments?.total_customers || 0) - (aiInsights?.churn_risk?.total_at_risk || 0))}
              </div>
              <div className="text-sm text-muted-foreground">Safe Customers</div>
            </div>
          </div>

          <div>
            <h4 className="font-medium mb-3">High-Risk Customers</h4>
            <div className="space-y-2">
              {aiInsights?.churn_risk?.high_risk_customers?.slice(0, 5).map((customer: ChurnRiskCustomer, index: number) => (
                <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <div className="font-medium">{customer.contact_name}</div>
                    <div className="text-sm text-muted-foreground">
                      Risk Score: {Math.round(customer.risk_score * 100)}%
                    </div>
                  </div>
                  <Badge variant="destructive">
                    {(customer.risk_level || 'MEDIUM').toUpperCase()}
                  </Badge>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h4 className="font-medium mb-3">Action Plan</h4>
            <div className="space-y-2">
              {aiInsights?.churn_risk?.recommendations?.map((rec: string, index: number) => (
                <div key={index} className="flex items-start space-x-2">
                  <Clock className="h-4 w-4 text-orange-600 mt-0.5 shrink-0" />
                  <span className="text-sm">{rec}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  </div>
);

// Helper functions (keeping original implementations)
function getTrendIcon(trend: string) {
  switch (trend) {
    case 'increasing':
      return <TrendingUp className="h-4 w-4 text-green-600" />;
    case 'decreasing':
      return <TrendingDown className="h-4 w-4 text-red-600" />;
    default:
      return <BarChart3 className="h-4 w-4 text-blue-600" />;
  }
}

function getQualityColor(quality: string) {
  const colors: { [key: string]: string } = {
    hot: 'text-red-600 bg-red-100',
    warm: 'text-orange-600 bg-orange-100',
    cold: 'text-blue-600 bg-blue-100',
  };
  return colors[quality] || 'text-gray-600 bg-gray-100';
}

function getSegmentColor(segment: string) {
  const colors: { [key: string]: string } = {
    high_value: 'text-purple-600 bg-purple-100',
    loyal: 'text-green-600 bg-green-100',
    at_risk: 'text-red-600 bg-red-100',
    new: 'text-blue-600 bg-blue-100',
    inactive: 'text-gray-600 bg-gray-100',
  };
  return colors[segment] || 'text-gray-600 bg-gray-100';
}

export default AIAnalyticsDashboard;
