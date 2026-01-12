'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Leaf, 
  BarChart3, 
  Target, 
  FileText, 
  TrendingUp, 
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  Download,
  Plus,
  Calendar,
  Building2,
  Droplets,
  Zap,
  Recycle,
  Users,
  Globe,
  Award,
  Factory,
  Truck
} from 'lucide-react';
import { esgReportingAPI } from '@/lib/api';

interface ESGMetric {
  id: string;
  name: string;
  category: 'environmental' | 'social' | 'governance';
  value: number;
  target: number;
  unit: string;
  trend: number;
  status: 'on-track' | 'at-risk' | 'off-track';
}

interface ESGTarget {
  id: string;
  name: string;
  description: string;
  category: string;
  target_value: number;
  current_value: number;
  deadline: string;
  progress: number;
}

interface ESGReport {
  id: string;
  name: string;
  framework: string;
  period: string;
  status: 'draft' | 'in-review' | 'published';
  created_at: string;
}

interface CarbonEntry {
  id: string;
  source: string;
  scope: 1 | 2 | 3;
  emissions: number;
  unit: string;
  period: string;
}

interface SupplierAssessment {
  id: string;
  supplier_name: string;
  score: number;
  risk_level: 'low' | 'medium' | 'high';
  last_assessed: string;
  categories: string[];
}

