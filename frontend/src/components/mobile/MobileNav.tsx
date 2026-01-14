'use client';

/**
 * Mobile Navigation Component
 * Bottom navigation bar for mobile devices
 */

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  HomeIcon,
  UsersIcon,
  UserGroupIcon,
  CurrencyDollarIcon,
  ChatBubbleLeftRightIcon,
} from '@heroicons/react/24/outline';
import {
  HomeIcon as HomeIconSolid,
  UsersIcon as UsersIconSolid,
  UserGroupIcon as UserGroupIconSolid,
  CurrencyDollarIcon as CurrencyDollarIconSolid,
  ChatBubbleLeftRightIcon as ChatBubbleLeftRightIconSolid,
} from '@heroicons/react/24/solid';

const navItems = [
  {
    name: 'Home',
    href: '/dashboard',
    icon: HomeIcon,
    activeIcon: HomeIconSolid,
  },
  {
    name: 'Leads',
    href: '/leads',
    icon: UserGroupIcon,
    activeIcon: UserGroupIconSolid,
  },
  {
    name: 'Contacts',
    href: '/contacts',
    icon: UsersIcon,
    activeIcon: UsersIconSolid,
  },
  {
    name: 'Deals',
    href: '/opportunities',
    icon: CurrencyDollarIcon,
    activeIcon: CurrencyDollarIconSolid,
  },
  {
    name: 'Chat',
    href: '/communications',
    icon: ChatBubbleLeftRightIcon,
    activeIcon: ChatBubbleLeftRightIconSolid,
  },
];

