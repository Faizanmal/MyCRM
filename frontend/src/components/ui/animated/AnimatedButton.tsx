'use client';

/**
 * Animated Button Component
 * 
 * Enhanced button with ripple effects, hover animations, and loading states.
 */

import React, { ReactNode, ButtonHTMLAttributes, useState } from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface AnimatedButtonProps extends Omit<HTMLMotionProps<'button'>, 'children'> {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'success';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  ripple?: boolean;
  glow?: boolean;
  fullWidth?: boolean;
  icon?: ReactNode;
  iconPosition?: 'left' | 'right';
  disabled?: boolean;
}

export function AnimatedButton({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  ripple = true,
  glow = false,
  fullWidth = false,
  icon,
  iconPosition = 'left',
  disabled = false,
  className,
  onClick,
  ...props
}: AnimatedButtonProps) {
  const [ripples, setRipples] = useState<Array<{ x: number; y: number; id: number }>>([]);

  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (loading || disabled) return;

    // Create ripple effect
    if (ripple) {
      const button = e.currentTarget;
      const rect = button.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      const newRipple = { x, y, id: Date.now() };
      setRipples((prev) => [...prev, newRipple]);

      // Remove ripple after animation
      setTimeout(() => {
        setRipples((prev) => prev.filter((r) => r.id !== newRipple.id));
      }, 600);
    }

    onClick?.(e);
  };

  const baseClasses = cn(
    'relative overflow-hidden font-medium rounded-lg transition-all duration-300',
    'focus:outline-none focus:ring-2 focus:ring-offset-2',
    'disabled:opacity-50 disabled:cursor-not-allowed',
    {
      'w-full': fullWidth,
    }
  );

  const variantClasses = {
    primary: cn(
      'bg-gradient-primary text-white',
      'hover:shadow-glow-md focus:ring-primary-500',
      { 'shadow-glow-md': glow }
    ),
    secondary: cn(
      'bg-gradient-secondary text-white',
      'hover:shadow-lg focus:ring-secondary-500',
      { 'shadow-glow-md': glow }
    ),
    outline: cn(
      'border-2 border-primary-500 text-primary-600 dark:text-primary-400',
      'hover:bg-primary-50 dark:hover:bg-primary-950 focus:ring-primary-500'
    ),
    ghost: cn(
      'text-gray-700 dark:text-gray-300',
      'hover:bg-gray-100 dark:hover:bg-gray-800 focus:ring-gray-500'
    ),
    danger: cn(
      'bg-gradient-danger text-white',
      'hover:shadow-lg focus:ring-danger-500',
      { 'shadow-glow-md': glow }
    ),
    success: cn(
      'bg-gradient-success text-white',
      'hover:shadow-lg focus:ring-success-500',
      { 'shadow-glow-md': glow }
    ),
  };

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  const buttonClasses = cn(
    baseClasses,
    variantClasses[variant],
    sizeClasses[size],
    className
  );

  return (
    <motion.button
      whileHover={{ scale: disabled || loading ? 1 : 1.05 }}
      whileTap={{ scale: disabled || loading ? 1 : 0.95 }}
      transition={{ duration: 0.2 }}
      className={buttonClasses}
      onClick={handleClick}
      disabled={disabled || loading}
      {...props}
    >
      {/* Ripple effects */}
      {ripples.map((ripple) => (
        <span
          key={ripple.id}
          className="absolute bg-white/30 rounded-full animate-ping"
          style={{
            left: ripple.x,
            top: ripple.y,
            width: 10,
            height: 10,
            transform: 'translate(-50%, -50%)',
          }}
        />
      ))}

      {/* Button content */}
      <span className="relative flex items-center justify-center gap-2">
        {loading ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>Loading...</span>
          </>
        ) : (
          <>
            {icon && iconPosition === 'left' && <span>{icon}</span>}
            <span>{children}</span>
            {icon && iconPosition === 'right' && <span>{icon}</span>}
          </>
        )}
      </span>

      {/* Shine effect on hover */}
      <motion.div
        className="absolute inset-0 bg-white opacity-0"
        whileHover={{ opacity: 0.1 }}
        transition={{ duration: 0.3 }}
      />
    </motion.button>
  );
}

/**
 * Icon Button - Circular button with icon only
 */
interface IconButtonProps extends Omit<AnimatedButtonProps, 'children'> {
  icon: ReactNode;
  'aria-label': string;
}

export function IconButton({
  icon,
  variant = 'ghost',
  size = 'md',
  className,
  ...props
}: IconButtonProps) {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12',
  };

  return (
    <AnimatedButton
      variant={variant}
      size={size}
      className={cn('!p-0 rounded-full', sizeClasses[size], className)}
      {...props}
    >
      {icon}
    </AnimatedButton>
  );
}

/**
 * Floating Action Button
 */
interface FABProps extends Omit<AnimatedButtonProps, 'children'> {
  icon: ReactNode;
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
  'aria-label': string;
}

export function FAB({
  icon,
  position = 'bottom-right',
  className,
  ...props
}: FABProps) {
  const positionClasses = {
    'bottom-right': 'bottom-6 right-6',
    'bottom-left': 'bottom-6 left-6',
    'top-right': 'top-6 right-6',
    'top-left': 'top-6 left-6',
  };

  return (
    <motion.div
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      transition={{ type: 'spring', stiffness: 260, damping: 20 }}
      className={cn('fixed z-50', positionClasses[position])}
    >
      <AnimatedButton
        variant="primary"
        size="lg"
        glow
        className={cn('!p-0 w-14 h-14 rounded-full shadow-2xl', className)}
        {...props}
      >
        {icon}
      </AnimatedButton>
    </motion.div>
  );
}

/**
 * Button Group
 */
interface ButtonGroupProps {
  children: ReactNode;
  className?: string;
}

export function ButtonGroup({ children, className }: ButtonGroupProps) {
  return (
    <div className={cn('inline-flex rounded-lg shadow-sm', className)} role="group">
      {children}
    </div>
  );
}
