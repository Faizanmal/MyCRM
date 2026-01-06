'use client';

import React, { useMemo, useState } from 'react';
import {
    Line, AreaChart, Area, BarChart, Bar,
    PieChart, Pie, Cell,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend,
    ResponsiveContainer, ComposedChart
} from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
    TrendingUp, TrendingDown, BarChart3, PieChart as PieChartIcon
} from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Dashboard Analytics Components
 * 
 * Provides comprehensive analytics visualizations:
 * - KPI cards with trends
 * - Revenue charts
 * - Pipeline analysis
 * - Activity tracking
 * - Performance metrics
 */

// Color palette
const COLORS = {
    primary: '#3b82f6',
    secondary: '#8b5cf6',
    success: '#22c55e',
    warning: '#f59e0b',
    danger: '#ef4444',
    info: '#06b6d4',
    muted: '#6b7280',
};

const CHART_COLORS = ['#3b82f6', '#8b5cf6', '#22c55e', '#f59e0b', '#ef4444', '#06b6d4'];

interface KPICardProps {
    title: string;
    value: string | number;
    change?: number;
    changeLabel?: string;
    icon?: React.ReactNode;
    trend?: 'up' | 'down' | 'neutral';
    description?: string;
    className?: string;
}

export function KPICard({
    title,
    value,
    change,
    changeLabel = 'vs last period',
    icon,
    trend,
    description,
    className,
}: KPICardProps) {
    const getTrendColor = () => {
        if (trend === 'up') return 'text-green-600 bg-green-50';
        if (trend === 'down') return 'text-red-600 bg-red-50';
        return 'text-gray-600 bg-gray-50';
    };

    const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : null;

    return (
        <Card className={cn('overflow-hidden', className)}>
            <CardContent className="p-6">
                <div className="flex items-center justify-between">
                    <div className="space-y-1">
                        <p className="text-sm font-medium text-gray-500">{title}</p>
                        <p className="text-2xl font-bold">{value}</p>
                        {change !== undefined && (
                            <div className="flex items-center gap-1">
                                <Badge variant="outline" className={cn('text-xs', getTrendColor())}>
                                    {TrendIcon && <TrendIcon className="h-3 w-3 mr-1" />}
                                    {change > 0 ? '+' : ''}{change}%
                                </Badge>
                                <span className="text-xs text-gray-500">{changeLabel}</span>
                            </div>
                        )}
                        {description && (
                            <p className="text-xs text-gray-500 mt-1">{description}</p>
                        )}
                    </div>
                    {icon && (
                        <div className="h-12 w-12 rounded-full bg-blue-50 flex items-center justify-center text-blue-600">
                            {icon}
                        </div>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}

interface RevenueChartProps {
    data: {
        month: string;
        revenue: number;
        target?: number;
        lastYear?: number;
    }[];
    className?: string;
}

export function RevenueChart({ data, className }: RevenueChartProps) {
    const [chartType, setChartType] = useState<'area' | 'bar'>('area');

    return (
        <Card className={className}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
                <div>
                    <CardTitle>Revenue Overview</CardTitle>
                    <CardDescription>Monthly revenue performance</CardDescription>
                </div>
                <Select value={chartType} onValueChange={(v) => setChartType(v as 'area' | 'bar')}>
                    <SelectTrigger className="w-24">
                        <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="area">Area</SelectItem>
                        <SelectItem value="bar">Bar</SelectItem>
                    </SelectContent>
                </Select>
            </CardHeader>
            <CardContent>
                <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                        {chartType === 'area' ? (
                            <AreaChart data={data}>
                                <defs>
                                    <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor={COLORS.primary} stopOpacity={0.3} />
                                        <stop offset="95%" stopColor={COLORS.primary} stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                                <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                                <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => `$${v / 1000}k`} />
                                <Tooltip
                                    formatter={(value: number) => [`$${value.toLocaleString()}`, 'Revenue']}
                                    contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
                                />
                                <Legend />
                                <Area
                                    type="monotone"
                                    dataKey="revenue"
                                    stroke={COLORS.primary}
                                    fillOpacity={1}
                                    fill="url(#colorRevenue)"
                                    name="Revenue"
                                />
                                {data[0]?.target && (
                                    <Line
                                        type="monotone"
                                        dataKey="target"
                                        stroke={COLORS.warning}
                                        strokeDasharray="5 5"
                                        name="Target"
                                    />
                                )}
                            </AreaChart>
                        ) : (
                            <BarChart data={data}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                                <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                                <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => `$${v / 1000}k`} />
                                <Tooltip
                                    formatter={(value: number) => [`$${value.toLocaleString()}`, 'Revenue']}
                                    contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
                                />
                                <Legend />
                                <Bar dataKey="revenue" fill={COLORS.primary} radius={[4, 4, 0, 0]} name="Revenue" />
                                {data[0]?.lastYear && (
                                    <Bar dataKey="lastYear" fill={COLORS.muted} radius={[4, 4, 0, 0]} name="Last Year" />
                                )}
                            </BarChart>
                        )}
                    </ResponsiveContainer>
                </div>
            </CardContent>
        </Card>
    );
}

interface PipelineChartProps {
    data: {
        stage: string;
        count: number;
        value: number;
    }[];
    className?: string;
}

export function PipelineChart({ data, className }: PipelineChartProps) {
    const [view, setView] = useState<'funnel' | 'pie'>('funnel');

    const totalValue = useMemo(() =>
        data.reduce((sum, item) => sum + item.value, 0),
        [data]
    );

    return (
        <Card className={className}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
                <div>
                    <CardTitle>Sales Pipeline</CardTitle>
                    <CardDescription>
                        Total: ${totalValue.toLocaleString()}
                    </CardDescription>
                </div>
                <Tabs value={view} onValueChange={(v) => setView(v as 'funnel' | 'pie')}>
                    <TabsList className="h-8">
                        <TabsTrigger value="funnel" className="text-xs px-2">
                            <BarChart3 className="h-3 w-3" />
                        </TabsTrigger>
                        <TabsTrigger value="pie" className="text-xs px-2">
                            <PieChartIcon className="h-3 w-3" />
                        </TabsTrigger>
                    </TabsList>
                </Tabs>
            </CardHeader>
            <CardContent>
                <div className="h-72">
                    <ResponsiveContainer width="100%" height="100%">
                        {view === 'funnel' ? (
                            <BarChart data={data} layout="vertical">
                                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                                <XAxis type="number" tickFormatter={(v) => `$${v / 1000}k`} />
                                <YAxis dataKey="stage" type="category" width={100} tick={{ fontSize: 11 }} />
                                <Tooltip
                                    formatter={(value: number) => [`$${value.toLocaleString()}`, 'Value']}
                                    contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
                                />
                                <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                                    {data.map((_, index) => (
                                        <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                                    ))}
                                </Bar>
                            </BarChart>
                        ) : (
                            <PieChart>
                                <Pie
                                    data={data}
                                    cx="50%"
                                    cy="50%"
                                    labelLine={false}
                                    label={({ name, percent }) => `${name}: ${(percent ? (percent * 100).toFixed(0) : 0)}%`}
                                    outerRadius={100}
                                    fill="#8884d8"
                                    dataKey="value"
                                >
                                    {data.map((_, index) => (
                                        <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip
                                    formatter={(value: number) => [`$${value.toLocaleString()}`, 'Value']}
                                    contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
                                />
                            </PieChart>
                        )}
                    </ResponsiveContainer>
                </div>
                {/* Legend */}
                <div className="flex flex-wrap gap-4 mt-4 justify-center">
                    {data.map((item, index) => (
                        <div key={item.stage} className="flex items-center gap-2">
                            <div
                                className="w-3 h-3 rounded-full"
                                style={{ backgroundColor: CHART_COLORS[index % CHART_COLORS.length] }}
                            />
                            <span className="text-xs text-gray-600">{item.stage} ({item.count})</span>
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
}

interface ActivityChartProps {
    data: {
        day: string;
        calls: number;
        emails: number;
        meetings: number;
        tasks: number;
    }[];
    className?: string;
}

export function ActivityChart({ data, className }: ActivityChartProps) {
    return (
        <Card className={className}>
            <CardHeader>
                <CardTitle>Activity Overview</CardTitle>
                <CardDescription>Daily activity breakdown</CardDescription>
            </CardHeader>
            <CardContent>
                <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                        <ComposedChart data={data}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                            <XAxis dataKey="day" tick={{ fontSize: 12 }} />
                            <YAxis tick={{ fontSize: 12 }} />
                            <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }} />
                            <Legend />
                            <Bar dataKey="calls" stackId="a" fill={COLORS.primary} name="Calls" />
                            <Bar dataKey="emails" stackId="a" fill={COLORS.secondary} name="Emails" />
                            <Bar dataKey="meetings" stackId="a" fill={COLORS.success} name="Meetings" />
                            <Line type="monotone" dataKey="tasks" stroke={COLORS.warning} name="Tasks" />
                        </ComposedChart>
                    </ResponsiveContainer>
                </div>
            </CardContent>
        </Card>
    );
}

interface LeaderboardProps {
    title: string;
    data: {
        id: string;
        name: string;
        value: number;
        avatar?: string;
        change?: number;
    }[];
    valueLabel?: string;
    valueFormatter?: (value: number) => string;
    className?: string;
}

export function Leaderboard({
    title,
    data,
    // valueLabel = 'Value',
    valueFormatter = (v) => v.toString(),
    className,
}: LeaderboardProps) {
    const maxValue = Math.max(...data.map(d => d.value));

    return (
        <Card className={className}>
            <CardHeader>
                <CardTitle>{title}</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    {data.map((item, index) => (
                        <div key={item.id} className="flex items-center gap-4">
                            <div className="flex items-center justify-center w-6 h-6 rounded-full bg-gray-100 text-sm font-medium">
                                {index + 1}
                            </div>
                            <div className="flex-1">
                                <div className="flex items-center justify-between mb-1">
                                    <span className="font-medium text-sm">{item.name}</span>
                                    <span className="text-sm text-gray-600">
                                        {valueFormatter(item.value)}
                                        {item.change !== undefined && (
                                            <span className={cn(
                                                'ml-2 text-xs',
                                                item.change >= 0 ? 'text-green-600' : 'text-red-600'
                                            )}>
                                                {item.change >= 0 ? '+' : ''}{item.change}%
                                            </span>
                                        )}
                                    </span>
                                </div>
                                <div className="w-full bg-gray-100 rounded-full h-2">
                                    <div
                                        className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                                        style={{ width: `${(item.value / maxValue) * 100}%` }}
                                    />
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
}

interface MetricsGridProps {
    metrics: {
        label: string;
        value: number;
        target?: number;
        format?: 'number' | 'currency' | 'percent';
    }[];
    className?: string;
}

export function MetricsGrid({ metrics, className }: MetricsGridProps) {
    const formatValue = (value: number, format?: string) => {
        switch (format) {
            case 'currency':
                return `$${value.toLocaleString()}`;
            case 'percent':
                return `${value}%`;
            default:
                return value.toLocaleString();
        }
    };

    return (
        <div className={cn('grid grid-cols-2 md:grid-cols-4 gap-4', className)}>
            {metrics.map((metric) => {
                const progress = metric.target
                    ? Math.min((metric.value / metric.target) * 100, 100)
                    : 100;

                return (
                    <Card key={metric.label} className="p-4">
                        <div className="space-y-2">
                            <p className="text-sm text-gray-500">{metric.label}</p>
                            <p className="text-xl font-bold">
                                {formatValue(metric.value, metric.format)}
                            </p>
                            {metric.target && (
                                <>
                                    <div className="w-full bg-gray-100 rounded-full h-1.5">
                                        <div
                                            className={cn(
                                                'h-1.5 rounded-full transition-all duration-300',
                                                progress >= 100 ? 'bg-green-500' : progress >= 75 ? 'bg-blue-500' : 'bg-amber-500'
                                            )}
                                            style={{ width: `${progress}%` }}
                                        />
                                    </div>
                                    <p className="text-xs text-gray-500">
                                        Target: {formatValue(metric.target, metric.format)}
                                    </p>
                                </>
                            )}
                        </div>
                    </Card>
                );
            })}
        </div>
    );
}

// Sample data generators for demo
export const sampleRevenueData = [
    { month: 'Jan', revenue: 65000, target: 60000, lastYear: 55000 },
    { month: 'Feb', revenue: 72000, target: 65000, lastYear: 58000 },
    { month: 'Mar', revenue: 85000, target: 70000, lastYear: 65000 },
    { month: 'Apr', revenue: 78000, target: 75000, lastYear: 70000 },
    { month: 'May', revenue: 92000, target: 80000, lastYear: 72000 },
    { month: 'Jun', revenue: 98000, target: 85000, lastYear: 78000 },
];

export const samplePipelineData = [
    { stage: 'Prospecting', count: 45, value: 125000 },
    { stage: 'Qualification', count: 32, value: 280000 },
    { stage: 'Proposal', count: 18, value: 420000 },
    { stage: 'Negotiation', count: 12, value: 380000 },
    { stage: 'Closed Won', count: 8, value: 520000 },
];

export const sampleActivityData = [
    { day: 'Mon', calls: 24, emails: 45, meetings: 8, tasks: 32 },
    { day: 'Tue', calls: 32, emails: 52, meetings: 12, tasks: 28 },
    { day: 'Wed', calls: 28, emails: 38, meetings: 6, tasks: 35 },
    { day: 'Thu', calls: 36, emails: 48, meetings: 10, tasks: 30 },
    { day: 'Fri', calls: 22, emails: 35, meetings: 4, tasks: 25 },
];

const dashboardAnalyticsComponents = {
    KPICard,
    RevenueChart,
    PipelineChart,
    ActivityChart,
    Leaderboard,
    MetricsGrid,
};

export default dashboardAnalyticsComponents;
