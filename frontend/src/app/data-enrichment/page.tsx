'use client';

import { useState, useEffect, useCallback } from 'react';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Progress } from '@/components/ui/progress';
import { toast } from 'sonner';
import {
  Database,
  Sparkles,
  RefreshCw,
  CheckCircle2,
  Clock,
  Building2,
  User,
  Mail,
  Linkedin,
  AlertTriangle,
  TrendingUp,
  Settings,
  Play,
  Pause,
  BarChart3,
  Target,
  Zap,
  Filter,
  Download
} from 'lucide-react';
import { dataEnrichmentAPI } from '@/lib/ai-workflow-api';

interface EnrichmentProvider {
  id: number;
  name: string;
  provider_type: string;
  is_active: boolean;
  priority: number;
  api_endpoint: string;
  success_rate: number;
  average_response_time: number;
  total_requests: number;
  monthly_limit: number;
  requests_this_month: number;
}

interface EnrichmentProfile {
  id: number;
  name: string;
  profile_type: string;
  fields_to_enrich: string[];
  auto_enrich: boolean;
  enrichment_triggers: string[];
  priority_score_threshold: number;
  is_active: boolean;
  created_at: string;
  contacts_enriched: number;
  companies_enriched: number;
}

interface EnrichmentJob {
  id: number;
  profile_name: string;
  record_type: string;
  status: string;
  total_records: number;
  processed_records: number;
  successful_records: number;
  failed_records: number;
  started_at: string;
  completed_at?: string;
  error_message?: string;
}

interface EnrichmentResult {
  id: number;
  contact_name?: string;
  company_name?: string;
  record_type: string;
  provider: string;
  fields_enriched: string[];
  data_quality_score: number;
  enriched_at: string;
  is_verified: boolean;
}

interface DataQualityMetrics {
  overall_score: number;
  completeness: number;
  accuracy: number;
  freshness: number;
  consistency: number;
  total_records: number;
  enriched_records: number;
  records_needing_update: number;
}

