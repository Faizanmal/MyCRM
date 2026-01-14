'use client';

import { useState } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Home,
    Users,
    Target,
    CheckSquare,
    Bell,
    Menu,
    Plus,
    Settings,
    BarChart3,
    Mail,
    Calendar,
    User,
} from 'lucide-react';

import { cn } from '@/lib/utils';

// Types
interface NavItem {
    href: string;
    icon: React.ElementType;
    label: string;
    badge?: number;
}

interface QuickAction {
    id: string;
    icon: React.ElementType;
    label: string;
    color: string;
    onClick: () => void;
}

// Main navigation items
const mainNavItems: NavItem[] = [
    { href: '/dashboard', icon: Home, label: 'Home' },
    { href: '/contacts', icon: Users, label: 'Contacts' },
    { href: '/deals', icon: Target, label: 'Deals' },
    { href: '/tasks', icon: CheckSquare, label: 'Tasks' },
];

// Quick actions for the FAB menu
const defaultQuickActions: QuickAction[] = [
    { id: 'contact', icon: Users, label: 'New Contact', color: 'bg-blue-500', onClick: () => { /* TODO: implement new contact */ } },
    { id: 'deal', icon: Target, label: 'New Deal', color: 'bg-green-500', onClick: () => { /* TODO: implement new deal */ } },
    { id: 'task', icon: CheckSquare, label: 'New Task', color: 'bg-purple-500', onClick: () => { /* TODO: implement new task */ } },
    { id: 'email', icon: Mail, label: 'Send Email', color: 'bg-orange-500', onClick: () => { /* TODO: implement send email */ } },
];

// More menu items
const moreMenuItems: NavItem[] = [
    { href: '/analytics', icon: BarChart3, label: 'Analytics' },
    { href: '/calendar', icon: Calendar, label: 'Calendar' },
    { href: '/notifications', icon: Bell, label: 'Notifications', badge: 5 },
    { href: '/settings', icon: Settings, label: 'Settings' },
    { href: '/profile', icon: User, label: 'Profile' },
];

