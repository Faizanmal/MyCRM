'use client';

import React, {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  useCallback,
  useMemo,
} from 'react';

// ============================================================================
// Types
// ============================================================================

interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
}

interface PresenceData {
  userId: string;
  status: 'online' | 'busy' | 'away' | 'dnd' | 'offline';
  statusMessage?: string;
  currentPage?: string;
  isTyping?: boolean;
  typingField?: string;
  lastSeen?: Date;
}

interface CursorPosition {
  field: string;
  offset: number;
  length?: number;
}

interface Selection {
  field: string;
  start: number;
  end: number;
}

interface Participant {
  userId: string;
  user: User;
  role: 'owner' | 'editor' | 'commenter' | 'viewer';
  status: 'active' | 'idle' | 'away' | 'disconnected';
  cursor?: CursorPosition;
  selection?: Selection;
  color: string;
  joinedAt: Date;
}

interface CollaborationSession {
  id: string;
  entityType: string;
  entityId: string;
  participants: Participant[];
  isActive: boolean;
  createdAt: Date;
}

interface Change {
  id: string;
  fieldPath: string;
  changeType: 'insert' | 'delete' | 'replace' | 'move' | 'format';
  oldValue: unknown;
  newValue: unknown;
  position?: number;
  length?: number;
  version: number;
  userId: string;
  timestamp: Date;
}

interface Conflict {
  id: string;
  conflictType: string;
  localChange: Change;
  remoteChange: Change;
  resolution?: string;
  resolvedValue?: unknown;
}

interface Comment {
  id: string;
  content: string;
  fieldPath?: string;
  selectionStart?: number;
  selectionEnd?: number;
  quotedText?: string;
  author: User;
  parentId?: string;
  threadRootId?: string;
  status: 'open' | 'resolved' | 'wont_fix';
  replies: Comment[];
  createdAt: Date;
  resolvedAt?: Date;
  resolvedBy?: User;
}

interface Lock {
  id: string;
  fieldPath: string;
  userId: string;
  user: User;
  lockType: 'exclusive' | 'shared' | 'intent';
  acquiredAt: Date;
  expiresAt: Date;
}

interface RealtimeMessage {
  type: string;
  channel?: string;
  payload: unknown;
  senderId?: string;
  timestamp: string;
}

// ============================================================================
// Realtime Context
// ============================================================================

interface RealtimeContextValue {
  // Connection
  isConnected: boolean;
  connectionId: string | null;
  reconnect: () => void;
  
  // Presence
  presence: Map<string, PresenceData>;
  updatePresence: (status: string, message?: string) => void;
  updateLocation: (page: string, entityType?: string, entityId?: string) => void;
  
  // Sessions
  currentSession: CollaborationSession | null;
  joinSession: (entityType: string, entityId: string) => Promise<CollaborationSession>;
  leaveSession: () => Promise<void>;
  
  // Participants
  participants: Participant[];
  
  // Cursors & Selections
  updateCursor: (cursor: CursorPosition) => void;
  updateSelection: (selection: Selection | null) => void;
  
  // Changes
  applyChange: (change: Omit<Change, 'id' | 'version' | 'userId' | 'timestamp'>) => Promise<Change>;
  pendingChanges: Change[];
  version: number;
  
  // Conflicts
  conflicts: Conflict[];
  resolveConflict: (conflictId: string, resolvedValue: unknown) => void;
  
  // Typing indicators
  startTyping: (field: string) => void;
  stopTyping: () => void;
  typingUsers: Map<string, { userId: string; field: string }>;
  
  // Comments
  comments: Comment[];
  addComment: (content: string, options?: {
    fieldPath?: string;
    selectionStart?: number;
    selectionEnd?: number;
    quotedText?: string;
    parentId?: string;
  }) => Promise<Comment>;
  resolveComment: (commentId: string) => Promise<void>;
  
  // Locks
  locks: Lock[];
  acquireLock: (fieldPath?: string) => Promise<Lock | null>;
  releaseLock: (lockId: string) => Promise<void>;
  isFieldLocked: (fieldPath: string) => boolean;
  getFieldLockHolder: (fieldPath: string) => User | null;
  
