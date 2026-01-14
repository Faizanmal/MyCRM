'use client';

import { useState, useEffect } from 'react';
import { 
  Store, 
  Search, 
  Download, 
  Star, 
  Grid, 
  List,
  Filter,
  Settings,
  ExternalLink,
  Check,
  Trash2,
  Code,
  Puzzle,
  Zap,
  BarChart3,
  Mail,
  MessageSquare,
  Calendar,
  Users,
  Shield,
  Globe
} from 'lucide-react';

import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
// import { ScrollArea } from '@/components/ui/scroll-area';
// import { Separator } from '@/components/ui/separator';
// import { Progress } from '@/components/ui/progress';
import { appMarketplaceAPI } from '@/lib/api';

interface App {
  id: string;
  name: string;
  description: string;
  short_description: string;
  icon: string;
  category: string;
  developer: string;
  rating: number;
  reviews_count: number;
  installs: number;
  price: number;
  is_free: boolean;
  is_installed: boolean;
  version: string;
  last_updated: string;
  features: string[];
  screenshots: string[];
}

interface Category {
  id: string;
  name: string;
  slug: string;
  app_count: number;
  icon: string;
}

interface InstalledApp extends App {
  installed_at: string;
  settings: Record<string, unknown>;
}

const categoryIcons: Record<string, React.ReactNode> = {
  'analytics': <BarChart3 className="h-4 w-4" />,
  'communication': <MessageSquare className="h-4 w-4" />,
  'email': <Mail className="h-4 w-4" />,
  'calendar': <Calendar className="h-4 w-4" />,
  'team': <Users className="h-4 w-4" />,
  'security': <Shield className="h-4 w-4" />,
  'integration': <Puzzle className="h-4 w-4" />,
  'automation': <Zap className="h-4 w-4" />,
  'developer': <Code className="h-4 w-4" />,
  'other': <Globe className="h-4 w-4" />,
};

