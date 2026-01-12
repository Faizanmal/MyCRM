'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { 
  Inbox, 
  Send, 
  MessageSquare, 
  Twitter, 
  Facebook, 
  Instagram, 
  Linkedin, 
  Plus, 
  Search, 
  Filter,
  MoreHorizontal,
  Archive,
  Star,
  Clock,
  User,
  Reply,
  RefreshCw,
  Settings,
  Link,
  CheckCircle,
  AlertCircle,
  Calendar,
  Image,
  Paperclip,
  Smile,
  Hash,
  AtSign,
  TrendingUp,
  Eye,
  Heart,
  Repeat2,
  Share
} from 'lucide-react';
import { socialInboxAPI } from '@/lib/api';

interface SocialAccount {
  id: string;
  platform: 'twitter' | 'facebook' | 'instagram' | 'linkedin';
  username: string;
  display_name: string;
  avatar: string;
  connected: boolean;
  followers: number;
  last_synced: string;
}

interface Conversation {
  id: string;
  platform: 'twitter' | 'facebook' | 'instagram' | 'linkedin';
  contact: {
    name: string;
    username: string;
    avatar: string;
  };
  last_message: string;
  unread_count: number;
  starred: boolean;
  assigned_to: string | null;
  status: 'open' | 'pending' | 'resolved';
  created_at: string;
  updated_at: string;
  messages: {
    id: string;
    content: string;
    sender: 'contact' | 'agent';
    timestamp: string;
    read: boolean;
  }[];
}

interface SocialPost {
  id: string;
  content: string;
  platforms: string[];
  status: 'draft' | 'scheduled' | 'published' | 'failed';
  scheduled_at: string | null;
  published_at: string | null;
  engagement: {
    likes: number;
    comments: number;
    shares: number;
    views: number;
  };
  media: string[];
}

interface MonitoringRule {
  id: string;
  name: string;
  keywords: string[];
  platforms: string[];
  is_active: boolean;
  matches_count: number;
}

const platformIcons: Record<string, React.ReactNode> = {
  twitter: <Twitter className="h-4 w-4" />,
  facebook: <Facebook className="h-4 w-4" />,
  instagram: <Instagram className="h-4 w-4" />,
  linkedin: <Linkedin className="h-4 w-4" />,
};

const platformColors: Record<string, string> = {
  twitter: 'bg-blue-400',
  facebook: 'bg-blue-600',
  instagram: 'bg-pink-500',
  linkedin: 'bg-blue-700',
};

