'use client';

import { useState, useEffect, useCallback } from 'react';
// import { motion } from 'framer-motion';
import { toast } from 'sonner';
import {
    Settings,
    Palette,
    Bell,
    Layout,
    Shield,
    Download,
    Keyboard,
    Save,
    RotateCcw,
    Moon,
    Sun,
    Monitor,
    Loader2,
    Check,
} from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Slider } from '@/components/ui/slider';
import { useUserPreferences } from '@/hooks/useInteractiveFeatures';

// Types
interface AppearanceSettings {
    theme: 'light' | 'dark' | 'system';
    accentColor: string;
    fontSize: number;
    compactMode: boolean;
    animationsEnabled: boolean;
    highContrast: boolean;
}

interface NotificationSettings {
    emailNotifications: boolean;
    pushNotifications: boolean;
    dealUpdates: boolean;
    taskReminders: boolean;
    mentions: boolean;
    weeklyDigest: boolean;
    quietHoursEnabled: boolean;
    quietHoursStart: string;
    quietHoursEnd: string;
}

interface DashboardSettings {
    defaultView: 'overview' | 'pipeline' | 'activity' | 'analytics';
    sidebarCollapsed: boolean;
    showWelcomeMessage: boolean;
    autoRefreshEnabled: boolean;
    autoRefreshInterval: number;
}

interface PrivacySettings {
    shareActivityWithTeam: boolean;
    showOnlineStatus: boolean;
    allowMentions: boolean;
    dataExportEnabled: boolean;
}

interface KeyboardShortcuts {
    search: string;
    newContact: string;
    newDeal: string;
    newTask: string;
    help: string;
}

// Color palette options
const colorOptions = [
    { name: 'Blue', value: '#3b82f6' },
    { name: 'Purple', value: '#8b5cf6' },
    { name: 'Green', value: '#22c55e' },
    { name: 'Orange', value: '#f97316' },
    { name: 'Pink', value: '#ec4899' },
    { name: 'Teal', value: '#14b8a6' },
    { name: 'Red', value: '#ef4444' },
    { name: 'Indigo', value: '#6366f1' },
];

