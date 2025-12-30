'use client';

import { useState, useEffect, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
    TrendingUp,
    TrendingDown,
    BarChart3,
    PieChart,
    Calendar,
    ArrowUpRight,
    ArrowDownRight,
} from 'lucide-react';

// Types
interface DataPoint {
    label: string;
    value: number;
    color?: string;
}

interface LineDataPoint {
    date: string;
    value: number;
    secondaryValue?: number;
}

interface ChartProps {
    data: DataPoint[];
    height?: number;
    showLabels?: boolean;
    animated?: boolean;
}

interface LineChartProps {
    data: LineDataPoint[];
    height?: number;
    showSecondary?: boolean;
    primaryColor?: string;
    secondaryColor?: string;
}

// Utility functions
const getMaxValue = (data: DataPoint[]): number => {
    return Math.max(...data.map(d => d.value), 1);
};

const formatNumber = (value: number): string => {
    if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
    return value.toFixed(0);
};

// ==================== Bar Chart Component ====================

export function BarChart({ data, height = 200, showLabels = true, animated = true }: ChartProps) {
    const maxValue = getMaxValue(data);
    const barWidth = Math.min(60, (100 / data.length) - 2);

    return (
        <div className="w-full" style={{ height }}>
            <div className="flex items-end justify-around h-full gap-2">
                {data.map((item, index) => {
                    const barHeight = (item.value / maxValue) * 100;

                    return (
                        <div key={index} className="flex flex-col items-center flex-1">
                            <div
                                className="relative w-full flex items-end justify-center"
                                style={{ height: height - 30 }}
                            >
                                <motion.div
                                    initial={animated ? { height: 0 } : { height: `${barHeight}%` }}
                                    animate={{ height: `${barHeight}%` }}
                                    transition={{ delay: index * 0.1, duration: 0.5, ease: 'easeOut' }}
                                    className="rounded-t-md relative group cursor-pointer"
                                    style={{
                                        width: `${barWidth}%`,
                                        minWidth: 20,
                                        maxWidth: 60,
                                        backgroundColor: item.color || '#3b82f6',
                                    }}
                                >
                                    {/* Tooltip */}
                                    <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-gray-900 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                                        {formatNumber(item.value)}
                                    </div>

                                    {/* Gradient overlay */}
                                    <div className="absolute inset-0 bg-gradient-to-t from-white/0 to-white/20 rounded-t-md" />
                                </motion.div>
                            </div>

                            {showLabels && (
                                <span className="text-xs text-gray-500 mt-2 truncate max-w-[60px] text-center">
                                    {item.label}
                                </span>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

// ==================== Horizontal Bar Chart ====================

export function HorizontalBarChart({ data, height = 200 }: ChartProps) {
    const maxValue = getMaxValue(data);
    const barHeight = Math.min(40, height / data.length - 8);

    return (
        <div className="w-full space-y-3" style={{ minHeight: height }}>
            {data.map((item, index) => {
                const barWidth = (item.value / maxValue) * 100;

                return (
                    <div key={index} className="flex items-center gap-3">
                        <span className="text-sm text-gray-600 w-24 truncate">{item.label}</span>
                        <div className="flex-1 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden" style={{ height: barHeight }}>
                            <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${barWidth}%` }}
                                transition={{ delay: index * 0.1, duration: 0.5 }}
                                className="h-full rounded-full flex items-center justify-end pr-2"
                                style={{ backgroundColor: item.color || '#3b82f6' }}
                            >
                                <span className="text-xs text-white font-medium">
                                    {formatNumber(item.value)}
                                </span>
                            </motion.div>
                        </div>
                    </div>
                );
            })}
        </div>
    );
}

// ==================== Donut Chart Component ====================

export function DonutChart({ data, height = 200 }: ChartProps) {
    const total = data.reduce((sum, item) => sum + item.value, 0);
    const radius = 80;
    const strokeWidth = 30;
    const circumference = 2 * Math.PI * radius;

    let cumulativeOffset = 0;

    return (
        <div className="flex items-center justify-center gap-8" style={{ height }}>
            <div className="relative">
                <svg width={200} height={200} className="-rotate-90">
                    {data.map((item, index) => {
                        const percentage = item.value / total;
                        const strokeDasharray = circumference * percentage;
                        const strokeDashoffset = circumference * cumulativeOffset;
                        cumulativeOffset += percentage;

                        return (
                            <motion.circle
                                key={index}
                                cx={100}
                                cy={100}
                                r={radius}
                                fill="none"
                                stroke={item.color || `hsl(${index * 60}, 70%, 50%)`}
                                strokeWidth={strokeWidth}
                                strokeDasharray={`${strokeDasharray} ${circumference}`}
                                strokeDashoffset={-strokeDashoffset}
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                transition={{ delay: index * 0.2, duration: 0.5 }}
                                className="cursor-pointer hover:opacity-80 transition-opacity"
                            />
                        );
                    })}
                </svg>

                {/* Center text */}
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-2xl font-bold">{formatNumber(total)}</span>
                    <span className="text-xs text-gray-500">Total</span>
                </div>
            </div>

            {/* Legend */}
            <div className="space-y-2">
                {data.map((item, index) => (
                    <div key={index} className="flex items-center gap-2">
                        <div
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: item.color || `hsl(${index * 60}, 70%, 50%)` }}
                        />
                        <span className="text-sm text-gray-600">{item.label}</span>
                        <span className="text-sm font-medium">{((item.value / total) * 100).toFixed(1)}%</span>
                    </div>
                ))}
            </div>
        </div>
    );
}

// ==================== Line Chart Component ====================

export function LineChart({ data, height = 200, showSecondary = false, primaryColor = '#3b82f6', secondaryColor = '#22c55e' }: LineChartProps) {
    const maxValue = Math.max(...data.map(d => Math.max(d.value, d.secondaryValue || 0)), 1);
    const minValue = Math.min(...data.map(d => Math.min(d.value, d.secondaryValue || Infinity)), 0);
    const range = maxValue - minValue;

    const points = data.map((d, i) => ({
        x: (i / (data.length - 1)) * 100,
        y: 100 - ((d.value - minValue) / range) * 100,
        secondaryY: showSecondary && d.secondaryValue !== undefined
            ? 100 - ((d.secondaryValue - minValue) / range) * 100
            : undefined,
    }));

    const pathD = points.map((p, i) => (i === 0 ? `M ${p.x} ${p.y}` : `L ${p.x} ${p.y}`)).join(' ');
    const secondaryPathD = showSecondary
        ? points.filter(p => p.secondaryY !== undefined).map((p, i) => (i === 0 ? `M ${p.x} ${p.secondaryY}` : `L ${p.x} ${p.secondaryY}`)).join(' ')
        : '';

    return (
        <div className="w-full relative" style={{ height }}>
            <svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="none" className="overflow-visible">
                {/* Grid lines */}
                {[0, 25, 50, 75, 100].map(y => (
                    <line key={y} x1="0" y1={y} x2="100" y2={y} stroke="#e5e7eb" strokeWidth="0.2" />
                ))}

                {/* Area fill */}
                <motion.path
                    d={`${pathD} L 100 100 L 0 100 Z`}
                    fill={`${primaryColor}20`}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.5 }}
                />

                {/* Primary line */}
                <motion.path
                    d={pathD}
                    fill="none"
                    stroke={primaryColor}
                    strokeWidth="0.5"
                    strokeLinecap="round"
                    initial={{ pathLength: 0 }}
                    animate={{ pathLength: 1 }}
                    transition={{ duration: 1, ease: 'easeOut' }}
                />

                {/* Secondary line */}
                {showSecondary && secondaryPathD && (
                    <motion.path
                        d={secondaryPathD}
                        fill="none"
                        stroke={secondaryColor}
                        strokeWidth="0.5"
                        strokeLinecap="round"
                        strokeDasharray="2 1"
                        initial={{ pathLength: 0 }}
                        animate={{ pathLength: 1 }}
                        transition={{ duration: 1, delay: 0.2, ease: 'easeOut' }}
                    />
                )}

                {/* Data points */}
                {points.map((p, i) => (
                    <motion.circle
                        key={i}
                        cx={p.x}
                        cy={p.y}
                        r="1"
                        fill={primaryColor}
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ delay: i * 0.05 }}
                        className="cursor-pointer hover:r-[1.5]"
                    />
                ))}
            </svg>

            {/* X-axis labels */}
            <div className="absolute bottom-0 left-0 right-0 flex justify-between text-xs text-gray-500 transform translate-y-4">
                {data.filter((_, i) => i % Math.ceil(data.length / 6) === 0).map((d, i) => (
                    <span key={i}>{d.date}</span>
                ))}
            </div>
        </div>
    );
}

// ==================== Sparkline Component ====================

export function Sparkline({ data, color = '#3b82f6', height = 40 }: { data: number[]; color?: string; height?: number }) {
    const max = Math.max(...data, 1);
    const min = Math.min(...data, 0);
    const range = max - min || 1;

    const points = data.map((v, i) => ({
        x: (i / (data.length - 1)) * 100,
        y: 100 - ((v - min) / range) * 100,
    }));

    const pathD = points.map((p, i) => (i === 0 ? `M ${p.x} ${p.y}` : `L ${p.x} ${p.y}`)).join(' ');

    return (
        <svg width="100%" height={height} viewBox="0 0 100 100" preserveAspectRatio="none">
            <motion.path
                d={pathD}
                fill="none"
                stroke={color}
                strokeWidth="2"
                strokeLinecap="round"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: 0.8 }}
            />
        </svg>
    );
}

// ==================== Progress Ring Component ====================

export function ProgressRing({
    value,
    max = 100,
    size = 120,
    strokeWidth = 10,
    color = '#3b82f6',
    label,
    sublabel,
}: {
    value: number;
    max?: number;
    size?: number;
    strokeWidth?: number;
    color?: string;
    label?: string;
    sublabel?: string;
}) {
    const radius = (size - strokeWidth) / 2;
    const circumference = 2 * Math.PI * radius;
    const percentage = Math.min(value / max, 1);
    const strokeDashoffset = circumference * (1 - percentage);

    return (
        <div className="relative inline-flex items-center justify-center">
            <svg width={size} height={size} className="-rotate-90">
                {/* Background circle */}
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    fill="none"
                    stroke="#e5e7eb"
                    strokeWidth={strokeWidth}
                />

                {/* Progress circle */}
                <motion.circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    fill="none"
                    stroke={color}
                    strokeWidth={strokeWidth}
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    initial={{ strokeDashoffset: circumference }}
                    animate={{ strokeDashoffset }}
                    transition={{ duration: 1, ease: 'easeOut' }}
                />
            </svg>

            {/* Center content */}
            <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-xl font-bold">{label || `${(percentage * 100).toFixed(0)}%`}</span>
                {sublabel && <span className="text-xs text-gray-500">{sublabel}</span>}
            </div>
        </div>
    );
}

// ==================== Stat Card with Sparkline ====================

export function StatCardWithSparkline({
    title,
    value,
    change,
    changeLabel,
    sparklineData,
    color = '#3b82f6',
}: {
    title: string;
    value: string | number;
    change: number;
    changeLabel?: string;
    sparklineData: number[];
    color?: string;
}) {
    const isPositive = change >= 0;

    return (
        <Card>
            <CardContent className="p-4">
                <div className="flex justify-between items-start mb-2">
                    <span className="text-sm text-gray-500">{title}</span>
                    <Badge
                        variant="outline"
                        className={`gap-1 text-xs ${isPositive
                                ? 'text-green-600 border-green-200'
                                : 'text-red-600 border-red-200'
                            }`}
                    >
                        {isPositive ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                        {Math.abs(change).toFixed(1)}%
                    </Badge>
                </div>

                <div className="text-2xl font-bold mb-1">{value}</div>
                {changeLabel && <p className="text-xs text-gray-500 mb-3">{changeLabel}</p>}

                <Sparkline data={sparklineData} color={color} height={30} />
            </CardContent>
        </Card>
    );
}

// ==================== Funnel Chart ====================

export function FunnelChart({ data }: { data: DataPoint[] }) {
    const maxValue = data[0]?.value || 1;

    return (
        <div className="space-y-2">
            {data.map((item, index) => {
                const width = (item.value / maxValue) * 100;
                const conversionRate = index > 0 ? ((item.value / data[index - 1].value) * 100).toFixed(1) : '100';

                return (
                    <div key={index} className="flex items-center gap-3">
                        <div className="w-24 text-right">
                            <span className="text-sm font-medium">{item.label}</span>
                        </div>
                        <div className="flex-1 flex items-center">
                            <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${width}%` }}
                                transition={{ delay: index * 0.15, duration: 0.5 }}
                                className="h-10 rounded-r-full flex items-center justify-end pr-3"
                                style={{
                                    backgroundColor: item.color || `hsl(${220 - index * 20}, 70%, ${50 + index * 5}%)`,
                                    minWidth: 60,
                                }}
                            >
                                <span className="text-white text-sm font-medium">
                                    {formatNumber(item.value)}
                                </span>
                            </motion.div>
                            {index > 0 && (
                                <span className="ml-2 text-xs text-gray-500">
                                    {conversionRate}% conversion
                                </span>
                            )}
                        </div>
                    </div>
                );
            })}
        </div>
    );
}

// ==================== Heat Map ====================

export function HeatMap({
    data,
    rows,
    cols,
    cellSize = 30,
    colorScale = ['#dcfce7', '#22c55e', '#166534'],
}: {
    data: number[][];
    rows: string[];
    cols: string[];
    cellSize?: number;
    colorScale?: string[];
}) {
    const maxValue = Math.max(...data.flat(), 1);

    const getColor = (value: number): string => {
        const ratio = value / maxValue;
        if (ratio < 0.33) return colorScale[0];
        if (ratio < 0.66) return colorScale[1];
        return colorScale[2];
    };

    return (
        <div className="overflow-x-auto">
            <div className="inline-block">
                {/* Header row */}
                <div className="flex">
                    <div style={{ width: 80 }} />
                    {cols.map((col, i) => (
                        <div
                            key={i}
                            className="text-xs text-gray-500 text-center"
                            style={{ width: cellSize }}
                        >
                            {col}
                        </div>
                    ))}
                </div>

                {/* Data rows */}
                {data.map((row, rowIndex) => (
                    <div key={rowIndex} className="flex items-center">
                        <div className="text-xs text-gray-500 w-20 truncate">{rows[rowIndex]}</div>
                        {row.map((value, colIndex) => (
                            <motion.div
                                key={colIndex}
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                transition={{ delay: (rowIndex * cols.length + colIndex) * 0.02 }}
                                className="rounded-sm cursor-pointer hover:ring-2 hover:ring-blue-500"
                                style={{
                                    width: cellSize - 2,
                                    height: cellSize - 2,
                                    margin: 1,
                                    backgroundColor: getColor(value),
                                }}
                                title={`${rows[rowIndex]}, ${cols[colIndex]}: ${value}`}
                            />
                        ))}
                    </div>
                ))}
            </div>
        </div>
    );
}

// ==================== Demo/Example Usage ====================

export default function ChartsDemoPage() {
    const barData: DataPoint[] = [
        { label: 'Jan', value: 4500, color: '#3b82f6' },
        { label: 'Feb', value: 5200, color: '#3b82f6' },
        { label: 'Mar', value: 4800, color: '#3b82f6' },
        { label: 'Apr', value: 6100, color: '#22c55e' },
        { label: 'May', value: 5900, color: '#3b82f6' },
        { label: 'Jun', value: 7200, color: '#22c55e' },
    ];

    const donutData: DataPoint[] = [
        { label: 'Won', value: 45, color: '#22c55e' },
        { label: 'Lost', value: 23, color: '#ef4444' },
        { label: 'Open', value: 67, color: '#3b82f6' },
        { label: 'Stalled', value: 12, color: '#f59e0b' },
    ];

    const funnelData: DataPoint[] = [
        { label: 'Leads', value: 1000 },
        { label: 'Qualified', value: 650 },
        { label: 'Proposal', value: 320 },
        { label: 'Negotiation', value: 180 },
        { label: 'Won', value: 75 },
    ];

    const lineData: LineDataPoint[] = [
        { date: 'Week 1', value: 4200, secondaryValue: 3800 },
        { date: 'Week 2', value: 4800, secondaryValue: 4100 },
        { date: 'Week 3', value: 4500, secondaryValue: 4600 },
        { date: 'Week 4', value: 5200, secondaryValue: 4900 },
        { date: 'Week 5', value: 5800, secondaryValue: 5200 },
        { date: 'Week 6', value: 6100, secondaryValue: 5500 },
        { date: 'Week 7', value: 5900, secondaryValue: 5800 },
        { date: 'Week 8', value: 6500, secondaryValue: 6100 },
    ];

    const sparklineData = [23, 45, 32, 67, 54, 78, 65, 89, 76, 92];

    return (
        <div className="p-6 space-y-8">
            <h1 className="text-2xl font-bold">Dashboard Visualizations</h1>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCardWithSparkline
                    title="Revenue"
                    value="$125,430"
                    change={12.5}
                    changeLabel="vs last month"
                    sparklineData={sparklineData}
                    color="#22c55e"
                />
                <StatCardWithSparkline
                    title="Deals Won"
                    value="24"
                    change={8.3}
                    changeLabel="vs last month"
                    sparklineData={[5, 8, 6, 12, 9, 15, 11, 18]}
                    color="#3b82f6"
                />
                <StatCardWithSparkline
                    title="Conversion Rate"
                    value="24.5%"
                    change={-2.1}
                    changeLabel="vs last month"
                    sparklineData={[28, 26, 25, 24, 25, 24, 23, 24]}
                    color="#f59e0b"
                />
                <StatCardWithSparkline
                    title="Avg Deal Size"
                    value="$5,226"
                    change={15.2}
                    changeLabel="vs last month"
                    sparklineData={[4200, 4500, 4800, 5100, 4900, 5200, 5100, 5226]}
                    color="#8b5cf6"
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <BarChart3 className="w-5 h-5 text-blue-500" />
                            Monthly Revenue
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <BarChart data={barData} height={200} />
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <PieChart className="w-5 h-5 text-purple-500" />
                            Deal Status
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <DonutChart data={donutData} height={200} />
                    </CardContent>
                </Card>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Revenue Trend</CardTitle>
                    <CardDescription>This year vs Last year</CardDescription>
                </CardHeader>
                <CardContent>
                    <LineChart data={lineData} height={200} showSecondary primaryColor="#3b82f6" secondaryColor="#94a3b8" />
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>Sales Funnel</CardTitle>
                </CardHeader>
                <CardContent>
                    <FunnelChart data={funnelData} />
                </CardContent>
            </Card>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <Card className="flex flex-col items-center py-6">
                    <CardTitle className="mb-4">Quota Achievement</CardTitle>
                    <ProgressRing value={78} max={100} size={150} color="#22c55e" sublabel="of $100K" />
                </Card>

                <Card className="flex flex-col items-center py-6">
                    <CardTitle className="mb-4">Lead Response</CardTitle>
                    <ProgressRing value={92} max={100} size={150} color="#3b82f6" sublabel="< 24 hours" />
                </Card>

                <Card className="flex flex-col items-center py-6">
                    <CardTitle className="mb-4">Win Rate</CardTitle>
                    <ProgressRing value={24.5} max={100} size={150} color="#8b5cf6" label="24.5%" sublabel="this quarter" />
                </Card>
            </div>
        </div>
    );
}
