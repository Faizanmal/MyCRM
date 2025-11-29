'use client';

import { useEffect, useState, useCallback } from 'react';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import {
  Calendar,
  Clock,
  Video,
  Phone,
  MapPin,
  Plus,
  Settings,
  Link as LinkIcon,
  Copy,
  ExternalLink,
  Users,
  TrendingUp,
  XCircle,
  RefreshCw,
  Globe,
  Edit
} from 'lucide-react';
import { toast } from 'sonner';
import { smartSchedulingAPI } from '@/lib/premium-features-api';

interface MeetingType {
  id: string;
  name: string;
  duration: number;
  location_type: string;
  color: string;
  is_active: boolean;
  bookings_count: number;
}

interface Meeting {
  id: string;
  meeting_type_name: string;
  attendee_name: string;
  attendee_email: string;
  start_time: string;
  end_time: string;
  status: string;
  location_type: string;
  meeting_link?: string;
}

interface SchedulingPage {
  id: string;
  name: string;
  slug: string;
  is_active: boolean;
  meeting_types_count: number;
  total_bookings: number;
}

interface SchedulingMetrics {
  total_meetings: number;
  meetings_this_week: number;
  avg_meetings_per_day: number;
  no_show_rate: number;
  most_popular_type: string;
}

export default function SmartSchedulingPage() {
  const [loading, setLoading] = useState(true);
  const [meetingTypes, setMeetingTypes] = useState<MeetingType[]>([]);
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [pages, setPages] = useState<SchedulingPage[]>([]);
  const [metrics, setMetrics] = useState<SchedulingMetrics | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      
      const [typesRes, meetingsRes, pagesRes, analyticsRes] = await Promise.all([
        smartSchedulingAPI.getMeetingTypes(),
        smartSchedulingAPI.getMeetings({ limit: 10 }),
        smartSchedulingAPI.getPages(),
        smartSchedulingAPI.getSchedulingAnalytics()
      ]);

      setMeetingTypes(typesRes.data.results || []);
      setMeetings(meetingsRes.data.results || []);
      setPages(pagesRes.data.results || []);
      setMetrics(analyticsRes.data || null);
    } catch (error) {
      console.error('Failed to fetch scheduling data:', error);
      // Demo data
      setMeetingTypes([
        { id: '1', name: '15 Minute Call', duration: 15, location_type: 'phone', color: '#3b82f6', is_active: true, bookings_count: 89 },
        { id: '2', name: '30 Minute Meeting', duration: 30, location_type: 'video', color: '#8b5cf6', is_active: true, bookings_count: 156 },
        { id: '3', name: '60 Minute Consultation', duration: 60, location_type: 'video', color: '#10b981', is_active: true, bookings_count: 45 },
        { id: '4', name: 'In-Person Demo', duration: 45, location_type: 'in_person', color: '#f59e0b', is_active: false, bookings_count: 23 },
      ]);
      setMeetings([
        { id: '1', meeting_type_name: '30 Minute Meeting', attendee_name: 'John Smith', attendee_email: 'john@acme.com', start_time: new Date(Date.now() + 3600000).toISOString(), end_time: new Date(Date.now() + 5400000).toISOString(), status: 'confirmed', location_type: 'video', meeting_link: 'https://meet.example.com/abc123' },
        { id: '2', meeting_type_name: '15 Minute Call', attendee_name: 'Sarah Johnson', attendee_email: 'sarah@techcorp.io', start_time: new Date(Date.now() + 86400000).toISOString(), end_time: new Date(Date.now() + 87300000).toISOString(), status: 'confirmed', location_type: 'phone' },
        { id: '3', meeting_type_name: '60 Minute Consultation', attendee_name: 'Mike Chen', attendee_email: 'mike@startup.co', start_time: new Date(Date.now() + 172800000).toISOString(), end_time: new Date(Date.now() + 176400000).toISOString(), status: 'pending', location_type: 'video' },
      ]);
      setPages([
        { id: '1', name: 'Sales Team', slug: 'sales', is_active: true, meeting_types_count: 3, total_bookings: 234 },
        { id: '2', name: 'Customer Success', slug: 'success', is_active: true, meeting_types_count: 2, total_bookings: 156 },
      ]);
      setMetrics({
        total_meetings: 523,
        meetings_this_week: 24,
        avg_meetings_per_day: 3.4,
        no_show_rate: 8,
        most_popular_type: '30 Minute Meeting'
      });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleCopyLink = (slug: string) => {
    const link = `${window.location.origin}/book/${slug}`;
    navigator.clipboard.writeText(link);
    toast.success('Booking link copied to clipboard');
  };

  const handleCancelMeeting = async (meetingId: string) => {
    try {
      await smartSchedulingAPI.cancelMeeting(meetingId);
      toast.success('Meeting cancelled');
      fetchData();
    } catch {
      toast.error('Failed to cancel meeting');
    }
  };

  const getLocationIcon = (type: string) => {
    switch (type) {
      case 'video':
        return <Video className="w-4 h-4" />;
      case 'phone':
        return <Phone className="w-4 h-4" />;
      case 'in_person':
        return <MapPin className="w-4 h-4" />;
      default:
        return <Globe className="w-4 h-4" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      confirmed: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
      pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
      cancelled: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
      completed: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
    };
    return styles[status] || styles.pending;
  };

  const formatDateTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return {
      date: date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }),
      time: date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })
    };
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-6 space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h1 className="text-3xl font-bold gradient-text flex items-center gap-2">
                <Calendar className="w-8 h-8" />
                Smart Scheduling
              </h1>
              <p className="text-muted-foreground mt-1">
                Let clients book time with you automatically
              </p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => fetchData()}>
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </Button>
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                New Meeting Type
              </Button>
            </div>
          </div>

          {/* Metrics Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card className="modern-card">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Total Meetings
                </CardTitle>
                <Calendar className="w-5 h-5 text-blue-500" />
              </CardHeader>
              <CardContent>
                {loading ? (
                  <Skeleton className="h-8 w-20" />
                ) : (
                  <div className="text-2xl font-bold">{metrics?.total_meetings}</div>
                )}
              </CardContent>
            </Card>

            <Card className="modern-card">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  This Week
                </CardTitle>
                <TrendingUp className="w-5 h-5 text-green-500" />
              </CardHeader>
              <CardContent>
                {loading ? (
                  <Skeleton className="h-8 w-20" />
                ) : (
                  <>
                    <div className="text-2xl font-bold">{metrics?.meetings_this_week}</div>
                    <p className="text-xs text-muted-foreground">~{metrics?.avg_meetings_per_day}/day</p>
                  </>
                )}
              </CardContent>
            </Card>

            <Card className="modern-card">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  No-Show Rate
                </CardTitle>
                <XCircle className="w-5 h-5 text-red-500" />
              </CardHeader>
              <CardContent>
                {loading ? (
                  <Skeleton className="h-8 w-20" />
                ) : (
                  <div className="text-2xl font-bold">{metrics?.no_show_rate}%</div>
                )}
              </CardContent>
            </Card>

            <Card className="modern-card">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Most Popular
                </CardTitle>
                <Users className="w-5 h-5 text-purple-500" />
              </CardHeader>
              <CardContent>
                {loading ? (
                  <Skeleton className="h-8 w-32" />
                ) : (
                  <div className="text-lg font-bold truncate">{metrics?.most_popular_type}</div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Tabs */}
          <Tabs defaultValue="upcoming" className="space-y-4">
            <TabsList className="grid w-full grid-cols-3 lg:w-auto lg:inline-grid">
              <TabsTrigger value="upcoming">Upcoming Meetings</TabsTrigger>
              <TabsTrigger value="meeting-types">Meeting Types</TabsTrigger>
              <TabsTrigger value="booking-pages">Booking Pages</TabsTrigger>
            </TabsList>

            <TabsContent value="upcoming" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Upcoming Meetings</CardTitle>
                  <CardDescription>Your scheduled meetings</CardDescription>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <div className="space-y-3">
                      {[1, 2, 3].map((i) => (
                        <Skeleton key={i} className="h-20 w-full" />
                      ))}
                    </div>
                  ) : meetings.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      <Calendar className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p>No upcoming meetings</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {meetings.map((meeting) => {
                        const { date, time } = formatDateTime(meeting.start_time);
                        return (
                          <div
                            key={meeting.id}
                            className="flex items-center justify-between p-4 rounded-lg border hover:bg-accent/50 transition-colors"
                          >
                            <div className="flex items-start gap-4">
                              <div className="text-center min-w-[80px]">
                                <div className="text-sm font-medium">{date}</div>
                                <div className="text-lg font-bold text-primary">{time}</div>
                              </div>
                              <div>
                                <div className="flex items-center gap-2">
                                  <h4 className="font-semibold">{meeting.attendee_name}</h4>
                                  <Badge className={getStatusBadge(meeting.status)}>
                                    {meeting.status}
                                  </Badge>
                                </div>
                                <p className="text-sm text-muted-foreground">{meeting.attendee_email}</p>
                                <div className="flex items-center gap-2 mt-1 text-sm text-muted-foreground">
                                  {getLocationIcon(meeting.location_type)}
                                  <span>{meeting.meeting_type_name}</span>
                                </div>
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              {meeting.meeting_link && (
                                <Button variant="outline" size="sm" asChild>
                                  <a href={meeting.meeting_link} target="_blank" rel="noopener noreferrer">
                                    <Video className="w-4 h-4 mr-2" />
                                    Join
                                  </a>
                                </Button>
                              )}
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleCancelMeeting(meeting.id)}
                              >
                                Cancel
                              </Button>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="meeting-types" className="space-y-4">
              <Card>
                <CardHeader>
                  <div className="flex justify-between items-center">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        <Clock className="w-5 h-5" />
                        Meeting Types
                      </CardTitle>
                      <CardDescription>Configure different meeting durations and types</CardDescription>
                    </div>
                    <Button>
                      <Plus className="w-4 h-4 mr-2" />
                      Add Type
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {[1, 2, 3, 4].map((i) => (
                        <Skeleton key={i} className="h-32 w-full" />
                      ))}
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {meetingTypes.map((type) => (
                        <div
                          key={type.id}
                          className="p-4 rounded-lg border hover:shadow-md transition-all"
                          style={{ borderLeftWidth: '4px', borderLeftColor: type.color }}
                        >
                          <div className="flex items-start justify-between">
                            <div>
                              <div className="flex items-center gap-2">
                                <h4 className="font-semibold">{type.name}</h4>
                                {!type.is_active && (
                                  <Badge variant="outline" className="text-muted-foreground">
                                    Inactive
                                  </Badge>
                                )}
                              </div>
                              <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                                <span className="flex items-center gap-1">
                                  <Clock className="w-4 h-4" />
                                  {type.duration} min
                                </span>
                                <span className="flex items-center gap-1">
                                  {getLocationIcon(type.location_type)}
                                  {type.location_type.replace('_', ' ')}
                                </span>
                              </div>
                              <p className="text-sm mt-2">
                                <span className="font-medium">{type.bookings_count}</span> bookings
                              </p>
                            </div>
                            <div className="flex items-center gap-2">
                              <Switch checked={type.is_active} />
                              <Button variant="ghost" size="icon">
                                <Edit className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="booking-pages" className="space-y-4">
              <Card>
                <CardHeader>
                  <div className="flex justify-between items-center">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        <Globe className="w-5 h-5" />
                        Booking Pages
                      </CardTitle>
                      <CardDescription>Public pages where clients can book time with you</CardDescription>
                    </div>
                    <Button>
                      <Plus className="w-4 h-4 mr-2" />
                      New Page
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <div className="space-y-4">
                      {[1, 2].map((i) => (
                        <Skeleton key={i} className="h-24 w-full" />
                      ))}
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {pages.map((page) => (
                        <div
                          key={page.id}
                          className="flex items-center justify-between p-4 rounded-lg border hover:bg-accent/50 transition-colors"
                        >
                          <div>
                            <div className="flex items-center gap-2">
                              <h4 className="font-semibold">{page.name}</h4>
                              <Badge
                                className={
                                  page.is_active
                                    ? 'bg-green-100 text-green-800 dark:bg-green-900/30'
                                    : 'bg-gray-100 text-gray-800 dark:bg-gray-900/30'
                                }
                              >
                                {page.is_active ? 'Active' : 'Inactive'}
                              </Badge>
                            </div>
                            <div className="flex items-center gap-1 mt-1 text-sm text-muted-foreground">
                              <LinkIcon className="w-3 h-3" />
                              <code className="text-xs bg-secondary px-2 py-0.5 rounded">
                                /book/{page.slug}
                              </code>
                            </div>
                            <div className="flex items-center gap-4 mt-2 text-sm">
                              <span>{page.meeting_types_count} meeting types</span>
                              <span>{page.total_bookings} bookings</span>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleCopyLink(page.slug)}
                            >
                              <Copy className="w-4 h-4 mr-2" />
                              Copy Link
                            </Button>
                            <Button variant="outline" size="sm" asChild>
                              <a href={`/book/${page.slug}`} target="_blank" rel="noopener noreferrer">
                                <ExternalLink className="w-4 h-4 mr-2" />
                                Preview
                              </a>
                            </Button>
                            <Button variant="ghost" size="icon">
                              <Settings className="w-4 h-4" />
                            </Button>
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