export default function UserPreferencesPage() {
    const { preferences, updatePreferences, isLoading } = useUserPreferences();
    const [isSaving, setIsSaving] = useState(false);
    const [hasChanges, setHasChanges] = useState(false);

    // Local state for settings
    const [appearance, setAppearance] = useState<AppearanceSettings>({
        theme: 'system',
        accentColor: '#3b82f6',
        fontSize: 14,
        compactMode: false,
        animationsEnabled: true,
        highContrast: false,
    });

    const [notifications, setNotifications] = useState<NotificationSettings>({
        emailNotifications: true,
        pushNotifications: true,
        dealUpdates: true,
        taskReminders: true,
        mentions: true,
        weeklyDigest: true,
        quietHoursEnabled: false,
        quietHoursStart: '22:00',
        quietHoursEnd: '08:00',
    });

    const [dashboard, setDashboard] = useState<DashboardSettings>({
        defaultView: 'overview',
        sidebarCollapsed: false,
        showWelcomeMessage: true,
        autoRefreshEnabled: true,
        autoRefreshInterval: 30,
    });

    const [privacy, setPrivacy] = useState<PrivacySettings>({
        shareActivityWithTeam: true,
        showOnlineStatus: true,
        allowMentions: true,
        dataExportEnabled: true,
    });

    const [shortcuts, setShortcuts] = useState<KeyboardShortcuts>({
        search: '⌘+K',
        newContact: '⌘+Shift+C',
        newDeal: '⌘+Shift+D',
        newTask: '⌘+Shift+T',
        help: '⌘+/',
    });

    // Load preferences from API
    useEffect(() => {
        if (preferences) {
            setAppearance(prev => ({
                ...prev,
                theme: preferences.theme || 'system',
                accentColor: preferences.accent_color || '#3b82f6',
            }));
            setDashboard(prev => ({
                ...prev,
                sidebarCollapsed: preferences.sidebar_collapsed || false,
            }));
            // Load other settings from preferences
        }
    }, [preferences]);

    // Track changes
    const handleChange = useCallback(() => {
        setHasChanges(true);
    }, []);

    // Save all settings
    const saveSettings = async () => {
        setIsSaving(true);
        try {
            await updatePreferences({
                theme: appearance.theme,
                accent_color: appearance.accentColor,
                sidebar_collapsed: dashboard.sidebarCollapsed,
                enable_sounds: appearance.animationsEnabled,
                enable_desktop_notifications: notifications.pushNotifications,
            });

            // Save to localStorage for quick access
            localStorage.setItem('crm_appearance', JSON.stringify(appearance));
            localStorage.setItem('crm_notifications', JSON.stringify(notifications));
            localStorage.setItem('crm_dashboard', JSON.stringify(dashboard));
            localStorage.setItem('crm_privacy', JSON.stringify(privacy));

            setHasChanges(false);
            toast.success('Settings saved successfully');
        } catch (error) {
            console.warn("Failed to save settings",error);
            toast.error('Failed to save settings');
        } finally {
            setIsSaving(false);
        }
    };

    // Reset to defaults
    const resetToDefaults = () => {
        setAppearance({
            theme: 'system',
            accentColor: '#3b82f6',
            fontSize: 14,
            compactMode: false,
            animationsEnabled: true,
            highContrast: false,
        });
        setNotifications({
            emailNotifications: true,
            pushNotifications: true,
            dealUpdates: true,
            taskReminders: true,
            mentions: true,
            weeklyDigest: true,
            quietHoursEnabled: false,
            quietHoursStart: '22:00',
            quietHoursEnd: '08:00',
        });
        setDashboard({
            defaultView: 'overview',
            sidebarCollapsed: false,
            showWelcomeMessage: true,
            autoRefreshEnabled: true,
            autoRefreshInterval: 30,
        });
        setPrivacy({
            shareActivityWithTeam: true,
            showOnlineStatus: true,
            allowMentions: true,
            dataExportEnabled: true,
        });
        setHasChanges(true);
        toast.info('Settings reset to defaults');
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
            </div>
        );
    }

    return (
        <div className="container mx-auto py-8 px-4 max-w-4xl">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-3xl font-bold flex items-center gap-3">
                        <Settings className="w-8 h-8 text-gray-500" />
                        Settings
                    </h1>
                    <p className="text-gray-500 mt-1">Manage your preferences and account settings</p>
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

            <Tabs defaultValue="appearance" className="space-y-6">
                <TabsList className="grid w-full grid-cols-5">
                    <TabsTrigger value="appearance" className="gap-2">
                        <Palette className="w-4 h-4" />
                        Appearance
                    </TabsTrigger>
                    <TabsTrigger value="notifications" className="gap-2">
                        <Bell className="w-4 h-4" />
                        Notifications
                    </TabsTrigger>
                    <TabsTrigger value="dashboard" className="gap-2">
                        <Layout className="w-4 h-4" />
                        Dashboard
                    </TabsTrigger>
                    <TabsTrigger value="privacy" className="gap-2">
                        <Shield className="w-4 h-4" />
                        Privacy
                    </TabsTrigger>
                    <TabsTrigger value="shortcuts" className="gap-2">
                        <Keyboard className="w-4 h-4" />
                        Shortcuts
                    </TabsTrigger>
                </TabsList>

                {/* Appearance Tab */}
                <TabsContent value="appearance">
                    <Card>
                        <CardHeader>
                            <CardTitle>Appearance</CardTitle>
                            <CardDescription>Customize how MyCRM looks and feels</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            {/* Theme */}
                            <div className="space-y-3">
                                <Label className="text-base font-medium">Theme</Label>
                                <RadioGroup
                                    value={appearance.theme}
                                    onValueChange={(value) => {
                                        setAppearance(prev => ({ ...prev, theme: value as AppearanceSettings['theme'] }));
                                        handleChange();
                                    }}
                                    className="grid grid-cols-3 gap-4"
                                >
                                    <Label
                                        htmlFor="light"
                                        className={`flex flex-col items-center gap-2 p-4 rounded-lg border-2 cursor-pointer transition-colors ${appearance.theme === 'light' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                                            }`}
                                    >
                                        <RadioGroupItem value="light" id="light" className="sr-only" />
                                        <Sun className="w-8 h-8 text-yellow-500" />
                                        <span>Light</span>
                                    </Label>
                                    <Label
                                        htmlFor="dark"
                                        className={`flex flex-col items-center gap-2 p-4 rounded-lg border-2 cursor-pointer transition-colors ${appearance.theme === 'dark' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                                            }`}
                                    >
                                        <RadioGroupItem value="dark" id="dark" className="sr-only" />
                                        <Moon className="w-8 h-8 text-gray-700" />
                                        <span>Dark</span>
                                    </Label>
                                    <Label
                                        htmlFor="system"
                                        className={`flex flex-col items-center gap-2 p-4 rounded-lg border-2 cursor-pointer transition-colors ${appearance.theme === 'system' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                                            }`}
                                    >
                                        <RadioGroupItem value="system" id="system" className="sr-only" />
                                        <Monitor className="w-8 h-8 text-gray-500" />
                                        <span>System</span>
                                    </Label>
                                </RadioGroup>
                            </div>

                            <Separator />

                            {/* Accent Color */}
                            <div className="space-y-3">
                                <Label className="text-base font-medium">Accent Color</Label>
                                <div className="flex flex-wrap gap-3">
                                    {colorOptions.map((color) => (
                                        <button
                                            key={color.value}
                                            onClick={() => {
                                                setAppearance(prev => ({ ...prev, accentColor: color.value }));
                                                handleChange();
                                            }}
                                            className={`w-10 h-10 rounded-full flex items-center justify-center transition-transform hover:scale-110 ${appearance.accentColor === color.value ? 'ring-2 ring-offset-2 ring-gray-400' : ''
                                                }`}
                                            style={{ backgroundColor: color.value }}
                                            title={color.name}
                                        >
                                            {appearance.accentColor === color.value && (
                                                <Check className="w-5 h-5 text-white" />
                                            )}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <Separator />

                            {/* Font Size */}
                            <div className="space-y-3">
                                <div className="flex items-center justify-between">
                                    <Label className="text-base font-medium">Font Size</Label>
                                    <span className="text-sm text-gray-500">{appearance.fontSize}px</span>
                                </div>
                                <Slider
                                    value={[appearance.fontSize]}
                                    onValueChange={(value) => {
                                        setAppearance(prev => ({ ...prev, fontSize: value[0] }));
                                        handleChange();
                                    }}
                                    min={12}
                                    max={20}
                                    step={1}
                                />
                            </div>

                            <Separator />

                            {/* Toggle Options */}
                            <div className="space-y-4">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <Label className="text-base font-medium">Compact Mode</Label>
                                        <p className="text-sm text-gray-500">Reduce spacing and padding</p>
                                    </div>
                                    <Switch
                                        checked={appearance.compactMode}
                                        onCheckedChange={(checked) => {
                                            setAppearance(prev => ({ ...prev, compactMode: checked }));
                                            handleChange();
                                        }}
                                    />
                                </div>

                                <div className="flex items-center justify-between">
                                    <div>
                                        <Label className="text-base font-medium">Animations</Label>
                                        <p className="text-sm text-gray-500">Enable smooth transitions</p>
                                    </div>
                                    <Switch
                                        checked={appearance.animationsEnabled}
                                        onCheckedChange={(checked) => {
                                            setAppearance(prev => ({ ...prev, animationsEnabled: checked }));
                                            handleChange();
                                        }}
                                    />
                                </div>

                                <div className="flex items-center justify-between">
                                    <div>
                                        <Label className="text-base font-medium">High Contrast</Label>
                                        <p className="text-sm text-gray-500">Increase visual contrast</p>
                                    </div>
                                    <Switch
                                        checked={appearance.highContrast}
                                        onCheckedChange={(checked) => {
                                            setAppearance(prev => ({ ...prev, highContrast: checked }));
                                            handleChange();
                                        }}
                                    />
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Notifications Tab */}
                <TabsContent value="notifications">
                    <Card>
                        <CardHeader>
                            <CardTitle>Notifications</CardTitle>
                            <CardDescription>Configure how you receive notifications</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            {/* Notification Channels */}
                            <div className="space-y-4">
                                <Label className="text-base font-medium">Channels</Label>

                                <div className="flex items-center justify-between">
                                    <div>
                                        <Label>Email Notifications</Label>
                                        <p className="text-sm text-gray-500">Receive updates via email</p>
                                    </div>
                                    <Switch
                                        checked={notifications.emailNotifications}
                                        onCheckedChange={(checked) => {
                                            setNotifications(prev => ({ ...prev, emailNotifications: checked }));
                                            handleChange();
                                        }}
                                    />
                                </div>

                                <div className="flex items-center justify-between">
                                    <div>
                                        <Label>Push Notifications</Label>
                                        <p className="text-sm text-gray-500">Browser push notifications</p>
                                    </div>
                                    <Switch
                                        checked={notifications.pushNotifications}
                                        onCheckedChange={(checked) => {
                                            setNotifications(prev => ({ ...prev, pushNotifications: checked }));
                                            handleChange();
                                        }}
                                    />
                                </div>
                            </div>

                            <Separator />

                            {/* Notification Types */}
                            <div className="space-y-4">
                                <Label className="text-base font-medium">Notification Types</Label>

                                {[
                                    { key: 'dealUpdates', label: 'Deal Updates', desc: 'When deal stages change' },
                                    { key: 'taskReminders', label: 'Task Reminders', desc: 'Before tasks are due' },
                                    { key: 'mentions', label: 'Mentions', desc: 'When someone @mentions you' },
                                    { key: 'weeklyDigest', label: 'Weekly Digest', desc: 'Weekly performance summary' },
                                ].map((item) => (
                                    <div key={item.key} className="flex items-center justify-between">
                                        <div>
                                            <Label>{item.label}</Label>
                                            <p className="text-sm text-gray-500">{item.desc}</p>
                                        </div>
                                        <Switch
                                            checked={notifications[item.key as keyof NotificationSettings] as boolean}
                                            onCheckedChange={(checked) => {
                                                setNotifications(prev => ({ ...prev, [item.key]: checked }));
                                                handleChange();
                                            }}
                                        />
                                    </div>
                                ))}
                            </div>

                            <Separator />

                            {/* Quiet Hours */}
                            <div className="space-y-4">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <Label className="text-base font-medium">Quiet Hours</Label>
                                        <p className="text-sm text-gray-500">Pause notifications during specific hours</p>
                                    </div>
                                    <Switch
                                        checked={notifications.quietHoursEnabled}
                                        onCheckedChange={(checked) => {
                                            setNotifications(prev => ({ ...prev, quietHoursEnabled: checked }));
                                            handleChange();
                                        }}
                                    />
                                </div>

                                {notifications.quietHoursEnabled && (
                                    <div className="flex items-center gap-4 ml-4">
                                        <div>
                                            <Label className="text-sm">Start</Label>
                                            <Input
                                                type="time"
                                                value={notifications.quietHoursStart}
                                                onChange={(e) => {
                                                    setNotifications(prev => ({ ...prev, quietHoursStart: e.target.value }));
                                                    handleChange();
                                                }}
                                                className="w-32"
                                            />
                                        </div>
                                        <div>
                                            <Label className="text-sm">End</Label>
                                            <Input
                                                type="time"
                                                value={notifications.quietHoursEnd}
                                                onChange={(e) => {
                                                    setNotifications(prev => ({ ...prev, quietHoursEnd: e.target.value }));
                                                    handleChange();
                                                }}
                                                className="w-32"
                                            />
                                        </div>
                                    </div>
                                )}
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Dashboard Tab */}
                <TabsContent value="dashboard">
                    <Card>
                        <CardHeader>
                            <CardTitle>Dashboard</CardTitle>
                            <CardDescription>Customize your dashboard experience</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            {/* Default View */}
                            <div className="space-y-3">
                                <Label className="text-base font-medium">Default View</Label>
                                <RadioGroup
                                    value={dashboard.defaultView}
                                    onValueChange={(value) => {
                                        setDashboard(prev => ({ ...prev, defaultView: value as DashboardSettings['defaultView'] }));
                                        handleChange();
                                    }}
                                    className="grid grid-cols-2 gap-4"
                                >
                                    {[
                                        { value: 'overview', label: 'Overview', desc: 'Summary dashboard' },
                                        { value: 'pipeline', label: 'Pipeline', desc: 'Deal pipeline view' },
                                        { value: 'activity', label: 'Activity', desc: 'Recent activity feed' },
                                        { value: 'analytics', label: 'Analytics', desc: 'Charts and metrics' },
                                    ].map((view) => (
                                        <Label
                                            key={view.value}
                                            htmlFor={view.value}
                                            className={`flex flex-col p-4 rounded-lg border-2 cursor-pointer transition-colors ${dashboard.defaultView === view.value ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                                                }`}
                                        >
                                            <RadioGroupItem value={view.value} id={view.value} className="sr-only" />
                                            <span className="font-medium">{view.label}</span>
                                            <span className="text-sm text-gray-500">{view.desc}</span>
                                        </Label>
                                    ))}
                                </RadioGroup>
                            </div>

                            <Separator />

                            {/* Toggle Options */}
                            <div className="space-y-4">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <Label>Collapsed Sidebar</Label>
                                        <p className="text-sm text-gray-500">Start with sidebar collapsed</p>
                                    </div>
                                    <Switch
                                        checked={dashboard.sidebarCollapsed}
                                        onCheckedChange={(checked) => {
                                            setDashboard(prev => ({ ...prev, sidebarCollapsed: checked }));
                                            handleChange();
                                        }}
                                    />
                                </div>

                                <div className="flex items-center justify-between">
                                    <div>
                                        <Label>Welcome Message</Label>
                                        <p className="text-sm text-gray-500">Show personalized greeting</p>
                                    </div>
                                    <Switch
                                        checked={dashboard.showWelcomeMessage}
                                        onCheckedChange={(checked) => {
                                            setDashboard(prev => ({ ...prev, showWelcomeMessage: checked }));
                                            handleChange();
                                        }}
                                    />
                                </div>

                                <div className="flex items-center justify-between">
                                    <div>
                                        <Label>Auto Refresh</Label>
                                        <p className="text-sm text-gray-500">Automatically refresh data</p>
                                    </div>
                                    <Switch
                                        checked={dashboard.autoRefreshEnabled}
                                        onCheckedChange={(checked) => {
                                            setDashboard(prev => ({ ...prev, autoRefreshEnabled: checked }));
                                            handleChange();
                                        }}
                                    />
                                </div>

                                {dashboard.autoRefreshEnabled && (
                                    <div className="ml-4 space-y-2">
                                        <div className="flex items-center justify-between">
                                            <Label className="text-sm">Refresh Interval</Label>
                                            <span className="text-sm text-gray-500">{dashboard.autoRefreshInterval}s</span>
                                        </div>
                                        <Slider
                                            value={[dashboard.autoRefreshInterval]}
                                            onValueChange={(value) => {
                                                setDashboard(prev => ({ ...prev, autoRefreshInterval: value[0] }));
                                                handleChange();
                                            }}
                                            min={10}
                                            max={120}
                                            step={10}
                                        />
                                    </div>
                                )}
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Privacy Tab */}
                <TabsContent value="privacy">
                    <Card>
                        <CardHeader>
                            <CardTitle>Privacy & Data</CardTitle>
                            <CardDescription>Manage your privacy settings and data</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            {/* Privacy Toggles */}
                            <div className="space-y-4">
                                {[
                                    { key: 'shareActivityWithTeam', label: 'Share Activity', desc: 'Team can see your activity' },
                                    { key: 'showOnlineStatus', label: 'Online Status', desc: 'Show when you\'re online' },
                                    { key: 'allowMentions', label: 'Allow Mentions', desc: 'Let others @mention you' },
                                    { key: 'dataExportEnabled', label: 'Data Export', desc: 'Allow exporting your data' },
                                ].map((item) => (
                                    <div key={item.key} className="flex items-center justify-between">
                                        <div>
                                            <Label>{item.label}</Label>
                                            <p className="text-sm text-gray-500">{item.desc}</p>
                                        </div>
                                        <Switch
                                            checked={privacy[item.key as keyof PrivacySettings]}
                                            onCheckedChange={(checked) => {
                                                setPrivacy(prev => ({ ...prev, [item.key]: checked }));
                                                handleChange();
                                            }}
                                        />
                                    </div>
                                ))}
                            </div>

                            <Separator />

                            {/* Data Export */}
                            <div className="space-y-4">
                                <Label className="text-base font-medium">Export Your Data</Label>
                                <p className="text-sm text-gray-500">
                                    Download a copy of all your data including contacts, deals, tasks, and activities.
                                </p>
                                <Button variant="outline" className="gap-2">
                                    <Download className="w-4 h-4" />
                                    Export Data as CSV
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Shortcuts Tab */}
                <TabsContent value="shortcuts">
                    <Card>
                        <CardHeader>
                            <CardTitle>Keyboard Shortcuts</CardTitle>
                            <CardDescription>Customize your keyboard shortcuts</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                {Object.entries(shortcuts).map(([key, value]) => (
                                    <div key={key} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                                        <Label className="capitalize">{key.replace(/([A-Z])/g, ' $1').trim()}</Label>
                                        <div className="flex items-center gap-2">
                                            <Input
                                                value={value}
                                                onChange={(e) => {
                                                    setShortcuts(prev => ({ ...prev, [key]: e.target.value }));
                                                    handleChange();
                                                }}
                                                className="w-32 text-center font-mono"
                                            />
                                            <Badge variant="outline" className="font-mono">
                                                {value}
                                            </Badge>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                        <CardFooter>
                            <p className="text-sm text-gray-500">
                                Press the desired key combination to set a new shortcut.
                            </p>
                        </CardFooter>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
}

