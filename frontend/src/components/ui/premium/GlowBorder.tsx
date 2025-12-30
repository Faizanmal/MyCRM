'use client';

/**
 * GlowBorder Component
 * 
 * Adds animated glowing border effect to any element.
 */

import React, { ReactNode } from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface GlowBorderProps {
  children: ReactNode;
  className?: string;
  glowColor?: 'primary' | 'secondary' | 'accent' | 'success' | 'rainbow';
  intensity?: 'subtle' | 'medium' | 'strong';
  animated?: boolean;
  rounded?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full';
}

const glowColors = {
  primary: 'from-primary-400 via-purple-400 to-pink-400',
  secondary: 'from-blue-400 via-cyan-400 to-teal-400',
  accent: 'from-rose-400 via-pink-400 to-purple-400',
  success: 'from-emerald-400 via-green-400 to-teal-400',
  rainbow: 'from-red-400 via-yellow-400 via-green-400 via-blue-400 to-purple-400',
};

const intensityClasses = {
  subtle: 'opacity-40 blur-md',
  medium: 'opacity-60 blur-lg',
  strong: 'opacity-80 blur-xl',
};

const roundedClasses = {
  sm: 'rounded-sm',
  md: 'rounded-md',
  lg: 'rounded-lg',
  xl: 'rounded-xl',
  '2xl': 'rounded-2xl',
  full: 'rounded-full',
};

export function GlowBorder({
  children,
  className,
  glowColor = 'primary',
  intensity = 'medium',
  animated = true,
  rounded = 'xl',
}: GlowBorderProps) {
  return (
    <div className={cn('relative', className)}>
      {/* Glow Effect */}
      <motion.div
        animate={animated ? {
          backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
        } : {}}
        transition={{
          duration: 5,
          repeat: Infinity,
          ease: 'linear',
        }}
        className={cn(
          'absolute -inset-0.5 bg-linear-to-r',
          glowColors[glowColor],
          intensityClasses[intensity],
          roundedClasses[rounded],
        )}
        style={{ backgroundSize: '200% 200%' }}
      />
      
      {/* Content */}
      <div className={cn('relative', roundedClasses[rounded])}>
        {children}
      </div>
    </div>
  );
}

/**
 * GlowText - Text with glow effect
 */
interface GlowTextProps {
  children: ReactNode;
  className?: string;
  glowColor?: string;
}

export function GlowText({
  children,
  className,
  glowColor = 'rgba(99, 102, 241, 0.5)',
}: GlowTextProps) {
  return (
    <motion.span
      animate={{
        textShadow: [
          `0 0 10px ${glowColor}`,
          `0 0 20px ${glowColor}`,
          `0 0 10px ${glowColor}`,
        ],
      }}
      transition={{
        duration: 2,
        repeat: Infinity,
        ease: 'easeInOut',
      }}
      className={cn('gradient-text font-bold', className)}
    >
      {children}
    </motion.span>
  );
}

/**
 * PulsingDot - Animated pulsing indicator
 */
interface PulsingDotProps {
  color?: 'primary' | 'success' | 'warning' | 'danger';
  size?: 'sm' | 'md' | 'lg';
}

const dotColors = {
  primary: 'bg-primary-500',
  success: 'bg-emerald-500',
  warning: 'bg-amber-500',
  danger: 'bg-red-500',
};

const dotSizes = {
  sm: 'w-2 h-2',
  md: 'w-3 h-3',
  lg: 'w-4 h-4',
};

export function PulsingDot({ color = 'primary', size = 'md' }: PulsingDotProps) {
  return (
    <span className="relative inline-flex">
      <span className={cn('rounded-full', dotColors[color], dotSizes[size])} />
      <motion.span
        animate={{ scale: [1, 2], opacity: [0.5, 0] }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: 'easeOut',
        }}
        className={cn(
          'absolute inset-0 rounded-full',
          dotColors[color]
        )}
      />
    </span>
  );
}
