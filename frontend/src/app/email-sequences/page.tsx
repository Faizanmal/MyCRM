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
import { Textarea } from '@/components/ui/textarea';
import {
  Mail,
  Plus,
  Search,
  Play,
  Pause,
  Copy,
  BarChart3,
  Users,
  Zap,
  Target,
  Sparkles,
  Eye,
  MousePointer,
  Reply,
  RefreshCw,
  MoreVertical,
  Edit,
  CheckCircle2,
  XCircle,
  AlertCircle,
} from 'lucide-react';
import { toast } from 'sonner';
import { emailSequenceAPI } from '@/lib/ai-workflow-api';

interface EmailSequence {
  id: string;
  name: string;
  description: string;
  status: 'draft' | 'active' | 'paused' | 'archived';
  steps_count: number;
  enrolled_count: number;
  completed_count: number;
  reply_rate: number;
  open_rate: number;
  click_rate: number;
  created_at: string;
}



interface Enrollment {
  id: string;
  contact_name: string;
  contact_email: string;
  sequence_name: string;
  status: 'active' | 'paused' | 'completed' | 'unsubscribed' | 'bounced';
  current_step: number;
  total_steps: number;
  enrolled_at: string;
  last_activity: string;
}

interface ABTest {
  id: string;
  name: string;
  step_name: string;
  status: 'running' | 'completed' | 'paused';
  variant_a_opens: number;
  variant_b_opens: number;
  variant_a_clicks: number;
  variant_b_clicks: number;
  sample_size: number;
  winner: string | null;
}

interface SequenceMetrics {
  total_sequences: number;
  active_sequences: number;
  total_enrolled: number;
  total_completed: number;
  average_open_rate: number;
  average_reply_rate: number;
  emails_sent_today: number;
  replies_today: number;
}

