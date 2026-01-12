'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/contexts/AuthContext';
import { ThemeToggle } from '@/components/ThemeToggle';
import {
  BarChart3,
  Users,
  UserPlus,
  TrendingUp,
  Calendar,
  Mail,
  Settings,
  Search,
  LogOut,
  Menu,
  X,
  FileText,
  Workflow,
  Shield,
  Upload,
  Zap,
  FileCode,
  Target,
  PieChart,
  Activity,
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
  MessageSquare,
  Store,
  Leaf,
  Users2,
  Globe,
  ShieldCheck,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import NotificationsDropdown from '@/components/NotificationsDropdown';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: BarChart3 },
  { name: 'Contacts', href: '/contacts', icon: Users },
  { name: 'Leads', href: '/leads', icon: UserPlus },
  { name: 'Opportunities', href: '/opportunities', icon: TrendingUp },
  { name: 'Tasks', href: '/tasks', icon: Calendar },
  { name: 'Communications', href: '/communications', icon: Mail },
];

const analyticsNavigation = [
  { name: 'Pipeline Analytics', href: '/analytics/pipeline', icon: PieChart },
  { name: 'Revenue Intelligence', href: '/revenue-intelligence', icon: DollarSign },
  { name: 'Lead Scoring', href: '/lead-qualification', icon: Target },
  { name: 'Advanced Reports', href: '/advanced-reporting', icon: LayoutDashboard },
  { name: 'Reports', href: '/reports', icon: FileText },
];

const advancedNavigation = [
  { name: 'Integration Hub', href: '/integration-hub', icon: Puzzle },
  { name: 'AI Insights', href: '/ai-insights', icon: Sparkles },
  { name: 'AI Sales Assistant', href: '/ai-assistant', icon: Brain },
  { name: 'AI Chatbot', href: '/ai-chatbot', icon: MessageSquare },
  { name: 'Gamification', href: '/gamification', icon: Trophy },
  { name: 'App Marketplace', href: '/marketplace', icon: Store },
];

const aiWorkflowNavigation = [
  { name: 'Email Sequences', href: '/email-sequences', icon: MailCheck },
  { name: 'Lead Routing', href: '/lead-routing', icon: Route },
  { name: 'Smart Scheduling AI', href: '/scheduling/ai', icon: CalendarClock },
  { name: 'Data Enrichment', href: '/data-enrichment', icon: Database },
  { name: 'Voice Intelligence', href: '/voice-intelligence', icon: Mic },
];

const premiumNavigation = [
  { name: 'Email Tracking', href: '/email-tracking', icon: Eye },
  { name: 'Smart Scheduling', href: '/scheduling', icon: Clock },
  { name: 'Customer Success', href: '/customer-success', icon: Heart },
  { name: 'Call Intelligence', href: '/conversation-intelligence', icon: Mic },
  { name: 'E-Signatures', href: '/document-esign', icon: FileSignature },
  { name: 'Social Selling', href: '/social-selling', icon: Share2 },
  { name: 'Social Inbox', href: '/social-inbox', icon: Globe },
  { name: 'Realtime Collab', href: '/realtime-collaboration', icon: Users2 },
  { name: 'Customer Portal', href: '/customer-portal', icon: Users },
];

