'use client';

import { useState, useEffect } from 'react';
import { 
  Shield,
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  Monitor, 
  Smartphone, 
  Globe, 
  Clock,
  Eye,
  Download,
  Plus,
  Search,
  Filter,
  RefreshCw,
  Trash2,
  Settings,
  Users,
  FileText,
  Activity,
  MapPin,
  LogOut,
  Ban,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
// import { ScrollArea } from '@/components/ui/scroll-area';
import { Progress } from '@/components/ui/progress';
import { Switch } from '@/components/ui/switch';
// import { Label } from '@/components/ui/label';
// import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
// import { Textarea } from '@/components/ui/textarea';
import { enterpriseSecurityAPI } from '@/lib/api';

interface SecurityDashboard {
  risk_score: number;
  active_sessions: number;
  trusted_devices: number;
  blocked_attempts: number;
  policy_compliance: number;
  recent_threats: number;
}

interface Device {
  id: string;
  name: string;
  type: 'desktop' | 'mobile' | 'tablet';
  os: string;
  browser: string;
  ip_address: string;
  location: string;
  last_active: string;
  is_trusted: boolean;
  is_current: boolean;
}

interface Session {
  id: string;
  device: string;
  ip_address: string;
  location: string;
  started_at: string;
  last_activity: string;
  is_current: boolean;
}

interface AuditLog {
  id: string;
  action: string;
  user: string;
  resource: string;
  ip_address: string;
  timestamp: string;
  status: 'success' | 'failure' | 'warning';
  details: string;
}

interface AccessPolicy {
  id: string;
  name: string;
  description: string;
  type: 'ip_restriction' | 'time_restriction' | 'mfa_required' | 'role_based';
  is_active: boolean;
  affected_users: number;
  rules: Record<string, unknown>;
}

interface Threat {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  source: string;
  description: string;
  detected_at: string;
  status: 'active' | 'investigating' | 'resolved';
}

interface Incident {
  id: string;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'investigating' | 'resolved' | 'closed';
  created_at: string;
  resolved_at: string | null;
  assigned_to: string;
}

export default function EnterpriseSecurityPage() {
  const [dashboard, setDashboard] = useState<SecurityDashboard | null>(null);
  const [devices, setDevices] = useState<Device[]>([]);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [policies, setPolicies] = useState<AccessPolicy[]>([]);
  const [threats, setThreats] = useState<Threat[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [, setIsLoading] = useState(true);
  const [] = useState('');
  const [selectedDateRange, setSelectedDateRange] = useState('7d');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [dashData, devicesData, sessionsData, logsData, policiesData, threatsData, incidentsData] = await Promise.all([
        enterpriseSecurityAPI.getDashboard(),
        enterpriseSecurityAPI.getDevices(),
        enterpriseSecurityAPI.getSessions(),
        enterpriseSecurityAPI.getAuditLogs(),
        enterpriseSecurityAPI.getPolicies(),
        enterpriseSecurityAPI.getThreats(),
        enterpriseSecurityAPI.getIncidents(),
      ]);
      setDashboard(dashData);
      setDevices(devicesData.results || devicesData || []);
      setSessions(sessionsData.results || sessionsData || []);
      setAuditLogs(logsData.results || logsData || []);
      setPolicies(policiesData.results || policiesData || []);
      setThreats(threatsData.results || threatsData || []);
      setIncidents(incidentsData.results || incidentsData || []);
    } catch (error) {
      console.error('Failed to load data:', error);
      // Demo data
      setDashboard({
        risk_score: 25,
        active_sessions: 8,
        trusted_devices: 12,
        blocked_attempts: 45,
        policy_compliance: 94,
        recent_threats: 3,
      });
      setDevices([
        { id: '1', name: 'MacBook Pro', type: 'desktop', os: 'macOS 14.2', browser: 'Chrome 120', ip_address: '192.168.1.100', location: 'New York, US', last_active: '2026-01-12T14:30:00Z', is_trusted: true, is_current: true },
        { id: '2', name: 'iPhone 15', type: 'mobile', os: 'iOS 17.2', browser: 'Safari', ip_address: '192.168.1.101', location: 'New York, US', last_active: '2026-01-12T10:00:00Z', is_trusted: true, is_current: false },
        { id: '3', name: 'Windows PC', type: 'desktop', os: 'Windows 11', browser: 'Edge 120', ip_address: '10.0.0.50', location: 'Boston, US', last_active: '2026-01-11T16:00:00Z', is_trusted: true, is_current: false },
        { id: '4', name: 'Android Tablet', type: 'tablet', os: 'Android 14', browser: 'Chrome', ip_address: '192.168.2.55', location: 'Chicago, US', last_active: '2026-01-10T09:00:00Z', is_trusted: false, is_current: false },
      ]);
      setSessions([
        { id: '1', device: 'MacBook Pro - Chrome', ip_address: '192.168.1.100', location: 'New York, US', started_at: '2026-01-12T08:00:00Z', last_activity: '2026-01-12T14:30:00Z', is_current: true },
        { id: '2', device: 'iPhone 15 - Safari', ip_address: '192.168.1.101', location: 'New York, US', started_at: '2026-01-12T09:00:00Z', last_activity: '2026-01-12T10:00:00Z', is_current: false },
        { id: '3', device: 'Windows PC - Edge', ip_address: '10.0.0.50', location: 'Boston, US', started_at: '2026-01-11T14:00:00Z', last_activity: '2026-01-11T16:00:00Z', is_current: false },
      ]);
      setAuditLogs([
        { id: '1', action: 'Login', user: 'john.doe@company.com', resource: 'Auth System', ip_address: '192.168.1.100', timestamp: '2026-01-12T14:30:00Z', status: 'success', details: 'Successful login with MFA' },
        { id: '2', action: 'Password Change', user: 'jane.smith@company.com', resource: 'User Settings', ip_address: '10.0.0.25', timestamp: '2026-01-12T13:00:00Z', status: 'success', details: 'Password updated successfully' },
        { id: '3', action: 'Failed Login', user: 'unknown@attacker.com', resource: 'Auth System', ip_address: '45.33.32.156', timestamp: '2026-01-12T12:30:00Z', status: 'failure', details: 'Invalid credentials - IP blocked' },
        { id: '4', action: 'Data Export', user: 'admin@company.com', resource: 'Contacts', ip_address: '192.168.1.50', timestamp: '2026-01-12T11:00:00Z', status: 'success', details: 'Exported 5000 contacts' },
        { id: '5', action: 'API Access', user: 'integration@company.com', resource: 'API Gateway', ip_address: '52.14.123.45', timestamp: '2026-01-12T10:30:00Z', status: 'warning', details: 'High API usage detected' },
      ]);
      setPolicies([
        { id: '1', name: 'MFA Required for Admins', description: 'All admin users must use multi-factor authentication', type: 'mfa_required', is_active: true, affected_users: 5, rules: {} },
        { id: '2', name: 'Office Hours Only', description: 'Restrict access to business hours (9 AM - 6 PM)', type: 'time_restriction', is_active: false, affected_users: 50, rules: {} },
        { id: '3', name: 'US Only Access', description: 'Block access from outside United States', type: 'ip_restriction', is_active: true, affected_users: 100, rules: {} },
        { id: '4', name: 'Finance Team Access', description: 'Restrict financial data to finance team only', type: 'role_based', is_active: true, affected_users: 8, rules: {} },
      ]);
      setThreats([
        { id: '1', type: 'Brute Force Attack', severity: 'high', source: '45.33.32.156', description: 'Multiple failed login attempts detected', detected_at: '2026-01-12T12:30:00Z', status: 'resolved' },
        { id: '2', type: 'Suspicious API Activity', severity: 'medium', source: 'api-key-xyz123', description: 'Unusual API request patterns detected', detected_at: '2026-01-12T10:00:00Z', status: 'investigating' },
        { id: '3', type: 'New Device Login', severity: 'low', source: 'user: jane.smith', description: 'Login from new device in different location', detected_at: '2026-01-11T15:00:00Z', status: 'resolved' },
      ]);
      setIncidents([
        { id: '1', title: 'Unauthorized Access Attempt', description: 'Multiple failed login attempts from suspicious IP', severity: 'high', status: 'resolved', created_at: '2026-01-12T12:30:00Z', resolved_at: '2026-01-12T13:00:00Z', assigned_to: 'Security Team' },
        { id: '2', title: 'Data Export Alert', description: 'Large data export detected - under review', severity: 'medium', status: 'investigating', created_at: '2026-01-12T11:00:00Z', resolved_at: null, assigned_to: 'Admin' },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const trustDevice = async (deviceId: string) => {
    try {
      await enterpriseSecurityAPI.trustDevice(deviceId);
      setDevices(devices.map(d => d.id === deviceId ? { ...d, is_trusted: true } : d));
    } catch (error) {
      console.error('Failed to trust device:', error);
      setDevices(devices.map(d => d.id === deviceId ? { ...d, is_trusted: true } : d));
    }
  };

  const blockDevice = async (deviceId: string) => {
    try {
      await enterpriseSecurityAPI.blockDevice(deviceId);
      setDevices(devices.filter(d => d.id !== deviceId));
    } catch (error) {
      console.error('Failed to block device:', error);
    }
  };

  const terminateSession = async (sessionId: string) => {
    try {
      await enterpriseSecurityAPI.terminateSession(sessionId);
      setSessions(sessions.filter(s => s.id !== sessionId));
    } catch (error) {
      console.error('Failed to terminate session:', error);
      setSessions(sessions.filter(s => s.id !== sessionId));
    }
  };

  const terminateAllSessions = async () => {
    try {
      await enterpriseSecurityAPI.terminateAllSessions();
      setSessions(sessions.filter(s => s.is_current));
    } catch (error) {
      console.error('Failed to terminate all sessions:', error);
    }
  };

  const togglePolicy = (policyId: string) => {
    setPolicies(policies.map(p => 
      p.id === policyId ? { ...p, is_active: !p.is_active } : p
    ));
  };

  const getSeverityBadge = (severity: string) => {
    const styles: Record<string, string> = {
      'low': 'bg-blue-100 text-blue-700',
      'medium': 'bg-yellow-100 text-yellow-700',
      'high': 'bg-orange-100 text-orange-700',
      'critical': 'bg-red-100 text-red-700',
    };
    return <Badge className={styles[severity]}>{severity}</Badge>;
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      'success': 'bg-green-100 text-green-700',
      'failure': 'bg-red-100 text-red-700',
      'warning': 'bg-yellow-100 text-yellow-700',
      'active': 'bg-red-100 text-red-700',
      'investigating': 'bg-yellow-100 text-yellow-700',
      'resolved': 'bg-green-100 text-green-700',
      'open': 'bg-blue-100 text-blue-700',
      'closed': 'bg-gray-100 text-gray-700',
    };
    return <Badge className={styles[status] || 'bg-gray-100'}>{status}</Badge>;
  };

  const getDeviceIcon = (type: string) => {
    switch (type) {
      case 'mobile':
        return <Smartphone className="h-5 w-5" />;
      case 'tablet':
        return <Monitor className="h-5 w-5" />;
      default:
        return <Monitor className="h-5 w-5" />;
    }
  };

  const getRiskColor = (score: number) => {
    if (score <= 30) return 'text-green-500';
    if (score <= 60) return 'text-yellow-500';
    if (score <= 80) return 'text-orange-500';
    return 'text-red-500';
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Shield className="h-8 w-8" />
            Enterprise Security
          </h1>
          <p className="text-muted-foreground">
            Monitor and manage security across your organization
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Select value={selectedDateRange} onValueChange={setSelectedDateRange}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="24h">Last 24 hours</SelectItem>
              <SelectItem value="7d">Last 7 days</SelectItem>
              <SelectItem value="30d">Last 30 days</SelectItem>
              <SelectItem value="90d">Last 90 days</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" onClick={loadData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Dashboard Cards */}
      <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Risk Score</p>
                <p className={`text-3xl font-bold ${getRiskColor(dashboard?.risk_score || 0)}`}>
                  {dashboard?.risk_score || 0}
                </p>
              </div>
              <div className={`rounded-full p-3 ${(dashboard?.risk_score || 0) <= 30 ? 'bg-green-100' : 'bg-yellow-100'}`}>
                <Shield className={`h-6 w-6 ${(dashboard?.risk_score || 0) <= 30 ? 'text-green-600' : 'text-yellow-600'}`} />
              </div>
            </div>
            <Progress value={100 - (dashboard?.risk_score || 0)} className="mt-4" />
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Active Sessions</p>
                <p className="text-3xl font-bold">{dashboard?.active_sessions || 0}</p>
              </div>
              <div className="bg-blue-100 rounded-full p-3">
                <Activity className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Trusted Devices</p>
                <p className="text-3xl font-bold">{dashboard?.trusted_devices || 0}</p>
              </div>
              <div className="bg-green-100 rounded-full p-3">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Blocked Attempts</p>
                <p className="text-3xl font-bold">{dashboard?.blocked_attempts || 0}</p>
              </div>
              <div className="bg-red-100 rounded-full p-3">
                <Ban className="h-6 w-6 text-red-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Policy Compliance</p>
                <p className="text-3xl font-bold">{dashboard?.policy_compliance || 0}%</p>
              </div>
              <div className="bg-purple-100 rounded-full p-3">
                <FileText className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Recent Threats</p>
                <p className="text-3xl font-bold">{dashboard?.recent_threats || 0}</p>
              </div>
              <div className="bg-orange-100 rounded-full p-3">
                <AlertTriangle className="h-6 w-6 text-orange-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="devices">
        <TabsList>
          <TabsTrigger value="devices">Devices</TabsTrigger>
          <TabsTrigger value="sessions">Sessions</TabsTrigger>
          <TabsTrigger value="audit">Audit Logs</TabsTrigger>
          <TabsTrigger value="policies">Access Policies</TabsTrigger>
          <TabsTrigger value="threats">Threats</TabsTrigger>
          <TabsTrigger value="incidents">Incidents</TabsTrigger>
        </TabsList>

        <TabsContent value="devices" className="mt-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Registered Devices</CardTitle>
                <div className="flex items-center gap-2">
                  <Input placeholder="Search devices..." className="w-64" />
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {devices.map((device) => (
                  <div key={device.id} className={`flex items-center justify-between p-4 border rounded-lg ${device.is_current ? 'border-primary bg-primary/5' : ''}`}>
                    <div className="flex items-center gap-4">
                      <div className={`rounded-full p-3 ${device.is_trusted ? 'bg-green-100' : 'bg-gray-100'}`}>
                        {getDeviceIcon(device.type)}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="font-medium">{device.name}</p>
                          {device.is_current && <Badge variant="outline">Current</Badge>}
                          {device.is_trusted && <Badge className="bg-green-100 text-green-700">Trusted</Badge>}
                        </div>
                        <p className="text-sm text-muted-foreground">{device.os} • {device.browser}</p>
                        <div className="flex items-center gap-4 mt-1 text-xs text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <Globe className="h-3 w-3" />
                            {device.ip_address}
                          </span>
                          <span className="flex items-center gap-1">
                            <MapPin className="h-3 w-3" />
                            {device.location}
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {new Date(device.last_active).toLocaleString()}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {!device.is_trusted && (
                        <Button variant="outline" size="sm" onClick={() => trustDevice(device.id)}>
                          <CheckCircle2 className="h-4 w-4 mr-1" />
                          Trust
                        </Button>
                      )}
                      {!device.is_current && (
                        <Button variant="ghost" size="sm" onClick={() => blockDevice(device.id)}>
                          <Ban className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="sessions" className="mt-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Active Sessions</CardTitle>
                <Button variant="destructive" size="sm" onClick={terminateAllSessions}>
                  <LogOut className="h-4 w-4 mr-2" />
                  Terminate All Other Sessions
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {sessions.map((session) => (
                  <div key={session.id} className={`flex items-center justify-between p-4 border rounded-lg ${session.is_current ? 'border-primary bg-primary/5' : ''}`}>
                    <div className="flex items-center gap-4">
                      <div className="bg-blue-100 rounded-full p-3">
                        <Activity className="h-5 w-5 text-blue-600" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="font-medium">{session.device}</p>
                          {session.is_current && <Badge variant="outline">Current Session</Badge>}
                        </div>
                        <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <Globe className="h-3 w-3" />
                            {session.ip_address}
                          </span>
                          <span className="flex items-center gap-1">
                            <MapPin className="h-3 w-3" />
                            {session.location}
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">
                          Started: {new Date(session.started_at).toLocaleString()} • 
                          Last active: {new Date(session.last_activity).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    {!session.is_current && (
                      <Button variant="ghost" size="sm" onClick={() => terminateSession(session.id)}>
                        <LogOut className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="audit" className="mt-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Audit Logs</CardTitle>
                <div className="flex items-center gap-2">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input placeholder="Search logs..." className="pl-10 w-64" />
                  </div>
                  <Button variant="outline" size="sm">
                    <Filter className="h-4 w-4 mr-2" />
                    Filter
                  </Button>
                  <Button variant="outline" size="sm">
                    <Download className="h-4 w-4 mr-2" />
                    Export
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {auditLogs.map((log) => (
                  <div key={log.id} className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50">
                    <div className="flex items-center gap-4">
                      <div className={`rounded-full p-2 ${
                        log.status === 'success' ? 'bg-green-100' :
                        log.status === 'failure' ? 'bg-red-100' : 'bg-yellow-100'
                      }`}>
                        {log.status === 'success' ? <CheckCircle className="h-4 w-4 text-green-600" /> :
                         log.status === 'failure' ? <XCircle className="h-4 w-4 text-red-600" /> :
                         <AlertCircle className="h-4 w-4 text-yellow-600" />}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="font-medium">{log.action}</p>
                          {getStatusBadge(log.status)}
                        </div>
                        <p className="text-sm text-muted-foreground">{log.user} • {log.resource}</p>
                        <p className="text-xs text-muted-foreground">{log.details}</p>
                      </div>
                    </div>
                    <div className="text-right text-sm text-muted-foreground">
                      <p>{new Date(log.timestamp).toLocaleString()}</p>
                      <p className="text-xs">{log.ip_address}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="policies" className="mt-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Access Policies</CardTitle>
                <Button size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  Create Policy
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {policies.map((policy) => (
                  <div key={policy.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center gap-4">
                      <Switch checked={policy.is_active} onCheckedChange={() => togglePolicy(policy.id)} />
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="font-medium">{policy.name}</p>
                          <Badge variant="outline">{policy.type.replace('_', ' ')}</Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">{policy.description}</p>
                        <p className="text-xs text-muted-foreground mt-1">
                          <Users className="h-3 w-3 inline mr-1" />
                          Affects {policy.affected_users} users
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button variant="outline" size="sm">
                        <Settings className="h-4 w-4 mr-1" />
                        Configure
                      </Button>
                      <Button variant="ghost" size="sm">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="threats" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Threat Detection</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {threats.map((threat) => (
                  <div key={threat.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center gap-4">
                      <div className={`rounded-full p-3 ${
                        threat.severity === 'critical' ? 'bg-red-100' :
                        threat.severity === 'high' ? 'bg-orange-100' :
                        threat.severity === 'medium' ? 'bg-yellow-100' : 'bg-blue-100'
                      }`}>
                        <AlertTriangle className={`h-5 w-5 ${
                          threat.severity === 'critical' ? 'text-red-600' :
                          threat.severity === 'high' ? 'text-orange-600' :
                          threat.severity === 'medium' ? 'text-yellow-600' : 'text-blue-600'
                        }`} />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="font-medium">{threat.type}</p>
                          {getSeverityBadge(threat.severity)}
                          {getStatusBadge(threat.status)}
                        </div>
                        <p className="text-sm text-muted-foreground">{threat.description}</p>
                        <p className="text-xs text-muted-foreground mt-1">
                          Source: {threat.source} • Detected: {new Date(threat.detected_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {threat.status !== 'resolved' && (
                        <Button variant="outline" size="sm">
                          Investigate
                        </Button>
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
        </TabsContent>

        <TabsContent value="incidents" className="mt-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Security Incidents</CardTitle>
                <Button size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  Report Incident
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {incidents.map((incident) => (
                  <div key={incident.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center gap-4">
                      <div className={`rounded-full p-3 ${
                        incident.status === 'open' ? 'bg-blue-100' :
                        incident.status === 'investigating' ? 'bg-yellow-100' : 'bg-green-100'
                      }`}>
                        <AlertCircle className={`h-5 w-5 ${
                          incident.status === 'open' ? 'text-blue-600' :
                          incident.status === 'investigating' ? 'text-yellow-600' : 'text-green-600'
                        }`} />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="font-medium">{incident.title}</p>
                          {getSeverityBadge(incident.severity)}
                          {getStatusBadge(incident.status)}
                        </div>
                        <p className="text-sm text-muted-foreground">{incident.description}</p>
                        <p className="text-xs text-muted-foreground mt-1">
                          Assigned to: {incident.assigned_to} • Created: {new Date(incident.created_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button variant="outline" size="sm">View Details</Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