export default function SocialInboxPage() {
  const [accounts, setAccounts] = useState<SocialAccount[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [posts, setPosts] = useState<SocialPost[]>([]);
  const [rules, setRules] = useState<MonitoringRule[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [replyMessage, setReplyMessage] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState<'all' | 'unread' | 'starred'>('all');
  const [isCreatePostOpen, setIsCreatePostOpen] = useState(false);
  const [newPost, setNewPost] = useState({ content: '', platforms: [] as string[], scheduled_at: '' });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [dashData, accountsData, convoData, postsData, rulesData] = await Promise.all([
        socialInboxAPI.getDashboard(),
        socialInboxAPI.getAccounts(),
        socialInboxAPI.getConversations(),
        socialInboxAPI.getPosts(),
        socialInboxAPI.getMonitoringRules(),
      ]);
      setAccounts(accountsData.results || accountsData || []);
      setConversations(convoData.results || convoData || []);
      setPosts(postsData.results || postsData || []);
      setRules(rulesData.results || rulesData || []);
    } catch (error) {
      console.error('Failed to load data:', error);
      // Demo data
      setAccounts([
        { id: '1', platform: 'twitter', username: '@mycompany', display_name: 'My Company', avatar: '', connected: true, followers: 15200, last_synced: '2026-01-12T10:00:00Z' },
        { id: '2', platform: 'facebook', username: 'mycompany', display_name: 'My Company', avatar: '', connected: true, followers: 28500, last_synced: '2026-01-12T10:00:00Z' },
        { id: '3', platform: 'instagram', username: '@mycompany', display_name: 'My Company', avatar: '', connected: true, followers: 42300, last_synced: '2026-01-12T10:00:00Z' },
        { id: '4', platform: 'linkedin', username: 'my-company', display_name: 'My Company', avatar: '', connected: false, followers: 8900, last_synced: '2026-01-10T10:00:00Z' },
      ]);
      setConversations([
        {
          id: '1',
          platform: 'twitter',
          contact: { name: 'John Smith', username: '@johnsmith', avatar: '' },
          last_message: 'Thanks for the quick response! I\'ll check that out.',
          unread_count: 2,
          starred: true,
          assigned_to: null,
          status: 'open',
          created_at: '2026-01-12T09:00:00Z',
          updated_at: '2026-01-12T14:30:00Z',
          messages: [
            { id: '1', content: 'Hey, I\'m having issues with my account login. Can you help?', sender: 'contact', timestamp: '2026-01-12T09:00:00Z', read: true },
            { id: '2', content: 'Hi John! I\'d be happy to help. Can you tell me what error message you\'re seeing?', sender: 'agent', timestamp: '2026-01-12T09:15:00Z', read: true },
            { id: '3', content: 'It says "Invalid credentials" but I\'m sure my password is correct', sender: 'contact', timestamp: '2026-01-12T14:00:00Z', read: false },
            { id: '4', content: 'Thanks for the quick response! I\'ll check that out.', sender: 'contact', timestamp: '2026-01-12T14:30:00Z', read: false },
          ],
        },
        {
          id: '2',
          platform: 'facebook',
          contact: { name: 'Sarah Johnson', username: 'sarah.johnson', avatar: '' },
          last_message: 'When will the new feature be available?',
          unread_count: 1,
          starred: false,
          assigned_to: 'Agent 1',
          status: 'pending',
          created_at: '2026-01-11T15:00:00Z',
          updated_at: '2026-01-12T10:00:00Z',
          messages: [
            { id: '1', content: 'Hi! I saw your announcement about the new AI features. When will they be available?', sender: 'contact', timestamp: '2026-01-11T15:00:00Z', read: true },
            { id: '2', content: 'Hello Sarah! The new AI features are scheduled for release in Q1 2026. Stay tuned!', sender: 'agent', timestamp: '2026-01-11T16:00:00Z', read: true },
            { id: '3', content: 'When will the new feature be available?', sender: 'contact', timestamp: '2026-01-12T10:00:00Z', read: false },
          ],
        },
        {
          id: '3',
          platform: 'instagram',
          contact: { name: 'Mike Chen', username: '@mikechen', avatar: '' },
          last_message: 'Love your product! 🎉',
          unread_count: 0,
          starred: true,
          assigned_to: null,
          status: 'resolved',
          created_at: '2026-01-10T12:00:00Z',
          updated_at: '2026-01-10T14:00:00Z',
          messages: [
            { id: '1', content: 'Love your product! 🎉', sender: 'contact', timestamp: '2026-01-10T12:00:00Z', read: true },
            { id: '2', content: 'Thank you so much Mike! We appreciate your support! ❤️', sender: 'agent', timestamp: '2026-01-10T14:00:00Z', read: true },
          ],
        },
      ]);
      setPosts([
        {
          id: '1',
          content: '🚀 Exciting news! Our new AI-powered features are now live. Check them out and let us know what you think! #AI #CRM #Innovation',
          platforms: ['twitter', 'facebook', 'linkedin'],
          status: 'published',
          scheduled_at: null,
          published_at: '2026-01-10T09:00:00Z',
          engagement: { likes: 245, comments: 32, shares: 18, views: 5200 },
          media: [],
        },
        {
          id: '2',
          content: 'Join us for a live webinar on "Maximizing Your CRM Potential" this Thursday at 2 PM EST. Register now! 📺',
          platforms: ['twitter', 'linkedin'],
          status: 'scheduled',
          scheduled_at: '2026-01-15T14:00:00Z',
          published_at: null,
          engagement: { likes: 0, comments: 0, shares: 0, views: 0 },
          media: [],
        },
        {
          id: '3',
          content: 'Customer spotlight: See how @acmecorp increased their sales by 40% using our platform! 📈',
          platforms: ['twitter', 'facebook', 'instagram'],
          status: 'draft',
          scheduled_at: null,
          published_at: null,
          engagement: { likes: 0, comments: 0, shares: 0, views: 0 },
          media: [],
        },
      ]);
      setRules([
        { id: '1', name: 'Brand Mentions', keywords: ['mycompany', 'mycrm', '#mycrm'], platforms: ['twitter', 'instagram'], is_active: true, matches_count: 156 },
        { id: '2', name: 'Competitor Tracking', keywords: ['competitor1', 'competitor2'], platforms: ['twitter', 'linkedin'], is_active: true, matches_count: 43 },
        { id: '3', name: 'Industry Keywords', keywords: ['CRM', 'sales automation', 'customer success'], platforms: ['twitter', 'linkedin'], is_active: false, matches_count: 892 },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const sendReply = async (conversationId: string) => {
    if (!replyMessage.trim()) return;
    try {
      await socialInboxAPI.replyToConversation(conversationId, replyMessage);
      // Update locally
      const newMessage = {
        id: Date.now().toString(),
        content: replyMessage,
        sender: 'agent' as const,
        timestamp: new Date().toISOString(),
        read: true,
      };
      setConversations(conversations.map(c => 
        c.id === conversationId 
          ? { ...c, messages: [...c.messages, newMessage], last_message: replyMessage }
          : c
      ));
      if (selectedConversation?.id === conversationId) {
        setSelectedConversation({
          ...selectedConversation,
          messages: [...selectedConversation.messages, newMessage],
          last_message: replyMessage,
        });
      }
      setReplyMessage('');
    } catch (error) {
      console.error('Failed to send reply:', error);
    }
  };

  const toggleStar = (conversationId: string) => {
    setConversations(conversations.map(c => 
      c.id === conversationId ? { ...c, starred: !c.starred } : c
    ));
  };

  const archiveConversation = async (conversationId: string) => {
    try {
      await socialInboxAPI.archiveConversation(conversationId);
      setConversations(conversations.filter(c => c.id !== conversationId));
      if (selectedConversation?.id === conversationId) {
        setSelectedConversation(null);
      }
    } catch (error) {
      console.error('Failed to archive:', error);
    }
  };

  const createPost = async () => {
    try {
      const post = await socialInboxAPI.createPost({
        content: newPost.content,
        platforms: newPost.platforms,
        scheduled_at: newPost.scheduled_at || undefined,
      });
      setPosts([post, ...posts]);
      setIsCreatePostOpen(false);
      setNewPost({ content: '', platforms: [], scheduled_at: '' });
    } catch (error) {
      console.error('Failed to create post:', error);
    }
  };

  const filteredConversations = conversations.filter(c => {
    if (activeFilter === 'unread' && c.unread_count === 0) return false;
    if (activeFilter === 'starred' && !c.starred) return false;
    if (searchQuery && !c.contact.name.toLowerCase().includes(searchQuery.toLowerCase()) && 
        !c.last_message.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  const getInitials = (name: string) => name.split(' ').map(n => n[0]).join('').toUpperCase();

  const totalUnread = conversations.reduce((sum, c) => sum + c.unread_count, 0);

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Inbox className="h-8 w-8" />
            Social Inbox
          </h1>
          <p className="text-muted-foreground">
            Manage all your social media conversations in one place
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={loadData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Sync
          </Button>
          <Dialog open={isCreatePostOpen} onOpenChange={setIsCreatePostOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                New Post
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Create New Post</DialogTitle>
                <DialogDescription>Compose and schedule a post across multiple platforms.</DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label>Content</Label>
                  <Textarea
                    placeholder="What's on your mind?"
                    value={newPost.content}
                    onChange={(e) => setNewPost({ ...newPost, content: e.target.value })}
                    rows={4}
                  />
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <div className="flex items-center gap-4">
                      <Button variant="ghost" size="sm" className="h-8">
                        <Image className="h-4 w-4 mr-1" />
                        Image
                      </Button>
                      <Button variant="ghost" size="sm" className="h-8">
                        <Smile className="h-4 w-4 mr-1" />
                        Emoji
                      </Button>
                      <Button variant="ghost" size="sm" className="h-8">
                        <Hash className="h-4 w-4 mr-1" />
                        Hashtag
                      </Button>
                    </div>
                    <span>{newPost.content.length}/280</span>
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Platforms</Label>
                  <div className="flex gap-2">
                    {accounts.filter(a => a.connected).map((account) => (
                      <Button
                        key={account.id}
                        variant={newPost.platforms.includes(account.platform) ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => {
                          const platforms = newPost.platforms.includes(account.platform)
                            ? newPost.platforms.filter(p => p !== account.platform)
                            : [...newPost.platforms, account.platform];
                          setNewPost({ ...newPost, platforms });
                        }}
                      >
                        <span className={`${platformColors[account.platform]} rounded-full p-1 mr-2`}>
                          {platformIcons[account.platform]}
                        </span>
                        {account.platform}
                      </Button>
                    ))}
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Schedule (optional)</Label>
                  <Input
                    type="datetime-local"
                    value={newPost.scheduled_at}
                    onChange={(e) => setNewPost({ ...newPost, scheduled_at: e.target.value })}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsCreatePostOpen(false)}>Cancel</Button>
                <Button variant="outline">Save Draft</Button>
                <Button onClick={createPost} disabled={!newPost.content.trim() || newPost.platforms.length === 0}>
                  {newPost.scheduled_at ? 'Schedule' : 'Publish Now'}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Connected Accounts */}
      <div className="flex gap-4 overflow-x-auto pb-2">
        {accounts.map((account) => (
          <Card key={account.id} className={`min-w-[200px] ${!account.connected ? 'opacity-50' : ''}`}>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className={`${platformColors[account.platform]} rounded-full p-2 text-white`}>
                  {platformIcons[account.platform]}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">{account.display_name}</p>
                  <p className="text-xs text-muted-foreground">{account.username}</p>
                </div>
                {account.connected ? (
                  <CheckCircle className="h-4 w-4 text-green-500" />
                ) : (
                  <AlertCircle className="h-4 w-4 text-yellow-500" />
                )}
              </div>
              <div className="flex items-center justify-between mt-3 text-xs text-muted-foreground">
                <span>{account.followers.toLocaleString()} followers</span>
                {account.connected && <span>Synced just now</span>}
              </div>
            </CardContent>
          </Card>
        ))}
        <Card className="min-w-[200px] border-dashed cursor-pointer hover:bg-muted/50">
          <CardContent className="p-4 flex items-center justify-center h-full">
            <div className="text-center">
              <Plus className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
              <p className="text-sm text-muted-foreground">Connect Account</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="inbox">
        <TabsList>
          <TabsTrigger value="inbox" className="flex items-center gap-1">
            <MessageSquare className="h-4 w-4" />
            Inbox
            {totalUnread > 0 && (
              <Badge variant="destructive" className="ml-1 h-5 w-5 p-0 flex items-center justify-center text-xs">
                {totalUnread}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="posts" className="flex items-center gap-1">
            <Send className="h-4 w-4" />
            Posts
          </TabsTrigger>
          <TabsTrigger value="monitoring" className="flex items-center gap-1">
            <Eye className="h-4 w-4" />
            Monitoring
          </TabsTrigger>
        </TabsList>

        <TabsContent value="inbox" className="mt-6">
          <div className="flex gap-6 h-[600px]">
            {/* Conversation List */}
            <Card className="w-96 flex flex-col">
              <CardHeader className="pb-2">
                <div className="flex items-center gap-2">
                  <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search conversations..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                  <Button variant="outline" size="icon">
                    <Filter className="h-4 w-4" />
                  </Button>
                </div>
                <div className="flex gap-1 mt-2">
                  <Button
                    variant={activeFilter === 'all' ? 'secondary' : 'ghost'}
                    size="sm"
                    onClick={() => setActiveFilter('all')}
                  >
                    All
                  </Button>
                  <Button
                    variant={activeFilter === 'unread' ? 'secondary' : 'ghost'}
                    size="sm"
                    onClick={() => setActiveFilter('unread')}
                  >
                    Unread
                  </Button>
                  <Button
                    variant={activeFilter === 'starred' ? 'secondary' : 'ghost'}
                    size="sm"
                    onClick={() => setActiveFilter('starred')}
                  >
                    Starred
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="flex-1 overflow-hidden p-0">
                <ScrollArea className="h-full">
                  <div className="space-y-1 p-2">
                    {filteredConversations.map((conversation) => (
                      <div
                        key={conversation.id}
                        className={`p-3 rounded-lg cursor-pointer transition-colors ${
                          selectedConversation?.id === conversation.id
                            ? 'bg-primary text-primary-foreground'
                            : 'hover:bg-muted'
                        }`}
                        onClick={() => setSelectedConversation(conversation)}
                      >
                        <div className="flex items-start gap-3">
                          <div className="relative">
                            <Avatar className="h-10 w-10">
                              <AvatarImage src={conversation.contact.avatar} />
                              <AvatarFallback>{getInitials(conversation.contact.name)}</AvatarFallback>
                            </Avatar>
                            <div className={`absolute -bottom-1 -right-1 ${platformColors[conversation.platform]} rounded-full p-1`}>
                              {platformIcons[conversation.platform]}
                            </div>
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between">
                              <p className="font-medium truncate">{conversation.contact.name}</p>
                              <div className="flex items-center gap-1">
                                {conversation.starred && (
                                  <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                                )}
                                {conversation.unread_count > 0 && (
                                  <Badge variant="destructive" className="h-5 w-5 p-0 flex items-center justify-center text-xs">
                                    {conversation.unread_count}
                                  </Badge>
                                )}
                              </div>
                            </div>
                            <p className="text-sm truncate opacity-70">{conversation.last_message}</p>
                            <p className="text-xs opacity-50 mt-1">
                              {new Date(conversation.updated_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Conversation Detail */}
            <Card className="flex-1 flex flex-col">
              {selectedConversation ? (
                <>
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Avatar className="h-10 w-10">
                          <AvatarFallback>{getInitials(selectedConversation.contact.name)}</AvatarFallback>
                        </Avatar>
                        <div>
                          <div className="flex items-center gap-2">
                            <CardTitle className="text-lg">{selectedConversation.contact.name}</CardTitle>
                            <div className={`${platformColors[selectedConversation.platform]} rounded-full p-1`}>
                              {platformIcons[selectedConversation.platform]}
                            </div>
                          </div>
                          <CardDescription>{selectedConversation.contact.username}</CardDescription>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button variant="ghost" size="icon" onClick={() => toggleStar(selectedConversation.id)}>
                          <Star className={`h-4 w-4 ${selectedConversation.starred ? 'fill-yellow-400 text-yellow-400' : ''}`} />
                        </Button>
                        <Button variant="ghost" size="icon" onClick={() => archiveConversation(selectedConversation.id)}>
                          <Archive className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="icon">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <Separator />
                  <CardContent className="flex-1 overflow-hidden p-0">
                    <ScrollArea className="h-full p-4">
                      <div className="space-y-4">
                        {selectedConversation.messages.map((msg) => (
                          <div key={msg.id} className={`flex ${msg.sender === 'agent' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-[70%] rounded-lg p-3 ${
                              msg.sender === 'agent'
                                ? 'bg-primary text-primary-foreground'
                                : 'bg-muted'
                            }`}>
                              <p className="text-sm">{msg.content}</p>
                              <p className="text-xs opacity-50 mt-1">
                                {new Date(msg.timestamp).toLocaleString()}
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </ScrollArea>
                  </CardContent>
                  <Separator />
                  <CardFooter className="p-4">
                    <div className="flex gap-2 w-full">
                      <Textarea
                        placeholder="Type your reply..."
                        value={replyMessage}
                        onChange={(e) => setReplyMessage(e.target.value)}
                        className="flex-1"
                        rows={2}
                      />
                      <Button onClick={() => sendReply(selectedConversation.id)} disabled={!replyMessage.trim()}>
                        <Send className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardFooter>
                </>
              ) : (
                <CardContent className="flex-1 flex items-center justify-center">
                  <div className="text-center">
                    <MessageSquare className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                    <p className="text-lg font-medium mb-2">Select a conversation</p>
                    <p className="text-muted-foreground">Choose a conversation to view messages</p>
                  </div>
                </CardContent>
              )}
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="posts" className="mt-6">
          <div className="space-y-4">
            {posts.map((post) => (
              <Card key={post.id}>
                <CardContent className="p-4">
                  <div className="flex items-start gap-4">
                    <div className="flex-1">
                      <p className="mb-3">{post.content}</p>
                      <div className="flex items-center gap-2 mb-3">
                        {post.platforms.map((platform) => (
                          <div key={platform} className={`${platformColors[platform]} rounded-full p-1 text-white`}>
                            {platformIcons[platform]}
                          </div>
                        ))}
                      </div>
                      {post.status === 'published' && (
                        <div className="flex items-center gap-6 text-sm text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <Heart className="h-4 w-4" />
                            {post.engagement.likes}
                          </span>
                          <span className="flex items-center gap-1">
                            <MessageSquare className="h-4 w-4" />
                            {post.engagement.comments}
                          </span>
                          <span className="flex items-center gap-1">
                            <Repeat2 className="h-4 w-4" />
                            {post.engagement.shares}
                          </span>
                          <span className="flex items-center gap-1">
                            <Eye className="h-4 w-4" />
                            {post.engagement.views}
                          </span>
                        </div>
                      )}
                    </div>
                    <div className="text-right">
                      <Badge variant={
                        post.status === 'published' ? 'default' :
                        post.status === 'scheduled' ? 'secondary' : 'outline'
                      }>
                        {post.status}
                      </Badge>
                      <p className="text-xs text-muted-foreground mt-2">
                        {post.status === 'published' && post.published_at && 
                          `Published: ${new Date(post.published_at).toLocaleDateString()}`}
                        {post.status === 'scheduled' && post.scheduled_at && 
                          `Scheduled: ${new Date(post.scheduled_at).toLocaleDateString()}`}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="monitoring" className="mt-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Monitoring Rules</CardTitle>
                <Button size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Rule
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {rules.map((rule) => (
                  <div key={rule.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center gap-4">
                      <Switch checked={rule.is_active} />
                      <div>
                        <p className="font-medium">{rule.name}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <div className="flex gap-1">
                            {rule.keywords.slice(0, 3).map((kw, idx) => (
                              <Badge key={idx} variant="outline" className="text-xs">{kw}</Badge>
                            ))}
                            {rule.keywords.length > 3 && (
                              <Badge variant="outline" className="text-xs">+{rule.keywords.length - 3}</Badge>
                            )}
                          </div>
                          <span className="text-muted-foreground">•</span>
                          <div className="flex gap-1">
                            {rule.platforms.map((platform) => (
                              <span key={platform} className={`${platformColors[platform]} rounded-full p-1`}>
                                {platformIcons[platform]}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="text-2xl font-bold">{rule.matches_count}</p>
                        <p className="text-xs text-muted-foreground">matches</p>
                      </div>
                      <Button variant="outline" size="sm">View</Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
