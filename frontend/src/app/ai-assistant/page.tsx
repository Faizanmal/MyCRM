'use client';

import { useEffect, useState, useCallback } from 'react';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import {
  Sparkles,
  Mail,
  Phone,
  MessageSquare,
  ThumbsUp,
  ThumbsDown,
  RefreshCw,
  Copy,
  Lightbulb,
  Target,
  TrendingUp,
  AlertCircle,
  CheckCircle2,
  Brain,
  Zap,
  BookOpen,
  Users
} from 'lucide-react';
import { toast } from 'sonner';
import { aiSalesAssistantAPI } from '@/lib/premium-features-api';

interface EmailDraft {
  id: string;
  email_type: string;
  subject: string;
  body: string;
  tone: string;
  created_at: string;
  contact_name?: string;
}

interface CoachingAdvice {
  id: string;
  coaching_type: string;
  situation: string;
  advice: string;
  action_items: string[];
  helpful?: boolean;
  created_at: string;
}

interface ObjectionResponse {
  id: string;
  objection: string;
  response: string;
  alternative_responses: string[];
  tips: string[];
}

export default function AISalesAssistantPage() {
  const [loading, setLoading] = useState(true);
  const [emailDrafts, setEmailDrafts] = useState<EmailDraft[]>([]);
  const [coachingAdvice, setCoachingAdvice] = useState<CoachingAdvice[]>([]);
  const [objectionResponses, setObjectionResponses] = useState<ObjectionResponse[]>([]);
  const [generating, setGenerating] = useState(false);

  // Form states
  const [emailForm, setEmailForm] = useState({ type: 'follow_up', context: '', tone: 'professional' });
  const [coachingForm, setCoachingForm] = useState({ type: 'deal_strategy', situation: '' });
  const [objectionForm, setObjectionForm] = useState({ objection: '', context: '' });

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      
      const [draftsRes, coachingRes, objectionsRes] = await Promise.all([
        aiSalesAssistantAPI.getEmailDrafts({ limit: 5 }),
        aiSalesAssistantAPI.getCoachingAdvice({ limit: 5 }),
        aiSalesAssistantAPI.getObjectionResponses({ limit: 5 })
      ]);

      setEmailDrafts(draftsRes.data.results || []);
      setCoachingAdvice(coachingRes.data.results || []);
      setObjectionResponses(objectionsRes.data.results || []);
    } catch (error) {
      console.error('Failed to fetch AI data:', error);
      // Demo data
      setEmailDrafts([
        { id: '1', email_type: 'follow_up', subject: 'Following up on our conversation', body: 'Hi John,\n\nI wanted to follow up on our conversation last week about improving your sales process. Based on what you shared, I think our solution could help you...\n\nBest regards', tone: 'professional', created_at: new Date().toISOString(), contact_name: 'John Smith' },
        { id: '2', email_type: 'cold_outreach', subject: 'Quick question about your sales team', body: 'Hi Sarah,\n\nI noticed TechCorp recently expanded your sales team. Congrats! Many companies in your situation struggle with...', tone: 'friendly', created_at: new Date(Date.now() - 86400000).toISOString(), contact_name: 'Sarah Johnson' },
      ]);
      setCoachingAdvice([
        { id: '1', coaching_type: 'deal_strategy', situation: 'Enterprise deal stalled after demo', advice: 'The deal appears stalled due to lack of executive sponsorship. Consider these approaches...', action_items: ['Identify executive champion', 'Create business case document', 'Schedule exec briefing'], created_at: new Date().toISOString() },
        { id: '2', coaching_type: 'negotiation', situation: 'Customer asking for 40% discount', advice: 'Instead of discounting, focus on value and consider these alternatives...', action_items: ['Highlight ROI', 'Offer payment terms', 'Bundle additional features'], created_at: new Date(Date.now() - 3600000).toISOString() },
      ]);
      setObjectionResponses([
        { id: '1', objection: 'Your price is too high', response: 'I understand budget is a key consideration. Let me share how our customers typically see a 3x return within the first year...', alternative_responses: ['Let\'s break down the total cost of ownership...', 'What would the cost of not solving this problem be?'], tips: ['Focus on ROI', 'Use customer success stories'] },
        { id: '2', objection: 'We\'re happy with our current solution', response: 'That\'s great to hear you have a solution in place. Many of our customers said the same thing before discovering...', alternative_responses: ['What would need to change for you to consider alternatives?'], tips: ['Ask discovery questions', 'Identify pain points'] },
      ]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleGenerateEmail = async () => {
    if (!emailForm.context) {
      toast.error('Please provide some context');
      return;
    }
    try {
      setGenerating(true);
      await aiSalesAssistantAPI.generateEmailDraft({
        email_type: emailForm.type,
        context: emailForm.context,
        tone: emailForm.tone
      });
      toast.success('Email draft generated');
      fetchData();
      setEmailForm({ ...emailForm, context: '' });
    } catch {
      toast.error('Failed to generate email');
    } finally {
      setGenerating(false);
    }
  };

  const handleRequestCoaching = async () => {
    if (!coachingForm.situation) {
      toast.error('Please describe your situation');
      return;
    }
    try {
      setGenerating(true);
      await aiSalesAssistantAPI.requestCoaching({
        coaching_type: coachingForm.type,
        situation: coachingForm.situation
      });
      toast.success('Coaching advice generated');
      fetchData();
      setCoachingForm({ ...coachingForm, situation: '' });
    } catch {
      toast.error('Failed to get coaching');
    } finally {
      setGenerating(false);
    }
  };

  const handleGenerateObjectionResponse = async () => {
    if (!objectionForm.objection) {
      toast.error('Please enter the objection');
      return;
    }
    try {
      setGenerating(true);
      await aiSalesAssistantAPI.generateObjectionResponse({
        objection: objectionForm.objection,
        context: objectionForm.context
      });
      toast.success('Response generated');
      fetchData();
      setObjectionForm({ objection: '', context: '' });
    } catch {
      toast.error('Failed to generate response');
    } finally {
      setGenerating(false);
    }
  };

  const handleCopyText = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard');
  };

  const handleFeedback = async (id: string, helpful: boolean) => {
    try {
      await aiSalesAssistantAPI.markHelpful(id, helpful);
      toast.success('Feedback recorded');
    } catch {
      toast.error('Failed to record feedback');
    }
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-6 space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h1 className="text-3xl font-bold gradient-text flex items-center gap-2">
                <Sparkles className="w-8 h-8" />
                AI Sales Assistant
              </h1>
              <p className="text-muted-foreground mt-1">
                AI-powered email drafts, coaching, and objection handling
              </p>
            </div>
            <Button variant="outline" onClick={() => fetchData()}>
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="modern-card hover:shadow-lg transition-shadow cursor-pointer">
              <CardContent className="p-4 flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                  <Mail className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold">Draft Email</h3>
                  <p className="text-sm text-muted-foreground">AI-written emails</p>
                </div>
              </CardContent>
            </Card>

            <Card className="modern-card hover:shadow-lg transition-shadow cursor-pointer">
              <CardContent className="p-4 flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
                  <Brain className="w-6 h-6 text-purple-600" />
                </div>
                <div>
                  <h3 className="font-semibold">Get Coaching</h3>
                  <p className="text-sm text-muted-foreground">Deal strategy advice</p>
                </div>
              </CardContent>
            </Card>

            <Card className="modern-card hover:shadow-lg transition-shadow cursor-pointer">
              <CardContent className="p-4 flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                  <MessageSquare className="w-6 h-6 text-green-600" />
                </div>
                <div>
                  <h3 className="font-semibold">Handle Objection</h3>
                  <p className="text-sm text-muted-foreground">Smart responses</p>
                </div>
              </CardContent>
            </Card>

            <Card className="modern-card hover:shadow-lg transition-shadow cursor-pointer">
              <CardContent className="p-4 flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center">
                  <Phone className="w-6 h-6 text-orange-600" />
                </div>
                <div>
                  <h3 className="font-semibold">Call Script</h3>
                  <p className="text-sm text-muted-foreground">Guided conversations</p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Tabs */}
          <Tabs defaultValue="email" className="space-y-4">
            <TabsList className="grid w-full grid-cols-4 lg:w-auto lg:inline-grid">
              <TabsTrigger value="email">Email Drafts</TabsTrigger>
              <TabsTrigger value="coaching">Sales Coaching</TabsTrigger>
              <TabsTrigger value="objections">Objection Handling</TabsTrigger>
              <TabsTrigger value="scripts">Call Scripts</TabsTrigger>
            </TabsList>

            {/* Email Drafts Tab */}
            <TabsContent value="email" className="space-y-4">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Generator */}
                <Card className="lg:col-span-1">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Zap className="w-5 h-5" />
                      Generate Email
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label>Email Type</Label>
                      <Select
                        value={emailForm.type}
                        onValueChange={(v) => setEmailForm({ ...emailForm, type: v })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="cold_outreach">Cold Outreach</SelectItem>
                          <SelectItem value="follow_up">Follow Up</SelectItem>
                          <SelectItem value="meeting_request">Meeting Request</SelectItem>
                          <SelectItem value="proposal">Proposal</SelectItem>
                          <SelectItem value="thank_you">Thank You</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label>Tone</Label>
                      <Select
                        value={emailForm.tone}
                        onValueChange={(v) => setEmailForm({ ...emailForm, tone: v })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="professional">Professional</SelectItem>
                          <SelectItem value="friendly">Friendly</SelectItem>
                          <SelectItem value="casual">Casual</SelectItem>
                          <SelectItem value="formal">Formal</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label>Context</Label>
                      <Textarea
                        placeholder="Describe the situation, recipient, and what you want to achieve..."
                        rows={4}
                        value={emailForm.context}
                        onChange={(e) => setEmailForm({ ...emailForm, context: e.target.value })}
                      />
                    </div>
                    <Button
                      className="w-full"
                      onClick={handleGenerateEmail}
                      disabled={generating}
                    >
                      {generating ? (
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      ) : (
                        <Sparkles className="w-4 h-4 mr-2" />
                      )}
                      Generate Email
                    </Button>
                  </CardContent>
                </Card>

                {/* Recent Drafts */}
                <Card className="lg:col-span-2">
                  <CardHeader>
                    <CardTitle>Recent Drafts</CardTitle>
                    <CardDescription>Your AI-generated email drafts</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {loading ? (
                      <div className="space-y-4">
                        {[1, 2].map((i) => (
                          <Skeleton key={i} className="h-40 w-full" />
                        ))}
                      </div>
                    ) : emailDrafts.length === 0 ? (
                      <div className="text-center py-8 text-muted-foreground">
                        <Mail className="w-12 h-12 mx-auto mb-4 opacity-50" />
                        <p>No email drafts yet. Generate your first one!</p>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {emailDrafts.map((draft) => (
                          <div key={draft.id} className="p-4 rounded-lg border">
                            <div className="flex items-center justify-between mb-2">
                              <div className="flex items-center gap-2">
                                <Badge variant="outline">{draft.email_type.replace('_', ' ')}</Badge>
                                <Badge variant="secondary">{draft.tone}</Badge>
                                {draft.contact_name && (
                                  <span className="text-sm text-muted-foreground">
                                    for {draft.contact_name}
                                  </span>
                                )}
                              </div>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleCopyText(draft.body)}
                              >
                                <Copy className="w-4 h-4" />
                              </Button>
                            </div>
                            <h4 className="font-semibold mb-2">{draft.subject}</h4>
                            <p className="text-sm text-muted-foreground whitespace-pre-line line-clamp-4">
                              {draft.body}
                            </p>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* Coaching Tab */}
            <TabsContent value="coaching" className="space-y-4">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Request Coaching */}
                <Card className="lg:col-span-1">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Brain className="w-5 h-5" />
                      Get Advice
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label>Coaching Type</Label>
                      <Select
                        value={coachingForm.type}
                        onValueChange={(v) => setCoachingForm({ ...coachingForm, type: v })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="deal_strategy">Deal Strategy</SelectItem>
                          <SelectItem value="negotiation">Negotiation</SelectItem>
                          <SelectItem value="stakeholder">Stakeholder Management</SelectItem>
                          <SelectItem value="closing">Closing Techniques</SelectItem>
                          <SelectItem value="discovery">Discovery Questions</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label>Describe Your Situation</Label>
                      <Textarea
                        placeholder="What's happening with the deal? What challenges are you facing?"
                        rows={6}
                        value={coachingForm.situation}
                        onChange={(e) => setCoachingForm({ ...coachingForm, situation: e.target.value })}
                      />
                    </div>
                    <Button
                      className="w-full"
                      onClick={handleRequestCoaching}
                      disabled={generating}
                    >
                      {generating ? (
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      ) : (
                        <Lightbulb className="w-4 h-4 mr-2" />
                      )}
                      Get Coaching
                    </Button>
                  </CardContent>
                </Card>

                {/* Coaching History */}
                <Card className="lg:col-span-2">
                  <CardHeader>
                    <CardTitle>Coaching Advice</CardTitle>
                    <CardDescription>AI-powered sales coaching</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {loading ? (
                      <div className="space-y-4">
                        {[1, 2].map((i) => (
                          <Skeleton key={i} className="h-48 w-full" />
                        ))}
                      </div>
                    ) : coachingAdvice.length === 0 ? (
                      <div className="text-center py-8 text-muted-foreground">
                        <Brain className="w-12 h-12 mx-auto mb-4 opacity-50" />
                        <p>No coaching advice yet. Ask for your first tip!</p>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {coachingAdvice.map((advice) => (
                          <div key={advice.id} className="p-4 rounded-lg border">
                            <div className="flex items-center justify-between mb-3">
                              <Badge>{advice.coaching_type.replace('_', ' ')}</Badge>
                              <div className="flex items-center gap-2">
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleFeedback(advice.id, true)}
                                >
                                  <ThumbsUp className="w-4 h-4" />
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleFeedback(advice.id, false)}
                                >
                                  <ThumbsDown className="w-4 h-4" />
                                </Button>
                              </div>
                            </div>
                            <p className="text-sm text-muted-foreground mb-3">
                              <strong>Situation:</strong> {advice.situation}
                            </p>
                            <p className="text-sm mb-3">{advice.advice}</p>
                            <div>
                              <h5 className="text-sm font-semibold mb-2">Action Items:</h5>
                              <ul className="space-y-1">
                                {advice.action_items.map((item, i) => (
                                  <li key={i} className="flex items-center gap-2 text-sm">
                                    <CheckCircle2 className="w-4 h-4 text-green-500" />
                                    {item}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* Objections Tab */}
            <TabsContent value="objections" className="space-y-4">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Handle Objection */}
                <Card className="lg:col-span-1">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <MessageSquare className="w-5 h-5" />
                      Handle Objection
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label>The Objection</Label>
                      <Textarea
                        placeholder="What objection did you receive? e.g., 'Your price is too high'"
                        rows={3}
                        value={objectionForm.objection}
                        onChange={(e) => setObjectionForm({ ...objectionForm, objection: e.target.value })}
                      />
                    </div>
                    <div>
                      <Label>Context (optional)</Label>
                      <Textarea
                        placeholder="Any additional context about the deal or customer?"
                        rows={3}
                        value={objectionForm.context}
                        onChange={(e) => setObjectionForm({ ...objectionForm, context: e.target.value })}
                      />
                    </div>
                    <Button
                      className="w-full"
                      onClick={handleGenerateObjectionResponse}
                      disabled={generating}
                    >
                      {generating ? (
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      ) : (
                        <Zap className="w-4 h-4 mr-2" />
                      )}
                      Generate Response
                    </Button>
                  </CardContent>
                </Card>

                {/* Objection Library */}
                <Card className="lg:col-span-2">
                  <CardHeader>
                    <CardTitle>Objection Library</CardTitle>
                    <CardDescription>Smart responses to common objections</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {loading ? (
                      <div className="space-y-4">
                        {[1, 2].map((i) => (
                          <Skeleton key={i} className="h-40 w-full" />
                        ))}
                      </div>
                    ) : objectionResponses.length === 0 ? (
                      <div className="text-center py-8 text-muted-foreground">
                        <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-50" />
                        <p>No objection responses yet.</p>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {objectionResponses.map((obj) => (
                          <div key={obj.id} className="p-4 rounded-lg border">
                            <div className="flex items-center justify-between mb-2">
                              <h4 className="font-semibold text-red-600 dark:text-red-400">
                                &#34;{obj.objection}&#34;
                              </h4>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleCopyText(obj.response)}
                              >
                                <Copy className="w-4 h-4" />
                              </Button>
                            </div>
                            <p className="text-sm mb-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                              {obj.response}
                            </p>
                            {obj.alternative_responses.length > 0 && (
                              <div className="mb-3">
                                <h5 className="text-xs font-semibold text-muted-foreground mb-2">
                                  ALTERNATIVE RESPONSES:
                                </h5>
                                <ul className="space-y-1">
                                  {obj.alternative_responses.map((alt, i) => (
                                    <li key={i} className="text-sm text-muted-foreground">
                                      • {alt}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}
                            <div className="flex flex-wrap gap-2">
                              {obj.tips.map((tip, i) => (
                                <Badge key={i} variant="secondary" className="text-xs">
                                  💡 {tip}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* Call Scripts Tab */}
            <TabsContent value="scripts" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BookOpen className="w-5 h-5" />
                    Call Scripts Library
                  </CardTitle>
                  <CardDescription>Guided conversation frameworks for different scenarios</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {[
                      { type: 'discovery', title: 'Discovery Call', desc: 'Uncover needs and pain points', icon: Target },
                      { type: 'demo', title: 'Product Demo', desc: 'Showcase your solution', icon: Users },
                      { type: 'follow_up', title: 'Follow-up Call', desc: 'Re-engage prospects', icon: Phone },
                      { type: 'closing', title: 'Closing Call', desc: 'Close the deal', icon: CheckCircle2 },
                      { type: 'negotiation', title: 'Negotiation', desc: 'Navigate pricing discussions', icon: TrendingUp },
                      { type: 'objection', title: 'Objection Handling', desc: 'Address concerns', icon: AlertCircle },
                    ].map((script) => (
                      <Card key={script.type} className="hover:shadow-md transition-shadow cursor-pointer">
                        <CardContent className="p-4">
                          <div className="flex items-start gap-3">
                            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                              <script.icon className="w-5 h-5 text-primary" />
                            </div>
                            <div>
                              <h4 className="font-semibold">{script.title}</h4>
                              <p className="text-sm text-muted-foreground">{script.desc}</p>
                            </div>
                          </div>
                          <Button variant="outline" className="w-full mt-4" size="sm">
                            Generate Script
                          </Button>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
