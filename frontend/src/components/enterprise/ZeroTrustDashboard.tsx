'use client';

import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
// import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
// import { Label } from '@/components/ui/label';
import { 
  Shield, 
  Smartphone,
  Laptop,
  Globe,
  Lock,
  Unlock,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  MapPin,
  Fingerprint,
  Settings,
  Trash2
} from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { formatDistanceToNow } from 'date-fns';

// Types
interface TrustedDevice {
  id: string;
  device_name: string;
  device_type: string;
  trust_level: string;
  is_trusted: boolean;
  last_activity_at: string;
  last_ip_address: string;
  login_count: number;
  os_name?: string;
  browser_name?: string;
  verified_at?: string;
}

interface SecuritySession {
  id: string;
  ip_address: string;
  status: string;
  auth_method: string;
  mfa_verified: boolean;
  auth_strength: number;
  risk_score: number;
  risk_factors: string[];
  started_at: string;
  last_activity_at: string;
  geo_city?: string;
  geo_country?: string;
}

interface AccessPolicy {
  id: string;
  name: string;
  description: string;
  effect: 'allow' | 'deny';
  is_active: boolean;
  priority: number;
  conditions: {
    roles?: string[];
    ip_ranges?: string[];
    mfa_required?: boolean;
    device_trust?: string;
  };
  resource_patterns: string[];
}

// Mock API functions - replace with actual API calls
const api = {
  getTrustedDevices: async (): Promise<TrustedDevice[]> => {
    // Simulated API response
    return [
      {
        id: '1',
        device_name: 'Chrome on MacBook Pro',
        device_type: 'laptop',
        trust_level: 'verified',
        is_trusted: true,
        last_activity_at: new Date().toISOString(),
        last_ip_address: '192.168.1.100',
        login_count: 45,
        os_name: 'macOS',
        browser_name: 'Chrome',
        verified_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: '2',
        device_name: 'Safari on iPhone',
        device_type: 'mobile',
        trust_level: 'basic',
        is_trusted: true,
        last_activity_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        last_ip_address: '192.168.1.101',
        login_count: 12,
        os_name: 'iOS',
        browser_name: 'Safari',
      },
    ];
  },
  getActiveSessions: async (): Promise<SecuritySession[]> => {
    return [
      {
        id: '1',
        ip_address: '192.168.1.100',
        status: 'active',
        auth_method: 'password',
        mfa_verified: true,
        auth_strength: 4,
        risk_score: 15,
        risk_factors: [],
        started_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        last_activity_at: new Date().toISOString(),
        geo_city: 'San Francisco',
        geo_country: 'US',
      },
    ];
  },
  getAccessPolicies: async (): Promise<AccessPolicy[]> => {
    return [
      {
        id: '1',
        name: 'Admin Access Policy',
        description: 'Require MFA and trusted device for admin access',
        effect: 'allow',
        is_active: true,
        priority: 100,
        conditions: {
          roles: ['admin'],
          mfa_required: true,
          device_trust: 'verified',
        },
        resource_patterns: ['/api/admin/*', '/settings/*'],
      },
      {
        id: '2',
        name: 'Block External Access to Exports',
        description: 'Block data exports from external IPs',
        effect: 'deny',
        is_active: true,
        priority: 90,
        conditions: {
          ip_ranges: ['!10.0.0.0/8', '!192.168.0.0/16'],
        },
        resource_patterns: ['/api/*/export', '/api/reports/download/*'],
      },
    ];
  },
  revokeDevice: async (deviceId: string): Promise<void> => {
    console.log('Revoking device:', deviceId);
  },
  terminateSession: async (sessionId: string): Promise<void> => {
    console.log('Terminating session:', sessionId);
  },
  verifyDevice: async (deviceId: string): Promise<void> => {
    console.log('Verifying device:', deviceId);
  },
};

// Device Icon Component
const DeviceIcon: React.FC<{ type: string }> = ({ type }) => {
  switch (type) {
    case 'mobile':
      return <Smartphone className="h-5 w-5" />;
    case 'laptop':
    case 'desktop':
      return <Laptop className="h-5 w-5" />;
    default:
      return <Globe className="h-5 w-5" />;
  }
};

// Trust Level Badge Component
const TrustLevelBadge: React.FC<{ level: string; isTrusted: boolean }> = ({ level, isTrusted }) => {
  if (!isTrusted) {
    return <Badge variant="destructive">Untrusted</Badge>;
  }
  
  const variants: Record<string, { color: string; label: string }> = {
    verified: { color: 'bg-green-100 text-green-800', label: 'Verified' },
    basic: { color: 'bg-blue-100 text-blue-800', label: 'Basic Trust' },
    corporate: { color: 'bg-purple-100 text-purple-800', label: 'Corporate' },
  };
  
  const variant = variants[level] || { color: 'bg-gray-100 text-gray-800', label: level };
  
  return (
    <Badge className={variant.color}>
      {variant.label}
    </Badge>
  );
};