export default function MarketplacePage() {
  const [apps, setApps] = useState<App[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [myApps, setMyApps] = useState<InstalledApp[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [isLoading, setIsLoading] = useState(true);
  const [_selectedApp, setSelectedApp] = useState<App | null>(null);
  const [activeTab, setActiveTab] = useState('browse');

  useEffect(() => {
    loadMarketplace();
  }, []);

  const loadMarketplace = async () => {
    setIsLoading(true);
    try {
      const [appsData, categoriesData, myAppsData] = await Promise.all([
        appMarketplaceAPI.getApps(),
        appMarketplaceAPI.getCategories(),
        appMarketplaceAPI.getMyApps(),
      ]);
      setApps(appsData.results || appsData || []);
      setCategories(categoriesData.results || categoriesData || []);
      setMyApps(myAppsData.results || myAppsData || []);
    } catch (error) {
      console.error('Failed to load marketplace:', error);
      // Demo data
      setCategories([
        { id: '1', name: 'Analytics', slug: 'analytics', app_count: 12, icon: 'chart' },
        { id: '2', name: 'Communication', slug: 'communication', app_count: 8, icon: 'message' },
        { id: '3', name: 'Email', slug: 'email', app_count: 15, icon: 'mail' },
        { id: '4', name: 'Calendar', slug: 'calendar', app_count: 6, icon: 'calendar' },
        { id: '5', name: 'Team', slug: 'team', app_count: 10, icon: 'users' },
        { id: '6', name: 'Security', slug: 'security', app_count: 5, icon: 'shield' },
        { id: '7', name: 'Automation', slug: 'automation', app_count: 18, icon: 'zap' },
        { id: '8', name: 'Developer', slug: 'developer', app_count: 7, icon: 'code' },
      ]);
      setApps([
        { id: '1', name: 'Slack Integration', description: 'Connect Slack to receive real-time CRM notifications and updates directly in your channels.', short_description: 'Real-time CRM notifications in Slack', icon: '💬', category: 'communication', developer: 'Slack Technologies', rating: 4.8, reviews_count: 1250, installs: 50000, price: 0, is_free: true, is_installed: false, version: '2.1.0', last_updated: '2026-01-10', features: ['Real-time notifications', 'Channel integration', 'Slash commands'], screenshots: [] },
        { id: '2', name: 'Google Calendar Sync', description: 'Sync your meetings and appointments with Google Calendar for seamless scheduling.', short_description: 'Two-way calendar synchronization', icon: '📅', category: 'calendar', developer: 'Google', rating: 4.9, reviews_count: 2100, installs: 85000, price: 0, is_free: true, is_installed: true, version: '3.0.1', last_updated: '2026-01-08', features: ['Two-way sync', 'Meeting reminders', 'Conflict detection'], screenshots: [] },
        { id: '3', name: 'Advanced Analytics Pro', description: 'Get deep insights into your sales performance with advanced charts and predictive analytics.', short_description: 'Advanced sales analytics and forecasting', icon: '📊', category: 'analytics', developer: 'DataViz Inc', rating: 4.7, reviews_count: 890, installs: 25000, price: 29.99, is_free: false, is_installed: false, version: '1.5.0', last_updated: '2026-01-05', features: ['Predictive analytics', 'Custom dashboards', 'Export reports'], screenshots: [] },
        { id: '4', name: 'Mailchimp Connector', description: 'Sync your contacts with Mailchimp and automate your email marketing campaigns.', short_description: 'Email marketing automation', icon: '📧', category: 'email', developer: 'Mailchimp', rating: 4.6, reviews_count: 1500, installs: 45000, price: 0, is_free: true, is_installed: false, version: '2.3.0', last_updated: '2026-01-12', features: ['Contact sync', 'Campaign tracking', 'Audience segmentation'], screenshots: [] },
        { id: '5', name: 'Zapier Automation', description: 'Connect your CRM to 5000+ apps and automate workflows without coding.', short_description: 'Connect to 5000+ apps', icon: '⚡', category: 'automation', developer: 'Zapier', rating: 4.9, reviews_count: 3200, installs: 120000, price: 0, is_free: true, is_installed: true, version: '4.0.0', last_updated: '2026-01-11', features: ['5000+ integrations', 'Visual workflow builder', 'Multi-step automations'], screenshots: [] },
        { id: '6', name: 'DocuSign eSignature', description: 'Send documents for electronic signature directly from your CRM.', short_description: 'Electronic signatures integration', icon: '✍️', category: 'automation', developer: 'DocuSign', rating: 4.8, reviews_count: 980, installs: 35000, price: 14.99, is_free: false, is_installed: false, version: '1.8.0', last_updated: '2026-01-09', features: ['Send for signature', 'Track status', 'Template library'], screenshots: [] },
        { id: '7', name: 'Teams Collaboration', description: 'Integrate Microsoft Teams for seamless team collaboration and notifications.', short_description: 'Microsoft Teams integration', icon: '👥', category: 'team', developer: 'Microsoft', rating: 4.7, reviews_count: 1800, installs: 65000, price: 0, is_free: true, is_installed: false, version: '2.5.0', last_updated: '2026-01-07', features: ['Team notifications', 'Chat integration', 'Meeting scheduling'], screenshots: [] },
        { id: '8', name: 'Security Scanner', description: 'Scan your CRM data for security vulnerabilities and compliance issues.', short_description: 'Security and compliance scanning', icon: '🔒', category: 'security', developer: 'SecureCloud', rating: 4.5, reviews_count: 420, installs: 12000, price: 49.99, is_free: false, is_installed: false, version: '1.2.0', last_updated: '2026-01-06', features: ['Vulnerability scanning', 'Compliance reports', 'Risk assessment'], screenshots: [] },
      ]);
      setMyApps([
        { id: '2', name: 'Google Calendar Sync', description: 'Sync your meetings and appointments with Google Calendar.', short_description: 'Two-way calendar synchronization', icon: '📅', category: 'calendar', developer: 'Google', rating: 4.9, reviews_count: 2100, installs: 85000, price: 0, is_free: true, is_installed: true, version: '3.0.1', last_updated: '2026-01-08', features: [], screenshots: [], installed_at: '2026-01-01T10:00:00Z', settings: {} },
        { id: '5', name: 'Zapier Automation', description: 'Connect your CRM to 5000+ apps.', short_description: 'Connect to 5000+ apps', icon: '⚡', category: 'automation', developer: 'Zapier', rating: 4.9, reviews_count: 3200, installs: 120000, price: 0, is_free: true, is_installed: true, version: '4.0.0', last_updated: '2026-01-11', features: [], screenshots: [], installed_at: '2025-12-15T14:30:00Z', settings: {} },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const installApp = async (appId: string) => {
    try {
      await appMarketplaceAPI.installApp(appId);
      setApps(apps.map(app => 
        app.id === appId ? { ...app, is_installed: true } : app
      ));
      const installedApp = apps.find(app => app.id === appId);
      if (installedApp) {
        setMyApps([...myApps, { 
          ...installedApp, 
          is_installed: true, 
          installed_at: new Date().toISOString(), 
          settings: {} 
        }]);
      }
    } catch (error) {
      console.error('Failed to install app:', error);
      // Demo: just update state
      setApps(apps.map(app => 
        app.id === appId ? { ...app, is_installed: true } : app
      ));
    }
  };

  const uninstallApp = async (appId: string) => {
    try {
      await appMarketplaceAPI.uninstallApp(appId);
      setApps(apps.map(app => 
        app.id === appId ? { ...app, is_installed: false } : app
      ));
      setMyApps(myApps.filter(app => app.id !== appId));
    } catch (error) {
      console.error('Failed to uninstall app:', error);
      setApps(apps.map(app => 
        app.id === appId ? { ...app, is_installed: false } : app
      ));
      setMyApps(myApps.filter(app => app.id !== appId));
    }
  };

  const searchApps = async (query: string) => {
    setSearchQuery(query);
    if (!query) {
      loadMarketplace();
      return;
    }
    try {
      const results = await appMarketplaceAPI.searchApps(query);
      setApps(results.results || results || []);
    } catch (error) {
      console.error('Failed to search apps:', error);
      // Filter locally
      const filtered = apps.filter(app => 
        app.name.toLowerCase().includes(query.toLowerCase()) ||
        app.description.toLowerCase().includes(query.toLowerCase())
      );
      setApps(filtered);
    }
  };

  const filteredApps = selectedCategory 
    ? apps.filter(app => app.category === selectedCategory)
    : apps;

  const renderStars = (rating: number) => {
    return (
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`h-3 w-3 ${
              star <= Math.round(rating)
                ? 'fill-yellow-400 text-yellow-400'
                : 'text-gray-300'
            }`}
          />
        ))}
        <span className="text-xs text-muted-foreground ml-1">({rating})</span>
      </div>
    );
  };

  const formatInstalls = (count: number) => {
    if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`;
    if (count >= 1000) return `${(count / 1000).toFixed(0)}K`;
    return count.toString();
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Store className="h-8 w-8" />
            App Marketplace
          </h1>
          <p className="text-muted-foreground">
            Extend your CRM with powerful integrations and apps
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}>
            {viewMode === 'grid' ? <List className="h-4 w-4" /> : <Grid className="h-4 w-4" />}
          </Button>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search apps..."
            value={searchQuery}
            onChange={(e) => searchApps(e.target.value)}
            className="pl-10"
          />
        </div>
        <Button variant="outline">
          <Filter className="h-4 w-4 mr-2" />
          Filters
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="browse">Browse Apps</TabsTrigger>
          <TabsTrigger value="installed">My Apps ({myApps.length})</TabsTrigger>
          <TabsTrigger value="developer">Developer</TabsTrigger>
        </TabsList>

        <TabsContent value="browse" className="mt-6">
          <div className="flex gap-6">
            {/* Categories Sidebar */}
            <Card className="w-64 h-fit">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Categories</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <div className="space-y-1 p-2">
                  <Button
                    variant={selectedCategory === null ? 'secondary' : 'ghost'}
                    className="w-full justify-start"
                    onClick={() => setSelectedCategory(null)}
                  >
                    <Globe className="h-4 w-4 mr-2" />
                    All Apps
                  </Button>
                  {categories.map((category) => (
                    <Button
                      key={category.id}
                      variant={selectedCategory === category.slug ? 'secondary' : 'ghost'}
                      className="w-full justify-between"
                      onClick={() => setSelectedCategory(category.slug)}
                    >
                      <span className="flex items-center">
                        {categoryIcons[category.slug] || <Puzzle className="h-4 w-4" />}
                        <span className="ml-2">{category.name}</span>
                      </span>
                      <Badge variant="outline" className="text-xs">
                        {category.app_count}
                      </Badge>
                    </Button>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Apps Grid */}
            <div className="flex-1">
              {isLoading ? (
                <div className="flex items-center justify-center h-64">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
              ) : viewMode === 'grid' ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {filteredApps.map((app) => (
                    <Card key={app.id} className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => setSelectedApp(app)}>
                      <CardHeader className="pb-2">
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-3">
                            <div className="text-3xl">{app.icon}</div>
                            <div>
                              <CardTitle className="text-base">{app.name}</CardTitle>
                              <p className="text-xs text-muted-foreground">{app.developer}</p>
                            </div>
                          </div>
                          {app.is_installed && (
                            <Badge variant="secondary" className="text-xs">
                              <Check className="h-3 w-3 mr-1" />
                              Installed
                            </Badge>
                          )}
                        </div>
                      </CardHeader>
                      <CardContent className="pb-2">
                        <p className="text-sm text-muted-foreground line-clamp-2">
                          {app.short_description}
                        </p>
                        <div className="flex items-center justify-between mt-3">
                          {renderStars(app.rating)}
                          <span className="text-xs text-muted-foreground">
                            {formatInstalls(app.installs)} installs
                          </span>
                        </div>
                      </CardContent>
                      <CardFooter className="pt-2">
                        {app.is_installed ? (
                          <div className="flex gap-2 w-full">
                            <Button variant="outline" size="sm" className="flex-1" onClick={(e) => { e.stopPropagation(); }}>
                              <Settings className="h-4 w-4 mr-1" />
                              Configure
                            </Button>
                            <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); uninstallApp(app.id); }}>
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        ) : (
                          <Button size="sm" className="w-full" onClick={(e) => { e.stopPropagation(); installApp(app.id); }}>
                            <Download className="h-4 w-4 mr-2" />
                            {app.is_free ? 'Install Free' : `Install - $${app.price}/mo`}
                          </Button>
                        )}
                      </CardFooter>
                    </Card>
                  ))}
                </div>
              ) : (
                <div className="space-y-2">
                  {filteredApps.map((app) => (
                    <Card key={app.id} className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => setSelectedApp(app)}>
                      <CardContent className="p-4">
                        <div className="flex items-center gap-4">
                          <div className="text-3xl">{app.icon}</div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <h3 className="font-medium">{app.name}</h3>
                              {app.is_installed && (
                                <Badge variant="secondary" className="text-xs">Installed</Badge>
                              )}
                            </div>
                            <p className="text-sm text-muted-foreground">{app.short_description}</p>
                            <div className="flex items-center gap-4 mt-1">
                              {renderStars(app.rating)}
                              <span className="text-xs text-muted-foreground">{formatInstalls(app.installs)} installs</span>
                              <span className="text-xs text-muted-foreground">{app.developer}</span>
                            </div>
                          </div>
                          {app.is_installed ? (
                            <Button variant="outline" size="sm">
                              <Settings className="h-4 w-4 mr-1" />
                              Configure
                            </Button>
                          ) : (
                            <Button size="sm" onClick={(e) => { e.stopPropagation(); installApp(app.id); }}>
                              <Download className="h-4 w-4 mr-2" />
                              {app.is_free ? 'Install' : `$${app.price}/mo`}
                            </Button>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          </div>
        </TabsContent>

        <TabsContent value="installed" className="mt-6">
          <div className="space-y-4">
            {myApps.length === 0 ? (
              <Card>
                <CardContent className="flex flex-col items-center justify-center py-12">
                  <Puzzle className="h-16 w-16 text-muted-foreground mb-4" />
                  <h3 className="text-lg font-medium mb-2">No apps installed</h3>
                  <p className="text-muted-foreground mb-4">Browse the marketplace to find apps that enhance your CRM</p>
                  <Button onClick={() => setActiveTab('browse')}>
                    <Store className="h-4 w-4 mr-2" />
                    Browse Apps
                  </Button>
                </CardContent>
              </Card>
            ) : (
              myApps.map((app) => (
                <Card key={app.id}>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-4">
                      <div className="text-3xl">{app.icon}</div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h3 className="font-medium">{app.name}</h3>
                          <Badge variant="outline" className="text-xs">v{app.version}</Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">{app.short_description}</p>
                        <p className="text-xs text-muted-foreground mt-1">
                          Installed: {new Date(app.installed_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm">
                          <Settings className="h-4 w-4 mr-1" />
                          Settings
                        </Button>
                        <Button variant="outline" size="sm">
                          <ExternalLink className="h-4 w-4 mr-1" />
                          Open
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => uninstallApp(app.id)}>
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </TabsContent>

        <TabsContent value="developer" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Code className="h-5 w-5" />
                Developer Portal
              </CardTitle>
              <CardDescription>
                Build and publish your own apps to the marketplace
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className="bg-primary/10 rounded-full p-4 inline-block mb-4">
                        <Code className="h-8 w-8 text-primary" />
                      </div>
                      <h3 className="font-medium mb-2">Create Apps</h3>
                      <p className="text-sm text-muted-foreground mb-4">
                        Use our SDK to build powerful integrations
                      </p>
                      <Button variant="outline" size="sm">
                        View Documentation
                      </Button>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className="bg-green-100 rounded-full p-4 inline-block mb-4">
                        <Zap className="h-8 w-8 text-green-600" />
                      </div>
                      <h3 className="font-medium mb-2">API Access</h3>
                      <p className="text-sm text-muted-foreground mb-4">
                        Get API keys and access to all endpoints
                      </p>
                      <Button variant="outline" size="sm">
                        Get API Keys
                      </Button>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className="bg-purple-100 rounded-full p-4 inline-block mb-4">
                        <Store className="h-8 w-8 text-purple-600" />
                      </div>
                      <h3 className="font-medium mb-2">Publish</h3>
                      <p className="text-sm text-muted-foreground mb-4">
                        Submit your app for review and listing
                      </p>
                      <Button variant="outline" size="sm">
                        Submit App
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* App Detail Modal would go here */}
    </div>
  );
}

