'use client';

import React, { useState } from 'react';
import { 
  Shield,
  AlertTriangle,
  Eye,
  FileSearch,
  Lock,
  CheckCircle,
  XCircle,
  Plus,
  Settings,
  Download,
  Mail,
  Share2,
  Search
} from 'lucide-react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { formatDistanceToNow } from 'date-fns';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
// import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
// import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
// import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';

// Types
interface DataClassification {
  id: string;
  name: string;
  level: 'public' | 'internal' | 'confidential' | 'restricted' | 'top_secret';
  description: string;
  requires_encryption: boolean;
  requires_mfa: boolean;
  can_export: boolean;
  can_share_external: boolean;
  patterns: string[];
  keywords: string[];
}

interface DLPPolicy {
  id: string;
  name: string;
  description: string;
  classifications: string[];
  action: 'allow' | 'warn' | 'block' | 'quarantine' | 'encrypt' | 'redact';
  on_download: boolean;
  on_export: boolean;
  on_share: boolean;
  on_email: boolean;
  is_active: boolean;
  priority: number;
  incident_count: number;
}

interface DLPIncident {
  id: string;
  user_email: string;
  action_attempted: string;
  resource_type: string;
  resource_id: string;
  classification_level: string;
  status: 'new' | 'investigating' | 'resolved' | 'false_positive' | 'escalated';
  was_blocked: boolean;
  occurred_at: string;
  policy_name?: string;
}

// Mock API
const api = {
  getClassifications: async (): Promise<DataClassification[]> => [
    {
      id: '1',
      name: 'PII Data',
      level: 'restricted',
      description: 'Personally Identifiable Information',
      requires_encryption: true,
      requires_mfa: true,
      can_export: false,
      can_share_external: false,
      patterns: ['\\b\\d{3}-\\d{2}-\\d{4}\\b', '\\b\\d{16}\\b'],
      keywords: ['social security', 'ssn', 'credit card'],
    },
    {
      id: '2',
      name: 'Financial Data',
      level: 'confidential',
      description: 'Financial records and transactions',
      requires_encryption: true,
      requires_mfa: false,
      can_export: true,
      can_share_external: false,
      patterns: ['\\$[\\d,]+\\.\\d{2}'],
      keywords: ['revenue', 'salary', 'invoice'],
    },
    {
      id: '3',
      name: 'Internal Documents',
      level: 'internal',
      description: 'Internal company documents',
      requires_encryption: false,
      requires_mfa: false,
      can_export: true,
      can_share_external: true,
      patterns: [],
      keywords: ['internal use only', 'confidential'],
    },
  ],
  getPolicies: async (): Promise<DLPPolicy[]> => [
    {
      id: '1',
      name: 'Block PII Export',
      description: 'Prevent export of documents containing PII',
      classifications: ['PII Data'],
      action: 'block',
      on_download: true,
      on_export: true,
      on_share: true,
      on_email: true,
      is_active: true,
      priority: 100,
      incident_count: 23,
    },
    {
      id: '2',
      name: 'Warn on Financial Export',
      description: 'Warn when exporting financial data',
      classifications: ['Financial Data'],
      action: 'warn',
      on_download: true,
      on_export: true,
      on_share: false,
      on_email: true,
      is_active: true,
      priority: 90,
      incident_count: 45,
    },
  ],
  getIncidents: async (): Promise<DLPIncident[]> => [
    {
      id: '1',
      user_email: 'john@example.com',
      action_attempted: 'export',
      resource_type: 'Contact',
      resource_id: 'c-123',
      classification_level: 'restricted',
      status: 'new',
      was_blocked: true,
      occurred_at: new Date().toISOString(),
      policy_name: 'Block PII Export',
    },
    {
      id: '2',
      user_email: 'jane@example.com',
      action_attempted: 'email',
      resource_type: 'Report',
      resource_id: 'r-456',
      classification_level: 'confidential',
      status: 'investigating',
      was_blocked: false,
      occurred_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      policy_name: 'Warn on Financial Export',
    },
  ],
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  classifyContent: async (content: string): Promise<{
    matches: { classification: string; level: string }[];
    highest_level: string;
  }> => ({
    matches: [{ classification: 'PII Data', level: 'restricted' }],
    highest_level: 'restricted',
  }),
};

