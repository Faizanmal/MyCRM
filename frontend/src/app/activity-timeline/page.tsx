'use client';

import { useEffect, useState, useCallback } from 'react';
import {
  Activity,
  User,
  Users,
  Target,
  Briefcase,
  ListChecks,
  MessageSquare,
  Edit,
  Trash2,
  Plus,
  CheckCircle2,
  Eye,
  Upload,
  Share2,
  RefreshCw,
  Search,
  MoreVertical,
  ChevronDown,
  ChevronUp,
  Loader2,
  FileText,
  Link,
  Mail,
  AtSign,
} from 'lucide-react';
import { toast } from 'sonner';
import { format, formatDistanceToNow, isToday, isYesterday, isThisWeek } from 'date-fns';

import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { activityTimelineAPI, Activity as ActivityType } from '@/lib/enterprise-api';


const ACTION_ICONS: Record<string, React.ElementType> = {
  created: Plus,
  updated: Edit,
  deleted: Trash2,
  commented: MessageSquare,
  mentioned: AtSign,
  assigned: User,
  completed: CheckCircle2,
  shared: Share2,
  uploaded: Upload,
  status_changed: RefreshCw,
};

const ACTION_COLORS: Record<string, string> = {
  created: 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400',
  updated: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400',
  deleted: 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400',
  commented: 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400',
  mentioned: 'bg-pink-100 text-pink-600 dark:bg-pink-900/30 dark:text-pink-400',
  assigned: 'bg-amber-100 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400',
  completed: 'bg-emerald-100 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400',
  shared: 'bg-indigo-100 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400',
  uploaded: 'bg-cyan-100 text-cyan-600 dark:bg-cyan-900/30 dark:text-cyan-400',
  status_changed: 'bg-orange-100 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400',
};

const ENTITY_ICONS: Record<string, React.ElementType> = {
  contact: Users,
  lead: Target,
  opportunity: Briefcase,
  task: ListChecks,
  document: FileText,
  communication: Mail,
};

interface ActivityGroup {
  date: string;
  label: string;
  activities: ActivityType[];
}

