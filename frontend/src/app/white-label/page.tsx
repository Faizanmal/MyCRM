"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { 
  Package, Users, DollarSign, 
  CheckCircle, XCircle, Clock, Palette, Globe,
  Building2, Download, Plus, Edit,
  ArrowUpRight, AlertCircle, Star
} from "lucide-react";

interface Subscription {
  id: number;
  organization_name: string;
  plan: string;
  status: "active" | "trial" | "past_due" | "cancelled";
  mrr: number;
  users: number;
  started_at: string;
  next_billing: string;
  custom_domain: string | null;
}

interface Plan {
  id: number;
  name: string;
  price: number;
  billing_period: "monthly" | "yearly";
  features: string[];
  user_limit: number;
  popular: boolean;
}

interface UsageMetric {
  metric: string;
  current: number;
  limit: number;
  unit: string;
}

export default function WhiteLabelBillingPage() {
  const [subscriptions] = useState<Subscription[]>([
    { id: 1, organization_name: "TechCorp Solutions", plan: "Enterprise", status: "active", mrr: 2999, users: 75, started_at: "2024-06-15", next_billing: "2025-12-15", custom_domain: "crm.techcorp.com" },
    { id: 2, organization_name: "StartupXYZ", plan: "Professional", status: "active", mrr: 499, users: 15, started_at: "2025-03-01", next_billing: "2025-12-01", custom_domain: null },
    { id: 3, organization_name: "Global Partners Inc", plan: "Enterprise", status: "trial", mrr: 0, users: 25, started_at: "2025-11-20", next_billing: "2025-12-20", custom_domain: "sales.globalpartners.io" },
    { id: 4, organization_name: "Local Business LLC", plan: "Starter", status: "past_due", mrr: 99, users: 5, started_at: "2025-01-10", next_billing: "2025-11-10", custom_domain: null },
  ]);

  const [plans] = useState<Plan[]>([
    { id: 1, name: "Starter", price: 99, billing_period: "monthly", user_limit: 5, popular: false, features: ["Basic CRM", "Email Integration", "5 Users", "1GB Storage", "Email Support"] },
    { id: 2, name: "Professional", price: 499, billing_period: "monthly", user_limit: 25, popular: true, features: ["Everything in Starter", "AI Insights", "25 Users", "10GB Storage", "API Access", "Priority Support"] },
    { id: 3, name: "Enterprise", price: 2999, billing_period: "monthly", user_limit: -1, popular: false, features: ["Everything in Pro", "White Label", "Unlimited Users", "Unlimited Storage", "Custom Integrations", "Dedicated Support", "SLA Guarantee"] },
  ]);

  const [usageMetrics] = useState<UsageMetric[]>([
    { metric: "API Calls", current: 45000, limit: 100000, unit: "calls/month" },
    { metric: "Storage", current: 12.5, limit: 50, unit: "GB" },
    { metric: "Email Sends", current: 8500, limit: 25000, unit: "emails/month" },
    { metric: "Active Users", current: 120, limit: 150, unit: "users" },
  ]);

  const [brandSettings, setBrandSettings] = useState({
    primary_color: "#6366f1",
    logo_url: "/logo.png",
    company_name: "MyCRM Pro",
    custom_domain: "app.mycrm.com",
    email_from: "noreply@mycrm.com",
    hide_powered_by: true,
  });

  const totalMRR = subscriptions.filter(s => s.status === "active").reduce((sum, s) => sum + s.mrr, 0);
  const totalUsers = subscriptions.reduce((sum, s) => sum + s.users, 0);
  const activeSubscriptions = subscriptions.filter(s => s.status === "active").length;
  const churnRisk = subscriptions.filter(s => s.status === "past_due").length;

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active": return "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400";
      case "trial": return "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400";
      case "past_due": return "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400";
      case "cancelled": return "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400";
      default: return "bg-gray-100 text-gray-700";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "active": return <CheckCircle className="w-4 h-4" />;
      case "trial": return <Clock className="w-4 h-4" />;
      case "past_due": return <AlertCircle className="w-4 h-4" />;
      case "cancelled": return <XCircle className="w-4 h-4" />;
      default: return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">
            White Label & Billing
          </h1>
          <p className="text-muted-foreground mt-1">
            Manage subscriptions, billing, and white-label customization
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Export Report
          </Button>
          <Button className="bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-700 hover:to-orange-700">
            <Plus className="w-4 h-4 mr-2" />
            New Subscription
          </Button>
        </div>
      </div>

      {/* Revenue Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-950/50 dark:to-green-900/30 border-green-200 dark:border-green-800">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-green-600 dark:text-green-400">Monthly Revenue</p>
                <p className="text-3xl font-bold text-green-700 dark:text-green-300">${totalMRR.toLocaleString()}</p>
              </div>
              <DollarSign className="w-10 h-10 text-green-500 opacity-80" />
            </div>
            <div className="flex items-center gap-1 text-xs text-green-600/70 dark:text-green-400/70 mt-2">
              <ArrowUpRight className="w-3 h-3" />
              +12% vs last month
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950/50 dark:to-blue-900/30 border-blue-200 dark:border-blue-800">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-blue-600 dark:text-blue-400">Active Subscriptions</p>
                <p className="text-3xl font-bold text-blue-700 dark:text-blue-300">{activeSubscriptions}</p>
              </div>
              <Package className="w-10 h-10 text-blue-500 opacity-80" />
            </div>
            <p className="text-xs text-blue-600/70 dark:text-blue-400/70 mt-2">
              {subscriptions.filter(s => s.status === "trial").length} in trial
            </p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-950/50 dark:to-purple-900/30 border-purple-200 dark:border-purple-800">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-purple-600 dark:text-purple-400">Total Users</p>
                <p className="text-3xl font-bold text-purple-700 dark:text-purple-300">{totalUsers}</p>
              </div>
              <Users className="w-10 h-10 text-purple-500 opacity-80" />
            </div>
            <p className="text-xs text-purple-600/70 dark:text-purple-400/70 mt-2">
              Across all organizations
            </p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-red-50 to-red-100 dark:from-red-950/50 dark:to-red-900/30 border-red-200 dark:border-red-800">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-red-600 dark:text-red-400">Churn Risk</p>
                <p className="text-3xl font-bold text-red-700 dark:text-red-300">{churnRisk}</p>
              </div>
              <AlertCircle className="w-10 h-10 text-red-500 opacity-80" />
            </div>
            <p className="text-xs text-red-600/70 dark:text-red-400/70 mt-2">
              Past due accounts
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="subscriptions" className="space-y-4">
        <TabsList className="bg-muted/50">
          <TabsTrigger value="subscriptions">Subscriptions</TabsTrigger>
          <TabsTrigger value="plans">Plans & Pricing</TabsTrigger>
          <TabsTrigger value="usage">Usage & Limits</TabsTrigger>
          <TabsTrigger value="branding">White Label</TabsTrigger>
        </TabsList>

        {/* Subscriptions Tab */}
        <TabsContent value="subscriptions" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Active Subscriptions</CardTitle>
                  <CardDescription>Manage customer subscriptions and billing</CardDescription>
                </div>
                <Input placeholder="Search organizations..." className="w-[250px]" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {subscriptions.map((sub) => (
                  <div key={sub.id} className="p-4 rounded-lg border bg-card hover:shadow-md transition-all">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-4">
                        <div className="p-3 rounded-lg bg-amber-100 dark:bg-amber-900/30">
                          <Building2 className="w-6 h-6 text-amber-600 dark:text-amber-400" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-semibold">{sub.organization_name}</h3>
                            <Badge className={getStatusColor(sub.status)}>
                              <span className="flex items-center gap-1">
                                {getStatusIcon(sub.status)}
                                {sub.status.replace("_", " ")}
                              </span>
                            </Badge>
                          </div>
                          <div className="flex items-center gap-4 text-sm text-muted-foreground">
                            <span className="flex items-center gap-1">
                              <Package className="w-3 h-3" />
                              {sub.plan}
                            </span>
                            <span className="flex items-center gap-1">
                              <Users className="w-3 h-3" />
                              {sub.users} users
                            </span>
                            {sub.custom_domain && (
                              <span className="flex items-center gap-1">
                                <Globe className="w-3 h-3" />
                                {sub.custom_domain}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                            ${sub.mrr.toLocaleString()}
                          </p>
                          <p className="text-xs text-muted-foreground">MRR</p>
                        </div>
                        <Button size="sm" variant="outline">
                          <Edit className="w-4 h-4 mr-2" />
                          Manage
                        </Button>
                      </div>
                    </div>
                    
                    <div className="mt-4 pt-4 border-t flex items-center justify-between text-sm">
                      <div className="flex items-center gap-4 text-muted-foreground">
                        <span>Started: {new Date(sub.started_at).toLocaleDateString()}</span>
                        <span>Next billing: {new Date(sub.next_billing).toLocaleDateString()}</span>
                      </div>
                      {sub.status === "past_due" && (
                        <Button size="sm" variant="destructive">
                          Send Reminder
                        </Button>
                      )}
                      {sub.status === "trial" && (
                        <Badge variant="outline" className="text-blue-600">
                          Trial ends in 7 days
                        </Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Plans & Pricing Tab */}
        <TabsContent value="plans" className="space-y-4">
          <div className="grid gap-6 md:grid-cols-3">
            {plans.map((plan) => (
              <Card key={plan.id} className={`relative ${plan.popular ? "border-amber-500 shadow-lg" : ""}`}>
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                    <Badge className="bg-amber-500 text-white">
                      <Star className="w-3 h-3 mr-1" />
                      Most Popular
                    </Badge>
                  </div>
                )}
                <CardHeader className="text-center pb-2">
                  <CardTitle className="text-xl">{plan.name}</CardTitle>
                  <div className="mt-4">
                    <span className="text-4xl font-bold">${plan.price}</span>
                    <span className="text-muted-foreground">/month</span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {plan.user_limit === -1 ? "Unlimited users" : `Up to ${plan.user_limit} users`}
                  </p>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3">
                    {plan.features.map((feature, idx) => (
                      <li key={idx} className="flex items-center gap-2 text-sm">
                        <CheckCircle className="w-4 h-4 text-green-500" />
                        {feature}
                      </li>
                    ))}
                  </ul>
                  <Button 
                    className={`w-full mt-6 ${plan.popular ? "bg-gradient-to-r from-amber-600 to-orange-600" : ""}`}
                    variant={plan.popular ? "default" : "outline"}
                  >
                    {plan.popular ? "Get Started" : "Choose Plan"}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold">Need a custom plan?</h3>
                  <p className="text-sm text-muted-foreground">
                    Contact us for volume discounts and custom enterprise solutions
                  </p>
                </div>
                <Button variant="outline">
                  Contact Sales
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Usage & Limits Tab */}
        <TabsContent value="usage" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {usageMetrics.map((metric, idx) => (
              <Card key={idx}>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold">{metric.metric}</h3>
                    <Badge variant={metric.current / metric.limit > 0.8 ? "destructive" : "secondary"}>
                      {((metric.current / metric.limit) * 100).toFixed(0)}% used
                    </Badge>
                  </div>
                  <Progress value={(metric.current / metric.limit) * 100} className="h-3 mb-2" />
                  <div className="flex items-center justify-between text-sm text-muted-foreground">
                    <span>{metric.current.toLocaleString()} used</span>
                    <span>{metric.limit.toLocaleString()} {metric.unit}</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
          
          <Card>
            <CardHeader>
              <CardTitle>Usage Alerts</CardTitle>
              <CardDescription>Configure notifications for usage thresholds</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {[
                { threshold: 80, enabled: true },
                { threshold: 90, enabled: true },
                { threshold: 100, enabled: true },
              ].map((alert, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                  <div className="flex items-center gap-2">
                    <AlertCircle className={`w-4 h-4 ${alert.threshold === 100 ? "text-red-500" : "text-yellow-500"}`} />
                    <span>Alert at {alert.threshold}% usage</span>
                  </div>
                  <Switch checked={alert.enabled} />
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        {/* White Label Tab */}
        <TabsContent value="branding" className="space-y-4">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Palette className="w-5 h-5" />
                  Brand Customization
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <Label>Company Name</Label>
                  <Input 
                    value={brandSettings.company_name} 
                    onChange={(e) => setBrandSettings({...brandSettings, company_name: e.target.value})}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label>Primary Brand Color</Label>
                  <div className="flex items-center gap-3">
                    <input 
                      type="color" 
                      value={brandSettings.primary_color}
                      onChange={(e) => setBrandSettings({...brandSettings, primary_color: e.target.value})}
                      className="w-12 h-12 rounded-lg cursor-pointer"
                    />
                    <Input 
                      value={brandSettings.primary_color}
                      onChange={(e) => setBrandSettings({...brandSettings, primary_color: e.target.value})}
                      className="flex-1"
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label>Logo URL</Label>
                  <div className="flex gap-2">
                    <Input 
                      value={brandSettings.logo_url}
                      onChange={(e) => setBrandSettings({...brandSettings, logo_url: e.target.value})}
                      className="flex-1"
                    />
                    <Button variant="outline">Upload</Button>
                  </div>
                </div>
                
                <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                  <div>
                    <p className="font-medium">Hide &#34;Powered by&#34; badge</p>
                    <p className="text-sm text-muted-foreground">Remove branding from customer-facing pages</p>
                  </div>
                  <Switch 
                    checked={brandSettings.hide_powered_by}
                    onCheckedChange={(checked) => setBrandSettings({...brandSettings, hide_powered_by: checked})}
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Globe className="w-5 h-5" />
                  Domain Settings
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <Label>Custom Domain</Label>
                  <Input 
                    value={brandSettings.custom_domain}
                    onChange={(e) => setBrandSettings({...brandSettings, custom_domain: e.target.value})}
                    placeholder="app.yourdomain.com"
                  />
                  <p className="text-xs text-muted-foreground">
                    Point your CNAME record to crm.platform.com
                  </p>
                </div>
                
                <div className="space-y-2">
                  <Label>Email From Address</Label>
                  <Input 
                    value={brandSettings.email_from}
                    onChange={(e) => setBrandSettings({...brandSettings, email_from: e.target.value})}
                    placeholder="noreply@yourdomain.com"
                  />
                </div>
                
                <div className="p-4 rounded-lg bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-800">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="w-4 h-4 text-green-600" />
                    <span className="font-medium text-green-700 dark:text-green-300">SSL Certificate Active</span>
                  </div>
                  <p className="text-sm text-green-600/80 dark:text-green-400/80">
                    Your custom domain is secured with auto-renewed SSL
                  </p>
                </div>
                
                <Button className="w-full bg-gradient-to-r from-amber-600 to-orange-600">
                  Save Brand Settings
                </Button>
              </CardContent>
            </Card>
          </div>
          
          <Card>
            <CardHeader>
              <CardTitle>Preview</CardTitle>
              <CardDescription>See how your brand customization will look</CardDescription>
            </CardHeader>
            <CardContent>
              <div 
                className="p-6 rounded-lg border"
                style={{ borderColor: brandSettings.primary_color }}
              >
                <div className="flex items-center gap-3 mb-4">
                  <div 
                    className="w-10 h-10 rounded-lg flex items-center justify-center text-white font-bold"
                    style={{ backgroundColor: brandSettings.primary_color }}
                  >
                    {brandSettings.company_name.charAt(0)}
                  </div>
                  <span className="text-xl font-bold">{brandSettings.company_name}</span>
                </div>
                <div className="flex gap-2">
                  <Button 
                    size="sm"
                    style={{ backgroundColor: brandSettings.primary_color }}
                    className="text-white"
                  >
                    Primary Button
                  </Button>
                  <Button 
                    size="sm" 
                    variant="outline"
                    style={{ borderColor: brandSettings.primary_color, color: brandSettings.primary_color }}
                  >
                    Secondary Button
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
