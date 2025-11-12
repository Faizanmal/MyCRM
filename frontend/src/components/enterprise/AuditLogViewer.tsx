// Audit Log Viewer Component
/* eslint-disable @typescript-eslint/no-explicit-any */
'use client';

import React, { useState, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Shield, Search, Filter, AlertTriangle, Info, AlertCircle } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import axios from 'axios';
import { format } from 'date-fns';

interface AuditLog {
  id: string;
  user: {
    id: string;
    username: string;
    email: string;
  };
  action: string;
  model_name: string;
  object_id?: string;
  changes: Record<string, any>;
  ip_address: string;
  user_agent: string;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  timestamp: string;
  metadata?: Record<string, any>;
}

export default function AuditLogViewer() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [actionFilter, setActionFilter] = useState('all');
  const [riskFilter, setRiskFilter] = useState('all');
  const { toast } = useToast();

  const loadLogs = useCallback(async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/core/audit-logs/');
      setLogs(response.data.results || response.data);
    } catch {
      toast({
        title: 'Error',
        description: 'Failed to load audit logs',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  }, [toast]);

  React.useEffect(() => {
    loadLogs();
  }, [loadLogs]);

  const filteredLogs = logs.filter(log => {
    const matchesSearch = searchTerm === '' || 
      log.user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.model_name.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesAction = actionFilter === 'all' || log.action === actionFilter;
    const matchesRisk = riskFilter === 'all' || log.risk_level === riskFilter;

    return matchesSearch && matchesAction && matchesRisk;
  });

  const getRiskBadgeVariant = (risk: string) => {
    switch (risk) {
      case 'critical': return 'destructive';
      case 'high': return 'destructive';
      case 'medium': return 'default';
      default: return 'secondary';
    }
  };

  const getRiskIcon = (risk: string) => {
    switch (risk) {
      case 'critical':
      case 'high':
        return <AlertTriangle className="h-4 w-4" />;
      case 'medium':
        return <AlertCircle className="h-4 w-4" />;
      default:
        return <Info className="h-4 w-4" />;
    }
  };

  const getActionColor = (action: string) => {
    switch (action) {
      case 'create': return 'text-green-600';
      case 'update': return 'text-blue-600';
      case 'delete': return 'text-red-600';
      case 'login': return 'text-purple-600';
      case 'logout': return 'text-gray-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Shield className="h-8 w-8" />
            Audit Log Viewer
          </h1>
          <p className="text-muted-foreground mt-1">Track all system activities and changes</p>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Input
                placeholder="Search logs..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full"
              />
            </div>
            <div>
              <Select value={actionFilter} onValueChange={setActionFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="All Actions" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Actions</SelectItem>
                  <SelectItem value="create">Create</SelectItem>
                  <SelectItem value="update">Update</SelectItem>
                  <SelectItem value="delete">Delete</SelectItem>
                  <SelectItem value="login">Login</SelectItem>
                  <SelectItem value="logout">Logout</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Select value={riskFilter} onValueChange={setRiskFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="All Risk Levels" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Risk Levels</SelectItem>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="critical">Critical</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Audit Logs */}
      <Card>
        <CardHeader>
          <CardTitle>Audit Logs</CardTitle>
          <CardDescription>
            {filteredLogs.length} log entries {searchTerm || actionFilter !== 'all' || riskFilter !== 'all' ? '(filtered)' : ''}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[600px] pr-4">
            <div className="space-y-3">
              {filteredLogs.length > 0 ? (
                filteredLogs.map(log => (
                  <AuditLogItem key={log.id} log={log} />
                ))
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  <Shield className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No audit logs found</p>
                </div>
              )}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
}

// Audit Log Item Component
function AuditLogItem({ log }: { log: AuditLog }) {
  const [expanded, setExpanded] = useState(false);

  const getRiskBadgeVariant = (risk: string) => {
    switch (risk) {
      case 'critical': return 'destructive';
      case 'high': return 'destructive';
      case 'medium': return 'default';
      default: return 'secondary';
    }
  };

  const getRiskIcon = (risk: string) => {
    switch (risk) {
      case 'critical':
      case 'high':
        return <AlertTriangle className="h-4 w-4" />;
      case 'medium':
        return <AlertCircle className="h-4 w-4" />;
      default:
        return <Info className="h-4 w-4" />;
    }
  };

  const getActionColor = (action: string) => {
    switch (action) {
      case 'create': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300';
      case 'update': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300';
      case 'delete': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300';
      case 'login': return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300';
      case 'logout': return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300';
    }
  };

  return (
    <Card className="hover:bg-accent/50 transition-colors">
      <CardContent className="pt-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 space-y-2">
            <div className="flex items-center gap-2 flex-wrap">
              <Badge className={getActionColor(log.action)}>
                {log.action.toUpperCase()}
              </Badge>
              <Badge variant={getRiskBadgeVariant(log.risk_level)}>
                {getRiskIcon(log.risk_level)}
                <span className="ml-1">{log.risk_level.toUpperCase()}</span>
              </Badge>
              <span className="text-sm text-muted-foreground">
                {log.model_name}
              </span>
            </div>

            <div className="flex items-center gap-4 text-sm">
              <span className="font-medium">{log.user.username}</span>
              <span className="text-muted-foreground">{log.user.email}</span>
              <span className="text-muted-foreground">
                {format(new Date(log.timestamp), 'PPpp')}
              </span>
            </div>

            <div className="flex items-center gap-4 text-xs text-muted-foreground">
              <span>IP: {log.ip_address}</span>
              {log.object_id && <span>Object ID: {log.object_id}</span>}
            </div>

            {expanded && (
              <div className="mt-4 pt-4 border-t space-y-3">
                {log.changes && Object.keys(log.changes).length > 0 && (
                  <div>
                    <p className="text-sm font-medium mb-2">Changes:</p>
                    <div className="bg-muted p-3 rounded text-xs space-y-1">
                      {Object.entries(log.changes).map(([key, value]) => (
                        <div key={key} className="font-mono">
                          <span className="text-muted-foreground">{key}:</span>{' '}
                          <span>{JSON.stringify(value)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {log.metadata && Object.keys(log.metadata).length > 0 && (
                  <div>
                    <p className="text-sm font-medium mb-2">Metadata:</p>
                    <div className="bg-muted p-3 rounded text-xs">
                      <pre className="font-mono whitespace-pre-wrap">
                        {JSON.stringify(log.metadata, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}

                <div>
                  <p className="text-sm font-medium mb-2">User Agent:</p>
                  <p className="text-xs text-muted-foreground font-mono bg-muted p-2 rounded">
                    {log.user_agent}
                  </p>
                </div>
              </div>
            )}
          </div>

          <Button
            variant="ghost"
            size="sm"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? 'Less' : 'More'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
