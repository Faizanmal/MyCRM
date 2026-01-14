'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  ChartBarIcon,
  CurrencyDollarIcon,
  ClockIcon,
  FunnelIcon,
  BoltIcon,
} from '@heroicons/react/24/outline';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  PieLabelRenderProps,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

import { analyticsAPI } from '@/lib/api';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

interface PipelineHealthData {
  health_score?: number;
  total_pipeline_value?: number;
  deal_count?: number;
  by_stage?: Array<Record<string, unknown>>;
}

interface DealVelocityData {
  average_days?: number;
  by_stage?: Array<Record<string, unknown>>;
}

interface ConversionFunnelData {
  overall_conversion_rate?: number;
  stage_metrics?: Array<Record<string, unknown>>;
}

interface AnalyticsData {
  pipeline_health?: PipelineHealthData;
  deal_velocity?: DealVelocityData;
  conversion_funnel?: ConversionFunnelData;
}

interface SalesForecastData {
  monthly_forecast?: Array<Record<string, unknown>>;
  confidence_score?: number;
  total_predicted?: number;
}

interface AIInsightsData {
  insights?: Array<Record<string, unknown>>;
}

export default function PipelineAnalyticsPage() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [forecast, setForecast] = useState<SalesForecastData | null>(null);
  const [aiInsights, setAIInsights] = useState<AIInsightsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [forecastMonths, setForecastMonths] = useState(3);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [analyticsRes, forecastRes, insightsRes] = await Promise.all([
        analyticsAPI.getPipelineAnalytics(),
        analyticsAPI.getSalesForecast(forecastMonths),
        analyticsAPI.getAIInsights(),
      ]);
      
      setAnalytics(analyticsRes.data);
      setForecast(forecastRes.data);
      setAIInsights(insightsRes.data);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  }, [forecastMonths]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  if (loading) {
    return (
      <ProtectedRoute>
        <MainLayout>
          <div className="flex items-center justify-center h-96">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        </MainLayout>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-6">
          {/* Header */}
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900 flex items-center">
              <ChartBarIcon className="w-8 h-8 mr-3 text-blue-600" />
              Pipeline Analytics & Forecasting
            </h1>
            <p className="text-gray-600 mt-1">AI-powered insights into your sales pipeline</p>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {/* Pipeline Health */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-gray-600">Pipeline Health</h3>
                <BoltIcon className="w-6 h-6 text-green-600" />
              </div>
              <div className="flex items-baseline">
                <span className="text-3xl font-bold text-gray-900">
                  {analytics?.pipeline_health?.health_score || 0}
                </span>
                <span className="text-xl text-gray-500 ml-1">/100</span>
              </div>
              <div className="mt-2">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-green-600 h-2 rounded-full"
                    style={{ width: `${analytics?.pipeline_health?.health_score || 0}%` }}
                  ></div>
                </div>
              </div>
            </div>

            {/* Total Pipeline Value */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-gray-600">Pipeline Value</h3>
                <CurrencyDollarIcon className="w-6 h-6 text-blue-600" />
              </div>
              <div className="text-3xl font-bold text-gray-900">
                ${analytics?.pipeline_health?.total_pipeline_value?.toLocaleString() || 0}
              </div>
              <p className="text-sm text-gray-500 mt-1">
                {analytics?.pipeline_health?.deal_count || 0} active deals
              </p>
            </div>

            {/* Avg Deal Velocity */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-gray-600">Deal Velocity</h3>
                <ClockIcon className="w-6 h-6 text-purple-600" />
              </div>
              <div className="text-3xl font-bold text-gray-900">
                {analytics?.deal_velocity?.average_days?.toFixed(0) || 0}
              </div>
              <p className="text-sm text-gray-500 mt-1">days to close</p>
            </div>

            {/* Conversion Rate */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-gray-600">Conversion Rate</h3>
                <FunnelIcon className="w-6 h-6 text-orange-600" />
              </div>
              <div className="text-3xl font-bold text-gray-900">
                {analytics?.conversion_funnel?.overall_conversion_rate?.toFixed(1) || 0}%
              </div>
              <p className="text-sm text-gray-500 mt-1">overall rate</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* Sales Forecast */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Sales Forecast</h3>
                <select
                  value={forecastMonths}
                  onChange={(e) => setForecastMonths(Number(e.target.value))}
                  className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
                >
                  <option value={3}>3 Months</option>
                  <option value={6}>6 Months</option>
                  <option value={12}>12 Months</option>
                </select>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={forecast?.monthly_forecast || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip formatter={(value: number | string) => `$${Number(value).toLocaleString()}`} />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="predicted_revenue"
                    stroke="#3B82F6"
                    strokeWidth={2}
                    name="Predicted Revenue"
                  />
                  <Line
                    type="monotone"
                    dataKey="confidence_lower"
                    stroke="#94A3B8"
                    strokeDasharray="5 5"
                    name="Lower Bound"
                  />
                  <Line
                    type="monotone"
                    dataKey="confidence_upper"
                    stroke="#94A3B8"
                    strokeDasharray="5 5"
                    name="Upper Bound"
                  />
                </LineChart>
              </ResponsiveContainer>
              <div className="mt-4 grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Total Forecast</p>
                  <p className="text-xl font-bold text-gray-900">
                    ${(forecast?.total_predicted as number)?.toLocaleString?.() || 0}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Confidence</p>
                  <p className="text-xl font-bold text-gray-900">
                    {(forecast?.confidence_score as number)?.toFixed?.(0) || 0}%
                  </p>
                </div>
              </div>
            </div>

            {/* Conversion Funnel */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Conversion Funnel</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={analytics?.conversion_funnel?.stage_metrics || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="stage" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="count" fill="#3B82F6" name="Opportunities" />
                  <Bar dataKey="value" fill="#10B981" name="Value ($)" />
                </BarChart>
              </ResponsiveContainer>
              <div className="mt-4">
                <p className="text-sm text-gray-600 mb-2">Stage Conversion Rates</p>
                <div className="space-y-2">
                  {analytics?.conversion_funnel?.stage_metrics?.map((stage: Record<string, unknown>, index: number) => (
                    <div key={index} className="flex items-center justify-between">
                      <span className="text-sm text-gray-700">{stage.stage as string}</span>
                      <span className="text-sm font-medium text-gray-900">
                        {(stage.conversion_rate as number)?.toFixed(1)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Pipeline by Stage */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Pipeline by Stage</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={analytics?.pipeline_health?.by_stage || []}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(props: PieLabelRenderProps) => `${(props.name as string)}: ${(((props.percent as number) || 0) * 100).toFixed(0)}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {analytics?.pipeline_health?.by_stage?.map((entry: Record<string, unknown>, index: number) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number | string) => `$${Number(value).toLocaleString()}`} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* AI Insights */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <BoltIcon className="w-5 h-5 mr-2 text-yellow-500" />
                AI Insights
              </h3>
              <div className="space-y-4">
                {aiInsights?.insights?.slice(0, 5).map((insight: Record<string, unknown>, index: number) => (
                  <div key={index} className="flex items-start space-x-3">
                    <div className={`shrink-0 w-2 h-2 mt-2 rounded-full ${
                      (insight.priority as string) === 'high' ? 'bg-red-500' :
                      (insight.priority as string) === 'medium' ? 'bg-yellow-500' :
                      'bg-blue-500'
                    }`}></div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{insight.title as string}</p>
                      <p className="text-sm text-gray-600">{insight.description as string}</p>
                      {(insight.recommendation as string) && (
                        <p className="text-sm text-blue-600 mt-1">
                          💡 {insight.recommendation as string}
                        </p>
                      )}
                    </div>
                  </div>
                )) || (
                  <p className="text-gray-500 text-center py-8">
                    No insights available yet. More data is needed for AI analysis.
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Deal Velocity by Stage */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Deal Velocity by Stage</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analytics?.deal_velocity?.by_stage || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="stage" />
                <YAxis label={{ value: 'Days', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="average_days" fill="#8B5CF6" name="Avg Days in Stage" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}

