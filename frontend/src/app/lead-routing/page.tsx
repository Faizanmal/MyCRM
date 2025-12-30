'use client';

import { useEffect, useState, useCallback } from 'react';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import {
  Route,
  Users,
  UserCheck,
  UserPlus,
  Target,
  TrendingUp,
  Clock,

  RefreshCw,
  Plus,
  Search,
  Settings,
  BarChart3,
  ArrowRight,
  Shuffle,
  MoreVertical,
  Zap,
  Award,
  MapPin,
  Building2,
} from 'lucide-react';
import { toast } from 'sonner';
import { leadRoutingAPI } from '@/lib/ai-workflow-api';

interface SalesRep {
  id: string;
  user_name: string;
  user_email: string;
  avatar_url?: string;
  is_available: boolean;
  current_load: number;
  max_capacity: number;
  specializations: string[];
  territories: string[];
  conversion_rate: number;
  avg_response_time_hours: number;
  total_assignments: number;
  active_leads: number;
}

interface RoutingRule {
  id: string;
  name: string;
  priority: number;
  is_active: boolean;
  routing_type: 'round_robin' | 'weighted' | 'skill_based' | 'territory' | 'ai';
  conditions: Record<string, unknown>;
  assigned_reps_count: number;
  leads_routed: number;
  success_rate: number;
}

interface LeadAssignment {
  id: string;
  lead_name: string;
  lead_email: string;
  lead_company: string;
  assigned_to: string;
  assigned_to_avatar?: string;
  status: 'pending' | 'accepted' | 'rejected' | 'escalated' | 'converted';
  assignment_reason: string;
  match_score: number;
  assigned_at: string;
  response_time_hours?: number;
}

interface RoutingMetrics {
  total_leads_routed_today: number;
  avg_assignment_time_seconds: number;
  acceptance_rate: number;
  conversion_rate: number;
  avg_response_time_hours: number;
  leads_pending: number;
  leads_escalated: number;
  top_performer_id: string;
  top_performer_name: string;
}

