'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import {
    CommandDialog,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
    CommandList,
    CommandSeparator,
    CommandShortcut,
} from '@/components/ui/command';
import {
    BarChart3,
    Users,
    UserPlus,
    TrendingUp,
    Calendar,
    Mail,
    Settings,
    FileText,
    Workflow,
    Shield,
    Upload,
    Zap,
    Target,
    PieChart,
    LayoutDashboard,
    Sparkles,
    Puzzle,
    Trophy,
    DollarSign,
    Eye,
    Clock,
    Brain,
    Heart,
    Mic,
    FileSignature,
    Share2,
    MailCheck,
    Route,
    Database,
    CalendarClock,
    Search,
    Plus,
    MessageSquare,
    Bell,
    HelpCircle,
    Keyboard,
    Moon,
    Sun,
    LogOut,
} from 'lucide-react';
import { useTheme } from 'next-themes';
import { Badge } from '@/components/ui/badge';

interface CommandItem {
    name: string;
    href?: string;
    icon: React.ElementType;
    shortcut?: string;
    action?: () => void;
    keywords?: string[];
    badge?: string;
}

const navigationItems: CommandItem[] = [
    { name: 'Dashboard', href: '/dashboard', icon: BarChart3, keywords: ['home', 'overview', 'stats'] },
    { name: 'Contacts', href: '/contacts', icon: Users, keywords: ['people', 'customers', 'clients'] },
    { name: 'Leads', href: '/leads', icon: UserPlus, keywords: ['prospects', 'potential', 'new'] },
    { name: 'Opportunities', href: '/opportunities', icon: TrendingUp, keywords: ['deals', 'sales', 'pipeline'] },
    { name: 'Tasks', href: '/tasks', icon: Calendar, keywords: ['todo', 'activities', 'schedule'] },
    { name: 'Communications', href: '/communications', icon: Mail, keywords: ['email', 'messages', 'calls'] },
];

const analyticsItems: CommandItem[] = [
    { name: 'Pipeline Analytics', href: '/analytics/pipeline', icon: PieChart, keywords: ['funnel', 'conversion'] },
    { name: 'Revenue Intelligence', href: '/revenue-intelligence', icon: DollarSign, keywords: ['money', 'income'] },
    { name: 'Lead Scoring', href: '/lead-qualification', icon: Target, keywords: ['qualify', 'score', 'rank'] },
    { name: 'Advanced Reports', href: '/advanced-reporting', icon: LayoutDashboard, keywords: ['analytics', 'metrics'] },
    { name: 'Reports', href: '/reports', icon: FileText, keywords: ['export', 'summary'] },
];

const aiItems: CommandItem[] = [
    { name: 'AI Insights', href: '/ai-insights', icon: Sparkles, badge: 'AI', keywords: ['predictions', 'recommendations'] },
    { name: 'AI Sales Assistant', href: '/ai-assistant', icon: Brain, badge: 'AI', keywords: ['chat', 'help', 'assistant'] },
    { name: 'Email Sequences', href: '/email-sequences', icon: MailCheck, keywords: ['automation', 'drip'] },
    { name: 'Lead Routing', href: '/lead-routing', icon: Route, keywords: ['assign', 'distribute'] },
    { name: 'Smart Scheduling AI', href: '/scheduling/ai', icon: CalendarClock, badge: 'AI', keywords: ['meeting', 'calendar'] },
    { name: 'Data Enrichment', href: '/data-enrichment', icon: Database, keywords: ['enrich', 'enhance', 'complete'] },
    { name: 'Voice Intelligence', href: '/voice-intelligence', icon: Mic, badge: 'AI', keywords: ['call', 'transcribe'] },
];

