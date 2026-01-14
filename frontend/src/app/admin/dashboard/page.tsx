'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
    TrendingUp,
    TrendingDown,
    Users,
    DollarSign,
    Target,
    Activity,
    BarChart3,
    PieChart,
    ArrowUpRight,
    ArrowDownRight,
    Download,
    RefreshCw,
    Clock,
    Star,
    Trophy,
    Zap,
    Percent,
} from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
// import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton';
import {
    BarChart,
    DonutChart,
    HorizontalBarChart,
    FunnelChart,
    HeatMap,
} from '@/components/charts/DashboardCharts';

// Types
interface TeamMember {
    id: string;
    name: string;
    avatar?: string;
    deals: number;
    revenue: number;
    activities: number;
    conversionRate: number;
    trend: number;
}

interface AnalyticsData {
    overview: {
        totalRevenue: number;
        revenueGrowth: number;
        totalDeals: number;
        dealsGrowth: number;
        conversionRate: number;
        conversionGrowth: number;
        activeLeads: number;
        leadsGrowth: number;
    };
    revenueByMonth: { label: string; value: number }[];
    dealsByStage: { label: string; value: number; color: string }[];
    teamPerformance: TeamMember[];
    funnelData: { label: string; value: number }[];
    activityByDay: number[][];
    topSources: { label: string; value: number; color: string }[];
    revenueByProduct: { label: string; value: number; color: string }[];
}

// Mock data generator
const generateMockData = (): AnalyticsData => ({
    overview: {
        totalRevenue: 1250750,
        revenueGrowth: 18.5,
        totalDeals: 234,
        dealsGrowth: 12.3,
        conversionRate: 24.5,
        conversionGrowth: 5.2,
        activeLeads: 1567,
        leadsGrowth: -3.8,
    },
    revenueByMonth: [
        { label: 'Jan', value: 85000 },
        { label: 'Feb', value: 92000 },
        { label: 'Mar', value: 78000 },
        { label: 'Apr', value: 105000 },
        { label: 'May', value: 118000 },
        { label: 'Jun', value: 145000 },
        { label: 'Jul', value: 132000 },
        { label: 'Aug', value: 156000 },
        { label: 'Sep', value: 143000 },
        { label: 'Oct', value: 178000 },
        { label: 'Nov', value: 165000 },
        { label: 'Dec', value: 152000 },
    ],
    dealsByStage: [
        { label: 'Prospecting', value: 145, color: '#3b82f6' },
        { label: 'Qualification', value: 98, color: '#8b5cf6' },
        { label: 'Proposal', value: 67, color: '#f59e0b' },
        { label: 'Negotiation', value: 45, color: '#22c55e' },
        { label: 'Closed Won', value: 234, color: '#10b981' },
        { label: 'Closed Lost', value: 89, color: '#ef4444' },
    ],
    teamPerformance: [
        { id: '1', name: 'Alex Chen', deals: 45, revenue: 256000, activities: 234, conversionRate: 32, trend: 15 },
        { id: '2', name: 'Sarah Johnson', deals: 38, revenue: 198000, activities: 189, conversionRate: 28, trend: 8 },
        { id: '3', name: 'Mike Wilson', deals: 35, revenue: 175000, activities: 210, conversionRate: 25, trend: -3 },
        { id: '4', name: 'Emily Davis', deals: 32, revenue: 165000, activities: 156, conversionRate: 27, trend: 12 },
        { id: '5', name: 'James Brown', deals: 28, revenue: 142000, activities: 178, conversionRate: 22, trend: -5 },
    ],
    funnelData: [
        { label: 'Website Visits', value: 10000 },
        { label: 'Leads Generated', value: 1500 },
        { label: 'MQLs', value: 450 },
        { label: 'SQLs', value: 180 },
        { label: 'Opportunities', value: 90 },
        { label: 'Customers', value: 35 },
    ],
    activityByDay: [
        [12, 15, 18, 14, 22, 8, 5],
        [14, 18, 22, 16, 25, 10, 6],
        [10, 12, 15, 11, 18, 6, 4],
        [18, 22, 25, 19, 28, 12, 8],
        [15, 19, 22, 17, 24, 9, 7],
    ],
    topSources: [
        { label: 'Organic Search', value: 35, color: '#3b82f6' },
        { label: 'Referral', value: 25, color: '#22c55e' },
        { label: 'LinkedIn', value: 20, color: '#0077b5' },
        { label: 'Paid Ads', value: 12, color: '#f59e0b' },
        { label: 'Events', value: 8, color: '#8b5cf6' },
    ],
    revenueByProduct: [
        { label: 'Enterprise', value: 450000, color: '#3b82f6' },
        { label: 'Professional', value: 380000, color: '#8b5cf6' },
        { label: 'Starter', value: 245000, color: '#22c55e' },
        { label: 'Add-ons', value: 175750, color: '#f59e0b' },
    ],
});

// Format utilities
const formatCurrency = (value: number): string => {
    if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `$${(value / 1000).toFixed(0)}K`;
    return `$${value.toFixed(0)}`;
};