// Classification Level Badge
const ClassificationBadge: React.FC<{ level: string }> = ({ level }) => {
  const colors: Record<string, string> = {
    public: 'bg-gray-100 text-gray-800',
    internal: 'bg-blue-100 text-blue-800',
    confidential: 'bg-yellow-100 text-yellow-800',
    restricted: 'bg-orange-100 text-orange-800',
    top_secret: 'bg-red-100 text-red-800',
  };
  
  return (
    <Badge className={colors[level] || 'bg-gray-100 text-gray-800'}>
      {level.replace('_', ' ').toUpperCase()}
    </Badge>
  );
};

// Action Badge
const ActionBadge: React.FC<{ action: string }> = ({ action }) => {
  const config: Record<string, { color: string; icon: React.ReactNode }> = {
    allow: { color: 'bg-green-100 text-green-800', icon: <CheckCircle className="h-3 w-3" /> },
    warn: { color: 'bg-yellow-100 text-yellow-800', icon: <AlertTriangle className="h-3 w-3" /> },
    block: { color: 'bg-red-100 text-red-800', icon: <XCircle className="h-3 w-3" /> },
    quarantine: { color: 'bg-purple-100 text-purple-800', icon: <Lock className="h-3 w-3" /> },
    encrypt: { color: 'bg-blue-100 text-blue-800', icon: <Lock className="h-3 w-3" /> },
    redact: { color: 'bg-orange-100 text-orange-800', icon: <Eye className="h-3 w-3" /> },
  };
  
  const { color, icon } = config[action] || { color: 'bg-gray-100 text-gray-800', icon: null };
  
  return (
    <Badge className={`${color} flex items-center gap-1`}>
      {icon}
      {action.toUpperCase()}
    </Badge>
  );
};

// Status Badge
const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const colors: Record<string, string> = {
    new: 'bg-blue-100 text-blue-800',
    investigating: 'bg-yellow-100 text-yellow-800',
    resolved: 'bg-green-100 text-green-800',
    false_positive: 'bg-gray-100 text-gray-800',
    escalated: 'bg-red-100 text-red-800',
  };
  
  return (
    <Badge className={colors[status] || 'bg-gray-100 text-gray-800'}>
      {status.replace('_', ' ')}
    </Badge>
  );
};

