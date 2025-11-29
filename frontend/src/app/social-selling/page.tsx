"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Progress } from "@/components/ui/progress";
import { 
  Share2, Linkedin, Twitter, Users, TrendingUp, MessageSquare, 
  Heart, Repeat2, Eye, Send, Calendar, Search, UserPlus, Target,
  BarChart3, Clock, Sparkles, Globe, CheckCircle, AlertCircle
} from "lucide-react";

interface SocialProfile {
  id: number;
  platform: string;
  username: string;
  followers: number;
  engagement_rate: number;
  connected: boolean;
  last_sync: string;
}

interface SocialPost {
  id: number;
  platform: string;
  content: string;
  status: string;
  scheduled_at: string | null;
  published_at: string | null;
  likes: number;
  comments: number;
  shares: number;
  impressions: number;
}

interface LeadFromSocial {
  id: number;
  name: string;
  platform: string;
  profile_url: string;
  engagement_score: number;
  last_interaction: string;
  status: string;
}

export default function SocialSellingPage() {
  const [profiles] = useState<SocialProfile[]>([
    { id: 1, platform: "linkedin", username: "company-page", followers: 15420, engagement_rate: 4.2, connected: true, last_sync: "2025-11-29T10:00:00Z" },
    { id: 2, platform: "twitter", username: "@companyhandle", followers: 8750, engagement_rate: 3.8, connected: true, last_sync: "2025-11-29T09:30:00Z" },
  ]);
  
  const [posts] = useState<SocialPost[]>([
    { id: 1, platform: "linkedin", content: "Excited to announce our new AI-powered CRM features! 🚀", status: "published", scheduled_at: null, published_at: "2025-11-28T14:00:00Z", likes: 245, comments: 32, shares: 18, impressions: 4520 },
    { id: 2, platform: "twitter", content: "How are you leveraging AI in your sales process? Let us know! #SalesTech #AI", status: "published", scheduled_at: null, published_at: "2025-11-27T16:30:00Z", likes: 89, comments: 15, shares: 24, impressions: 2180 },
    { id: 3, platform: "linkedin", content: "Join our upcoming webinar on modern sales strategies...", status: "scheduled", scheduled_at: "2025-12-01T10:00:00Z", published_at: null, likes: 0, comments: 0, shares: 0, impressions: 0 },
  ]);

  const [socialLeads] = useState<LeadFromSocial[]>([
    { id: 1, name: "Sarah Mitchell", platform: "linkedin", profile_url: "https://linkedin.com/in/sarahmitchell", engagement_score: 92, last_interaction: "2025-11-29T08:15:00Z", status: "hot" },
    { id: 2, name: "David Chen", platform: "linkedin", profile_url: "https://linkedin.com/in/davidchen", engagement_score: 78, last_interaction: "2025-11-28T14:30:00Z", status: "warm" },
    { id: 3, name: "Emily Rodriguez", platform: "twitter", profile_url: "https://twitter.com/emilyrod", engagement_score: 65, last_interaction: "2025-11-27T11:00:00Z", status: "warm" },
  ]);

  const [newPostContent, setNewPostContent] = useState("");
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(["linkedin"]);

  const totalFollowers = profiles.reduce((sum, p) => sum + p.followers, 0);
  const avgEngagement = profiles.reduce((sum, p) => sum + p.engagement_rate, 0) / profiles.length;
  const totalImpressions = posts.reduce((sum, p) => sum + p.impressions, 0);

  const getPlatformIcon = (platform: string) => {
    switch (platform) {
      case "linkedin": return <Linkedin className="w-4 h-4 text-blue-600" />;
      case "twitter": return <Twitter className="w-4 h-4 text-sky-500" />;
      default: return <Globe className="w-4 h-4" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "hot": return "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400";
      case "warm": return "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400";
      case "cold": return "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400";
      default: return "bg-gray-100 text-gray-700";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
            Social Selling Hub
          </h1>
          <p className="text-muted-foreground mt-1">
            LinkedIn & Twitter integration for lead generation
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Calendar className="w-4 h-4 mr-2" />
            Content Calendar
          </Button>
          <Button className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700">
            <Share2 className="w-4 h-4 mr-2" />
            Connect Account
          </Button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950/50 dark:to-blue-900/30 border-blue-200 dark:border-blue-800">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-blue-600 dark:text-blue-400">Total Followers</p>
                <p className="text-3xl font-bold text-blue-700 dark:text-blue-300">{totalFollowers.toLocaleString()}</p>
              </div>
              <Users className="w-10 h-10 text-blue-500 opacity-80" />
            </div>
            <p className="text-xs text-blue-600/70 dark:text-blue-400/70 mt-2">+12% this month</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-950/50 dark:to-green-900/30 border-green-200 dark:border-green-800">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-green-600 dark:text-green-400">Engagement Rate</p>
                <p className="text-3xl font-bold text-green-700 dark:text-green-300">{avgEngagement.toFixed(1)}%</p>
              </div>
              <TrendingUp className="w-10 h-10 text-green-500 opacity-80" />
            </div>
            <p className="text-xs text-green-600/70 dark:text-green-400/70 mt-2">Above industry avg (2.5%)</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-950/50 dark:to-purple-900/30 border-purple-200 dark:border-purple-800">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-purple-600 dark:text-purple-400">Total Impressions</p>
                <p className="text-3xl font-bold text-purple-700 dark:text-purple-300">{totalImpressions.toLocaleString()}</p>
              </div>
              <Eye className="w-10 h-10 text-purple-500 opacity-80" />
            </div>
            <p className="text-xs text-purple-600/70 dark:text-purple-400/70 mt-2">Last 30 days</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-950/50 dark:to-orange-900/30 border-orange-200 dark:border-orange-800">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-orange-600 dark:text-orange-400">Social Leads</p>
                <p className="text-3xl font-bold text-orange-700 dark:text-orange-300">{socialLeads.length}</p>
              </div>
              <Target className="w-10 h-10 text-orange-500 opacity-80" />
            </div>
            <p className="text-xs text-orange-600/70 dark:text-orange-400/70 mt-2">{socialLeads.filter(l => l.status === "hot").length} hot leads</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="compose" className="space-y-4">
        <TabsList className="bg-muted/50">
          <TabsTrigger value="compose">Compose</TabsTrigger>
          <TabsTrigger value="posts">Posts</TabsTrigger>
          <TabsTrigger value="leads">Social Leads</TabsTrigger>
          <TabsTrigger value="accounts">Accounts</TabsTrigger>
        </TabsList>

        {/* Compose Tab */}
        <TabsContent value="compose" className="space-y-4">
          <div className="grid gap-6 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Send className="w-5 h-5" />
                    Create Post
                  </CardTitle>
                  <CardDescription>Write once, publish everywhere</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex gap-2">
                    <Button 
                      variant={selectedPlatforms.includes("linkedin") ? "default" : "outline"}
                      size="sm"
                      onClick={() => {
                        if (selectedPlatforms.includes("linkedin")) {
                          setSelectedPlatforms(selectedPlatforms.filter(p => p !== "linkedin"));
                        } else {
                          setSelectedPlatforms([...selectedPlatforms, "linkedin"]);
                        }
                      }}
                    >
                      <Linkedin className="w-4 h-4 mr-2" />
                      LinkedIn
                    </Button>
                    <Button 
                      variant={selectedPlatforms.includes("twitter") ? "default" : "outline"}
                      size="sm"
                      onClick={() => {
                        if (selectedPlatforms.includes("twitter")) {
                          setSelectedPlatforms(selectedPlatforms.filter(p => p !== "twitter"));
                        } else {
                          setSelectedPlatforms([...selectedPlatforms, "twitter"]);
                        }
                      }}
                    >
                      <Twitter className="w-4 h-4 mr-2" />
                      Twitter
                    </Button>
                  </div>
                  
                  <Textarea 
                    placeholder="What would you like to share with your network?"
                    value={newPostContent}
                    onChange={(e) => setNewPostContent(e.target.value)}
                    className="min-h-[150px]"
                  />
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <span>{newPostContent.length} characters</span>
                      {selectedPlatforms.includes("twitter") && newPostContent.length > 280 && (
                        <Badge variant="destructive">Twitter limit exceeded</Badge>
                      )}
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline">
                        <Clock className="w-4 h-4 mr-2" />
                        Schedule
                      </Button>
                      <Button className="bg-gradient-to-r from-blue-600 to-cyan-600">
                        <Send className="w-4 h-4 mr-2" />
                        Post Now
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-yellow-500" />
                  AI Suggestions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="p-3 rounded-lg bg-muted/50 hover:bg-muted cursor-pointer transition-colors">
                  <p className="text-sm">💡 Share a customer success story</p>
                </div>
                <div className="p-3 rounded-lg bg-muted/50 hover:bg-muted cursor-pointer transition-colors">
                  <p className="text-sm">📊 Post industry insights with data</p>
                </div>
                <div className="p-3 rounded-lg bg-muted/50 hover:bg-muted cursor-pointer transition-colors">
                  <p className="text-sm">🎯 Ask an engaging question</p>
                </div>
                <div className="p-3 rounded-lg bg-muted/50 hover:bg-muted cursor-pointer transition-colors">
                  <p className="text-sm">🏆 Celebrate team achievements</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Posts Tab */}
        <TabsContent value="posts" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Posts</CardTitle>
              <CardDescription>Track performance of your social content</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {posts.map((post) => (
                  <div key={post.id} className="p-4 rounded-lg border bg-card hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          {getPlatformIcon(post.platform)}
                          <Badge variant={post.status === "published" ? "default" : "secondary"}>
                            {post.status}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {post.published_at 
                              ? new Date(post.published_at).toLocaleDateString()
                              : `Scheduled: ${new Date(post.scheduled_at!).toLocaleDateString()}`
                            }
                          </span>
                        </div>
                        <p className="text-sm">{post.content}</p>
                      </div>
                    </div>
                    
                    {post.status === "published" && (
                      <div className="flex items-center gap-6 mt-4 pt-4 border-t">
                        <div className="flex items-center gap-1 text-sm text-muted-foreground">
                          <Heart className="w-4 h-4" />
                          <span>{post.likes}</span>
                        </div>
                        <div className="flex items-center gap-1 text-sm text-muted-foreground">
                          <MessageSquare className="w-4 h-4" />
                          <span>{post.comments}</span>
                        </div>
                        <div className="flex items-center gap-1 text-sm text-muted-foreground">
                          <Repeat2 className="w-4 h-4" />
                          <span>{post.shares}</span>
                        </div>
                        <div className="flex items-center gap-1 text-sm text-muted-foreground">
                          <Eye className="w-4 h-4" />
                          <span>{post.impressions.toLocaleString()}</span>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Social Leads Tab */}
        <TabsContent value="leads" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Leads from Social</CardTitle>
                  <CardDescription>Prospects engaged with your content</CardDescription>
                </div>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input placeholder="Search leads..." className="pl-9 w-[200px]" />
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {socialLeads.map((lead) => (
                  <div key={lead.id} className="flex items-center justify-between p-4 rounded-lg border bg-card hover:shadow-md transition-shadow">
                    <div className="flex items-center gap-4">
                      <Avatar>
                        <AvatarFallback>{lead.name.split(" ").map(n => n[0]).join("")}</AvatarFallback>
                      </Avatar>
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="font-medium">{lead.name}</p>
                          {getPlatformIcon(lead.platform)}
                        </div>
                        <p className="text-sm text-muted-foreground">
                          Last interaction: {new Date(lead.last_interaction).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="text-sm font-medium">Engagement Score</p>
                        <div className="flex items-center gap-2">
                          <Progress value={lead.engagement_score} className="w-20 h-2" />
                          <span className="text-sm text-muted-foreground">{lead.engagement_score}%</span>
                        </div>
                      </div>
                      <Badge className={getStatusColor(lead.status)}>
                        {lead.status.toUpperCase()}
                      </Badge>
                      <Button size="sm" variant="outline">
                        <UserPlus className="w-4 h-4 mr-2" />
                        Add to CRM
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Accounts Tab */}
        <TabsContent value="accounts" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {profiles.map((profile) => (
              <Card key={profile.id}>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className={`p-3 rounded-full ${profile.platform === "linkedin" ? "bg-blue-100 dark:bg-blue-900/30" : "bg-sky-100 dark:bg-sky-900/30"}`}>
                        {profile.platform === "linkedin" 
                          ? <Linkedin className="w-6 h-6 text-blue-600" />
                          : <Twitter className="w-6 h-6 text-sky-500" />
                        }
                      </div>
                      <div>
                        <p className="font-semibold capitalize">{profile.platform}</p>
                        <p className="text-sm text-muted-foreground">{profile.username}</p>
                      </div>
                    </div>
                    <Badge variant={profile.connected ? "default" : "secondary"} className="flex items-center gap-1">
                      {profile.connected ? <CheckCircle className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
                      {profile.connected ? "Connected" : "Disconnected"}
                    </Badge>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-3 rounded-lg bg-muted/50">
                      <p className="text-sm text-muted-foreground">Followers</p>
                      <p className="text-xl font-bold">{profile.followers.toLocaleString()}</p>
                    </div>
                    <div className="p-3 rounded-lg bg-muted/50">
                      <p className="text-sm text-muted-foreground">Engagement</p>
                      <p className="text-xl font-bold">{profile.engagement_rate}%</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between mt-4 pt-4 border-t">
                    <p className="text-xs text-muted-foreground">
                      Last synced: {new Date(profile.last_sync).toLocaleString()}
                    </p>
                    <Button size="sm" variant="outline">
                      <BarChart3 className="w-4 h-4 mr-2" />
                      Analytics
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
            
            <Card className="border-dashed">
              <CardContent className="p-6 flex flex-col items-center justify-center min-h-[200px]">
                <Globe className="w-12 h-12 text-muted-foreground mb-4" />
                <p className="font-medium">Connect Another Account</p>
                <p className="text-sm text-muted-foreground text-center mt-1">
                  Add more social platforms to expand your reach
                </p>
                <Button className="mt-4" variant="outline">
                  <Share2 className="w-4 h-4 mr-2" />
                  Connect
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
