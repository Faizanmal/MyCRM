'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  Mic,
  Phone,
  PhoneIncoming,
  PhoneOutgoing,
  Play,
  Pause,
  Clock,
  User,
  FileText,
  CheckCircle2,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Sparkles,
  Target,
  BarChart3,
  Activity,
  MessageSquare,
  ThumbsUp,
  ThumbsDown,
  Minus,
  Download,
  Search,
  RefreshCw,
  Volume2,
  Settings,
  Calendar,
  Zap,
  Brain
} from 'lucide-react';

import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
// import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
// import { Label } from '@/components/ui/label';
// import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
// import { Textarea } from '@/components/ui/textarea';
import { Progress } from '@/components/ui/progress';
import { voiceIntelligenceAPI } from '@/lib/ai-workflow-api';

interface VoiceRecording {
  id: number;
  call_id: string;
  contact_name?: string;
  company_name?: string;
  direction: 'inbound' | 'outbound';
  duration_seconds: number;
  recording_url: string;
  call_start_time: string;
  call_end_time: string;
  phone_number: string;
  user_name: string;
  status: string;
  transcription_status: string;
  ai_processed: boolean;
}

interface Transcription {
  id: number;
  recording_id: number;
  full_transcript: string;
  speaker_segments: SpeakerSegment[];
  key_phrases: string[];
  mentioned_competitors: string[];
  mentioned_products: string[];
  questions_asked: string[];
  objections_raised: string[];
  word_count: number;
  processing_time: number;
}

interface SpeakerSegment {
  speaker: string;
  start_time: number;
  end_time: number;
  text: string;
  confidence: number;
}

interface AISummary {
  id: number;
  recording_id: number;
  summary: string;
  key_points: string[];
  sentiment_overall: 'positive' | 'neutral' | 'negative';
  sentiment_score: number;
  engagement_score: number;
  talk_ratio: { rep: number; customer: number };
  topics_discussed: string[];
  customer_mood_progression: string[];
  recommendations: string[];
  generated_at: string;
}

interface ActionItem {
  id: number;
  recording_id: number;
  description: string;
  assigned_to?: string;
  due_date?: string;
  priority: 'high' | 'medium' | 'low';
  status: 'pending' | 'completed' | 'cancelled';
  created_at: string;
  ai_confidence: number;
}

interface CallScore {
  id: number;
  recording_id: number;
  overall_score: number;
  opening_score: number;
  discovery_score: number;
  presentation_score: number;
  objection_handling_score: number;
  closing_score: number;
  criteria_scores: Record<string, number>;
  strengths: string[];
  areas_for_improvement: string[];
  coaching_tips: string[];
}

interface CallAnalytics {
  total_calls: number;
  total_duration_minutes: number;
  avg_call_duration: number;
  avg_sentiment_score: number;
  avg_engagement_score: number;
  avg_call_score: number;
  calls_by_direction: { inbound: number; outbound: number };
  calls_by_sentiment: { positive: number; neutral: number; negative: number };
  top_topics: { topic: string; count: number }[];
  top_competitors_mentioned: { name: string; count: number }[];
}