// Auth Strength Indicator Component
const AuthStrengthIndicator: React.FC<{ strength: number }> = ({ strength }) => {
  const bars = [1, 2, 3, 4, 5];
  
  return (
    <div className="flex items-center gap-1">
      {bars.map((bar) => (
        <div
          key={bar}
          className={`h-3 w-1.5 rounded-sm ${
            bar <= strength
              ? strength >= 4
                ? 'bg-green-500'
                : strength >= 2
                ? 'bg-yellow-500'
                : 'bg-red-500'
              : 'bg-gray-200'
          }`}
        />
      ))}
      <span className="ml-2 text-xs text-gray-500">{strength}/5</span>
    </div>
  );
};

// Trusted Devices Tab Component
const TrustedDevicesTab: React.FC = () => {
  const queryClient = useQueryClient();
  
  const { data: devices, isLoading } = useQuery({
    queryKey: ['trusted-devices'],
    queryFn: api.getTrustedDevices,
  });

  const revokeMutation = useMutation({
    mutationFn: api.revokeDevice,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trusted-devices'] });
    },
  });

  const verifyMutation = useMutation({
    mutationFn: api.verifyDevice,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trusted-devices'] });
    },
  });

  if (isLoading) {
    return <div className="flex justify-center p-8">Loading devices...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-medium">Trusted Devices</h3>
          <p className="text-sm text-muted-foreground">
            Manage devices that are trusted for accessing your account
          </p>
        </div>
        <Button variant="outline" size="sm">
          <Fingerprint className="h-4 w-4 mr-2" />
          Register New Device
        </Button>
      </div>

      <div className="space-y-3">
        {devices?.map((device) => (
          <Card key={device.id}>
            <CardContent className="p-4">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-gray-100 rounded-lg">
                    <DeviceIcon type={device.device_type} />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{device.device_name}</span>
                      <TrustLevelBadge level={device.trust_level} isTrusted={device.is_trusted} />
                    </div>
                    <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <MapPin className="h-3 w-3" />
                        {device.last_ip_address}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {formatDistanceToNow(new Date(device.last_activity_at), { addSuffix: true })}
                      </span>
                      <span>{device.login_count} logins</span>
                    </div>
                    {device.os_name && device.browser_name && (
                      <p className="text-xs text-muted-foreground mt-1">
                        {device.browser_name} on {device.os_name}
                      </p>
                    )}
                  </div>
                </div>
                <div className="flex gap-2">
                  {!device.is_trusted && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => verifyMutation.mutate(device.id)}
                      disabled={verifyMutation.isPending}
                    >
                      <CheckCircle className="h-4 w-4 mr-1" />
                      Verify
                    </Button>
                  )}
                  <Button
                    variant="outline"
                    size="sm"
                    className="text-red-600 hover:text-red-700"
                    onClick={() => revokeMutation.mutate(device.id)}
                    disabled={revokeMutation.isPending}
                  >
                    <Trash2 className="h-4 w-4 mr-1" />
                    Revoke
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

// Active Sessions Tab Component
const ActiveSessionsTab: React.FC = () => {
  const queryClient = useQueryClient();
  
  const { data: sessions, isLoading } = useQuery({
    queryKey: ['active-sessions'],
    queryFn: api.getActiveSessions,
  });

  const terminateMutation = useMutation({
    mutationFn: api.terminateSession,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['active-sessions'] });
    },
  });

  if (isLoading) {
    return <div className="flex justify-center p-8">Loading sessions...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-medium">Active Sessions</h3>
          <p className="text-sm text-muted-foreground">
            Monitor and manage your active login sessions
          </p>
        </div>
        <Button variant="destructive" size="sm">
          Terminate All Other Sessions
        </Button>
      </div>

      <div className="space-y-3">
        {sessions?.map((session) => (
          <Card key={session.id}>
            <CardContent className="p-4">
              <div className="flex items-start justify-between">
                <div className="space-y-2">
                  <div className="flex items-center gap-3">
                    <Badge variant={session.status === 'active' ? 'default' : 'secondary'}>
                      {session.status}
                    </Badge>
                    <span className="text-sm font-medium">
                      {session.geo_city}, {session.geo_country}
                    </span>
                    <span className="text-sm text-muted-foreground">
                      IP: {session.ip_address}
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-6">
                    <div>
                      <span className="text-xs text-muted-foreground">Auth Method</span>
                      <p className="text-sm font-medium flex items-center gap-1">
                        {session.auth_method}
                        {session.mfa_verified && (
                          <Shield className="h-3 w-3 text-green-500" />
                        )}
                      </p>
                    </div>
                    
                    <div>
                      <span className="text-xs text-muted-foreground">Auth Strength</span>
                      <AuthStrengthIndicator strength={session.auth_strength} />
                    </div>
                    
                    <div>
                      <span className="text-xs text-muted-foreground">Risk Score</span>
                      <p className={`text-sm font-medium ${
                        session.risk_score > 50 ? 'text-red-600' :
                        session.risk_score > 25 ? 'text-yellow-600' : 'text-green-600'
                      }`}>
                        {session.risk_score}/100
                      </p>
                    </div>
                    
                    <div>
                      <span className="text-xs text-muted-foreground">Started</span>
                      <p className="text-sm">
                        {formatDistanceToNow(new Date(session.started_at), { addSuffix: true })}
                      </p>
                    </div>
                  </div>

                  {session.risk_factors.length > 0 && (
                    <div className="flex gap-2">
                      {session.risk_factors.map((factor) => (
                        <Badge key={factor} variant="outline" className="text-yellow-600">
                          <AlertTriangle className="h-3 w-3 mr-1" />
                          {factor.replace('_', ' ')}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  className="text-red-600 hover:text-red-700"
                  onClick={() => terminateMutation.mutate(session.id)}
                  disabled={terminateMutation.isPending}
                >
                  <XCircle className="h-4 w-4 mr-1" />
                  Terminate
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

// Access Policies Tab Component
const AccessPoliciesTab: React.FC = () => {
  const { data: policies, isLoading } = useQuery({
    queryKey: ['access-policies'],
    queryFn: api.getAccessPolicies,
  });

  if (isLoading) {
    return <div className="flex justify-center p-8">Loading policies...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-medium">Access Policies</h3>
          <p className="text-sm text-muted-foreground">
            Configure micro-segmentation and access control policies
          </p>
        </div>
        <Button size="sm">
          <Settings className="h-4 w-4 mr-2" />
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
                    {policy.effect === 'allow' ? (
                      <Unlock className="h-5 w-5 text-green-500" />
                    ) : (
                      <Lock className="h-5 w-5 text-red-500" />
                    )}
                    <span className="font-medium">{policy.name}</span>
                    <Badge variant={policy.is_active ? 'default' : 'secondary'}>
                      {policy.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                    <Badge variant="outline">Priority: {policy.priority}</Badge>
                  </div>
                  
                  <p className="text-sm text-muted-foreground">{policy.description}</p>
                  
                  <div className="flex flex-wrap gap-2">
                    {policy.conditions.roles && (
                      <Badge variant="outline">
                        Roles: {policy.conditions.roles.join(', ')}
                      </Badge>
                    )}
                    {policy.conditions.mfa_required && (
                      <Badge variant="outline" className="bg-blue-50">
                        MFA Required
                      </Badge>
                    )}
                    {policy.conditions.device_trust && (
                      <Badge variant="outline" className="bg-green-50">
                        Device Trust: {policy.conditions.device_trust}
                      </Badge>
                    )}
                  </div>
                  
                  <div className="text-xs text-muted-foreground">
                    <span className="font-medium">Resources:</span>{' '}
                    {policy.resource_patterns.join(', ')}
                  </div>
                </div>

                <div className="flex items-center gap-4">
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

// Main Zero Trust Dashboard Component
export const ZeroTrustDashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Shield className="h-6 w-6" />
            Zero Trust Security
          </h2>
          <p className="text-muted-foreground">
            Never trust, always verify - manage device trust, sessions, and access policies
          </p>
        </div>
      </div>

      {/* Security Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Trusted Devices</p>
                <p className="text-2xl font-bold">5</p>
              </div>
              <Laptop className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Active Sessions</p>
                <p className="text-2xl font-bold">2</p>
              </div>
              <Globe className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Access Policies</p>
                <p className="text-2xl font-bold">8</p>
              </div>
              <Lock className="h-8 w-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Risk Score</p>
                <p className="text-2xl font-bold text-green-600">Low</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="devices" className="space-y-4">
        <TabsList>
          <TabsTrigger value="devices">Trusted Devices</TabsTrigger>
          <TabsTrigger value="sessions">Active Sessions</TabsTrigger>
          <TabsTrigger value="policies">Access Policies</TabsTrigger>
        </TabsList>

        <TabsContent value="devices">
          <TrustedDevicesTab />
        </TabsContent>

        <TabsContent value="sessions">
          <ActiveSessionsTab />
        </TabsContent>

        <TabsContent value="policies">
          <AccessPoliciesTab />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ZeroTrustDashboard;
