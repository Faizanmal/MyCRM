'use client';

/**
 * Mobile App Shell Layout
 * Provides the PWA shell structure with mobile navigation and offline support
 */

import React from 'react';
import { PlusIcon } from '@heroicons/react/24/outline';

import { MobileNav, FloatingActionButton } from '@/components/mobile/MobileNav';
import { PWAInstallPrompt, IOSInstallPrompt, OfflineIndicator, UpdatePrompt } from '@/components/mobile/PWAInstallPrompt';
import { useDevice, useOnlineStatus } from '@/hooks/useMobile';

interface MobileShellProps {
  children: React.ReactNode;
  showFAB?: boolean;
  onFABClick?: () => void;
  fabIcon?: React.ReactNode;
  fabLabel?: string;
}

export function MobileShell({
  children,
  showFAB = true,
  onFABClick,
  fabIcon,
  fabLabel,
}: MobileShellProps) {
  const device = useDevice();
  const { isOnline } = useOnlineStatus();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Offline indicator */}
      <OfflineIndicator />

      {/* Main content */}
      <main 
        className={`pb-20 md:pb-0 ${!isOnline ? 'pt-10' : ''}`}
        style={{
          // Account for notch on iOS
          paddingTop: device.isStandalone ? 'env(safe-area-inset-top)' : undefined,
        }}
      >
        {children}
      </main>

      {/* Mobile navigation */}
      {device.isMobile && <MobileNav />}

      {/* Floating action button */}
      {showFAB && onFABClick && (
        <FloatingActionButton
          onClick={onFABClick}
          icon={fabIcon || <PlusIcon className="w-6 h-6" />}
          label={fabLabel}
        />
      )}

      {/* PWA prompts */}
      <PWAInstallPrompt />
      <IOSInstallPrompt />
      <UpdatePrompt />
    </div>
  );
}

// Mobile header component
interface MobileHeaderProps {
  title: string;
  subtitle?: string;
  leftAction?: React.ReactNode;
  rightAction?: React.ReactNode;
  sticky?: boolean;
}

export function MobileHeader({
  title,
  subtitle,
  leftAction,
  rightAction,
  sticky = true,
}: MobileHeaderProps) {
  return (
    <header
      className={`bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 ${
        sticky ? 'sticky top-0 z-40' : ''
      }`}
    >
      <div className="flex items-center justify-between px-4 h-14">
        <div className="flex items-center gap-3">
          {leftAction && <div className="shrink-0">{leftAction}</div>}
          <div>
            <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
              {title}
            </h1>
            {subtitle && (
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {subtitle}
              </p>
            )}
          </div>
        </div>
        {rightAction && <div className="shrink-0">{rightAction}</div>}
      </div>
    </header>
  );
}

// Mobile search bar
interface MobileSearchBarProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  onFocus?: () => void;
  onBlur?: () => void;
}

export function MobileSearchBar({
  value,
  onChange,
  placeholder = 'Search...',
  onFocus,
  onBlur,
}: MobileSearchBarProps) {
  return (
    <div className="px-4 py-2 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
      <div className="relative">
        <svg
          className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
        <input
          type="search"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          onFocus={onFocus}
          onBlur={onBlur}
          className="w-full pl-10 pr-4 py-2 bg-gray-100 dark:bg-gray-800 border-0 rounded-lg text-sm text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:bg-white dark:focus:bg-gray-700"
        />
      </div>
    </div>
  );
}

// Bottom sheet component
interface BottomSheetProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  height?: 'auto' | 'half' | 'full';
}

export function BottomSheet({
  isOpen,
  onClose,
  title,
  children,
  height = 'auto',
}: BottomSheetProps) {
  const heightClasses = {
    auto: 'max-h-[90vh]',
    half: 'h-1/2',
    full: 'h-[90vh]',
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 z-50 transition-opacity"
        onClick={onClose}
        onKeyDown={(e) => { if (e.key === 'Escape') onClose(); }}
        tabIndex={0}
      />

      {/* Sheet */}
      <div
        className={`fixed bottom-0 left-0 right-0 z-50 bg-white dark:bg-gray-900 rounded-t-2xl shadow-xl ${heightClasses[height]} overflow-hidden animate-slide-up`}
      >
        {/* Handle */}
        <div className="flex justify-center py-2">
          <div className="w-10 h-1 bg-gray-300 dark:bg-gray-600 rounded-full" />
        </div>

        {/* Header */}
        {title && (
          <div className="px-4 pb-2 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              {title}
            </h2>
          </div>
        )}

        {/* Content */}
        <div className="overflow-auto p-4" style={{ maxHeight: 'calc(100% - 60px)' }}>
          {children}
        </div>
      </div>
    </>
  );
}

// Action sheet (mobile menu)
interface ActionSheetProps {
  isOpen: boolean;
  onClose: () => void;
  actions: {
    label: string;
    icon?: React.ReactNode;
    onClick: () => void;
    destructive?: boolean;
  }[];
}

export function ActionSheet({ isOpen, onClose, actions }: ActionSheetProps) {
  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 z-50"
        onClick={onClose}
        onKeyDown={(e) => { if (e.key === 'Escape') onClose(); }}
        tabIndex={0}
      />

      {/* Sheet */}
      <div className="fixed bottom-0 left-0 right-0 z-50 p-4 safe-area-bottom animate-slide-up">
        <div className="bg-white dark:bg-gray-800 rounded-2xl overflow-hidden">
          {actions.map((action, index) => (
            <button
              key={index}
              onClick={() => {
                action.onClick();
                onClose();
              }}
              className={`w-full flex items-center gap-3 px-4 py-3 text-left border-b border-gray-100 dark:border-gray-700 last:border-b-0 active:bg-gray-50 dark:active:bg-gray-700 ${
                action.destructive
                  ? 'text-red-600 dark:text-red-400'
                  : 'text-gray-900 dark:text-white'
              }`}
            >
              {action.icon && <span className="shrink-0">{action.icon}</span>}
              <span className="font-medium">{action.label}</span>
            </button>
          ))}
        </div>

        {/* Cancel button */}
        <button
          onClick={onClose}
          className="w-full mt-2 bg-white dark:bg-gray-800 rounded-2xl px-4 py-3 text-center font-semibold text-blue-600 dark:text-blue-400 active:bg-gray-50 dark:active:bg-gray-700"
        >
          Cancel
        </button>
      </div>
    </>
  );
}

// Skeleton loader for mobile
interface MobileSkeletonProps {
  type?: 'list' | 'card' | 'header';
  count?: number;
}

export function MobileSkeleton({ type = 'list', count = 3 }: MobileSkeletonProps) {
  const items = Array.from({ length: count });

  if (type === 'header') {
    return (
      <div className="px-4 py-3 animate-pulse">
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/4 mb-2" />
        <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-3/4" />
      </div>
    );
  }

  if (type === 'card') {
    return (
      <div className="p-4 space-y-4">
        {items.map((_, i) => (
          <div key={i} className="bg-white dark:bg-gray-800 rounded-xl p-4 animate-pulse">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded-full" />
              <div className="flex-1">
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-1" />
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/3" />
              </div>
            </div>
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-full mb-2" />
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-3/4" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="divide-y divide-gray-100 dark:divide-gray-700">
      {items.map((_, i) => (
        <div key={i} className="px-4 py-3 flex items-center gap-3 animate-pulse">
          <div className="w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded-full" />
          <div className="flex-1">
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-1" />
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-2/3" />
          </div>
          <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded" />
        </div>
      ))}
    </div>
  );
}

