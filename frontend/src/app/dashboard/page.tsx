'use client';

import { useEffect, useState, useCallback } from 'react';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { 
  Users, 
  UserPlus, 
  TrendingUp, 
  DollarSign,
  ArrowUpRight,
  ArrowDownRight,
  Phone,
  Mail,
  Calendar,
  CheckCircle2,
  AlertCircle,
  Clock,
  Target,
  RefreshCw
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { dashboardAPI, contactsAPI, leadsAPI, opportunitiesAPI, tasksAPI } from '@/lib/api';
import { toast } from 'sonner';

interface DashboardMetrics {
  contacts: {
    total: number;
    new_this_month: number;
  };
  leads: {
    total: number;
    converted: number;
    conversion_rate: number;
  };
  opportunities: {
    total: number;
    pipeline_value: number;
  };
  tasks: {
    total: number;
    completed: number;
    overdue: number;
  };
}

interface PipelineStage {
  stage: string;
  stage_display: string;
  count: number;
  total_value: number;
}

interface Task {
  id: number;
  title: string;
  description?: string;
  priority: 'low' | 'medium' | 'high';
  status: string;
  due_date: string;
  related_to?: string;
}

interface Opportunity {
  id: number;
  name: string;
  amount: number;
  stage: string;
  closed_at?: string;
  company_name?: string;
}

interface Activity {
  id: number;
  action_type: string;
  description: string;
  created_at: string;
}

interface StatCardProps {
  title: string;
  value: string | number;
  change?: string;
  trend?: 'up' | 'down';
  icon: React.ElementType;
  loading?: boolean;
}

function StatCard({ title, value, change, trend = 'up', icon: Icon, loading }: StatCardProps) {
  if (loading) {
    return (
      <Card className="modern-card">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-8 w-8 rounded-xl" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-8 w-20 mb-2" />
          <Skeleton className="h-4 w-32" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="modern-card hover:scale-105 transition-transform duration-300 group">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
        <div className={`p-2 rounded-xl ${trend === 'up' ? 'bg-green-500/10 text-green-600 dark:bg-green-500/20' : 'bg-blue-500/10 text-blue-600 dark:bg-blue-500/20'} group-hover:scale-110 transition-transform`}>
          <Icon className="h-4 w-4" />
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold gradient-text">{value}</div>
        {change && (
          <p className="text-xs flex items-center mt-2">
            {trend === 'up' ? (
              <ArrowUpRight className="w-4 h-4 text-green-600 dark:text-green-400 mr-1" />
            ) : (
              <ArrowDownRight className="w-4 h-4 text-red-600 dark:text-red-400 mr-1" />
            )}
            <span className={`font-semibold ${trend === 'up' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
              {change}
            </span>
            <span className="text-muted-foreground ml-1">from last month</span>
          </p>
        )}
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [pipeline, setPipeline] = useState<PipelineStage[]>([]);
  const [recentActivities, setRecentActivities] = useState<Activity[]>([]);
  const [upcomingTasks, setUpcomingTasks] = useState<Task[]>([]);
  const [recentWins, setRecentWins] = useState<Opportunity[]>([]);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = useCallback(async (showRefreshing = false) => {
    try {
      if (showRefreshing) setIsRefreshing(true);
      setError(null);

      // Fetch all data in parallel
      const [
        metricsRes,
        contactsRes,
        leadsRes,
        opportunitiesRes,
        tasksRes,
        wonOpportunitiesRes
      ] = await Promise.allSettled([
        dashboardAPI.getMetrics().catch(() => null),
        contactsAPI.getContacts({ page_size: 1 }),
        leadsAPI.getLeads({ page_size: 1 }),
        opportunitiesAPI.getOpportunities({ page_size: 1 }),
        tasksAPI.getTasks({ status__in: 'pending,in_progress', ordering: 'due_date', page_size: 5 }),
        opportunitiesAPI.getOpportunities({ stage: 'won', ordering: '-updated_at', page_size: 5 })
      ]);

      // Build metrics from API responses or fall back to counts
      const buildMetrics = (): DashboardMetrics => {
        if (metricsRes.status === 'fulfilled' && metricsRes.value) {
          return metricsRes.value;
        }

        // Build from individual responses
        const contactCount = contactsRes.status === 'fulfilled' ? 
          (contactsRes.value?.count || contactsRes.value?.results?.length || 0) : 0;
        const leadCount = leadsRes.status === 'fulfilled' ? 
          (leadsRes.value?.count || leadsRes.value?.results?.length || 0) : 0;
        const oppCount = opportunitiesRes.status === 'fulfilled' ? 
          (opportunitiesRes.value?.count || opportunitiesRes.value?.results?.length || 0) : 0;
        const taskCount = tasksRes.status === 'fulfilled' ? 
          (tasksRes.value?.count || tasksRes.value?.results?.length || 0) : 0;

        return {
          contacts: { total: contactCount, new_this_month: 0 },
          leads: { total: leadCount, converted: 0, conversion_rate: 0 },
          opportunities: { total: oppCount, pipeline_value: 0 },
          tasks: { total: taskCount, completed: 0, overdue: 0 }
        };
      };

      setMetrics(buildMetrics());

      // Set upcoming tasks
      if (tasksRes.status === 'fulfilled' && tasksRes.value?.results) {
        setUpcomingTasks(tasksRes.value.results);
      }

      // Set recent wins
      if (wonOpportunitiesRes.status === 'fulfilled' && wonOpportunitiesRes.value?.results) {
        setRecentWins(wonOpportunitiesRes.value.results);
      }

      // Try to get pipeline data
      try {
        const pipelineRes = await dashboardAPI.getSalesPipeline();
        if (pipelineRes && Array.isArray(pipelineRes)) {
          setPipeline(pipelineRes);
        }
      } catch {
        // Use default pipeline stages
        setPipeline([
          { stage: 'prospecting', stage_display: 'Prospecting', count: 0, total_value: 0 },
          { stage: 'qualification', stage_display: 'Qualification', count: 0, total_value: 0 },
          { stage: 'proposal', stage_display: 'Proposal', count: 0, total_value: 0 },
          { stage: 'negotiation', stage_display: 'Negotiation', count: 0, total_value: 0 },
        ]);
      }

      // Try to get activities
      try {
        const activitiesRes = await dashboardAPI.getRecentActivities(5);
        if (activitiesRes?.results) {
          setRecentActivities(activitiesRes.results);
        }
      } catch {
        setRecentActivities([]);
      }

    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load dashboard data');
      toast.error('Failed to load dashboard data');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  const handleRefresh = () => {
    fetchDashboardData(true);
  };

  const formatCurrency = (value: number) => {
    if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `$${(value / 1000).toFixed(1)}K`;
    return `$${value}`;
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  };

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'high': return <Badge variant="destructive">High</Badge>;
      case 'medium': return <Badge variant="secondary">Medium</Badge>;
      default: return <Badge variant="outline">Low</Badge>;
    }
  };

  if (error && !metrics) {
    return (
      <ProtectedRoute>
        <MainLayout>
          <div className="p-6">
            <Card className="p-8 text-center">
              <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <h2 className="text-xl font-semibold mb-2">Failed to Load Dashboard</h2>
              <p className="text-muted-foreground mb-4">{error}</p>
              <Button onClick={handleRefresh}>
                <RefreshCw className="w-4 h-4 mr-2" />
                Try Again
              </Button>
            </Card>
          </div>
        </MainLayout>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="space-y-6">
          {/* Welcome Section */}
          <div className="relative overflow-hidden modern-card bg-linear-to-br from-blue-600 via-purple-600 to-pink-600 dark:from-blue-700 dark:via-purple-700 dark:to-pink-700 p-8 text-white shadow-2xl">
            <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -mr-32 -mt-32 blur-3xl"></div>
            <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/10 rounded-full -ml-24 -mb-24 blur-3xl"></div>
            <div className="relative z-10 flex justify-between items-start">
              <div>
                <h2 className="text-3xl lg:text-4xl font-bold mb-3 flex items-center gap-3">
                  Welcome back, {user?.first_name || user?.username || 'User'}! 
                  <span className="inline-block animate-bounce">👋</span>
                </h2>
                <p className="text-blue-50 text-lg">Here&apos;s what&apos;s happening with your CRM today.</p>
              </div>
              <Button 
                variant="secondary" 
                size="sm" 
                onClick={handleRefresh}
                disabled={isRefreshing}
                className="bg-white/20 hover:bg-white/30 text-white border-0"
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
            <StatCard
              title="Total Contacts"
              value={metrics?.contacts.total.toLocaleString() || '0'}
              change={metrics?.contacts.new_this_month ? `+${metrics.contacts.new_this_month} new` : undefined}
              trend="up"
              icon={Users}
              loading={isLoading}
            />
            <StatCard
              title="Active Leads"
              value={metrics?.leads.total.toLocaleString() || '0'}
              change={metrics?.leads.conversion_rate ? `${metrics.leads.conversion_rate}% converted` : undefined}
              trend="up"
              icon={UserPlus}
              loading={isLoading}
            />
            <StatCard
              title="Opportunities"
              value={metrics?.opportunities.total.toLocaleString() || '0'}
              trend="up"
              icon={TrendingUp}
              loading={isLoading}
            />
            <StatCard
              title="Pipeline Value"
              value={formatCurrency(metrics?.opportunities.pipeline_value || 0)}
              trend="up"
              icon={DollarSign}
              loading={isLoading}
            />
          </div>

          {/* Charts and Analytics */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Sales Pipeline */}
            <Card>
              <CardHeader>
                <CardTitle>Sales Pipeline</CardTitle>
                <CardDescription>Current opportunities by stage</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {isLoading ? (
                  [...Array(4)].map((_, i) => (
                    <div key={i} className="space-y-2">
                      <Skeleton className="h-4 w-full" />
                      <Skeleton className="h-2 w-full" />
                    </div>
                  ))
                ) : pipeline.length > 0 ? (
                  pipeline.map((stage, index) => {
                    const totalValue = pipeline.reduce((sum, s) => sum + s.total_value, 0);
                    const percentage = totalValue > 0 ? (stage.total_value / totalValue) * 100 : 0;
                    const colors = ['bg-blue-600', 'bg-indigo-600', 'bg-purple-600', 'bg-green-600', 'bg-yellow-600'];
                    
                    return (
                      <div key={stage.stage} className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="font-medium">{stage.stage_display}</span>
                          <span className="text-muted-foreground">
                            {stage.count} deal{stage.count !== 1 ? 's' : ''} • {formatCurrency(stage.total_value)}
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className={`${colors[index % colors.length]} h-2 rounded-full transition-all duration-500`} 
                            style={{ width: `${Math.max(percentage, 2)}%` }}
                          ></div>
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <p className="text-muted-foreground text-center py-4">No pipeline data available</p>
                )}
              </CardContent>
            </Card>

            {/* Recent Wins */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Wins</CardTitle>
                <CardDescription>Deals closed recently</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {isLoading ? (
                  [...Array(3)].map((_, i) => (
                    <div key={i} className="flex items-start space-x-3">
                      <Skeleton className="w-10 h-10 rounded-full" />
                      <div className="flex-1">
                        <Skeleton className="h-4 w-3/4 mb-2" />
                        <Skeleton className="h-3 w-1/2" />
                      </div>
                    </div>
                  ))
                ) : recentWins.length > 0 ? (
                  recentWins.map((opp) => (
                    <div key={opp.id} className="flex items-start space-x-3">
                      <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center shrink-0">
                        <CheckCircle2 className="w-5 h-5 text-green-600" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{opp.name}</p>
                        <p className="text-xs text-muted-foreground">
                          {formatCurrency(opp.amount)} 
                          {opp.closed_at && ` • Closed ${formatTimeAgo(opp.closed_at)}`}
                        </p>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-muted-foreground text-center py-4">No recent wins yet</p>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Activity and Tasks */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Recent Activities */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Activities</CardTitle>
                <CardDescription>Latest updates from your team</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {isLoading ? (
                  [...Array(5)].map((_, i) => (
                    <div key={i} className="flex items-center space-x-4">
                      <Skeleton className="w-2 h-2 rounded-full" />
                      <div className="flex-1">
                        <Skeleton className="h-4 w-3/4 mb-1" />
                        <Skeleton className="h-3 w-1/2" />
                      </div>
                      <Skeleton className="h-3 w-16" />
                    </div>
                  ))
                ) : recentActivities.length > 0 ? (
                  recentActivities.map((activity) => {
                    const colors: Record<string, string> = {
                      'create': 'bg-green-500',
                      'update': 'bg-blue-500',
                      'delete': 'bg-red-500',
                      'convert': 'bg-purple-500',
                      'complete': 'bg-yellow-500',
                    };
                    const colorClass = colors[activity.action_type] || 'bg-gray-500';

                    return (
                      <div key={activity.id} className="flex items-center space-x-4">
                        <div className={`w-2 h-2 ${colorClass} rounded-full shrink-0`}></div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium capitalize">{activity.action_type.replace('_', ' ')}</p>
                          <p className="text-xs text-muted-foreground truncate">{activity.description}</p>
                        </div>
                        <span className="text-xs text-muted-foreground shrink-0">
                          {formatTimeAgo(activity.created_at)}
                        </span>
                      </div>
                    );
                  })
                ) : (
                  <p className="text-muted-foreground text-center py-4">No recent activities</p>
                )}
              </CardContent>
            </Card>

            {/* Upcoming Tasks */}
            <Card>
              <CardHeader>
                <CardTitle>Upcoming Tasks</CardTitle>
                <CardDescription>Your priorities for today and tomorrow</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {isLoading ? (
                  [...Array(5)].map((_, i) => (
                    <div key={i} className="flex items-center justify-between">
                      <div className="flex items-center space-x-3 flex-1">
                        <Skeleton className="w-2 h-2 rounded-full" />
                        <div className="flex-1">
                          <Skeleton className="h-4 w-3/4 mb-1" />
                          <Skeleton className="h-3 w-1/2" />
                        </div>
                      </div>
                      <Skeleton className="h-5 w-16" />
                    </div>
                  ))
                ) : upcomingTasks.length > 0 ? (
                  upcomingTasks.map((task) => {
                    const priorityColors: Record<string, string> = {
                      'high': 'bg-red-500',
                      'medium': 'bg-yellow-500',
                      'low': 'bg-green-500',
                    };

                    return (
                      <div key={task.id} className="flex items-center justify-between">
                        <div className="flex items-center space-x-3 flex-1 min-w-0">
                          <div className={`w-2 h-2 ${priorityColors[task.priority] || 'bg-gray-500'} rounded-full shrink-0`}></div>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium truncate">{task.title}</p>
                            <p className="text-xs text-muted-foreground truncate">
                              {task.related_to || `Due: ${new Date(task.due_date).toLocaleDateString()}`}
                            </p>
                          </div>
                        </div>
                        {getPriorityBadge(task.priority)}
                      </div>
                    );
                  })
                ) : (
                  <p className="text-muted-foreground text-center py-4">No upcoming tasks</p>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>Common tasks and shortcuts</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Button 
                  variant="outline" 
                  className="h-24 flex flex-col space-y-2 hover:bg-blue-50 hover:border-blue-300 dark:hover:bg-blue-950"
                  onClick={() => window.location.href = '/contacts?action=add'}
                >
                  <UserPlus className="w-6 h-6 text-blue-600" />
                  <span className="text-sm">Add Contact</span>
                </Button>
                
                <Button 
                  variant="outline" 
                  className="h-24 flex flex-col space-y-2 hover:bg-green-50 hover:border-green-300 dark:hover:bg-green-950"
                  onClick={() => window.location.href = '/communications?action=call'}
                >
                  <Phone className="w-6 h-6 text-green-600" />
                  <span className="text-sm">Log Call</span>
                </Button>
                
                <Button 
                  variant="outline" 
                  className="h-24 flex flex-col space-y-2 hover:bg-purple-50 hover:border-purple-300 dark:hover:bg-purple-950"
                  onClick={() => window.location.href = '/campaigns'}
                >
                  <Mail className="w-6 h-6 text-purple-600" />
                  <span className="text-sm">Send Email</span>
                </Button>
                
                <Button 
                  variant="outline" 
                  className="h-24 flex flex-col space-y-2 hover:bg-orange-50 hover:border-orange-300 dark:hover:bg-orange-950"
                  onClick={() => window.location.href = '/tasks?action=add'}
                >
                  <Calendar className="w-6 h-6 text-orange-600" />
                  <span className="text-sm">Create Task</span>
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Performance Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Lead Conversion Rate</CardTitle>
                <Target className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {metrics?.leads.conversion_rate || 0}%
                </div>
                <div className="mt-2 h-2 bg-gray-200 rounded-full">
                  <div 
                    className="h-2 bg-linear-to-r from-green-500 to-green-600 rounded-full transition-all duration-500" 
                    style={{ width: `${metrics?.leads.conversion_rate || 0}%` }}
                  ></div>
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  {metrics?.leads.converted || 0} of {metrics?.leads.total || 0} leads converted
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Tasks Completed</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics?.tasks.completed || 0}</div>
                <p className="text-xs flex items-center mt-1">
                  <span className="text-muted-foreground">
                    {metrics?.tasks.overdue || 0} overdue • {metrics?.tasks.total || 0} total
                  </span>
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">New Contacts This Month</CardTitle>
                <AlertCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics?.contacts.new_this_month || 0}</div>
                <p className="text-xs flex items-center mt-1">
                  <ArrowUpRight className="w-3 h-3 text-green-600 mr-1" />
                  <span className="text-green-600">Growing</span>
                  <span className="text-muted-foreground ml-1">your network</span>
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
