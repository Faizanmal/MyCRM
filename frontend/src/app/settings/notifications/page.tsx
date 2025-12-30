'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { toast } from 'sonner';
import {
    Bell,
    Mail,
    Smartphone,
    Monitor,
    Volume2,
    VolumeX,
    Clock,
    Calendar,
    Target,
    Users,
    MessageSquare,
    Trophy,
    Sparkles,
    AlertCircle,
    CheckCircle2,
    Settings,
    Save,
    RotateCcw,
    Loader2,
    BellOff,
    Zap,
} from 'lucide-react';

// Types
interface NotificationChannel {
    id: string;
    label: string;
    description: string;
    icon: React.ElementType;
    enabled: boolean;
}

interface NotificationType {
    id: string;
    label: string;
    description: string;
    icon: React.ElementType;
    category: 'deals' | 'tasks' | 'social' | 'system' | 'ai';
    channels: {
        email: boolean;
        push: boolean;
        inApp: boolean;
        sms: boolean;
    };
    frequency: 'instant' | 'hourly' | 'daily' | 'weekly';
    priority: 'low' | 'medium' | 'high';
}

interface QuietHours {
    enabled: boolean;
    startTime: string;
    endTime: string;
    days: string[];
}

interface DigestSettings {
    enabled: boolean;
    frequency: 'daily' | 'weekly';
    time: string;
    includeAI: boolean;
    includeMetrics: boolean;
}

// Default notification types
const defaultNotificationTypes: NotificationType[] = [
    // Deals
    {
        id: 'deal_stage_change',
        label: 'Deal Stage Changes',
        description: 'When a deal moves to a new stage',
        icon: Target,
        category: 'deals',
        channels: { email: true, push: true, inApp: true, sms: false },
        frequency: 'instant',
        priority: 'high',
    },
    {
        id: 'deal_won',
        label: 'Deal Won',
        description: 'When a deal is marked as won',
        icon: Trophy,
        category: 'deals',
        channels: { email: true, push: true, inApp: true, sms: false },
        frequency: 'instant',
        priority: 'high',
    },
    {
        id: 'deal_lost',
        label: 'Deal Lost',
        description: 'When a deal is marked as lost',
        icon: AlertCircle,
        category: 'deals',
        channels: { email: true, push: false, inApp: true, sms: false },
        frequency: 'instant',
        priority: 'medium',
    },
    {
        id: 'deal_assigned',
        label: 'Deal Assigned',
        description: 'When a deal is assigned to you',
        icon: Target,
        category: 'deals',
        channels: { email: true, push: true, inApp: true, sms: false },
        frequency: 'instant',
        priority: 'high',
    },

    // Tasks
    {
        id: 'task_due_soon',
        label: 'Task Due Soon',
        description: 'Reminder before task deadline',
        icon: Clock,
        category: 'tasks',
        channels: { email: true, push: true, inApp: true, sms: false },
        frequency: 'instant',
        priority: 'high',
    },
    {
        id: 'task_overdue',
        label: 'Task Overdue',
        description: 'When a task passes its due date',
        icon: AlertCircle,
        category: 'tasks',
        channels: { email: true, push: true, inApp: true, sms: true },
        frequency: 'instant',
        priority: 'high',
    },
    {
        id: 'task_assigned',
        label: 'Task Assigned',
        description: 'When a task is assigned to you',
        icon: CheckCircle2,
        category: 'tasks',
        channels: { email: true, push: true, inApp: true, sms: false },
        frequency: 'instant',
        priority: 'medium',
    },

    // Social
    {
        id: 'mention',
        label: 'Mentions',
        description: 'When someone @mentions you',
        icon: MessageSquare,
        category: 'social',
        channels: { email: true, push: true, inApp: true, sms: false },
        frequency: 'instant',
        priority: 'high',
    },
    {
        id: 'comment',
        label: 'Comments',
        description: 'New comments on your items',
        icon: MessageSquare,
        category: 'social',
        channels: { email: false, push: true, inApp: true, sms: false },
        frequency: 'instant',
        priority: 'medium',
    },
    {
        id: 'team_activity',
        label: 'Team Activity',
        description: 'Activity from your team members',
        icon: Users,
        category: 'social',
        channels: { email: false, push: false, inApp: true, sms: false },
        frequency: 'hourly',
        priority: 'low',
    },

    // System
    {
        id: 'system_updates',
        label: 'System Updates',
        description: 'Product updates and new features',
        icon: Settings,
        category: 'system',
        channels: { email: true, push: false, inApp: true, sms: false },
        frequency: 'weekly',
        priority: 'low',
    },
    {
        id: 'security_alerts',
        label: 'Security Alerts',
        description: 'Login attempts and security events',
        icon: AlertCircle,
        category: 'system',
        channels: { email: true, push: true, inApp: true, sms: true },
        frequency: 'instant',
        priority: 'high',
    },

    // AI
    {
        id: 'ai_recommendations',
        label: 'AI Recommendations',
        description: 'Personalized AI-powered suggestions',
        icon: Sparkles,
        category: 'ai',
        channels: { email: false, push: true, inApp: true, sms: false },
        frequency: 'daily',
        priority: 'medium',
    },
    {
        id: 'ai_insights',
        label: 'AI Insights',
        description: 'Automated insights about your data',
        icon: Zap,
        category: 'ai',
        channels: { email: true, push: false, inApp: true, sms: false },
        frequency: 'weekly',
        priority: 'low',
    },
];