export default function VoiceIntelligencePage() {
  const [recordings, setRecordings] = useState<VoiceRecording[]>([]);
  const [selectedRecording, setSelectedRecording] = useState<VoiceRecording | null>(null);
  const [transcription, setTranscription] = useState<Transcription | null>(null);
  const [summary, setSummary] = useState<AISummary | null>(null);
  const [actionItems, setActionItems] = useState<ActionItem[]>([]);
  const [callScore, setCallScore] = useState<CallScore | null>(null);
  const [analytics, setAnalytics] = useState<CallAnalytics | null>(null);
  const [, setLoading] = useState(true);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const loadDemoData = () => {
    const now = Date.now();
    setRecordings([
      {
        id: 1,
        call_id: 'CALL-001',
        contact_name: 'John Smith',
        company_name: 'TechCorp Inc',
        direction: 'outbound',
        duration_seconds: 1845,
        recording_url: '/recordings/call-001.mp3',
        call_start_time: new Date(now - 7200000).toISOString(),
        call_end_time: new Date(now - 5355000).toISOString(),
        phone_number: '+1 (555) 123-4567',
        user_name: 'Sarah Johnson',
        status: 'completed',
        transcription_status: 'completed',
        ai_processed: true
      },
      {
        id: 2,
        call_id: 'CALL-002',
        contact_name: 'Emily Davis',
        company_name: 'StartupXYZ',
        direction: 'inbound',
        duration_seconds: 923,
        recording_url: '/recordings/call-002.mp3',
        call_start_time: new Date(now - 86400000).toISOString(),
        call_end_time: new Date(now - 85477000).toISOString(),
        phone_number: '+1 (555) 987-6543',
        user_name: 'Mike Wilson',
        status: 'completed',
        transcription_status: 'completed',
        ai_processed: true
      },
      {
        id: 3,
        call_id: 'CALL-003',
        contact_name: 'Robert Chen',
        company_name: 'Enterprise Solutions',
        direction: 'outbound',
        duration_seconds: 2156,
        recording_url: '/recordings/call-003.mp3',
        call_start_time: new Date(now - 172800000).toISOString(),
        call_end_time: new Date(now - 170644000).toISOString(),
        phone_number: '+1 (555) 456-7890',
        user_name: 'Sarah Johnson',
        status: 'completed',
        transcription_status: 'processing',
        ai_processed: false
      }
    ]);
  };

  const fetchRecordings = useCallback(async () => {
    // Defer setting loading to avoid synchronous setState inside useEffect
    Promise.resolve().then(() => setLoading(true));
    try {
      const response = await voiceIntelligenceAPI.getRecordings();
      setRecordings(response.data.results || []);
      if ((response.data.results || []).length === 0) {
        loadDemoData();
      }
    } catch (error) {
      console.error('Failed to fetch recordings:', error);
      loadDemoData();
    }
    setLoading(false);
  }, []);

  const loadDemoAnalytics = () => {
    setAnalytics({
      total_calls: 156,
      total_duration_minutes: 4280,
      avg_call_duration: 27.4,
      avg_sentiment_score: 72,
      avg_engagement_score: 78,
      avg_call_score: 75,
      calls_by_direction: { inbound: 45, outbound: 111 },
      calls_by_sentiment: { positive: 89, neutral: 52, negative: 15 },
      top_topics: [
        { topic: 'Pricing', count: 78 },
        { topic: 'Product Features', count: 65 },
        { topic: 'Integration', count: 54 },
        { topic: 'Support', count: 42 },
        { topic: 'Implementation', count: 38 }
      ],
      top_competitors_mentioned: [
        { name: 'Salesforce', count: 32 },
        { name: 'HubSpot', count: 28 },
        { name: 'Pipedrive', count: 15 }
      ]
    });
  };

  const selectRecording = async (recording: VoiceRecording) => {
    setSelectedRecording(recording);

    // Load demo transcription and summary
    setTranscription({
      id: 1,
      recording_id: recording.id,
      full_transcript: `Sarah: Hi John, thanks for taking my call today. How are you doing?

John: I'm doing well, Sarah. Thanks for reaching out. I've been looking forward to learning more about your CRM solution.

Sarah: Great! I understand you're currently evaluating different options for your sales team. Can you tell me a bit about your current setup and what challenges you're facing?

John: Sure. We're using spreadsheets right now, and it's becoming unmanageable. We have about 50 sales reps and tracking everything manually is a nightmare.

Sarah: I completely understand. That's actually a very common challenge we help solve. Our CRM is specifically designed for teams your size. Would it help if I walked you through how we handle lead tracking and pipeline management?

John: Yes, that would be great. Also, I'm curious about pricing - we're working with a limited budget this quarter.

Sarah: Absolutely, I'll cover pricing as well. Let me share my screen and show you the main features...`,
      speaker_segments: [
        { speaker: 'Sarah', start_time: 0, end_time: 15, text: "Hi John, thanks for taking my call today. How are you doing?", confidence: 0.95 },
        { speaker: 'John', start_time: 16, end_time: 35, text: "I'm doing well, Sarah. Thanks for reaching out. I've been looking forward to learning more about your CRM solution.", confidence: 0.92 },
      ],
      key_phrases: ['CRM solution', 'sales team', 'lead tracking', 'pipeline management', 'limited budget'],
      mentioned_competitors: [],
      mentioned_products: ['CRM', 'lead tracking', 'pipeline management'],
      questions_asked: ['What challenges are you facing?', 'Would a demo help?'],
      objections_raised: ['Working with limited budget'],
      word_count: 245,
      processing_time: 12.5
    });

    setSummary({
      id: 1,
      recording_id: recording.id,
      summary: "Discovery call with John Smith from TechCorp Inc. The prospect is currently using spreadsheets to manage their 50-person sales team and is experiencing significant pain points with manual tracking. They're actively evaluating CRM solutions but have budget constraints this quarter. Sarah successfully identified key pain points and scheduled a demo to show lead tracking and pipeline management features.",
      key_points: [
        'Prospect has 50 sales reps using spreadsheets',
        'Major pain point: manual tracking is unmanageable',
        'Budget constraints this quarter',
        'Interested in lead tracking and pipeline features',
        'Scheduled product demo'
      ],
      sentiment_overall: 'positive',
      sentiment_score: 78,
      engagement_score: 85,
      talk_ratio: { rep: 45, customer: 55 },
      topics_discussed: ['Current challenges', 'Team size', 'CRM features', 'Pricing concerns', 'Product demo'],
      customer_mood_progression: ['interested', 'engaged', 'curious about pricing', 'optimistic'],
      recommendations: [
        'Prepare ROI analysis for follow-up',
        'Highlight cost-saving features in demo',
        'Send case study from similar-sized company',
        'Address budget concerns with flexible pricing options'
      ],
      generated_at: new Date().toISOString()
    });

    setActionItems([
      {
        id: 1,
        recording_id: recording.id,
        description: 'Send product demo recording and follow-up materials',
        assigned_to: 'Sarah Johnson',
        due_date: new Date(new Date().getTime() + 86400000).toISOString(),
        priority: 'high',
        status: 'pending',
        created_at: new Date().toISOString(),
        ai_confidence: 0.95
      },
      {
        id: 2,
        recording_id: recording.id,
        description: 'Prepare ROI analysis comparing spreadsheet vs CRM costs',
        assigned_to: 'Sarah Johnson',
        due_date: new Date(new Date().getTime() + 172800000).toISOString(),
        priority: 'high',
        status: 'pending',
        created_at: new Date().toISOString(),
        ai_confidence: 0.88
      },
      {
        id: 3,
        recording_id: recording.id,
        description: 'Find and send case study from 50+ seat deployment',
        assigned_to: 'Sarah Johnson',
        due_date: new Date(new Date().getTime() + 86400000).toISOString(),
        priority: 'medium',
        status: 'pending',
        created_at: new Date().toISOString(),
        ai_confidence: 0.82
      }
    ]);

    setCallScore({
      id: 1,
      recording_id: recording.id,
      overall_score: 82,
      opening_score: 90,
      discovery_score: 85,
      presentation_score: 78,
      objection_handling_score: 75,
      closing_score: 80,
      criteria_scores: {
        'Active Listening': 88,
        'Question Quality': 82,
        'Value Proposition': 79,
        'Next Steps': 85,
        'Rapport Building': 91
      },
      strengths: [
        'Excellent rapport building and warm opening',
        'Good discovery questions about current pain points',
        'Clear next steps established',
        'Professional and empathetic tone'
      ],
      areas_for_improvement: [
        'Could have probed deeper on budget specifics',
        'Missed opportunity to quantify pain point costs',
        'Presentation could include more customer success stories'
      ],
      coaching_tips: [
        'Try using the "impact" question: "What does this cost your team in hours/dollars?"',
        'When budget concerns arise, pivot to ROI discussion earlier',
        'Include a brief competitor comparison to address potential objections'
      ]
    });
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return <ThumbsUp className="h-4 w-4 text-green-500" />;
      case 'negative': return <ThumbsDown className="h-4 w-4 text-red-500" />;
      default: return <Minus className="h-4 w-4 text-gray-500" />;
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'bg-green-100 text-green-700';
      case 'negative': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-700';
      case 'medium': return 'bg-yellow-100 text-yellow-700';
      default: return 'bg-green-100 text-green-700';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  useEffect(() => {
    // Defer calls to avoid synchronous setState inside effect
    Promise.resolve().then(() => {
      fetchRecordings();
      loadDemoAnalytics();
    });
  }, [fetchRecordings]);

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-6 space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold flex items-center gap-2">
                <Mic className="h-8 w-8 text-violet-600" />
                Voice Intelligence
              </h1>
              <p className="text-gray-500 mt-1">
                AI-powered call transcription, analysis, and coaching
              </p>
            </div>
            <div className="flex gap-3">
              <Button variant="outline" onClick={fetchRecordings}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
              <Button>
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </Button>
            </div>
          </div>

          {/* Stats Cards */}
          {analytics && (
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500">Total Calls</p>
                      <p className="text-2xl font-bold">{analytics.total_calls}</p>
                    </div>
                    <Phone className="h-8 w-8 text-blue-500" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500">Avg Duration</p>
                      <p className="text-2xl font-bold">{analytics.avg_call_duration.toFixed(1)}m</p>
                    </div>
                    <Clock className="h-8 w-8 text-indigo-500" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500">Avg Sentiment</p>
                      <p className={`text-2xl font-bold ${getScoreColor(analytics.avg_sentiment_score)}`}>
                        {analytics.avg_sentiment_score}%
                      </p>
                    </div>
                    <Activity className="h-8 w-8 text-green-500" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500">Avg Call Score</p>
                      <p className={`text-2xl font-bold ${getScoreColor(analytics.avg_call_score)}`}>
                        {analytics.avg_call_score}
                      </p>
                    </div>
                    <Target className="h-8 w-8 text-violet-500" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500">Engagement</p>
                      <p className={`text-2xl font-bold ${getScoreColor(analytics.avg_engagement_score)}`}>
                        {analytics.avg_engagement_score}%
                      </p>
                    </div>
                    <Zap className="h-8 w-8 text-yellow-500" />
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Main Content */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Recordings List */}
            <Card className="lg:col-span-1">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Volume2 className="h-5 w-5" />
                  Call Recordings
                </CardTitle>
                <div className="relative mt-2">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search calls..."
                    className="pl-9"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 max-h-[600px] overflow-y-auto">
                  {recordings.map(recording => (
                    <div
                      key={recording.id}
                      className={`p-3 border rounded-lg cursor-pointer transition-colors ${selectedRecording?.id === recording.id ? 'border-violet-500 bg-violet-50' : 'hover:bg-gray-50'
                        }`}
                      onClick={() => selectRecording(recording)}
                      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { selectRecording(recording); e.preventDefault(); } }}
                      tabIndex={0}
                      role="button"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          {recording.direction === 'inbound' ? (
                            <PhoneIncoming className="h-4 w-4 text-green-500" />
                          ) : (
                            <PhoneOutgoing className="h-4 w-4 text-blue-500" />
                          )}
                          <span className="font-medium text-sm">{recording.contact_name}</span>
                        </div>
                        {recording.ai_processed && (
                          <Badge variant="secondary" className="text-xs">
                            <Brain className="h-3 w-3 mr-1" />
                            AI
                          </Badge>
                        )}
                      </div>
                      <p className="text-xs text-gray-500 mb-1">{recording.company_name}</p>
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {formatDuration(recording.duration_seconds)}
                        </span>
                        <span>{new Date(recording.call_start_time).toLocaleDateString()}</span>
                      </div>
                      <div className="mt-2 flex items-center gap-2">
                        <Badge variant="outline" className="text-xs capitalize">{recording.direction}</Badge>
                        <Badge
                          variant="outline"
                          className={`text-xs ${recording.transcription_status === 'completed' ? 'text-green-600' : 'text-yellow-600'
                            }`}
                        >
                          {recording.transcription_status}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Recording Details */}
            <Card className="lg:col-span-2">
              {selectedRecording ? (
                <>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div>
                        <CardTitle className="flex items-center gap-2">
                          {selectedRecording.contact_name}
                          {summary && (
                            <Badge className={getSentimentColor(summary.sentiment_overall)}>
                              {getSentimentIcon(summary.sentiment_overall)}
                              <span className="ml-1 capitalize">{summary.sentiment_overall}</span>
                            </Badge>
                          )}
                        </CardTitle>
                        <CardDescription className="mt-1">
                          {selectedRecording.company_name} • {selectedRecording.phone_number}
                        </CardDescription>
                      </div>
                      <div className="flex gap-2">
                        <Button size="sm" variant="outline">
                          <Download className="h-4 w-4 mr-1" />
                          Export
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => setIsPlayingAudio(!isPlayingAudio)}>
                          {isPlayingAudio ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                        </Button>
                      </div>
                    </div>
                    <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
                      <span className="flex items-center gap-1">
                        <User className="h-4 w-4" />
                        {selectedRecording.user_name}
                      </span>
                      <span className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        {new Date(selectedRecording.call_start_time).toLocaleString()}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        {formatDuration(selectedRecording.duration_seconds)}
                      </span>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <Tabs defaultValue="summary">
                      <TabsList className="grid w-full grid-cols-5">
                        <TabsTrigger value="summary">Summary</TabsTrigger>
                        <TabsTrigger value="transcript">Transcript</TabsTrigger>
                        <TabsTrigger value="actions">Actions</TabsTrigger>
                        <TabsTrigger value="score">Call Score</TabsTrigger>
                        <TabsTrigger value="coaching">Coaching</TabsTrigger>
                      </TabsList>

                      {/* Summary Tab */}
                      <TabsContent value="summary" className="space-y-4">
                        {summary && (
                          <>
                            <div className="p-4 bg-gray-50 rounded-lg">
                              <h4 className="font-medium mb-2 flex items-center gap-2">
                                <Sparkles className="h-4 w-4 text-violet-500" />
                                AI Summary
                              </h4>
                              <p className="text-sm text-gray-700">{summary.summary}</p>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                              <div className="p-4 border rounded-lg">
                                <h4 className="font-medium mb-2">Key Points</h4>
                                <ul className="space-y-2">
                                  {summary.key_points.map((point, idx) => (
                                    <li key={idx} className="flex items-start gap-2 text-sm">
                                      <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5" />
                                      {point}
                                    </li>
                                  ))}
                                </ul>
                              </div>

                              <div className="space-y-4">
                                <div className="p-4 border rounded-lg">
                                  <h4 className="font-medium mb-2">Talk Ratio</h4>
                                  <div className="flex items-center gap-2">
                                    <div className="flex-1">
                                      <div className="flex justify-between text-xs mb-1">
                                        <span>Rep: {summary.talk_ratio.rep}%</span>
                                        <span>Customer: {summary.talk_ratio.customer}%</span>
                                      </div>
                                      <div className="w-full h-3 bg-gray-200 rounded-full flex overflow-hidden">
                                        <div
                                          className="bg-violet-500 h-full"
                                          style={{ width: `${summary.talk_ratio.rep}%` }}
                                        />
                                        <div
                                          className="bg-blue-500 h-full"
                                          style={{ width: `${summary.talk_ratio.customer}%` }}
                                        />
                                      </div>
                                    </div>
                                  </div>
                                </div>

                                <div className="p-4 border rounded-lg">
                                  <h4 className="font-medium mb-2">Scores</h4>
                                  <div className="grid grid-cols-2 gap-2">
                                    <div>
                                      <p className="text-xs text-gray-500">Sentiment</p>
                                      <p className={`text-lg font-semibold ${getScoreColor(summary.sentiment_score)}`}>
                                        {summary.sentiment_score}%
                                      </p>
                                    </div>
                                    <div>
                                      <p className="text-xs text-gray-500">Engagement</p>
                                      <p className={`text-lg font-semibold ${getScoreColor(summary.engagement_score)}`}>
                                        {summary.engagement_score}%
                                      </p>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            </div>

                            <div className="p-4 border rounded-lg">
                              <h4 className="font-medium mb-2">Topics Discussed</h4>
                              <div className="flex flex-wrap gap-2">
                                {summary.topics_discussed.map((topic, idx) => (
                                  <Badge key={idx} variant="secondary">{topic}</Badge>
                                ))}
                              </div>
                            </div>

                            <div className="p-4 bg-violet-50 rounded-lg">
                              <h4 className="font-medium mb-2 flex items-center gap-2">
                                <Target className="h-4 w-4 text-violet-600" />
                                Recommendations
                              </h4>
                              <ul className="space-y-2">
                                {summary.recommendations.map((rec, idx) => (
                                  <li key={idx} className="flex items-start gap-2 text-sm text-violet-800">
                                    <Sparkles className="h-4 w-4 text-violet-500 mt-0.5" />
                                    {rec}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          </>
                        )}
                      </TabsContent>

                      {/* Transcript Tab */}
                      <TabsContent value="transcript" className="space-y-4">
                        {transcription && (
                          <>
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-4 text-sm text-gray-500">
                                <span>{transcription.word_count} words</span>
                                <span>Processed in {transcription.processing_time}s</span>
                              </div>
                              <Button size="sm" variant="outline">
                                <Download className="h-4 w-4 mr-1" />
                                Download
                              </Button>
                            </div>

                            <div className="p-4 border rounded-lg max-h-100 overflow-y-auto">
                              <pre className="whitespace-pre-wrap text-sm font-sans">
                                {transcription.full_transcript}
                              </pre>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                              <div className="p-4 border rounded-lg">
                                <h4 className="font-medium mb-2">Key Phrases</h4>
                                <div className="flex flex-wrap gap-1">
                                  {transcription.key_phrases.map((phrase, idx) => (
                                    <Badge key={idx} variant="outline" className="text-xs">{phrase}</Badge>
                                  ))}
                                </div>
                              </div>

                              <div className="p-4 border rounded-lg">
                                <h4 className="font-medium mb-2">Objections Raised</h4>
                                <ul className="space-y-1">
                                  {transcription.objections_raised.map((obj, idx) => (
                                    <li key={idx} className="flex items-center gap-2 text-sm text-yellow-700">
                                      <AlertTriangle className="h-3 w-3" />
                                      {obj}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            </div>
                          </>
                        )}
                      </TabsContent>

                      {/* Actions Tab */}
                      <TabsContent value="actions" className="space-y-4">
                        <div className="flex items-center justify-between">
                          <h4 className="font-medium">AI-Generated Action Items</h4>
                          <Button size="sm">
                            <CheckCircle2 className="h-4 w-4 mr-1" />
                            Add Action
                          </Button>
                        </div>
                        {actionItems.map(action => (
                          <div key={action.id} className="border rounded-lg p-4">
                            <div className="flex items-start justify-between mb-2">
                              <div className="flex items-start gap-3">
                                <input
                                  type="checkbox"
                                  checked={action.status === 'completed'}
                                  className="mt-1 h-4 w-4 rounded border-gray-300"
                                  onChange={() => { /* TODO: implement action status toggle */ }}
                                />
                                <div>
                                  <p className={`font-medium ${action.status === 'completed' ? 'line-through text-gray-400' : ''}`}>
                                    {action.description}
                                  </p>
                                  <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                                    {action.assigned_to && (
                                      <span className="flex items-center gap-1">
                                        <User className="h-3 w-3" />
                                        {action.assigned_to}
                                      </span>
                                    )}
                                    {action.due_date && (
                                      <span className="flex items-center gap-1">
                                        <Calendar className="h-3 w-3" />
                                        Due: {new Date(action.due_date).toLocaleDateString()}
                                      </span>
                                    )}
                                  </div>
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                <Badge className={getPriorityColor(action.priority)}>
                                  {action.priority}
                                </Badge>
                                <span className="text-xs text-gray-400">
                                  AI: {Math.round(action.ai_confidence * 100)}%
                                </span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </TabsContent>

                      {/* Call Score Tab */}
                      <TabsContent value="score" className="space-y-4">
                        {callScore && (
                          <>
                            <div className="text-center py-6">
                              <div className={`inline-flex items-center justify-center w-24 h-24 rounded-full ${callScore.overall_score >= 80 ? 'bg-green-100' :
                                  callScore.overall_score >= 60 ? 'bg-yellow-100' : 'bg-red-100'
                                }`}>
                                <span className={`text-3xl font-bold ${getScoreColor(callScore.overall_score)}`}>
                                  {callScore.overall_score}
                                </span>
                              </div>
                              <p className="mt-2 font-medium">Overall Call Score</p>
                            </div>

                            <div className="grid grid-cols-5 gap-4">
                              {[
                                { label: 'Opening', score: callScore.opening_score },
                                { label: 'Discovery', score: callScore.discovery_score },
                                { label: 'Presentation', score: callScore.presentation_score },
                                { label: 'Objections', score: callScore.objection_handling_score },
                                { label: 'Closing', score: callScore.closing_score }
                              ].map((item, idx) => (
                                <div key={idx} className="text-center p-3 border rounded-lg">
                                  <p className={`text-2xl font-semibold ${getScoreColor(item.score)}`}>
                                    {item.score}
                                  </p>
                                  <p className="text-xs text-gray-500">{item.label}</p>
                                </div>
                              ))}
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                              <div className="p-4 border rounded-lg">
                                <h4 className="font-medium mb-2 flex items-center gap-2">
                                  <TrendingUp className="h-4 w-4 text-green-500" />
                                  Strengths
                                </h4>
                                <ul className="space-y-2">
                                  {callScore.strengths.map((strength, idx) => (
                                    <li key={idx} className="flex items-start gap-2 text-sm text-green-700">
                                      <CheckCircle2 className="h-4 w-4 mt-0.5" />
                                      {strength}
                                    </li>
                                  ))}
                                </ul>
                              </div>

                              <div className="p-4 border rounded-lg">
                                <h4 className="font-medium mb-2 flex items-center gap-2">
                                  <TrendingDown className="h-4 w-4 text-yellow-500" />
                                  Areas for Improvement
                                </h4>
                                <ul className="space-y-2">
                                  {callScore.areas_for_improvement.map((area, idx) => (
                                    <li key={idx} className="flex items-start gap-2 text-sm text-yellow-700">
                                      <AlertTriangle className="h-4 w-4 mt-0.5" />
                                      {area}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            </div>
                          </>
                        )}
                      </TabsContent>

                      {/* Coaching Tab */}
                      <TabsContent value="coaching" className="space-y-4">
                        {callScore && (
                          <>
                            <div className="p-4 bg-violet-50 rounded-lg">
                              <h4 className="font-medium mb-3 flex items-center gap-2">
                                <Brain className="h-5 w-5 text-violet-600" />
                                AI Coaching Tips
                              </h4>
                              <ul className="space-y-3">
                                {callScore.coaching_tips.map((tip, idx) => (
                                  <li key={idx} className="flex items-start gap-3 p-3 bg-white rounded-lg">
                                    <div className="flex items-center justify-center w-6 h-6 rounded-full bg-violet-100 text-violet-600 text-sm font-medium">
                                      {idx + 1}
                                    </div>
                                    <span className="text-sm text-gray-700">{tip}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>

                            <div className="p-4 border rounded-lg">
                              <h4 className="font-medium mb-3">Skill Breakdown</h4>
                              <div className="space-y-3">
                                {Object.entries(callScore.criteria_scores).map(([skill, score]) => (
                                  <div key={skill}>
                                    <div className="flex justify-between mb-1">
                                      <span className="text-sm">{skill}</span>
                                      <span className={`text-sm font-medium ${getScoreColor(score)}`}>
                                        {score}%
                                      </span>
                                    </div>
                                    <Progress value={score} />
                                  </div>
                                ))}
                              </div>
                            </div>

                            <div className="flex gap-4">
                              <Button className="flex-1">
                                <MessageSquare className="h-4 w-4 mr-2" />
                                Request 1:1 Coaching
                              </Button>
                              <Button variant="outline" className="flex-1">
                                <FileText className="h-4 w-4 mr-2" />
                                View Training Resources
                              </Button>
                            </div>
                          </>
                        )}
                      </TabsContent>
                    </Tabs>
                  </CardContent>
                </>
              ) : (
                <CardContent className="flex flex-col items-center justify-center h-[600px] text-gray-500">
                  <Mic className="h-16 w-16 mb-4 text-gray-300" />
                  <p className="text-lg font-medium">Select a recording to view details</p>
                  <p className="text-sm">Click on a call recording from the list to see AI analysis</p>
                </CardContent>
              )}
            </Card>
          </div>

          {/* Analytics Section */}
          {analytics && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5" />
                    Calls by Direction
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <PhoneOutgoing className="h-4 w-4 text-blue-500" />
                        <span>Outbound</span>
                      </div>
                      <span className="font-semibold">{analytics.calls_by_direction.outbound}</span>
                    </div>
                    <Progress
                      value={(analytics.calls_by_direction.outbound / analytics.total_calls) * 100}
                      className="h-2"
                    />
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <PhoneIncoming className="h-4 w-4 text-green-500" />
                        <span>Inbound</span>
                      </div>
                      <span className="font-semibold">{analytics.calls_by_direction.inbound}</span>
                    </div>
                    <Progress
                      value={(analytics.calls_by_direction.inbound / analytics.total_calls) * 100}
                      className="h-2"
                    />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-5 w-5" />
                    Top Topics
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {analytics.top_topics.slice(0, 5).map((topic, idx) => (
                      <div key={idx} className="flex items-center justify-between">
                        <span className="text-sm">{topic.topic}</span>
                        <Badge variant="secondary">{topic.count}</Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="h-5 w-5" />
                    Sentiment Distribution
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <ThumbsUp className="h-4 w-4 text-green-500" />
                        <span>Positive</span>
                      </div>
                      <span className="font-semibold text-green-600">{analytics.calls_by_sentiment.positive}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Minus className="h-4 w-4 text-gray-500" />
                        <span>Neutral</span>
                      </div>
                      <span className="font-semibold text-gray-600">{analytics.calls_by_sentiment.neutral}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <ThumbsDown className="h-4 w-4 text-red-500" />
                        <span>Negative</span>
                      </div>
                      <span className="font-semibold text-red-600">{analytics.calls_by_sentiment.negative}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}

