'use client';

import React, { useState } from 'react';
// import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
// import { Progress } from '@/components/ui/progress';
import { Switch } from '@/components/ui/switch';
import {
  Code,
  Key,
  Webhook,
  BarChart3,
  Book,
  Download,
  Copy,
  Eye,
  EyeOff,
  Plus,
  Trash2,
  RefreshCw,
  CheckCircle,
  XCircle,
  ExternalLink,
  Terminal,
  Zap,
  GitBranch,
  Package,
  Send,
  Settings,
} from 'lucide-react';

// Types
interface APIKey {
  id: string;
  name: string;
  keyPrefix: string;
  scopes: string[];
  rateLimitPerMinute: number;
  isActive: boolean;
  lastUsedAt?: string;
  totalRequests: number;
  expiresAt?: string;
  createdAt: string;
}

interface WebhookConfig {
  id: string;
  name: string;
  url: string;
  events: string[];
  isActive: boolean;
  consecutiveFailures: number;
  lastTriggeredAt?: string;
  lastSuccessAt?: string;
}

interface WebhookDelivery {
  id: string;
  eventType: string;
  status: 'success' | 'failed' | 'retrying';
  responseStatusCode?: number;
  responseTimeMs?: number;
  attemptCount: number;
  createdAt: string;
}

interface APIAnalytics {
  totalRequests: number;
  successRate: number;
  avgResponseTime: number;
  topEndpoints: { endpoint: string; count: number; avgTime: number }[];
  statusCodes: { code: string; count: number }[];
  requestsOverTime: { date: string; count: number }[];
}

// Mock data
const mockAPIKeys: APIKey[] = [
  {
    id: '1',
    name: 'Production API Key',
    keyPrefix: 'sk_live_',
    scopes: ['contacts:read', 'contacts:write', 'deals:read', 'deals:write'],
    rateLimitPerMinute: 60,
    isActive: true,
    lastUsedAt: '2024-03-15T10:30:00',
    totalRequests: 125000,
    createdAt: '2024-01-01',
  },
  {
    id: '2',
    name: 'Development Key',
    keyPrefix: 'sk_test_',
    scopes: ['*'],
    rateLimitPerMinute: 100,
    isActive: true,
    lastUsedAt: '2024-03-15T09:15:00',
    totalRequests: 45000,
    createdAt: '2024-02-15',
  },
];

const mockWebhooks: WebhookConfig[] = [
  {
    id: '1',
    name: 'Slack Notifications',
    url: 'https://hooks.slack.com/services/xxx',
    events: ['deal.won', 'deal.lost'],
    isActive: true,
    consecutiveFailures: 0,
    lastTriggeredAt: '2024-03-15T10:00:00',
    lastSuccessAt: '2024-03-15T10:00:00',
  },
  {
    id: '2',
    name: 'Zapier Integration',
    url: 'https://hooks.zapier.com/xxx',
    events: ['contact.created', 'contact.updated'],
    isActive: true,
    consecutiveFailures: 2,
    lastTriggeredAt: '2024-03-15T09:30:00',
    lastSuccessAt: '2024-03-14T15:00:00',
  },
];

const mockDeliveries: WebhookDelivery[] = [
  { id: '1', eventType: 'deal.won', status: 'success', responseStatusCode: 200, responseTimeMs: 145, attemptCount: 1, createdAt: '2024-03-15T10:00:00' },
  { id: '2', eventType: 'contact.updated', status: 'failed', responseStatusCode: 500, responseTimeMs: 2500, attemptCount: 3, createdAt: '2024-03-15T09:30:00' },
  { id: '3', eventType: 'deal.created', status: 'success', responseStatusCode: 200, responseTimeMs: 89, attemptCount: 1, createdAt: '2024-03-15T09:00:00' },
  { id: '4', eventType: 'contact.created', status: 'retrying', attemptCount: 2, createdAt: '2024-03-15T08:45:00' },
];

