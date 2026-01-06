/**
 * Compliance Dashboard Component
 * ================================
 * 
 * Comprehensive GDPR, SOC2, and regulatory compliance monitoring
 */

'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
// import {
//   Dialog,
//   DialogContent,
//   DialogDescription,
//   DialogFooter,
//   DialogHeader,
//   DialogTitle,
//   DialogTrigger,
// } from '@/components/ui/dialog';
import {
  AlertTriangle,
  CheckCircle2,
  Clock,
  Download,
  Eye,
  FileCheck,
  FileText,
  History,
  Lock,
  PenLine,
  RefreshCw,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Trash2,
  UserX,
  XCircle,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// =============================================================================
// Types
// =============================================================================

interface ComplianceStatus {
  gdpr: ComplianceFramework;
  soc2: ComplianceFramework;
  hipaa: ComplianceFramework;
  ccpa: ComplianceFramework;
  overall_score: number;
  last_audit: string;
  next_audit: string;
}

interface ComplianceFramework {
  name: string;
  score: number;
  status: 'compliant' | 'partial' | 'non_compliant';
  controls_passed: number;
  controls_total: number;
  findings: ComplianceFinding[];
}

interface ComplianceFinding {
  id: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  title: string;
  description: string;
  remediation: string;
  status: 'open' | 'in_progress' | 'resolved';
  due_date: string;
  assigned_to?: string;
}

interface DataSubjectRequest {
  id: string;
  type: 'access' | 'rectification' | 'erasure' | 'portability' | 'restriction';
  subject_email: string;
  subject_name: string;
  status: 'pending' | 'in_progress' | 'completed' | 'rejected';
  submitted_at: string;
  due_date: string;
  completed_at?: string;
}

interface AuditLogEntry {
  id: string;
  timestamp: string;
  user: string;
  action: string;
  resource: string;
  details: string;
  ip_address: string;
  risk_level: 'low' | 'medium' | 'high';
}

interface ConsentRecord {
  id: string;
  contact_email: string;
  contact_name: string;
  consent_type: string;
  status: 'active' | 'withdrawn' | 'expired';
  given_at: string;
  expires_at?: string;
  source: string;
}

// =============================================================================
// API Hooks
// =============================================================================

function useComplianceStatus() {
  return useQuery<ComplianceStatus>({
    queryKey: ['compliance', 'status'],
    queryFn: async () => {
      const res = await fetch('/api/compliance/status');
      if (!res.ok) throw new Error('Failed to fetch compliance status');
      return res.json();
    },
    refetchInterval: 60000, // 1 minute
  });
}

function useDataSubjectRequests() {
  return useQuery<DataSubjectRequest[]>({
    queryKey: ['compliance', 'dsr'],
    queryFn: async () => {
      const res = await fetch('/api/compliance/dsr');
      if (!res.ok) throw new Error('Failed to fetch DSR');
      return res.json();
    },
  });
}

function useAuditLogs() {
  return useQuery<AuditLogEntry[]>({
    queryKey: ['compliance', 'audit-logs'],
    queryFn: async () => {
      const res = await fetch('/api/compliance/audit-logs?limit=100');
      if (!res.ok) throw new Error('Failed to fetch audit logs');
      return res.json();
    },
  });
}

function useConsentRecords() {
  return useQuery<ConsentRecord[]>({
    queryKey: ['compliance', 'consents'],
    queryFn: async () => {
      const res = await fetch('/api/compliance/consents');
      if (!res.ok) throw new Error('Failed to fetch consent records');
      return res.json();
    },
  });
}

function useProcessDSR() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, action }: { id: string; action: 'approve' | 'reject' | 'complete' }) => {
      const res = await fetch(`/api/compliance/dsr/${id}/${action}`, {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to process DSR');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['compliance', 'dsr'] });
    },
  });
}

// =============================================================================
// Main Component
// =============================================================================