  // Subscriptions
  subscribe: (channel: string) => void;
  unsubscribe: (channel: string) => void;
  
  // Events
  on: (event: string, handler: (payload: unknown) => void) => () => void;
  emit: (event: string, payload: unknown) => void;
}

const RealtimeContext = createContext<RealtimeContextValue | null>(null);

// ============================================================================
// Color Utilities
// ============================================================================

const PARTICIPANT_COLORS = [
  '#3B82F6', // blue
  '#10B981', // green
  '#F59E0B', // amber
  '#EF4444', // red
  '#8B5CF6', // purple
  '#EC4899', // pink
  '#06B6D4', // cyan
  '#F97316', // orange
];

function getParticipantColor(index: number): string {
  return PARTICIPANT_COLORS[index % PARTICIPANT_COLORS.length];
}

// ============================================================================
// Provider
// ============================================================================

interface RealtimeProviderProps {
  children: React.ReactNode;
  wsUrl?: string;
  userId: string;
  user: User;
  reconnectInterval?: number;
  heartbeatInterval?: number;
}

export function RealtimeProvider({
  children,
  wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/realtime/',
  userId,
  user,
  reconnectInterval = 3000,
  heartbeatInterval = 30000,
}: RealtimeProviderProps) {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionId, setConnectionId] = useState<string | null>(null);
  const [presence, setPresence] = useState<Map<string, PresenceData>>(new Map());
  const [currentSession, setCurrentSession] = useState<CollaborationSession | null>(null);
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [version, setVersion] = useState(0);
  const [pendingChanges, setPendingChanges] = useState<Change[]>([]);
  const [conflicts, setConflicts] = useState<Conflict[]>([]);
  const [typingUsers, setTypingUsers] = useState<Map<string, { userId: string; field: string }>>(new Map());
  const [comments, setComments] = useState<Comment[]>([]);
  const [locks, setLocks] = useState<Lock[]>([]);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const eventHandlersRef = useRef<Map<string, Set<(payload: unknown) => void>>>(new Map());
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  // Handle incoming messages
  const handleMessage = useCallback((message: RealtimeMessage) => {
    const { type, payload, senderId } = message;
    
    // Trigger registered event handlers
    const handlers = eventHandlersRef.current.get(type);
    if (handlers) {
      handlers.forEach(handler => handler(payload));
    }
    
    switch (type) {
      case 'presence:joined':
      case 'presence:update': {
        const p = payload as any;
        setPresence(prev => {
          const next = new Map(prev);
          next.set(p.user_id, {
            userId: p.user_id,
            status: p.status,
            statusMessage: p.status_message,
            currentPage: p.current_page,
            lastSeen: new Date(),
          });
          return next;
        });
        break;
      }
      
      case 'presence:left': {
        const p = payload as any;
        setPresence(prev => {
          const next = new Map(prev);
          next.delete(p.user_id);
          return next;
        });
        break;
      }
      
      case 'presence:typing_start': {
        const p = payload as any;
        setTypingUsers(prev => {
          const next = new Map(prev);
          next.set(p.user_id, {
            userId: p.user_id,
            field: p.field,
          });
          return next;
        });
        break;
      }
      
      case 'presence:typing_stop': {
        const p = payload as any;
        setTypingUsers(prev => {
          const next = new Map(prev);
          next.delete(p.user_id);
          return next;
        });
        break;
      }
      
      case 'session:participant_joined': {
        const p = payload as any;
        setParticipants(prev => {
          const exists = prev.some(participant => participant.userId === p.user_id);
          if (exists) return prev;
          
          return [...prev, {
            userId: p.user_id,
            user: p.user,
            role: p.role || 'editor',
            status: 'active',
            color: getParticipantColor(prev.length),
            joinedAt: new Date(),
          }];
        });
        break;
      }
      
      case 'session:participant_left': {
        const p = payload as any;
        setParticipants(prev => 
          prev.filter(participant => participant.userId !== p.user_id)
        );
        break;
      }
      
      case 'session:cursor_moved': {
        const p = payload as any;
        if (senderId !== userId) {
          setParticipants(prev => prev.map(participant => 
            participant.userId === p.user_id
              ? { ...participant, cursor: p.cursor }
              : participant
          ));
        }
        break;
      }
      
      case 'session:selection_changed': {
        const p = payload as any;
        if (senderId !== userId) {
          setParticipants(prev => prev.map(participant => 
            participant.userId === p.user_id
              ? { ...participant, selection: p.selection }
              : participant
          ));
        }
        break;
      }
      
      case 'change:applied': {
        const p = payload as any;
        setVersion(p.version);
        if (senderId !== userId) {
          setPendingChanges(prev => [...prev, {
            id: p.change_id,
            fieldPath: p.field_path,
            changeType: p.change_type,
            oldValue: p.old_value,
            newValue: p.new_value,
            position: p.position,
            length: p.length,
            version: p.version,
            userId: p.user_id,
            timestamp: new Date(message.timestamp),
          }]);
        }
        break;
      }
      
      case 'change:conflict_resolved': {
        const p = payload as any;
        if (p.conflict) {
          setConflicts(prev => [...prev, {
            id: p.conflict.conflict_id,
            conflictType: p.conflict.conflict_type,
            localChange: p.local_change,
            remoteChange: p.remote_change,
            resolution: p.conflict.resolution,
            resolvedValue: p.conflict.resolved_value,
          }]);
        }
        break;
      }
      
      case 'comment:added': {
        const p = payload as any;
        setComments(prev => {
          const newComment: Comment = {
            id: p.comment_id,
            content: p.content,
            fieldPath: p.field_path,
            author: p.author,
            parentId: p.parent_id,
            threadRootId: p.thread_root_id,
            status: 'open',
            replies: [],
            createdAt: new Date(p.created_at),
          };
          
          if (p.parent_id) {
            // Add as reply
            return prev.map(c => 
              c.id === p.parent_id || c.id === p.thread_root_id
                ? { ...c, replies: [...c.replies, newComment] }
                : c
            );
          }
          return [...prev, newComment];
        });
        break;
      }
      
      case 'comment:resolved': {
        const p = payload as any;
        setComments(prev => prev.map(c => 
          c.id === p.comment_id
            ? { ...c, status: 'resolved', resolvedAt: new Date() }
            : c
        ));
        break;
      }
      
      case 'lock:acquired': {
        const p = payload as any;
        setLocks(prev => [...prev, {
          id: p.lock_id,
          fieldPath: p.field_path,
          userId: p.user_id,
          user: p.user,
          lockType: p.lock_type,
          acquiredAt: new Date(),
          expiresAt: new Date(p.expires_at),
        }]);
        break;
      }
      
      case 'lock:released': {
        const p = payload as any;
        setLocks(prev => prev.filter(l => l.id !== p.lock_id));
        break;
      }
    }
  }, [userId]);
  
  // Connect to WebSocket
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    
    const ws = new WebSocket(`${wsUrl}?user_id=${userId}`);
    wsRef.current = ws;
    
    ws.onopen = () => {
      setIsConnected(true);
      const connId = `conn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      setConnectionId(connId);
      
      // Send initial presence
      ws.send(JSON.stringify({
        type: 'presence:update',
        status: 'online',
      }));
      
      // Start heartbeat
      heartbeatIntervalRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'heartbeat' }));
        }
      }, heartbeatInterval);
    };
    
    ws.onmessage = (event) => {
      try {
        const message: RealtimeMessage = JSON.parse(event.data);
        handleMessage(message);
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e);
      }
    };
    
    ws.onclose = () => {
      setIsConnected(false);
      setConnectionId(null);
      
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
      }
      
      // Attempt reconnect
      reconnectTimeoutRef.current = setTimeout(connect, reconnectInterval);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }, [wsUrl, userId, reconnectInterval, heartbeatInterval, handleMessage]);
  
  // Send message
  const send = useCallback((message: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);
  
  // Connect on mount
  useEffect(() => {
    connect();
    
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
      }
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
      wsRef.current?.close();
    };
  }, [connect]);
  
  // Reconnect function
  const reconnect = useCallback(() => {
    wsRef.current?.close();
    connect();
  }, [connect]);
  
  // Presence functions
  const updatePresence = useCallback((status: string, message?: string) => {
    send({ type: 'presence:update', status, status_message: message });
  }, [send]);
  
  const updateLocation = useCallback((page: string, entityType?: string, entityId?: string) => {
    send({ 
      type: 'presence:location', 
      page, 
      entity_type: entityType,
      entity_id: entityId,
    });
  }, [send]);
  
  // Session functions
  const joinSession = useCallback(async (entityType: string, entityId: string): Promise<CollaborationSession> => {
    return new Promise((resolve, reject) => {
      const channel = `session:${entityType}:${entityId}`;
      
      // Subscribe to session channel
      send({ type: 'subscribe', channel });
      
      // Join session
      send({ 
        type: 'session:join', 
        entity_type: entityType,
        entity_id: entityId,
      });
      
      // For now, create a mock session
      // In production, this would wait for server response
      const session: CollaborationSession = {
        id: `session_${Date.now()}`,
        entityType,
        entityId,
        participants: [{
          userId,
          user,
          role: 'editor',
          status: 'active',
          color: getParticipantColor(0),
          joinedAt: new Date(),
        }],
        isActive: true,
        createdAt: new Date(),
      };
      
      setCurrentSession(session);
      setParticipants(session.participants);
      resolve(session);
    });
  }, [send, userId, user]);
  
  const leaveSession = useCallback(async () => {
    if (!currentSession) return;
    
    const channel = `session:${currentSession.entityType}:${currentSession.entityId}`;
    send({ type: 'session:leave', session_id: currentSession.id });
    send({ type: 'unsubscribe', channel });
    
    setCurrentSession(null);
    setParticipants([]);
    setPendingChanges([]);
  }, [currentSession, send]);
  
  // Cursor functions
  const updateCursor = useCallback((cursor: CursorPosition) => {
    if (!currentSession) return;
    send({ 
      type: 'cursor:move', 
      session_id: currentSession.id,
      cursor,
    });
  }, [currentSession, send]);
  
  const updateSelection = useCallback((selection: Selection | null) => {
    if (!currentSession) return;
    send({ 
      type: 'selection:change', 
      session_id: currentSession.id,
      selection,
    });
  }, [currentSession, send]);
  
  // Change functions
  const applyChange = useCallback(async (change: Omit<Change, 'id' | 'version' | 'userId' | 'timestamp'>): Promise<Change> => {
    return new Promise((resolve, reject) => {
      if (!currentSession) {
        reject(new Error('No active session'));
        return;
      }
      
      send({
        type: 'change:apply',
        session_id: currentSession.id,
        field_path: change.fieldPath,
        change_type: change.changeType,
        old_value: change.oldValue,
        new_value: change.newValue,
        position: change.position,
        length: change.length,
      });
      
      // Create optimistic change
      const fullChange: Change = {
        ...change,
        id: `change_${Date.now()}`,
        version: version + 1,
        userId,
        timestamp: new Date(),
      };
      
      setVersion(v => v + 1);
      resolve(fullChange);
    });
  }, [currentSession, version, userId, send]);
  
  // Conflict resolution
  const resolveConflict = useCallback((conflictId: string, resolvedValue: unknown) => {
    send({
      type: 'conflict:resolve',
      conflict_id: conflictId,
      resolved_value: resolvedValue,
    });
    
    setConflicts(prev => prev.filter(c => c.id !== conflictId));
  }, [send]);
  
  // Typing indicators
  const startTyping = useCallback((field: string) => {
    send({ type: 'typing:start', field });
    
    // Auto-stop after 5 seconds
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }
    typingTimeoutRef.current = setTimeout(() => {
      send({ type: 'typing:stop' });
    }, 5000);
  }, [send]);
  
  const stopTyping = useCallback(() => {
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }
    send({ type: 'typing:stop' });
  }, [send]);
  
  // Comment functions
  const addComment = useCallback(async (content: string, options?: {
    fieldPath?: string;
    selectionStart?: number;
    selectionEnd?: number;
    quotedText?: string;
    parentId?: string;
  }): Promise<Comment> => {
    return new Promise((resolve) => {
      if (!currentSession) {
        throw new Error('No active session');
      }
      
      send({
        type: 'comment:add',
        entity_type: currentSession.entityType,
        entity_id: currentSession.entityId,
        content,
        ...options,
      });
      
      const comment: Comment = {
        id: `comment_${Date.now()}`,
        content,
        fieldPath: options?.fieldPath,
        selectionStart: options?.selectionStart,
        selectionEnd: options?.selectionEnd,
        quotedText: options?.quotedText,
        author: user,
        parentId: options?.parentId,
        status: 'open',
        replies: [],
        createdAt: new Date(),
      };
      
      resolve(comment);
    });
  }, [currentSession, user, send]);
  
  const resolveComment = useCallback(async (commentId: string) => {
    send({ type: 'comment:resolve', comment_id: commentId });
  }, [send]);
  
  // Lock functions
  const acquireLock = useCallback(async (fieldPath: string = ''): Promise<Lock | null> => {
    return new Promise((resolve) => {
      if (!currentSession) {
        resolve(null);
        return;
      }
      
      send({
        type: 'lock:acquire',
        entity_type: currentSession.entityType,
        entity_id: currentSession.entityId,
        field_path: fieldPath,
      });
      
      // Optimistic lock
      const lock: Lock = {
        id: `lock_${Date.now()}`,
        fieldPath,
        userId,
        user,
        lockType: 'exclusive',
        acquiredAt: new Date(),
        expiresAt: new Date(Date.now() + 30 * 60 * 1000),
      };
      
      setLocks(prev => [...prev, lock]);
      resolve(lock);
    });
  }, [currentSession, userId, user, send]);
  
  const releaseLock = useCallback(async (lockId: string) => {
    send({ type: 'lock:release', lock_id: lockId });
    setLocks(prev => prev.filter(l => l.id !== lockId));
  }, [send]);
  
  const isFieldLocked = useCallback((fieldPath: string): boolean => {
    return locks.some(l => 
      (l.fieldPath === fieldPath || l.fieldPath === '') && 
      l.userId !== userId
    );
  }, [locks, userId]);
  
  const getFieldLockHolder = useCallback((fieldPath: string): User | null => {
    const lock = locks.find(l => 
      (l.fieldPath === fieldPath || l.fieldPath === '') && 
      l.userId !== userId
    );
    return lock?.user || null;
  }, [locks, userId]);
  
  // Subscription functions
  const subscribe = useCallback((channel: string) => {
    send({ type: 'subscribe', channel });
  }, [send]);
  
  const unsubscribe = useCallback((channel: string) => {
    send({ type: 'unsubscribe', channel });
  }, [send]);
  
  // Event handling
  const on = useCallback((event: string, handler: (payload: unknown) => void) => {
    if (!eventHandlersRef.current.has(event)) {
      eventHandlersRef.current.set(event, new Set());
    }
    eventHandlersRef.current.get(event)!.add(handler);
    
    return () => {
      eventHandlersRef.current.get(event)?.delete(handler);
    };
  }, []);
  
  const emit = useCallback((event: string, payload: unknown) => {
    send({ type: event, payload });
  }, [send]);
  
  const value = useMemo<RealtimeContextValue>(() => ({
    isConnected,
    connectionId,
    reconnect,
    presence,
    updatePresence,
    updateLocation,
    currentSession,
    joinSession,
    leaveSession,
    participants,
    updateCursor,
    updateSelection,
    applyChange,
    pendingChanges,
    version,
    conflicts,
    resolveConflict,
    startTyping,
    stopTyping,
    typingUsers,
    comments,
    addComment,
    resolveComment,
    locks,
    acquireLock,
    releaseLock,
    isFieldLocked,
    getFieldLockHolder,
    subscribe,
    unsubscribe,
    on,
    emit,
  }), [
    isConnected, connectionId, reconnect, presence, updatePresence, updateLocation,
    currentSession, joinSession, leaveSession, participants, updateCursor, updateSelection,
    applyChange, pendingChanges, version, conflicts, resolveConflict,
    startTyping, stopTyping, typingUsers, comments, addComment, resolveComment,
    locks, acquireLock, releaseLock, isFieldLocked, getFieldLockHolder,
    subscribe, unsubscribe, on, emit,
  ]);
  
  return (
    <RealtimeContext.Provider value={value}>
      {children}
    </RealtimeContext.Provider>
  );
}

// ============================================================================
// Hooks
// ============================================================================

export function useRealtime() {
  const context = useContext(RealtimeContext);
  if (!context) {
    throw new Error('useRealtime must be used within a RealtimeProvider');
  }
  return context;
}

export function usePresence(entityType?: string, entityId?: string) {
  const { presence, updatePresence, updateLocation } = useRealtime();
  
  useEffect(() => {
    if (entityType && entityId) {
      updateLocation(window.location.pathname, entityType, entityId);
    }
  }, [entityType, entityId, updateLocation]);
  
  const onlineUsers = useMemo(() => {
    return Array.from(presence.values()).filter(p => 
      p.status !== 'offline'
    );
  }, [presence]);
  
  return {
    presence,
    onlineUsers,
    updateStatus: updatePresence,
  };
}

export function useCollaboration(entityType: string, entityId: string) {
  const realtime = useRealtime();
  
  useEffect(() => {
    realtime.joinSession(entityType, entityId);
    
    return () => {
      realtime.leaveSession();
    };
  }, [entityType, entityId, realtime.joinSession, realtime.leaveSession]);
  
  return {
    session: realtime.currentSession,
    participants: realtime.participants,
    version: realtime.version,
    pendingChanges: realtime.pendingChanges,
    applyChange: realtime.applyChange,
    updateCursor: realtime.updateCursor,
    updateSelection: realtime.updateSelection,
  };
}

export function useTypingIndicator(field: string) {
  const { startTyping, stopTyping, typingUsers } = useRealtime();
  
  const typing = useMemo(() => {
    return Array.from(typingUsers.values()).filter(t => t.field === field);
  }, [typingUsers, field]);
  
  const handleTyping = useCallback(() => {
    startTyping(field);
  }, [field, startTyping]);
  
  return {
    typingUsers: typing,
    onTyping: handleTyping,
    onBlur: stopTyping,
  };
}

export function useComments(entityType: string, entityId: string) {
  const { comments, addComment, resolveComment, subscribe, unsubscribe } = useRealtime();
  
  useEffect(() => {
    const channel = `comments:${entityType}:${entityId}`;
    subscribe(channel);
    return () => unsubscribe(channel);
  }, [entityType, entityId, subscribe, unsubscribe]);
  
  const threadedComments = useMemo(() => {
    return comments.filter(c => !c.parentId);
  }, [comments]);
  
  return {
    comments: threadedComments,
    addComment,
    resolveComment,
  };
}

export function useLocks(entityType: string, entityId: string) {
  const { locks, acquireLock, releaseLock, isFieldLocked, getFieldLockHolder } = useRealtime();
  
  const entityLocks = useMemo(() => {
    return locks;
  }, [locks]);
  
  return {
    locks: entityLocks,
    acquireLock,
    releaseLock,
    isFieldLocked,
    getFieldLockHolder,
  };
}

export function useRealtimeEvent(event: string, handler: (payload: unknown) => void) {
  const { on } = useRealtime();
  
  useEffect(() => {
    return on(event, handler);
  }, [event, handler, on]);
}

// ============================================================================
// Export Types
// ============================================================================

export type {
  User,
  PresenceData,
  CursorPosition,
  Selection,
  Participant,
  CollaborationSession,
  Change,
  Conflict,
  Comment,
  Lock,
  RealtimeMessage,
  RealtimeContextValue,
};
