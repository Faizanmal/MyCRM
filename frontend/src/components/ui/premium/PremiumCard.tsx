'use client';

/**
 * PremiumCard Component
 * 
 * High-end card with gradient borders, glow effects,
 * and stunning hover animations.
 */

import React, { ReactNode } from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';
import { cn } from '@/lib/utils';

interface PremiumCardProps extends Omit<HTMLMotionProps<'div'>, 'children'> {
  children: ReactNode;
  className?: string;
  variant?: 'default' | 'gradient' | 'glow' | 'minimal';
  hover?: 'lift' | 'glow' | 'scale' | 'tilt' | 'none';
  padding?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  delay?: number;
}

const paddingClasses = {
  none: '',
  sm: 'p-4',
  md: 'p-5',
  lg: 'p-6',
  xl: 'p-8',
};

export function PremiumCard({
  children,
  className,
  variant = 'default',
  hover = 'lift',
  padding = 'lg',
  delay = 0,
  ...props
}: PremiumCardProps) {
  const hoverEffects = {
    lift: { y: -8, transition: { duration: 0.3 } },
    glow: { boxShadow: '0 0 40px rgba(99, 102, 241, 0.3)', transition: { duration: 0.3 } },
    scale: { scale: 1.02, transition: { duration: 0.3 } },
    tilt: { rotateX: 5, rotateY: -5, transition: { duration: 0.3 } },
    none: {},
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay, ease: [0.4, 0, 0.2, 1] }}
      whileHover={hoverEffects[hover]}
      style={hover === 'tilt' ? { transformStyle: 'preserve-3d', perspective: 1000 } : {}}
      className={cn(
        'premium-card',
        paddingClasses[padding],
        variant === 'gradient' && 'bg-linear-to-br from-card via-card to-primary/5',
        variant === 'glow' && 'glow-soft',
        className
      )}
      {...props}
    >
      {children}
    </motion.div>
  );
}

/**
 * StatCard - Premium card for displaying statistics
 */
interface StatCardProps {
  title: string;
  value: string | number;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
  icon?: ReactNode;
  iconColor?: string;
  loading?: boolean;
  delay?: number;
}

export function StatCard({
  title,
  value,
  change,
  changeType = 'neutral',
  icon,
  iconColor = 'from-primary-500 to-purple-500',
  loading = false,
  delay = 0,
}: StatCardProps) {
  const changeColors = {
    positive: 'text-emerald-500 bg-emerald-500/10',
    negative: 'text-red-500 bg-red-500/10',
    neutral: 'text-muted-foreground bg-muted',
  };

  if (loading) {
    return (
      <PremiumCard delay={delay} className="overflow-hidden">
        <div className="flex items-start justify-between">
          <div className="space-y-3 flex-1">
            <div className="skeleton h-4 w-24 rounded" />
            <div className="skeleton h-8 w-32 rounded" />
            <div className="skeleton h-4 w-16 rounded-full" />
          </div>
          <div className="skeleton h-12 w-12 rounded-xl" />
        </div>
      </PremiumCard>
    );
  }

  return (
    <PremiumCard delay={delay} hover="lift">
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <motion.p
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: delay + 0.2 }}
            className="text-3xl font-bold text-foreground"
          >
            {value}
          </motion.p>
          {change && (
            <motion.span
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: delay + 0.4 }}
              className={cn(
                'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium',
                changeColors[changeType]
              )}
            >
              {changeType === 'positive' && '↑'}
              {changeType === 'negative' && '↓'}
              {change}
            </motion.span>
          )}
        </div>
        {icon && (
          <motion.div
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4, delay: delay + 0.3, type: 'spring' }}
            className={cn(
              'p-3 rounded-xl bg-linear-to-br shadow-lg',
              iconColor
            )}
          >
            <div className="text-white">{icon}</div>
          </motion.div>
        )}
      </div>
    </PremiumCard>
  );
}

/**
 * FeatureCard - Card for displaying features with icons
 */
interface FeatureCardProps {
  title: string;
  description: string;
  icon: ReactNode;
  gradient?: string;
  delay?: number;
}

export function FeatureCard({
  title,
  description,
  icon,
  gradient = 'from-primary-500 to-purple-500',
  delay = 0,
}: FeatureCardProps) {
  return (
    <PremiumCard delay={delay} hover="lift" className="group">
      <motion.div
        whileHover={{ scale: 1.1, rotate: 5 }}
        className={cn(
          'inline-flex p-3 rounded-xl bg-linear-to-br mb-4',
          'transition-transform duration-300',
          gradient
        )}
      >
        <div className="text-white">{icon}</div>
      </motion.div>
      <h3 className="text-lg font-semibold text-foreground mb-2 group-hover:text-primary transition-colors">
        {title}
      </h3>
      <p className="text-muted-foreground text-sm leading-relaxed">
        {description}
      </p>
    </PremiumCard>
  );
}

/**
 * GradientBorderCard - Card with animated gradient border
 */
interface GradientBorderCardProps {
  children: ReactNode;
  className?: string;
  borderWidth?: number;
  animate?: boolean;
}

export function GradientBorderCard({
  children,
  className,
  borderWidth = 2,
  animate = true,
}: GradientBorderCardProps) {
  return (
    <div 
      className="relative rounded-2xl overflow-hidden group"
      style={{ padding: `${borderWidth}px` }}
    >
      {/* Animated gradient border */}
      <motion.div
        animate={animate ? {
          backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
        } : {}}
        transition={{
          duration: 5,
          repeat: Infinity,
          ease: 'linear',
        }}
        className="absolute inset-0 bg-linear-to-r from-primary-500 via-purple-500 to-pink-500 opacity-75 group-hover:opacity-100 transition-opacity"
        style={{ backgroundSize: '200% 200%' }}
      />
      
      {/* Card content */}
      <div className={cn(
        'relative bg-card rounded-2xl p-6',
        className
      )}>
        {children}
      </div>
    </div>
  );
}
