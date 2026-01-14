'use client';

/**
 * AnimatedCounter Component
 * 
 * Smooth number counter animation.
 */

import React, { useEffect, useRef, useState } from 'react';
import { motion, useSpring, useTransform, useInView } from 'framer-motion';

import { cn } from '@/lib/utils';

interface AnimatedCounterProps {
  value: number;
  delay?: number;
  prefix?: string;
  suffix?: string;
  decimals?: number;
  className?: string;
  format?: boolean;
}

export function AnimatedCounter({
  value,
  delay = 0,
  prefix = '',
  suffix = '',
  decimals = 0,
  className,
  format = true,
}: AnimatedCounterProps) {
  const ref = useRef<HTMLSpanElement>(null);
  const isInView = useInView(ref, { once: true });
  
  const spring = useSpring(0, {
    stiffness: 50,
    damping: 30,
  });

  const display = useTransform(spring, (current) => {
    const formatted = current.toFixed(decimals);
    if (format && decimals === 0) {
      return parseInt(formatted).toLocaleString();
    }
    return formatted;
  });

  useEffect(() => {
    if (isInView) {
      const timeout = setTimeout(() => {
        spring.set(value);
      }, delay * 1000);
      return () => clearTimeout(timeout);
    }
  }, [isInView, value, spring, delay]);

  return (
    <span ref={ref} className={cn('tabular-nums', className)}>
      {prefix}
      <motion.span>{display}</motion.span>
      {suffix}
    </span>
  );
}

/**
 * CountUp - Simple count up animation
 */
interface CountUpProps {
  end: number;
  start?: number;
  duration?: number;
  delay?: number;
  separator?: string;
  prefix?: string;
  suffix?: string;
  className?: string;
}

export function CountUp({
  end,
  start = 0,
  duration = 2000,
  delay = 0,
  separator = ',',
  prefix = '',
  suffix = '',
  className,
}: CountUpProps) {
  const [count, setCount] = useState(start);
  const ref = useRef<HTMLSpanElement>(null);
  const isInView = useInView(ref, { once: true });

  useEffect(() => {
    if (!isInView) return;

    const timeout = setTimeout(() => {
      let startTime: number | null = null;
      const step = (timestamp: number) => {
        if (!startTime) startTime = timestamp;
        const progress = Math.min((timestamp - startTime) / duration, 1);
        const easeProgress = 1 - Math.pow(1 - progress, 4); // easeOutQuart
        setCount(Math.floor(easeProgress * (end - start) + start));
        if (progress < 1) {
          window.requestAnimationFrame(step);
        }
      };
      window.requestAnimationFrame(step);
    }, delay);

    return () => clearTimeout(timeout);
  }, [isInView, end, start, duration, delay]);

  const formatNumber = (num: number) => {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, separator);
  };

  return (
    <span ref={ref} className={cn('tabular-nums', className)}>
      {prefix}{formatNumber(count)}{suffix}
    </span>
  );
}

/**
 * PercentageCircle - Animated circular progress
 */
interface PercentageCircleProps {
  percentage: number;
  size?: number;
  strokeWidth?: number;
  color?: string;
  bgColor?: string;
  showValue?: boolean;
  className?: string;
  delay?: number;
}

export function PercentageCircle({
  percentage,
  size = 120,
  strokeWidth = 8,
  color = 'url(#gradient)',
  bgColor = 'rgba(99, 102, 241, 0.1)',
  showValue = true,
  className,
  delay = 0,
}: PercentageCircleProps) {
  const ref = useRef<SVGSVGElement>(null);
  const isInView = useInView(ref, { once: true });
  
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (percentage / 100) * circumference;

  return (
    <div className={cn('relative inline-flex items-center justify-center', className)}>
      <svg
        ref={ref}
        width={size}
        height={size}
        className="transform -rotate-90"
      >
        <defs>
          <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#6366f1" />
            <stop offset="50%" stopColor="#a855f7" />
            <stop offset="100%" stopColor="#ec4899" />
          </linearGradient>
        </defs>

        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={bgColor}
          strokeWidth={strokeWidth}
          fill="none"
        />

        {/* Progress circle */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={strokeWidth}
          fill="none"
          strokeLinecap="round"
          initial={{ strokeDashoffset: circumference }}
          animate={isInView ? { strokeDashoffset: offset } : { strokeDashoffset: circumference }}
          transition={{ duration: 1.5, delay, ease: 'easeOut' }}
          style={{
            strokeDasharray: circumference,
          }}
        />
      </svg>

      {/* Value */}
      {showValue && (
        <div className="absolute inset-0 flex items-center justify-center">
          <AnimatedCounter
            value={percentage}
            suffix="%"
            className="text-2xl font-bold"
            delay={delay}
          />
        </div>
      )}
    </div>
  );
}

/**
 * ProgressBar - Animated horizontal progress bar
 */
interface ProgressBarProps {
  value: number;
  max?: number;
  height?: number;
  showValue?: boolean;
  className?: string;
  gradient?: boolean;
}

export function ProgressBar({
  value,
  max = 100,
  height = 8,
  showValue = false,
  className,
  gradient = true,
}: ProgressBarProps) {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true });
  const percentage = (value / max) * 100;

  return (
    <div className={cn('w-full', className)}>
      {showValue && (
        <div className="flex justify-between mb-2 text-sm">
          <span className="text-muted-foreground">Progress</span>
          <span className="font-medium">{Math.round(percentage)}%</span>
        </div>
      )}
      <div
        ref={ref}
        className="w-full overflow-hidden rounded-full bg-muted"
        style={{ height }}
      >
        <motion.div
          initial={{ width: 0 }}
          animate={isInView ? { width: `${percentage}%` } : { width: 0 }}
          transition={{ duration: 1, ease: 'easeOut' }}
          className={cn(
            'h-full rounded-full',
            gradient
              ? 'bg-linear-to-r from-primary-500 via-purple-500 to-pink-500'
              : 'bg-primary'
          )}
        />
      </div>
    </div>
  );
}

