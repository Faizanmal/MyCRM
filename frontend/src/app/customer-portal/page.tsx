'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog';
import { 
  Users, 
  Ticket, 
  ShoppingCart, 
  BookOpen, 
  Bell, 
  Search, 
  Plus, 
  MessageSquare,
  Clock,
  CheckCircle,
  AlertCircle,
  HelpCircle,
  FileText,
  ExternalLink,
  ChevronRight,
  Send,
  Package,
  CreditCard,
  TrendingUp,
  Eye,
  Settings
} from 'lucide-react';
import { customerPortalAPI } from '@/lib/api';

interface Ticket {
  id: string;
  subject: string;
  description: string;
  status: 'open' | 'in-progress' | 'resolved' | 'closed';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  created_at: string;
  updated_at: string;
  messages: {
    id: string;
    author: string;
    content: string;
    timestamp: string;
    is_staff: boolean;
  }[];
}

interface Order {
  id: string;
  order_number: string;
  status: 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled';
  total: number;
  items: {
    name: string;
    quantity: number;
    price: number;
  }[];
  created_at: string;
  tracking_number?: string;
}

interface KBArticle {
  id: string;
  title: string;
  excerpt: string;
  category: string;
  views: number;
  helpful_count: number;
}

interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning';
  read: boolean;
  created_at: string;
}

interface DashboardStats {
  open_tickets: number;
  pending_orders: number;
  unread_notifications: number;
  total_orders: number;
}

