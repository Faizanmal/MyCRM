// Lead Scoring Dashboard Component
'use client';

import React, { useState, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { TrendingUp, Target, Flame, Users, BarChart3, RefreshCw } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import axios from 'axios';

interface Lead {
  id: string;
  name: string;
  email: string;
  company?: string;
  score: number;
  score_category: 'hot' | 'warm' | 'cold';
  scoring_factors: Record<string, number>;
}

interface ScoreDistribution {
  hot: number;
  warm: number;
  cold: number;
}

export default function LeadScoringDashboard() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [distribution, setDistribution] = useState<ScoreDistribution>({ hot: 0, warm: 0, cold: 0 });
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const loadLeads = useCallback(async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/core/lead-scores/');
      setLeads(response.data);
      calculateDistribution(response.data);
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load lead scores';
      console.error('Load leads error:', errorMessage);
      toast({
        title: 'Error',
        description: errorMessage,
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  }, [toast]);

  React.useEffect(() => {
    loadLeads();
  }, [loadLeads]);

  const calculateDistribution = (leads: Lead[]) => {
    const dist = leads.reduce((acc, lead) => {
      acc[lead.score_category] = (acc[lead.score_category] || 0) + 1;
      return acc;
    }, { hot: 0, warm: 0, cold: 0 } as ScoreDistribution);
    setDistribution(dist);
  };

  const recalculateScores = async () => {
    setLoading(true);
    try {
      await axios.post('/api/core/lead-scores/recalculate/');
      toast({
        title: 'Success',
        description: 'Lead scores recalculated',
      });
      loadLeads();
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to recalculate scores';
      console.error('Recalculate scores error:', errorMessage);
      toast({
        title: 'Error',
        description: errorMessage,
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const hotLeads = leads.filter(l => l.score_category === 'hot').slice(0, 10);
  const warmLeads = leads.filter(l => l.score_category === 'warm').slice(0, 10);
  const coldLeads = leads.filter(l => l.score_category === 'cold').slice(0, 10);

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Target className="h-8 w-8" />
            Lead Scoring Dashboard
          </h1>
          <CardDescription>Analyze and manage qualified leads by scoring</CardDescription>
        </div>
        <Button onClick={recalculateScores} disabled={loading}>
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Recalculate Scores
        </Button>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Leads</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Users className="h-5 w-5 text-blue-500" />
              <p className="text-3xl font-bold">{leads.length}</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Hot Leads</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Flame className="h-5 w-5 text-red-500" />
              <p className="text-3xl font-bold text-red-500">{distribution.hot}</p>
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {leads.length > 0 ? ((distribution.hot / leads.length) * 100).toFixed(1) : 0}% of total
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Warm Leads</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-orange-500" />
              <p className="text-3xl font-bold text-orange-500">{distribution.warm}</p>
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {leads.length > 0 ? ((distribution.warm / leads.length) * 100).toFixed(1) : 0}% of total
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Cold Leads</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-blue-500" />
              <p className="text-3xl font-bold text-blue-500">{distribution.cold}</p>
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {leads.length > 0 ? ((distribution.cold / leads.length) * 100).toFixed(1) : 0}% of total
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Lead Lists by Category */}
      <Tabs defaultValue="hot" className="space-y-4">
        <TabsList>
          <TabsTrigger value="hot">
            <Flame className="h-4 w-4 mr-2" />
            Hot Leads ({distribution.hot})
          </TabsTrigger>
          <TabsTrigger value="warm">
            <TrendingUp className="h-4 w-4 mr-2" />
            Warm Leads ({distribution.warm})
          </TabsTrigger>
          <TabsTrigger value="cold">
            <BarChart3 className="h-4 w-4 mr-2" />
            Cold Leads ({distribution.cold})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="hot" className="space-y-4">
          <LeadList leads={hotLeads} category="hot" />
        </TabsContent>

        <TabsContent value="warm" className="space-y-4">
          <LeadList leads={warmLeads} category="warm" />
        </TabsContent>

        <TabsContent value="cold" className="space-y-4">
          <LeadList leads={coldLeads} category="cold" />
        </TabsContent>
      </Tabs>
    </div>
  );
}

// Lead List Component
function LeadList({ leads, category }: { leads: Lead[]; category: string }) {
  const getBadgeVariant = (cat: string) => {
    switch (cat) {
      case 'hot': return 'destructive';
      case 'warm': return 'default';
      default: return 'secondary';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-red-500';
    if (score >= 60) return 'text-orange-500';
    return 'text-blue-500';
  };

  if (leads.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center text-muted-foreground">
          <p>No {category} leads found</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-3">
      {leads.map(lead => (
        <Card key={lead.id}>
          <CardContent className="pt-6">
            <div className="flex justify-between items-start mb-4">
              <div className="flex-1">
                <h3 className="font-semibold text-lg">{lead.name}</h3>
                <p className="text-sm text-muted-foreground">{lead.email}</p>
                {lead.company && (
                  <p className="text-sm text-muted-foreground">{lead.company}</p>
                )}
              </div>
              <div className="text-right">
                <Badge variant={getBadgeVariant(lead.score_category)}>
                  {lead.score_category.toUpperCase()}
                </Badge>
                <p className={`text-3xl font-bold mt-2 ${getScoreColor(lead.score)}`}>
                  {lead.score}
                </p>
                <p className="text-xs text-muted-foreground">Score</p>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center text-sm">
                <span className="text-muted-foreground">Overall Score</span>
                <span className="font-medium">{lead.score}/100</span>
              </div>
              <Progress value={lead.score} className="h-2" />
            </div>

            {lead.scoring_factors && Object.keys(lead.scoring_factors).length > 0 && (
              <div className="mt-4 pt-4 border-t">
                <p className="text-sm font-medium mb-2">Scoring Factors</p>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(lead.scoring_factors).slice(0, 6).map(([factor, value]) => (
                    <div key={factor} className="flex justify-between text-xs">
                      <span className="text-muted-foreground capitalize">
                        {factor.replace(/_/g, ' ')}
                      </span>
                      <span className="font-medium">+{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="mt-4 flex gap-2">
              <Button size="sm" className="flex-1">View Details</Button>
              <Button size="sm" variant="outline" className="flex-1">Contact</Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