export default function MobileBottomNav() {
    const pathname = usePathname();
    const [showFAB, setShowFAB] = useState(false);
    const [showMoreMenu, setShowMoreMenu] = useState(false);
    const [notificationCount] = useState(5);

    return (
        <>
            {/* FAB Menu Overlay */}
            <AnimatePresence>
                {showFAB && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={() => setShowFAB(false)}
                        className="fixed inset-0 bg-black/50 z-40 md:hidden"
                    />
                )}
            </AnimatePresence>

            {/* FAB Quick Actions */}
            <AnimatePresence>
                {showFAB && (
                    <div className="fixed bottom-24 left-1/2 -translate-x-1/2 z-50 md:hidden">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.8, y: 20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.8, y: 20 }}
                            className="flex flex-col items-center gap-3"
                        >
                            {defaultQuickActions.map((action, index) => (
                                <motion.button
                                    key={action.id}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: 20 }}
                                    transition={{ delay: index * 0.05 }}
                                    onClick={() => {
                                        action.onClick();
                                        setShowFAB(false);
                                    }}
                                    className="flex items-center gap-3 bg-white dark:bg-gray-800 rounded-full pl-4 pr-6 py-3 shadow-lg"
                                >
                                    <div className={cn(
                                        'w-10 h-10 rounded-full flex items-center justify-center text-white',
                                        action.color
                                    )}>
                                        <action.icon className="w-5 h-5" />
                                    </div>
                                    <span className="font-medium">{action.label}</span>
                                </motion.button>
                            ))}
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>

            {/* More Menu Overlay */}
            <AnimatePresence>
                {showMoreMenu && (
                    <>
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={() => setShowMoreMenu(false)}
                            className="fixed inset-0 bg-black/50 z-40 md:hidden"
                        />

                        <motion.div
                            initial={{ y: '100%' }}
                            animate={{ y: 0 }}
                            exit={{ y: '100%' }}
                            transition={{ type: 'spring', damping: 25 }}
                            className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-900 rounded-t-2xl z-50 md:hidden shadow-xl"
                        >
                            {/* Handle */}
                            <div className="flex justify-center pt-3 pb-2">
                                <div className="w-10 h-1 bg-gray-300 dark:bg-gray-700 rounded-full" />
                            </div>

                            {/* Menu Items */}
                            <div className="p-4 grid grid-cols-3 gap-4">
                                {moreMenuItems.map((item) => (
                                    <Link
                                        key={item.href}
                                        href={item.href}
                                        onClick={() => setShowMoreMenu(false)}
                                        className={cn(
                                            'flex flex-col items-center gap-2 p-4 rounded-xl transition-colors',
                                            'hover:bg-gray-100 dark:hover:bg-gray-800',
                                            pathname === item.href && 'bg-blue-50 dark:bg-blue-900/20'
                                        )}
                                    >
                                        <div className="relative">
                                            <item.icon className={cn(
                                                'w-6 h-6',
                                                pathname === item.href
                                                    ? 'text-blue-500'
                                                    : 'text-gray-500'
                                            )} />
                                            {item.badge && item.badge > 0 && (
                                                <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                                                    {item.badge > 9 ? '9+' : item.badge}
                                                </span>
                                            )}
                                        </div>
                                        <span className={cn(
                                            'text-xs font-medium',
                                            pathname === item.href
                                                ? 'text-blue-500'
                                                : 'text-gray-600 dark:text-gray-400'
                                        )}>
                                            {item.label}
                                        </span>
                                    </Link>
                                ))}
                            </div>

                            {/* Close button */}
                            <div className="p-4 pt-0">
                                <button
                                    onClick={() => setShowMoreMenu(false)}
                                    className="w-full py-3 bg-gray-100 dark:bg-gray-800 rounded-xl font-medium text-gray-600 dark:text-gray-400"
                                >
                                    Cancel
                                </button>
                            </div>

                            {/* Safe area padding */}
                            <div className="h-safe-area-inset-bottom" />
                        </motion.div>
                    </>
                )}
            </AnimatePresence>

            {/* Bottom Navigation Bar */}
            <nav className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-900 border-t dark:border-gray-800 z-30 md:hidden">
                <div className="flex items-center justify-around h-16 px-2">
                    {/* Main Nav Items */}
                    {mainNavItems.map((item) => (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                'flex flex-col items-center justify-center w-14 h-14 rounded-xl transition-colors',
                                pathname === item.href || pathname.startsWith(`${item.href  }/`)
                                    ? 'text-blue-500'
                                    : 'text-gray-500'
                            )}
                        >
                            <item.icon className="w-5 h-5" />
                            <span className="text-[10px] mt-1 font-medium">{item.label}</span>
                        </Link>
                    ))}

                    {/* Center FAB Button */}
                    <button
                        onClick={() => setShowFAB(!showFAB)}
                        className={cn(
                            'relative flex items-center justify-center w-14 h-14 -mt-6 rounded-full shadow-lg transition-colors',
                            showFAB
                                ? 'bg-gray-800 dark:bg-gray-200 rotate-45'
                                : 'bg-blue-500'
                        )}
                    >
                        <Plus className={cn(
                            'w-6 h-6 transition-transform',
                            showFAB ? 'text-white dark:text-gray-900' : 'text-white'
                        )} />
                    </button>

                    {/* Notifications & More */}
                    <Link
                        href="/notifications"
                        className={cn(
                            'relative flex flex-col items-center justify-center w-14 h-14 rounded-xl transition-colors',
                            pathname === '/notifications'
                                ? 'text-blue-500'
                                : 'text-gray-500'
                        )}
                    >
                        <Bell className="w-5 h-5" />
                        {notificationCount > 0 && (
                            <span className="absolute top-2 right-2 w-4 h-4 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                                {notificationCount > 9 ? '9+' : notificationCount}
                            </span>
                        )}
                        <span className="text-[10px] mt-1 font-medium">Alerts</span>
                    </Link>

                    <button
                        onClick={() => setShowMoreMenu(true)}
                        className="flex flex-col items-center justify-center w-14 h-14 rounded-xl text-gray-500"
                    >
                        <Menu className="w-5 h-5" />
                        <span className="text-[10px] mt-1 font-medium">More</span>
                    </button>
                </div>

                {/* Safe area padding for notched devices */}
                <div className="h-safe-area-inset-bottom bg-white dark:bg-gray-900" />
            </nav>

            {/* Spacer to prevent content from being hidden behind nav */}
            <div className="h-20 md:hidden" />
        </>
    );
}

// Export for customization
export { mainNavItems, moreMenuItems, defaultQuickActions };
export type { NavItem, QuickAction };