export default function LeadRoutingPage() {
  const [loading, setLoading] = useState(true);
  const [reps, setReps] = useState<SalesRep[]>([]);
  const [rules, setRules] = useState<RoutingRule[]>([]);
  const [assignments, setAssignments] = useState<LeadAssignment[]>([]);
  const [metrics, setMetrics] = useState<RoutingMetrics | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTab, setSelectedTab] = useState('dashboard');
  const [createRuleDialogOpen, setCreateRuleDialogOpen] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);

      const [repsRes, rulesRes, assignmentsRes, dashboardRes] = await Promise.all([
        leadRoutingAPI.getRepProfiles({ limit: 20 }),
        leadRoutingAPI.getRoutingRules({ limit: 20 }),
        leadRoutingAPI.getAssignments({ limit: 20 }),
        leadRoutingAPI.getRoutingDashboard(),
      ]);

      setReps(repsRes.data.results || []);
      setRules(rulesRes.data.results || []);
      setAssignments(assignmentsRes.data.results || []);
      setMetrics(dashboardRes.data || null);
    } catch (error) {
      console.error('Failed to fetch routing data:', error);
      // Demo data
      setReps([
        {
          id: '1',
          user_name: 'Alex Johnson',
          user_email: 'alex@company.com',
          is_available: true,
          current_load: 12,
          max_capacity: 20,
          specializations: ['Enterprise', 'SaaS'],
          territories: ['North America', 'Europe'],
          conversion_rate: 32.5,
          avg_response_time_hours: 1.2,
          total_assignments: 156,
          active_leads: 12,
        },
        {
          id: '2',
          user_name: 'Sarah Miller',
          user_email: 'sarah@company.com',
          is_available: true,
          current_load: 8,
          max_capacity: 15,
          specializations: ['SMB', 'E-commerce'],
          territories: ['North America'],
          conversion_rate: 28.3,
          avg_response_time_hours: 2.1,
          total_assignments: 134,
          active_leads: 8,
        },
        {
          id: '3',
          user_name: 'Mike Chen',
          user_email: 'mike@company.com',
          is_available: false,
          current_load: 15,
          max_capacity: 15,
          specializations: ['Enterprise', 'Healthcare'],
          territories: ['Asia Pacific'],
          conversion_rate: 35.8,
          avg_response_time_hours: 0.8,
          total_assignments: 189,
          active_leads: 15,
        },
        {
          id: '4',
          user_name: 'Emily Davis',
          user_email: 'emily@company.com',
          is_available: true,
          current_load: 5,
          max_capacity: 20,
          specializations: ['Startup', 'Tech'],
          territories: ['Europe', 'Middle East'],
          conversion_rate: 24.1,
          avg_response_time_hours: 3.5,
          total_assignments: 98,
          active_leads: 5,
        },
      ]);
      setRules([
        {
          id: '1',
          name: 'Enterprise Round Robin',
          priority: 1,
          is_active: true,
          routing_type: 'round_robin',
          conditions: { company_size: 'enterprise' },
          assigned_reps_count: 4,
          leads_routed: 234,
          success_rate: 78.5,
        },
        {
          id: '2',
          name: 'Territory-Based Routing',
          priority: 2,
          is_active: true,
          routing_type: 'territory',
          conditions: { by_region: true },
          assigned_reps_count: 6,
          leads_routed: 456,
          success_rate: 82.3,
        },
        {
          id: '3',
          name: 'AI Smart Routing',
          priority: 3,
          is_active: true,
          routing_type: 'ai',
          conditions: { use_ai_matching: true },
          assigned_reps_count: 8,
          leads_routed: 189,
          success_rate: 91.2,
        },
        {
          id: '4',
          name: 'SMB Weighted Distribution',
          priority: 4,
          is_active: false,
          routing_type: 'weighted',
          conditions: { company_size: 'smb' },
          assigned_reps_count: 3,
          leads_routed: 123,
          success_rate: 65.4,
        },
      ]);
      setAssignments([
        {
          id: '1',
          lead_name: 'John Smith',
          lead_email: 'john@acme.com',
          lead_company: 'Acme Corp',
          assigned_to: 'Alex Johnson',
          status: 'accepted',
          assignment_reason: 'Territory match + Enterprise specialization',
          match_score: 92,
          assigned_at: new Date(Date.now() - 3600000).toISOString(),
          response_time_hours: 0.5,
        },
        {
          id: '2',
          lead_name: 'Lisa Wang',
          lead_email: 'lisa@techstartup.io',
          lead_company: 'TechStartup',
          assigned_to: 'Emily Davis',
          status: 'pending',
          assignment_reason: 'AI match: Startup specialization',
          match_score: 87,
          assigned_at: new Date(Date.now() - 1800000).toISOString(),
        },
        {
          id: '3',
          lead_name: 'Robert Brown',
          lead_email: 'robert@healthcare.org',
          lead_company: 'HealthCare Inc',
          assigned_to: 'Mike Chen',
          status: 'converted',
          assignment_reason: 'Healthcare vertical expertise',
          match_score: 95,
          assigned_at: new Date(Date.now() - 86400000 * 3).toISOString(),
          response_time_hours: 0.3,
        },
        {
          id: '4',
          lead_name: 'Amanda Green',
          lead_email: 'amanda@retail.com',
          lead_company: 'Retail Plus',
          assigned_to: 'Sarah Miller',
          status: 'escalated',
          assignment_reason: 'Round robin assignment',
          match_score: 72,
          assigned_at: new Date(Date.now() - 86400000).toISOString(),
          response_time_hours: 8.2,
        },
      ]);
      setMetrics({
        total_leads_routed_today: 47,
        avg_assignment_time_seconds: 2.3,
        acceptance_rate: 89.5,
        conversion_rate: 28.7,
        avg_response_time_hours: 1.8,
        leads_pending: 12,
        leads_escalated: 3,
        top_performer_id: '3',
        top_performer_name: 'Mike Chen',
      });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleToggleAvailability = async (repId: string, isAvailable: boolean) => {
    try {
      await leadRoutingAPI.updateAvailability(repId, { is_available: !isAvailable });
      toast.success(`Availability ${!isAvailable ? 'enabled' : 'disabled'}`);
      fetchData();
    } catch {
      toast.error('Failed to update availability');
    }
  };

  const handleToggleRule = async (ruleId: string, isActive: boolean) => {
    try {
      await leadRoutingAPI.updateRoutingRule(ruleId, { is_active: !isActive });
      toast.success(`Rule ${!isActive ? 'activated' : 'deactivated'}`);
      fetchData();
    } catch {
      toast.error('Failed to update rule');
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, { variant: 'default' | 'secondary' | 'destructive' | 'outline'; color: string }> = {
      pending: { variant: 'outline', color: 'text-yellow-600' },
      accepted: { variant: 'default', color: 'text-green-600' },
      rejected: { variant: 'destructive', color: 'text-red-600' },
      escalated: { variant: 'secondary', color: 'text-orange-600' },
      converted: { variant: 'default', color: 'text-blue-600' },
    };
    const config = variants[status] || { variant: 'outline' as const, color: '' };
    return (
      <Badge variant={config.variant} className={`capitalize ${config.color}`}>
        {status}
      </Badge>
    );
  };

  const getRoutingTypeBadge = (type: string) => {
    const icons: Record<string, React.ReactNode> = {
      round_robin: <Shuffle className="w-3 h-3 mr-1" />,
      weighted: <BarChart3 className="w-3 h-3 mr-1" />,
      skill_based: <Target className="w-3 h-3 mr-1" />,
      territory: <MapPin className="w-3 h-3 mr-1" />,
      ai: <Zap className="w-3 h-3 mr-1" />,
    };
    return (
      <Badge variant="outline" className="capitalize">
        {icons[type]}
        {type.replace('_', ' ')}
      </Badge>
    );
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-6 space-y-6">
          {/* Header */}
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold gradient-text flex items-center gap-2">
                <Route className="w-8 h-8" />
                Lead Routing
              </h1>
              <p className="text-muted-foreground mt-1">
                AI-powered lead assignment and distribution
              </p>
            </div>
            <div className="flex items-center gap-3">
              <Button variant="outline" onClick={() => fetchData()}>
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </Button>
              <Dialog open={createRuleDialogOpen} onOpenChange={setCreateRuleDialogOpen}>
                <DialogTrigger asChild>
                  <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                    <Plus className="w-4 h-4 mr-2" />
                    New Rule
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Create Routing Rule</DialogTitle>
                    <DialogDescription>
                      Set up a new rule for automatic lead assignment
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4 py-4">
                    <div className="space-y-2">
                      <Label>Rule Name</Label>
                      <Input placeholder="e.g., Enterprise Lead Routing" />
                    </div>
                    <div className="space-y-2">
                      <Label>Routing Type</Label>
                      <Select>
                        <SelectTrigger>
                          <SelectValue placeholder="Select type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="round_robin">Round Robin</SelectItem>
                          <SelectItem value="weighted">Weighted Distribution</SelectItem>
                          <SelectItem value="skill_based">Skill-Based</SelectItem>
                          <SelectItem value="territory">Territory-Based</SelectItem>
                          <SelectItem value="ai">AI Smart Routing</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>Priority</Label>
                      <Input type="number" placeholder="1" min={1} max={100} />
                    </div>
                    <Button className="w-full">Create Rule</Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </div>

          {/* Metrics Cards */}
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {[1, 2, 3, 4].map((i) => (
                <Skeleton key={i} className="h-32" />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950/50 dark:to-blue-900/30 border-blue-200 dark:border-blue-800">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Routed Today</p>
                      <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                        {metrics?.total_leads_routed_today || 0}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {metrics?.avg_assignment_time_seconds?.toFixed(1)}s avg time
                      </p>
                    </div>
                    <div className="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center">
                      <UserPlus className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-950/50 dark:to-green-900/30 border-green-200 dark:border-green-800">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Acceptance Rate</p>
                      <p className="text-3xl font-bold text-green-600 dark:text-green-400">
                        {metrics?.acceptance_rate?.toFixed(1) || 0}%
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {metrics?.conversion_rate?.toFixed(1)}% conversion
                      </p>
                    </div>
                    <div className="w-12 h-12 bg-green-500/20 rounded-xl flex items-center justify-center">
                      <UserCheck className="w-6 h-6 text-green-600 dark:text-green-400" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-950/50 dark:to-purple-900/30 border-purple-200 dark:border-purple-800">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Avg Response</p>
                      <p className="text-3xl font-bold text-purple-600 dark:text-purple-400">
                        {metrics?.avg_response_time_hours?.toFixed(1) || 0}h
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {metrics?.leads_pending || 0} pending
                      </p>
                    </div>
                    <div className="w-12 h-12 bg-purple-500/20 rounded-xl flex items-center justify-center">
                      <Clock className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-950/50 dark:to-orange-900/30 border-orange-200 dark:border-orange-800">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Top Performer</p>
                      <p className="text-lg font-bold text-orange-600 dark:text-orange-400 truncate">
                        {metrics?.top_performer_name || 'N/A'}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {metrics?.leads_escalated || 0} escalated
                      </p>
                    </div>
                    <div className="w-12 h-12 bg-orange-500/20 rounded-xl flex items-center justify-center">
                      <Award className="w-6 h-6 text-orange-600 dark:text-orange-400" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Tabs */}
          <Tabs value={selectedTab} onValueChange={setSelectedTab}>
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <TabsList>
                <TabsTrigger value="dashboard" className="gap-2">
                  <BarChart3 className="w-4 h-4" />
                  Dashboard
                </TabsTrigger>
                <TabsTrigger value="reps" className="gap-2">
                  <Users className="w-4 h-4" />
                  Sales Reps
                </TabsTrigger>
                <TabsTrigger value="rules" className="gap-2">
                  <Settings className="w-4 h-4" />
                  Rules
                </TabsTrigger>
                <TabsTrigger value="assignments" className="gap-2">
                  <ArrowRight className="w-4 h-4" />
                  Assignments
                </TabsTrigger>
              </TabsList>
              <div className="relative w-full md:w-64">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="Search..."
                  className="pl-10"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            </div>

            <TabsContent value="dashboard" className="mt-6">
              <div className="grid lg:grid-cols-2 gap-6">
                {/* Rep Workload */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Team Workload</CardTitle>
                    <CardDescription>Current capacity utilization</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {reps.slice(0, 4).map((rep) => (
                      <div key={rep.id} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Avatar className="h-8 w-8">
                              <AvatarImage src={rep.avatar_url} />
                              <AvatarFallback>{rep.user_name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                            </Avatar>
                            <div>
                              <p className="text-sm font-medium">{rep.user_name}</p>
                              <p className="text-xs text-muted-foreground">
                                {rep.current_load}/{rep.max_capacity} leads
                              </p>
                            </div>
                          </div>
                          <Badge variant={rep.is_available ? 'default' : 'secondary'}>
                            {rep.is_available ? 'Available' : 'Busy'}
                          </Badge>
                        </div>
                        <Progress
                          value={(rep.current_load / rep.max_capacity) * 100}
                          className="h-2"
                        />
                      </div>
                    ))}
                  </CardContent>
                </Card>

                {/* Recent Assignments */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Recent Assignments</CardTitle>
                    <CardDescription>Latest lead routing activity</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {assignments.slice(0, 4).map((assignment) => (
                      <div
                        key={assignment.id}
                        className="flex items-center justify-between p-3 rounded-lg bg-muted/50"
                      >
                        <div className="flex-1 min-w-0">
                          <p className="font-medium truncate">{assignment.lead_name}</p>
                          <p className="text-sm text-muted-foreground truncate">
                            {assignment.lead_company}
                          </p>
                        </div>
                        <div className="flex items-center gap-2 ml-4">
                          <ArrowRight className="w-4 h-4 text-muted-foreground" />
                          <span className="text-sm">{assignment.assigned_to}</span>
                          {getStatusBadge(assignment.status)}
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="reps" className="mt-6">
              {loading ? (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {[1, 2, 3, 4].map((i) => (
                    <Skeleton key={i} className="h-64" />
                  ))}
                </div>
              ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {reps.map((rep) => (
                    <Card key={rep.id} className="hover:shadow-lg transition-shadow">
                      <CardContent className="pt-6">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex items-center gap-3">
                            <Avatar className="h-12 w-12">
                              <AvatarImage src={rep.avatar_url} />
                              <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-500 text-white">
                                {rep.user_name.split(' ').map(n => n[0]).join('')}
                              </AvatarFallback>
                            </Avatar>
                            <div>
                              <p className="font-semibold">{rep.user_name}</p>
                              <p className="text-sm text-muted-foreground">{rep.user_email}</p>
                            </div>
                          </div>
                          <Switch
                            checked={rep.is_available}
                            onCheckedChange={() => handleToggleAvailability(rep.id, rep.is_available)}
                          />
                        </div>

                        <div className="space-y-3">
                          <div>
                            <div className="flex items-center justify-between text-sm mb-1">
                              <span className="text-muted-foreground">Workload</span>
                              <span>{rep.current_load}/{rep.max_capacity}</span>
                            </div>
                            <Progress value={(rep.current_load / rep.max_capacity) * 100} className="h-2" />
                          </div>

                          <div className="grid grid-cols-2 gap-2 text-sm">
                            <div className="flex items-center gap-1">
                              <TrendingUp className="w-4 h-4 text-green-500" />
                              <span>{rep.conversion_rate}% conv.</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Clock className="w-4 h-4 text-blue-500" />
                              <span>{rep.avg_response_time_hours}h resp.</span>
                            </div>
                          </div>

                          <div className="flex flex-wrap gap-1">
                            {rep.specializations.map((spec) => (
                              <Badge key={spec} variant="outline" className="text-xs">
                                {spec}
                              </Badge>
                            ))}
                          </div>

                          <div className="flex items-center gap-1 text-sm text-muted-foreground">
                            <MapPin className="w-4 h-4" />
                            {rep.territories.join(', ')}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>

            <TabsContent value="rules" className="mt-6">
              {loading ? (
                <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <Skeleton key={i} className="h-24" />
                  ))}
                </div>
              ) : (
                <div className="space-y-4">
                  {rules.map((rule) => (
                    <Card key={rule.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-4">
                            <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-primary/10">
                              <span className="font-bold text-primary">{rule.priority}</span>
                            </div>
                            <div>
                              <div className="flex items-center gap-2">
                                <h3 className="font-semibold">{rule.name}</h3>
                                {getRoutingTypeBadge(rule.routing_type)}
                              </div>
                              <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
                                <span>{rule.assigned_reps_count} reps assigned</span>
                                <span>{rule.leads_routed} leads routed</span>
                                <span>{rule.success_rate}% success</span>
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Switch
                              checked={rule.is_active}
                              onCheckedChange={() => handleToggleRule(rule.id, rule.is_active)}
                            />
                            <Button variant="ghost" size="sm">
                              <MoreVertical className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>

            <TabsContent value="assignments" className="mt-6">
              {loading ? (
                <Skeleton className="h-96" />
              ) : (
                <Card>
                  <CardContent className="p-0">
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead className="bg-muted/50">
                          <tr>
                            <th className="px-4 py-3 text-left text-sm font-medium">Lead</th>
                            <th className="px-4 py-3 text-left text-sm font-medium">Company</th>
                            <th className="px-4 py-3 text-left text-sm font-medium">Assigned To</th>
                            <th className="px-4 py-3 text-left text-sm font-medium">Match Score</th>
                            <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
                            <th className="px-4 py-3 text-left text-sm font-medium">Response</th>
                            <th className="px-4 py-3 text-right text-sm font-medium">Actions</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y">
                          {assignments.map((assignment) => (
                            <tr key={assignment.id} className="hover:bg-muted/30">
                              <td className="px-4 py-3">
                                <div>
                                  <p className="font-medium">{assignment.lead_name}</p>
                                  <p className="text-sm text-muted-foreground">{assignment.lead_email}</p>
                                </div>
                              </td>
                              <td className="px-4 py-3">
                                <div className="flex items-center gap-2">
                                  <Building2 className="w-4 h-4 text-muted-foreground" />
                                  {assignment.lead_company}
                                </div>
                              </td>
                              <td className="px-4 py-3">
                                <div className="flex items-center gap-2">
                                  <Avatar className="h-6 w-6">
                                    <AvatarFallback className="text-xs">
                                      {assignment.assigned_to.split(' ').map(n => n[0]).join('')}
                                    </AvatarFallback>
                                  </Avatar>
                                  {assignment.assigned_to}
                                </div>
                              </td>
                              <td className="px-4 py-3">
                                <div className="flex items-center gap-2">
                                  <Progress value={assignment.match_score} className="w-16 h-2" />
                                  <span className="text-sm font-medium">{assignment.match_score}%</span>
                                </div>
                              </td>
                              <td className="px-4 py-3">{getStatusBadge(assignment.status)}</td>
                              <td className="px-4 py-3 text-sm text-muted-foreground">
                                {assignment.response_time_hours
                                  ? `${assignment.response_time_hours}h`
                                  : 'Pending'}
                              </td>
                              <td className="px-4 py-3 text-right">
                                <div className="flex items-center justify-end gap-1">
                                  <Button variant="ghost" size="sm" title="Reassign">
                                    <Shuffle className="w-4 h-4" />
                                  </Button>
                                  <Button variant="ghost" size="sm">
                                    <MoreVertical className="w-4 h-4" />
                                  </Button>
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