export default function EmailSequencesPage() {
  const [loading, setLoading] = useState(true);
  const [sequences, setSequences] = useState<EmailSequence[]>([]);
  const [enrollments, setEnrollments] = useState<Enrollment[]>([]);
  const [abTests, setABTests] = useState<ABTest[]>([]);
  const [metrics, setMetrics] = useState<SequenceMetrics | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTab, setSelectedTab] = useState('sequences');
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newSequence, setNewSequence] = useState({
    name: '',
    description: '',
    goal: 'engagement',
  });

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);

      const [sequencesRes, enrollmentsRes, abTestsRes] = await Promise.all([
        emailSequenceAPI.getSequences({ limit: 20 }),
        emailSequenceAPI.getEnrollments({ limit: 20 }),
        emailSequenceAPI.getABTests({ limit: 10 }),
      ]);

      setSequences(sequencesRes.data.results || []);
      setEnrollments(enrollmentsRes.data.results || []);
      setABTests(abTestsRes.data.results || []);
    } catch (error) {
      console.error('Failed to fetch sequence data:', error);
      // Demo data
      setSequences([
        {
          id: '1',
          name: 'New Lead Nurture',
          description: 'Welcome sequence for new leads',
          status: 'active',
          steps_count: 5,
          enrolled_count: 245,
          completed_count: 156,
          reply_rate: 18.5,
          open_rate: 62.3,
          click_rate: 24.1,
          created_at: new Date(Date.now() - 30 * 86400000).toISOString(),
        },
        {
          id: '2',
          name: 'Re-engagement Campaign',
          description: 'Win back inactive contacts',
          status: 'active',
          steps_count: 4,
          enrolled_count: 189,
          completed_count: 89,
          reply_rate: 12.3,
          open_rate: 45.6,
          click_rate: 15.8,
          created_at: new Date(Date.now() - 15 * 86400000).toISOString(),
        },
        {
          id: '3',
          name: 'Post-Demo Follow-up',
          description: 'Follow up after product demo',
          status: 'paused',
          steps_count: 3,
          enrolled_count: 67,
          completed_count: 45,
          reply_rate: 28.4,
          open_rate: 78.2,
          click_rate: 42.5,
          created_at: new Date(Date.now() - 7 * 86400000).toISOString(),
        },
        {
          id: '4',
          name: 'Trial Conversion',
          description: 'Convert trial users to paid',
          status: 'draft',
          steps_count: 6,
          enrolled_count: 0,
          completed_count: 0,
          reply_rate: 0,
          open_rate: 0,
          click_rate: 0,
          created_at: new Date().toISOString(),
        },
      ]);
      setEnrollments([
        {
          id: '1',
          contact_name: 'John Smith',
          contact_email: 'john@acme.com',
          sequence_name: 'New Lead Nurture',
          status: 'active',
          current_step: 3,
          total_steps: 5,
          enrolled_at: new Date(Date.now() - 5 * 86400000).toISOString(),
          last_activity: new Date(Date.now() - 86400000).toISOString(),
        },
        {
          id: '2',
          contact_name: 'Sarah Johnson',
          contact_email: 'sarah@techcorp.io',
          sequence_name: 'New Lead Nurture',
          status: 'completed',
          current_step: 5,
          total_steps: 5,
          enrolled_at: new Date(Date.now() - 14 * 86400000).toISOString(),
          last_activity: new Date(Date.now() - 2 * 86400000).toISOString(),
        },
        {
          id: '3',
          contact_name: 'Mike Wilson',
          contact_email: 'mike@startup.co',
          sequence_name: 'Post-Demo Follow-up',
          status: 'active',
          current_step: 2,
          total_steps: 3,
          enrolled_at: new Date(Date.now() - 3 * 86400000).toISOString(),
          last_activity: new Date().toISOString(),
        },
      ]);
      setABTests([
        {
          id: '1',
          name: 'Subject Line Test',
          step_name: 'Welcome Email',
          status: 'running',
          variant_a_opens: 234,
          variant_b_opens: 256,
          variant_a_clicks: 45,
          variant_b_clicks: 62,
          sample_size: 500,
          winner: null,
        },
        {
          id: '2',
          name: 'CTA Button Test',
          step_name: 'Follow-up #2',
          status: 'completed',
          variant_a_opens: 189,
          variant_b_opens: 178,
          variant_a_clicks: 67,
          variant_b_clicks: 42,
          sample_size: 400,
          winner: 'A',
        },
      ]);
      setMetrics({
        total_sequences: 12,
        active_sequences: 8,
        total_enrolled: 1247,
        total_completed: 834,
        average_open_rate: 58.4,
        average_reply_rate: 15.2,
        emails_sent_today: 342,
        replies_today: 28,
      });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleCreateSequence = async () => {
    try {
      await emailSequenceAPI.createSequence(newSequence);
      toast.success('Sequence created successfully');
      setCreateDialogOpen(false);
      setNewSequence({ name: '', description: '', goal: 'engagement' });
      fetchData();
    } catch {
      toast.error('Failed to create sequence');
    }
  };

  const handleToggleSequence = async (id: string, currentStatus: string) => {
    try {
      if (currentStatus === 'active') {
        await emailSequenceAPI.pauseSequence(id);
        toast.success('Sequence paused');
      } else {
        await emailSequenceAPI.activateSequence(id);
        toast.success('Sequence activated');
      }
      fetchData();
    } catch {
      toast.error('Failed to update sequence');
    }
  };

  const handleCloneSequence = async (id: string) => {
    try {
      await emailSequenceAPI.cloneSequence(id);
      toast.success('Sequence cloned successfully');
      fetchData();
    } catch {
      toast.error('Failed to clone sequence');
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, { variant: 'default' | 'secondary' | 'destructive' | 'outline'; icon: React.ReactNode }> = {
      active: { variant: 'default', icon: <Play className="w-3 h-3 mr-1" /> },
      paused: { variant: 'secondary', icon: <Pause className="w-3 h-3 mr-1" /> },
      draft: { variant: 'outline', icon: <Edit className="w-3 h-3 mr-1" /> },
      archived: { variant: 'destructive', icon: <XCircle className="w-3 h-3 mr-1" /> },
      completed: { variant: 'default', icon: <CheckCircle2 className="w-3 h-3 mr-1" /> },
      unsubscribed: { variant: 'destructive', icon: <XCircle className="w-3 h-3 mr-1" /> },
      bounced: { variant: 'destructive', icon: <AlertCircle className="w-3 h-3 mr-1" /> },
      running: { variant: 'default', icon: <RefreshCw className="w-3 h-3 mr-1 animate-spin" /> },
    };
    const config = variants[status] || { variant: 'outline' as const, icon: null };
    return (
      <Badge variant={config.variant} className="capitalize">
        {config.icon}
        {status}
      </Badge>
    );
  };

  const filteredSequences = sequences.filter(
    (s) =>
      s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-6 space-y-6">
          {/* Header */}
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold gradient-text flex items-center gap-2">
                <Mail className="w-8 h-8" />
                Email Sequences
              </h1>
              <p className="text-muted-foreground mt-1">
                Automate your email outreach with AI-powered sequences
              </p>
            </div>
            <div className="flex items-center gap-3">
              <Button variant="outline" onClick={() => fetchData()}>
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </Button>
              <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
                <DialogTrigger asChild>
                  <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                    <Plus className="w-4 h-4 mr-2" />
                    New Sequence
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Create Email Sequence</DialogTitle>
                    <DialogDescription>
                      Set up a new automated email sequence for your contacts
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4 py-4">
                    <div className="space-y-2">
                      <Label>Sequence Name</Label>
                      <Input
                        placeholder="e.g., Welcome Series"
                        value={newSequence.name}
                        onChange={(e) => setNewSequence({ ...newSequence, name: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Description</Label>
                      <Textarea
                        placeholder="Describe the purpose of this sequence..."
                        value={newSequence.description}
                        onChange={(e) => setNewSequence({ ...newSequence, description: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Goal</Label>
                      <Select
                        value={newSequence.goal}
                        onValueChange={(value) => setNewSequence({ ...newSequence, goal: value })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="engagement">Engagement</SelectItem>
                          <SelectItem value="conversion">Conversion</SelectItem>
                          <SelectItem value="nurture">Lead Nurture</SelectItem>
                          <SelectItem value="onboarding">Onboarding</SelectItem>
                          <SelectItem value="re-engagement">Re-engagement</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <Button onClick={handleCreateSequence} className="w-full">
                      <Sparkles className="w-4 h-4 mr-2" />
                      Create Sequence
                    </Button>
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
                      <p className="text-sm text-muted-foreground">Active Sequences</p>
                      <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                        {metrics?.active_sequences || 0}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        of {metrics?.total_sequences || 0} total
                      </p>
                    </div>
                    <div className="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center">
                      <Zap className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-950/50 dark:to-green-900/30 border-green-200 dark:border-green-800">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Total Enrolled</p>
                      <p className="text-3xl font-bold text-green-600 dark:text-green-400">
                        {metrics?.total_enrolled?.toLocaleString() || 0}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {metrics?.total_completed || 0} completed
                      </p>
                    </div>
                    <div className="w-12 h-12 bg-green-500/20 rounded-xl flex items-center justify-center">
                      <Users className="w-6 h-6 text-green-600 dark:text-green-400" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-950/50 dark:to-purple-900/30 border-purple-200 dark:border-purple-800">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Avg Open Rate</p>
                      <p className="text-3xl font-bold text-purple-600 dark:text-purple-400">
                        {metrics?.average_open_rate?.toFixed(1) || 0}%
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {metrics?.emails_sent_today || 0} sent today
                      </p>
                    </div>
                    <div className="w-12 h-12 bg-purple-500/20 rounded-xl flex items-center justify-center">
                      <Eye className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-950/50 dark:to-orange-900/30 border-orange-200 dark:border-orange-800">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Avg Reply Rate</p>
                      <p className="text-3xl font-bold text-orange-600 dark:text-orange-400">
                        {metrics?.average_reply_rate?.toFixed(1) || 0}%
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {metrics?.replies_today || 0} replies today
                      </p>
                    </div>
                    <div className="w-12 h-12 bg-orange-500/20 rounded-xl flex items-center justify-center">
                      <Reply className="w-6 h-6 text-orange-600 dark:text-orange-400" />
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
                <TabsTrigger value="sequences" className="gap-2">
                  <Mail className="w-4 h-4" />
                  Sequences
                </TabsTrigger>
                <TabsTrigger value="enrollments" className="gap-2">
                  <Users className="w-4 h-4" />
                  Enrollments
                </TabsTrigger>
                <TabsTrigger value="ab-tests" className="gap-2">
                  <Target className="w-4 h-4" />
                  A/B Tests
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

            <TabsContent value="sequences" className="mt-6">
              {loading ? (
                <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <Skeleton key={i} className="h-40" />
                  ))}
                </div>
              ) : (
                <div className="grid gap-4">
                  {filteredSequences.map((sequence) => (
                    <Card key={sequence.id} className="hover:shadow-lg transition-shadow">
                      <CardContent className="p-6">
                        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <h3 className="text-lg font-semibold">{sequence.name}</h3>
                              {getStatusBadge(sequence.status)}
                            </div>
                            <p className="text-sm text-muted-foreground mb-4">
                              {sequence.description}
                            </p>
                            <div className="flex flex-wrap items-center gap-4 text-sm">
                              <div className="flex items-center gap-1">
                                <Mail className="w-4 h-4 text-muted-foreground" />
                                <span>{sequence.steps_count} steps</span>
                              </div>
                              <div className="flex items-center gap-1">
                                <Users className="w-4 h-4 text-muted-foreground" />
                                <span>{sequence.enrolled_count} enrolled</span>
                              </div>
                              <div className="flex items-center gap-1">
                                <Eye className="w-4 h-4 text-green-500" />
                                <span>{sequence.open_rate.toFixed(1)}% opens</span>
                              </div>
                              <div className="flex items-center gap-1">
                                <MousePointer className="w-4 h-4 text-blue-500" />
                                <span>{sequence.click_rate.toFixed(1)}% clicks</span>
                              </div>
                              <div className="flex items-center gap-1">
                                <Reply className="w-4 h-4 text-purple-500" />
                                <span>{sequence.reply_rate.toFixed(1)}% replies</span>
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleToggleSequence(sequence.id, sequence.status)}
                              disabled={sequence.status === 'draft'}
                            >
                              {sequence.status === 'active' ? (
                                <>
                                  <Pause className="w-4 h-4 mr-1" />
                                  Pause
                                </>
                              ) : (
                                <>
                                  <Play className="w-4 h-4 mr-1" />
                                  Activate
                                </>
                              )}
                            </Button>
                            <Button variant="outline" size="sm" onClick={() => handleCloneSequence(sequence.id)}>
                              <Copy className="w-4 h-4" />
                            </Button>
                            <Button variant="outline" size="sm">
                              <BarChart3 className="w-4 h-4" />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <MoreVertical className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                        {sequence.enrolled_count > 0 && (
                          <div className="mt-4 pt-4 border-t">
                            <div className="flex items-center justify-between text-sm mb-2">
                              <span className="text-muted-foreground">Completion Progress</span>
                              <span className="font-medium">
                                {((sequence.completed_count / sequence.enrolled_count) * 100).toFixed(0)}%
                              </span>
                            </div>
                            <Progress
                              value={(sequence.completed_count / sequence.enrolled_count) * 100}
                              className="h-2"
                            />
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>

            <TabsContent value="enrollments" className="mt-6">
              {loading ? (
                <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <Skeleton key={i} className="h-20" />
                  ))}
                </div>
              ) : (
                <Card>
                  <CardContent className="p-0">
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead className="bg-muted/50">
                          <tr>
                            <th className="px-4 py-3 text-left text-sm font-medium">Contact</th>
                            <th className="px-4 py-3 text-left text-sm font-medium">Sequence</th>
                            <th className="px-4 py-3 text-left text-sm font-medium">Progress</th>
                            <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
                            <th className="px-4 py-3 text-left text-sm font-medium">Last Activity</th>
                            <th className="px-4 py-3 text-right text-sm font-medium">Actions</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y">
                          {enrollments.map((enrollment) => (
                            <tr key={enrollment.id} className="hover:bg-muted/30">
                              <td className="px-4 py-3">
                                <div>
                                  <p className="font-medium">{enrollment.contact_name}</p>
                                  <p className="text-sm text-muted-foreground">{enrollment.contact_email}</p>
                                </div>
                              </td>
                              <td className="px-4 py-3 text-sm">{enrollment.sequence_name}</td>
                              <td className="px-4 py-3">
                                <div className="flex items-center gap-2">
                                  <Progress
                                    value={(enrollment.current_step / enrollment.total_steps) * 100}
                                    className="w-20 h-2"
                                  />
                                  <span className="text-sm text-muted-foreground">
                                    {enrollment.current_step}/{enrollment.total_steps}
                                  </span>
                                </div>
                              </td>
                              <td className="px-4 py-3">{getStatusBadge(enrollment.status)}</td>
                              <td className="px-4 py-3 text-sm text-muted-foreground">
                                {new Date(enrollment.last_activity).toLocaleDateString()}
                              </td>
                              <td className="px-4 py-3 text-right">
                                <Button variant="ghost" size="sm">
                                  <MoreVertical className="w-4 h-4" />
                                </Button>
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

            <TabsContent value="ab-tests" className="mt-6">
              {loading ? (
                <div className="space-y-4">
                  {[1, 2].map((i) => (
                    <Skeleton key={i} className="h-40" />
                  ))}
                </div>
              ) : (
                <div className="grid gap-4">
                  {abTests.map((test) => (
                    <Card key={test.id}>
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <div>
                            <CardTitle className="text-lg">{test.name}</CardTitle>
                            <CardDescription>Testing in: {test.step_name}</CardDescription>
                          </div>
                          {getStatusBadge(test.status)}
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="grid md:grid-cols-2 gap-6">
                          <div className="space-y-3">
                            <div className="flex items-center justify-between">
                              <span className="font-medium">Variant A</span>
                              {test.winner === 'A' && (
                                <Badge variant="default" className="bg-green-500">Winner</Badge>
                              )}
                            </div>
                            <div className="space-y-2">
                              <div className="flex items-center justify-between text-sm">
                                <span className="text-muted-foreground">Opens</span>
                                <span>{test.variant_a_opens}</span>
                              </div>
                              <div className="flex items-center justify-between text-sm">
                                <span className="text-muted-foreground">Clicks</span>
                                <span>{test.variant_a_clicks}</span>
                              </div>
                              <div className="flex items-center justify-between text-sm">
                                <span className="text-muted-foreground">Click Rate</span>
                                <span>
                                  {test.variant_a_opens > 0
                                    ? ((test.variant_a_clicks / test.variant_a_opens) * 100).toFixed(1)
                                    : 0}%
                                </span>
                              </div>
                            </div>
                          </div>
                          <div className="space-y-3">
                            <div className="flex items-center justify-between">
                              <span className="font-medium">Variant B</span>
                              {test.winner === 'B' && (
                                <Badge variant="default" className="bg-green-500">Winner</Badge>
                              )}
                            </div>
                            <div className="space-y-2">
                              <div className="flex items-center justify-between text-sm">
                                <span className="text-muted-foreground">Opens</span>
                                <span>{test.variant_b_opens}</span>
                              </div>
                              <div className="flex items-center justify-between text-sm">
                                <span className="text-muted-foreground">Clicks</span>
                                <span>{test.variant_b_clicks}</span>
                              </div>
                              <div className="flex items-center justify-between text-sm">
                                <span className="text-muted-foreground">Click Rate</span>
                                <span>
                                  {test.variant_b_opens > 0
                                    ? ((test.variant_b_clicks / test.variant_b_opens) * 100).toFixed(1)
                                    : 0}%
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                        <div className="mt-4 pt-4 border-t flex items-center justify-between">
                          <span className="text-sm text-muted-foreground">
                            Sample size: {test.sample_size} contacts
                          </span>
                          {test.status === 'running' && (
                            <Button size="sm" variant="outline">
                              Select Winner
                            </Button>
                          )}
                        </div>
                      </CardContent>
                    </Card>
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
