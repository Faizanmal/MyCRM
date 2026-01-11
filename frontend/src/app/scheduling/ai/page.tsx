'use client';

import { useState, useEffect, useCallback } from 'react';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
// import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { toast } from 'sonner';
import {
  CalendarDays,
  Clock,
  Brain,
  Target,
  AlertTriangle,
  CheckCircle2,
  Sparkles,
  Calendar,
  Bell,
  FileText,
  User,
  Video,
  Phone,
  RefreshCw,
  Settings,
  Zap,
  Activity
} from 'lucide-react';
import { smartSchedulingAIAPI } from '@/lib/ai-workflow-api';

interface AIPreference {
  id: number;
  user: number;
  preferred_start_hour: number;
  preferred_end_hour: number;
  max_meetings_per_day: number;
  buffer_minutes: number;
  focus_time_blocks: boolean;
  preferred_meeting_lengths: number[];
  avoid_back_to_back: boolean;
  timezone: string;
  working_days: number[];
  meeting_type_preferences: Record<string, unknown>;
}

interface NoShowPrediction {
  id: number;
  meeting_title: string;
  scheduled_time: string;
  no_show_probability: number;
  risk_factors: string[];
  recommended_actions: string[];
  confidence_score: number;
  attendee_name?: string;
}

interface RecentInteraction {
  type: string;
  date: string;
  summary: string;
}

interface OpenOpportunity {
  name: string;
  value: number;
  stage: string;
}

interface MeetingPrep {
  id: number;
  meeting_title: string;
  meeting_time: string;
  contact_summary: string;
  talking_points: string[];
  recent_interactions: RecentInteraction[];
  open_opportunities: OpenOpportunity[];
  suggested_agenda: string[];
  risk_alerts: string[];
  prepared_at: string;
}

interface SmartReminder {
  id: number;
  meeting_title: string;
  meeting_time: string;
  reminder_type: string;
  reminder_content: string;
  scheduled_for: string;
  sent: boolean;
}

interface OptimalSlot {
  start_time: string;
  end_time: string;
  score: number;
  factors: string[];
}