export default function ESGReportingPage() {
  const [metrics, setMetrics] = useState<ESGMetric[]>([]);
  const [targets, setTargets] = useState<ESGTarget[]>([]);
  const [reports, setReports] = useState<ESGReport[]>([]);
  const [carbonData, setCarbonData] = useState<CarbonEntry[]>([]);
  const [suppliers, setSuppliers] = useState<SupplierAssessment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState('2026');

  useEffect(() => {
    loadESGData();
  }, []);

  const loadESGData = async () => {
    setIsLoading(true);
    try {
      const [dashboardData, metricsData, targetsData, reportsData, carbonDataRes, suppliersData] = await Promise.all([
        esgReportingAPI.getDashboard(),
        esgReportingAPI.getMetrics(),
        esgReportingAPI.getTargets(),
        esgReportingAPI.getReports(),
        esgReportingAPI.getCarbonData(),
        esgReportingAPI.getSupplierAssessments(),
      ]);
      setMetrics(metricsData.results || metricsData || []);
      setTargets(targetsData.results || targetsData || []);
      setReports(reportsData.results || reportsData || []);
      setCarbonData(carbonDataRes.results || carbonDataRes || []);
      setSuppliers(suppliersData.results || suppliersData || []);
    } catch (error) {
      console.error('Failed to load ESG data:', error);
      // Demo data
      setMetrics([
        { id: '1', name: 'Carbon Emissions', category: 'environmental', value: 1250, target: 1000, unit: 'tCO2e', trend: -12, status: 'at-risk' },
        { id: '2', name: 'Renewable Energy', category: 'environmental', value: 65, target: 80, unit: '%', trend: 8, status: 'on-track' },
        { id: '3', name: 'Water Usage', category: 'environmental', value: 45000, target: 50000, unit: 'm³', trend: -5, status: 'on-track' },
        { id: '4', name: 'Waste Recycled', category: 'environmental', value: 78, target: 90, unit: '%', trend: 3, status: 'at-risk' },
        { id: '5', name: 'Employee Diversity', category: 'social', value: 42, target: 50, unit: '%', trend: 5, status: 'on-track' },
        { id: '6', name: 'Training Hours', category: 'social', value: 32, target: 40, unit: 'hrs/employee', trend: 10, status: 'on-track' },
        { id: '7', name: 'Safety Incidents', category: 'social', value: 3, target: 0, unit: 'incidents', trend: -25, status: 'at-risk' },
        { id: '8', name: 'Board Independence', category: 'governance', value: 75, target: 70, unit: '%', trend: 0, status: 'on-track' },
        { id: '9', name: 'Ethics Training', category: 'governance', value: 95, target: 100, unit: '%', trend: 2, status: 'on-track' },
      ]);
      setTargets([
        { id: '1', name: 'Net Zero by 2030', description: 'Achieve net zero carbon emissions', category: 'environmental', target_value: 0, current_value: 1250, deadline: '2030-12-31', progress: 45 },
        { id: '2', name: '100% Renewable Energy', description: 'Transition to 100% renewable energy sources', category: 'environmental', target_value: 100, current_value: 65, deadline: '2028-12-31', progress: 65 },
        { id: '3', name: 'Gender Parity', description: 'Achieve 50% gender diversity in leadership', category: 'social', target_value: 50, current_value: 42, deadline: '2027-12-31', progress: 84 },
        { id: '4', name: 'Zero Waste to Landfill', description: 'Eliminate all waste sent to landfills', category: 'environmental', target_value: 100, current_value: 78, deadline: '2028-12-31', progress: 78 },
      ]);
      setReports([
        { id: '1', name: 'Annual Sustainability Report 2025', framework: 'GRI Standards', period: '2025', status: 'published', created_at: '2026-01-05T10:00:00Z' },
        { id: '2', name: 'Q4 2025 ESG Update', framework: 'SASB', period: 'Q4 2025', status: 'published', created_at: '2026-01-10T14:00:00Z' },
        { id: '3', name: 'Carbon Disclosure Report', framework: 'CDP', period: '2025', status: 'in-review', created_at: '2026-01-08T09:00:00Z' },
        { id: '4', name: 'TCFD Climate Report', framework: 'TCFD', period: '2025', status: 'draft', created_at: '2026-01-12T11:00:00Z' },
      ]);
      setCarbonData([
        { id: '1', source: 'Natural Gas', scope: 1, emissions: 450, unit: 'tCO2e', period: '2025' },
        { id: '2', source: 'Company Vehicles', scope: 1, emissions: 180, unit: 'tCO2e', period: '2025' },
        { id: '3', source: 'Purchased Electricity', scope: 2, emissions: 320, unit: 'tCO2e', period: '2025' },
        { id: '4', source: 'Business Travel', scope: 3, emissions: 150, unit: 'tCO2e', period: '2025' },
        { id: '5', source: 'Supply Chain', scope: 3, emissions: 850, unit: 'tCO2e', period: '2025' },
      ]);
      setSuppliers([
        { id: '1', supplier_name: 'EcoTech Materials', score: 92, risk_level: 'low', last_assessed: '2025-12-15', categories: ['Environmental', 'Labor'] },
        { id: '2', supplier_name: 'Global Logistics Co', score: 68, risk_level: 'medium', last_assessed: '2025-11-20', categories: ['Carbon', 'Safety'] },
        { id: '3', supplier_name: 'Office Supplies Inc', score: 85, risk_level: 'low', last_assessed: '2025-12-01', categories: ['Environmental', 'Ethics'] },
        { id: '4', supplier_name: 'Heavy Industries Ltd', score: 45, risk_level: 'high', last_assessed: '2025-10-10', categories: ['Carbon', 'Labor', 'Safety'] },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'environmental':
        return <Leaf className="h-4 w-4 text-green-500" />;
      case 'social':
        return <Users className="h-4 w-4 text-blue-500" />;
      case 'governance':
        return <Building2 className="h-4 w-4 text-purple-500" />;
      default:
        return <Globe className="h-4 w-4" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'on-track':
        return <Badge className="bg-green-100 text-green-700">On Track</Badge>;
      case 'at-risk':
        return <Badge className="bg-yellow-100 text-yellow-700">At Risk</Badge>;
      case 'off-track':
        return <Badge className="bg-red-100 text-red-700">Off Track</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getRiskBadge = (risk: string) => {
    switch (risk) {
      case 'low':
        return <Badge className="bg-green-100 text-green-700">Low Risk</Badge>;
      case 'medium':
        return <Badge className="bg-yellow-100 text-yellow-700">Medium Risk</Badge>;
      case 'high':
        return <Badge className="bg-red-100 text-red-700">High Risk</Badge>;
      default:
        return <Badge variant="outline">{risk}</Badge>;
    }
  };

  const totalCarbonByScope = carbonData.reduce((acc, entry) => {
    acc[entry.scope] = (acc[entry.scope] || 0) + entry.emissions;
    return acc;
  }, {} as Record<number, number>);

  const environmentalMetrics = metrics.filter(m => m.category === 'environmental');
  const socialMetrics = metrics.filter(m => m.category === 'social');
  const governanceMetrics = metrics.filter(m => m.category === 'governance');

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Leaf className="h-8 w-8 text-green-500" />
            ESG Reporting
          </h1>
          <p className="text-muted-foreground">
            Environmental, Social & Governance performance tracking
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="2026">2026</SelectItem>
              <SelectItem value="2025">2025</SelectItem>
              <SelectItem value="2024">2024</SelectItem>
            </SelectContent>
          </Select>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            New Report
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Overall ESG Score</p>
                <p className="text-3xl font-bold">78</p>
              </div>
              <div className="bg-green-100 rounded-full p-3">
                <Award className="h-6 w-6 text-green-600" />
              </div>
            </div>
            <Progress value={78} className="mt-4" />
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Carbon Footprint</p>
                <p className="text-3xl font-bold">1,950</p>
                <p className="text-xs text-muted-foreground">tCO2e total</p>
              </div>
              <div className="bg-blue-100 rounded-full p-3">
                <Factory className="h-6 w-6 text-blue-600" />
              </div>
            </div>
            <div className="flex items-center gap-1 mt-2">
              <TrendingDown className="h-4 w-4 text-green-500" />
              <span className="text-sm text-green-500">-12% vs last year</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Targets On Track</p>
                <p className="text-3xl font-bold">3/4</p>
              </div>
              <div className="bg-yellow-100 rounded-full p-3">
                <Target className="h-6 w-6 text-yellow-600" />
              </div>
            </div>
            <p className="text-xs text-muted-foreground mt-2">1 target needs attention</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Supplier Risk</p>
                <p className="text-3xl font-bold">1</p>
                <p className="text-xs text-muted-foreground">high-risk supplier</p>
              </div>
              <div className="bg-red-100 rounded-full p-3">
                <Truck className="h-6 w-6 text-red-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="dashboard">
        <TabsList>
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="carbon">Carbon Footprint</TabsTrigger>
          <TabsTrigger value="targets">Targets</TabsTrigger>
          <TabsTrigger value="suppliers">Suppliers</TabsTrigger>
          <TabsTrigger value="reports">Reports</TabsTrigger>
        </TabsList>

        <TabsContent value="dashboard" className="mt-6 space-y-6">
          {/* Environmental Metrics */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Leaf className="h-5 w-5 text-green-500" />
                Environmental
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {environmentalMetrics.map((metric) => (
                  <Card key={metric.id}>
                    <CardContent className="pt-4">
                      <div className="flex items-center justify-between mb-2">
                        <p className="text-sm font-medium">{metric.name}</p>
                        {getStatusBadge(metric.status)}
                      </div>
                      <p className="text-2xl font-bold">{metric.value.toLocaleString()} <span className="text-sm font-normal text-muted-foreground">{metric.unit}</span></p>
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-xs text-muted-foreground">Target: {metric.target.toLocaleString()} {metric.unit}</span>
                        <span className={`text-xs flex items-center gap-1 ${metric.trend > 0 ? 'text-green-500' : 'text-red-500'}`}>
                          {metric.trend > 0 ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                          {Math.abs(metric.trend)}%
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Social Metrics */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5 text-blue-500" />
                Social
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {socialMetrics.map((metric) => (
                  <Card key={metric.id}>
                    <CardContent className="pt-4">
                      <div className="flex items-center justify-between mb-2">
                        <p className="text-sm font-medium">{metric.name}</p>
                        {getStatusBadge(metric.status)}
                      </div>
                      <p className="text-2xl font-bold">{metric.value.toLocaleString()} <span className="text-sm font-normal text-muted-foreground">{metric.unit}</span></p>
                      <Progress value={(metric.value / metric.target) * 100} className="mt-2" />
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Governance Metrics */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building2 className="h-5 w-5 text-purple-500" />
                Governance
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {governanceMetrics.map((metric) => (
                  <Card key={metric.id}>
                    <CardContent className="pt-4">
                      <div className="flex items-center justify-between mb-2">
                        <p className="text-sm font-medium">{metric.name}</p>
                        {getStatusBadge(metric.status)}
                      </div>
                      <p className="text-2xl font-bold">{metric.value}%</p>
                      <Progress value={metric.value} className="mt-2" />
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="carbon" className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center gap-3 mb-2">
                  <div className="bg-red-100 rounded-full p-2">
                    <Factory className="h-5 w-5 text-red-600" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Scope 1 (Direct)</p>
                    <p className="text-2xl font-bold">{totalCarbonByScope[1] || 0} tCO2e</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center gap-3 mb-2">
                  <div className="bg-yellow-100 rounded-full p-2">
                    <Zap className="h-5 w-5 text-yellow-600" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Scope 2 (Electricity)</p>
                    <p className="text-2xl font-bold">{totalCarbonByScope[2] || 0} tCO2e</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center gap-3 mb-2">
                  <div className="bg-blue-100 rounded-full p-2">
                    <Truck className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Scope 3 (Value Chain)</p>
                    <p className="text-2xl font-bold">{totalCarbonByScope[3] || 0} tCO2e</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Emission Sources</CardTitle>
                <Button variant="outline" size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Entry
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {carbonData.map((entry) => (
                  <div key={entry.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center gap-4">
                      <div className={`rounded-full p-2 ${
                        entry.scope === 1 ? 'bg-red-100' : entry.scope === 2 ? 'bg-yellow-100' : 'bg-blue-100'
                      }`}>
                        {entry.scope === 1 ? <Factory className="h-4 w-4 text-red-600" /> :
                         entry.scope === 2 ? <Zap className="h-4 w-4 text-yellow-600" /> :
                         <Truck className="h-4 w-4 text-blue-600" />}
                      </div>
                      <div>
                        <p className="font-medium">{entry.source}</p>
                        <p className="text-sm text-muted-foreground">Scope {entry.scope}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-bold">{entry.emissions} {entry.unit}</p>
                      <p className="text-sm text-muted-foreground">{entry.period}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="targets" className="mt-6">
          <div className="space-y-4">
            {targets.map((target) => (
              <Card key={target.id}>
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-start gap-3">
                      {getCategoryIcon(target.category)}
                      <div>
                        <h3 className="font-medium">{target.name}</h3>
                        <p className="text-sm text-muted-foreground">{target.description}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">
                        {new Date(target.deadline).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span>Progress</span>
                      <span className="font-medium">{target.progress}%</span>
                    </div>
                    <Progress value={target.progress} />
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span>Current: {target.current_value}</span>
                      <span>Target: {target.target_value}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="suppliers" className="mt-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Supplier ESG Assessments</CardTitle>
                <Button variant="outline" size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Assessment
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {suppliers.map((supplier) => (
                  <div key={supplier.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center gap-4">
                      <div className={`rounded-full p-3 ${
                        supplier.risk_level === 'low' ? 'bg-green-100' :
                        supplier.risk_level === 'medium' ? 'bg-yellow-100' : 'bg-red-100'
                      }`}>
                        <Building2 className={`h-5 w-5 ${
                          supplier.risk_level === 'low' ? 'text-green-600' :
                          supplier.risk_level === 'medium' ? 'text-yellow-600' : 'text-red-600'
                        }`} />
                      </div>
                      <div>
                        <p className="font-medium">{supplier.supplier_name}</p>
                        <div className="flex items-center gap-2 mt-1">
                          {supplier.categories.map((cat, idx) => (
                            <Badge key={idx} variant="outline" className="text-xs">{cat}</Badge>
                          ))}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-6">
                      <div className="text-center">
                        <p className="text-2xl font-bold">{supplier.score}</p>
                        <p className="text-xs text-muted-foreground">ESG Score</p>
                      </div>
                      {getRiskBadge(supplier.risk_level)}
                      <p className="text-sm text-muted-foreground">
                        Assessed: {new Date(supplier.last_assessed).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="reports" className="mt-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>ESG Reports</CardTitle>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Create Report
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {reports.map((report) => (
                  <div key={report.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center gap-4">
                      <div className="bg-muted rounded-full p-3">
                        <FileText className="h-5 w-5" />
                      </div>
                      <div>
                        <p className="font-medium">{report.name}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge variant="outline" className="text-xs">{report.framework}</Badge>
                          <span className="text-sm text-muted-foreground">{report.period}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <Badge variant={
                        report.status === 'published' ? 'default' :
                        report.status === 'in-review' ? 'secondary' : 'outline'
                      }>
                        {report.status}
                      </Badge>
                      <Button variant="outline" size="sm">
                        <Download className="h-4 w-4 mr-2" />
                        Download
                      </Button>
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