// Classifications Tab
const ClassificationsTab: React.FC = () => {
  const { data: classifications, isLoading } = useQuery({
    queryKey: ['classifications'],
    queryFn: api.getClassifications,
  });

  if (isLoading) return <div className="flex justify-center p-8">Loading...</div>;

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-medium">Data Classifications</h3>
          <p className="text-sm text-muted-foreground">
            Define classification levels and detection patterns
          </p>
        </div>
        <Button size="sm">
          <Plus className="h-4 w-4 mr-2" />
          Add Classification
        </Button>
      </div>

      <div className="space-y-3">
        {classifications?.map((classification) => (
          <Card key={classification.id}>
            <CardContent className="p-4">
              <div className="flex items-start justify-between">
                <div className="space-y-2">
                  <div className="flex items-center gap-3">
                    <span className="font-medium">{classification.name}</span>
                    <ClassificationBadge level={classification.level} />
                  </div>
                  
                  <p className="text-sm text-muted-foreground">{classification.description}</p>
                  
                  <div className="flex flex-wrap gap-2">
                    {classification.requires_encryption && (
                      <Badge variant="outline" className="text-blue-600">
                        <Lock className="h-3 w-3 mr-1" />
                        Encryption Required
                      </Badge>
                    )}
                    {classification.requires_mfa && (
                      <Badge variant="outline" className="text-purple-600">
                        <Shield className="h-3 w-3 mr-1" />
                        MFA Required
                      </Badge>
                    )}
                    {!classification.can_export && (
                      <Badge variant="outline" className="text-red-600">
                        <Download className="h-3 w-3 mr-1" />
                        Export Blocked
                      </Badge>
                    )}
                    {!classification.can_share_external && (
                      <Badge variant="outline" className="text-orange-600">
                        <Share2 className="h-3 w-3 mr-1" />
                        External Sharing Blocked
                      </Badge>
                    )}
                  </div>

                  {classification.keywords.length > 0 && (
                    <div className="text-xs text-muted-foreground">
                      <span className="font-medium">Keywords:</span>{' '}
                      {classification.keywords.join(', ')}
                    </div>
                  )}
                </div>

                <Button variant="ghost" size="sm">
                  <Settings className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

// Policies Tab
const PoliciesTab: React.FC = () => {
  const { data: policies, isLoading } = useQuery({
    queryKey: ['dlp-policies'],
    queryFn: api.getPolicies,
  });

  if (isLoading) return <div className="flex justify-center p-8">Loading...</div>;

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-medium">DLP Policies</h3>
          <p className="text-sm text-muted-foreground">
            Configure automated protection policies for sensitive data
          </p>
        </div>
        <Button size="sm">
          <Plus className="h-4 w-4 mr-2" />
          Create Policy
        </Button>
      </div>

      <div className="space-y-3">
        {policies?.map((policy) => (
          <Card key={policy.id}>
            <CardContent className="p-4">
              <div className="flex items-start justify-between">
                <div className="space-y-2">
                  <div className="flex items-center gap-3">
                    <span className="font-medium">{policy.name}</span>
                    <ActionBadge action={policy.action} />
                    <Badge variant={policy.is_active ? 'default' : 'secondary'}>
                      {policy.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                    <Badge variant="outline">Priority: {policy.priority}</Badge>
                  </div>
                  
                  <p className="text-sm text-muted-foreground">{policy.description}</p>
                  
                  <div className="flex items-center gap-4 text-sm">
                    <span className="text-muted-foreground">Triggers:</span>
                    {policy.on_download && (
                      <Badge variant="outline" className="text-xs">
                        <Download className="h-3 w-3 mr-1" />
                        Download
                      </Badge>
                    )}
                    {policy.on_export && (
                      <Badge variant="outline" className="text-xs">
                        <FileSearch className="h-3 w-3 mr-1" />
                        Export
                      </Badge>
                    )}
                    {policy.on_share && (
                      <Badge variant="outline" className="text-xs">
                        <Share2 className="h-3 w-3 mr-1" />
                        Share
                      </Badge>
                    )}
                    {policy.on_email && (
                      <Badge variant="outline" className="text-xs">
                        <Mail className="h-3 w-3 mr-1" />
                        Email
                      </Badge>
                    )}
                  </div>

                  <div className="text-xs text-muted-foreground">
                    <span className="font-medium">Classifications:</span>{' '}
                    {policy.classifications.join(', ')}
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold">{policy.incident_count}</p>
                    <p className="text-xs text-muted-foreground">Incidents</p>
                  </div>
                  <Switch checked={policy.is_active} />
                  <Button variant="ghost" size="sm">
                    <Settings className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

// Incidents Tab
const IncidentsTab: React.FC = () => {
  const [filter, setFilter] = useState<string>('all');
  
  const { data: incidents, isLoading } = useQuery({
    queryKey: ['dlp-incidents'],
    queryFn: api.getIncidents,
  });

  if (isLoading) return <div className="flex justify-center p-8">Loading...</div>;

  const filteredIncidents = filter === 'all' 
    ? incidents 
    : incidents?.filter(i => i.status === filter);

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-medium">DLP Incidents</h3>
          <p className="text-sm text-muted-foreground">
            Review and investigate data loss prevention incidents
          </p>
        </div>
        <div className="flex gap-2">
          <Select value={filter} onValueChange={setFilter}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Filter by status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Incidents</SelectItem>
              <SelectItem value="new">New</SelectItem>
              <SelectItem value="investigating">Investigating</SelectItem>
              <SelectItem value="escalated">Escalated</SelectItem>
              <SelectItem value="resolved">Resolved</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export Report
          </Button>
        </div>
      </div>

      <div className="space-y-3">
        {filteredIncidents?.map((incident) => (
          <Card key={incident.id}>
            <CardContent className="p-4">
              <div className="flex items-start justify-between">
                <div className="space-y-2">
                  <div className="flex items-center gap-3">
                    {incident.was_blocked ? (
                      <XCircle className="h-5 w-5 text-red-500" />
                    ) : (
                      <AlertTriangle className="h-5 w-5 text-yellow-500" />
                    )}
                    <span className="font-medium">
                      {incident.action_attempted.toUpperCase()} attempted on {incident.resource_type}
                    </span>
                    <StatusBadge status={incident.status} />
                    <ClassificationBadge level={incident.classification_level} />
                  </div>
                  
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <span>User: {incident.user_email}</span>
                    <span>Resource: {incident.resource_id}</span>
                    <span>
                      {formatDistanceToNow(new Date(incident.occurred_at), { addSuffix: true })}
                    </span>
                  </div>

                  {incident.policy_name && (
                    <div className="text-xs text-muted-foreground">
                      Triggered by: <span className="font-medium">{incident.policy_name}</span>
                    </div>
                  )}
                </div>

                <div className="flex gap-2">
                  <Button variant="outline" size="sm">
                    <Eye className="h-4 w-4 mr-1" />
                    Investigate
                  </Button>
                  <Button variant="ghost" size="sm">
                    <CheckCircle className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

// Content Scanner Component
const ContentScanner: React.FC = () => {
  const [content, setContent] = useState('');
  const [result, setResult] = useState<{
    matches: { classification: string; level: string }[];
    highest_level: string;
  } | null>(null);

  const scanMutation = useMutation({
    mutationFn: api.classifyContent,
    onSuccess: setResult,
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <FileSearch className="h-5 w-5" />
          Content Scanner
        </CardTitle>
        <CardDescription>
          Scan content for sensitive data before sharing
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Textarea
          placeholder="Paste content to scan for sensitive data..."
          value={content}
          onChange={(e) => setContent(e.target.value)}
          rows={5}
        />
        <Button 
          onClick={() => scanMutation.mutate(content)}
          disabled={!content || scanMutation.isPending}
        >
          <Search className="h-4 w-4 mr-2" />
          {scanMutation.isPending ? 'Scanning...' : 'Scan Content'}
        </Button>

        {result && (
          <div className="p-4 border rounded-lg space-y-2">
            <div className="flex items-center gap-2">
              <span className="font-medium">Classification:</span>
              <ClassificationBadge level={result.highest_level} />
            </div>
            {result.matches.length > 0 && (
              <div>
                <span className="text-sm text-muted-foreground">Detected:</span>
                <div className="flex flex-wrap gap-2 mt-1">
                  {result.matches.map((match, i) => (
                    <Badge key={i} variant="outline">
                      {match.classification}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Main DLP Dashboard Component
export const DLPDashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Shield className="h-6 w-6" />
            Data Loss Prevention
          </h2>
          <p className="text-muted-foreground">
            Protect sensitive data with automated classification and policy enforcement
          </p>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Classifications</p>
                <p className="text-2xl font-bold">5</p>
              </div>
              <FileSearch className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Active Policies</p>
                <p className="text-2xl font-bold">12</p>
              </div>
              <Shield className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Incidents (30d)</p>
                <p className="text-2xl font-bold">68</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-yellow-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Blocked Actions</p>
                <p className="text-2xl font-bold">23</p>
              </div>
              <XCircle className="h-8 w-8 text-red-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Tabs defaultValue="incidents" className="space-y-4">
            <TabsList>
              <TabsTrigger value="incidents">Incidents</TabsTrigger>
              <TabsTrigger value="policies">Policies</TabsTrigger>
              <TabsTrigger value="classifications">Classifications</TabsTrigger>
            </TabsList>

            <TabsContent value="incidents">
              <IncidentsTab />
            </TabsContent>

            <TabsContent value="policies">
              <PoliciesTab />
            </TabsContent>

            <TabsContent value="classifications">
              <ClassificationsTab />
            </TabsContent>
          </Tabs>
        </div>

        <div>
          <ContentScanner />
        </div>
      </div>
    </div>
  );
};

export default DLPDashboard;