const mockAnalytics: APIAnalytics = {
  totalRequests: 125000,
  successRate: 99.2,
  avgResponseTime: 145,
  topEndpoints: [
    { endpoint: 'GET /api/contacts', count: 45000, avgTime: 120 },
    { endpoint: 'GET /api/deals', count: 32000, avgTime: 180 },
    { endpoint: 'POST /api/contacts', count: 15000, avgTime: 250 },
    { endpoint: 'PUT /api/deals/:id', count: 12000, avgTime: 200 },
    { endpoint: 'GET /api/activities', count: 8000, avgTime: 95 },
  ],
  statusCodes: [
    { code: '2xx', count: 124000 },
    { code: '4xx', count: 850 },
    { code: '5xx', count: 150 },
  ],
  requestsOverTime: [],
};

// const availableScopes = [
//   { scope: 'contacts:read', description: 'Read contacts' },
//   { scope: 'contacts:write', description: 'Create/update contacts' },
//   { scope: 'deals:read', description: 'Read deals' },
//   { scope: 'deals:write', description: 'Create/update deals' },
//   { scope: 'activities:read', description: 'Read activities' },
//   { scope: 'activities:write', description: 'Create activities' },
//   { scope: 'reports:read', description: 'Access reports' },
//   { scope: 'webhooks:manage', description: 'Manage webhooks' },
// ];

// const availableEvents = [
//   'contact.created', 'contact.updated', 'contact.deleted',
//   'deal.created', 'deal.updated', 'deal.won', 'deal.lost',
//   'task.created', 'task.completed',
//   'activity.created',
// ];

