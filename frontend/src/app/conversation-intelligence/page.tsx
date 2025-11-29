"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { 
  Mic, Phone, Video, PlayCircle, PauseCircle, Clock, 
  TrendingUp, TrendingDown, AlertTriangle, CheckCircle,
  Search, Filter, Download, MessageSquare,
  Sparkles, Target, Zap, ThumbsUp, ThumbsDown
} from "lucide-react";

interface CallRecording {
  id: number;
  title: string;
  contact_name: string;
  contact_company: string;
  call_type: "inbound" | "outbound";
  duration: number;
  recorded_at: string;
  sentiment_score: number;
  talk_ratio: { rep: number; customer: number };
  keywords: string[];
  action_items: string[];
  next_steps: string[];
  transcript_available: boolean;
}

interface TeamMetric {
  rep_name: string;
  calls_count: number;
  avg_duration: number;
  avg_sentiment: number;
  talk_ratio: number;
  conversion_rate: number;
}

export default function ConversationIntelligencePage() {
  const [recordings] = useState<CallRecording[]>([
    {
      id: 1,
      title: "Discovery Call",
      contact_name: "Sarah Mitchell",
      contact_company: "TechCorp Inc.",
      call_type: "outbound",
      duration: 1847,
      recorded_at: "2025-11-29T10:30:00Z",
      sentiment_score: 78,
      talk_ratio: { rep: 35, customer: 65 },
      keywords: ["pricing", "implementation", "timeline", "ROI"],
      action_items: ["Send pricing proposal", "Schedule demo with IT team"],
      next_steps: ["Follow up on Friday", "Prepare custom demo"],
      transcript_available: true
    },
    {
      id: 2,
      title: "Demo Presentation",
      contact_name: "Michael Chen",
      contact_company: "Global Solutions",
      call_type: "outbound",
      duration: 2563,
      recorded_at: "2025-11-28T14:00:00Z",
      sentiment_score: 92,
      talk_ratio: { rep: 55, customer: 45 },
      keywords: ["features", "integration", "support", "training"],
      action_items: ["Share integration docs", "Intro to customer success"],
      next_steps: ["Send contract by EOD", "Schedule onboarding call"],
      transcript_available: true
    },
    {
      id: 3,
      title: "Objection Handling",
      contact_name: "Emily Rodriguez",
      contact_company: "StartupXYZ",
      call_type: "inbound",
      duration: 1234,
      recorded_at: "2025-11-28T09:15:00Z",
      sentiment_score: 45,
      talk_ratio: { rep: 40, customer: 60 },
      keywords: ["budget", "competitor", "concerns", "delay"],
      action_items: ["Address budget concerns", "Prepare competitor comparison"],
      next_steps: ["Send case studies", "Revisit in Q1"],
      transcript_available: true
    },
    {
      id: 4,
      title: "Closing Call",
      contact_name: "David Park",
      contact_company: "Enterprise Ltd",
      call_type: "outbound",
      duration: 987,
      recorded_at: "2025-11-27T16:45:00Z",
      sentiment_score: 95,
      talk_ratio: { rep: 30, customer: 70 },
      keywords: ["contract", "signature", "start date", "celebration"],
      action_items: ["Send final contract", "Notify customer success"],
      next_steps: ["Begin onboarding Monday", "Introduce account manager"],
      transcript_available: true
    },
  ]);

  const [teamMetrics] = useState<TeamMetric[]>([
    { rep_name: "Alex Johnson", calls_count: 45, avg_duration: 22, avg_sentiment: 76, talk_ratio: 42, conversion_rate: 28 },
    { rep_name: "Maria Garcia", calls_count: 52, avg_duration: 18, avg_sentiment: 82, talk_ratio: 38, conversion_rate: 35 },
    { rep_name: "James Wilson", calls_count: 38, avg_duration: 25, avg_sentiment: 68, talk_ratio: 55, conversion_rate: 22 },
    { rep_name: "Lisa Chen", calls_count: 61, avg_duration: 15, avg_sentiment: 85, talk_ratio: 35, conversion_rate: 42 },
  ]);

  const [isPlaying, setIsPlaying] = useState(false);

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const getSentimentColor = (score: number) => {
    if (score >= 75) return "text-green-600 dark:text-green-400";
    if (score >= 50) return "text-yellow-600 dark:text-yellow-400";
    return "text-red-600 dark:text-red-400";
  };

  const getSentimentBg = (score: number) => {
    if (score >= 75) return "bg-green-100 dark:bg-green-900/30";
    if (score >= 50) return "bg-yellow-100 dark:bg-yellow-900/30";
    return "bg-red-100 dark:bg-red-900/30";
  };

  const getSentimentIcon = (score: number) => {
    if (score >= 75) return <ThumbsUp className="w-4 h-4" />;
    if (score >= 50) return <AlertTriangle className="w-4 h-4" />;
    return <ThumbsDown className="w-4 h-4" />;
  };

  const avgSentiment = recordings.reduce((sum, r) => sum + r.sentiment_score, 0) / recordings.length;
  const totalCalls = recordings.length;
  const avgTalkRatio = recordings.reduce((sum, r) => sum + r.talk_ratio.rep, 0) / recordings.length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-violet-600 to-fuchsia-600 bg-clip-text text-transparent">
            Conversation Intelligence
          </h1>
          <p className="text-muted-foreground mt-1">
            AI-powered call recording, transcription & analysis
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Export Data
          </Button>
          <Button className="bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-700 hover:to-fuchsia-700">
            <Mic className="w-4 h-4 mr-2" />
            Start Recording
          </Button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="bg-gradient-to-br from-violet-50 to-violet-100 dark:from-violet-950/50 dark:to-violet-900/30 border-violet-200 dark:border-violet-800">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-violet-600 dark:text-violet-400">Total Calls</p>
                <p className="text-3xl font-bold text-violet-700 dark:text-violet-300">{totalCalls}</p>
              </div>
              <Phone className="w-10 h-10 text-violet-500 opacity-80" />
            </div>
            <p className="text-xs text-violet-600/70 dark:text-violet-400/70 mt-2">This week</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-950/50 dark:to-green-900/30 border-green-200 dark:border-green-800">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-green-600 dark:text-green-400">Avg Sentiment</p>
                <p className="text-3xl font-bold text-green-700 dark:text-green-300">{avgSentiment.toFixed(0)}%</p>
              </div>
              <ThumbsUp className="w-10 h-10 text-green-500 opacity-80" />
            </div>
            <p className="text-xs text-green-600/70 dark:text-green-400/70 mt-2">+5% vs last week</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950/50 dark:to-blue-900/30 border-blue-200 dark:border-blue-800">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-blue-600 dark:text-blue-400">Talk Ratio</p>
                <p className="text-3xl font-bold text-blue-700 dark:text-blue-300">{avgTalkRatio.toFixed(0)}%</p>
              </div>
              <MessageSquare className="w-10 h-10 text-blue-500 opacity-80" />
            </div>
            <p className="text-xs text-blue-600/70 dark:text-blue-400/70 mt-2">Rep talk time (ideal: 40%)</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-950/50 dark:to-orange-900/30 border-orange-200 dark:border-orange-800">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-orange-600 dark:text-orange-400">Action Items</p>
                <p className="text-3xl font-bold text-orange-700 dark:text-orange-300">
                  {recordings.reduce((sum, r) => sum + r.action_items.length, 0)}
                </p>
              </div>
              <Target className="w-10 h-10 text-orange-500 opacity-80" />
            </div>
            <p className="text-xs text-orange-600/70 dark:text-orange-400/70 mt-2">AI-extracted</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="recordings" className="space-y-4">
        <TabsList className="bg-muted/50">
          <TabsTrigger value="recordings">Recordings</TabsTrigger>
          <TabsTrigger value="insights">AI Insights</TabsTrigger>
          <TabsTrigger value="team">Team Analytics</TabsTrigger>
          <TabsTrigger value="coaching">Coaching</TabsTrigger>
        </TabsList>

        {/* Recordings Tab */}
        <TabsContent value="recordings" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Call Recordings</CardTitle>
                  <CardDescription>Review and analyze your sales conversations</CardDescription>
                </div>
                <div className="flex gap-2">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <Input placeholder="Search calls..." className="pl-9 w-[200px]" />
                  </div>
                  <Button variant="outline" size="icon">
                    <Filter className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recordings.map((recording) => (
                  <div 
                    key={recording.id} 
                    className="p-4 rounded-lg border bg-card hover:shadow-md transition-all"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex items-start gap-4">
                        <div className={`p-3 rounded-lg ${getSentimentBg(recording.sentiment_score)}`}>
                          {recording.call_type === "inbound" 
                            ? <Phone className="w-6 h-6 text-violet-600 dark:text-violet-400" />
                            : <Video className="w-6 h-6 text-violet-600 dark:text-violet-400" />
                          }
                        </div>
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-semibold">{recording.title}</h3>
                            <Badge variant="outline" className="text-xs">
                              {recording.call_type}
                            </Badge>
                          </div>
                          <div className="flex items-center gap-2 text-sm text-muted-foreground">
                            <span>{recording.contact_name}</span>
                            <span>•</span>
                            <span>{recording.contact_company}</span>
                          </div>
                          <div className="flex items-center gap-4 mt-2 text-sm">
                            <span className="flex items-center gap-1 text-muted-foreground">
                              <Clock className="w-3 h-3" />
                              {formatDuration(recording.duration)}
                            </span>
                            <span className="text-muted-foreground">
                              {new Date(recording.recorded_at).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <p className="text-sm text-muted-foreground mb-1">Sentiment</p>
                          <div className={`flex items-center gap-1 font-bold ${getSentimentColor(recording.sentiment_score)}`}>
                            {getSentimentIcon(recording.sentiment_score)}
                            {recording.sentiment_score}%
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-muted-foreground mb-1">Talk Ratio</p>
                          <div className="flex items-center gap-1">
                            <div className="w-16 h-2 rounded-full bg-muted overflow-hidden">
                              <div 
                                className="h-full bg-violet-500" 
                                style={{ width: `${recording.talk_ratio.rep}%` }}
                              />
                            </div>
                            <span className="text-sm">{recording.talk_ratio.rep}%</span>
                          </div>
                        </div>
                        <Button size="sm" variant="ghost" onClick={(e) => { e.stopPropagation(); setIsPlaying(!isPlaying); }}>
                          {isPlaying ? <PauseCircle className="w-8 h-8" /> : <PlayCircle className="w-8 h-8" />}
                        </Button>
                      </div>
                    </div>
                    
                    <div className="mt-4 flex flex-wrap gap-2">
                      {recording.keywords.map((keyword, idx) => (
                        <Badge key={idx} variant="secondary" className="text-xs">
                          {keyword}
                        </Badge>
                      ))}
                    </div>
                    
                    {recording.action_items.length > 0 && (
                      <div className="mt-3 p-3 rounded-lg bg-orange-50 dark:bg-orange-950/30">
                        <p className="text-xs font-medium text-orange-600 dark:text-orange-400 mb-1">
                          <Sparkles className="w-3 h-3 inline mr-1" />
                          AI Action Items
                        </p>
                        <ul className="text-sm text-orange-700 dark:text-orange-300 space-y-1">
                          {recording.action_items.map((item, idx) => (
                            <li key={idx}>• {item}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* AI Insights Tab */}
        <TabsContent value="insights" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-yellow-500" />
                  Key Insights
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="p-4 rounded-lg bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-800">
                  <div className="flex items-start gap-3">
                    <TrendingUp className="w-5 h-5 text-green-600 mt-0.5" />
                    <div>
                      <p className="font-medium text-green-700 dark:text-green-300">Positive Trend</p>
                      <p className="text-sm text-green-600/80 dark:text-green-400/80">
                        Customer sentiment improved 15% this week. Demo calls show highest engagement.
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="p-4 rounded-lg bg-yellow-50 dark:bg-yellow-950/30 border border-yellow-200 dark:border-yellow-800">
                  <div className="flex items-start gap-3">
                    <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
                    <div>
                      <p className="font-medium text-yellow-700 dark:text-yellow-300">Attention Needed</p>
                      <p className="text-sm text-yellow-600/80 dark:text-yellow-400/80">
                        3 calls mentioned competitor pricing. Consider preparing objection responses.
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="p-4 rounded-lg bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800">
                  <div className="flex items-start gap-3">
                    <Zap className="w-5 h-5 text-blue-600 mt-0.5" />
                    <div>
                      <p className="font-medium text-blue-700 dark:text-blue-300">Quick Win</p>
                      <p className="text-sm text-blue-600/80 dark:text-blue-400/80">
                        Integration questions came up in 80% of calls. Add to demo script.
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Top Keywords This Week</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {[
                    { keyword: "pricing", count: 24, trend: "up" },
                    { keyword: "integration", count: 18, trend: "up" },
                    { keyword: "timeline", count: 15, trend: "neutral" },
                    { keyword: "support", count: 12, trend: "down" },
                    { keyword: "competitor", count: 8, trend: "up" },
                  ].map((item, idx) => (
                    <div key={idx} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="text-lg font-mono text-muted-foreground">#{idx + 1}</span>
                        <span className="font-medium">{item.keyword}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-muted-foreground">{item.count} mentions</span>
                        {item.trend === "up" && <TrendingUp className="w-4 h-4 text-green-500" />}
                        {item.trend === "down" && <TrendingDown className="w-4 h-4 text-red-500" />}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Team Analytics Tab */}
        <TabsContent value="team" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Team Performance</CardTitle>
              <CardDescription>Compare conversation metrics across your team</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {teamMetrics.map((metric, idx) => (
                  <div key={idx} className="p-4 rounded-lg border bg-card">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <Avatar>
                          <AvatarFallback>{metric.rep_name.split(" ").map(n => n[0]).join("")}</AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="font-semibold">{metric.rep_name}</p>
                          <p className="text-sm text-muted-foreground">{metric.calls_count} calls this week</p>
                        </div>
                      </div>
                      <Badge className={metric.conversion_rate >= 30 ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}>
                        {metric.conversion_rate}% conversion
                      </Badge>
                    </div>
                    
                    <div className="grid grid-cols-4 gap-4">
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">Avg Duration</p>
                        <p className="font-semibold">{metric.avg_duration} min</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">Sentiment</p>
                        <div className="flex items-center gap-1">
                          <Progress value={metric.avg_sentiment} className="h-2 flex-1" />
                          <span className="text-sm font-medium">{metric.avg_sentiment}%</span>
                        </div>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">Talk Ratio</p>
                        <div className="flex items-center gap-1">
                          <Progress value={metric.talk_ratio} className="h-2 flex-1" />
                          <span className="text-sm font-medium">{metric.talk_ratio}%</span>
                        </div>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">Calls</p>
                        <p className="font-semibold">{metric.calls_count}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Coaching Tab */}
        <TabsContent value="coaching" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="w-5 h-5" />
                  Coaching Opportunities
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {[
                  { rep: "James Wilson", issue: "High talk ratio (55%)", suggestion: "Practice active listening techniques", priority: "high" },
                  { rep: "Alex Johnson", issue: "Missed closing signals", suggestion: "Review closing call recordings", priority: "medium" },
                  { rep: "Maria Garcia", issue: "Long discovery calls", suggestion: "Use BANT framework", priority: "low" },
                ].map((item, idx) => (
                  <div key={idx} className="p-4 rounded-lg border">
                    <div className="flex items-center justify-between mb-2">
                      <p className="font-medium">{item.rep}</p>
                      <Badge variant={item.priority === "high" ? "destructive" : item.priority === "medium" ? "default" : "secondary"}>
                        {item.priority}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">{item.issue}</p>
                    <p className="text-sm text-violet-600 dark:text-violet-400">
                      💡 {item.suggestion}
                    </p>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  Best Practices Library
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {[
                  { title: "Perfect Discovery Call", rep: "Lisa Chen", sentiment: 95, duration: "18:32" },
                  { title: "Objection Handling Master", rep: "Maria Garcia", sentiment: 88, duration: "12:45" },
                  { title: "Smooth Closing Technique", rep: "David Park", sentiment: 92, duration: "15:20" },
                ].map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 rounded-lg bg-muted/50 hover:bg-muted cursor-pointer transition-colors">
                    <div className="flex items-center gap-3">
                      <PlayCircle className="w-8 h-8 text-violet-500" />
                      <div>
                        <p className="font-medium">{item.title}</p>
                        <p className="text-sm text-muted-foreground">by {item.rep}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge className="bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">
                        {item.sentiment}% sentiment
                      </Badge>
                      <p className="text-xs text-muted-foreground mt-1">{item.duration}</p>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
