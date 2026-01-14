'use client';

import { useEffect, useState, useCallback } from 'react';
import {
  Mail,
  Send,
  Eye,
  MousePointer,
  Reply,
  Clock,
  Plus,
  Search,
  Play,
  Pause,
  RefreshCw,
  FileText,
  Zap
} from 'lucide-react';
import { toast } from 'sonner';

import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { emailTrackingAPI } from '@/lib/premium-features-api';

interface TrackedEmail {
  id: string;
  to_email: string;
  subject: string;
  status: string;
  opens: number;
  clicks: number;
  replied: boolean;
  sent_at: string;
}

interface EmailTemplate {
  id: string;
  name: string;
  subject: string;
  category: string;
  usage_count: number;
  open_rate: number;
  click_rate: number;
}

interface EmailSequence {
  id: string;
  name: string;
  status: string;
  enrolled_count: number;
  completed_count: number;
  reply_rate: number;
  steps_count: number;
}

interface EmailMetrics {
  total_sent: number;
  total_opens: number;
  total_clicks: number;
  total_replies: number;
  open_rate: number;
  click_rate: number;
  reply_rate: number;
}

export default function EmailTrackingPage() {
  const [loading, setLoading] = useState(true);
  const [emails, setEmails] = useState<TrackedEmail[]>([]);
  const [templates, setTemplates] = useState<EmailTemplate[]>([]);
  const [sequences, setSequences] = useState<EmailSequence[]>([]);
  const [metrics, setMetrics] = useState<EmailMetrics | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [composeOpen, setComposeOpen] = useState(false);
  const [newEmail, setNewEmail] = useState({ to: '', subject: '', body: '' });

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      
      const [emailsRes, templatesRes, sequencesRes, analyticsRes] = await Promise.all([
        emailTrackingAPI.getEmails({ limit: 20 }),
        emailTrackingAPI.getTemplates(),
        emailTrackingAPI.getSequences(),
        emailTrackingAPI.getAnalytics()
      ]);

      setEmails(emailsRes.data.results || []);
      setTemplates(templatesRes.data.results || []);
      setSequences(sequencesRes.data.results || []);
      setMetrics(analyticsRes.data || null);
    } catch (error) {
      console.error('Failed to fetch email data:', error);
      // Demo data
      setEmails([
        { id: '1', to_email: 'john@acme.com', subject: 'Following up on our conversation', status: 'delivered', opens: 3, clicks: 1, replied: true, sent_at: new Date().toISOString() },
        { id: '2', to_email: 'sarah@techcorp.io', subject: 'Quick demo request', status: 'delivered', opens: 5, clicks: 2, replied: false, sent_at: new Date(Date.now() - 86400000).toISOString() },
        { id: '3', to_email: 'mike@startup.co', subject: 'Proposal attached', status: 'opened', opens: 2, clicks: 0, replied: false, sent_at: new Date(Date.now() - 172800000).toISOString() },
      ]);
      setTemplates([
        { id: '1', name: 'Cold Outreach', subject: 'Quick question about {{company}}', category: 'Prospecting', usage_count: 245, open_rate: 42, click_rate: 12 },
        { id: '2', name: 'Follow Up', subject: 'Following up on our call', category: 'Follow-up', usage_count: 189, open_rate: 65, click_rate: 28 },
        { id: '3', name: 'Meeting Request', subject: 'Time for a quick chat?', category: 'Scheduling', usage_count: 156, open_rate: 55, click_rate: 35 },
      ]);
      setSequences([
        { id: '1', name: 'New Lead Nurture', status: 'active', enrolled_count: 124, completed_count: 89, reply_rate: 18, steps_count: 5 },
        { id: '2', name: 'Re-engagement Campaign', status: 'active', enrolled_count: 67, completed_count: 34, reply_rate: 12, steps_count: 4 },
        { id: '3', name: 'Post-Demo Follow-up', status: 'paused', enrolled_count: 45, completed_count: 32, reply_rate: 25, steps_count: 3 },
      ]);
      setMetrics({
        total_sent: 1247,
        total_opens: 623,
        total_clicks: 187,
        total_replies: 94,
        open_rate: 50,
        click_rate: 15,
        reply_rate: 7.5
      });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleSendEmail = async () => {
    try {
      await emailTrackingAPI.sendEmail({
        to_email: newEmail.to,
        subject: newEmail.subject,
        body: newEmail.body
      });
      toast.success('Email sent with tracking enabled');
      setComposeOpen(false);
      setNewEmail({ to: '', subject: '', body: '' });
      fetchData();
    } catch {
      toast.error('Failed to send email');
    }
  };

  const handleToggleSequence = async (sequence: EmailSequence) => {
    try {
      if (sequence.status === 'active') {
        await emailTrackingAPI.pauseSequence(sequence.id);
        toast.success('Sequence paused');
      } else {
        await emailTrackingAPI.activateSequence(sequence.id);
        toast.success('Sequence activated');
      }
      fetchData();
    } catch {
      toast.error('Failed to update sequence');
    }
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      delivered: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
      opened: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
      clicked: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400',
      bounced: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
      pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
    };
    return styles[status] || styles.pending;
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-6 space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h1 className="text-3xl font-bold gradient-text flex items-center gap-2">
                <Mail className="w-8 h-8" />
                Email Tracking
              </h1>
              <p className="text-muted-foreground mt-1">
                Track opens, clicks, and replies with intelligent sequences
              </p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => fetchData()}>
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </Button>
              <Dialog open={composeOpen} onOpenChange={setComposeOpen}>
                <DialogTrigger asChild>
                  <Button>
                    <Plus className="w-4 h-4 mr-2" />
                    Compose
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl">
                  <DialogHeader>
                    <DialogTitle>Compose Tracked Email</DialogTitle>
                    <DialogDescription>
                      Send an email with open and click tracking enabled
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4 mt-4">
                    <div>
                      <Label>To</Label>
                      <Input
                        placeholder="recipient@example.com"
                        value={newEmail.to}
                        onChange={(e) => setNewEmail({ ...newEmail, to: e.target.value })}
                      />
                    </div>
                    <div>
                      <Label>Subject</Label>
                      <Input
                        placeholder="Email subject"
                        value={newEmail.subject}
                        onChange={(e) => setNewEmail({ ...newEmail, subject: e.target.value })}
                      />
                    </div>
                    <div>
                      <Label>Message</Label>
                      <Textarea
                        placeholder="Write your message..."
                        rows={8}
                        value={newEmail.body}
                        onChange={(e) => setNewEmail({ ...newEmail, body: e.target.value })}
                      />
                    </div>
                    <div className="flex justify-end gap-2">
                      <Button variant="outline" onClick={() => setComposeOpen(false)}>
                        Cancel
                      </Button>
                      <Button onClick={handleSendEmail}>
                        <Send className="w-4 h-4 mr-2" />
                        Send with Tracking
                      </Button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </div>

          {/* Metrics Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card className="modern-card">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Emails Sent
                </CardTitle>
                <Send className="w-5 h-5 text-blue-500" />
              </CardHeader>
              <CardContent>
                {loading ? (
                  <Skeleton className="h-8 w-20" />
                ) : (
                  <div className="text-2xl font-bold">{metrics?.total_sent.toLocaleString()}</div>
                )}
              </CardContent>
            </Card>

            <Card className="modern-card">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Open Rate
                </CardTitle>
                <Eye className="w-5 h-5 text-green-500" />
              </CardHeader>
              <CardContent>
                {loading ? (
                  <Skeleton className="h-8 w-20" />
                ) : (
                  <>
                    <div className="text-2xl font-bold">{metrics?.open_rate}%</div>
                    <p className="text-xs text-muted-foreground">{metrics?.total_opens} opens</p>
                  </>
                )}
              </CardContent>
            </Card>

            <Card className="modern-card">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Click Rate
                </CardTitle>
                <MousePointer className="w-5 h-5 text-purple-500" />
              </CardHeader>
              <CardContent>
                {loading ? (
                  <Skeleton className="h-8 w-20" />
                ) : (
                  <>
                    <div className="text-2xl font-bold">{metrics?.click_rate}%</div>
                    <p className="text-xs text-muted-foreground">{metrics?.total_clicks} clicks</p>
                  </>
                )}
              </CardContent>
            </Card>

            <Card className="modern-card">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Reply Rate
                </CardTitle>
                <Reply className="w-5 h-5 text-yellow-500" />
              </CardHeader>
              <CardContent>
                {loading ? (
                  <Skeleton className="h-8 w-20" />
                ) : (
                  <>
                    <div className="text-2xl font-bold">{metrics?.reply_rate}%</div>
                    <p className="text-xs text-muted-foreground">{metrics?.total_replies} replies</p>
                  </>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Tabs */}
          <Tabs defaultValue="emails" className="space-y-4">
            <TabsList className="grid w-full grid-cols-3 lg:w-auto lg:inline-grid">
              <TabsTrigger value="emails">Sent Emails</TabsTrigger>
              <TabsTrigger value="templates">Templates</TabsTrigger>
              <TabsTrigger value="sequences">Sequences</TabsTrigger>
            </TabsList>

            <TabsContent value="emails" className="space-y-4">
              <Card>
                <CardHeader>
                  <div className="flex flex-col sm:flex-row justify-between gap-4">
                    <div>
                      <CardTitle>Tracked Emails</CardTitle>
                      <CardDescription>Monitor email engagement in real-time</CardDescription>
                    </div>
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                      <Input
                        placeholder="Search emails..."
                        className="pl-10 w-64"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                      />
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <div className="space-y-3">
                      {[1, 2, 3].map((i) => (
                        <Skeleton key={i} className="h-16 w-full" />
                      ))}
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {emails.map((email) => (
                        <div
                          key={email.id}
                          className="flex items-center justify-between p-4 rounded-lg border hover:bg-accent/50 transition-colors"
                        >
                          <div className="flex-1">
                            <div className="flex items-center gap-3">
                              <h4 className="font-medium">{email.subject}</h4>
                              <Badge className={getStatusBadge(email.status)}>
                                {email.status}
                              </Badge>
                              {email.replied && (
                                <Badge className="bg-green-100 text-green-800 dark:bg-green-900/30">
                                  <Reply className="w-3 h-3 mr-1" />
                                  Replied
                                </Badge>
                              )}
                            </div>
                            <p className="text-sm text-muted-foreground mt-1">
                              To: {email.to_email}
                            </p>
                          </div>
                          <div className="flex items-center gap-6 text-sm">
                            <div className="flex items-center gap-1 text-muted-foreground">
                              <Eye className="w-4 h-4" />
                              {email.opens}
                            </div>
                            <div className="flex items-center gap-1 text-muted-foreground">
                              <MousePointer className="w-4 h-4" />
                              {email.clicks}
                            </div>
                            <div className="flex items-center gap-1 text-muted-foreground">
                              <Clock className="w-4 h-4" />
                              {new Date(email.sent_at).toLocaleDateString()}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="templates" className="space-y-4">
              <Card>
                <CardHeader>
                  <div className="flex justify-between items-center">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        <FileText className="w-5 h-5" />
                        Email Templates
                      </CardTitle>
                      <CardDescription>Reusable templates with performance analytics</CardDescription>
                    </div>
                    <Button>
                      <Plus className="w-4 h-4 mr-2" />
                      New Template
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <div className="space-y-3">
                      {[1, 2, 3].map((i) => (
                        <Skeleton key={i} className="h-20 w-full" />
                      ))}
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {templates.map((template) => (
                        <div
                          key={template.id}
                          className="flex items-center justify-between p-4 rounded-lg border hover:bg-accent/50 transition-colors"
                        >
                          <div>
                            <div className="flex items-center gap-3">
                              <h4 className="font-semibold">{template.name}</h4>
                              <Badge variant="outline">{template.category}</Badge>
                            </div>
                            <p className="text-sm text-muted-foreground mt-1">
                              {template.subject}
                            </p>
                          </div>
                          <div className="flex items-center gap-6">
                            <div className="text-center">
                              <div className="text-lg font-bold text-green-600">{template.open_rate}%</div>
                              <div className="text-xs text-muted-foreground">Open Rate</div>
                            </div>
                            <div className="text-center">
                              <div className="text-lg font-bold text-purple-600">{template.click_rate}%</div>
                              <div className="text-xs text-muted-foreground">Click Rate</div>
                            </div>
                            <div className="text-center">
                              <div className="text-lg font-bold">{template.usage_count}</div>
                              <div className="text-xs text-muted-foreground">Uses</div>
                            </div>
                            <Button variant="outline" size="sm">
                              Use
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="sequences" className="space-y-4">
              <Card>
                <CardHeader>
                  <div className="flex justify-between items-center">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        <Zap className="w-5 h-5" />
                        Email Sequences
                      </CardTitle>
                      <CardDescription>Automated multi-step email campaigns</CardDescription>
                    </div>
                    <Button>
                      <Plus className="w-4 h-4 mr-2" />
                      New Sequence
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <div className="space-y-3">
                      {[1, 2, 3].map((i) => (
                        <Skeleton key={i} className="h-24 w-full" />
                      ))}
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {sequences.map((sequence) => (
                        <div
                          key={sequence.id}
                          className="p-4 rounded-lg border hover:bg-accent/50 transition-colors"
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <h4 className="font-semibold">{sequence.name}</h4>
                              <Badge
                                className={
                                  sequence.status === 'active'
                                    ? 'bg-green-100 text-green-800 dark:bg-green-900/30'
                                    : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30'
                                }
                              >
                                {sequence.status}
                              </Badge>
                            </div>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleToggleSequence(sequence)}
                            >
                              {sequence.status === 'active' ? (
                                <>
                                  <Pause className="w-4 h-4 mr-2" />
                                  Pause
                                </>
                              ) : (
                                <>
                                  <Play className="w-4 h-4 mr-2" />
                                  Activate
                                </>
                              )}
                            </Button>
                          </div>
                          <div className="grid grid-cols-4 gap-4 mt-4">
                            <div className="text-center p-2 bg-secondary/50 rounded-lg">
                              <div className="text-lg font-bold">{sequence.steps_count}</div>
                              <div className="text-xs text-muted-foreground">Steps</div>
                            </div>
                            <div className="text-center p-2 bg-secondary/50 rounded-lg">
                              <div className="text-lg font-bold">{sequence.enrolled_count}</div>
                              <div className="text-xs text-muted-foreground">Enrolled</div>
                            </div>
                            <div className="text-center p-2 bg-secondary/50 rounded-lg">
                              <div className="text-lg font-bold">{sequence.completed_count}</div>
                              <div className="text-xs text-muted-foreground">Completed</div>
                            </div>
                            <div className="text-center p-2 bg-secondary/50 rounded-lg">
                              <div className="text-lg font-bold text-green-600">{sequence.reply_rate}%</div>
                              <div className="text-xs text-muted-foreground">Reply Rate</div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}

