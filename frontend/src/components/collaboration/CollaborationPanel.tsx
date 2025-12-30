'use client';

import React, { useState, useEffect, useMemo } from 'react';
import {
  Users,
  MessageSquare,
  Lock,
  Unlock,
  AlertTriangle,
  Check,
  X,
  Send,
  Reply,
  MoreHorizontal,
  Circle,
  Wifi,
  WifiOff,
  Eye,
  Edit3,
  UserPlus,
  Clock,
  ChevronDown,
  ChevronUp,
  AtSign,
  Quote,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  useRealtime,
  useCollaboration,
  usePresence,
  useTypingIndicator,
  useComments,
  useLocks,
  type Participant,
  type Comment,
  type Lock as LockType,
  type Conflict,
} from '@/lib/realtime/RealtimeProvider';

// ============================================================================
// Connection Status
// ============================================================================

function ConnectionStatus() {
  const { isConnected, connectionId, reconnect } = useRealtime();
  
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className={`gap-2 ${isConnected ? 'text-green-600' : 'text-red-600'}`}
            onClick={() => !isConnected && reconnect()}
          >
            {isConnected ? (
              <>
                <Wifi className="h-4 w-4" />
                <span className="hidden sm:inline">Connected</span>
              </>
            ) : (
              <>
                <WifiOff className="h-4 w-4" />
                <span className="hidden sm:inline">Disconnected</span>
              </>
            )}
          </Button>
        </TooltipTrigger>
        <TooltipContent>
          {isConnected ? (
            <p>Connected: {connectionId?.slice(0, 12)}...</p>
          ) : (
            <p>Click to reconnect</p>
          )}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

// ============================================================================
// Presence Avatars
// ============================================================================

interface PresenceAvatarsProps {
  entityType: string;
  entityId: string;
  maxVisible?: number;
}

function PresenceAvatars({ 
  entityType, 
  entityId, 
  maxVisible = 5 
}: PresenceAvatarsProps) {
  const { onlineUsers } = usePresence(entityType, entityId);
  
  const visibleUsers = onlineUsers.slice(0, maxVisible);
  const extraCount = onlineUsers.length - maxVisible;
  
  const statusColors: Record<string, string> = {
    online: 'bg-green-500',
    busy: 'bg-red-500',
    away: 'bg-yellow-500',
    dnd: 'bg-red-600',
    offline: 'bg-gray-400',
  };
  
  return (
    <div className="flex items-center -space-x-2">
      {visibleUsers.map((user) => (
        <TooltipProvider key={user.userId}>
          <Tooltip>
            <TooltipTrigger asChild>
              <div className="relative">
                <Avatar className="h-8 w-8 border-2 border-background">
                  <AvatarImage src={`https://api.dicebear.com/7.x/initials/svg?seed=${user.userId}`} />
                  <AvatarFallback>
                    {user.userId.slice(0, 2).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <span 
                  className={`absolute bottom-0 right-0 h-2.5 w-2.5 rounded-full border-2 border-background ${statusColors[user.status]}`}
                />
              </div>
            </TooltipTrigger>
            <TooltipContent>
              <p className="font-medium">{user.userId}</p>
              <p className="text-xs text-muted-foreground capitalize">
                {user.status}
                {user.statusMessage && ` - ${user.statusMessage}`}
              </p>
              {user.isTyping && (
                <p className="text-xs text-blue-500">
                  Typing in {user.typingField}...
                </p>
              )}
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      ))}
      
      {extraCount > 0 && (
        <div className="flex h-8 w-8 items-center justify-center rounded-full border-2 border-background bg-muted text-xs font-medium">
          +{extraCount}
        </div>
      )}
    </div>
  );
}

// ============================================================================
// Participant List
// ============================================================================

interface ParticipantListProps {
  participants: Participant[];
  compact?: boolean;
}

function ParticipantList({ participants, compact = false }: ParticipantListProps) {
  const roleIcons: Record<string, React.ReactNode> = {
    owner: <Edit3 className="h-3 w-3" />,
    editor: <Edit3 className="h-3 w-3" />,
    commenter: <MessageSquare className="h-3 w-3" />,
    viewer: <Eye className="h-3 w-3" />,
  };
  
  const statusColors: Record<string, string> = {
    active: 'bg-green-500',
    idle: 'bg-yellow-500',
    away: 'bg-orange-500',
    disconnected: 'bg-gray-400',
  };
  
  if (compact) {
    return (
      <div className="flex flex-wrap gap-2">
        {participants.map((participant) => (
          <TooltipProvider key={participant.userId}>
            <Tooltip>
              <TooltipTrigger asChild>
                <div 
                  className="flex items-center gap-1 rounded-full px-2 py-1 text-xs"
                  style={{ backgroundColor: `${participant.color}20`, color: participant.color }}
                >
                  <span 
                    className={`h-2 w-2 rounded-full ${statusColors[participant.status]}`}
                  />
                  {participant.user.name.split(' ')[0]}
                </div>
              </TooltipTrigger>
              <TooltipContent>
                <p>{participant.user.name}</p>
                <p className="text-xs capitalize">{participant.role}</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        ))}
      </div>
    );
  }
  
  return (
    <div className="space-y-2">
      {participants.map((participant) => (
        <div 
          key={participant.userId}
          className="flex items-center justify-between rounded-lg border p-2"
          style={{ borderColor: participant.color }}
        >
          <div className="flex items-center gap-3">
            <div className="relative">
              <Avatar className="h-8 w-8">
                <AvatarImage src={participant.user.avatar} />
                <AvatarFallback style={{ backgroundColor: participant.color, color: 'white' }}>
                  {participant.user.name.slice(0, 2).toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <span 
                className={`absolute bottom-0 right-0 h-2.5 w-2.5 rounded-full border-2 border-background ${statusColors[participant.status]}`}
              />
            </div>
            
            <div>
              <p className="text-sm font-medium">{participant.user.name}</p>
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                {roleIcons[participant.role]}
                <span className="capitalize">{participant.role}</span>
              </div>
            </div>
          </div>
          
          {participant.cursor && (
            <Badge variant="secondary" className="text-xs">
              Editing: {participant.cursor.field}
            </Badge>
          )}
        </div>
      ))}
    </div>
  );
}

// ============================================================================
// Typing Indicator
// ============================================================================

interface TypingIndicatorProps {
  field: string;
}

function TypingIndicator({ field }: TypingIndicatorProps) {
  const { typingUsers } = useTypingIndicator(field);
  
  if (typingUsers.length === 0) return null;
  
  const names = typingUsers.map(t => t.userId.slice(0, 8));
  let text: string;
  
  if (names.length === 1) {
    text = `${names[0]} is typing...`;
  } else if (names.length === 2) {
    text = `${names[0]} and ${names[1]} are typing...`;
  } else {
    text = `${names.length} people are typing...`;
  }
  
  return (
    <div className="flex items-center gap-2 text-xs text-muted-foreground">
      <div className="flex gap-1">
        <span className="animate-bounce">.</span>
        <span className="animate-bounce" style={{ animationDelay: '0.1s' }}>.</span>
        <span className="animate-bounce" style={{ animationDelay: '0.2s' }}>.</span>
      </div>
      <span>{text}</span>
    </div>
  );
}

// ============================================================================
// Cursors Overlay
// ============================================================================

interface CursorsOverlayProps {
  participants: Participant[];
  containerRef: React.RefObject<HTMLElement>;
}

function CursorsOverlay({ participants, containerRef }: CursorsOverlayProps) {
  // Filter participants with cursor positions
  const withCursors = participants.filter(p => p.cursor);
  
  if (withCursors.length === 0) return null;
  
  return (
    <div className="pointer-events-none absolute inset-0">
      {withCursors.map((participant) => (
        <div
          key={participant.userId}
          className="absolute flex items-start"
          style={{
            // Position would be calculated based on cursor offset
            top: `${(participant.cursor?.offset || 0) % 100}%`,
            left: 0,
          }}
        >
          {/* Cursor line */}
          <div 
            className="h-5 w-0.5"
            style={{ backgroundColor: participant.color }}
          />
          
          {/* Name label */}
          <div 
            className="ml-0.5 rounded px-1 py-0.5 text-xs text-white"
            style={{ backgroundColor: participant.color }}
          >
            {participant.user.name.split(' ')[0]}
          </div>
        </div>
      ))}
    </div>
  );
}

// ============================================================================
// Conflict Resolution Dialog
// ============================================================================

interface ConflictResolutionProps {
  conflict: Conflict;
  onResolve: (value: any) => void;
  onDismiss: () => void;
}

function ConflictResolution({ conflict, onResolve, onDismiss }: ConflictResolutionProps) {
  return (
    <Card className="border-yellow-500">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-yellow-500" />
          <CardTitle className="text-base">Conflict Detected</CardTitle>
        </div>
        <CardDescription>
          Changes conflict with another user's edits. Choose how to resolve.
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <div className="grid gap-3 sm:grid-cols-2">
          <div className="space-y-2">
            <p className="text-xs font-medium text-muted-foreground">Your Change</p>
            <div className="rounded-lg border bg-blue-50 p-3 dark:bg-blue-950">
              <pre className="text-sm whitespace-pre-wrap">
                {JSON.stringify(conflict.localChange?.newValue, null, 2)}
              </pre>
            </div>
          </div>
          
          <div className="space-y-2">
            <p className="text-xs font-medium text-muted-foreground">Their Change</p>
            <div className="rounded-lg border bg-orange-50 p-3 dark:bg-orange-950">
              <pre className="text-sm whitespace-pre-wrap">
                {JSON.stringify(conflict.remoteChange?.newValue, null, 2)}
              </pre>
            </div>
          </div>
        </div>
        
        {Boolean(conflict.resolvedValue) && (
          <div className="space-y-2">
            <p className="text-xs font-medium text-muted-foreground">
              Auto-merged Result ({conflict.resolution})
            </p>
            <div className="rounded-lg border bg-green-50 p-3 dark:bg-green-950">
              <pre className="text-sm whitespace-pre-wrap">
                {JSON.stringify(conflict.resolvedValue, null, 2)}
              </pre>
            </div>
          </div>
        )}
        
        <div className="flex flex-wrap gap-2">
          <Button
            size="sm"
            onClick={() => onResolve(conflict.localChange?.newValue)}
          >
            Use My Version
          </Button>
          <Button
            size="sm"
            variant="secondary"
            onClick={() => onResolve(conflict.remoteChange?.newValue)}
          >
            Use Their Version
          </Button>
          {Boolean(conflict.resolvedValue) && (
            <Button
              size="sm"
              variant="outline"
              onClick={() => onResolve(conflict.resolvedValue)}
            >
              Accept Merge
            </Button>
          )}
          <Button size="sm" variant="ghost" onClick={onDismiss}>
            Dismiss
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

// ============================================================================
// Lock Indicator
// ============================================================================

interface LockIndicatorProps {
  fieldPath: string;
  entityType: string;
  entityId: string;
}

function LockIndicator({ fieldPath, entityType, entityId }: LockIndicatorProps) {
  const { isFieldLocked, getFieldLockHolder, acquireLock, releaseLock, locks } = useLocks(entityType, entityId);
  
  const isLocked = isFieldLocked(fieldPath);
  const lockHolder = getFieldLockHolder(fieldPath);
  const myLock = locks.find(l => l.fieldPath === fieldPath && l.user);
  
  if (!isLocked && !myLock) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0"
              onClick={() => acquireLock(fieldPath)}
            >
              <Unlock className="h-3 w-3 text-muted-foreground" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>Click to lock for editing</TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }
  
  if (myLock) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0"
              onClick={() => releaseLock(myLock.id)}
            >
              <Lock className="h-3 w-3 text-blue-500" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>Locked by you. Click to release.</TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }
  
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div className="flex h-6 w-6 items-center justify-center">
            <Lock className="h-3 w-3 text-red-500" />
          </div>
        </TooltipTrigger>
        <TooltipContent>
          Locked by {lockHolder?.name || 'another user'}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

// ============================================================================
// Comments Panel
// ============================================================================

interface CommentItemProps {
  comment: Comment;
  onResolve: (id: string) => void;
  onReply: (id: string) => void;
  depth?: number;
}

function CommentItem({ comment, onResolve, onReply, depth = 0 }: CommentItemProps) {
  const [showReplies, setShowReplies] = useState(true);
  
  return (
    <div className={`space-y-2 ${depth > 0 ? 'ml-6 border-l pl-4' : ''}`}>
      <div className={`rounded-lg border p-3 ${comment.status === 'resolved' ? 'bg-muted opacity-60' : ''}`}>
        <div className="mb-2 flex items-start justify-between">
          <div className="flex items-center gap-2">
            <Avatar className="h-6 w-6">
              <AvatarImage src={comment.author.avatar} />
              <AvatarFallback className="text-xs">
                {comment.author.name.slice(0, 2).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <div>
              <p className="text-sm font-medium">{comment.author.name}</p>
              <p className="text-xs text-muted-foreground">
                {new Date(comment.createdAt).toLocaleString()}
              </p>
            </div>
          </div>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => onReply(comment.id)}>
                <Reply className="mr-2 h-4 w-4" />
                Reply
              </DropdownMenuItem>
              {comment.status === 'open' && (
                <DropdownMenuItem onClick={() => onResolve(comment.id)}>
                  <Check className="mr-2 h-4 w-4" />
                  Resolve
                </DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
        
        {comment.quotedText && (
          <div className="mb-2 flex items-start gap-2 rounded bg-muted p-2 text-sm">
            <Quote className="h-4 w-4 text-muted-foreground" />
            <span className="italic text-muted-foreground">{comment.quotedText}</span>
          </div>
        )}
        
        <p className="text-sm">{comment.content}</p>
        
        {comment.status === 'resolved' && (
          <div className="mt-2 flex items-center gap-1 text-xs text-green-600">
            <Check className="h-3 w-3" />
            Resolved
            {comment.resolvedBy && ` by ${comment.resolvedBy.name}`}
          </div>
        )}
      </div>
      
      {comment.replies.length > 0 && (
        <>
          <Button
            variant="ghost"
            size="sm"
            className="gap-1 text-xs"
            onClick={() => setShowReplies(!showReplies)}
          >
            {showReplies ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
            {comment.replies.length} {comment.replies.length === 1 ? 'reply' : 'replies'}
          </Button>
          
          {showReplies && comment.replies.map((reply) => (
            <CommentItem
              key={reply.id}
              comment={reply}
              onResolve={onResolve}
              onReply={onReply}
              depth={depth + 1}
            />
          ))}
        </>
      )}
    </div>
  );
}

interface CommentsPanelProps {
  entityType: string;
  entityId: string;
}

function CommentsPanel({ entityType, entityId }: CommentsPanelProps) {
  const { comments, addComment, resolveComment } = useComments(entityType, entityId);
  const [newComment, setNewComment] = useState('');
  const [replyingTo, setReplyingTo] = useState<string | null>(null);
  
  const handleSubmit = async () => {
    if (!newComment.trim()) return;
    
    await addComment(newComment, {
      parentId: replyingTo || undefined,
    });
    
    setNewComment('');
    setReplyingTo(null);
  };
  
  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-base">
            <MessageSquare className="h-4 w-4" />
            Comments
          </CardTitle>
          <Badge variant="secondary">{comments.length}</Badge>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Comment list */}
        <div className="max-h-[400px] space-y-4 overflow-auto">
          {comments.length === 0 ? (
            <p className="py-4 text-center text-sm text-muted-foreground">
              No comments yet
            </p>
          ) : (
            comments.map((comment) => (
              <CommentItem
                key={comment.id}
                comment={comment}
                onResolve={resolveComment}
                onReply={setReplyingTo}
              />
            ))
          )}
        </div>
        
        {/* New comment */}
        <div className="space-y-2 border-t pt-4">
          {replyingTo && (
            <div className="flex items-center justify-between rounded bg-muted px-2 py-1 text-xs">
              <span>Replying to comment...</span>
              <Button
                variant="ghost"
                size="sm"
                className="h-5 w-5 p-0"
                onClick={() => setReplyingTo(null)}
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
          )}
          
          <div className="flex gap-2">
            <Textarea
              placeholder="Add a comment..."
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              className="min-h-[60px] flex-1 resize-none"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                  handleSubmit();
                }
              }}
            />
            <Button size="sm" onClick={handleSubmit} disabled={!newComment.trim()}>
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// ============================================================================
// Collaboration Panel (Main Component)
// ============================================================================

interface CollaborationPanelProps {
  entityType: string;
  entityId: string;
}

function CollaborationPanel({ entityType, entityId }: CollaborationPanelProps) {
  const { session, participants, version } = useCollaboration(entityType, entityId);
  const { conflicts, resolveConflict } = useRealtime();
  const [activeTab, setActiveTab] = useState('participants');
  
  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-base">
            <Users className="h-4 w-4" />
            Collaboration
          </CardTitle>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="font-mono text-xs">
              v{version}
            </Badge>
            <ConnectionStatus />
          </div>
        </div>
        <CardDescription>
          {participants.length} {participants.length === 1 ? 'person' : 'people'} editing
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Conflicts */}
        {conflicts.map((conflict) => (
          <ConflictResolution
            key={conflict.id}
            conflict={conflict}
            onResolve={(value) => resolveConflict(conflict.id, value)}
            onDismiss={() => resolveConflict(conflict.id, conflict.resolvedValue)}
          />
        ))}
        
        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="participants">
              <Users className="mr-1 h-3 w-3" />
              Participants
            </TabsTrigger>
            <TabsTrigger value="comments">
              <MessageSquare className="mr-1 h-3 w-3" />
              Comments
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="participants" className="mt-4">
            <ParticipantList participants={participants} />
            
            <Button variant="outline" size="sm" className="mt-4 w-full gap-2">
              <UserPlus className="h-4 w-4" />
              Invite Collaborators
            </Button>
          </TabsContent>
          
          <TabsContent value="comments" className="mt-4">
            <CommentsPanel entityType={entityType} entityId={entityId} />
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}

// ============================================================================
// Collaborative Field Wrapper
// ============================================================================

interface CollaborativeFieldProps {
  fieldPath: string;
  entityType: string;
  entityId: string;
  children: React.ReactNode;
}

function CollaborativeField({ 
  fieldPath, 
  entityType, 
  entityId, 
  children 
}: CollaborativeFieldProps) {
  const { participants } = useCollaboration(entityType, entityId);
  const { onTyping, onBlur, typingUsers } = useTypingIndicator(fieldPath);
  
  // Find participants editing this field
  const editingParticipants = participants.filter(
    p => p.cursor?.field === fieldPath || p.selection?.field === fieldPath
  );
  
  return (
    <div className="relative">
      {/* Editing indicators */}
      {editingParticipants.length > 0 && (
        <div className="absolute -left-2 top-0 flex flex-col gap-1">
          {editingParticipants.map((p) => (
            <div
              key={p.userId}
              className="h-full w-1 rounded"
              style={{ backgroundColor: p.color }}
            />
          ))}
        </div>
      )}
      
      {/* Field content */}
      <div
        onFocus={onTyping}
        onBlur={onBlur}
        onKeyDown={onTyping}
      >
        {children}
      </div>
      
      {/* Typing indicator */}
      <TypingIndicator field={fieldPath} />
      
      {/* Lock indicator */}
      <div className="absolute right-2 top-2">
        <LockIndicator 
          fieldPath={fieldPath} 
          entityType={entityType} 
          entityId={entityId} 
        />
      </div>
    </div>
  );
}

// ============================================================================
// Export All Components
// ============================================================================

export {
  ConnectionStatus,
  PresenceAvatars,
  ParticipantList,
  TypingIndicator,
  CursorsOverlay,
  ConflictResolution,
  LockIndicator,
  CommentsPanel,
  CollaborationPanel,
  CollaborativeField,
};
