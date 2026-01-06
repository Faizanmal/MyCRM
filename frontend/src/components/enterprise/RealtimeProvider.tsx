/**
 * Real-Time Updates Provider
 * ===========================
 * 
 * WebSocket-powered real-time data synchronization
 */

'use client';

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useToast } from '@/hooks/use-toast';

// =============================================================================
// Types
// =============================================================================

interface RealtimeMessage {
  type: string;
  channel: string;
  payload: unknown;
  timestamp: string;
}

interface PresenceUser {
  id: string;
  name: string;
  avatar?: string;
  status: 'online' | 'away' | 'busy' | 'offline';
  lastSeen: Date;
  currentPage?: string;
}

interface RealtimeContextType {
  isConnected: boolean;
  connectionState: 'connecting' | 'connected' | 'disconnected' | 'reconnecting';
  subscribe: (channel: string, callback: (data: unknown) => void) => () => void;
  publish: (channel: string, data: unknown) => void;
  presence: PresenceUser[];
  setPresence: (status: PresenceUser['status'], currentPage?: string) => void;
}

const RealtimeContext = createContext<RealtimeContextType | null>(null);

// Handle data updates from server
interface DataUpdatePayload {
  entity: string;
  id?: string;
  action: 'create' | 'update' | 'delete';
}

// =============================================================================
// Provider
// =============================================================================