const formatPercent = (value: number): string => `${value.toFixed(1)}%`;

export default function AdminDashboard() {
    const [data, setData] = useState<AnalyticsData | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [timeRange, setTimeRange] = useState('year');
    const [isRefreshing, setIsRefreshing] = useState(false);

    useEffect(() => {
        const loadData = async () => {
            setIsLoading(true);
            await new Promise(resolve => setTimeout(resolve, 800));
            setData(generateMockData());
            setIsLoading(false);
        };
        loadData();
    }, [timeRange]);

    const refresh = async () => {
        setIsRefreshing(true);
        await new Promise(resolve => setTimeout(resolve, 500));
        setData(generateMockData());
        setIsRefreshing(false);
    };

    if (isLoading || !data) {
        return (
            <div className="p-6 space-y-6">
                <div className="grid grid-cols-4 gap-4">
                    {[1, 2, 3, 4].map(i => (
                        <Skeleton key={i} className="h-32" />
                    ))}
                </div>
                <div className="grid grid-cols-2 gap-6">
                    <Skeleton className="h-80" />
                    <Skeleton className="h-80" />
                </div>
            </div>
        );
    }

    return (
        <div className="p-6 space-y-6 bg-gray-50 dark:bg-gray-900 min-h-screen">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Admin Dashboard</h1>
                    <p className="text-gray-500">Company-wide analytics and performance metrics</p>
                </div>

                <div className="flex items-center gap-3">
                    <Select value={timeRange} onValueChange={setTimeRange}>
                        <SelectTrigger className="w-40">
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="week">This Week</SelectItem>
                            <SelectItem value="month">This Month</SelectItem>
                            <SelectItem value="quarter">This Quarter</SelectItem>
                            <SelectItem value="year">This Year</SelectItem>
                        </SelectContent>
                    </Select>

                    <Button variant="outline" size="sm" onClick={refresh} disabled={isRefreshing}>
                        <RefreshCw className={`w-4 h-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
                        Refresh
                    </Button>

                    <Button variant="outline" size="sm">
                        <Download className="w-4 h-4 mr-2" />
                        Export
                    </Button>
                </div>
            </div>

            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0 }}>
                    <Card className="relative overflow-hidden">
                        <div className="absolute inset-0 bg-linear-to-br from-green-500/10 to-emerald-500/5" />
                        <CardContent className="p-6">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-sm text-gray-500">Total Revenue</span>
                                <DollarSign className="w-5 h-5 text-green-500" />
                            </div>
                            <div className="text-3xl font-bold">{formatCurrency(data.overview.totalRevenue)}</div>
                            <div className={`flex items-center gap-1 mt-2 text-sm ${data.overview.revenueGrowth >= 0 ? 'text-green-600' : 'text-red-600'
                                }`}>
                                {data.overview.revenueGrowth >= 0 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                                {Math.abs(data.overview.revenueGrowth)}% vs last period
                            </div>
                        </CardContent>
                    </Card>
                </motion.div>

                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
                    <Card className="relative overflow-hidden">
                        <div className="absolute inset-0 bg-linear-to-br from-blue-500/10 to-indigo-500/5" />
                        <CardContent className="p-6">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-sm text-gray-500">Deals Closed</span>
                                <Target className="w-5 h-5 text-blue-500" />
                            </div>
                            <div className="text-3xl font-bold">{data.overview.totalDeals}</div>
                            <div className={`flex items-center gap-1 mt-2 text-sm ${data.overview.dealsGrowth >= 0 ? 'text-green-600' : 'text-red-600'
                                }`}>
                                {data.overview.dealsGrowth >= 0 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                                {Math.abs(data.overview.dealsGrowth)}% vs last period
                            </div>
                        </CardContent>
                    </Card>
                </motion.div>

                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
                    <Card className="relative overflow-hidden">
                        <div className="absolute inset-0 bg-linear-to-br from-purple-500/10 to-pink-500/5" />
                        <CardContent className="p-6">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-sm text-gray-500">Conversion Rate</span>
                                <Percent className="w-5 h-5 text-purple-500" />
                            </div>
                            <div className="text-3xl font-bold">{formatPercent(data.overview.conversionRate)}</div>
                            <div className={`flex items-center gap-1 mt-2 text-sm ${data.overview.conversionGrowth >= 0 ? 'text-green-600' : 'text-red-600'
                                }`}>
                                {data.overview.conversionGrowth >= 0 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                                {Math.abs(data.overview.conversionGrowth)}% vs last period
                            </div>
                        </CardContent>
                    </Card>
                </motion.div>

                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
                    <Card className="relative overflow-hidden">
                        <div className="absolute inset-0 bg-linear-to-br from-amber-500/10 to-orange-500/5" />
                        <CardContent className="p-6">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-sm text-gray-500">Active Leads</span>
                                <Users className="w-5 h-5 text-amber-500" />
                            </div>
                            <div className="text-3xl font-bold">{data.overview.activeLeads.toLocaleString()}</div>
                            <div className={`flex items-center gap-1 mt-2 text-sm ${data.overview.leadsGrowth >= 0 ? 'text-green-600' : 'text-red-600'
                                }`}>
                                {data.overview.leadsGrowth >= 0 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                                {Math.abs(data.overview.leadsGrowth)}% vs last period
                            </div>
                        </CardContent>
                    </Card>
                </motion.div>
            </div>

            {/* Charts Row 1 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <BarChart3 className="w-5 h-5 text-blue-500" />
                            Revenue by Month
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <BarChart data={data.revenueByMonth} height={250} />
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <PieChart className="w-5 h-5 text-purple-500" />
                            Deals by Stage
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <DonutChart data={data.dealsByStage} height={250} />
                    </CardContent>
                </Card>
            </div>

            {/* Team Performance */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Trophy className="w-5 h-5 text-amber-500" />
                        Team Performance
                    </CardTitle>
                    <CardDescription>Individual sales rep metrics</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b">
                                    <th className="text-left py-3 px-4 font-medium text-gray-500">Rank</th>
                                    <th className="text-left py-3 px-4 font-medium text-gray-500">Name</th>
                                    <th className="text-right py-3 px-4 font-medium text-gray-500">Deals</th>
                                    <th className="text-right py-3 px-4 font-medium text-gray-500">Revenue</th>
                                    <th className="text-right py-3 px-4 font-medium text-gray-500">Activities</th>
                                    <th className="text-right py-3 px-4 font-medium text-gray-500">Conversion</th>
                                    <th className="text-right py-3 px-4 font-medium text-gray-500">Trend</th>
                                </tr>
                            </thead>
                            <tbody>
                                {data.teamPerformance.map((member, index) => (
                                    <motion.tr
                                        key={member.id}
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: index * 0.1 }}
                                        className="border-b hover:bg-gray-50 dark:hover:bg-gray-800"
                                    >
                                        <td className="py-4 px-4">
                                            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-white ${index === 0 ? 'bg-amber-500' :
                                                index === 1 ? 'bg-gray-400' :
                                                    index === 2 ? 'bg-orange-400' :
                                                        'bg-gray-300'
                                                }`}>
                                                {index + 1}
                                            </div>
                                        </td>
                                        <td className="py-4 px-4 font-medium">{member.name}</td>
                                        <td className="py-4 px-4 text-right">{member.deals}</td>
                                        <td className="py-4 px-4 text-right font-medium text-green-600">
                                            {formatCurrency(member.revenue)}
                                        </td>
                                        <td className="py-4 px-4 text-right">{member.activities}</td>
                                        <td className="py-4 px-4 text-right">{member.conversionRate}%</td>
                                        <td className="py-4 px-4 text-right">
                                            <Badge className={`gap-1 ${member.trend >= 0
                                                ? 'bg-green-100 text-green-700'
                                                : 'bg-red-100 text-red-700'
                                                }`}>
                                                {member.trend >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                                                {Math.abs(member.trend)}%
                                            </Badge>
                                        </td>
                                    </motion.tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </CardContent>
            </Card>

            {/* Charts Row 2 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                    <CardHeader>
                        <CardTitle>Sales Funnel</CardTitle>
                        <CardDescription>Lead to customer conversion</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <FunnelChart data={data.funnelData} />
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Revenue by Product</CardTitle>
                        <CardDescription>Top performing products</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <HorizontalBarChart data={data.revenueByProduct} height={200} />
                    </CardContent>
                </Card>
            </div>

            {/* Lead Sources & Activity Heatmap */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                    <CardHeader>
                        <CardTitle>Lead Sources</CardTitle>
                        <CardDescription>Where your leads come from</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <DonutChart data={data.topSources} height={200} />
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Activity className="w-5 h-5 text-green-500" />
                            Activity Heatmap
                        </CardTitle>
                        <CardDescription>Team activity by day and week</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <HeatMap
                            data={data.activityByDay}
                            rows={['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5']}
                            cols={['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']}
                            cellSize={35}
                        />
                    </CardContent>
                </Card>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
                {[
                    { label: 'Avg Deal Size', value: '$5,226', icon: DollarSign, color: 'text-green-500' },
                    { label: 'Win Rate', value: '24.5%', icon: Target, color: 'text-blue-500' },
                    { label: 'Sales Cycle', value: '32 days', icon: Clock, color: 'text-purple-500' },
                    { label: 'NPS Score', value: '72', icon: Star, color: 'text-amber-500' },
                    { label: 'Active Users', value: '45', icon: Users, color: 'text-indigo-500' },
                    { label: 'Pipeline Value', value: '$2.1M', icon: Zap, color: 'text-pink-500' },
                ].map((stat, index) => (
                    <motion.div
                        key={stat.label}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: index * 0.05 }}
                    >
                        <Card>
                            <CardContent className="p-4 text-center">
                                <stat.icon className={`w-6 h-6 mx-auto mb-2 ${stat.color}`} />
                                <div className="text-xl font-bold">{stat.value}</div>
                                <div className="text-xs text-gray-500">{stat.label}</div>
                            </CardContent>
                        </Card>
                    </motion.div>
                ))}
            </div>
        </div>
    );
}

