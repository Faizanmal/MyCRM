'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
// import { Skeleton } from '@/components/ui/skeleton';
import {
    Bell,
    X,
    Check,
    CheckCheck,
    Calendar,
    DollarSign,
    MessageSquare,
    Trophy,
    Info,
    Sparkles,
    ExternalLink,
    Trash2,
    MoreHorizontal,
} from 'lucide-react';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { activityAPI } from '@/lib/api';
import { useRealtime, useRealtimeSubscription } from '@/hooks/useRealtimeNotifications';

type NotificationType = 'mention' | 'deal' | 'task' | 'achievement' | 'system' | 'ai';
type NotificationPriority = 'low' | 'normal' | 'high' | 'urgent';

interface Notification {
    id: string;
    type: NotificationType;
    priority: NotificationPriority;
    title: string;
    message: string;
    timestamp: Date;
    read: boolean;
    actionUrl?: string;
    actionLabel?: string;
    sender?: {
        name: string;
        avatar?: string;
    };
}

const typeIcons: Record<NotificationType, React.ElementType> = {
    mention: MessageSquare,
    deal: DollarSign,
    task: Calendar,
    achievement: Trophy,
    system: Info,
    ai: Sparkles,
};

const typeColors: Record<NotificationType, string> = {
    mention: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30',
    deal: 'bg-green-100 text-green-600 dark:bg-green-900/30',
    task: 'bg-amber-100 text-amber-600 dark:bg-amber-900/30',
    achievement: 'bg-purple-100 text-purple-600 dark:bg-purple-900/30',
    system: 'bg-gray-100 text-gray-600 dark:bg-gray-800',
    ai: 'bg-pink-100 text-pink-600 dark:bg-pink-900/30',
};

const priorityColors: Record<NotificationPriority, string> = {
    low: 'bg-gray-200 text-gray-600',
    normal: 'bg-blue-200 text-blue-700',
    high: 'bg-amber-200 text-amber-700',
    urgent: 'bg-red-200 text-red-700',
};

// Mock notifications - replace with actual API
const mockNotifications: Notification[] = [
    {
        id: '1',
        type: 'mention',
        priority: 'high',
        title: 'Sarah mentioned you',
        message: 'Can you take a look at the TechCorp deal proposal?',
        timestamp: new Date(Date.now() - 5 * 60 * 1000),
        read: false,
        actionUrl: '/opportunities/123',
        actionLabel: 'View Deal',
        sender: { name: 'Sarah Johnson' },
    },
    {
        id: '2',
        type: 'deal',
        priority: 'urgent',
        title: 'Deal stage changed',
        message: 'Enterprise Deal - TechCorp moved to "Negotiation" stage',
        timestamp: new Date(Date.now() - 30 * 60 * 1000),
        read: false,
        actionUrl: '/opportunities/456',
        actionLabel: 'View Pipeline',
    },
    {
        id: '3',
        type: 'achievement',
        priority: 'normal',
        title: '🏆 New Achievement!',
        message: 'You earned "Deal Closer" badge for closing 10 deals!',
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
        read: false,
        actionUrl: '/gamification',
        actionLabel: 'View Achievements',
    },
    {
        id: '4',
        type: 'task',
        priority: 'high',
        title: 'Task Overdue',
        message: 'Follow up with John Smith is now overdue',
        timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000),
        read: true,
        actionUrl: '/tasks/789',
        actionLabel: 'View Task',
    },
    {
        id: '5',
        type: 'ai',
        priority: 'normal',
        title: 'AI Insight',
        message: 'Based on engagement patterns, 3 leads have high conversion potential',
        timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000),
        read: true,
        actionUrl: '/ai-insights',
        actionLabel: 'View Insights',
    },
];