export default function ActivityTimelinePage() {
  const [activities, setActivities] = useState<ActivityType[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [actionFilter, setActionFilter] = useState<string>('all');
  const [entityFilter, setEntityFilter] = useState<string>('all');
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({});
  const [refreshing, setRefreshing] = useState(false);

  const loadActivities = useCallback(async () => {
    try {
      setLoading(true);
      const data = await activityTimelineAPI.list({
        action: actionFilter !== 'all' ? actionFilter : undefined,
        content_type: entityFilter !== 'all' ? entityFilter : undefined,
      });
      setActivities(data.results || data || []);
    } catch (error) {
      console.error('Failed to load activities:', error);
      // Use mock data for demo
      setActivities([
        {
          id: '1',
          actor: { id: 1, username: 'john.doe', first_name: 'John', last_name: 'Doe' },
          action: 'created',
          content_type: 'lead',
          object_id: '123',
          target_name: 'Acme Corp - Enterprise Deal',
          description: 'Created new lead "Acme Corp - Enterprise Deal"',
          metadata: { value: 75000 },
          is_public: true,
          created_at: new Date().toISOString(),
        },
        {
          id: '2',
          actor: { id: 2, username: 'jane.smith', first_name: 'Jane', last_name: 'Smith' },
          action: 'commented',
          content_type: 'opportunity',
          object_id: '456',
          target_name: 'TechStart Expansion',
          description: 'Left a comment on opportunity "TechStart Expansion"',
          metadata: { comment_preview: 'Great progress on this deal! The client seems very interested.' },
          is_public: true,
          created_at: new Date(Date.now() - 3600000).toISOString(),
        },
        {
          id: '3',
          actor: { id: 1, username: 'john.doe', first_name: 'John', last_name: 'Doe' },
          action: 'status_changed',
          content_type: 'task',
          object_id: '789',
          target_name: 'Follow up with client',
          description: 'Changed task status from "In Progress" to "Completed"',
          metadata: { from_status: 'in_progress', to_status: 'completed' },
          is_public: true,
          created_at: new Date(Date.now() - 7200000).toISOString(),
        },
        {
          id: '4',
          actor: { id: 3, username: 'bob.wilson', first_name: 'Bob', last_name: 'Wilson' },
          action: 'assigned',
          content_type: 'lead',
          object_id: '321',
          target_name: 'GlobalTech Initiative',
          description: 'Assigned lead "GlobalTech Initiative" to Jane Smith',
          metadata: { assignee: 'Jane Smith' },
          is_public: true,
          created_at: new Date(Date.now() - 86400000).toISOString(),
        },
        {
          id: '5',
          actor: { id: 2, username: 'jane.smith', first_name: 'Jane', last_name: 'Smith' },
          action: 'uploaded',
          content_type: 'document',
          object_id: '654',
          target_name: 'Q4 Proposal.pdf',
          description: 'Uploaded document "Q4 Proposal.pdf"',
          metadata: { file_size: '2.4 MB', file_type: 'pdf' },
          is_public: true,
          created_at: new Date(Date.now() - 86400000 * 2).toISOString(),
        },
        {
          id: '6',
          actor: { id: 1, username: 'john.doe', first_name: 'John', last_name: 'Doe' },
          action: 'completed',
          content_type: 'opportunity',
          object_id: '987',
          target_name: 'Enterprise Software License',
          description: 'Won opportunity "Enterprise Software License" worth $125,000',
          metadata: { value: 125000, status: 'won' },
          is_public: true,
          created_at: new Date(Date.now() - 86400000 * 3).toISOString(),
        },
        {
          id: '7',
          actor: { id: 3, username: 'bob.wilson', first_name: 'Bob', last_name: 'Wilson' },
          action: 'mentioned',
          content_type: 'contact',
          object_id: '159',
          target_name: 'Sarah Johnson',
          description: 'Mentioned you in a note on contact "Sarah Johnson"',
          metadata: { mention_context: 'Need @john.doe to follow up on the contract details' },
          is_public: true,
          created_at: new Date(Date.now() - 86400000 * 5).toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  }, [actionFilter, entityFilter]);

  useEffect(() => {
    loadActivities();
  }, [loadActivities]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadActivities();
    setRefreshing(false);
    toast.success('Timeline refreshed');
  };

  const groupActivitiesByDate = (activities: ActivityType[]): ActivityGroup[] => {
    const groups: Record<string, ActivityType[]> = {};

    activities.forEach(activity => {
      const date = new Date(activity.created_at);
      let key: string;

      if (isToday(date)) {
        key = 'today';
      } else if (isYesterday(date)) {
        key = 'yesterday';
      } else if (isThisWeek(date)) {
        key = 'this_week';
      } else {
        key = format(date, 'yyyy-MM');
      }

      if (!groups[key]) {
        groups[key] = [];
      }
      groups[key].push(activity);
    });

    const order = ['today', 'yesterday', 'this_week'];
    const sortedKeys = Object.keys(groups).sort((a, b) => {
      const aIndex = order.indexOf(a);
      const bIndex = order.indexOf(b);
      if (aIndex !== -1 && bIndex !== -1) return aIndex - bIndex;
      if (aIndex !== -1) return -1;
      if (bIndex !== -1) return 1;
      return b.localeCompare(a);
    });

    return sortedKeys.map(key => ({
      date: key,
      label: key === 'today' ? 'Today' : key === 'yesterday' ? 'Yesterday' : key === 'this_week' ? 'This Week' : format(new Date(`${key  }-01`), 'MMMM yyyy'),
      activities: groups[key],
    }));
  };

  const filteredActivities = activities.filter(activity => {
    const matchesSearch = searchQuery === '' ||
      activity.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      activity.target_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      activity.actor.first_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      activity.actor.last_name.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesTab = activeTab === 'all' ||
      (activeTab === 'my' && activity.actor.username === 'john.doe') ||
      (activeTab === 'mentions' && activity.action === 'mentioned');

    return matchesSearch && matchesTab;
  });

  const groupedActivities = groupActivitiesByDate(filteredActivities);

  const toggleGroup = (date: string) => {
    setExpandedGroups(prev => ({
      ...prev,
      [date]: !prev[date],
    }));
  };

  const getInitials = (firstName: string, lastName: string) => {
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
  };

  const formatActivityTime = (dateStr: string) => {
    const date = new Date(dateStr);
    if (isToday(date)) {
      return formatDistanceToNow(date, { addSuffix: true });
    }
    return format(date, 'MMM d, h:mm a');
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-4 lg:p-6 space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-2xl lg:text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <Activity className="w-8 h-8 text-indigo-600" />
                Activity Timeline
              </h1>
              <p className="text-gray-500 dark:text-gray-400 mt-1">
                Track all activities across your CRM in one place
              </p>
            </div>
            <Button
              variant="outline"
              onClick={handleRefresh}
              disabled={refreshing}
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <Card className="bg-linear-to-br from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-indigo-100 dark:bg-indigo-900/50">
                    <Activity className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-indigo-700 dark:text-indigo-300">
                      {activities.length}
                    </div>
                    <div className="text-sm text-indigo-600 dark:text-indigo-400">Total Activities</div>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card className="bg-linear-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-green-100 dark:bg-green-900/50">
                    <Plus className="w-5 h-5 text-green-600 dark:text-green-400" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-green-700 dark:text-green-300">
                      {activities.filter(a => a.action === 'created').length}
                    </div>
                    <div className="text-sm text-green-600 dark:text-green-400">Created</div>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card className="bg-linear-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-purple-100 dark:bg-purple-900/50">
                    <MessageSquare className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-purple-700 dark:text-purple-300">
                      {activities.filter(a => a.action === 'commented').length}
                    </div>
                    <div className="text-sm text-purple-600 dark:text-purple-400">Comments</div>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card className="bg-linear-to-br from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-amber-100 dark:bg-amber-900/50">
                    <CheckCircle2 className="w-5 h-5 text-amber-600 dark:text-amber-400" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-amber-700 dark:text-amber-300">
                      {activities.filter(a => a.action === 'completed').length}
                    </div>
                    <div className="text-sm text-amber-600 dark:text-amber-400">Completed</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Filters */}
          <Card>
            <CardContent className="p-4">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <Input
                    placeholder="Search activities..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9"
                  />
                </div>
                <Select value={actionFilter} onValueChange={setActionFilter}>
                  <SelectTrigger className="w-full sm:w-48">
                    <SelectValue placeholder="Filter by action" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Actions</SelectItem>
                    <SelectItem value="created">Created</SelectItem>
                    <SelectItem value="updated">Updated</SelectItem>
                    <SelectItem value="commented">Commented</SelectItem>
                    <SelectItem value="assigned">Assigned</SelectItem>
                    <SelectItem value="completed">Completed</SelectItem>
                    <SelectItem value="status_changed">Status Changed</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={entityFilter} onValueChange={setEntityFilter}>
                  <SelectTrigger className="w-full sm:w-48">
                    <SelectValue placeholder="Filter by entity" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Entities</SelectItem>
                    <SelectItem value="contact">Contacts</SelectItem>
                    <SelectItem value="lead">Leads</SelectItem>
                    <SelectItem value="opportunity">Opportunities</SelectItem>
                    <SelectItem value="task">Tasks</SelectItem>
                    <SelectItem value="document">Documents</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList>
              <TabsTrigger value="all" className="flex items-center gap-2">
                <Activity className="w-4 h-4" />
                All Activity
              </TabsTrigger>
              <TabsTrigger value="my" className="flex items-center gap-2">
                <User className="w-4 h-4" />
                My Activity
              </TabsTrigger>
              <TabsTrigger value="mentions" className="flex items-center gap-2">
                <AtSign className="w-4 h-4" />
                Mentions
              </TabsTrigger>
            </TabsList>

            <TabsContent value={activeTab} className="mt-4">
              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
                </div>
              ) : groupedActivities.length === 0 ? (
                <Card className="border-dashed">
                  <CardContent className="flex flex-col items-center justify-center py-12">
                    <Activity className="w-12 h-12 text-gray-300 dark:text-gray-600 mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                      No activities found
                    </h3>
                    <p className="text-gray-500 dark:text-gray-400 text-center max-w-md">
                      Activities will appear here as you and your team work in the CRM.
                    </p>
                  </CardContent>
                </Card>
              ) : (
                <div className="space-y-6">
                  {groupedActivities.map((group) => (
                    <div key={group.date}>
                      <button
                        onClick={() => toggleGroup(group.date)}
                        className="flex items-center gap-2 mb-3 text-sm font-semibold text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
                      >
                        {expandedGroups[group.date] === false ? (
                          <ChevronDown className="w-4 h-4" />
                        ) : (
                          <ChevronUp className="w-4 h-4" />
                        )}
                        {group.label}
                        <Badge variant="secondary" className="ml-2">
                          {group.activities.length}
                        </Badge>
                      </button>

                      {expandedGroups[group.date] !== false && (
                        <div className="relative pl-8 space-y-0">
                          {/* Timeline line */}
                          <div className="absolute left-3.5 top-2 bottom-2 w-0.5 bg-gray-200 dark:bg-gray-700" />

                          {group.activities.map((activity) => {
                            const ActionIcon = ACTION_ICONS[activity.action] || Activity;
                            const EntityIcon = ENTITY_ICONS[activity.content_type] || FileText;

                            return (
                              <div key={activity.id} className="relative pb-6 last:pb-0">
                                {/* Timeline dot */}
                                <div className={`absolute -left-4 p-1.5 rounded-full ${ACTION_COLORS[activity.action] || 'bg-gray-100 text-gray-600'}`}>
                                  <ActionIcon className="w-3.5 h-3.5" />
                                </div>

                                <Card className="ml-4 hover:shadow-md transition-shadow">
                                  <CardContent className="p-4">
                                    <div className="flex items-start gap-3">
                                      <Avatar className="w-10 h-10">
                                        <AvatarImage src={activity.actor.avatar} />
                                        <AvatarFallback className="bg-linear-to-br from-indigo-500 to-purple-600 text-white text-sm">
                                          {getInitials(activity.actor.first_name, activity.actor.last_name)}
                                        </AvatarFallback>
                                      </Avatar>

                                      <div className="flex-1 min-w-0">
                                        <div className="flex items-start justify-between gap-2">
                                          <div>
                                            <span className="font-medium text-gray-900 dark:text-white">
                                              {activity.actor.first_name} {activity.actor.last_name}
                                            </span>
                                            <span className="text-gray-500 dark:text-gray-400 mx-1.5">•</span>
                                            <span className="text-sm text-gray-500 dark:text-gray-400">
                                              {formatActivityTime(activity.created_at)}
                                            </span>
                                          </div>
                                          <DropdownMenu>
                                            <DropdownMenuTrigger asChild>
                                              <Button variant="ghost" size="icon" className="h-8 w-8">
                                                <MoreVertical className="w-4 h-4" />
                                              </Button>
                                            </DropdownMenuTrigger>
                                            <DropdownMenuContent align="end">
                                              <DropdownMenuItem>
                                                <Eye className="w-4 h-4 mr-2" />
                                                View Details
                                              </DropdownMenuItem>
                                              <DropdownMenuItem>
                                                <Link className="w-4 h-4 mr-2" />
                                                Copy Link
                                              </DropdownMenuItem>
                                            </DropdownMenuContent>
                                          </DropdownMenu>
                                        </div>

                                        <p className="text-gray-700 dark:text-gray-300 mt-1">
                                          {activity.description}
                                        </p>

                                        {activity.target_name && (
                                          <div className="flex items-center gap-2 mt-2">
                                            <div className="flex items-center gap-1.5 px-2 py-1 rounded-md bg-gray-100 dark:bg-gray-800 text-sm">
                                              <EntityIcon className="w-3.5 h-3.5 text-gray-500" />
                                              <span className="text-gray-700 dark:text-gray-300">
                                                {activity.target_name}
                                              </span>
                                            </div>
                                            <Badge variant="outline" className="capitalize text-xs">
                                              {activity.content_type}
                                            </Badge>
                                          </div>
                                        )}

                                        {/* Metadata display */}
                                        {activity.metadata && Object.keys(activity.metadata).length > 0 && (
                                          <div className="mt-2 p-2 rounded-md bg-gray-50 dark:bg-gray-800/50 text-sm">
                                            {!!activity.metadata.comment_preview && (
                                              <p className="text-gray-600 dark:text-gray-400 italic">
                                                &ldquo;{activity.metadata.comment_preview as string}&rdquo;
                                              </p>
                                            )}
                                            {!!activity.metadata.value && (
                                              <p className="text-gray-600 dark:text-gray-400">
                                                Value: <span className="font-semibold text-green-600">${(activity.metadata.value as number).toLocaleString()}</span>
                                              </p>
                                            )}
                                            {!!activity.metadata.assignee && (
                                              <p className="text-gray-600 dark:text-gray-400">
                                                Assigned to: <span className="font-medium">{activity.metadata.assignee as string}</span>
                                              </p>
                                            )}
                                            {!!activity.metadata.mention_context && (
                                              <p className="text-gray-600 dark:text-gray-400 italic">
                                                &ldquo;{activity.metadata.mention_context as string}&rdquo;
                                              </p>
                                            )}
                                          </div>
                                        )}
                                      </div>
                                    </div>
                                  </CardContent>
                                </Card>
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}

