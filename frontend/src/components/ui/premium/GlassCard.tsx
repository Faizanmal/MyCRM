'use client';

/**
 * GlassCard Component
 * 
 * A beautiful glassmorphism card with blur effects, 
 * subtle borders, and smooth hover animations.
 */

import React, { ReactNode } from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';
import { cn } from '@/lib/utils';

interface GlassCardProps extends Omit<HTMLMotionProps<'div'>, 'children'> {
  children: ReactNode;
  className?: string;
  variant?: 'default' | 'subtle' | 'strong';
  hover?: boolean;
  glow?: boolean;
  padding?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  rounded?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full';
}

const paddingClasses = {
  none: '',
  sm: 'p-3',
  md: 'p-4',
  lg: 'p-6',
  xl: 'p-8',
};

const roundedClasses = {
  sm: 'rounded-sm',
  md: 'rounded-md',
  lg: 'rounded-lg',
  xl: 'rounded-xl',
  '2xl': 'rounded-2xl',
  full: 'rounded-full',
};

export function GlassCard({
  children,
  className,
  variant = 'default',
  hover = true,
  glow = false,
  padding = 'lg',
  rounded = 'xl',
  ...props
}: GlassCardProps) {
  const variantClasses = {
    default: 'glass-card',
    subtle: 'glass-subtle',
    strong: 'glass',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      whileHover={hover ? { 
        y: -4, 
        scale: 1.01,
        transition: { duration: 0.3 }
      } : undefined}
      className={cn(
        variantClasses[variant],
        paddingClasses[padding],
        roundedClasses[rounded],
        glow && 'glow-soft hover:glow-border',
        'transition-all duration-300',
        className
      )}
      {...props}
    >
      {children}
    </motion.div>
  );
}

/**
 * GlassCardHeader Component
 */
interface GlassCardHeaderProps {
  children: ReactNode;
  className?: string;
  icon?: ReactNode;
  action?: ReactNode;
}

export function GlassCardHeader({ 
  children, 
  className,
  icon,
  action 
}: GlassCardHeaderProps) {
  return (
    <div className={cn('flex items-center justify-between mb-4', className)}>
      <div className="flex items-center gap-3">
        {icon && (
          <div className="p-2 rounded-xl bg-gradient-to-br from-primary-500/10 to-purple-500/10 text-primary">
            {icon}
          </div>
        )}
        <div>{children}</div>
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}

/**
 * GlassCardTitle Component
 */
interface GlassCardTitleProps {
  children: ReactNode;
  className?: string;
  gradient?: boolean;
}

export function GlassCardTitle({ 
  children, 
  className,
  gradient = false 
}: GlassCardTitleProps) {
  return (
    <h3 className={cn(
      'text-lg font-semibold',
      gradient ? 'gradient-text' : 'text-foreground',
      className
    )}>
      {children}
    </h3>
  );
}

/**
 * GlassCardDescription Component
 */
interface GlassCardDescriptionProps {
  children: ReactNode;
  className?: string;
}

export function GlassCardDescription({ 
  children, 
  className 
}: GlassCardDescriptionProps) {
  return (
    <p className={cn('text-sm text-muted-foreground mt-1', className)}>
      {children}
    </p>
  );
}

/**
 * GlassCardContent Component
 */
interface GlassCardContentProps {
  children: ReactNode;
  className?: string;
}

export function GlassCardContent({ 
  children, 
  className 
}: GlassCardContentProps) {
  return (
    <div className={cn('', className)}>
      {children}
    </div>
  );
}

/**
 * GlassCardFooter Component
 */
interface GlassCardFooterProps {
  children: ReactNode;
  className?: string;
}

export function GlassCardFooter({ 
  children, 
  className 
}: GlassCardFooterProps) {
  return (
    <div className={cn(
      'flex items-center gap-3 mt-4 pt-4 border-t border-border/50',
      className
    )}>
      {children}
    </div>
  );
}