export function MobileNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 md:hidden safe-area-bottom">
      <div className="flex justify-around items-center h-16">
        {navItems.map((item) => {
          const isActive = pathname.startsWith(item.href);
          const Icon = isActive ? item.activeIcon : item.icon;

          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex flex-col items-center justify-center flex-1 h-full transition-colors ${
                isActive
                  ? 'text-blue-600 dark:text-blue-400'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100'
              }`}
            >
              <Icon className="h-6 w-6" />
              <span className="text-xs mt-1 font-medium">{item.name}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}

// Floating Action Button for mobile
interface FABProps {
  onClick: () => void;
  icon?: React.ReactNode;
  label?: string;
  variant?: 'primary' | 'secondary';
}

export function FloatingActionButton({
  onClick,
  icon,
  label,
  variant = 'primary',
}: FABProps) {
  return (
    <button
      onClick={onClick}
      className={`fixed bottom-20 right-4 z-40 flex items-center justify-center rounded-full shadow-lg transition-transform active:scale-95 md:bottom-6 ${
        variant === 'primary'
          ? 'bg-blue-600 text-white hover:bg-blue-700'
          : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700'
      } ${label ? 'px-4 py-3 gap-2' : 'w-14 h-14'}`}
      aria-label={label || 'Action'}
    >
      {icon || (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
      )}
      {label && <span className="font-medium">{label}</span>}
    </button>
  );
}

// Pull to refresh component
interface PullToRefreshProps {
  onRefresh: () => Promise<void>;
  children: React.ReactNode;
}

export function PullToRefresh({ onRefresh, children }: PullToRefreshProps) {
  const [pulling, setPulling] = React.useState(false);
  const [refreshing, setRefreshing] = React.useState(false);
  const [pullDistance, setPullDistance] = React.useState(0);
  const startY = React.useRef(0);
  const containerRef = React.useRef<HTMLDivElement>(null);

  const THRESHOLD = 80;

  const handleTouchStart = (e: React.TouchEvent) => {
    if (containerRef.current?.scrollTop === 0) {
      startY.current = e.touches[0].clientY;
      setPulling(true);
    }
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!pulling) return;

    const currentY = e.touches[0].clientY;
    const distance = Math.min(currentY - startY.current, THRESHOLD * 1.5);

    if (distance > 0) {
      setPullDistance(distance);
    }
  };

  const handleTouchEnd = async () => {
    if (pullDistance >= THRESHOLD) {
      setRefreshing(true);
      setPullDistance(THRESHOLD);
      await onRefresh();
      setRefreshing(false);
    }

    setPulling(false);
    setPullDistance(0);
  };

  return (
    <div
      ref={containerRef}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      className="relative overflow-auto h-full"
    >
      {/* Pull indicator */}
      <div
        className={`absolute left-0 right-0 flex justify-center transition-transform ${
          pullDistance > 0 ? '' : 'hidden'
        }`}
        style={{ transform: `translateY(${pullDistance - 40}px)` }}
      >
        <div
          className={`w-8 h-8 rounded-full border-2 border-blue-600 border-t-transparent ${
            refreshing ? 'animate-spin' : ''
          }`}
          style={{
            transform: refreshing ? 'none' : `rotate(${pullDistance * 3}deg)`,
          }}
        />
      </div>

      {/* Content */}
      <div
        style={{
          transform: pullDistance > 0 ? `translateY(${pullDistance}px)` : 'none',
          transition: pulling ? 'none' : 'transform 0.2s',
        }}
      >
        {children}
      </div>
    </div>
  );
}

// Swipeable card component
interface SwipeableCardProps {
  children: React.ReactNode;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  leftAction?: React.ReactNode;
  rightAction?: React.ReactNode;
}

export function SwipeableCard({
  children,
  onSwipeLeft,
  onSwipeRight,
  leftAction,
  rightAction,
}: SwipeableCardProps) {
  const [offset, setOffset] = React.useState(0);
  const [swiping, setSwiping] = React.useState(false);
  const startX = React.useRef(0);

  const THRESHOLD = 100;

  const handleTouchStart = (e: React.TouchEvent) => {
    startX.current = e.touches[0].clientX;
    setSwiping(true);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!swiping) return;
    const currentX = e.touches[0].clientX;
    const newOffset = currentX - startX.current;
    setOffset(newOffset);
  };

  const handleTouchEnd = () => {
    if (offset > THRESHOLD && onSwipeRight) {
      onSwipeRight();
    } else if (offset < -THRESHOLD && onSwipeLeft) {
      onSwipeLeft();
    }

    setSwiping(false);
    setOffset(0);
  };

  return (
    <div className="relative overflow-hidden">
      {/* Background actions */}
      {leftAction && (
        <div
          className="absolute inset-y-0 left-0 flex items-center justify-start px-4 bg-green-500"
          style={{ width: Math.max(0, offset) }}
        >
          {leftAction}
        </div>
      )}
      {rightAction && (
        <div
          className="absolute inset-y-0 right-0 flex items-center justify-end px-4 bg-red-500"
          style={{ width: Math.max(0, -offset) }}
        >
          {rightAction}
        </div>
      )}

      {/* Main content */}
      <div
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        style={{
          transform: `translateX(${offset}px)`,
          transition: swiping ? 'none' : 'transform 0.2s',
        }}
        className="relative bg-white dark:bg-gray-800"
      >
        {children}
      </div>
    </div>
  );
}

// Mobile-optimized list item
interface MobileListItemProps {
  title: string;
  subtitle?: string;
  avatar?: React.ReactNode;
  badge?: React.ReactNode;
  onClick?: () => void;
  rightContent?: React.ReactNode;
}

export function MobileListItem({
  title,
  subtitle,
  avatar,
  badge,
  onClick,
  rightContent,
}: MobileListItemProps) {
  return (
    <div
      onClick={onClick}
      onKeyDown={onClick ? (e) => { if (e.key === 'Enter' || e.key === ' ') { onClick(); e.preventDefault(); } } : undefined}
      tabIndex={onClick ? 0 : -1}
      role={onClick ? 'button' : undefined}
      className={`flex items-center px-4 py-3 border-b border-gray-100 dark:border-gray-700 ${
        onClick ? 'active:bg-gray-50 dark:active:bg-gray-800 cursor-pointer' : ''
      }`}
    >
      {avatar && <div className="shrink-0 mr-3">{avatar}</div>}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
            {title}
          </p>
          {badge}
        </div>
        {subtitle && (
          <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
            {subtitle}
          </p>
        )}
      </div>
      {rightContent && <div className="shrink-0 ml-3">{rightContent}</div>}
    </div>
  );
}

