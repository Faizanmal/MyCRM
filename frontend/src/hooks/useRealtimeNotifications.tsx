'use client';

import { createContext, useContext, useEffect, useState, useCallback, useRef, ReactNode } from 'react';
import { toast } from 'sonner';

interface RealtimeMessage {
    type: string;
    payload: Record<string, unknown>;
    timestamp: string;
}

interface RealtimeContextType {
    isConnected: boolean;
    lastMessage: RealtimeMessage | null;
    subscribe: (channel: string, callback: (message: RealtimeMessage) => void) => () => void;
    send: (type: string, payload: Record<string, unknown>) => void;
}

const RealtimeContext = createContext<RealtimeContextType | null>(null);

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/crm/';

export function RealtimeNotificationProvider({ children }: { children: ReactNode }) {
    const [isConnected, setIsConnected] = useState(false);
    const [lastMessage, setLastMessage] = useState<RealtimeMessage | null>(null);
    const wsRef = useRef<WebSocket | null>(null);
    const subscribersRef = useRef<Map<string, Set<(message: RealtimeMessage) => void>>>(new Map());
    const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const reconnectAttemptsRef = useRef(0);
    const maxReconnectAttempts = 5;
    const connectRef = useRef<() => void | null>(null);

    const handleSystemMessage = useCallback((message: RealtimeMessage) => {
        switch (message.type) {
            case 'notification':
                const { title, body } = message.payload as { title?: string; body?: string };
                if (title) {
                    toast(title, { description: body });
                }
                break;

            case 'achievement':
                const achievement = message.payload as { name?: string; xp?: number };
                toast.success(`🏆 Achievement Unlocked: ${achievement.name}`, {
                    description: `+${achievement.xp || 0} XP`,
                });
                break;

            case 'recommendation':
                // New AI recommendation available
                toast.info('💡 New AI insight available', {
                    action: {
                        label: 'View',
                        onClick: () => window.location.href = '/dashboard',
                    },
                });
                break;

            case 'deal_update':
                const deal = message.payload as { name?: string; stage?: string };
                toast(`Deal Updated: ${deal.name}`, {
                    description: `Moved to ${deal.stage}`,
                });
                break;

            case 'mention':
                const mention = message.payload as { from?: string; context?: string };
                toast(`${mention.from} mentioned you`, {
                    description: mention.context,
                });
                break;
        }
    }, []);

    const connect = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return;

        const token = localStorage.getItem('access_token');
        if (!token) return;

        try {
            const ws = new WebSocket(`${WS_URL}?token=${token}`);

            ws.onopen = () => {
                setIsConnected(true);
                reconnectAttemptsRef.current = 0;
                console.warn('WebSocket connected');
            };

            ws.onmessage = (event) => {
                try {
                    const message: RealtimeMessage = JSON.parse(event.data);
                    setLastMessage(message);

                    // Dispatch to subscribers
                    const channelSubscribers = subscribersRef.current.get(message.type);
                    if (channelSubscribers) {
                        channelSubscribers.forEach(callback => callback(message));
                    }

                    // Also dispatch to 'all' subscribers
                    const allSubscribers = subscribersRef.current.get('all');
                    if (allSubscribers) {
                        allSubscribers.forEach(callback => callback(message));
                    }

                    // Handle specific message types
                    handleSystemMessage(message);
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error);
                }
            };

            ws.onclose = () => {
                setIsConnected(false);
                wsRef.current = null;

                // Attempt reconnection
                if (reconnectAttemptsRef.current < maxReconnectAttempts) {
                    const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000);
                    reconnectTimeoutRef.current = setTimeout(() => {
                        reconnectAttemptsRef.current++;
                        connectRef.current?.();
                    }, delay);
                }
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };

            wsRef.current = ws;
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
        }
    }, [handleSystemMessage]);

    useEffect(() => {
        connectRef.current = connect;
    }, [connect]);

    const disconnect = useCallback(() => {
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
        }
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }
        setIsConnected(false);
    }, []);

    const subscribe = useCallback((channel: string, callback: (message: RealtimeMessage) => void) => {
        if (!subscribersRef.current.has(channel)) {
            subscribersRef.current.set(channel, new Set());
        }
        subscribersRef.current.get(channel)!.add(callback);

        // Return unsubscribe function
        return () => {
            const channelSubs = subscribersRef.current.get(channel);
            if (channelSubs) {
                channelSubs.delete(callback);
                if (channelSubs.size === 0) {
                    subscribersRef.current.delete(channel);
                }
            }
        };
    }, []);

    const send = useCallback((type: string, payload: Record<string, unknown>) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ type, payload, timestamp: new Date().toISOString() }));
        }
    }, []);

    useEffect(() => {
        connect();
        return () => disconnect();
    }, [connect, disconnect]);

    return (
        <RealtimeContext.Provider value={{ isConnected, lastMessage, subscribe, send }}>
            {children}
        </RealtimeContext.Provider>
    );
}

export function useRealtime() {
    const context = useContext(RealtimeContext);
    if (!context) {
        // Return a mock context when not inside provider
        return {
            isConnected: false,
            lastMessage: null,
            subscribe: () => () => { /* mock */ },
            send: () => { /* mock */ },
        };
    }
    return context;
}

// Hook to subscribe to specific message types
export function useRealtimeSubscription(
    channel: string,
    callback: (message: RealtimeMessage) => void,
    deps: unknown[] = []
) {
    const { subscribe } = useRealtime();

    useEffect(() => {
        const unsubscribe = subscribe(channel, callback);
        return unsubscribe;

    }, [channel, subscribe, callback, deps]);
}

// Hook for real-time notifications
export function useRealtimeNotifications() {
    const [notifications, setNotifications] = useState<RealtimeMessage[]>([]);
    const { subscribe } = useRealtime();

    useEffect(() => {
        const unsubscribe = subscribe('notification', (message) => {
            setNotifications(prev => [message, ...prev].slice(0, 50));
        });
        return unsubscribe;
    }, [subscribe]);

    const clearNotifications = () => setNotifications([]);

    return { notifications, clearNotifications };
}