const premiumItems: CommandItem[] = [
    { name: 'Email Tracking', href: '/email-tracking', icon: Eye, badge: 'Pro', keywords: ['opens', 'clicks'] },
    { name: 'Smart Scheduling', href: '/scheduling', icon: Clock, keywords: ['calendar', 'book'] },
    { name: 'Customer Success', href: '/customer-success', icon: Heart, keywords: ['retention', 'health'] },
    { name: 'Call Intelligence', href: '/conversation-intelligence', icon: Mic, badge: 'Pro', keywords: ['transcribe'] },
    { name: 'E-Signatures', href: '/document-esign', icon: FileSignature, keywords: ['sign', 'contract'] },
    { name: 'Social Selling', href: '/social-selling', icon: Share2, keywords: ['linkedin', 'twitter'] },
    { name: 'Integration Hub', href: '/integration-hub', icon: Puzzle, keywords: ['connect', 'apps', 'zapier'] },
    { name: 'Gamification', href: '/gamification', icon: Trophy, keywords: ['points', 'achievements', 'leaderboard'] },
];

const toolsItems: CommandItem[] = [
    { name: 'Email Campaigns', href: '/campaigns', icon: Zap, keywords: ['marketing', 'blast'] },
    { name: 'Workflows', href: '/workflows', icon: Workflow, keywords: ['automation', 'rules'] },
    { name: 'Import/Export', href: '/data', icon: Upload, keywords: ['csv', 'backup'] },
    { name: 'Security', href: '/security', icon: Shield, keywords: ['password', '2fa', 'auth'] },
    { name: 'Settings', href: '/settings', icon: Settings, keywords: ['preferences', 'config'] },
];

