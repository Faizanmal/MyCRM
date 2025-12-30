'use client';

import { useState } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import {
    Settings,
    User,
    Bell,
    Palette,
    Shield,
    Download,
    Keyboard,
    CreditCard,
    Users,
    Building2,
    Plug,
    Database,
    Mail,
    Lock,
    Globe,
    ChevronRight,
    ChevronDown,
    Menu,
    X,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';

// Types
interface NavItem {
    title: string;
    href: string;
    icon: React.ElementType;
    badge?: string;
    badgeVariant?: 'default' | 'secondary' | 'destructive' | 'outline';
    children?: NavItem[];
}

interface NavSection {
    title: string;
    items: NavItem[];
}

// Navigation structure
const settingsNavigation: NavSection[] = [
    {
        title: 'Account',
        items: [
            { title: 'Profile', href: '/settings/profile', icon: User },
            { title: 'Preferences', href: '/settings/preferences', icon: Palette },
            { title: 'Notifications', href: '/settings/notifications', icon: Bell, badge: '3', badgeVariant: 'destructive' },
            { title: 'Security', href: '/settings/security', icon: Lock },
            { title: 'Privacy', href: '/settings/privacy', icon: Shield },
        ],
    },
    {
        title: 'Workspace',
        items: [
            { title: 'Team', href: '/settings/team', icon: Users },
            { title: 'Organization', href: '/settings/organization', icon: Building2 },
            { title: 'Billing', href: '/settings/billing', icon: CreditCard, badge: 'Pro', badgeVariant: 'secondary' },
        ],
    },
    {
        title: 'Data',
        items: [
            { title: 'Import', href: '/settings/import', icon: Database },
            { title: 'Export', href: '/settings/export', icon: Download },
            { title: 'Integrations', href: '/settings/integrations', icon: Plug, badge: '5' },
        ],
    },
    {
        title: 'Communication',
        items: [
            { title: 'Email Settings', href: '/settings/email', icon: Mail },
            { title: 'Templates', href: '/settings/templates', icon: Globe },
        ],
    },
    {
        title: 'Advanced',
        items: [
            { title: 'Keyboard Shortcuts', href: '/settings/shortcuts', icon: Keyboard },
            { title: 'API Keys', href: '/settings/api', icon: Lock },
        ],
    },
];

// Sidebar Item Component
function SidebarItem({ item, isActive, collapsed }: { item: NavItem; isActive: boolean; collapsed: boolean }) {
    const [isExpanded, setIsExpanded] = useState(false);
    const hasChildren = item.children && item.children.length > 0;
    const pathname = usePathname();

    const isChildActive = hasChildren && item.children?.some(child => pathname === child.href);
    const shouldHighlight = isActive || isChildActive;

    return (
        <div>
            <Link
                href={hasChildren ? '#' : item.href}
                onClick={hasChildren ? (e) => { e.preventDefault(); setIsExpanded(!isExpanded); } : undefined}
                className={cn(
                    'flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all',
                    'hover:bg-gray-100 dark:hover:bg-gray-800',
                    shouldHighlight && 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 font-medium',
                    !shouldHighlight && 'text-gray-700 dark:text-gray-300'
                )}
            >
                <item.icon className={cn(
                    'w-5 h-5 shrink-0',
                    shouldHighlight ? 'text-blue-600 dark:text-blue-400' : 'text-gray-400'
                )} />

                {!collapsed && (
                    <>
                        <span className="flex-1">{item.title}</span>

                        {item.badge && (
                            <Badge
                                variant={item.badgeVariant || 'default'}
                                className="ml-auto text-xs"
                            >
                                {item.badge}
                            </Badge>
                        )}

                        {hasChildren && (
                            <motion.div
                                animate={{ rotate: isExpanded ? 90 : 0 }}
                                transition={{ duration: 0.2 }}
                            >
                                <ChevronRight className="w-4 h-4" />
                            </motion.div>
                        )}
                    </>
                )}
            </Link>

            {/* Children */}
            <AnimatePresence>
                {!collapsed && hasChildren && isExpanded && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="ml-8 mt-1 space-y-1 overflow-hidden"
                    >
                        {item.children?.map((child) => (
                            <Link
                                key={child.href}
                                href={child.href}
                                className={cn(
                                    'flex items-center gap-2 px-3 py-1.5 rounded text-sm transition-colors',
                                    'hover:bg-gray-100 dark:hover:bg-gray-800',
                                    pathname === child.href && 'text-blue-600 dark:text-blue-400 font-medium'
                                )}
                            >
                                <child.icon className="w-4 h-4" />
                                {child.title}
                            </Link>
                        ))}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}

// Main Sidebar Component
export default function SettingsSidebar() {
    const pathname = usePathname();
    const [collapsed, setCollapsed] = useState(false);
    const [mobileOpen, setMobileOpen] = useState(false);

    const SidebarContent = () => (
        <div className="h-full flex flex-col">
            {/* Header */}
            <div className={cn(
                'flex items-center gap-3 px-4 py-4 border-b dark:border-gray-800',
                collapsed && 'justify-center'
            )}>
                <Settings className="w-6 h-6 text-blue-500" />
                {!collapsed && <h2 className="text-lg font-semibold">Settings</h2>}
            </div>

            {/* Navigation */}
            <ScrollArea className="flex-1 py-4">
                <div className="px-3 space-y-6">
                    {settingsNavigation.map((section, idx) => (
                        <div key={section.title}>
                            {!collapsed && (
                                <h3 className="px-3 mb-2 text-xs font-semibold uppercase tracking-wider text-gray-400">
                                    {section.title}
                                </h3>
                            )}
                            <div className="space-y-1">
                                {section.items.map((item) => (
                                    <SidebarItem
                                        key={item.href}
                                        item={item}
                                        isActive={pathname === item.href}
                                        collapsed={collapsed}
                                    />
                                ))}
                            </div>
                            {idx < settingsNavigation.length - 1 && collapsed && (
                                <Separator className="my-4" />
                            )}
                        </div>
                    ))}
                </div>
            </ScrollArea>

            {/* Footer */}
            <div className="p-4 border-t dark:border-gray-800">
                <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setCollapsed(!collapsed)}
                    className="w-full justify-center"
                >
                    {collapsed ? (
                        <ChevronRight className="w-4 h-4" />
                    ) : (
                        <>
                            <ChevronDown className="w-4 h-4 mr-2 rotate-90" />
                            Collapse
                        </>
                    )}
                </Button>
            </div>
        </div>
    );

    return (
        <>
            {/* Desktop Sidebar */}
            <motion.aside
                animate={{ width: collapsed ? 80 : 280 }}
                transition={{ duration: 0.2 }}
                className="hidden md:block h-screen bg-white dark:bg-gray-900 border-r dark:border-gray-800 sticky top-0"
            >
                <SidebarContent />
            </motion.aside>

            {/* Mobile Toggle */}
            <div className="md:hidden fixed bottom-4 left-4 z-50">
                <Button
                    size="icon"
                    variant="secondary"
                    onClick={() => setMobileOpen(true)}
                    className="rounded-full shadow-lg"
                >
                    <Menu className="w-5 h-5" />
                </Button>
            </div>

            {/* Mobile Sidebar */}
            <AnimatePresence>
                {mobileOpen && (
                    <>
                        {/* Overlay */}
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={() => setMobileOpen(false)}
                            className="md:hidden fixed inset-0 bg-black/50 z-40"
                        />

                        {/* Sidebar */}
                        <motion.aside
                            initial={{ x: -280 }}
                            animate={{ x: 0 }}
                            exit={{ x: -280 }}
                            transition={{ type: 'spring', damping: 25 }}
                            className="md:hidden fixed inset-y-0 left-0 w-72 bg-white dark:bg-gray-900 z-50 shadow-xl"
                        >
                            <div className="absolute top-4 right-4">
                                <Button
                                    size="icon"
                                    variant="ghost"
                                    onClick={() => setMobileOpen(false)}
                                >
                                    <X className="w-5 h-5" />
                                </Button>
                            </div>
                            <SidebarContent />
                        </motion.aside>
                    </>
                )}
            </AnimatePresence>
        </>
    );
}

// Export for use in settings layout
export { settingsNavigation };
export type { NavItem, NavSection };
