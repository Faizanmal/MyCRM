'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { activityAPI } from '@/lib/api';
import {
  BellIcon,
  ChatBubbleLeftIcon,
  UserIcon,
  AtSymbolIcon,
  PaperAirplaneIcon,
} from '@heroicons/react/24/outline';

interface Activity {
  id: string;
  activity_type: string;
  description: string;
  created_at: string;
  user_display_name?: string;
  metadata?: Record<string, unknown>;
}

interface Comment {
  id: string;
  content: string;
  created_at: string;
  user_display_name?: string;
  reply_count?: number;
}

interface ActivityFeedProps {
  entityModel: string;
  entityId: string;
  showComments?: boolean;
  maxHeight?: string;
}

export default function ActivityFeed({
  entityModel,
  entityId,
  showComments = true,
  maxHeight = '600px',
}: ActivityFeedProps) {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'activity' | 'comments'>('activity');
  const commentInputRef = useRef<HTMLTextAreaElement>(null);

  const loadActivities = useCallback(async () => {
    try {
      let response;
      if (entityModel && entityId) {
        response = await activityAPI.getEntityActivities(entityModel, entityId);
      } else {
        response = await activityAPI.getMyFeed();
      }
      setActivities(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to load activities:', error);
    } finally {
      setLoading(false);
    }
  }, [entityModel, entityId]);

  const loadComments = useCallback(async () => {
    if (!entityModel || !entityId) return;
    
    try {
      const response = await activityAPI.getComments(entityModel, entityId);
      setComments(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to load comments:', error);
    }
  }, [entityModel, entityId]);

  useEffect(() => {
    loadActivities();
    if (showComments && entityModel && entityId) {
      loadComments();
    }
  }, [entityModel, entityId, showComments, loadActivities, loadComments]);

  const handleAddComment = async () => {
    if (!newComment.trim() || !entityModel || !entityId) return;

    try {
      await activityAPI.addComment({
        content: newComment,
        content_type: entityModel,
        object_id: entityId,
      });
      setNewComment('');
      await loadComments();
      await loadActivities(); // Reload activities to show the new comment activity
    } catch (error) {
      console.error('Failed to add comment:', error);
      alert('Failed to add comment');
    }
  };

  const getActivityIcon = (activityType: string) => {
    switch (activityType) {
      case 'comment':
        return <ChatBubbleLeftIcon className="w-5 h-5 text-blue-600" />;
      case 'mention':
        return <AtSymbolIcon className="w-5 h-5 text-purple-600" />;
      case 'status_change':
        return <BellIcon className="w-5 h-5 text-green-600" />;
      case 'assignment':
        return <UserIcon className="w-5 h-5 text-orange-600" />;
      default:
        return <BellIcon className="w-5 h-5 text-gray-600" />;
    }
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (seconds < 60) return 'just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
    return date.toLocaleDateString();
  };

  const parseCommentContent = (content: string) => {
    // Simple mention parsing - replace @username with styled spans
    const parts = content.split(/(@\w+)/g);
    return parts.map((part, index) => {
      if (part.startsWith('@')) {
        return (
          <span key={index} className="text-blue-600 font-medium">
            {part}
          </span>
        );
      }
      return part;
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-40">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      {/* Tabs (if comments are enabled) */}
      {showComments && entityModel && entityId && (
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            <button
              onClick={() => setActiveTab('activity')}
              className={`py-4 px-6 text-sm font-medium border-b-2 ${
                activeTab === 'activity'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <BellIcon className="w-4 h-4 inline-block mr-2" />
              Activity ({activities.length})
            </button>
            <button
              onClick={() => setActiveTab('comments')}
              className={`py-4 px-6 text-sm font-medium border-b-2 ${
                activeTab === 'comments'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <ChatBubbleLeftIcon className="w-4 h-4 inline-block mr-2" />
              Comments ({comments.length})
            </button>
          </nav>
        </div>
      )}

      {/* Activity Tab */}
      {activeTab === 'activity' && (
        <div className="divide-y divide-gray-200" style={{ maxHeight, overflowY: 'auto' }}>
          {activities.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <BellIcon className="mx-auto h-12 w-12 text-gray-400 mb-3" />
              <p>No activity yet</p>
            </div>
          ) : (
            activities.map((activity) => (
              <div key={activity.id} className="p-4 hover:bg-gray-50">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    {getActivityIcon(activity.activity_type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="text-sm text-gray-900">
                          <span className="font-medium">{activity.user_display_name || 'Someone'}</span>
                          {' '}
                          <span className="text-gray-600">{activity.description}</span>
                        </p>
                        {activity.metadata && Object.keys(activity.metadata).length > 0 && (
                          <div className="mt-1 text-xs text-gray-500">
                            {JSON.stringify(activity.metadata).slice(0, 100)}
                          </div>
                        )}
                      </div>
                      <span className="text-xs text-gray-500 whitespace-nowrap ml-2">
                        {formatTimeAgo(activity.created_at)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Comments Tab */}
      {activeTab === 'comments' && showComments && (
        <div>
          {/* Comment Input */}
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-start space-x-3">
              <div className="shrink-0">
                <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                  <UserIcon className="w-5 h-5 text-gray-600" />
                </div>
              </div>
              <div className="flex-1">
                <textarea
                  ref={commentInputRef}
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  placeholder="Add a comment... Use @username to mention someone"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={2}
                />
                <div className="mt-2 flex items-center justify-between">
                  <p className="text-xs text-gray-500">
                    Tip: Use @username to mention team members
                  </p>
                  <button
                    onClick={handleAddComment}
                    disabled={!newComment.trim()}
                    className="inline-flex items-center px-3 py-1.5 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <PaperAirplaneIcon className="w-4 h-4 mr-1" />
                    Post
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Comments List */}
          <div className="divide-y divide-gray-200" style={{ maxHeight: '500px', overflowY: 'auto' }}>
            {comments.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <ChatBubbleLeftIcon className="mx-auto h-12 w-12 text-gray-400 mb-3" />
                <p>No comments yet</p>
                <p className="text-sm mt-1">Be the first to comment!</p>
              </div>
            ) : (
              comments.map((comment) => (
                <div key={comment.id} className="p-4 hover:bg-gray-50">
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-sm font-medium text-blue-600">
                          {comment.user_display_name?.charAt(0).toUpperCase() || '?'}
                        </span>
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-gray-900">
                          {comment.user_display_name || 'Anonymous'}
                        </span>
                        <span className="text-xs text-gray-500">
                          {formatTimeAgo(comment.created_at)}
                        </span>
                      </div>
                      <div className="mt-1 text-sm text-gray-700">
                        {parseCommentContent(comment.content)}
                      </div>
                      {(comment.reply_count ?? 0) > 0 && (
                        <button className="mt-2 text-xs text-blue-600 hover:text-blue-700">
                          {comment.reply_count} {comment.reply_count === 1 ? 'reply' : 'replies'}
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
