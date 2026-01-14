'use client';

/**
 * SkeletonLoader Components
 * 
 * Premium animated skeleton loading states.
 */

import React from 'react';
import { motion } from 'framer-motion';

import { cn } from '@/lib/utils';

interface SkeletonProps {
  className?: string;
  variant?: 'default' | 'shimmer' | 'pulse';
  rounded?: 'none' | 'sm' | 'md' | 'lg' | 'xl' | 'full';
}

const roundedClasses = {
  none: '',
  sm: 'rounded-sm',
  md: 'rounded-md',
  lg: 'rounded-lg',
  xl: 'rounded-xl',
  full: 'rounded-full',
};

export function Skeleton({ 
  className, 
  variant = 'shimmer',
  rounded = 'md' 
}: SkeletonProps) {
  const baseClasses = cn(
    'bg-muted relative overflow-hidden',
    roundedClasses[rounded],
    className
  );

  if (variant === 'pulse') {
    return (
      <motion.div
        className={baseClasses}
        animate={{ opacity: [1, 0.5, 1] }}
        transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
      />
    );
  }

  if (variant === 'shimmer') {
    return (
      <div className={baseClasses}>
        <motion.div
          className="absolute inset-0"
          style={{
            background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent)',
          }}
          animate={{ x: ['-100%', '100%'] }}
          transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
        />
      </div>
    );
  }

  return <div className={baseClasses} />;
}

/**
 * SkeletonText - Text placeholder
 */
interface SkeletonTextProps {
  lines?: number;
  className?: string;
  lastLineWidth?: string;
}

export function SkeletonText({ 
  lines = 3, 
  className,
  lastLineWidth = '60%' 
}: SkeletonTextProps) {
  return (
    <div className={cn('space-y-3', className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          className={cn(
            'h-4',
            i === lines - 1 ? `w-[${lastLineWidth}]` : 'w-full'
          )}
          rounded="sm"
        />
      ))}
    </div>
  );
}

/**
 * SkeletonCard - Card placeholder
 */
interface SkeletonCardProps {
  className?: string;
  hasImage?: boolean;
  hasFooter?: boolean;
}

export function SkeletonCard({ 
  className, 
  hasImage = false,
  hasFooter = false 
}: SkeletonCardProps) {
  return (
    <div className={cn('p-6 rounded-xl border border-border bg-card', className)}>
      {hasImage && (
        <Skeleton className="h-40 w-full mb-4" rounded="lg" />
      )}
      <div className="space-y-3">
        <Skeleton className="h-6 w-3/4" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-5/6" />
      </div>
      {hasFooter && (
        <div className="flex items-center gap-3 mt-4 pt-4 border-t border-border">
          <Skeleton className="h-8 w-8" rounded="full" />
          <Skeleton className="h-4 w-24" />
        </div>
      )}
    </div>
  );
}

/**
 * SkeletonAvatar - Avatar placeholder
 */
interface SkeletonAvatarProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const avatarSizes = {
  sm: 'h-8 w-8',
  md: 'h-10 w-10',
  lg: 'h-12 w-12',
  xl: 'h-16 w-16',
};

export function SkeletonAvatar({ size = 'md', className }: SkeletonAvatarProps) {
  return (
    <Skeleton 
      className={cn(avatarSizes[size], className)} 
      rounded="full" 
    />
  );
}

/**
 * SkeletonStatCard - Stat card placeholder
 */
export function SkeletonStatCard({ className }: { className?: string }) {
  return (
    <div className={cn('p-6 rounded-xl border border-border bg-card', className)}>
      <div className="flex items-start justify-between">
        <div className="space-y-3 flex-1">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-8 w-32" />
          <Skeleton className="h-5 w-16" rounded="full" />
        </div>
        <Skeleton className="h-12 w-12" rounded="xl" />
      </div>
    </div>
  );
}

/**
 * SkeletonTable - Table placeholder
 */
interface SkeletonTableProps {
  rows?: number;
  columns?: number;
  className?: string;
}

export function SkeletonTable({ 
  rows = 5, 
  columns = 4,
  className 
}: SkeletonTableProps) {
  return (
    <div className={cn('rounded-xl border border-border overflow-hidden', className)}>
      {/* Header */}
      <div className="flex items-center gap-4 p-4 bg-muted/50 border-b border-border">
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={i} className="h-4 flex-1" />
        ))}
      </div>
      
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div 
          key={rowIndex} 
          className="flex items-center gap-4 p-4 border-b border-border last:border-0"
        >
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton 
              key={colIndex} 
              className={cn(
                'h-4 flex-1',
                colIndex === 0 && 'w-40',
                colIndex === columns - 1 && 'w-20'
              )} 
            />
          ))}
        </div>
      ))}
    </div>
  );
}

/**
 * SkeletonList - List placeholder
 */
interface SkeletonListProps {
  items?: number;
  showAvatar?: boolean;
  className?: string;
}

export function SkeletonList({ 
  items = 5, 
  showAvatar = true,
  className 
}: SkeletonListProps) {
  return (
    <div className={cn('space-y-4', className)}>
      {Array.from({ length: items }).map((_, i) => (
        <div key={i} className="flex items-center gap-4">
          {showAvatar && <SkeletonAvatar />}
          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-3 w-1/2" />
          </div>
        </div>
      ))}
    </div>
  );
}

/**
 * SkeletonChart - Chart placeholder
 */
export function SkeletonChart({ className }: { className?: string }) {
  // Pre-compute heights to avoid Math.random in render
  const barHeights = [65, 40, 78, 52, 85, 45, 70, 58, 92, 48, 75, 55];

  return (
    <div className={cn('p-6 rounded-xl border border-border bg-card', className)}>
      <div className="flex items-center justify-between mb-4">
        <Skeleton className="h-6 w-32" />
        <Skeleton className="h-8 w-24" rounded="lg" />
      </div>
      <div className="flex items-end justify-between gap-2 h-48">
        {barHeights.map((height, i) => (
          <div 
            key={i} 
            className="flex-1"
            style={{ height: `${height}%` }}
          >
            <Skeleton className="w-full h-full" rounded="sm" />
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * PageSkeleton - Full page loading skeleton
 */
export function PageSkeleton() {
  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-4 w-64" />
        </div>
        <Skeleton className="h-10 w-32" rounded="lg" />
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <SkeletonStatCard key={i} />
        ))}
      </div>

      {/* Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <SkeletonChart />
        </div>
        <SkeletonCard hasFooter />
      </div>
    </div>
  );
}

