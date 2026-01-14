'use client';

/**
 * ModernInput Component
 * 
 * Beautifully styled input with glass effects,
 * animated focus states, and icon support.
 */

import React, { forwardRef, ReactNode, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertCircle, Check, Eye, EyeOff } from 'lucide-react';

import { cn } from '@/lib/utils';

interface ModernInputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'> {
  label?: string;
  error?: string;
  success?: boolean;
  hint?: string;
  icon?: ReactNode;
  iconPosition?: 'left' | 'right';
  variant?: 'default' | 'glass' | 'filled';
  inputSize?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
}

const variantClasses = {
  default: 'bg-background border-border focus:border-primary',
  glass: 'bg-white/5 dark:bg-white/5 backdrop-blur-md border-white/10 focus:border-primary/50',
  filled: 'bg-muted border-transparent focus:border-primary',
};

const sizeClasses = {
  sm: 'h-9 px-3 text-sm',
  md: 'h-11 px-4 text-base',
  lg: 'h-14 px-5 text-lg',
};

export const ModernInput = forwardRef<HTMLInputElement, ModernInputProps>(({
  label,
  error,
  success,
  hint,
  icon,
  iconPosition = 'left',
  variant = 'default',
  inputSize = 'md',
  fullWidth = true,
  className,
  type,
  placeholder,
  disabled,
  required,
  name,
  id,
  value,
  defaultValue,
  onChange,
  onBlur: onBlurProp,
  onFocus: onFocusProp,
}, ref) => {
  const [isFocused, setIsFocused] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const isPassword = type === 'password';
  const inputType = isPassword ? (showPassword ? 'text' : 'password') : type;

  const handleFocus = (e: React.FocusEvent<HTMLInputElement>) => {
    setIsFocused(true);
    onFocusProp?.(e);
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    setIsFocused(false);
    onBlurProp?.(e);
  };

  return (
    <div className={cn('relative', fullWidth && 'w-full')}>
      {/* Label */}
      {label && (
        <motion.label
          initial={false}
          animate={{
            color: error ? 'rgb(239, 68, 68)' : isFocused ? 'var(--primary)' : 'var(--muted-foreground)',
          }}
          className="block text-sm font-medium mb-2 transition-colors"
        >
          {label}
        </motion.label>
      )}

      {/* Input Container */}
      <div className="relative">
        {/* Left Icon */}
        {icon && iconPosition === 'left' && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
            {icon}
          </div>
        )}

        {/* Input */}
        <input
          ref={ref}
          type={inputType}
          name={name}
          id={id}
          placeholder={placeholder}
          disabled={disabled}
          required={required}
          value={value}
          defaultValue={defaultValue}
          onChange={onChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          className={cn(
            'w-full rounded-xl border transition-all duration-300',
            'placeholder:text-muted-foreground',
            'focus:outline-none focus:ring-2 focus:ring-primary/20',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            variantClasses[variant],
            sizeClasses[inputSize],
            icon && iconPosition === 'left' && 'pl-10',
            (icon && iconPosition === 'right') || isPassword ? 'pr-10' : '',
            error && 'border-destructive focus:border-destructive focus:ring-destructive/20',
            success && 'border-emerald-500 focus:border-emerald-500 focus:ring-emerald-500/20',
            className
          )}
        />

        {/* Right Icon or Password Toggle */}
        {isPassword ? (
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
          >
            {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
          </button>
        ) : icon && iconPosition === 'right' ? (
          <div className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground">
            {icon}
          </div>
        ) : null}

        {/* Success Icon */}
        {success && !error && (
          <motion.div
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-emerald-500"
          >
            <Check className="w-5 h-5" />
          </motion.div>
        )}

        {/* Focus Ring Animation */}
        <motion.div
          className="absolute inset-0 rounded-xl pointer-events-none"
          initial={false}
          animate={{
            boxShadow: isFocused && !error
              ? '0 0 0 3px rgba(99, 102, 241, 0.1), 0 0 20px rgba(99, 102, 241, 0.1)'
              : '0 0 0 0px transparent',
          }}
          transition={{ duration: 0.2 }}
        />
      </div>

      {/* Error or Hint */}
      <AnimatePresence mode="wait">
        {error ? (
          <motion.p
            key="error"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="flex items-center gap-1.5 mt-2 text-sm text-destructive"
          >
            <AlertCircle className="w-4 h-4" />
            {error}
          </motion.p>
        ) : hint ? (
          <motion.p
            key="hint"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-2 text-sm text-muted-foreground"
          >
            {hint}
          </motion.p>
        ) : null}
      </AnimatePresence>
    </div>
  );
});

ModernInput.displayName = 'ModernInput';

/**
 * ModernTextarea Component
 */
interface ModernTextareaProps {
  label?: string;
  error?: string;
  hint?: string;
  variant?: 'default' | 'glass' | 'filled';
  className?: string;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  name?: string;
  id?: string;
  value?: string;
  defaultValue?: string;
  rows?: number;
  onChange?: React.ChangeEventHandler<HTMLTextAreaElement>;
}

export const ModernTextarea = forwardRef<HTMLTextAreaElement, ModernTextareaProps>(({
  label,
  error,
  hint,
  variant = 'default',
  className,
  placeholder,
  disabled,
  required,
  name,
  id,
  value,
  defaultValue,
  rows,
  onChange,
}, ref) => {
  const [isFocused, setIsFocused] = useState(false);

  return (
    <div className="relative w-full">
      {label && (
        <motion.label
          initial={false}
          animate={{
            color: error ? 'rgb(239, 68, 68)' : isFocused ? 'var(--primary)' : 'var(--muted-foreground)',
          }}
          className="block text-sm font-medium mb-2 transition-colors"
        >
          {label}
        </motion.label>
      )}

      <textarea
        ref={ref}
        name={name}
        id={id}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        value={value}
        defaultValue={defaultValue}
        rows={rows}
        onChange={onChange}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        className={cn(
          'w-full min-h-[120px] px-4 py-3 rounded-xl border transition-all duration-300',
          'placeholder:text-muted-foreground resize-none',
          'focus:outline-none focus:ring-2 focus:ring-primary/20',
          variantClasses[variant],
          error && 'border-destructive focus:border-destructive',
          className
        )}
      />

      <AnimatePresence mode="wait">
        {error ? (
          <motion.p
            key="error"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="flex items-center gap-1.5 mt-2 text-sm text-destructive"
          >
            <AlertCircle className="w-4 h-4" />
            {error}
          </motion.p>
        ) : hint ? (
          <motion.p
            key="hint"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-2 text-sm text-muted-foreground"
          >
            {hint}
          </motion.p>
        ) : null}
      </AnimatePresence>
    </div>
  );
});

ModernTextarea.displayName = 'ModernTextarea';