export default function CustomerPortalPage() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [articles, setArticles] = useState<KBArticle[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const [isCreateTicketOpen, setIsCreateTicketOpen] = useState(false);
  const [newTicket, setNewTicket] = useState({ subject: '', description: '', priority: 'medium' });
  const [ticketReply, setTicketReply] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [dashboardData, ticketsData, ordersData, kbData, notifData] = await Promise.all([
        customerPortalAPI.getDashboard(),
        customerPortalAPI.getTickets(),
        customerPortalAPI.getOrders(),
        customerPortalAPI.getKnowledgeBase(),
        customerPortalAPI.getNotifications(),
      ]);
      setStats(dashboardData);
      setTickets(ticketsData.results || ticketsData || []);
      setOrders(ordersData.results || ordersData || []);
      setArticles(kbData.results || kbData || []);
      setNotifications(notifData.results || notifData || []);
    } catch (error) {
      console.error('Failed to load data:', error);
      // Demo data
      setStats({
        open_tickets: 2,
        pending_orders: 1,
        unread_notifications: 3,
        total_orders: 15,
      });
      setTickets([
        {
          id: '1',
          subject: 'Unable to access premium features',
          description: 'I upgraded my plan but still cannot access the advanced reporting features.',
          status: 'in-progress',
          priority: 'high',
          created_at: '2026-01-10T10:00:00Z',
          updated_at: '2026-01-12T09:00:00Z',
          messages: [
            { id: '1', author: 'You', content: 'I upgraded my plan but still cannot access the advanced reporting features.', timestamp: '2026-01-10T10:00:00Z', is_staff: false },
            { id: '2', author: 'Support Agent', content: 'Thank you for reaching out. I can see your upgrade was processed. Let me refresh your account permissions.', timestamp: '2026-01-10T14:00:00Z', is_staff: true },
            { id: '3', author: 'Support Agent', content: 'I have refreshed your permissions. Could you please log out and log back in to see if the issue is resolved?', timestamp: '2026-01-12T09:00:00Z', is_staff: true },
          ],
        },
        {
          id: '2',
          subject: 'Question about API rate limits',
          description: 'What are the API rate limits for the enterprise plan?',
          status: 'open',
          priority: 'medium',
          created_at: '2026-01-11T15:00:00Z',
          updated_at: '2026-01-11T15:00:00Z',
          messages: [
            { id: '1', author: 'You', content: 'What are the API rate limits for the enterprise plan?', timestamp: '2026-01-11T15:00:00Z', is_staff: false },
          ],
        },
        {
          id: '3',
          subject: 'Invoice request for December',
          description: 'Please provide the invoice for December 2025.',
          status: 'resolved',
          priority: 'low',
          created_at: '2026-01-05T08:00:00Z',
          updated_at: '2026-01-06T10:00:00Z',
          messages: [],
        },
      ]);
      setOrders([
        {
          id: '1',
          order_number: 'ORD-2026-001',
          status: 'delivered',
          total: 299.99,
          items: [{ name: 'Enterprise Plan - Annual', quantity: 1, price: 299.99 }],
          created_at: '2026-01-01T00:00:00Z',
        },
        {
          id: '2',
          order_number: 'ORD-2026-015',
          status: 'processing',
          total: 49.99,
          items: [{ name: 'Additional User Seats (5)', quantity: 1, price: 49.99 }],
          created_at: '2026-01-10T00:00:00Z',
        },
      ]);
      setArticles([
        { id: '1', title: 'Getting Started with MyCRM', excerpt: 'Learn how to set up your account and start managing your contacts...', category: 'Getting Started', views: 1250, helpful_count: 89 },
        { id: '2', title: 'How to Import Contacts', excerpt: 'Step-by-step guide to importing contacts from CSV, Excel, or other CRMs...', category: 'Data Management', views: 890, helpful_count: 67 },
        { id: '3', title: 'Setting Up Email Integration', excerpt: 'Connect your email provider to send and track emails directly from MyCRM...', category: 'Integrations', views: 756, helpful_count: 52 },
        { id: '4', title: 'Creating Custom Reports', excerpt: 'Build custom reports to track your sales performance and team productivity...', category: 'Reporting', views: 623, helpful_count: 45 },
        { id: '5', title: 'API Documentation Overview', excerpt: 'Learn how to use the MyCRM API to build custom integrations...', category: 'Developer', views: 512, helpful_count: 38 },
      ]);
      setNotifications([
        { id: '1', title: 'Ticket Updated', message: 'Your ticket "Unable to access premium features" has been updated.', type: 'info', read: false, created_at: '2026-01-12T09:00:00Z' },
        { id: '2', title: 'New Feature Available', message: 'AI-powered lead scoring is now available on your plan!', type: 'success', read: false, created_at: '2026-01-11T10:00:00Z' },
        { id: '3', title: 'Scheduled Maintenance', message: 'System maintenance scheduled for January 15, 2026 at 2:00 AM UTC.', type: 'warning', read: false, created_at: '2026-01-10T08:00:00Z' },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const createTicket = async () => {
    try {
      const ticket = await customerPortalAPI.createTicket({
        subject: newTicket.subject,
        description: newTicket.description,
        priority: newTicket.priority,
      });
      setTickets([ticket, ...tickets]);
      setIsCreateTicketOpen(false);
      setNewTicket({ subject: '', description: '', priority: 'medium' });
    } catch (error) {
      console.error('Failed to create ticket:', error);
      // Demo: add locally
      const demoTicket: Ticket = {
        id: Date.now().toString(),
        subject: newTicket.subject,
        description: newTicket.description,
        status: 'open',
        priority: newTicket.priority as 'low' | 'medium' | 'high' | 'urgent',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        messages: [{ id: '1', author: 'You', content: newTicket.description, timestamp: new Date().toISOString(), is_staff: false }],
      };
      setTickets([demoTicket, ...tickets]);
      setIsCreateTicketOpen(false);
      setNewTicket({ subject: '', description: '', priority: 'medium' });
    }
  };

  const addTicketReply = async (ticketId: string) => {
    try {
      await customerPortalAPI.addTicketComment(ticketId, ticketReply);
      // Update locally
      setTickets(tickets.map(t => 
        t.id === ticketId 
          ? { ...t, messages: [...t.messages, { id: Date.now().toString(), author: 'You', content: ticketReply, timestamp: new Date().toISOString(), is_staff: false }] }
          : t
      ));
      if (selectedTicket?.id === ticketId) {
        setSelectedTicket({
          ...selectedTicket,
          messages: [...selectedTicket.messages, { id: Date.now().toString(), author: 'You', content: ticketReply, timestamp: new Date().toISOString(), is_staff: false }],
        });
      }
      setTicketReply('');
    } catch (error) {
      console.error('Failed to add reply:', error);
    }
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      'open': 'bg-blue-100 text-blue-700',
      'in-progress': 'bg-yellow-100 text-yellow-700',
      'resolved': 'bg-green-100 text-green-700',
      'closed': 'bg-gray-100 text-gray-700',
      'pending': 'bg-yellow-100 text-yellow-700',
      'processing': 'bg-blue-100 text-blue-700',
      'shipped': 'bg-purple-100 text-purple-700',
      'delivered': 'bg-green-100 text-green-700',
      'cancelled': 'bg-red-100 text-red-700',
    };
    return <Badge className={styles[status] || 'bg-gray-100'}>{status}</Badge>;
  };

  const getPriorityBadge = (priority: string) => {
    const styles: Record<string, string> = {
      'low': 'bg-gray-100 text-gray-700',
      'medium': 'bg-blue-100 text-blue-700',
      'high': 'bg-orange-100 text-orange-700',
      'urgent': 'bg-red-100 text-red-700',
    };
    return <Badge variant="outline" className={styles[priority]}>{priority}</Badge>;
  };

  const markNotificationRead = async (id: string) => {
    try {
      await customerPortalAPI.markNotificationRead(id);
      setNotifications(notifications.map(n => n.id === id ? { ...n, read: true } : n));
    } catch (error) {
      console.error('Failed to mark notification:', error);
      setNotifications(notifications.map(n => n.id === id ? { ...n, read: true } : n));
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Users className="h-8 w-8" />
            Customer Portal
          </h1>
          <p className="text-muted-foreground">
            Manage your account, support tickets, and orders
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline">
            <Settings className="h-4 w-4 mr-2" />
            Account Settings
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Open Tickets</p>
                <p className="text-3xl font-bold">{stats?.open_tickets || 0}</p>
              </div>
              <div className="bg-blue-100 rounded-full p-3">
                <Ticket className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Pending Orders</p>
                <p className="text-3xl font-bold">{stats?.pending_orders || 0}</p>
              </div>
              <div className="bg-yellow-100 rounded-full p-3">
                <Package className="h-6 w-6 text-yellow-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Notifications</p>
                <p className="text-3xl font-bold">{stats?.unread_notifications || 0}</p>
              </div>
              <div className="bg-purple-100 rounded-full p-3">
                <Bell className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Orders</p>
                <p className="text-3xl font-bold">{stats?.total_orders || 0}</p>
              </div>
              <div className="bg-green-100 rounded-full p-3">
                <TrendingUp className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="tickets">
        <TabsList>
          <TabsTrigger value="tickets" className="flex items-center gap-1">
            <Ticket className="h-4 w-4" />
            Support Tickets
          </TabsTrigger>
          <TabsTrigger value="orders" className="flex items-center gap-1">
            <ShoppingCart className="h-4 w-4" />
            Orders
          </TabsTrigger>
          <TabsTrigger value="knowledge" className="flex items-center gap-1">
            <BookOpen className="h-4 w-4" />
            Knowledge Base
          </TabsTrigger>
          <TabsTrigger value="notifications" className="flex items-center gap-1">
            <Bell className="h-4 w-4" />
            Notifications
            {notifications.filter(n => !n.read).length > 0 && (
              <Badge variant="destructive" className="ml-1 h-5 w-5 p-0 flex items-center justify-center text-xs">
                {notifications.filter(n => !n.read).length}
              </Badge>
            )}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="tickets" className="mt-6">
          <div className="flex gap-6">
            {/* Ticket List */}
            <div className="w-1/3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-medium">Your Tickets</h3>
                <Dialog open={isCreateTicketOpen} onOpenChange={setIsCreateTicketOpen}>
                  <DialogTrigger asChild>
                    <Button size="sm">
                      <Plus className="h-4 w-4 mr-1" />
                      New Ticket
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Create Support Ticket</DialogTitle>
                      <DialogDescription>Describe your issue and our team will help you.</DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                      <div className="space-y-2">
                        <Label>Subject</Label>
                        <Input
                          placeholder="Brief description of your issue"
                          value={newTicket.subject}
                          onChange={(e) => setNewTicket({ ...newTicket, subject: e.target.value })}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>Priority</Label>
                        <Select value={newTicket.priority} onValueChange={(v) => setNewTicket({ ...newTicket, priority: v })}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="low">Low</SelectItem>
                            <SelectItem value="medium">Medium</SelectItem>
                            <SelectItem value="high">High</SelectItem>
                            <SelectItem value="urgent">Urgent</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label>Description</Label>
                        <Textarea
                          placeholder="Please describe your issue in detail..."
                          value={newTicket.description}
                          onChange={(e) => setNewTicket({ ...newTicket, description: e.target.value })}
                          rows={5}
                        />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setIsCreateTicketOpen(false)}>Cancel</Button>
                      <Button onClick={createTicket} disabled={!newTicket.subject.trim() || !newTicket.description.trim()}>
                        Create Ticket
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>
              <div className="space-y-2">
                {tickets.map((ticket) => (
                  <Card
                    key={ticket.id}
                    className={`cursor-pointer transition-colors ${selectedTicket?.id === ticket.id ? 'border-primary' : ''}`}
                    onClick={() => setSelectedTicket(ticket)}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <p className="font-medium truncate">{ticket.subject}</p>
                          <div className="flex items-center gap-2 mt-1">
                            {getStatusBadge(ticket.status)}
                            {getPriorityBadge(ticket.priority)}
                          </div>
                        </div>
                        <ChevronRight className="h-5 w-5 text-muted-foreground flex-shrink-0" />
                      </div>
                      <p className="text-xs text-muted-foreground mt-2">
                        Updated: {new Date(ticket.updated_at).toLocaleDateString()}
                      </p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>

            {/* Ticket Detail */}
            <div className="flex-1">
              {selectedTicket ? (
                <Card className="h-full flex flex-col">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div>
                        <CardTitle>{selectedTicket.subject}</CardTitle>
                        <div className="flex items-center gap-2 mt-2">
                          {getStatusBadge(selectedTicket.status)}
                          {getPriorityBadge(selectedTicket.priority)}
                          <span className="text-sm text-muted-foreground">
                            Created: {new Date(selectedTicket.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    </div>
                  </CardHeader>
                  <Separator />
                  <CardContent className="flex-1 overflow-hidden p-0">
                    <ScrollArea className="h-[400px] p-4">
                      <div className="space-y-4">
                        {selectedTicket.messages.map((msg) => (
                          <div key={msg.id} className={`flex ${msg.is_staff ? 'justify-start' : 'justify-end'}`}>
                            <div className={`max-w-[80%] rounded-lg p-3 ${msg.is_staff ? 'bg-muted' : 'bg-primary text-primary-foreground'}`}>
                              <p className="text-xs font-medium mb-1">{msg.author}</p>
                              <p className="text-sm">{msg.content}</p>
                              <p className="text-xs opacity-70 mt-1">
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
                        value={ticketReply}
                        onChange={(e) => setTicketReply(e.target.value)}
                        className="flex-1"
                        rows={2}
                      />
                      <Button onClick={() => addTicketReply(selectedTicket.id)} disabled={!ticketReply.trim()}>
                        <Send className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardFooter>
                </Card>
              ) : (
                <Card className="h-full flex items-center justify-center">
                  <CardContent className="text-center">
                    <MessageSquare className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                    <p className="text-lg font-medium mb-2">Select a ticket</p>
                    <p className="text-muted-foreground">Choose a ticket from the list to view details</p>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </TabsContent>

        <TabsContent value="orders" className="mt-6">
          <div className="space-y-4">
            {orders.map((order) => (
              <Card key={order.id}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="bg-muted rounded-full p-3">
                        <Package className="h-5 w-5" />
                      </div>
                      <div>
                        <p className="font-medium">{order.order_number}</p>
                        <p className="text-sm text-muted-foreground">
                          {order.items.map(i => i.name).join(', ')}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-6">
                      <div className="text-right">
                        <p className="font-bold">${order.total.toFixed(2)}</p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(order.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      {getStatusBadge(order.status)}
                      <Button variant="outline" size="sm">
                        <Eye className="h-4 w-4 mr-1" />
                        View
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="knowledge" className="mt-6">
          <div className="mb-6">
            <div className="relative max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search knowledge base..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {articles.filter(a => 
              a.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
              a.excerpt.toLowerCase().includes(searchQuery.toLowerCase())
            ).map((article) => (
              <Card key={article.id} className="hover:shadow-md transition-shadow cursor-pointer">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <Badge variant="outline" className="mb-2 text-xs">{article.category}</Badge>
                      <h3 className="font-medium mb-1">{article.title}</h3>
                      <p className="text-sm text-muted-foreground line-clamp-2">{article.excerpt}</p>
                      <div className="flex items-center gap-4 mt-3 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Eye className="h-3 w-3" />
                          {article.views} views
                        </span>
                        <span className="flex items-center gap-1">
                          <CheckCircle className="h-3 w-3" />
                          {article.helpful_count} found helpful
                        </span>
                      </div>
                    </div>
                    <ExternalLink className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="notifications" className="mt-6">
          <div className="space-y-2">
            {notifications.map((notif) => (
              <Card
                key={notif.id}
                className={`cursor-pointer ${!notif.read ? 'border-l-4 border-l-primary' : ''}`}
                onClick={() => markNotificationRead(notif.id)}
              >
                <CardContent className="p-4">
                  <div className="flex items-start gap-4">
                    <div className={`rounded-full p-2 ${
                      notif.type === 'success' ? 'bg-green-100' :
                      notif.type === 'warning' ? 'bg-yellow-100' : 'bg-blue-100'
                    }`}>
                      {notif.type === 'success' ? <CheckCircle className="h-4 w-4 text-green-600" /> :
                       notif.type === 'warning' ? <AlertCircle className="h-4 w-4 text-yellow-600" /> :
                       <Bell className="h-4 w-4 text-blue-600" />}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <p className={`font-medium ${!notif.read ? '' : 'text-muted-foreground'}`}>{notif.title}</p>
                        <span className="text-xs text-muted-foreground">
                          {new Date(notif.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground mt-1">{notif.message}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