export function ComplianceDashboard({ className }: { className?: string }) {
  const { data: status, isLoading, refetch } = useComplianceStatus();
  const [activeTab, setActiveTab] = useState('overview');

  if (isLoading || !status) {
    return (
      <div className={cn('space-y-6', className)}>
        <div className="animate-pulse space-y-4">
          <div className="h-32 bg-muted rounded-lg" />
          <div className="grid grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-24 bg-muted rounded-lg" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={cn('space-y-6', className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Compliance Dashboard</h2>
          <p className="text-muted-foreground">
            Monitor regulatory compliance and data protection
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={() => refetch()}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button>
            <Download className="h-4 w-4 mr-2" />
            Export Report
          </Button>
        </div>
      </div>

      {/* Overall Score */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-4 rounded-full bg-gradient-to-r from-green-500/20 to-emerald-500/20">
                <ShieldCheck className="h-8 w-8 text-green-500" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Overall Compliance Score</p>
                <p className="text-4xl font-bold">{status.overall_score}%</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-muted-foreground">Last Audit</p>
              <p className="font-medium">{new Date(status.last_audit).toLocaleDateString()}</p>
              <p className="text-sm text-muted-foreground mt-2">Next Audit</p>
              <p className="font-medium">{new Date(status.next_audit).toLocaleDateString()}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Framework Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <FrameworkCard framework={status.gdpr} icon={Shield} />
        <FrameworkCard framework={status.soc2} icon={FileCheck} />
        <FrameworkCard framework={status.hipaa} icon={Lock} />
        <FrameworkCard framework={status.ccpa} icon={UserX} />
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="dsr">Data Subject Requests</TabsTrigger>
          <TabsTrigger value="audit">Audit Logs</TabsTrigger>
          <TabsTrigger value="consents">Consent Management</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="mt-6">
          <OverviewTab status={status} />
        </TabsContent>

        <TabsContent value="dsr" className="mt-6">
          <DSRTab />
        </TabsContent>

        <TabsContent value="audit" className="mt-6">
          <AuditLogsTab />
        </TabsContent>

        <TabsContent value="consents" className="mt-6">
          <ConsentsTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}

// =============================================================================
// Framework Card
// =============================================================================

function FrameworkCard({
  framework,
  icon: Icon,
}: {
  framework: ComplianceFramework;
  icon: React.ComponentType<{ className?: string }>;
}) {
  const statusColors = {
    compliant: 'text-green-500',
    partial: 'text-yellow-500',
    non_compliant: 'text-red-500',
  };

  const statusLabels = {
    compliant: 'Compliant',
    partial: 'Partial',
    non_compliant: 'Non-Compliant',
  };

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Icon className={cn('h-5 w-5', statusColors[framework.status])} />
            <span className="font-semibold">{framework.name}</span>
          </div>
          <Badge
            variant={framework.status === 'compliant' ? 'default' : 'secondary'}
            className={cn(
              framework.status === 'compliant' && 'bg-green-500',
              framework.status === 'partial' && 'bg-yellow-500',
              framework.status === 'non_compliant' && 'bg-red-500'
            )}
          >
            {statusLabels[framework.status]}
          </Badge>
        </div>
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Score</span>
            <span className="font-medium">{framework.score}%</span>
          </div>
          <Progress value={framework.score} className="h-2" />
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Controls</span>
            <span className="font-medium">
              {framework.controls_passed}/{framework.controls_total} passed
            </span>
          </div>
        </div>
        {framework.findings.length > 0 && (
          <div className="mt-4 pt-4 border-t">
            <p className="text-sm text-muted-foreground">
              {framework.findings.filter((f) => f.status === 'open').length} open findings
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// =============================================================================
// Overview Tab
// =============================================================================

function OverviewTab({ status }: { status: ComplianceStatus }) {
  const allFindings = [
    ...status.gdpr.findings,
    ...status.soc2.findings,
    ...status.hipaa.findings,
    ...status.ccpa.findings,
  ].filter((f) => f.status === 'open');

  const criticalFindings = allFindings.filter((f) => f.severity === 'critical');
  const highFindings = allFindings.filter((f) => f.severity === 'high');

  return (
    <div className="space-y-6">
      {/* Alerts */}
      {criticalFindings.length > 0 && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Critical Findings</AlertTitle>
          <AlertDescription>
            There are {criticalFindings.length} critical compliance findings that require
            immediate attention.
          </AlertDescription>
        </Alert>
      )}

      {highFindings.length > 0 && (
        <Alert>
          <ShieldAlert className="h-4 w-4" />
          <AlertTitle>High Priority Findings</AlertTitle>
          <AlertDescription>
            {highFindings.length} high priority findings need to be addressed soon.
          </AlertDescription>
        </Alert>
      )}

      {/* Findings Table */}
      <Card>
        <CardHeader>
          <CardTitle>Open Findings</CardTitle>
          <CardDescription>
            Compliance issues that need to be addressed
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Severity</TableHead>
                <TableHead>Title</TableHead>
                <TableHead>Framework</TableHead>
                <TableHead>Due Date</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {allFindings.slice(0, 10).map((finding) => (
                <TableRow key={finding.id}>
                  <TableCell>
                    <SeverityBadge severity={finding.severity} />
                  </TableCell>
                  <TableCell className="font-medium">{finding.title}</TableCell>
                  <TableCell>GDPR</TableCell>
                  <TableCell>{new Date(finding.due_date).toLocaleDateString()}</TableCell>
                  <TableCell>
                    <StatusBadge status={finding.status} />
                  </TableCell>
                  <TableCell>
                    <Button variant="ghost" size="sm">
                      <Eye className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
              {allFindings.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8">
                    <CheckCircle2 className="h-8 w-8 mx-auto text-green-500 mb-2" />
                    <p className="text-muted-foreground">No open findings</p>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}

// =============================================================================
// DSR Tab
// =============================================================================

function DSRTab() {
  const { data: requests = [], isLoading } = useDataSubjectRequests();
  const processDSR = useProcessDSR();

  const pendingRequests = requests.filter((r) => r.status === 'pending');
  const overdueRequests = requests.filter(
    (r) => r.status === 'pending' && new Date(r.due_date) < new Date()
  );

  if (isLoading) {
    return <div className="animate-pulse h-64 bg-muted rounded-lg" />;
  }

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-2 rounded-lg bg-blue-500/20">
                <Clock className="h-5 w-5 text-blue-500" />
              </div>
              <div>
                <p className="text-2xl font-bold">{pendingRequests.length}</p>
                <p className="text-sm text-muted-foreground">Pending</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-2 rounded-lg bg-red-500/20">
                <AlertTriangle className="h-5 w-5 text-red-500" />
              </div>
              <div>
                <p className="text-2xl font-bold">{overdueRequests.length}</p>
                <p className="text-sm text-muted-foreground">Overdue</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-2 rounded-lg bg-green-500/20">
                <CheckCircle2 className="h-5 w-5 text-green-500" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {requests.filter((r) => r.status === 'completed').length}
                </p>
                <p className="text-sm text-muted-foreground">Completed</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-2 rounded-lg bg-gray-500/20">
                <FileText className="h-5 w-5 text-gray-500" />
              </div>
              <div>
                <p className="text-2xl font-bold">{requests.length}</p>
                <p className="text-sm text-muted-foreground">Total</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Requests Table */}
      <Card>
        <CardHeader>
          <CardTitle>Data Subject Requests</CardTitle>
          <CardDescription>
            GDPR Article 15-22 requests from data subjects
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Type</TableHead>
                <TableHead>Subject</TableHead>
                <TableHead>Submitted</TableHead>
                <TableHead>Due Date</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {requests.map((request) => (
                <TableRow key={request.id}>
                  <TableCell>
                    <DSRTypeBadge type={request.type} />
                  </TableCell>
                  <TableCell>
                    <div>
                      <p className="font-medium">{request.subject_name}</p>
                      <p className="text-sm text-muted-foreground">
                        {request.subject_email}
                      </p>
                    </div>
                  </TableCell>
                  <TableCell>
                    {new Date(request.submitted_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <span
                      className={cn(
                        new Date(request.due_date) < new Date() &&
                          request.status === 'pending' &&
                          'text-red-500 font-medium'
                      )}
                    >
                      {new Date(request.due_date).toLocaleDateString()}
                    </span>
                  </TableCell>
                  <TableCell>
                    <DSRStatusBadge status={request.status} />
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {request.status === 'pending' && (
                        <>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() =>
                              processDSR.mutate({ id: request.id, action: 'approve' })
                            }
                            disabled={processDSR.isPending}
                          >
                            Process
                          </Button>
                        </>
                      )}
                      <Button variant="ghost" size="icon">
                        <Eye className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
              {requests.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8">
                    <FileText className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
                    <p className="text-muted-foreground">No data subject requests</p>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}

// =============================================================================
// Audit Logs Tab
// =============================================================================

function AuditLogsTab() {
  const { data: logs = [], isLoading } = useAuditLogs();

  if (isLoading) {
    return <div className="animate-pulse h-64 bg-muted rounded-lg" />;
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Audit Logs</CardTitle>
            <CardDescription>
              Complete audit trail of system activities
            </CardDescription>
          </div>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[500px]">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Timestamp</TableHead>
                <TableHead>User</TableHead>
                <TableHead>Action</TableHead>
                <TableHead>Resource</TableHead>
                <TableHead>IP Address</TableHead>
                <TableHead>Risk</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {logs.map((log) => (
                <TableRow key={log.id}>
                  <TableCell className="font-mono text-sm">
                    {new Date(log.timestamp).toLocaleString()}
                  </TableCell>
                  <TableCell>{log.user}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{log.action}</Badge>
                  </TableCell>
                  <TableCell className="max-w-[200px] truncate">
                    {log.resource}
                  </TableCell>
                  <TableCell className="font-mono text-sm">{log.ip_address}</TableCell>
                  <TableCell>
                    <RiskBadge level={log.risk_level} />
                  </TableCell>
                </TableRow>
              ))}
              {logs.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8">
                    <History className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
                    <p className="text-muted-foreground">No audit logs</p>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}

// =============================================================================
// Consents Tab
// =============================================================================

function ConsentsTab() {
  const { data: consents = [], isLoading } = useConsentRecords();

  if (isLoading) {
    return <div className="animate-pulse h-64 bg-muted rounded-lg" />;
  }

  const activeConsents = consents.filter((c) => c.status === 'active');
  const withdrawnConsents = consents.filter((c) => c.status === 'withdrawn');

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-2 rounded-lg bg-green-500/20">
                <CheckCircle2 className="h-5 w-5 text-green-500" />
              </div>
              <div>
                <p className="text-2xl font-bold">{activeConsents.length}</p>
                <p className="text-sm text-muted-foreground">Active Consents</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-2 rounded-lg bg-red-500/20">
                <XCircle className="h-5 w-5 text-red-500" />
              </div>
              <div>
                <p className="text-2xl font-bold">{withdrawnConsents.length}</p>
                <p className="text-sm text-muted-foreground">Withdrawn</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-2 rounded-lg bg-blue-500/20">
                <FileText className="h-5 w-5 text-blue-500" />
              </div>
              <div>
                <p className="text-2xl font-bold">{consents.length}</p>
                <p className="text-sm text-muted-foreground">Total Records</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Consents Table */}
      <Card>
        <CardHeader>
          <CardTitle>Consent Records</CardTitle>
          <CardDescription>
            Track and manage user consent for data processing
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Contact</TableHead>
                <TableHead>Consent Type</TableHead>
                <TableHead>Given At</TableHead>
                <TableHead>Expires</TableHead>
                <TableHead>Source</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {consents.map((consent) => (
                <TableRow key={consent.id}>
                  <TableCell>
                    <div>
                      <p className="font-medium">{consent.contact_name}</p>
                      <p className="text-sm text-muted-foreground">
                        {consent.contact_email}
                      </p>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{consent.consent_type}</Badge>
                  </TableCell>
                  <TableCell>
                    {new Date(consent.given_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    {consent.expires_at
                      ? new Date(consent.expires_at).toLocaleDateString()
                      : 'Never'}
                  </TableCell>
                  <TableCell>{consent.source}</TableCell>
                  <TableCell>
                    <ConsentStatusBadge status={consent.status} />
                  </TableCell>
                </TableRow>
              ))}
              {consents.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8">
                    <FileText className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
                    <p className="text-muted-foreground">No consent records</p>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}

// =============================================================================
// Badge Components
// =============================================================================

function SeverityBadge({ severity }: { severity: string }) {
  const variants: Record<string, string> = {
    critical: 'bg-red-500 text-white',
    high: 'bg-orange-500 text-white',
    medium: 'bg-yellow-500 text-black dark:text-white',
    low: 'bg-blue-500 text-white',
  };

  return (
    <Badge className={variants[severity] || variants.low}>
      {severity.charAt(0).toUpperCase() + severity.slice(1)}
    </Badge>
  );
}

function StatusBadge({ status }: { status: string }) {
  const variants: Record<string, { variant: 'default' | 'secondary' | 'outline'; icon: React.ReactNode }> = {
    open: { variant: 'secondary', icon: <Clock className="h-3 w-3 mr-1" /> },
    in_progress: { variant: 'default', icon: <RefreshCw className="h-3 w-3 mr-1" /> },
    resolved: { variant: 'outline', icon: <CheckCircle2 className="h-3 w-3 mr-1" /> },
  };

  const config = variants[status] || variants.open;

  return (
    <Badge variant={config.variant} className="flex items-center w-fit">
      {config.icon}
      {status.replace('_', ' ')}
    </Badge>
  );
}

function DSRTypeBadge({ type }: { type: string }) {
  const icons: Record<string, React.ReactNode> = {
    access: <Eye className="h-3 w-3 mr-1" />,
    rectification: <PenLine className="h-3 w-3 mr-1" />,
    erasure: <Trash2 className="h-3 w-3 mr-1" />,
    portability: <Download className="h-3 w-3 mr-1" />,
    restriction: <Lock className="h-3 w-3 mr-1" />,
  };

  return (
    <Badge variant="outline" className="flex items-center w-fit">
      {icons[type]}
      {type.charAt(0).toUpperCase() + type.slice(1)}
    </Badge>
  );
}

function DSRStatusBadge({ status }: { status: string }) {
  const variants: Record<string, string> = {
    pending: 'bg-yellow-500',
    in_progress: 'bg-blue-500',
    completed: 'bg-green-500',
    rejected: 'bg-red-500',
  };

  return (
    <Badge className={cn('text-white', variants[status] || variants.pending)}>
      {status.replace('_', ' ')}
    </Badge>
  );
}

function RiskBadge({ level }: { level: string }) {
  const variants: Record<string, string> = {
    high: 'bg-red-500 text-white',
    medium: 'bg-yellow-500 text-black dark:text-white',
    low: 'bg-green-500 text-white',
  };

  return (
    <Badge className={variants[level] || variants.low}>
      {level.charAt(0).toUpperCase() + level.slice(1)}
    </Badge>
  );
}

function ConsentStatusBadge({ status }: { status: string }) {
  const variants: Record<string, { class: string; icon: React.ReactNode }> = {
    active: { class: 'bg-green-500 text-white', icon: <CheckCircle2 className="h-3 w-3 mr-1" /> },
    withdrawn: { class: 'bg-red-500 text-white', icon: <XCircle className="h-3 w-3 mr-1" /> },
    expired: { class: 'bg-gray-500 text-white', icon: <Clock className="h-3 w-3 mr-1" /> },
  };

  const config = variants[status] || variants.active;

  return (
    <Badge className={cn('flex items-center w-fit', config.class)}>
      {config.icon}
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </Badge>
  );
}

export default ComplianceDashboard;
