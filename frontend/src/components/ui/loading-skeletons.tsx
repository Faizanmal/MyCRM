'use client';

import { useMemo } from 'react';
import { Skeleton } from '@/components/ui/skeleton';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface SkeletonProps {
    className?: string;
}

/**
 * Page Loading Skeleton
 * Full page loading state with header, sidebar, and content area
 */
export function PageSkeleton({ className }: SkeletonProps) {
    return (
        <div className={cn('p-6 space-y-6', className)}>
            {/* Header skeleton */}
            <div className="flex items-center justify-between">
                <div className="space-y-2">
                    <Skeleton className="h-8 w-64" />
                    <Skeleton className="h-4 w-96" />
                </div>
                <div className="flex gap-3">
                    <Skeleton className="h-10 w-24" />
                    <Skeleton className="h-10 w-32" />
                </div>
            </div>

            {/* Stats cards skeleton */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {[...Array(4)].map((_, i) => (
                    <Card key={i}>
                        <CardContent className="pt-6">
                            <div className="flex items-center justify-between">
                                <div className="space-y-2">
                                    <Skeleton className="h-4 w-20" />
                                    <Skeleton className="h-6 w-16" />
                                </div>
                                <Skeleton className="h-8 w-8 rounded-full" />
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>

            {/* Content skeleton */}
            <Card>
                <CardHeader>
                    <Skeleton className="h-6 w-48" />
                    <Skeleton className="h-4 w-72" />
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        {[...Array(5)].map((_, i) => (
                            <div key={i} className="flex items-center gap-4">
                                <Skeleton className="h-12 w-12 rounded-full" />
                                <div className="flex-1 space-y-2">
                                    <Skeleton className="h-4 w-full max-w-md" />
                                    <Skeleton className="h-3 w-full max-w-sm" />
                                </div>
                                <Skeleton className="h-8 w-20" />
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}

/**
 * Table Loading Skeleton
 * Shows a loading state for data tables
 */
export function TableSkeleton({
    rows = 5,
    columns = 5,
    className
}: SkeletonProps & { rows?: number; columns?: number }) {
    return (
        <div className={cn('space-y-4', className)}>
            {/* Table header */}
            <div className="flex gap-4 pb-3 border-b">
                {[...Array(columns)].map((_, i) => (
                    <Skeleton key={i} className="h-4 flex-1" />
                ))}
            </div>

            {/* Table rows */}
            {[...Array(rows)].map((_, rowIndex) => (
                <div key={rowIndex} className="flex gap-4 py-3 border-b border-gray-100">
                    {[...Array(columns)].map((_, colIndex) => (
                        <Skeleton
                            key={colIndex}
                            className={cn(
                                'h-4 flex-1',
                                colIndex === 0 && 'max-w-[200px]'
                            )}
                        />
                    ))}
                </div>
            ))}
        </div>
    );
}

/**
 * Card Grid Loading Skeleton
 * Shows a grid of loading cards
 */
export function CardGridSkeleton({
    count = 6,
    className
}: SkeletonProps & { count?: number }) {
    return (
        <div className={cn('grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4', className)}>
            {[...Array(count)].map((_, i) => (
                <Card key={i}>
                    <CardContent className="pt-6">
                        <div className="space-y-4">
                            <div className="flex items-center gap-3">
                                <Skeleton className="h-12 w-12 rounded-full" />
                                <div className="flex-1 space-y-2">
                                    <Skeleton className="h-4 w-32" />
                                    <Skeleton className="h-3 w-24" />
                                </div>
                            </div>
                            <div className="space-y-2">
                                <Skeleton className="h-3 w-full" />
                                <Skeleton className="h-3 w-3/4" />
                            </div>
                            <div className="flex gap-2">
                                <Skeleton className="h-6 w-16 rounded-full" />
                                <Skeleton className="h-6 w-20 rounded-full" />
                            </div>
                        </div>
                    </CardContent>
                </Card>
            ))}
        </div>
    );
}

/**
 * Dashboard Widget Skeleton
 * Loading state for dashboard widgets
 */
export function WidgetSkeleton({ className }: SkeletonProps) {
    return (
        <Card className={className}>
            <CardHeader>
                <div className="flex items-center justify-between">
                    <Skeleton className="h-5 w-32" />
                    <Skeleton className="h-4 w-4" />
                </div>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    <Skeleton className="h-32 w-full" />
                    <div className="flex justify-between">
                        <Skeleton className="h-4 w-20" />
                        <Skeleton className="h-4 w-16" />
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}

/**
 * Form Loading Skeleton
 * Loading state for forms
 */
export function FormSkeleton({
    fields = 4,
    className
}: SkeletonProps & { fields?: number }) {
    return (
        <div className={cn('space-y-6', className)}>
            {[...Array(fields)].map((_, i) => (
                <div key={i} className="space-y-2">
                    <Skeleton className="h-4 w-24" />
                    <Skeleton className="h-10 w-full" />
                </div>
            ))}
            <div className="flex gap-3 pt-4">
                <Skeleton className="h-10 w-24" />
                <Skeleton className="h-10 w-20" />
            </div>
        </div>
    );
}

/**
 * Profile Loading Skeleton
 * Loading state for user profiles
 */
export function ProfileSkeleton({ className }: SkeletonProps) {
    return (
        <div className={cn('space-y-6', className)}>
            <div className="flex items-center gap-4">
                <Skeleton className="h-20 w-20 rounded-full" />
                <div className="space-y-2">
                    <Skeleton className="h-6 w-48" />
                    <Skeleton className="h-4 w-32" />
                    <Skeleton className="h-4 w-40" />
                </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
                {[...Array(4)].map((_, i) => (
                    <div key={i} className="space-y-2">
                        <Skeleton className="h-4 w-20" />
                        <Skeleton className="h-5 w-32" />
                    </div>
                ))}
            </div>
        </div>
    );
}

/**
 * Chart Loading Skeleton
 * Loading state for charts and graphs
 */
export function ChartSkeleton({ className }: SkeletonProps) {
    const barHeights = useMemo(() =>
        ['40%', '60%', '30%', '80%', '50%', '70%', '25%', '90%', '45%', '55%', '35%', '75%'],
        []
    );

    return (
        <Card className={className}>
            <CardHeader>
                <Skeleton className="h-5 w-40" />
                <Skeleton className="h-4 w-56" />
            </CardHeader>
            <CardContent>
                <div className="flex items-end justify-between h-48 gap-2">
                    {barHeights.map((height, i) => (
                        <Skeleton
                            key={i}
                            className="flex-1"
                            style={{ height }}
                        />
                    ))}
                </div>
                <div className="flex justify-between mt-4">
                    {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].map((month) => (
                        <span key={month} className="text-xs text-gray-400">{month}</span>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
}

/**
 * List Loading Skeleton
 * Simple list loading state
 */
export function ListSkeleton({
    items = 5,
    className
}: SkeletonProps & { items?: number }) {
    return (
        <div className={cn('space-y-3', className)}>
            {[...Array(items)].map((_, i) => (
                <div key={i} className="flex items-center gap-3 p-3 border rounded-lg">
                    <Skeleton className="h-10 w-10 rounded-lg" />
                    <div className="flex-1 space-y-1">
                        <Skeleton className="h-4 w-48" />
                        <Skeleton className="h-3 w-32" />
                    </div>
                    <Skeleton className="h-8 w-16" />
                </div>
            ))}
        </div>
    );
}

export default {
    PageSkeleton,
    TableSkeleton,
    CardGridSkeleton,
    WidgetSkeleton,
    FormSkeleton,
    ProfileSkeleton,
    ChartSkeleton,
    ListSkeleton,
};