const daysOfWeek = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

export default function NotificationPreferencesPage() {
    const [isSaving, setIsSaving] = useState(false);
    const [hasChanges, setHasChanges] = useState(false);

    // Channels state
    const [channels, setChannels] = useState<NotificationChannel[]>([
        { id: 'email', label: 'Email', description: 'Receive notifications via email', icon: Mail, enabled: true },
        { id: 'push', label: 'Push', description: 'Browser push notifications', icon: Monitor, enabled: true },
        { id: 'inApp', label: 'In-App', description: 'Notifications within the app', icon: Bell, enabled: true },
        { id: 'sms', label: 'SMS', description: 'Text message alerts', icon: Smartphone, enabled: false },
    ]);

    // Notification types state
    const [notificationTypes, setNotificationTypes] = useState<NotificationType[]>(defaultNotificationTypes);

    // Quiet hours state
    const [quietHours, setQuietHours] = useState<QuietHours>({
        enabled: false,
        startTime: '22:00',
        endTime: '08:00',
        days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
    });

    // Digest settings
    const [digest, setDigest] = useState<DigestSettings>({
        enabled: true,
        frequency: 'daily',
        time: '09:00',
        includeAI: true,
        includeMetrics: true,
    });

    // Sound settings
    const [soundEnabled, setSoundEnabled] = useState(true);
    const [soundVolume, setSoundVolume] = useState(70);

    // Toggle channel
    const toggleChannel = (channelId: string) => {
        setChannels(prev => prev.map(ch =>
            ch.id === channelId ? { ...ch, enabled: !ch.enabled } : ch
        ));
        setHasChanges(true);
    };

    // Toggle notification type channel
    const toggleNotificationChannel = (typeId: string, channelId: keyof NotificationType['channels']) => {
        setNotificationTypes(prev => prev.map(nt =>
            nt.id === typeId
                ? { ...nt, channels: { ...nt.channels, [channelId]: !nt.channels[channelId] } }
                : nt
        ));
        setHasChanges(true);
    };

    // Update frequency
    const updateFrequency = (typeId: string, frequency: NotificationType['frequency']) => {
        setNotificationTypes(prev => prev.map(nt =>
            nt.id === typeId ? { ...nt, frequency } : nt
        ));
        setHasChanges(true);
    };

    // Toggle quiet hours day
    const toggleQuietDay = (day: string) => {
        setQuietHours(prev => ({
            ...prev,
            days: prev.days.includes(day)
                ? prev.days.filter(d => d !== day)
                : [...prev.days, day],
        }));
        setHasChanges(true);
    };

    // Save settings
    const saveSettings = async () => {
        setIsSaving(true);
        try {
            await new Promise(resolve => setTimeout(resolve, 800));

            // Save to localStorage
            localStorage.setItem('notification_channels', JSON.stringify(channels));
            localStorage.setItem('notification_types', JSON.stringify(notificationTypes));
            localStorage.setItem('quiet_hours', JSON.stringify(quietHours));
            localStorage.setItem('digest_settings', JSON.stringify(digest));
            localStorage.setItem('sound_settings', JSON.stringify({ enabled: soundEnabled, volume: soundVolume }));

            setHasChanges(false);
            toast.success('Notification preferences saved');
        } catch (error) {
            toast.error('Failed to save preferences');
        } finally {
            setIsSaving(false);
        }
    };

    // Reset to defaults
    const resetToDefaults = () => {
        setNotificationTypes(defaultNotificationTypes);
        setQuietHours({
            enabled: false,
            startTime: '22:00',
            endTime: '08:00',
            days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
        });
        setDigest({
            enabled: true,
            frequency: 'daily',
            time: '09:00',
            includeAI: true,
            includeMetrics: true,
        });
        setSoundEnabled(true);
        setSoundVolume(70);
        setHasChanges(true);
        toast.info('Settings reset to defaults');
    };

    // Group notification types by category
    const groupedNotifications = notificationTypes.reduce((acc, nt) => {
        if (!acc[nt.category]) acc[nt.category] = [];
        acc[nt.category].push(nt);
        return acc;
    }, {} as Record<string, NotificationType[]>);

    const categoryLabels: Record<string, { label: string; icon: React.ElementType }> = {
        deals: { label: 'Deals & Pipeline', icon: Target },
        tasks: { label: 'Tasks & Reminders', icon: CheckCircle2 },
        social: { label: 'Social & Team', icon: Users },
        system: { label: 'System', icon: Settings },
        ai: { label: 'AI & Insights', icon: Sparkles },
    };

    return (
        <div className="container mx-auto py-8 px-4 max-w-4xl">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-3xl font-bold flex items-center gap-3">
                        <Bell className="w-8 h-8 text-blue-500" />
                        Notification Preferences
                    </h1>
                    <p className="text-gray-500 mt-1">Control how and when you receive notifications</p>
                </div>

                <div className="flex items-center gap-3">
                    <Button variant="outline" onClick={resetToDefaults}>
                        <RotateCcw className="w-4 h-4 mr-2" />
                        Reset
                    </Button>
                    <Button onClick={saveSettings} disabled={!hasChanges || isSaving}>
                        {isSaving ? (
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        ) : (
                            <Save className="w-4 h-4 mr-2" />
                        )}
                        Save Changes
                    </Button>
                </div>
            </div>

            <Tabs defaultValue="channels" className="space-y-6">
                <TabsList className="grid w-full grid-cols-4">
                    <TabsTrigger value="channels">Channels</TabsTrigger>
                    <TabsTrigger value="notifications">Notifications</TabsTrigger>
                    <TabsTrigger value="schedule">Schedule</TabsTrigger>
                    <TabsTrigger value="preferences">Preferences</TabsTrigger>
                </TabsList>

                {/* Channels Tab */}
                <TabsContent value="channels">
                    <Card>
                        <CardHeader>
                            <CardTitle>Notification Channels</CardTitle>
                            <CardDescription>Choose how you want to receive notifications</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {channels.map((channel) => (
                                <div
                                    key={channel.id}
                                    className={`flex items-center justify-between p-4 rounded-lg border transition-colors ${channel.enabled ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-200' : 'bg-gray-50 dark:bg-gray-800 border-gray-200'
                                        }`}
                                >
                                    <div className="flex items-center gap-4">
                                        <div className={`p-3 rounded-full ${channel.enabled ? 'bg-blue-100 text-blue-600' : 'bg-gray-200 text-gray-400'
                                            }`}>
                                            <channel.icon className="w-5 h-5" />
                                        </div>
                                        <div>
                                            <Label className="text-base font-medium">{channel.label}</Label>
                                            <p className="text-sm text-gray-500">{channel.description}</p>
                                        </div>
                                    </div>
                                    <Switch
                                        checked={channel.enabled}
                                        onCheckedChange={() => toggleChannel(channel.id)}
                                    />
                                </div>
                            ))}
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Notifications Tab */}
                <TabsContent value="notifications" className="space-y-6">
                    {Object.entries(groupedNotifications).map(([category, types]) => (
                        <Card key={category}>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    {categoryLabels[category] && (
                                        <>
                                            {(() => {
                                                const Icon = categoryLabels[category].icon;
                                                return <Icon className="w-5 h-5 text-blue-500" />;
                                            })()}
                                            {categoryLabels[category].label}
                                        </>
                                    )}
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                {types.map((type) => (
                                    <div key={type.id} className="border rounded-lg p-4">
                                        <div className="flex items-start justify-between mb-3">
                                            <div className="flex items-center gap-3">
                                                <type.icon className="w-5 h-5 text-gray-500" />
                                                <div>
                                                    <Label className="font-medium">{type.label}</Label>
                                                    <p className="text-sm text-gray-500">{type.description}</p>
                                                </div>
                                            </div>
                                            <Badge variant={
                                                type.priority === 'high' ? 'destructive' :
                                                    type.priority === 'medium' ? 'default' : 'secondary'
                                            }>
                                                {type.priority}
                                            </Badge>
                                        </div>

                                        <div className="flex items-center gap-6 mt-4">
                                            <div className="flex items-center gap-4">
                                                {Object.entries(type.channels).map(([channelId, enabled]) => {
                                                    const channel = channels.find(c => c.id === channelId);
                                                    const isChannelEnabled = channels.find(c => c.id === channelId)?.enabled;

                                                    return (
                                                        <div
                                                            key={channelId}
                                                            className={`flex items-center gap-2 ${!isChannelEnabled ? 'opacity-50' : ''}`}
                                                            title={!isChannelEnabled ? `${channel?.label} channel is disabled` : ''}
                                                        >
                                                            <Switch
                                                                id={`${type.id}-${channelId}`}
                                                                checked={enabled && isChannelEnabled}
                                                                onCheckedChange={() => toggleNotificationChannel(type.id, channelId as keyof NotificationType['channels'])}
                                                                disabled={!isChannelEnabled}
                                                            />
                                                            <Label htmlFor={`${type.id}-${channelId}`} className="text-sm capitalize">
                                                                {channelId === 'inApp' ? 'In-App' : channelId}
                                                            </Label>
                                                        </div>
                                                    );
                                                })}
                                            </div>

                                            <Separator orientation="vertical" className="h-6" />

                                            <div className="flex items-center gap-2">
                                                <Label className="text-sm text-gray-500">Frequency:</Label>
                                                <select
                                                    value={type.frequency}
                                                    onChange={(e) => updateFrequency(type.id, e.target.value as NotificationType['frequency'])}
                                                    className="text-sm border rounded px-2 py-1"
                                                >
                                                    <option value="instant">Instant</option>
                                                    <option value="hourly">Hourly</option>
                                                    <option value="daily">Daily</option>
                                                    <option value="weekly">Weekly</option>
                                                </select>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </CardContent>
                        </Card>
                    ))}
                </TabsContent>

                {/* Schedule Tab */}
                <TabsContent value="schedule" className="space-y-6">
                    {/* Quiet Hours */}
                    <Card>
                        <CardHeader>
                            <div className="flex items-center justify-between">
                                <div>
                                    <CardTitle className="flex items-center gap-2">
                                        <BellOff className="w-5 h-5" />
                                        Quiet Hours
                                    </CardTitle>
                                    <CardDescription>Pause notifications during specific times</CardDescription>
                                </div>
                                <Switch
                                    checked={quietHours.enabled}
                                    onCheckedChange={(checked) => {
                                        setQuietHours(prev => ({ ...prev, enabled: checked }));
                                        setHasChanges(true);
                                    }}
                                />
                            </div>
                        </CardHeader>
                        <AnimatePresence>
                            {quietHours.enabled && (
                                <motion.div
                                    initial={{ height: 0, opacity: 0 }}
                                    animate={{ height: 'auto', opacity: 1 }}
                                    exit={{ height: 0, opacity: 0 }}
                                >
                                    <CardContent className="space-y-4">
                                        <div className="flex items-center gap-4">
                                            <div>
                                                <Label>Start Time</Label>
                                                <Input
                                                    type="time"
                                                    value={quietHours.startTime}
                                                    onChange={(e) => {
                                                        setQuietHours(prev => ({ ...prev, startTime: e.target.value }));
                                                        setHasChanges(true);
                                                    }}
                                                    className="w-32"
                                                />
                                            </div>
                                            <div>
                                                <Label>End Time</Label>
                                                <Input
                                                    type="time"
                                                    value={quietHours.endTime}
                                                    onChange={(e) => {
                                                        setQuietHours(prev => ({ ...prev, endTime: e.target.value }));
                                                        setHasChanges(true);
                                                    }}
                                                    className="w-32"
                                                />
                                            </div>
                                        </div>

                                        <div>
                                            <Label className="mb-2 block">Active Days</Label>
                                            <div className="flex gap-2">
                                                {daysOfWeek.map((day) => (
                                                    <Button
                                                        key={day}
                                                        variant={quietHours.days.includes(day) ? 'default' : 'outline'}
                                                        size="sm"
                                                        onClick={() => toggleQuietDay(day)}
                                                        className="w-12"
                                                    >
                                                        {day}
                                                    </Button>
                                                ))}
                                            </div>
                                        </div>
                                    </CardContent>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </Card>

                    {/* Digest */}
                    <Card>
                        <CardHeader>
                            <div className="flex items-center justify-between">
                                <div>
                                    <CardTitle className="flex items-center gap-2">
                                        <Calendar className="w-5 h-5" />
                                        Email Digest
                                    </CardTitle>
                                    <CardDescription>Receive a summary of notifications</CardDescription>
                                </div>
                                <Switch
                                    checked={digest.enabled}
                                    onCheckedChange={(checked) => {
                                        setDigest(prev => ({ ...prev, enabled: checked }));
                                        setHasChanges(true);
                                    }}
                                />
                            </div>
                        </CardHeader>
                        <AnimatePresence>
                            {digest.enabled && (
                                <motion.div
                                    initial={{ height: 0, opacity: 0 }}
                                    animate={{ height: 'auto', opacity: 1 }}
                                    exit={{ height: 0, opacity: 0 }}
                                >
                                    <CardContent className="space-y-4">
                                        <div className="flex items-center gap-4">
                                            <div>
                                                <Label>Frequency</Label>
                                                <RadioGroup
                                                    value={digest.frequency}
                                                    onValueChange={(value) => {
                                                        setDigest(prev => ({ ...prev, frequency: value as DigestSettings['frequency'] }));
                                                        setHasChanges(true);
                                                    }}
                                                    className="flex gap-4 mt-2"
                                                >
                                                    <Label className="flex items-center gap-2">
                                                        <RadioGroupItem value="daily" />
                                                        Daily
                                                    </Label>
                                                    <Label className="flex items-center gap-2">
                                                        <RadioGroupItem value="weekly" />
                                                        Weekly
                                                    </Label>
                                                </RadioGroup>
                                            </div>

                                            <div>
                                                <Label>Send Time</Label>
                                                <Input
                                                    type="time"
                                                    value={digest.time}
                                                    onChange={(e) => {
                                                        setDigest(prev => ({ ...prev, time: e.target.value }));
                                                        setHasChanges(true);
                                                    }}
                                                    className="w-32"
                                                />
                                            </div>
                                        </div>

                                        <Separator />

                                        <div className="space-y-3">
                                            <div className="flex items-center justify-between">
                                                <Label>Include AI recommendations</Label>
                                                <Switch
                                                    checked={digest.includeAI}
                                                    onCheckedChange={(checked) => {
                                                        setDigest(prev => ({ ...prev, includeAI: checked }));
                                                        setHasChanges(true);
                                                    }}
                                                />
                                            </div>
                                            <div className="flex items-center justify-between">
                                                <Label>Include performance metrics</Label>
                                                <Switch
                                                    checked={digest.includeMetrics}
                                                    onCheckedChange={(checked) => {
                                                        setDigest(prev => ({ ...prev, includeMetrics: checked }));
                                                        setHasChanges(true);
                                                    }}
                                                />
                                            </div>
                                        </div>
                                    </CardContent>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </Card>
                </TabsContent>

                {/* Preferences Tab */}
                <TabsContent value="preferences">
                    <Card>
                        <CardHeader>
                            <CardTitle>Sound Settings</CardTitle>
                            <CardDescription>Configure notification sounds</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    {soundEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5 text-gray-400" />}
                                    <div>
                                        <Label>Notification Sounds</Label>
                                        <p className="text-sm text-gray-500">Play sounds for new notifications</p>
                                    </div>
                                </div>
                                <Switch
                                    checked={soundEnabled}
                                    onCheckedChange={(checked) => {
                                        setSoundEnabled(checked);
                                        setHasChanges(true);
                                    }}
                                />
                            </div>

                            {soundEnabled && (
                                <div className="space-y-2">
                                    <div className="flex items-center justify-between">
                                        <Label>Volume</Label>
                                        <span className="text-sm text-gray-500">{soundVolume}%</span>
                                    </div>
                                    <Slider
                                        value={[soundVolume]}
                                        onValueChange={(value) => {
                                            setSoundVolume(value[0]);
                                            setHasChanges(true);
                                        }}
                                        min={0}
                                        max={100}
                                        step={10}
                                    />
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
}