export function RealtimeProvider({ children }: { children: React.ReactNode }) {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState<
    'connecting' | 'connected' | 'disconnected' | 'reconnecting'
  >('disconnected');
  const [presence, setPresenceList] = useState<PresenceUser[]>([]);

  const wsRef = useRef<WebSocket | null>(null);
  const subscribersRef = useRef<Map<string, Set<(data: unknown) => void>>>(
    new Map()
  );
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const connectRef = useRef<(() => void) | null>(null);

  const queryClient = useQueryClient();
  const { toast } = useToast();

  const handleDataUpdate = useCallback(
    (payload: DataUpdatePayload) => {
      const { entity, id, action: _action } = payload;

      // Map entities to query keys
      const queryKeyMap: Record<string, string[]> = {
        lead: ['leads'],
        contact: ['contacts'],
        opportunity: ['opportunities'],
        task: ['tasks'],
        deal: ['deals'],
        activity: ['activities'],
      };

      const queryKeys = queryKeyMap[entity];
      if (queryKeys) {
        // Invalidate list queries
        queryClient.invalidateQueries({ queryKey: queryKeys });

        // Invalidate specific entity query
        if (id) {
          queryClient.invalidateQueries({ queryKey: [...queryKeys, id] });
        }
      }
    },
    [queryClient]
  );

  // Handle incoming messages
  const handleMessage = useCallback(
    (message: RealtimeMessage) => {
      const { type, channel, payload } = message;

      switch (type) {
        case 'pong':
          // Heartbeat response
          break;

        case 'message':
          // Dispatch to channel subscribers
          const subscribers = subscribersRef.current.get(channel);
          if (subscribers) {
            subscribers.forEach((callback) => callback(payload));
          }
          break;

        case 'presence':
          // Update presence list
          setPresenceList(payload as PresenceUser[]);
          break;

        case 'data_update':
          // Invalidate React Query cache
          handleDataUpdate(payload as DataUpdatePayload);
          break;

        case 'notification':
          // Show toast notification
          {
            const notif = payload as { title: string; message: string; type?: string };
            toast({
              title: notif.title,
              description: notif.message,
              variant: notif.type === 'error' ? 'destructive' : 'default',
            });
          }
          break;

        default:
          console.log('[Realtime] Unknown message type:', type);
      }
    },
    [toast, handleDataUpdate]
  );

  // Connect to WebSocket
  const connect = useCallback(() => {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      console.log('[Realtime] No auth token, skipping connection');
      return;
    }

    const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'
      }/ws/realtime?token=${token}`;

    // Defer setting connection state so calling connect from an effect doesn't synchronously set state
    Promise.resolve().then(() => setConnectionState('connecting'));

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('[Realtime] Connected');
        setIsConnected(true);
        setConnectionState('connected');
        reconnectAttemptsRef.current = 0;

        // Start heartbeat
        heartbeatIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }));
          }
        }, 30000);

        // Subscribe to existing channels
        subscribersRef.current.forEach((_, channel) => {
          ws.send(
            JSON.stringify({
              type: 'subscribe',
              channel,
            })
          );
        });
      };

      ws.onmessage = (event) => {
        try {
          const message: RealtimeMessage = JSON.parse(event.data);
          handleMessage(message);
        } catch (error) {
          console.error('[Realtime] Parse error:', error);
        }
      };

      ws.onclose = () => {
        console.log('[Realtime] Disconnected');
        setIsConnected(false);
        setConnectionState('disconnected');

        if (heartbeatIntervalRef.current) {
          clearInterval(heartbeatIntervalRef.current);
        }

        // Attempt reconnection with exponential backoff
        const delay = Math.min(
          1000 * Math.pow(2, reconnectAttemptsRef.current),
          30000
        );
        reconnectAttemptsRef.current++;

        setConnectionState('reconnecting');
        reconnectTimeoutRef.current = setTimeout(() => {
          connectRef.current?.();
        }, delay);
      };

      ws.onerror = (error) => {
        console.error('[Realtime] Error:', error);
      };
    } catch (error) {
      console.error('[Realtime] Connection failed:', error);
      setConnectionState('disconnected');
    }
  }, [handleMessage]);

  useEffect(() => {
    connectRef.current = connect;
  }, [connect]);

  // Subscribe to a channel
  const subscribe = useCallback(
    (channel: string, callback: (data: unknown) => void) => {
      if (!subscribersRef.current.has(channel)) {
        subscribersRef.current.set(channel, new Set());

        // Send subscribe message if connected
        if (wsRef.current?.readyState === WebSocket.OPEN) {
          wsRef.current.send(
            JSON.stringify({
              type: 'subscribe',
              channel,
            })
          );
        }
      }

      subscribersRef.current.get(channel)!.add(callback);

      // Return unsubscribe function
      return () => {
        const subscribers = subscribersRef.current.get(channel);
        if (subscribers) {
          subscribers.delete(callback);

          // Unsubscribe from channel if no more listeners
          if (subscribers.size === 0) {
            subscribersRef.current.delete(channel);

            if (wsRef.current?.readyState === WebSocket.OPEN) {
              wsRef.current.send(
                JSON.stringify({
                  type: 'unsubscribe',
                  channel,
                })
              );
            }
          }
        }
      };
    },
    []
  );

  // Publish to a channel
  const publish = useCallback((channel: string, data: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: 'message',
          channel,
          payload: data,
        })
      );
    }
  }, []);

  // Set user presence
  const setPresence = useCallback(
    (status: PresenceUser['status'], currentPage?: string) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(
          JSON.stringify({
            type: 'presence',
            payload: { status, currentPage },
          })
        );
      }
    },
    []
  );

  // Connect on mount
  useEffect(() => {
    // Defer connect to avoid synchronous setState inside effect
    Promise.resolve().then(() => connect());

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
      }
    };
  }, [connect]);

  // Track page visibility for presence
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        setPresence('away');
      } else {
        setPresence('online', window.location.pathname);
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [setPresence]);

  return (
    <RealtimeContext.Provider
      value={{
        isConnected,
        connectionState,
        subscribe,
        publish,
        presence,
        setPresence,
      }}
    >
      {children}
    </RealtimeContext.Provider>
  );
}

// =============================================================================
// Hooks
// =============================================================================

export function useRealtime() {
  const context = useContext(RealtimeContext);
  if (!context) {
    throw new Error('useRealtime must be used within RealtimeProvider');
  }
  return context;
}

export function useChannel<T = unknown>(
  channel: string,
  onMessage: (data: T) => void
) {
  const { subscribe } = useRealtime();

  useEffect(() => {
    const unsubscribe = subscribe(channel, onMessage as (data: unknown) => void);
    return unsubscribe;
  }, [channel, subscribe, onMessage]);
}

export function usePresence() {
  const { presence, setPresence } = useRealtime();
  return { presence, setPresence };
}

export function useConnectionStatus() {
  const { isConnected, connectionState } = useRealtime();
  return { isConnected, connectionState };
}

// =============================================================================
// Collaborative Editing Hook
// =============================================================================

interface CursorPosition {
  userId: string;
  userName: string;
  color: string;
  position: { x: number; y: number };
  selection?: { start: number; end: number };
}

export function useCollaborativeEditing(documentId: string) {
  const { subscribe, publish } = useRealtime();
  const [cursors, setCursors] = useState<Map<string, CursorPosition>>(new Map());

  useEffect(() => {
    const channel = `document:${documentId}`;

    const unsubscribe = subscribe(channel, (data) => {
      const cursorData = data as CursorPosition;
      setCursors((prev) => {
        const next = new Map(prev);
        next.set(cursorData.userId, cursorData);
        return next;
      });
    });

    return unsubscribe;
  }, [documentId, subscribe]);

  const updateCursor = useCallback(
    (position: { x: number; y: number }, selection?: { start: number; end: number }) => {
      publish(`document:${documentId}`, {
        type: 'cursor',
        position,
        selection,
      });
    },
    [documentId, publish]
  );

  const publishChange = useCallback(
    (change: unknown) => {
      publish(`document:${documentId}`, {
        type: 'change',
        change,
      });
    },
    [documentId, publish]
  );

  return {
    cursors: Array.from(cursors.values()),
    updateCursor,
    publishChange,
  };
}

// =============================================================================
// Live Activity Feed Hook
// =============================================================================

interface Activity {
  id: string;
  type: string;
  user: {
    id: string;
    name: string;
    avatar?: string;
  };
  action: string;
  target: string;
  timestamp: Date;
  metadata?: Record<string, unknown>;
}

export function useLiveActivityFeed(entityType?: string, entityId?: string) {
  const { subscribe } = useRealtime();
  const [activities, setActivities] = useState<Activity[]>([]);

  useEffect(() => {
    const channel = entityId
      ? `activity:${entityType}:${entityId}`
      : `activity:${entityType || 'global'}`;

    const unsubscribe = subscribe(channel, (data) => {
      const activity = data as Activity;
      setActivities((prev) => [activity, ...prev].slice(0, 50));
    });

    return unsubscribe;
  }, [entityType, entityId, subscribe]);

  return activities;
}

// =============================================================================
// Connection Status Indicator
// =============================================================================

export function ConnectionIndicator() {
  const { connectionState } = useConnectionStatus();

  const statusConfig = {
    connected: {
      color: 'bg-green-500',
      text: 'Connected',
    },
    connecting: {
      color: 'bg-yellow-500',
      text: 'Connecting...',
    },
    disconnected: {
      color: 'bg-red-500',
      text: 'Disconnected',
    },
    reconnecting: {
      color: 'bg-yellow-500 animate-pulse',
      text: 'Reconnecting...',
    },
  };

  const config = statusConfig[connectionState];

  return (
    <div className="flex items-center gap-2 text-sm">
      <div className={`w-2 h-2 rounded-full ${config.color}`} />
      <span className="text-muted-foreground">{config.text}</span>
    </div>
  );
}

export default RealtimeProvider;