const toolsNavigation = [
  { name: 'Email Campaigns', href: '/campaigns', icon: Zap },
  { name: 'Documents', href: '/documents', icon: FileCode },
  { name: 'Integrations', href: '/integrations', icon: Activity },
  { name: 'Workflows', href: '/workflows', icon: Workflow },
  { name: 'Import/Export', href: '/data', icon: Upload },
  { name: 'ESG Reporting', href: '/esg-reporting', icon: Leaf },
  { name: 'Security', href: '/security', icon: Shield },
  { name: 'Enterprise Security', href: '/enterprise-security', icon: ShieldCheck },
  { name: 'Settings', href: '/settings', icon: Settings },
]; export default function MainLayout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth();
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-theme transition-theme">
      {/* Header with glass morphism */}
      <header className="glass sticky top-0 z-40 px-4 lg:px-6 py-3.5 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="hidden lg:flex hover:bg-primary/10 transition-colors"
            >
              <Menu className="w-5 h-5" />
            </Button>

            <Button
              variant="ghost"
              size="sm"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden hover:bg-primary/10 transition-colors"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </Button>

            <Link href="/dashboard" className="flex items-center space-x-2 group">
              <div className="w-9 h-9 bg-linear-to-br from-blue-600 via-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-all duration-300 group-hover:scale-105">
                <Sparkles className="text-white w-5 h-5" />
              </div>
              <div className="hidden sm:block">
                <h1 className="text-xl font-bold gradient-text">MyCRM</h1>
                <p className="text-[10px] text-muted-foreground -mt-1">Modern CRM Solution</p>
              </div>
            </Link>
          </div>

          <div className="flex items-center space-x-2 lg:space-x-3">
            <button
              onClick={() => {
                const event = new KeyboardEvent('keydown', {
                  key: 'k',
                  metaKey: true,
                  ctrlKey: true,
                  bubbles: true,
                });
                document.dispatchEvent(event);
              }}
              className="hidden md:flex items-center gap-2 pl-3 pr-2 py-2 w-64 bg-secondary/50 dark:bg-secondary/30 border border-border/50 rounded-xl hover:bg-secondary/80 text-sm transition-all text-muted-foreground"
            >
              <Search className="w-4 h-4" />
              <span className="flex-1 text-left">Search anything...</span>
              <kbd className="pointer-events-none hidden h-5 select-none items-center gap-1 rounded border border-border bg-muted px-1.5 font-mono text-[10px] font-medium opacity-100 sm:flex">
                <span className="text-xs">⌘</span>K
              </kbd>
            </button>

            <ThemeToggle />

            <NotificationsDropdown />

            <div className="flex items-center space-x-2 pl-2 border-l border-border/50">
              <div className="w-9 h-9 bg-linear-to-br from-blue-500 via-purple-500 to-pink-500 rounded-full flex items-center justify-center shadow-md hover:shadow-lg transition-all duration-300 hover:scale-105 cursor-pointer">
                <span className="text-sm font-bold text-white">
                  {user?.first_name?.[0] || user?.username?.[0] || 'U'}
                </span>
              </div>
              <span className="text-sm font-medium text-foreground hidden sm:block">
                {user?.first_name && user?.last_name
                  ? `${user.first_name} ${user.last_name}`
                  : user?.username || 'User'
                }
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={logout}
                title="Logout"
                className="hover:bg-destructive/10 hover:text-destructive transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Desktop Sidebar with modern styling */}
        <aside
          className={cn(
            "hidden lg:block glass transition-all duration-300 sticky top-16 h-[calc(100vh-4rem)] overflow-y-auto border-r border-border/50",
            sidebarOpen ? "w-64" : "w-20"
          )}
        >
          <nav className="p-4 space-y-6">
            <div className="space-y-1">
              <h3 className={cn(
                "text-xs font-bold text-muted-foreground uppercase tracking-wider mb-3 px-2",
                !sidebarOpen && "text-center px-0"
              )}>
                {sidebarOpen ? '✦ Main' : '✦'}
              </h3>

              {navigation.map((item) => {
                const isActive = pathname === item.href || pathname?.startsWith(item.href + '/');
                return (
                  <Link key={item.name} href={item.href}>
                    <Button
                      variant="ghost"
                      className={cn(
                        "w-full justify-start transition-all duration-200 rounded-xl",
                        isActive
                          ? "bg-linear-to-r from-blue-500/10 to-purple-500/10 text-primary border border-primary/20 shadow-sm dark:from-blue-500/20 dark:to-purple-500/20"
                          : "text-foreground/80 hover:bg-accent hover:text-accent-foreground",
                        !sidebarOpen && "justify-center px-2"
                      )}
                      title={!sidebarOpen ? item.name : undefined}
                    >
                      <item.icon className={cn("w-4 h-4", sidebarOpen && "mr-3", isActive && "animate-pulse")} />
                      {sidebarOpen && <span className="font-medium">{item.name}</span>}
                    </Button>
                  </Link>
                );
              })}
            </div>

            <div className="space-y-1">
              <h3 className={cn(
                "text-xs font-bold text-muted-foreground uppercase tracking-wider mb-3 px-2",
                !sidebarOpen && "text-center px-0"
              )}>
                {sidebarOpen ? '📊 Analytics' : '📊'}
              </h3>

              {analyticsNavigation.map((item) => {
                const isActive = pathname === item.href || pathname?.startsWith(item.href + '/');
                return (
                  <Link key={item.name} href={item.href}>
                    <Button
                      variant="ghost"
                      className={cn(
                        "w-full justify-start transition-all duration-200 rounded-xl",
                        isActive
                          ? "bg-linear-to-r from-blue-500/10 to-purple-500/10 text-primary border border-primary/20 shadow-sm dark:from-blue-500/20 dark:to-purple-500/20"
                          : "text-foreground/80 hover:bg-accent hover:text-accent-foreground",
                        !sidebarOpen && "justify-center px-2"
                      )}
                      title={!sidebarOpen ? item.name : undefined}
                    >
                      <item.icon className={cn("w-4 h-4", sidebarOpen && "mr-3", isActive && "animate-pulse")} />
                      {sidebarOpen && <span className="font-medium">{item.name}</span>}
                    </Button>
                  </Link>
                );
              })}
            </div>

            <div className="space-y-1">
              <h3 className={cn(
                "text-xs font-bold text-muted-foreground uppercase tracking-wider mb-3 px-2",
                !sidebarOpen && "text-center px-0"
              )}>
                {sidebarOpen ? '✨ Advanced' : '✨'}
              </h3>

              {advancedNavigation.map((item) => {
                const isActive = pathname === item.href || pathname?.startsWith(item.href + '/');
                return (
                  <Link key={item.name} href={item.href}>
                    <Button
                      variant="ghost"
                      className={cn(
                        "w-full justify-start transition-all duration-200 rounded-xl",
                        isActive
                          ? "bg-linear-to-r from-blue-500/10 to-purple-500/10 text-primary border border-primary/20 shadow-sm dark:from-blue-500/20 dark:to-purple-500/20"
                          : "text-foreground/80 hover:bg-accent hover:text-accent-foreground",
                        !sidebarOpen && "justify-center px-2"
                      )}
                      title={!sidebarOpen ? item.name : undefined}
                    >
                      <item.icon className={cn("w-4 h-4", sidebarOpen && "mr-3", isActive && "animate-pulse")} />
                      {sidebarOpen && <span className="font-medium">{item.name}</span>}
                    </Button>
                  </Link>
                );
              })}
            </div>

            <div className="space-y-1">
              <h3 className={cn(
                "text-xs font-bold text-muted-foreground uppercase tracking-wider mb-3 px-2",
                !sidebarOpen && "text-center px-0"
              )}>
                {sidebarOpen ? '🤖 AI Workflows' : '🤖'}
              </h3>

              {aiWorkflowNavigation.map((item) => {
                const isActive = pathname === item.href || pathname?.startsWith(item.href + '/');
                return (
                  <Link key={item.name} href={item.href}>
                    <Button
                      variant="ghost"
                      className={cn(
                        "w-full justify-start transition-all duration-200 rounded-xl",
                        isActive
                          ? "bg-linear-to-r from-blue-500/10 to-purple-500/10 text-primary border border-primary/20 shadow-sm dark:from-blue-500/20 dark:to-purple-500/20"
                          : "text-foreground/80 hover:bg-accent hover:text-accent-foreground",
                        !sidebarOpen && "justify-center px-2"
                      )}
                      title={!sidebarOpen ? item.name : undefined}
                    >
                      <item.icon className={cn("w-4 h-4", sidebarOpen && "mr-3", isActive && "animate-pulse")} />
                      {sidebarOpen && <span className="font-medium">{item.name}</span>}
                    </Button>
                  </Link>
                );
              })}
            </div>

            <div className="space-y-1">
              <h3 className={cn(
                "text-xs font-bold text-muted-foreground uppercase tracking-wider mb-3 px-2",
                !sidebarOpen && "text-center px-0"
              )}>
                {sidebarOpen ? '💎 Premium' : '💎'}
              </h3>

              {premiumNavigation.map((item) => {
                const isActive = pathname === item.href || pathname?.startsWith(item.href + '/');
                return (
                  <Link key={item.name} href={item.href}>
                    <Button
                      variant="ghost"
                      className={cn(
                        "w-full justify-start transition-all duration-200 rounded-xl",
                        isActive
                          ? "bg-linear-to-r from-blue-500/10 to-purple-500/10 text-primary border border-primary/20 shadow-sm dark:from-blue-500/20 dark:to-purple-500/20"
                          : "text-foreground/80 hover:bg-accent hover:text-accent-foreground",
                        !sidebarOpen && "justify-center px-2"
                      )}
                      title={!sidebarOpen ? item.name : undefined}
                    >
                      <item.icon className={cn("w-4 h-4", sidebarOpen && "mr-3", isActive && "animate-pulse")} />
                      {sidebarOpen && <span className="font-medium">{item.name}</span>}
                    </Button>
                  </Link>
                );
              })}
            </div>

            <div className="space-y-1">
              <h3 className={cn(
                "text-xs font-bold text-muted-foreground uppercase tracking-wider mb-3 px-2",
                !sidebarOpen && "text-center px-0"
              )}>
                {sidebarOpen ? '⚙️ Tools' : '⚙️'}
              </h3>

              {toolsNavigation.map((item) => {
                const isActive = pathname === item.href || pathname?.startsWith(item.href + '/');
                return (
                  <Link key={item.name} href={item.href}>
                    <Button
                      variant="ghost"
                      className={cn(
                        "w-full justify-start transition-all duration-200 rounded-xl",
                        isActive
                          ? "bg-linear-to-r from-blue-500/10 to-purple-500/10 text-primary border border-primary/20 shadow-sm dark:from-blue-500/20 dark:to-purple-500/20"
                          : "text-foreground/80 hover:bg-accent hover:text-accent-foreground",
                        !sidebarOpen && "justify-center px-2"
                      )}
                      title={!sidebarOpen ? item.name : undefined}
                    >
                      <item.icon className={cn("w-4 h-4", sidebarOpen && "mr-3", isActive && "animate-pulse")} />
                      {sidebarOpen && <span className="font-medium">{item.name}</span>}
                    </Button>
                  </Link>
                );
              })}
            </div>
          </nav>
        </aside>

        {/* Mobile Sidebar with modern styling */}
        {mobileMenuOpen && (
          <div className="lg:hidden fixed inset-0 z-50 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200" onClick={() => setMobileMenuOpen(false)}>
            <aside
              className="absolute left-0 top-0 bottom-0 w-72 glass shadow-2xl animate-in slide-in-from-left duration-300"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-4 border-b border-border/50 flex items-center justify-between">
                <h2 className="font-bold text-lg gradient-text">Navigation</h2>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setMobileMenuOpen(false)}
                  className="hover:bg-destructive/10 hover:text-destructive"
                >
                  <X className="w-5 h-5" />
                </Button>
              </div>

              <nav className="p-4 space-y-6 overflow-y-auto h-[calc(100vh-5rem)]">
                <div className="space-y-1">
                  <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-3 px-2">
                    ✦ Main
                  </h3>

                  {navigation.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                      <Link key={item.name} href={item.href} onClick={() => setMobileMenuOpen(false)}>
                        <Button
                          variant="ghost"
                          className={cn(
                            "w-full justify-start transition-all duration-200 rounded-xl",
                            isActive
                              ? "bg-linear-to-r from-blue-500/10 to-purple-500/10 text-primary border border-primary/20 shadow-sm"
                              : "text-foreground/80 hover:bg-accent hover:text-accent-foreground"
                          )}
                        >
                          <item.icon className="w-4 h-4 mr-3" />
                          <span className="font-medium">{item.name}</span>
                        </Button>
                      </Link>
                    );
                  })}
                </div>

                <div className="space-y-1">
                  <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-3 px-2">
                    📊 Analytics
                  </h3>

                  {analyticsNavigation.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                      <Link key={item.name} href={item.href} onClick={() => setMobileMenuOpen(false)}>
                        <Button
                          variant="ghost"
                          className={cn(
                            "w-full justify-start transition-all duration-200 rounded-xl",
                            isActive
                              ? "bg-linear-to-r from-blue-500/10 to-purple-500/10 text-primary border border-primary/20 shadow-sm"
                              : "text-foreground/80 hover:bg-accent hover:text-accent-foreground"
                          )}
                        >
                          <item.icon className="w-4 h-4 mr-3" />
                          <span className="font-medium">{item.name}</span>
                        </Button>
                      </Link>
                    );
                  })}
                </div>

                <div className="space-y-1">
                  <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-3 px-2">
                    ✨ Advanced
                  </h3>

                  {advancedNavigation.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                      <Link key={item.name} href={item.href} onClick={() => setMobileMenuOpen(false)}>
                        <Button
                          variant="ghost"
                          className={cn(
                            "w-full justify-start transition-all duration-200 rounded-xl",
                            isActive
                              ? "bg-linear-to-r from-blue-500/10 to-purple-500/10 text-primary border border-primary/20 shadow-sm"
                              : "text-foreground/80 hover:bg-accent hover:text-accent-foreground"
                          )}
                        >
                          <item.icon className="w-4 h-4 mr-3" />
                          <span className="font-medium">{item.name}</span>
                        </Button>
                      </Link>
                    );
                  })}
                </div>

                <div className="space-y-1">
                  <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-3 px-2">
                    🤖 AI Workflows
                  </h3>

                  {aiWorkflowNavigation.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                      <Link key={item.name} href={item.href} onClick={() => setMobileMenuOpen(false)}>
                        <Button
                          variant="ghost"
                          className={cn(
                            "w-full justify-start transition-all duration-200 rounded-xl",
                            isActive
                              ? "bg-linear-to-r from-blue-500/10 to-purple-500/10 text-primary border border-primary/20 shadow-sm"
                              : "text-foreground/80 hover:bg-accent hover:text-accent-foreground"
                          )}
                        >
                          <item.icon className="w-4 h-4 mr-3" />
                          <span className="font-medium">{item.name}</span>
                        </Button>
                      </Link>
                    );
                  })}
                </div>

                <div className="space-y-1">
                  <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-3 px-2">
                    💎 Premium
                  </h3>

                  {premiumNavigation.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                      <Link key={item.name} href={item.href} onClick={() => setMobileMenuOpen(false)}>
                        <Button
                          variant="ghost"
                          className={cn(
                            "w-full justify-start transition-all duration-200 rounded-xl",
                            isActive
                              ? "bg-linear-to-r from-blue-500/10 to-purple-500/10 text-primary border border-primary/20 shadow-sm"
                              : "text-foreground/80 hover:bg-accent hover:text-accent-foreground"
                          )}
                        >
                          <item.icon className="w-4 h-4 mr-3" />
                          <span className="font-medium">{item.name}</span>
                        </Button>
                      </Link>
                    );
                  })}
                </div>

                <div className="space-y-1">
                  <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-3 px-2">
                    ⚙️ Tools
                  </h3>

                  {toolsNavigation.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                      <Link key={item.name} href={item.href} onClick={() => setMobileMenuOpen(false)}>
                        <Button
                          variant="ghost"
                          className={cn(
                            "w-full justify-start transition-all duration-200 rounded-xl",
                            isActive
                              ? "bg-linear-to-r from-blue-500/10 to-purple-500/10 text-primary border border-primary/20 shadow-sm"
                              : "text-foreground/80 hover:bg-accent hover:text-accent-foreground"
                          )}
                        >
                          <item.icon className="w-4 h-4 mr-3" />
                          <span className="font-medium">{item.name}</span>
                        </Button>
                      </Link>
                    );
                  })}
                </div>
              </nav>
            </aside>
          </div>
        )}

        {/* Main Content with modern styling */}
        <main className="flex-1 overflow-x-hidden p-6">
          <div className="max-w-[1600px] mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