export default function DataEnrichmentPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [providers, setProviders] = useState<EnrichmentProvider[]>([]);
  const [profiles, setProfiles] = useState<EnrichmentProfile[]>([]);
  const [jobs, setJobs] = useState<EnrichmentJob[]>([]);
  const [results, setResults] = useState<EnrichmentResult[]>([]);
  const [qualityMetrics, setQualityMetrics] = useState<DataQualityMetrics | null>(null);
  const [, setLoading] = useState(true);
  const [isCreateProfileDialogOpen, setIsCreateProfileDialogOpen] = useState(false);
  const [isConfigProviderDialogOpen, setIsConfigProviderDialogOpen] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [providersRes, profilesRes, jobsRes] = await Promise.all([
        dataEnrichmentAPI.getProviders().catch(() => ({ data: { results: [] } })),
        dataEnrichmentAPI.getProfiles().catch(() => ({ data: { results: [] } })),
        dataEnrichmentAPI.getJobs().catch(() => ({ data: { results: [] } }))
      ]);

      setProviders(providersRes.data.results || []);
      setProfiles(profilesRes.data.results || []);
      setJobs(jobsRes.data.results || []);

      // Load demo data if empty
      if ((providersRes.data.results || []).length === 0) {
        loadDemoData();
      }
    } catch (error) {
      console.error('Failed to fetch data:', error);
      loadDemoData();
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const loadDemoData = useCallback(() => {
    setProviders([
      {
        id: 1,
        name: 'Clearbit',
        provider_type: 'company',
        is_active: true,
        priority: 1,
        api_endpoint: 'https://api.clearbit.com/v2',
        success_rate: 94.5,
        average_response_time: 320,
        total_requests: 15420,
        monthly_limit: 50000,
        requests_this_month: 8750
      },
      {
        id: 2,
        name: 'ZoomInfo',
        provider_type: 'contact',
        is_active: true,
        priority: 1,
        api_endpoint: 'https://api.zoominfo.com/v1',
        success_rate: 91.2,
        average_response_time: 450,
        total_requests: 12300,
        monthly_limit: 25000,
        requests_this_month: 6200
      },
      {
        id: 3,
        name: 'Hunter.io',
        provider_type: 'email',
        is_active: true,
        priority: 2,
        api_endpoint: 'https://api.hunter.io/v2',
        success_rate: 88.7,
        average_response_time: 280,
        total_requests: 8900,
        monthly_limit: 10000,
        requests_this_month: 3400
      },
      {
        id: 4,
        name: 'LinkedIn Sales Navigator',
        provider_type: 'social',
        is_active: false,
        priority: 3,
        api_endpoint: 'https://api.linkedin.com/v2',
        success_rate: 85.3,
        average_response_time: 520,
        total_requests: 4500,
        monthly_limit: 15000,
        requests_this_month: 0
      }
    ]);

    setProfiles([
      {
        id: 1,
        name: 'High-Value Lead Enrichment',
        profile_type: 'contact',
        fields_to_enrich: ['job_title', 'phone', 'linkedin_url', 'company_size', 'industry'],
        auto_enrich: true,
        enrichment_triggers: ['lead_score_above_70', 'new_contact_created'],
        priority_score_threshold: 70,
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        contacts_enriched: 2450,
        companies_enriched: 0
      },
      {
        id: 2,
        name: 'Company Intelligence',
        profile_type: 'company',
        fields_to_enrich: ['revenue', 'employee_count', 'technologies', 'funding_info', 'social_profiles'],
        auto_enrich: true,
        enrichment_triggers: ['new_company_created', 'opportunity_created'],
        priority_score_threshold: 50,
        is_active: true,
        created_at: '2024-01-05T00:00:00Z',
        contacts_enriched: 0,
        companies_enriched: 890
      },
      {
        id: 3,
        name: 'Email Verification',
        profile_type: 'contact',
        fields_to_enrich: ['email_verified', 'email_deliverability'],
        auto_enrich: false,
        enrichment_triggers: ['manual'],
        priority_score_threshold: 0,
        is_active: true,
        created_at: '2024-01-10T00:00:00Z',
        contacts_enriched: 5600,
        companies_enriched: 0
      }
    ]);

    setJobs([
      {
        id: 1,
        profile_name: 'High-Value Lead Enrichment',
        record_type: 'contact',
        status: 'completed',
        total_records: 250,
        processed_records: 250,
        successful_records: 238,
        failed_records: 12,
        started_at: new Date(Date.now() - 3600000).toISOString(),
        completed_at: new Date(Date.now() - 1800000).toISOString()
      },
      {
        id: 2,
        profile_name: 'Company Intelligence',
        record_type: 'company',
        status: 'running',
        total_records: 150,
        processed_records: 87,
        successful_records: 82,
        failed_records: 5,
        started_at: new Date(Date.now() - 1200000).toISOString()
      },
      {
        id: 3,
        profile_name: 'Email Verification',
        record_type: 'contact',
        status: 'pending',
        total_records: 500,
        processed_records: 0,
        successful_records: 0,
        failed_records: 0,
        started_at: new Date().toISOString()
      }
    ]);

    setResults([
      {
        id: 1,
        contact_name: 'John Smith',
        record_type: 'contact',
        provider: 'ZoomInfo',
        fields_enriched: ['job_title', 'phone', 'linkedin_url'],
        data_quality_score: 95,
        enriched_at: new Date(Date.now() - 300000).toISOString(),
        is_verified: true
      },
      {
        id: 2,
        company_name: 'TechCorp Inc',
        record_type: 'company',
        provider: 'Clearbit',
        fields_enriched: ['revenue', 'employee_count', 'technologies', 'industry'],
        data_quality_score: 92,
        enriched_at: new Date(Date.now() - 600000).toISOString(),
        is_verified: true
      },
      {
        id: 3,
        contact_name: 'Sarah Johnson',
        record_type: 'contact',
        provider: 'Hunter.io',
        fields_enriched: ['email_verified'],
        data_quality_score: 88,
        enriched_at: new Date(Date.now() - 900000).toISOString(),
        is_verified: true
      }
    ]);

    setQualityMetrics({
      overall_score: 87,
      completeness: 82,
      accuracy: 94,
      freshness: 78,
      consistency: 91,
      total_records: 12500,
      enriched_records: 9800,
      records_needing_update: 1250
    });
  }, []);

  const triggerEnrichment = async (profileId: number) => {
    try {
      await dataEnrichmentAPI.triggerEnrichment(profileId, 'contact', []);
      toast.success('Enrichment job started');
      fetchData();
    } catch (error) {
      toast.info('Enrichment job queued (demo)');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-700';
      case 'running': return 'bg-blue-100 text-blue-700';
      case 'pending': return 'bg-yellow-100 text-yellow-700';
      case 'failed': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const getProviderIcon = (type: string) => {
    switch (type) {
      case 'company': return <Building2 className="h-5 w-5" />;
      case 'contact': return <User className="h-5 w-5" />;
      case 'email': return <Mail className="h-5 w-5" />;
      case 'social': return <Linkedin className="h-5 w-5" />;
      default: return <Database className="h-5 w-5" />;
    }
  };

  const getQualityColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getProgressColor = (score: number) => {
    if (score >= 90) return 'bg-green-500';
    if (score >= 70) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-6 space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold flex items-center gap-2">
                <Database className="h-8 w-8 text-emerald-600" />
                Data Enrichment
              </h1>
              <p className="text-gray-500 mt-1">
                AI-powered data enrichment and quality management
              </p>
            </div>
            <div className="flex gap-3">
              <Button variant="outline" onClick={fetchData}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
              <Dialog open={isCreateProfileDialogOpen} onOpenChange={setIsCreateProfileDialogOpen}>
                <DialogTrigger asChild>
                  <Button>
                    <Sparkles className="h-4 w-4 mr-2" />
                    Create Profile
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-lg">
                  <DialogHeader>
                    <DialogTitle>Create Enrichment Profile</DialogTitle>
                    <DialogDescription>
                      Define what data to enrich and when to trigger enrichment
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4 py-4">
                    <div>
                      <Label>Profile Name</Label>
                      <Input placeholder="e.g., Enterprise Lead Enrichment" />
                    </div>
                    <div>
                      <Label>Profile Type</Label>
                      <Select defaultValue="contact">
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="contact">Contact</SelectItem>
                          <SelectItem value="company">Company</SelectItem>
                          <SelectItem value="both">Both</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label>Fields to Enrich</Label>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {['job_title', 'phone', 'linkedin_url', 'company_size', 'industry', 'revenue', 'technologies'].map(field => (
                          <Badge key={field} variant="outline" className="cursor-pointer hover:bg-gray-100">
                            {field.replace('_', ' ')}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Auto-Enrich</Label>
                        <p className="text-sm text-gray-500">Automatically enrich matching records</p>
                      </div>
                      <Switch />
                    </div>
                    <div>
                      <Label>Priority Score Threshold</Label>
                      <Input type="number" defaultValue={50} min={0} max={100} />
                      <p className="text-xs text-gray-500 mt-1">Only enrich records with score above this threshold</p>
                    </div>
                    <Button className="w-full">Create Profile</Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Data Quality Score</p>
                    <p className={`text-2xl font-bold ${getQualityColor(qualityMetrics?.overall_score || 0)}`}>
                      {qualityMetrics?.overall_score || 0}%
                    </p>
                  </div>
                  <Target className="h-8 w-8 text-emerald-500" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Records Enriched</p>
                    <p className="text-2xl font-bold">{qualityMetrics?.enriched_records?.toLocaleString() || 0}</p>
                  </div>
                  <CheckCircle2 className="h-8 w-8 text-green-500" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Active Jobs</p>
                    <p className="text-2xl font-bold text-blue-600">
                      {jobs.filter(j => j.status === 'running').length}
                    </p>
                  </div>
                  <RefreshCw className="h-8 w-8 text-blue-500 animate-spin" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Need Update</p>
                    <p className="text-2xl font-bold text-yellow-600">
                      {qualityMetrics?.records_needing_update?.toLocaleString() || 0}
                    </p>
                  </div>
                  <AlertTriangle className="h-8 w-8 text-yellow-500" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Content Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="providers">Providers</TabsTrigger>
              <TabsTrigger value="profiles">Profiles</TabsTrigger>
              <TabsTrigger value="jobs">Jobs</TabsTrigger>
              <TabsTrigger value="quality">Data Quality</TabsTrigger>
            </TabsList>

            {/* Overview Tab */}
            <TabsContent value="overview" className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Data Quality Overview */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BarChart3 className="h-5 w-5" />
                      Data Quality Breakdown
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {qualityMetrics && (
                      <div className="space-y-4">
                        <div>
                          <div className="flex justify-between mb-1">
                            <span className="text-sm">Completeness</span>
                            <span className={`text-sm font-medium ${getQualityColor(qualityMetrics.completeness)}`}>
                              {qualityMetrics.completeness}%
                            </span>
                          </div>
                          <div className="w-full h-2 bg-gray-200 rounded-full">
                            <div
                              className={`h-full rounded-full ${getProgressColor(qualityMetrics.completeness)}`}
                              style={{ width: `${qualityMetrics.completeness}%` }}
                            />
                          </div>
                        </div>
                        <div>
                          <div className="flex justify-between mb-1">
                            <span className="text-sm">Accuracy</span>
                            <span className={`text-sm font-medium ${getQualityColor(qualityMetrics.accuracy)}`}>
                              {qualityMetrics.accuracy}%
                            </span>
                          </div>
                          <div className="w-full h-2 bg-gray-200 rounded-full">
                            <div
                              className={`h-full rounded-full ${getProgressColor(qualityMetrics.accuracy)}`}
                              style={{ width: `${qualityMetrics.accuracy}%` }}
                            />
                          </div>
                        </div>
                        <div>
                          <div className="flex justify-between mb-1">
                            <span className="text-sm">Freshness</span>
                            <span className={`text-sm font-medium ${getQualityColor(qualityMetrics.freshness)}`}>
                              {qualityMetrics.freshness}%
                            </span>
                          </div>
                          <div className="w-full h-2 bg-gray-200 rounded-full">
                            <div
                              className={`h-full rounded-full ${getProgressColor(qualityMetrics.freshness)}`}
                              style={{ width: `${qualityMetrics.freshness}%` }}
                            />
                          </div>
                        </div>
                        <div>
                          <div className="flex justify-between mb-1">
                            <span className="text-sm">Consistency</span>
                            <span className={`text-sm font-medium ${getQualityColor(qualityMetrics.consistency)}`}>
                              {qualityMetrics.consistency}%
                            </span>
                          </div>
                          <div className="w-full h-2 bg-gray-200 rounded-full">
                            <div
                              className={`h-full rounded-full ${getProgressColor(qualityMetrics.consistency)}`}
                              style={{ width: `${qualityMetrics.consistency}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Active Providers */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Zap className="h-5 w-5" />
                      Active Providers
                    </CardTitle>
                    <CardDescription>Data enrichment sources</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {providers.filter(p => p.is_active).map(provider => (
                        <div key={provider.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div className="flex items-center gap-3">
                            <div className="p-2 bg-white rounded-lg shadow-sm">
                              {getProviderIcon(provider.provider_type)}
                            </div>
                            <div>
                              <p className="font-medium">{provider.name}</p>
                              <p className="text-xs text-gray-500 capitalize">{provider.provider_type} data</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="text-sm font-medium text-green-600">{provider.success_rate}%</p>
                            <p className="text-xs text-gray-500">success rate</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Recent Enrichments */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Clock className="h-5 w-5" />
                      Recent Enrichments
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {results.slice(0, 5).map(result => (
                        <div key={result.id} className="flex items-center justify-between p-3 border rounded-lg">
                          <div className="flex items-center gap-3">
                            {result.record_type === 'contact' ? (
                              <User className="h-5 w-5 text-blue-500" />
                            ) : (
                              <Building2 className="h-5 w-5 text-purple-500" />
                            )}
                            <div>
                              <p className="font-medium">
                                {result.contact_name || result.company_name}
                              </p>
                              <p className="text-xs text-gray-500">
                                {result.fields_enriched.length} fields • {result.provider}
                              </p>
                            </div>
                          </div>
                          <Badge className={getQualityColor(result.data_quality_score)}>
                            {result.data_quality_score}%
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Running Jobs */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <RefreshCw className="h-5 w-5" />
                      Running Jobs
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {jobs.filter(j => j.status === 'running').map(job => (
                        <div key={job.id} className="p-3 border rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium">{job.profile_name}</span>
                            <Badge className={getStatusColor(job.status)}>{job.status}</Badge>
                          </div>
                          <div className="space-y-2">
                            <div className="flex justify-between text-sm text-gray-500">
                              <span>Progress</span>
                              <span>{job.processed_records}/{job.total_records}</span>
                            </div>
                            <Progress value={(job.processed_records / job.total_records) * 100} />
                          </div>
                        </div>
                      ))}
                      {jobs.filter(j => j.status === 'running').length === 0 && (
                        <p className="text-gray-500 text-center py-4">No jobs currently running</p>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* Providers Tab */}
            <TabsContent value="providers" className="space-y-4">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>Enrichment Providers</CardTitle>
                      <CardDescription>Manage your data enrichment sources</CardDescription>
                    </div>
                    <Button onClick={() => setIsConfigProviderDialogOpen(true)}>
                      <Settings className="h-4 w-4 mr-2" />
                      Add Provider
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {providers.map(provider => (
                      <div key={provider.id} className="border rounded-lg p-4">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex items-center gap-3">
                            <div className={`p-3 rounded-lg ${provider.is_active ? 'bg-emerald-100' : 'bg-gray-100'}`}>
                              {getProviderIcon(provider.provider_type)}
                            </div>
                            <div>
                              <div className="flex items-center gap-2">
                                <h3 className="font-semibold text-lg">{provider.name}</h3>
                                <Badge variant={provider.is_active ? 'default' : 'secondary'}>
                                  {provider.is_active ? 'Active' : 'Inactive'}
                                </Badge>
                              </div>
                              <p className="text-sm text-gray-500 capitalize">{provider.provider_type} Data Provider</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Switch checked={provider.is_active} />
                            <Button size="sm" variant="outline">
                              <Settings className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          <div className="p-3 bg-gray-50 rounded-lg">
                            <p className="text-xs text-gray-500">Success Rate</p>
                            <p className={`text-lg font-semibold ${getQualityColor(provider.success_rate)}`}>
                              {provider.success_rate}%
                            </p>
                          </div>
                          <div className="p-3 bg-gray-50 rounded-lg">
                            <p className="text-xs text-gray-500">Avg Response</p>
                            <p className="text-lg font-semibold">{provider.average_response_time}ms</p>
                          </div>
                          <div className="p-3 bg-gray-50 rounded-lg">
                            <p className="text-xs text-gray-500">Total Requests</p>
                            <p className="text-lg font-semibold">{provider.total_requests.toLocaleString()}</p>
                          </div>
                          <div className="p-3 bg-gray-50 rounded-lg">
                            <p className="text-xs text-gray-500">Monthly Usage</p>
                            <p className="text-lg font-semibold">
                              {provider.requests_this_month.toLocaleString()}/{provider.monthly_limit.toLocaleString()}
                            </p>
                          </div>
                        </div>

                        <div className="mt-4">
                          <div className="flex justify-between mb-1 text-sm">
                            <span className="text-gray-500">Monthly API Usage</span>
                            <span>{Math.round((provider.requests_this_month / provider.monthly_limit) * 100)}%</span>
                          </div>
                          <Progress value={(provider.requests_this_month / provider.monthly_limit) * 100} />
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Profiles Tab */}
            <TabsContent value="profiles" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Enrichment Profiles</CardTitle>
                  <CardDescription>Configure what data to enrich and enrichment triggers</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {profiles.map(profile => (
                      <div key={profile.id} className="border rounded-lg p-4">
                        <div className="flex items-start justify-between mb-4">
                          <div>
                            <div className="flex items-center gap-2">
                              <h3 className="font-semibold">{profile.name}</h3>
                              <Badge variant={profile.is_active ? 'default' : 'secondary'}>
                                {profile.is_active ? 'Active' : 'Inactive'}
                              </Badge>
                              <Badge variant="outline" className="capitalize">
                                {profile.profile_type}
                              </Badge>
                            </div>
                            <p className="text-sm text-gray-500 mt-1">
                              Created {new Date(profile.created_at).toLocaleDateString()}
                            </p>
                          </div>
                          <div className="flex items-center gap-2">
                            <Button size="sm" variant="outline" onClick={() => triggerEnrichment(profile.id)}>
                              <Play className="h-4 w-4 mr-1" />
                              Run Now
                            </Button>
                            <Switch checked={profile.is_active} />
                          </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                          <div>
                            <h4 className="text-sm font-medium mb-2">Fields to Enrich</h4>
                            <div className="flex flex-wrap gap-1">
                              {profile.fields_to_enrich.map(field => (
                                <Badge key={field} variant="secondary" className="text-xs">
                                  {field.replace('_', ' ')}
                                </Badge>
                              ))}
                            </div>
                          </div>
                          <div>
                            <h4 className="text-sm font-medium mb-2">Triggers</h4>
                            <div className="flex flex-wrap gap-1">
                              {profile.enrichment_triggers.map(trigger => (
                                <Badge key={trigger} variant="outline" className="text-xs">
                                  {trigger.replace(/_/g, ' ')}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center justify-between pt-3 border-t text-sm">
                          <div className="flex items-center gap-4">
                            <span className="text-gray-500">
                              Auto-enrich: <strong>{profile.auto_enrich ? 'Yes' : 'No'}</strong>
                            </span>
                            <span className="text-gray-500">
                              Threshold: <strong>{profile.priority_score_threshold}</strong>
                            </span>
                          </div>
                          <div className="flex items-center gap-4">
                            {profile.contacts_enriched > 0 && (
                              <span className="text-gray-500">
                                <User className="h-3 w-3 inline mr-1" />
                                {profile.contacts_enriched.toLocaleString()} contacts
                              </span>
                            )}
                            {profile.companies_enriched > 0 && (
                              <span className="text-gray-500">
                                <Building2 className="h-3 w-3 inline mr-1" />
                                {profile.companies_enriched.toLocaleString()} companies
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Jobs Tab */}
            <TabsContent value="jobs" className="space-y-4">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>Enrichment Jobs</CardTitle>
                      <CardDescription>View and manage enrichment job history</CardDescription>
                    </div>
                    <div className="flex gap-2">
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
                  <div className="space-y-4">
                    {jobs.map(job => (
                      <div key={job.id} className="border rounded-lg p-4">
                        <div className="flex items-start justify-between mb-3">
                          <div>
                            <div className="flex items-center gap-2">
                              <h3 className="font-medium">{job.profile_name}</h3>
                              <Badge className={getStatusColor(job.status)}>{job.status}</Badge>
                              <Badge variant="outline" className="capitalize">{job.record_type}</Badge>
                            </div>
                            <p className="text-sm text-gray-500 mt-1">
                              Started: {new Date(job.started_at).toLocaleString()}
                              {job.completed_at && ` • Completed: ${new Date(job.completed_at).toLocaleString()}`}
                            </p>
                          </div>
                          <div className="flex gap-2">
                            {job.status === 'running' && (
                              <Button size="sm" variant="outline">
                                <Pause className="h-4 w-4" />
                              </Button>
                            )}
                            {job.status === 'pending' && (
                              <Button size="sm" variant="outline">
                                <Play className="h-4 w-4" />
                              </Button>
                            )}
                          </div>
                        </div>

                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-500">Progress</span>
                            <span>{job.processed_records}/{job.total_records} records</span>
                          </div>
                          <Progress value={(job.processed_records / job.total_records) * 100} />
                        </div>

                        <div className="grid grid-cols-3 gap-4 mt-4 pt-3 border-t">
                          <div className="text-center">
                            <p className="text-2xl font-semibold text-green-600">{job.successful_records}</p>
                            <p className="text-xs text-gray-500">Successful</p>
                          </div>
                          <div className="text-center">
                            <p className="text-2xl font-semibold text-red-600">{job.failed_records}</p>
                            <p className="text-xs text-gray-500">Failed</p>
                          </div>
                          <div className="text-center">
                            <p className="text-2xl font-semibold text-gray-600">
                              {job.total_records - job.processed_records}
                            </p>
                            <p className="text-xs text-gray-500">Remaining</p>
                          </div>
                        </div>

                        {job.error_message && (
                          <div className="mt-3 p-2 bg-red-50 rounded text-sm text-red-700">
                            <AlertTriangle className="h-4 w-4 inline mr-1" />
                            {job.error_message}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Data Quality Tab */}
            <TabsContent value="quality" className="space-y-4">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Overall Data Quality</CardTitle>
                    <CardDescription>Comprehensive view of your CRM data health</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {qualityMetrics && (
                      <div className="space-y-6">
                        <div className="text-center py-6">
                          <div className="inline-flex items-center justify-center w-32 h-32 rounded-full bg-emerald-100">
                            <span className={`text-4xl font-bold ${getQualityColor(qualityMetrics.overall_score)}`}>
                              {qualityMetrics.overall_score}%
                            </span>
                          </div>
                          <p className="mt-3 text-lg font-medium">Overall Quality Score</p>
                          <p className="text-sm text-gray-500">Based on completeness, accuracy, freshness, and consistency</p>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                          <div className="p-4 bg-blue-50 rounded-lg">
                            <p className="text-sm text-blue-600">Total Records</p>
                            <p className="text-2xl font-bold text-blue-900">
                              {qualityMetrics.total_records.toLocaleString()}
                            </p>
                          </div>
                          <div className="p-4 bg-green-50 rounded-lg">
                            <p className="text-sm text-green-600">Enriched Records</p>
                            <p className="text-2xl font-bold text-green-900">
                              {qualityMetrics.enriched_records.toLocaleString()}
                            </p>
                          </div>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Quality Dimensions</CardTitle>
                    <CardDescription>Detailed breakdown of data quality metrics</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {qualityMetrics && (
                      <div className="space-y-6">
                        <div className="p-4 border rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <CheckCircle2 className="h-5 w-5 text-blue-500" />
                              <span className="font-medium">Completeness</span>
                            </div>
                            <span className={`font-semibold ${getQualityColor(qualityMetrics.completeness)}`}>
                              {qualityMetrics.completeness}%
                            </span>
                          </div>
                          <p className="text-sm text-gray-500 mb-2">How much of the expected data is present</p>
                          <Progress value={qualityMetrics.completeness} />
                        </div>

                        <div className="p-4 border rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <Target className="h-5 w-5 text-green-500" />
                              <span className="font-medium">Accuracy</span>
                            </div>
                            <span className={`font-semibold ${getQualityColor(qualityMetrics.accuracy)}`}>
                              {qualityMetrics.accuracy}%
                            </span>
                          </div>
                          <p className="text-sm text-gray-500 mb-2">How correct and reliable the data is</p>
                          <Progress value={qualityMetrics.accuracy} />
                        </div>

                        <div className="p-4 border rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <Clock className="h-5 w-5 text-yellow-500" />
                              <span className="font-medium">Freshness</span>
                            </div>
                            <span className={`font-semibold ${getQualityColor(qualityMetrics.freshness)}`}>
                              {qualityMetrics.freshness}%
                            </span>
                          </div>
                          <p className="text-sm text-gray-500 mb-2">How recently the data has been updated</p>
                          <Progress value={qualityMetrics.freshness} />
                        </div>

                        <div className="p-4 border rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <TrendingUp className="h-5 w-5 text-purple-500" />
                              <span className="font-medium">Consistency</span>
                            </div>
                            <span className={`font-semibold ${getQualityColor(qualityMetrics.consistency)}`}>
                              {qualityMetrics.consistency}%
                            </span>
                          </div>
                          <p className="text-sm text-gray-500 mb-2">How uniform the data format is across records</p>
                          <Progress value={qualityMetrics.consistency} />
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>

                <Card className="lg:col-span-2">
                  <CardHeader>
                    <CardTitle>Data Quality Recommendations</CardTitle>
                    <CardDescription>AI-generated suggestions to improve your data quality</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          <AlertTriangle className="h-5 w-5 text-yellow-600" />
                          <span className="font-medium text-yellow-900">Stale Data Alert</span>
                        </div>
                        <p className="text-sm text-yellow-800 mb-3">
                          {qualityMetrics?.records_needing_update.toLocaleString()} records haven&apos;t been updated in 90+ days.
                        </p>
                        <Button size="sm" variant="outline" className="border-yellow-400 text-yellow-700">
                          Re-enrich Records
                        </Button>
                      </div>

                      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          <Mail className="h-5 w-5 text-blue-600" />
                          <span className="font-medium text-blue-900">Missing Emails</span>
                        </div>
                        <p className="text-sm text-blue-800 mb-3">
                          1,250 contacts are missing email addresses. Consider running email finder.
                        </p>
                        <Button size="sm" variant="outline" className="border-blue-400 text-blue-700">
                          Find Emails
                        </Button>
                      </div>

                      <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          <Building2 className="h-5 w-5 text-purple-600" />
                          <span className="font-medium text-purple-900">Incomplete Companies</span>
                        </div>
                        <p className="text-sm text-purple-800 mb-3">
                          320 companies are missing revenue and employee data.
                        </p>
                        <Button size="sm" variant="outline" className="border-purple-400 text-purple-700">
                          Enrich Companies
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>

          {/* Add Provider Dialog */}
          <Dialog open={isConfigProviderDialogOpen} onOpenChange={setIsConfigProviderDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add Enrichment Provider</DialogTitle>
                <DialogDescription>
                  Connect a new data enrichment provider
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div>
                  <Label>Provider Name</Label>
                  <Input placeholder="e.g., Clearbit, ZoomInfo" />
                </div>
                <div>
                  <Label>Provider Type</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="company">Company Data</SelectItem>
                      <SelectItem value="contact">Contact Data</SelectItem>
                      <SelectItem value="email">Email Verification</SelectItem>
                      <SelectItem value="social">Social Profiles</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>API Endpoint</Label>
                  <Input placeholder="https://api.provider.com/v1" />
                </div>
                <div>
                  <Label>API Key</Label>
                  <Input type="password" placeholder="Enter your API key" />
                </div>
                <div>
                  <Label>Monthly Request Limit</Label>
                  <Input type="number" placeholder="50000" />
                </div>
                <div>
                  <Label>Priority</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Select priority" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">High (Primary)</SelectItem>
                      <SelectItem value="2">Medium (Secondary)</SelectItem>
                      <SelectItem value="3">Low (Fallback)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button className="w-full">Add Provider</Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