// Tab Components
const APIKeysTab: React.FC = () => {
  const [showKey, setShowKey] = useState<string | null>(null);
  const [] = useState('');

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-semibold">API Keys</h3>
          <p className="text-sm text-muted-foreground">
            Manage your API keys for programmatic access
          </p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Create API Key
        </Button>
      </div>

      <div className="space-y-4">
        {mockAPIKeys.map((key) => (
          <Card key={key.id}>
            <CardContent className="p-4">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4">
                  <div className="h-10 w-10 rounded-lg bg-blue-100 flex items-center justify-center">
                    <Key className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium">{key.name}</h4>
                      {key.isActive ? (
                        <Badge className="bg-green-100 text-green-800">Active</Badge>
                      ) : (
                        <Badge variant="secondary">Inactive</Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-2 mt-1">
                      <code className="text-sm bg-muted px-2 py-1 rounded">
                        {showKey === key.id ? `${key.keyPrefix}...abcd1234` : `${key.keyPrefix}••••••••••••`}
                      </code>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setShowKey(showKey === key.id ? null : key.id)}
                      >
                        {showKey === key.id ? (
                          <EyeOff className="h-4 w-4" />
                        ) : (
                          <Eye className="h-4 w-4" />
                        )}
                      </Button>
                      <Button variant="ghost" size="sm">
                        <Copy className="h-4 w-4" />
                      </Button>
                    </div>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {key.scopes.map((scope) => (
                        <Badge key={scope} variant="outline" className="text-xs">
                          {scope}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium">{key.totalRequests.toLocaleString()} requests</p>
                  <p className="text-xs text-muted-foreground">
                    Last used: {key.lastUsedAt ? new Date(key.lastUsedAt).toLocaleString() : 'Never'}
                  </p>
                  <div className="flex gap-2 mt-2 justify-end">
                    <Button variant="ghost" size="sm">
                      <RefreshCw className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="sm" className="text-red-600">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Quick Start */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Terminal className="h-5 w-5" />
            Quick Start
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="bg-gray-900 text-gray-100 p-4 rounded-lg font-mono text-sm">
            <div className="text-green-400"># Install the SDK</div>
            <div className="mt-1">npm install @mycrm/sdk</div>
            <div className="mt-4 text-green-400"># Initialize the client</div>
            <div className="mt-1">
              <span className="text-purple-400">import</span> {'{'} MyCRM {'}'}{' '}
              <span className="text-purple-400">from</span>{' '}
              <span className="text-yellow-300">&apos;@mycrm/sdk&apos;</span>;
            </div>
            <div className="mt-2">
              <span className="text-purple-400">const</span> client ={' '}
              <span className="text-purple-400">new</span> MyCRM({'{'}
            </div>
            <div className="pl-4">
              apiKey: <span className="text-yellow-300">&apos;sk_live_...&apos;</span>
            </div>
            <div>{'}'});</div>
            <div className="mt-4 text-green-400"># Make your first request</div>
            <div className="mt-1">
              <span className="text-purple-400">const</span> contacts ={' '}
              <span className="text-purple-400">await</span> client.contacts.list();
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

const WebhooksTab: React.FC = () => (
  <div className="space-y-6">
    <div className="flex justify-between items-center">
      <div>
        <h3 className="text-lg font-semibold">Webhooks</h3>
        <p className="text-sm text-muted-foreground">
          Receive real-time notifications when events occur
        </p>
      </div>
      <Button>
        <Plus className="h-4 w-4 mr-2" />
        Add Webhook
      </Button>
    </div>

    {/* Webhooks List */}
    <div className="space-y-4">
      {mockWebhooks.map((webhook) => (
        <Card key={webhook.id}>
          <CardContent className="p-4">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-4">
                <div
                  className={`h-10 w-10 rounded-lg flex items-center justify-center ${
                    webhook.consecutiveFailures > 0 ? 'bg-yellow-100' : 'bg-green-100'
                  }`}
                >
                  <Webhook
                    className={`h-5 w-5 ${
                      webhook.consecutiveFailures > 0 ? 'text-yellow-600' : 'text-green-600'
                    }`}
                  />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="font-medium">{webhook.name}</h4>
                    {webhook.consecutiveFailures > 0 && (
                      <Badge className="bg-yellow-100 text-yellow-800">
                        {webhook.consecutiveFailures} failures
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground font-mono">{webhook.url}</p>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {webhook.events.map((event) => (
                      <Badge key={event} variant="outline" className="text-xs">
                        {event}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <Switch checked={webhook.isActive} />
                <Button variant="ghost" size="sm">
                  <Send className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="sm">
                  <Settings className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>

    {/* Recent Deliveries */}
    <Card>
      <CardHeader>
        <CardTitle>Recent Deliveries</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {mockDeliveries.map((delivery) => (
            <div
              key={delivery.id}
              className="flex items-center justify-between p-3 rounded-lg border"
            >
              <div className="flex items-center gap-3">
                {delivery.status === 'success' ? (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                ) : delivery.status === 'failed' ? (
                  <XCircle className="h-5 w-5 text-red-500" />
                ) : (
                  <RefreshCw className="h-5 w-5 text-yellow-500 animate-spin" />
                )}
                <div>
                  <code className="text-sm font-medium">{delivery.eventType}</code>
                  <p className="text-xs text-muted-foreground">
                    Attempt {delivery.attemptCount} •{' '}
                    {new Date(delivery.createdAt).toLocaleString()}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                {delivery.responseStatusCode && (
                  <Badge
                    variant="outline"
                    className={
                      delivery.responseStatusCode >= 200 && delivery.responseStatusCode < 300
                        ? 'text-green-600'
                        : 'text-red-600'
                    }
                  >
                    {delivery.responseStatusCode}
                  </Badge>
                )}
                {delivery.responseTimeMs && (
                  <span className="text-sm text-muted-foreground">
                    {delivery.responseTimeMs}ms
                  </span>
                )}
                <Button variant="ghost" size="sm">
                  <Eye className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  </div>
);

const AnalyticsTab: React.FC = () => (
  <div className="space-y-6">
    {/* Overview Stats */}
    <div className="grid grid-cols-4 gap-4">
      <Card>
        <CardContent className="p-4">
          <p className="text-sm text-muted-foreground">Total Requests</p>
          <p className="text-2xl font-bold">{mockAnalytics.totalRequests.toLocaleString()}</p>
          <p className="text-xs text-green-600">+12% from last month</p>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-4">
          <p className="text-sm text-muted-foreground">Success Rate</p>
          <p className="text-2xl font-bold">{mockAnalytics.successRate}%</p>
          <p className="text-xs text-muted-foreground">Last 30 days</p>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-4">
          <p className="text-sm text-muted-foreground">Avg Response Time</p>
          <p className="text-2xl font-bold">{mockAnalytics.avgResponseTime}ms</p>
          <p className="text-xs text-green-600">-5% from last week</p>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-4">
          <p className="text-sm text-muted-foreground">Active API Keys</p>
          <p className="text-2xl font-bold">2</p>
          <p className="text-xs text-muted-foreground">Across all environments</p>
        </CardContent>
      </Card>
    </div>

    {/* Top Endpoints */}
    <Card>
      <CardHeader>
        <CardTitle>Top Endpoints</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {mockAnalytics.topEndpoints.map((endpoint, i) => (
            <div key={i} className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-sm text-muted-foreground w-6">{i + 1}.</span>
                <code className="text-sm font-medium">{endpoint.endpoint}</code>
              </div>
              <div className="flex items-center gap-6">
                <span className="text-sm">{endpoint.count.toLocaleString()} requests</span>
                <span className="text-sm text-muted-foreground w-20 text-right">
                  {endpoint.avgTime}ms avg
                </span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>

    {/* Status Codes */}
    <Card>
      <CardHeader>
        <CardTitle>Response Status Codes</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-4">
          {mockAnalytics.statusCodes.map((stat) => (
            <div
              key={stat.code}
              className={`p-4 rounded-lg ${
                stat.code === '2xx'
                  ? 'bg-green-50'
                  : stat.code === '4xx'
                  ? 'bg-yellow-50'
                  : 'bg-red-50'
              }`}
            >
              <p
                className={`text-sm font-medium ${
                  stat.code === '2xx'
                    ? 'text-green-700'
                    : stat.code === '4xx'
                    ? 'text-yellow-700'
                    : 'text-red-700'
                }`}
              >
                {stat.code} Responses
              </p>
              <p className="text-2xl font-bold mt-1">{stat.count.toLocaleString()}</p>
              <p className="text-xs text-muted-foreground mt-1">
                {((stat.count / mockAnalytics.totalRequests) * 100).toFixed(1)}% of total
              </p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  </div>
);

const DocsTab: React.FC = () => (
  <div className="space-y-6">
    <div className="grid grid-cols-3 gap-4">
      <Card className="cursor-pointer hover:bg-muted/50">
        <CardContent className="p-6">
          <Book className="h-8 w-8 text-blue-500 mb-3" />
          <h4 className="font-medium">API Reference</h4>
          <p className="text-sm text-muted-foreground mt-1">
            Complete documentation for all endpoints
          </p>
          <Button variant="link" className="p-0 mt-2">
            View Docs <ExternalLink className="h-3 w-3 ml-1" />
          </Button>
        </CardContent>
      </Card>
      <Card className="cursor-pointer hover:bg-muted/50">
        <CardContent className="p-6">
          <GitBranch className="h-8 w-8 text-purple-500 mb-3" />
          <h4 className="font-medium">GraphQL Playground</h4>
          <p className="text-sm text-muted-foreground mt-1">
            Interactive GraphQL explorer and IDE
          </p>
          <Button variant="link" className="p-0 mt-2">
            Open Playground <ExternalLink className="h-3 w-3 ml-1" />
          </Button>
        </CardContent>
      </Card>
      <Card className="cursor-pointer hover:bg-muted/50">
        <CardContent className="p-6">
          <Zap className="h-8 w-8 text-yellow-500 mb-3" />
          <h4 className="font-medium">Webhooks Guide</h4>
          <p className="text-sm text-muted-foreground mt-1">
            Learn how to handle webhook events
          </p>
          <Button variant="link" className="p-0 mt-2">
            Read Guide <ExternalLink className="h-3 w-3 ml-1" />
          </Button>
        </CardContent>
      </Card>
    </div>

    {/* SDKs */}
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Package className="h-5 w-5" />
          Official SDKs
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-4 gap-4">
          {[
            { name: 'JavaScript', icon: '🟨', version: '2.1.0', downloads: '45K' },
            { name: 'Python', icon: '🐍', version: '1.8.2', downloads: '32K' },
            { name: 'Ruby', icon: '💎', version: '1.5.0', downloads: '12K' },
            { name: 'PHP', icon: '🐘', version: '1.3.1', downloads: '8K' },
          ].map((sdk) => (
            <Card key={sdk.name}>
              <CardContent className="p-4 text-center">
                <span className="text-3xl">{sdk.icon}</span>
                <p className="font-medium mt-2">{sdk.name}</p>
                <p className="text-xs text-muted-foreground">v{sdk.version}</p>
                <Button variant="outline" size="sm" className="mt-2 w-full">
                  <Download className="h-3 w-3 mr-1" />
                  Install
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </CardContent>
    </Card>

    {/* API Status */}
    <Card>
      <CardHeader>
        <CardTitle>API Status</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {[
            { service: 'REST API', status: 'operational', uptime: '99.99%' },
            { service: 'GraphQL API', status: 'operational', uptime: '99.98%' },
            { service: 'Webhook Delivery', status: 'operational', uptime: '99.95%' },
            { service: 'OAuth Server', status: 'operational', uptime: '100%' },
          ].map((service) => (
            <div key={service.service} className="flex items-center justify-between p-3 border rounded-lg">
              <div className="flex items-center gap-3">
                <div className="h-3 w-3 rounded-full bg-green-500" />
                <span className="font-medium">{service.service}</span>
              </div>
              <div className="flex items-center gap-4">
                <Badge className="bg-green-100 text-green-800 capitalize">{service.status}</Badge>
                <span className="text-sm text-muted-foreground">{service.uptime} uptime</span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  </div>
);

// Main Component
export default function DeveloperPortal() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Code className="h-8 w-8 text-purple-600" />
            Developer Portal
          </h1>
          <p className="text-muted-foreground mt-1">
            API keys, webhooks, and developer resources
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Book className="h-4 w-4 mr-2" />
            API Docs
          </Button>
          <Button variant="outline">
            <Terminal className="h-4 w-4 mr-2" />
            GraphQL Playground
          </Button>
        </div>
      </div>

      <Tabs defaultValue="keys">
        <TabsList>
          <TabsTrigger value="keys" className="flex items-center gap-2">
            <Key className="h-4 w-4" />
            API Keys
          </TabsTrigger>
          <TabsTrigger value="webhooks" className="flex items-center gap-2">
            <Webhook className="h-4 w-4" />
            Webhooks
          </TabsTrigger>
          <TabsTrigger value="analytics" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Analytics
          </TabsTrigger>
          <TabsTrigger value="docs" className="flex items-center gap-2">
            <Book className="h-4 w-4" />
            Documentation
          </TabsTrigger>
        </TabsList>

        <TabsContent value="keys" className="mt-4">
          <APIKeysTab />
        </TabsContent>

        <TabsContent value="webhooks" className="mt-4">
          <WebhooksTab />
        </TabsContent>

        <TabsContent value="analytics" className="mt-4">
          <AnalyticsTab />
        </TabsContent>

        <TabsContent value="docs" className="mt-4">
          <DocsTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}
