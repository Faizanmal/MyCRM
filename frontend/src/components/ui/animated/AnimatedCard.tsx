'use client';

/**
 * Animated Card Component
 * 
 * A beautiful card component with hover effects, entrance animations,
 * and glassmorphism styling options.
 */

import React, { ReactNode } from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';

import { useScrollAnimation } from '@/hooks/useAnimations';
import { fadeInUp, cardHover } from '@/lib/animations';
import { cn } from '@/lib/utils';

interface AnimatedCardProps extends Omit<HTMLMotionProps<'div'>, 'children'> {
  children: ReactNode;
  delay?: number;
  hover?: boolean;
  glass?: boolean;
  glow?: boolean;
  className?: string;
  noBorder?: boolean;
}

export function AnimatedCard({ 
  children, 
  delay = 0,
  hover = true,
  glass = false,
  glow = false,
  className,
  noBorder = false,
  ...props 
}: AnimatedCardProps) {
  const { ref, inView } = useScrollAnimation();

  const cardClasses = cn(
    'rounded-xl p-6 transition-all duration-300',
    {
      // Glass morphism effect
      'bg-white/70 dark:bg-gray-900/70 backdrop-blur-md shadow-glass': glass,
      // Standard card
      'bg-white dark:bg-gray-900 shadow-card': !glass,
      // Border
      'border border-gray-200 dark:border-gray-800': !noBorder,
      // Glow effect
      'hover:shadow-glow-md': glow,
    },
    className
  );

  return (
    <motion.div
      ref={ref}
      initial="initial"
      animate={inView ? 'animate' : 'initial'}
      variants={fadeInUp}
      transition={{ delay }}
  whileHover={hover ? cardHover.hover : undefined}
      className={cardClasses}
      {...props}
    >
      {children}
    </motion.div>
  );
}

/**
 * Animated Card Header
 */
interface AnimatedCardHeaderProps {
  children: ReactNode;
  className?: string;
}

export function AnimatedCardHeader({ children, className }: AnimatedCardHeaderProps) {
  return (
    <div className={cn('mb-4', className)}>
      {children}
    </div>
  );
}

/**
 * Animated Card Title
 */
interface AnimatedCardTitleProps {
  children: ReactNode;
  className?: string;
}

export function AnimatedCardTitle({ children, className }: AnimatedCardTitleProps) {
  return (
    <h3 className={cn('text-lg font-semibold text-gray-900 dark:text-white', className)}>
      {children}
    </h3>
  );
}

/**
 * Animated Card Description
 */
interface AnimatedCardDescriptionProps {
  children: ReactNode;
  className?: string;
}

export function AnimatedCardDescription({ children, className }: AnimatedCardDescriptionProps) {
  return (
    <p className={cn('text-sm text-gray-500 dark:text-gray-400', className)}>
      {children}
    </p>
  );
}

/**
 * Animated Card Content
 */
interface AnimatedCardContentProps {
  children: ReactNode;
  className?: string;
}

export function AnimatedCardContent({ children, className }: AnimatedCardContentProps) {
  return (
    <div className={cn('', className)}>
      {children}
    </div>
  );
}

/**
 * Stat Card with animated counter
 */
interface StatCardProps {
  title: string;
  value: number | string;
  change?: number;
  icon?: ReactNode;
  delay?: number;
  prefix?: string;
  suffix?: string;
}

export function StatCard({ 
  title, 
  value, 
  change, 
  icon, 
  delay = 0,
  prefix = '',
  suffix = ''
}: StatCardProps) {
  const { ref, inView } = useScrollAnimation();
  
  const changeColor = change && change > 0 ? 'text-success-500' : 'text-danger-500';
  const changeIcon = change && change > 0 ? '↑' : '↓';

  return (
    <motion.div
      ref={ref}
      initial="initial"
      animate={inView ? 'animate' : 'initial'}
      variants={fadeInUp}
      transition={{ delay }}
      whileHover={cardHover.hover}
      className="bg-white dark:bg-gray-900 rounded-xl p-6 shadow-card border border-gray-200 dark:border-gray-800"
    >
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400">
          {title}
        </h4>
        {icon && (
          <div className="text-primary-500">
            {icon}
          </div>
        )}
      </div>
      
      <div className="space-y-2">
        <div className="text-3xl font-bold text-gray-900 dark:text-white">
          {prefix}{value}{suffix}
        </div>
        
        {change !== undefined && (
          <div className={cn('text-sm font-medium', changeColor)}>
            {changeIcon} {Math.abs(change)}% from last month
          </div>
        )}
      </div>
    </motion.div>
  );
}

/**
 * Feature Card with icon
 */
interface FeatureCardProps {
  icon: ReactNode;
  title: string;
  description: string;
  delay?: number;
}

export function FeatureCard({ icon, title, description, delay = 0 }: FeatureCardProps) {
  const { ref, inView } = useScrollAnimation();

  return (
    <motion.div
      ref={ref}
      initial="initial"
      animate={inView ? 'animate' : 'initial'}
      variants={fadeInUp}
      transition={{ delay }}
      whileHover={{ y: -8, boxShadow: '0 20px 40px rgba(0,0,0,0.12)' }}
      className="bg-white dark:bg-gray-900 rounded-xl p-6 shadow-card border border-gray-200 dark:border-gray-800 text-center"
    >
      <div className="inline-flex items-center justify-center w-12 h-12 mb-4 rounded-full bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-400">
        {icon}
      </div>
      
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
        {title}
      </h3>
      
      <p className="text-sm text-gray-500 dark:text-gray-400">
        {description}
      </p>
    </motion.div>
  );
}