export default function EnhancedNotifications() {
    const [isOpen, setIsOpen] = useState(false);
    const [notifications, setNotifications] = useState<Notification[]>(mockNotifications);
    const [filter, setFilter] = useState<'all' | NotificationType>('all');
    const [_isLoading, setIsLoading] = useState(true);
    const router = useRouter();

    // Real-time connection status
    const { isConnected } = useRealtime();

    // Listen for real-time notifications
    useRealtimeSubscription('notification', (message) => {
        const newNotification: Notification = {
            id: String(Date.now()),
            type: (message.payload.type as NotificationType) || 'system',
            priority: (message.payload.priority as NotificationPriority) || 'normal',
            title: String(message.payload.title || 'New Notification'),
            message: String(message.payload.message || ''),
            timestamp: new Date(message.timestamp),
            read: false,
            actionUrl: message.payload.action_url as string | undefined,
            actionLabel: message.payload.action_label as string | undefined,
        };
        setNotifications(prev => [newNotification, ...prev]);
    }, []);

    // Fetch notifications from API
    const fetchNotifications = useCallback(async () => {
        try {
            setIsLoading(true);
            const response = await activityAPI.getNotifications();
            const data = response?.data || response;
            const notificationsList = data?.results || data || [];
            const apiNotifications = (Array.isArray(notificationsList) ? notificationsList : []).map((n: Record<string, unknown>) => ({
                id: String(n.id),
                type: (n.notification_type as NotificationType) || 'system',
                priority: (n.priority as NotificationPriority) || 'normal',
                title: String(n.title || ''),
                message: String(n.message || ''),
                timestamp: new Date(String(n.created_at)),
                read: Boolean(n.is_read),
                actionUrl: n.action_url as string | undefined,
                actionLabel: n.action_label as string | undefined,
            }));
            setNotifications(apiNotifications.length > 0 ? apiNotifications : mockNotifications);
        } catch (error) {
            // Use mock data on error
            console.log('Using mock notifications', error);
            setNotifications(mockNotifications);
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchNotifications();
    }, [fetchNotifications]);

    const unreadCount = notifications.filter(n => !n.read).length;
    const filteredNotifications = filter === 'all'
        ? notifications
        : notifications.filter(n => n.type === filter);

    const markAsRead = useCallback(async (id: string) => {
        setNotifications(prev => prev.map(n =>
            n.id === id ? { ...n, read: true } : n
        ));
        try {
            await activityAPI.markNotificationRead(id);
        } catch (error) {
            // Already updated locally
            console.log('Failed to mark notification as read', error);
        }
    }, []);

    const markAllAsRead = useCallback(async () => {
        setNotifications(prev => prev.map(n => ({ ...n, read: true })));
        try {
            await activityAPI.markAllNotificationsRead();
        } catch (error) {
            // Already updated locally
            console.log('Failed to mark all notifications as read', error);
        }
        toast.success('All notifications marked as read');
    }, []);

    const deleteNotification = useCallback((id: string) => {
        setNotifications(prev => prev.filter(n => n.id !== id));
        toast.success('Notification deleted');
    }, []);

    const clearAll = useCallback(() => {
        setNotifications([]);
        toast.success('All notifications cleared');
    }, []);

    const handleAction = (notification: Notification) => {
        markAsRead(notification.id);
        if (notification.actionUrl) {
            router.push(notification.actionUrl);
            setIsOpen(false);
        }
    };

    const formatTime = (date: Date) => {
        const now = new Date();
        const diff = now.getTime() - date.getTime();
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);

        if (minutes < 1) return 'Just now';
        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        if (days === 1) return 'Yesterday';
        return `${days}d ago`;
    };

    // Close on escape
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'Escape') setIsOpen(false);
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, []);

    return (
        <div className="relative">
            {/* Notification Bell */}
            <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsOpen(!isOpen)}
                className="relative"
            >
                <Bell className="w-5 h-5" />
                {unreadCount > 0 && (
                    <motion.span
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center"
                    >
                        {unreadCount > 9 ? '9+' : unreadCount}
                    </motion.span>
                )}
                {/* Connection indicator */}
                <span className={`absolute bottom-0 right-0 w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-gray-400'}`}
                    title={isConnected ? 'Real-time connected' : 'Real-time disconnected'}
                />
            </Button>

            {/* Notification Panel */}
            <AnimatePresence>
                {isOpen && (
                    <>
                        {/* Backdrop */}
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={() => setIsOpen(false)}
                            className="fixed inset-0 z-40"
                        />

                        {/* Panel */}
                        <motion.div
                            initial={{ opacity: 0, y: 10, scale: 0.95 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            exit={{ opacity: 0, y: 10, scale: 0.95 }}
                            transition={{ duration: 0.15 }}
                            className="absolute right-0 mt-2 w-96 bg-white dark:bg-gray-900 rounded-xl shadow-2xl border dark:border-gray-800 z-50 overflow-hidden"
                        >
                            {/* Header */}
                            <div className="p-4 border-b dark:border-gray-800">
                                <div className="flex items-center justify-between mb-3">
                                    <div className="flex items-center gap-2">
                                        <h3 className="font-semibold">Notifications</h3>
                                        {unreadCount > 0 && (
                                            <Badge variant="secondary">{unreadCount} new</Badge>
                                        )}
                                    </div>
                                    <div className="flex items-center gap-1">
                                        {unreadCount > 0 && (
                                            <Button variant="ghost" size="sm" onClick={markAllAsRead}>
                                                <CheckCheck className="w-4 h-4 mr-1" />
                                                Mark all read
                                            </Button>
                                        )}
                                        <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => setIsOpen(false)}>
                                            <X className="w-4 h-4" />
                                        </Button>
                                    </div>
                                </div>

                                {/* Filter Tabs */}
                                <div className="flex items-center gap-1 overflow-x-auto pb-1">
                                    {(['all', 'mention', 'deal', 'task', 'achievement', 'ai'] as const).map(type => (
                                        <Button
                                            key={type}
                                            variant={filter === type ? 'default' : 'ghost'}
                                            size="sm"
                                            onClick={() => setFilter(type)}
                                            className="h-7 text-xs capitalize shrink-0"
                                        >
                                            {type === 'all' ? 'All' : type}
                                        </Button>
                                    ))}
                                </div>
                            </div>

                            {/* Notifications List */}
                            <ScrollArea className="max-h-[400px]">
                                {filteredNotifications.length > 0 ? (
                                    <div className="divide-y dark:divide-gray-800">
                                        {filteredNotifications.map((notification, index) => {
                                            const Icon = typeIcons[notification.type];
                                            return (
                                                <motion.div
                                                    key={notification.id}
                                                    initial={{ opacity: 0, x: -10 }}
                                                    animate={{ opacity: 1, x: 0 }}
                                                    transition={{ delay: index * 0.03 }}
                                                    className={`p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors cursor-pointer ${!notification.read ? 'bg-blue-50/50 dark:bg-blue-900/10' : ''
                                                        }`}
                                                    onClick={() => handleAction(notification)}
                                                >
                                                    <div className="flex items-start gap-3">
                                                        <div className={`p-2 rounded-lg shrink-0 ${typeColors[notification.type]}`}>
                                                            <Icon className="w-4 h-4" />
                                                        </div>
                                                        <div className="flex-1 min-w-0">
                                                            <div className="flex items-center gap-2 mb-0.5">
                                                                <span className="font-medium text-sm truncate">{notification.title}</span>
                                                                {!notification.read && (
                                                                    <div className="w-2 h-2 bg-blue-500 rounded-full shrink-0" />
                                                                )}
                                                            </div>
                                                            <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                                                                {notification.message}
                                                            </p>
                                                            <div className="flex items-center gap-2 mt-2">
                                                                <span className="text-xs text-gray-400">{formatTime(notification.timestamp)}</span>
                                                                {notification.priority !== 'normal' && (
                                                                    <Badge variant="outline" className={`text-xs ${priorityColors[notification.priority]}`}>
                                                                        {notification.priority}
                                                                    </Badge>
                                                                )}
                                                            </div>
                                                        </div>
                                                        <DropdownMenu>
                                                            <DropdownMenuTrigger asChild>
                                                                <Button
                                                                    variant="ghost"
                                                                    size="icon"
                                                                    className="h-7 w-7 shrink-0"
                                                                    onClick={e => e.stopPropagation()}
                                                                >
                                                                    <MoreHorizontal className="w-4 h-4" />
                                                                </Button>
                                                            </DropdownMenuTrigger>
                                                            <DropdownMenuContent align="end">
                                                                {!notification.read && (
                                                                    <DropdownMenuItem onClick={(e) => { e.stopPropagation(); markAsRead(notification.id); }}>
                                                                        <Check className="w-4 h-4 mr-2" />
                                                                        Mark as read
                                                                    </DropdownMenuItem>
                                                                )}
                                                                {notification.actionUrl && (
                                                                    <DropdownMenuItem onClick={(e) => { e.stopPropagation(); handleAction(notification); }}>
                                                                        <ExternalLink className="w-4 h-4 mr-2" />
                                                                        {notification.actionLabel || 'View'}
                                                                    </DropdownMenuItem>
                                                                )}
                                                                <DropdownMenuItem
                                                                    onClick={(e) => { e.stopPropagation(); deleteNotification(notification.id); }}
                                                                    className="text-red-600"
                                                                >
                                                                    <Trash2 className="w-4 h-4 mr-2" />
                                                                    Delete
                                                                </DropdownMenuItem>
                                                            </DropdownMenuContent>
                                                        </DropdownMenu>
                                                    </div>
                                                </motion.div>
                                            );
                                        })}
                                    </div>
                                ) : (
                                    <div className="p-8 text-center">
                                        <Bell className="w-12 h-12 text-gray-200 dark:text-gray-700 mx-auto mb-3" />
                                        <p className="text-gray-500">No notifications</p>
                                        <p className="text-sm text-gray-400">You&apos;re all caught up!</p>
                                    </div>
                                )}
                            </ScrollArea>

                            {/* Footer */}
                            {notifications.length > 0 && (
                                <div className="p-3 border-t dark:border-gray-800 flex items-center justify-between">
                                    <Button variant="ghost" size="sm" onClick={() => router.push('/settings/notifications')}>
                                        Notification Settings
                                    </Button>
                                    <Button variant="ghost" size="sm" onClick={clearAll} className="text-red-600 hover:text-red-700">
                                        Clear All
                                    </Button>
                                </div>
                            )}
                        </motion.div>
                    </>
                )}
            </AnimatePresence>
        </div>
    );
}
