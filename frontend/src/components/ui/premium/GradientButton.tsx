'use client';

/**
 * GradientButton Component
 * 
 * Premium button with gradient backgrounds, shine effects,
 * and smooth hover animations.
 */

import React, { ReactNode, useState } from 'react';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface GradientButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'glass' | 'outline';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  loading?: boolean;
  icon?: ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
  glow?: boolean;
  shine?: boolean;
  rounded?: 'md' | 'lg' | 'xl' | 'full';
}

const variantClasses = {
  primary: 'bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white hover:from-indigo-600 hover:via-purple-600 hover:to-pink-600',
  secondary: 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white hover:from-blue-600 hover:to-cyan-600',
  success: 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white hover:from-emerald-600 hover:to-teal-600',
  danger: 'bg-gradient-to-r from-red-500 to-rose-500 text-white hover:from-red-600 hover:to-rose-600',
  warning: 'bg-gradient-to-r from-amber-500 to-orange-500 text-white hover:from-amber-600 hover:to-orange-600',
  glass: 'bg-white/10 dark:bg-white/5 backdrop-blur-md border border-white/20 text-foreground hover:bg-white/20',
  outline: 'bg-transparent border-2 border-primary text-primary hover:bg-primary hover:text-white',
};

const sizeClasses = {
  xs: 'px-2.5 py-1.5 text-xs',
  sm: 'px-3 py-2 text-sm',
  md: 'px-4 py-2.5 text-sm',
  lg: 'px-6 py-3 text-base',
  xl: 'px-8 py-4 text-lg',
};

const roundedClasses = {
  md: 'rounded-md',
  lg: 'rounded-lg',
  xl: 'rounded-xl',
  full: 'rounded-full',
};

export function GradientButton({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  icon,
  iconPosition = 'left',
  fullWidth = false,
  glow = false,
  shine = true,
  rounded = 'xl',
  className,
  disabled,
  onClick,
  type = 'button',
}: GradientButtonProps) {
  const [isPressed, setIsPressed] = useState(false);

  return (
    <motion.button
      whileHover={{ scale: disabled || loading ? 1 : 1.02 }}
      whileTap={{ scale: disabled || loading ? 1 : 0.98 }}
      onMouseDown={() => setIsPressed(true)}
      onMouseUp={() => setIsPressed(false)}
      onMouseLeave={() => setIsPressed(false)}
      onClick={onClick}
      type={type}
      className={cn(
        'relative inline-flex items-center justify-center gap-2 font-semibold',
        'transition-all duration-300 ease-out',
        'focus:outline-none focus:ring-2 focus:ring-primary/50 focus:ring-offset-2',
        'disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none',
        variantClasses[variant],
        sizeClasses[size],
        roundedClasses[rounded],
        fullWidth && 'w-full',
        glow && 'shadow-lg shadow-primary/25 hover:shadow-xl hover:shadow-primary/30',
        shine && 'overflow-hidden',
        className
      )}
      disabled={disabled || loading}
    >
      {/* Shine Effect */}
      {shine && !disabled && (
        <motion.div
          className="absolute inset-0 -translate-x-full"
          animate={isPressed ? {} : { x: ['100%', '-100%'] }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            repeatDelay: 3,
            ease: 'easeInOut',
          }}
        >
          <div className="w-1/2 h-full bg-linear-to-r from-transparent via-white/20 to-transparent skew-x-12" />
        </motion.div>
      )}

      {/* Content */}
      <span className="relative flex items-center gap-2">
        {loading && <Loader2 className="w-4 h-4 animate-spin" />}
        {!loading && icon && iconPosition === 'left' && icon}
        <span>{children}</span>
        {!loading && icon && iconPosition === 'right' && icon}
      </span>
    </motion.button>
  );
}

/**
 * IconButton - Circular gradient button for icons
 */
interface IconButtonProps {
  icon: ReactNode;
  variant?: 'primary' | 'secondary' | 'glass';
  size?: 'sm' | 'md' | 'lg';
  glow?: boolean;
  className?: string;
  onClick?: () => void;
  disabled?: boolean;
}

export function IconButton({
  icon,
  variant = 'primary',
  size = 'md',
  glow = false,
  className,
  onClick,
  disabled,
}: IconButtonProps) {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12',
  };

  return (
    <motion.button
      whileHover={{ scale: disabled ? 1 : 1.1 }}
      whileTap={{ scale: disabled ? 1 : 0.95 }}
      onClick={onClick}
      disabled={disabled}
      className={cn(
        'relative inline-flex items-center justify-center rounded-full',
        'transition-all duration-300',
        'focus:outline-none focus:ring-2 focus:ring-primary/50',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        variantClasses[variant],
        sizeClasses[size],
        glow && 'shadow-lg shadow-primary/25',
        className
      )}
    >
      {icon}
    </motion.button>
  );
}