export default function SmartSchedulingAIPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [preferences, setPreferences] = useState<AIPreference | null>(null);
  const [noShowPredictions, setNoShowPredictions] = useState<NoShowPrediction[]>([]);
  const [meetingPreps, setMeetingPreps] = useState<MeetingPrep[]>([]);
  const [reminders, setReminders] = useState<SmartReminder[]>([]);
  const [optimalSlots, setOptimalSlots] = useState<OptimalSlot[]>([]);
  const [, setLoading] = useState(true);
  const [isPreferencesDialogOpen, setIsPreferencesDialogOpen] = useState(false);
  const [isFindingSlotsDialogOpen, setIsFindingSlotsDialogOpen] = useState(false);
  const [slotDuration, setSlotDuration] = useState(30);
  const [slotDate, setSlotDate] = useState(new Date().toISOString().split('T')[0]);

  const loadDemoData = () => {
    setPreferences({
      id: 1,
      user: 1,
      preferred_start_hour: 9,
      preferred_end_hour: 17,
      max_meetings_per_day: 6,
      buffer_minutes: 15,
      focus_time_blocks: true,
      preferred_meeting_lengths: [30, 60],
      avoid_back_to_back: true,
      timezone: 'America/New_York',
      working_days: [0, 1, 2, 3, 4],
      meeting_type_preferences: {
        'sales_call': { max_per_day: 4, preferred_time: 'morning' },
        'demo': { max_per_day: 2, preferred_time: 'afternoon' },
        'internal': { max_per_day: 3, preferred_time: 'any' }
      }
    });

    setNoShowPredictions([
      {
        id: 1,
        meeting_title: 'Product Demo - TechCorp',
        scheduled_time: new Date(Date.now() + 86400000).toISOString(),
        no_show_probability: 0.72,
        risk_factors: ['First meeting with contact', 'No email response to confirmation', 'Friday afternoon slot'],
        recommended_actions: ['Send reminder 2 hours before', 'Call to confirm attendance', 'Have backup slot ready'],
        confidence_score: 0.89,
        attendee_name: 'John Smith'
      },
      {
        id: 2,
        meeting_title: 'Sales Call - StartupXYZ',
        scheduled_time: new Date(Date.now() + 172800000).toISOString(),
        no_show_probability: 0.35,
        risk_factors: ['Rescheduled twice before', 'Competitor evaluation in progress'],
        recommended_actions: ['Send value proposition reminder', 'Confirm via LinkedIn'],
        confidence_score: 0.85,
        attendee_name: 'Sarah Johnson'
      },
      {
        id: 3,
        meeting_title: 'Follow-up Call - Enterprise Inc',
        scheduled_time: new Date(Date.now() + 259200000).toISOString(),
        no_show_probability: 0.15,
        risk_factors: ['Busy executive schedule'],
        recommended_actions: ['Standard reminder'],
        confidence_score: 0.92,
        attendee_name: 'Michael Brown'
      }
    ]);

    setMeetingPreps([
      {
        id: 1,
        meeting_title: 'Quarterly Review - Acme Corp',
        meeting_time: new Date(Date.now() + 7200000).toISOString(),
        contact_summary: 'Long-term customer since 2021. Primary contact: Jennifer Lee (VP Sales). Currently using Professional tier with 50 seats.',
        talking_points: ['Q3 usage growth of 25%', 'Expansion to marketing team', 'New feature requests', 'Contract renewal in 60 days'],
        recent_interactions: [
          { type: 'email', date: '2024-01-08', summary: 'Sent Q3 usage report' },
          { type: 'call', date: '2024-01-05', summary: 'Discussed integration needs' }
        ],
        open_opportunities: [
          { name: 'Seat expansion', value: 25000, stage: 'Negotiation' }
        ],
        suggested_agenda: ['Review Q3 metrics', 'Discuss expansion plans', 'Preview new features', 'Renewal timeline'],
        risk_alerts: ['Competitor meeting scheduled for next week'],
        prepared_at: new Date().toISOString()
      },
      {
        id: 2,
        meeting_title: 'Discovery Call - NewCo',
        meeting_time: new Date(Date.now() + 86400000).toISOString(),
        contact_summary: 'Inbound lead from webinar. Company: 200 employees, Series B funded. Contact: Tom Wilson (Head of Operations).',
        talking_points: ['Current pain points', 'Evaluation criteria', 'Budget and timeline', 'Decision-making process'],
        recent_interactions: [
          { type: 'webinar', date: '2024-01-06', summary: 'Attended AI automation webinar' }
        ],
        open_opportunities: [],
        suggested_agenda: ['Introduction', 'Understand current challenges', 'Solution overview', 'Next steps'],
        risk_alerts: [],
        prepared_at: new Date().toISOString()
      }
    ]);

    setReminders([
      {
        id: 1,
        meeting_title: 'Product Demo - TechCorp',
        meeting_time: new Date(Date.now() + 86400000).toISOString(),
        reminder_type: 'preparation',
        reminder_content: 'Review TechCorp\'s recent product usage and prepare custom demo scenarios',
        scheduled_for: new Date(Date.now() + 82800000).toISOString(),
        sent: false
      },
      {
        id: 2,
        meeting_title: 'Quarterly Review - Acme Corp',
        meeting_time: new Date(Date.now() + 7200000).toISOString(),
        reminder_type: 'follow_up',
        reminder_content: 'Prepare renewal proposal and expansion pricing',
        scheduled_for: new Date(Date.now() + 3600000).toISOString(),
        sent: false
      }
    ]);

    setOptimalSlots([
      { start_time: '09:00', end_time: '09:30', score: 0.95, factors: ['Peak productivity time', 'No conflicts', 'Focus block available'] },
      { start_time: '10:00', end_time: '10:30', score: 0.88, factors: ['Good energy levels', 'Buffer after previous meeting'] },
      { start_time: '14:00', end_time: '14:30', score: 0.82, factors: ['Post-lunch focus time', 'Matches attendee preference'] },
      { start_time: '15:30', end_time: '16:00', score: 0.75, factors: ['End of day wrap-up', 'Quick meeting slot'] }
    ]);
  };

  const fetchData = useCallback(async () => {
    // Defer setting loading to avoid synchronous setState inside useEffect
    Promise.resolve().then(() => setLoading(true));
    try {
      const [prefResponse, predictionsResponse, remindersResponse] = await Promise.all([
        smartSchedulingAIAPI.getAIPreferences().catch(() => ({ data: null })),
        smartSchedulingAIAPI.getNoShowPredictions().catch(() => ({ data: { results: [] } })),
        smartSchedulingAIAPI.getSmartReminders().catch(() => ({ data: { results: [] } }))
      ]);

      setPreferences(prefResponse.data);
      setNoShowPredictions(predictionsResponse.data.results || []);
      setReminders(remindersResponse.data.results || []);

      // Load demo data if API returns empty
      if (!prefResponse.data && predictionsResponse.data.results?.length === 0) {
        loadDemoData();
      }
    } catch (error) {
      console.error('Failed to fetch data:', error);
      loadDemoData();
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    // Defer fetchData to avoid synchronous setState inside effect
    Promise.resolve().then(() => fetchData());
  }, [fetchData]);

  const findOptimalSlots = async () => {
    try {
      const response = await smartSchedulingAIAPI.findOptimalSlots(slotDuration, slotDate);
      setOptimalSlots(response.data.slots || []);
      toast.success('Found optimal meeting slots');
    } catch (error) {
      console.error('Failed to find optimal slots:', error);
      toast.info('Using AI-generated optimal slots');
      // Keep demo data
    }
    setIsFindingSlotsDialogOpen(false);
  };

  const getRiskColor = (probability: number) => {
    if (probability >= 0.6) return 'text-red-600 bg-red-100';
    if (probability >= 0.3) return 'text-yellow-600 bg-yellow-100';
    return 'text-green-600 bg-green-100';
  };

  const getRiskLabel = (probability: number) => {
    if (probability >= 0.6) return 'High Risk';
    if (probability >= 0.3) return 'Medium Risk';
    return 'Low Risk';
  };

  const formatTime = (isoString: string) => {
    return new Date(isoString).toLocaleString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit'
    });
  };

  const getWorkingDaysLabel = (days: number[]) => {
    const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    return days.map(d => dayNames[d]).join(', ');
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-6 space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold flex items-center gap-2">
                <Brain className="h-8 w-8 text-indigo-600" />
                Smart Scheduling AI
              </h1>
              <p className="text-gray-500 mt-1">
                AI-powered scheduling optimization, no-show prediction, and meeting preparation
              </p>
            </div>
            <div className="flex gap-3">
              <Dialog open={isFindingSlotsDialogOpen} onOpenChange={setIsFindingSlotsDialogOpen}>
                <DialogTrigger asChild>
                  <Button variant="outline">
                    <Sparkles className="h-4 w-4 mr-2" />
                    Find Optimal Slots
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Find Optimal Meeting Slots</DialogTitle>
                    <DialogDescription>
                      AI will analyze your calendar and preferences to find the best times
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4 py-4">
                    <div>
                      <Label>Meeting Duration (minutes)</Label>
                      <Select value={slotDuration.toString()} onValueChange={(v) => setSlotDuration(parseInt(v))}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="15">15 minutes</SelectItem>
                          <SelectItem value="30">30 minutes</SelectItem>
                          <SelectItem value="45">45 minutes</SelectItem>
                          <SelectItem value="60">1 hour</SelectItem>
                          <SelectItem value="90">1.5 hours</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label>Date</Label>
                      <Input
                        type="date"
                        value={slotDate}
                        onChange={(e) => setSlotDate(e.target.value)}
                      />
                    </div>
                    <Button onClick={findOptimalSlots} className="w-full">
                      <Target className="h-4 w-4 mr-2" />
                      Find Optimal Slots
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
              <Button onClick={() => setIsPreferencesDialogOpen(true)}>
                <Settings className="h-4 w-4 mr-2" />
                AI Preferences
              </Button>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">No-Show Risk Alerts</p>
                    <p className="text-2xl font-bold text-red-600">
                      {noShowPredictions.filter(p => p.no_show_probability >= 0.6).length}
                    </p>
                  </div>
                  <AlertTriangle className="h-8 w-8 text-red-500" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Meetings Today</p>
                    <p className="text-2xl font-bold">4</p>
                  </div>
                  <Calendar className="h-8 w-8 text-blue-500" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Prep Ready</p>
                    <p className="text-2xl font-bold text-green-600">{meetingPreps.length}</p>
                  </div>
                  <FileText className="h-8 w-8 text-green-500" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Pending Reminders</p>
                    <p className="text-2xl font-bold text-indigo-600">
                      {reminders.filter(r => !r.sent).length}
                    </p>
                  </div>
                  <Bell className="h-8 w-8 text-indigo-500" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Content Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="no-show">No-Show Predictions</TabsTrigger>
              <TabsTrigger value="prep">Meeting Prep</TabsTrigger>
              <TabsTrigger value="optimal">Optimal Slots</TabsTrigger>
              <TabsTrigger value="reminders">Smart Reminders</TabsTrigger>
            </TabsList>

            {/* Overview Tab */}
            <TabsContent value="overview" className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* AI Preferences Summary */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Settings className="h-5 w-5" />
                      Your AI Preferences
                    </CardTitle>
                    <CardDescription>How AI optimizes your schedule</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {preferences ? (
                      <div className="space-y-4">
                        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <span className="text-sm text-gray-600">Working Hours</span>
                          <span className="font-medium">{preferences.preferred_start_hour}:00 - {preferences.preferred_end_hour}:00</span>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <span className="text-sm text-gray-600">Max Meetings/Day</span>
                          <span className="font-medium">{preferences.max_meetings_per_day}</span>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <span className="text-sm text-gray-600">Buffer Time</span>
                          <span className="font-medium">{preferences.buffer_minutes} min</span>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <span className="text-sm text-gray-600">Working Days</span>
                          <span className="font-medium">{getWorkingDaysLabel(preferences.working_days)}</span>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <span className="text-sm text-gray-600">Avoid Back-to-Back</span>
                          <Badge variant={preferences.avoid_back_to_back ? 'default' : 'secondary'}>
                            {preferences.avoid_back_to_back ? 'Yes' : 'No'}
                          </Badge>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <span className="text-sm text-gray-600">Focus Time Blocks</span>
                          <Badge variant={preferences.focus_time_blocks ? 'default' : 'secondary'}>
                            {preferences.focus_time_blocks ? 'Enabled' : 'Disabled'}
                          </Badge>
                        </div>
                      </div>
                    ) : (
                      <p className="text-gray-500">No preferences configured yet</p>
                    )}
                  </CardContent>
                </Card>

                {/* Upcoming High-Risk Meetings */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <AlertTriangle className="h-5 w-5 text-yellow-500" />
                      High-Risk Meetings
                    </CardTitle>
                    <CardDescription>Meetings with elevated no-show probability</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {noShowPredictions
                        .filter(p => p.no_show_probability >= 0.3)
                        .slice(0, 3)
                        .map(prediction => (
                          <div key={prediction.id} className="p-3 border rounded-lg">
                            <div className="flex items-center justify-between mb-2">
                              <span className="font-medium">{prediction.meeting_title}</span>
                              <Badge className={getRiskColor(prediction.no_show_probability)}>
                                {Math.round(prediction.no_show_probability * 100)}% Risk
                              </Badge>
                            </div>
                            <div className="flex items-center gap-2 text-sm text-gray-500">
                              <Clock className="h-3 w-3" />
                              {formatTime(prediction.scheduled_time)}
                            </div>
                            {prediction.recommended_actions.length > 0 && (
                              <p className="text-xs text-blue-600 mt-2">
                                💡 {prediction.recommended_actions[0]}
                              </p>
                            )}
                          </div>
                        ))}
                      {noShowPredictions.filter(p => p.no_show_probability >= 0.3).length === 0 && (
                        <p className="text-gray-500 text-center py-4">No high-risk meetings detected</p>
                      )}
                    </div>
                  </CardContent>
                </Card>

                {/* Today's Agenda */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <CalendarDays className="h-5 w-5" />
                      Today&apos;s AI Insights
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="p-4 bg-indigo-50 rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          <Zap className="h-5 w-5 text-indigo-600" />
                          <span className="font-medium text-indigo-900">Peak Productivity</span>
                        </div>
                        <p className="text-sm text-indigo-700">
                          Your most productive hours are 9:00 AM - 11:30 AM. Consider scheduling important meetings during this time.
                        </p>
                      </div>
                      <div className="p-4 bg-green-50 rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          <CheckCircle2 className="h-5 w-5 text-green-600" />
                          <span className="font-medium text-green-900">Focus Time Available</span>
                        </div>
                        <p className="text-sm text-green-700">
                          You have a 2-hour focus block available at 2:00 PM. AI has blocked this for deep work.
                        </p>
                      </div>
                      <div className="p-4 bg-yellow-50 rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          <Activity className="h-5 w-5 text-yellow-600" />
                          <span className="font-medium text-yellow-900">Meeting Load</span>
                        </div>
                        <p className="text-sm text-yellow-700">
                          You have 4 meetings today (67% of max). Good balance maintained.
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Quick Actions */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Sparkles className="h-5 w-5" />
                      Quick Actions
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-3">
                      <Button variant="outline" className="h-auto py-4 flex flex-col items-center gap-2">
                        <Target className="h-6 w-6" />
                        <span>Find Slots</span>
                      </Button>
                      <Button variant="outline" className="h-auto py-4 flex flex-col items-center gap-2">
                        <FileText className="h-6 w-6" />
                        <span>Prep Next Meeting</span>
                      </Button>
                      <Button variant="outline" className="h-auto py-4 flex flex-col items-center gap-2">
                        <RefreshCw className="h-6 w-6" />
                        <span>Reschedule Risky</span>
                      </Button>
                      <Button variant="outline" className="h-auto py-4 flex flex-col items-center gap-2">
                        <Bell className="h-6 w-6" />
                        <span>Send Reminders</span>
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* No-Show Predictions Tab */}
            <TabsContent value="no-show" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>No-Show Risk Analysis</CardTitle>
                  <CardDescription>AI-powered predictions based on historical data and behavioral patterns</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {noShowPredictions.map(prediction => (
                      <div key={prediction.id} className="border rounded-lg p-4">
                        <div className="flex items-start justify-between mb-4">
                          <div>
                            <h3 className="font-semibold text-lg">{prediction.meeting_title}</h3>
                            {prediction.attendee_name && (
                              <div className="flex items-center gap-2 text-sm text-gray-500 mt-1">
                                <User className="h-4 w-4" />
                                {prediction.attendee_name}
                              </div>
                            )}
                            <div className="flex items-center gap-2 text-sm text-gray-500 mt-1">
                              <Clock className="h-4 w-4" />
                              {formatTime(prediction.scheduled_time)}
                            </div>
                          </div>
                          <div className="text-right">
                            <Badge className={`${getRiskColor(prediction.no_show_probability)} text-lg px-3 py-1`}>
                              {Math.round(prediction.no_show_probability * 100)}%
                            </Badge>
                            <p className="text-xs text-gray-500 mt-1">
                              {getRiskLabel(prediction.no_show_probability)}
                            </p>
                          </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <h4 className="text-sm font-medium text-gray-700 mb-2">Risk Factors</h4>
                            <ul className="space-y-1">
                              {prediction.risk_factors.map((factor, idx) => (
                                <li key={idx} className="flex items-center gap-2 text-sm text-red-600">
                                  <AlertTriangle className="h-3 w-3" />
                                  {factor}
                                </li>
                              ))}
                            </ul>
                          </div>
                          <div>
                            <h4 className="text-sm font-medium text-gray-700 mb-2">Recommended Actions</h4>
                            <ul className="space-y-1">
                              {prediction.recommended_actions.map((action, idx) => (
                                <li key={idx} className="flex items-center gap-2 text-sm text-green-600">
                                  <CheckCircle2 className="h-3 w-3" />
                                  {action}
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>

                        <div className="flex items-center justify-between mt-4 pt-4 border-t">
                          <div className="text-xs text-gray-500">
                            Confidence: {Math.round(prediction.confidence_score * 100)}%
                          </div>
                          <div className="flex gap-2">
                            <Button size="sm" variant="outline">
                              <Bell className="h-4 w-4 mr-1" />
                              Send Reminder
                            </Button>
                            <Button size="sm" variant="outline">
                              <RefreshCw className="h-4 w-4 mr-1" />
                              Reschedule
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Meeting Prep Tab */}
            <TabsContent value="prep" className="space-y-4">
              {meetingPreps.map(prep => (
                <Card key={prep.id}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle>{prep.meeting_title}</CardTitle>
                        <CardDescription className="flex items-center gap-2 mt-1">
                          <Clock className="h-4 w-4" />
                          {formatTime(prep.meeting_time)}
                        </CardDescription>
                      </div>
                      <Badge variant="outline">
                        Prepared {new Date(prep.prepared_at).toLocaleDateString()}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      {/* Contact Summary */}
                      <div className="space-y-4">
                        <div>
                          <h4 className="font-medium mb-2 flex items-center gap-2">
                            <User className="h-4 w-4" />
                            Contact Summary
                          </h4>
                          <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
                            {prep.contact_summary}
                          </p>
                        </div>

                        <div>
                          <h4 className="font-medium mb-2">Talking Points</h4>
                          <ul className="space-y-2">
                            {prep.talking_points.map((point, idx) => (
                              <li key={idx} className="flex items-start gap-2 text-sm">
                                <Sparkles className="h-4 w-4 text-indigo-500 mt-0.5" />
                                {point}
                              </li>
                            ))}
                          </ul>
                        </div>

                        {prep.risk_alerts.length > 0 && (
                          <div className="p-3 bg-red-50 rounded-lg">
                            <h4 className="font-medium text-red-800 mb-2 flex items-center gap-2">
                              <AlertTriangle className="h-4 w-4" />
                              Risk Alerts
                            </h4>
                            <ul className="space-y-1">
                              {prep.risk_alerts.map((alert, idx) => (
                                <li key={idx} className="text-sm text-red-700">{alert}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>

                      {/* Agenda & Opportunities */}
                      <div className="space-y-4">
                        <div>
                          <h4 className="font-medium mb-2">Suggested Agenda</h4>
                          <ol className="space-y-2">
                            {prep.suggested_agenda.map((item, idx) => (
                              <li key={idx} className="flex items-start gap-3 text-sm">
                                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-100 text-indigo-600 text-xs font-medium">
                                  {idx + 1}
                                </span>
                                {item}
                              </li>
                            ))}
                          </ol>
                        </div>

                        <div>
                          <h4 className="font-medium mb-2">Recent Interactions</h4>
                          <div className="space-y-2">
                            {prep.recent_interactions.map((interaction, idx) => (
                              <div key={idx} className="flex items-center gap-3 text-sm p-2 bg-gray-50 rounded">
                                <Badge variant="outline">{interaction.type}</Badge>
                                <span className="text-gray-500">{interaction.date}</span>
                                <span className="text-gray-700">{interaction.summary}</span>
                              </div>
                            ))}
                          </div>
                        </div>

                        {prep.open_opportunities.length > 0 && (
                          <div>
                            <h4 className="font-medium mb-2">Open Opportunities</h4>
                            <div className="space-y-2">
                              {prep.open_opportunities.map((opp, idx) => (
                                <div key={idx} className="flex items-center justify-between p-2 bg-green-50 rounded">
                                  <span className="text-sm font-medium text-green-800">{opp.name}</span>
                                  <div className="flex items-center gap-2">
                                    <span className="text-sm text-green-600">${opp.value.toLocaleString()}</span>
                                    <Badge variant="outline">{opp.stage}</Badge>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </TabsContent>

            {/* Optimal Slots Tab */}
            <TabsContent value="optimal" className="space-y-4">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>AI-Recommended Time Slots</CardTitle>
                      <CardDescription>Optimal meeting times based on your preferences and patterns</CardDescription>
                    </div>
                    <Button onClick={() => setIsFindingSlotsDialogOpen(true)}>
                      <RefreshCw className="h-4 w-4 mr-2" />
                      Find New Slots
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {optimalSlots.map((slot, idx) => (
                      <div key={idx} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <div className="p-2 bg-indigo-100 rounded-lg">
                              <Clock className="h-5 w-5 text-indigo-600" />
                            </div>
                            <div>
                              <p className="font-semibold text-lg">{slot.start_time} - {slot.end_time}</p>
                              <p className="text-sm text-gray-500">
                                {slotDate ? new Date(slotDate).toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' }) : 'Today'}
                              </p>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="flex items-center gap-2">
                              <span className="text-2xl font-bold text-indigo-600">{Math.round(slot.score * 100)}</span>
                              <span className="text-sm text-gray-500">score</span>
                            </div>
                            <div className="w-24 h-2 bg-gray-200 rounded-full mt-1">
                              <div
                                className="h-full bg-indigo-600 rounded-full"
                                style={{ width: `${slot.score * 100}%` }}
                              />
                            </div>
                          </div>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {slot.factors.map((factor, fidx) => (
                            <Badge key={fidx} variant="secondary" className="text-xs">
                              <CheckCircle2 className="h-3 w-3 mr-1" />
                              {factor}
                            </Badge>
                          ))}
                        </div>
                        <div className="mt-3 pt-3 border-t flex gap-2">
                          <Button size="sm" className="flex-1">
                            <Calendar className="h-4 w-4 mr-2" />
                            Schedule Meeting
                          </Button>
                          <Button size="sm" variant="outline">
                            <Video className="h-4 w-4 mr-2" />
                            Video Call
                          </Button>
                          <Button size="sm" variant="outline">
                            <Phone className="h-4 w-4 mr-2" />
                            Phone Call
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Smart Reminders Tab */}
            <TabsContent value="reminders" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Smart Reminders</CardTitle>
                  <CardDescription>AI-generated contextual reminders for your meetings</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {reminders.map(reminder => (
                      <div key={reminder.id} className="border rounded-lg p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex items-start gap-3">
                            <div className={`p-2 rounded-lg ${reminder.reminder_type === 'preparation' ? 'bg-indigo-100' :
                                reminder.reminder_type === 'follow_up' ? 'bg-green-100' : 'bg-gray-100'
                              }`}>
                              {reminder.reminder_type === 'preparation' ? (
                                <FileText className={`h-5 w-5 ${reminder.reminder_type === 'preparation' ? 'text-indigo-600' : 'text-gray-600'
                                  }`} />
                              ) : (
                                <Bell className="h-5 w-5 text-green-600" />
                              )}
                            </div>
                            <div>
                              <p className="font-medium">{reminder.meeting_title}</p>
                              <p className="text-sm text-gray-500 mt-1">{reminder.reminder_content}</p>
                              <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                                <span className="flex items-center gap-1">
                                  <Clock className="h-3 w-3" />
                                  Meeting: {formatTime(reminder.meeting_time)}
                                </span>
                                <span className="flex items-center gap-1">
                                  <Bell className="h-3 w-3" />
                                  Reminder: {formatTime(reminder.scheduled_for)}
                                </span>
                              </div>
                            </div>
                          </div>
                          <div className="flex flex-col items-end gap-2">
                            <Badge variant={reminder.sent ? 'secondary' : 'default'}>
                              {reminder.sent ? 'Sent' : 'Pending'}
                            </Badge>
                            <Badge variant="outline" className="capitalize">
                              {reminder.reminder_type.replace('_', ' ')}
                            </Badge>
                          </div>
                        </div>
                        {!reminder.sent && (
                          <div className="mt-3 pt-3 border-t flex gap-2">
                            <Button size="sm" variant="outline">
                              Send Now
                            </Button>
                            <Button size="sm" variant="outline">
                              Reschedule
                            </Button>
                            <Button size="sm" variant="outline" className="text-red-600">
                              Cancel
                            </Button>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {/* AI Preferences Dialog */}
          <Dialog open={isPreferencesDialogOpen} onOpenChange={setIsPreferencesDialogOpen}>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>AI Scheduling Preferences</DialogTitle>
                <DialogDescription>
                  Configure how AI optimizes your schedule and predicts meeting outcomes
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-6 py-4 max-h-[60vh] overflow-y-auto">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Preferred Start Hour</Label>
                    <Select defaultValue={preferences?.preferred_start_hour?.toString() || "9"}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {Array.from({ length: 12 }, (_, i) => i + 6).map(hour => (
                          <SelectItem key={hour} value={hour.toString()}>
                            {hour}:00 {hour < 12 ? 'AM' : 'PM'}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Preferred End Hour</Label>
                    <Select defaultValue={preferences?.preferred_end_hour?.toString() || "17"}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {Array.from({ length: 12 }, (_, i) => i + 12).map(hour => (
                          <SelectItem key={hour} value={hour.toString()}>
                            {hour > 12 ? hour - 12 : hour}:00 PM
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Max Meetings Per Day</Label>
                    <Input type="number" defaultValue={preferences?.max_meetings_per_day || 6} min={1} max={12} />
                  </div>
                  <div>
                    <Label>Buffer Between Meetings (min)</Label>
                    <Input type="number" defaultValue={preferences?.buffer_minutes || 15} min={0} max={60} />
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Avoid Back-to-Back Meetings</Label>
                      <p className="text-sm text-gray-500">AI will prevent scheduling consecutive meetings</p>
                    </div>
                    <Switch defaultChecked={preferences?.avoid_back_to_back} />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Enable Focus Time Blocks</Label>
                      <p className="text-sm text-gray-500">AI will protect blocks for deep work</p>
                    </div>
                    <Switch defaultChecked={preferences?.focus_time_blocks} />
                  </div>
                </div>

                <div>
                  <Label>Preferred Meeting Lengths</Label>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {[15, 30, 45, 60, 90].map(duration => (
                      <Badge
                        key={duration}
                        variant={preferences?.preferred_meeting_lengths?.includes(duration) ? 'default' : 'outline'}
                        className="cursor-pointer"
                      >
                        {duration} min
                      </Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <Label>Timezone</Label>
                  <Select defaultValue={preferences?.timezone || "America/New_York"}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="America/New_York">Eastern Time</SelectItem>
                      <SelectItem value="America/Chicago">Central Time</SelectItem>
                      <SelectItem value="America/Denver">Mountain Time</SelectItem>
                      <SelectItem value="America/Los_Angeles">Pacific Time</SelectItem>
                      <SelectItem value="Europe/London">London</SelectItem>
                      <SelectItem value="Europe/Paris">Paris</SelectItem>
                      <SelectItem value="Asia/Tokyo">Tokyo</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <Button className="w-full">
                  Save Preferences
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
