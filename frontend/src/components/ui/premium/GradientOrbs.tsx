'use client';

/**
 * GradientOrbs Component
 * 
 * Animated gradient orbs for beautiful background effects.
 */

import React from 'react';
import { motion } from 'framer-motion';

import { cn } from '@/lib/utils';

interface GradientOrbsProps {
  variant?: 'default' | 'subtle' | 'vibrant';
  className?: string;
}

export function GradientOrbs({ variant = 'default', className }: GradientOrbsProps) {
  const opacityMap = {
    default: 0.4,
    subtle: 0.2,
    vibrant: 0.6,
  };

  const orbs = [
    {
      color: 'bg-gradient-to-br from-primary-500 to-purple-600',
      size: 'w-[500px] h-[500px]',
      position: 'top-[-200px] right-[-150px]',
      delay: 0,
    },
    {
      color: 'bg-gradient-to-br from-purple-500 to-pink-600',
      size: 'w-[400px] h-[400px]',
      position: 'bottom-[-150px] left-[-100px]',
      delay: 2,
    },
    {
      color: 'bg-gradient-to-br from-blue-500 to-cyan-600',
      size: 'w-[300px] h-[300px]',
      position: 'top-[40%] left-[30%]',
      delay: 4,
    },
  ];

  return (
    <div className={cn('absolute inset-0 overflow-hidden pointer-events-none', className)}>
      {orbs.map((orb, index) => (
        <motion.div
          key={index}
          initial={{ opacity: 0 }}
          animate={{
            opacity: opacityMap[variant],
            y: [0, -30, 0],
            x: [0, 15, 0],
          }}
          transition={{
            opacity: { duration: 1 },
            y: {
              duration: 8,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: orb.delay,
            },
            x: {
              duration: 10,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: orb.delay,
            },
          }}
          className={cn(
            'absolute rounded-full blur-[80px]',
            orb.color,
            orb.size,
            orb.position
          )}
        />
      ))}
    </div>
  );
}

/**
 * AuroraBackground - Animated aurora effect
 */
interface AuroraBackgroundProps {
  className?: string;
  children?: React.ReactNode;
}

export function AuroraBackground({ className, children }: AuroraBackgroundProps) {
  return (
    <div className={cn('relative overflow-hidden', className)}>
      <div className="absolute inset-0">
        <motion.div
          animate={{
            rotate: [0, 360],
          }}
          transition={{
            duration: 30,
            repeat: Infinity,
            ease: 'linear',
          }}
          className="absolute inset-[-50%] opacity-30 dark:opacity-20"
          style={{
            background: `conic-gradient(from 0deg at 50% 50%, 
              transparent 0deg, 
              rgba(99, 102, 241, 0.3) 60deg, 
              transparent 120deg,
              rgba(168, 85, 247, 0.3) 180deg,
              transparent 240deg,
              rgba(59, 130, 246, 0.3) 300deg,
              transparent 360deg
            )`,
          }}
        />
      </div>
      <div className="relative z-10">{children}</div>
    </div>
  );
}

/**
 * MeshGradient - Static mesh gradient background
 */
interface MeshGradientProps {
  className?: string;
  children?: React.ReactNode;
}

export function MeshGradient({ className, children }: MeshGradientProps) {
  return (
    <div className={cn('relative', className)}>
      <div 
        className="absolute inset-0 opacity-50 dark:opacity-30"
        style={{
          background: `
            radial-gradient(at 27% 37%, hsla(215, 98%, 61%, 0.15) 0px, transparent 50%),
            radial-gradient(at 97% 21%, hsla(125, 98%, 72%, 0.1) 0px, transparent 50%),
            radial-gradient(at 52% 99%, hsla(354, 98%, 61%, 0.1) 0px, transparent 50%),
            radial-gradient(at 10% 29%, hsla(256, 96%, 67%, 0.15) 0px, transparent 50%),
            radial-gradient(at 97% 96%, hsla(38, 60%, 74%, 0.1) 0px, transparent 50%),
            radial-gradient(at 33% 50%, hsla(222, 67%, 73%, 0.1) 0px, transparent 50%),
            radial-gradient(at 79% 53%, hsla(343, 68%, 79%, 0.1) 0px, transparent 50%)
          `,
        }}
      />
      <div className="relative z-10">{children}</div>
    </div>
  );
}

/**
 * SpotlightBeam - Moving spotlight effect
 */
interface SpotlightBeamProps {
  className?: string;
}

export function SpotlightBeam({ className }: SpotlightBeamProps) {
  return (
    <motion.div
      animate={{
        x: ['-100%', '100%'],
        opacity: [0, 0.5, 0],
      }}
      transition={{
        duration: 5,
        repeat: Infinity,
        ease: 'easeInOut',
      }}
      className={cn(
        'absolute top-0 w-1/3 h-full',
        'bg-linear-to-r from-transparent via-primary-500/20 to-transparent',
        'transform skew-x-12',
        className
      )}
    />
  );
}

/**
 * GridPattern - Subtle grid background pattern
 */
interface GridPatternProps {
  className?: string;
}

export function GridPattern({ className }: GridPatternProps) {
  return (
    <div
      className={cn('absolute inset-0 opacity-[0.03] dark:opacity-[0.05]', className)}
      style={{
        backgroundImage: `
          linear-gradient(to right, currentColor 1px, transparent 1px),
          linear-gradient(to bottom, currentColor 1px, transparent 1px)
        `,
        backgroundSize: '50px 50px',
      }}
    />
  );
}

/**
 * DotPattern - Dot grid background pattern
 */
interface DotPatternProps {
  className?: string;
}

export function DotPattern({ className }: DotPatternProps) {
  return (
    <div
      className={cn('absolute inset-0 opacity-20 dark:opacity-10', className)}
      style={{
        backgroundImage: `radial-gradient(circle at 1px 1px, currentColor 1px, transparent 0)`,
        backgroundSize: '30px 30px',
      }}
    />
  );
}