export default function CommandPalette() {
    const [open, setOpen] = useState(false);
    const router = useRouter();
    const { theme, setTheme } = useTheme();

    // Keyboard shortcut listener
    useEffect(() => {
        const down = (e: KeyboardEvent) => {
            if ((e.key === 'k' && (e.metaKey || e.ctrlKey)) || e.key === '/') {
                e.preventDefault();
                setOpen((open) => !open);
            }
        };

        document.addEventListener('keydown', down);
        return () => document.removeEventListener('keydown', down);
    }, []);

    const runCommand = useCallback((command: () => void) => {
        setOpen(false);
        command();
    }, []);

    const navigateTo = useCallback((href: string) => {
        runCommand(() => router.push(href));
    }, [router, runCommand]);

    const toggleTheme = useCallback(() => {
        runCommand(() => setTheme(theme === 'dark' ? 'light' : 'dark'));
    }, [theme, setTheme, runCommand]);

    const quickActions: CommandItem[] = [
        {
            name: 'Create New Lead',
            icon: UserPlus,
            shortcut: '⌘N',
            action: () => navigateTo('/leads?action=new'),
            keywords: ['add', 'new', 'create', 'lead']
        },
        {
            name: 'Create New Contact',
            icon: Users,
            action: () => navigateTo('/contacts?action=new'),
            keywords: ['add', 'new', 'create', 'contact']
        },
        {
            name: 'Create New Task',
            icon: Calendar,
            shortcut: '⌘T',
            action: () => navigateTo('/tasks?action=new'),
            keywords: ['add', 'new', 'create', 'task', 'todo']
        },
        {
            name: 'Create Opportunity',
            icon: TrendingUp,
            action: () => navigateTo('/opportunities?action=new'),
            keywords: ['add', 'new', 'create', 'deal', 'opportunity']
        },
        {
            name: 'Ask AI Assistant',
            icon: Brain,
            badge: 'AI',
            shortcut: '⌘I',
            action: () => navigateTo('/ai-assistant'),
            keywords: ['help', 'chat', 'assistant', 'ai']
        },
        {
            name: theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode',
            icon: theme === 'dark' ? Sun : Moon,
            shortcut: '⌘D',
            action: toggleTheme,
            keywords: ['theme', 'dark', 'light', 'mode']
        },
        {
            name: 'View Keyboard Shortcuts',
            icon: Keyboard,
            shortcut: '?',
            action: () => setOpen(false),
            keywords: ['help', 'shortcuts', 'keys']
        },
    ];

    const renderCommandItem = (item: CommandItem, index: number) => (
        <CommandItem
            key={`${item.name}-${index}`}
            onSelect={() => item.action ? item.action() : item.href && navigateTo(item.href)}
            className="flex items-center gap-3 cursor-pointer"
        >
            <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-background shadow-sm">
                <item.icon className="h-4 w-4" />
            </div>
            <div className="flex flex-col gap-0.5">
                <span className="font-medium">{item.name}</span>
            </div>
            <div className="ml-auto flex items-center gap-2">
                {item.badge && (
                    <Badge variant="secondary" className="text-xs">
                        {item.badge}
                    </Badge>
                )}
                {item.shortcut && (
                    <CommandShortcut>{item.shortcut}</CommandShortcut>
                )}
            </div>
        </CommandItem>
    );

    return (
        <>
            {/* Search Trigger Button - can be placed in header */}
            <button
                onClick={() => setOpen(true)}
                className="hidden md:flex items-center gap-2 px-3 py-2 text-sm text-muted-foreground hover:text-foreground transition-colors rounded-xl border border-border/50 bg-secondary/30 hover:bg-secondary/50"
            >
                <Search className="h-4 w-4" />
                <span>Search...</span>
                <kbd className="pointer-events-none hidden h-5 select-none items-center gap-1 rounded border border-border bg-muted px-1.5 font-mono text-[10px] font-medium opacity-100 sm:flex">
                    <span className="text-xs">⌘</span>K
                </kbd>
            </button>

            <CommandDialog open={open} onOpenChange={setOpen}>
                <CommandInput placeholder="Type a command or search..." />
                <CommandList className="max-h-[400px]">
                    <CommandEmpty>
                        <div className="flex flex-col items-center justify-center py-6 text-center">
                            <Search className="h-10 w-10 text-muted-foreground/50 mb-2" />
                            <p className="text-sm text-muted-foreground">No results found.</p>
                            <p className="text-xs text-muted-foreground/70">Try searching for pages, actions, or settings</p>
                        </div>
                    </CommandEmpty>

                    {/* Quick Actions */}
                    <CommandGroup heading="Quick Actions">
                        {quickActions.map((item, index) => renderCommandItem(item, index))}
                    </CommandGroup>

                    <CommandSeparator />

                    {/* Navigation */}
                    <CommandGroup heading="Navigation">
                        {navigationItems.map((item, index) => renderCommandItem(item, index))}
                    </CommandGroup>

                    <CommandSeparator />

                    {/* AI & Automation */}
                    <CommandGroup heading="AI & Automation">
                        {aiItems.map((item, index) => renderCommandItem(item, index))}
                    </CommandGroup>

                    <CommandSeparator />

                    {/* Analytics */}
                    <CommandGroup heading="Analytics">
                        {analyticsItems.map((item, index) => renderCommandItem(item, index))}
                    </CommandGroup>

                    <CommandSeparator />

                    {/* Premium Features */}
                    <CommandGroup heading="Premium Features">
                        {premiumItems.map((item, index) => renderCommandItem(item, index))}
                    </CommandGroup>

                    <CommandSeparator />

                    {/* Tools & Settings */}
                    <CommandGroup heading="Tools & Settings">
                        {toolsItems.map((item, index) => renderCommandItem(item, index))}
                    </CommandGroup>
                </CommandList>

                {/* Footer with tips */}
                <div className="flex items-center justify-between border-t border-border px-3 py-2 text-xs text-muted-foreground">
                    <div className="flex items-center gap-2">
                        <kbd className="rounded border px-1">↑↓</kbd>
                        <span>Navigate</span>
                        <kbd className="rounded border px-1">↵</kbd>
                        <span>Select</span>
                        <kbd className="rounded border px-1">esc</kbd>
                        <span>Close</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <Sparkles className="h-3 w-3 text-purple-500" />
                        <span>Powered by AI</span>
                    </div>
                </div>
            </CommandDialog>
        </>
    );
}
