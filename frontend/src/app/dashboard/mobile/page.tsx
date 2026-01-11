'use client';

/**
 * Mobile Dashboard Page
 * Optimized dashboard view for mobile devices
 */

import React, { useState } from 'react';
import { useDevice } from '@/hooks/useMobile';
import { MobileShell, MobileHeader, MobileSearchBar } from '@/components/mobile';
import { 
  ChartBarIcon, 
  UserGroupIcon, 
  CurrencyDollarIcon,
  CheckCircleIcon,
  ClockIcon,
  ArrowTrendingUpIcon,
  PlusIcon,
} from '@heroicons/react/24/outline';
import Link from 'next/link';

// Quick stats component
function QuickStats() {
  const stats = [
    { label: 'Leads', value: '248', change: '+12%', icon: UserGroupIcon, color: 'blue' },
    { label: 'Deals', value: '$1.2M', change: '+8%', icon: CurrencyDollarIcon, color: 'green' },
    { label: 'Tasks', value: '18', change: '-3', icon: CheckCircleIcon, color: 'orange' },
    { label: 'Revenue', value: '$4.8M', change: '+15%', icon: ArrowTrendingUpIcon, color: 'purple' },
  ];

  return (
    <div className="grid grid-cols-2 gap-3 p-4">
      {stats.map((stat) => {
        const Icon = stat.icon;
        return (
          <div 
            key={stat.label}
            className="bg-white dark:bg-gray-800 rounded-2xl p-4 shadow-sm border border-gray-100 dark:border-gray-700"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
                {stat.label}
              </span>
              <Icon className={`w-4 h-4 text-${stat.color}-500`} />
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
              {stat.value}
            </div>
            <div className={`text-xs font-medium ${stat.change.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
              {stat.change}
            </div>
          </div>
        );
      })}
    </div>
  );
}

// Recent activity component
function RecentActivity() {
  const activities = [
    { id: 1, type: 'lead', title: 'New lead from website', time: '5m ago', icon: '👤' },
    { id: 2, type: 'deal', title: 'Deal moved to negotiation', time: '1h ago', icon: '💰' },
    { id: 3, type: 'task', title: 'Follow-up call completed', time: '2h ago', icon: '✅' },
    { id: 4, type: 'meeting', title: 'Demo scheduled', time: '3h ago', icon: '📅' },
  ];

  return (
    <div className="bg-white dark:bg-gray-800 mx-4 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-700">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
          Recent Activity
        </h3>
      </div>
      <div className="divide-y divide-gray-100 dark:divide-gray-700">
        {activities.map((activity) => (
          <div key={activity.id} className="px-4 py-3 active:bg-gray-50 dark:active:bg-gray-700">
            <div className="flex items-center gap-3">
              <span className="text-2xl">{activity.icon}</span>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {activity.title}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {activity.time}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
      <Link
        href="/activity"
        className="block px-4 py-3 text-center text-sm font-medium text-blue-600 dark:text-blue-400 border-t border-gray-100 dark:border-gray-700 active:bg-gray-50 dark:active:bg-gray-700"
      >
        View All Activity
      </Link>
    </div>
  );
}

// Quick actions component
function QuickActions() {
  const actions = [
    { label: 'Add Lead', icon: '👤', href: '/leads/new', color: 'blue' },
    { label: 'Create Deal', icon: '💼', href: '/opportunities/new', color: 'green' },
    { label: 'New Task', icon: '✅', href: '/tasks/new', color: 'orange' },
    { label: 'Schedule', icon: '📅', href: '/calendar', color: 'purple' },
  ];

  return (
    <div className="px-4 py-3">
      <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
        Quick Actions
      </h3>
      <div className="grid grid-cols-4 gap-3">
        {actions.map((action) => (
          <Link
            key={action.label}
            href={action.href}
            className="flex flex-col items-center gap-2 p-3 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 active:scale-95 transition-transform"
          >
            <span className="text-2xl">{action.icon}</span>
            <span className="text-xs font-medium text-gray-700 dark:text-gray-300 text-center">
              {action.label}
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}

// Tasks today component
function TasksToday() {
  const tasks = [
    { id: 1, title: 'Follow up with Acme Corp', time: '10:00 AM', priority: 'high' },
    { id: 2, title: 'Review proposal for TechStart', time: '2:00 PM', priority: 'medium' },
    { id: 3, title: 'Team sync meeting', time: '4:00 PM', priority: 'low' },
  ];

  return (
    <div className="bg-white dark:bg-gray-800 mx-4 mt-4 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
          Today&apos;s Tasks
        </h3>
        <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
          {tasks.length} tasks
        </span>
      </div>
      <div className="divide-y divide-gray-100 dark:divide-gray-700">
        {tasks.map((task) => (
          <div key={task.id} className="px-4 py-3 active:bg-gray-50 dark:active:bg-gray-700">
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {task.title}
                </p>
                <div className="flex items-center gap-2 mt-1">
                  <ClockIcon className="w-3 h-3 text-gray-400" />
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {task.time}
                  </p>
                  <span className={`px-1.5 py-0.5 text-xs font-medium rounded ${
                    task.priority === 'high' ? 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300' :
                    task.priority === 'medium' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300' :
                    'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
                  }`}>
                    {task.priority}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function MobileDashboard() {
  const [searchQuery, setSearchQuery] = useState('');
  const [showNewMenu, setShowNewMenu] = useState(false);
  const device = useDevice();

  // Show desktop version on larger screens
  if (!device.isMobile && !device.isTablet) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
        <p>This is the mobile-optimized dashboard. You&apos;re viewing from a desktop device.</p>
        <p className="mt-2">Visit from a mobile device or resize your browser to see the mobile version.</p>
      </div>
    );
  }

  return (
    <MobileShell
      showFAB={true}
      onFABClick={() => setShowNewMenu(true)}
      fabIcon={<PlusIcon className="w-6 h-6" />}
    >
      <MobileHeader
        title="Dashboard"
        subtitle="Welcome back!"
        rightAction={
          <button className="p-2 text-gray-600 dark:text-gray-400">
            <ChartBarIcon className="w-6 h-6" />
          </button>
        }
      />

      <MobileSearchBar
        value={searchQuery}
        onChange={setSearchQuery}
        placeholder="Search contacts, deals, tasks..."
      />

      <div className="pb-4">
        <QuickStats />
        <QuickActions />
        <RecentActivity />
        <TasksToday />
      </div>

      {/* Action menu modal */}
      {showNewMenu && (
        <>
          <div
            className="fixed inset-0 bg-black/50 z-50"
            onClick={() => setShowNewMenu(false)}
          />
          <div className="fixed bottom-0 left-0 right-0 z-50 p-4 safe-area-bottom animate-slide-up">
            <div className="bg-white dark:bg-gray-800 rounded-2xl overflow-hidden">
              <Link
                href="/leads/new"
                onClick={() => setShowNewMenu(false)}
                className="flex items-center gap-3 px-4 py-3 text-left border-b border-gray-100 dark:border-gray-700 active:bg-gray-50 dark:active:bg-gray-700"
              >
                <span className="text-2xl">👤</span>
                <span className="font-medium text-gray-900 dark:text-white">Add Lead</span>
              </Link>
              <Link
                href="/opportunities/new"
                onClick={() => setShowNewMenu(false)}
                className="flex items-center gap-3 px-4 py-3 text-left border-b border-gray-100 dark:border-gray-700 active:bg-gray-50 dark:active:bg-gray-700"
              >
                <span className="text-2xl">💼</span>
                <span className="font-medium text-gray-900 dark:text-white">Create Deal</span>
              </Link>
              <Link
                href="/tasks/new"
                onClick={() => setShowNewMenu(false)}
                className="flex items-center gap-3 px-4 py-3 text-left active:bg-gray-50 dark:active:bg-gray-700"
              >
                <span className="text-2xl">✅</span>
                <span className="font-medium text-gray-900 dark:text-white">New Task</span>
              </Link>
            </div>
            <button
              onClick={() => setShowNewMenu(false)}
              className="w-full mt-2 bg-white dark:bg-gray-800 rounded-2xl px-4 py-3 text-center font-semibold text-blue-600 dark:text-blue-400 active:bg-gray-50 dark:active:bg-gray-700"
            >
              Cancel
            </button>
          </div>
        </>
      )}
    </MobileShell>
  );
}
