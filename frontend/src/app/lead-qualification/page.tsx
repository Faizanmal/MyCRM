'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Target, Award, Workflow, TrendingUp, Plus, Edit, Trash2,
  Play, Pause, BarChart3, Users, CheckCircle, XCircle
} from 'lucide-react';
import Link from 'next/link';

interface Lead {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  company?: string;
  status: string;
  score?: number;
  qualification_status?: string;
}

interface LeadScore {
  id: number;
  lead: Lead;
  total_score: number;
  qualification_status: string;
  last_calculated: string;
}

interface ScoringRule {
  id: number;
  name: string;
  field: string;
  operator: string;
  value: string;
  score: number;
  is_active: boolean;
}

interface QualificationCriteria {
  id: number;
  name: string;
  min_score: number;
  max_score: number;
  status_label: string;
  is_active: boolean;
}

export default function LeadQualificationPage() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'rules' | 'criteria' | 'workflows'>('dashboard');
  const [leadScores, setLeadScores] = useState<LeadScore[]>([]);
  const [scoringRules, setScoringRules] = useState<ScoringRule[]>([]);
  const [criteria, setCriteria] = useState<QualificationCriteria[]>([]);
  const [stats, setStats] = useState({
    total_leads: 0,
    mql_count: 0,
    sql_count: 0,
    opportunity_count: 0,
    avg_score: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Fetch data based on active tab
      if (activeTab === 'dashboard') {
        // Fetch lead scores and stats
        const scoresRes = await fetch('/api/lead-qualification/lead-scores/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        if (scoresRes.ok) {
          const data = await scoresRes.json();
          setLeadScores(data.results || data);
        }

        // Calculate stats
        const statsRes = await fetch('/api/lead-qualification/lead-scores/summary/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        if (statsRes.ok) {
          const statsData = await statsRes.json();
          setStats(statsData);
        }
      } else if (activeTab === 'rules') {
        const res = await fetch('/api/lead-qualification/scoring-rules/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        if (res.ok) {
          const data = await res.json();
          setScoringRules(data.results || data);
        }
      } else if (activeTab === 'criteria') {
        const res = await fetch('/api/lead-qualification/qualification-criteria/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        if (res.ok) {
          const data = await res.json();
          setCriteria(data.results || data);
        }
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getQualificationBadge = (status: string) => {
    const statusConfig: Record<string, { label: string; color: string }> = {
      unqualified: { label: 'Unqualified', color: 'bg-gray-500' },
      mql: { label: 'MQL', color: 'bg-blue-500' },
      sql: { label: 'SQL', color: 'bg-purple-500' },
      opportunity: { label: 'Opportunity', color: 'bg-green-500' },
      disqualified: { label: 'Disqualified', color: 'bg-red-500' }
    };
    const config = statusConfig[status] || statusConfig.unqualified;
    return <Badge className={config.color}>{config.label}</Badge>;
  };

  const renderDashboard = () => (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Leads</p>
              <p className="text-2xl font-bold">{stats.total_leads}</p>
            </div>
            <Users className="w-8 h-8 text-gray-400" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">MQLs</p>
              <p className="text-2xl font-bold text-blue-600">{stats.mql_count}</p>
            </div>
            <Target className="w-8 h-8 text-blue-400" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">SQLs</p>
              <p className="text-2xl font-bold text-purple-600">{stats.sql_count}</p>
            </div>
            <Award className="w-8 h-8 text-purple-400" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Opportunities</p>
              <p className="text-2xl font-bold text-green-600">{stats.opportunity_count}</p>
            </div>
            <TrendingUp className="w-8 h-8 text-green-400" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Avg Score</p>
              <p className="text-2xl font-bold">{stats.avg_score.toFixed(1)}</p>
            </div>
            <BarChart3 className="w-8 h-8 text-gray-400" />
          </div>
        </Card>
      </div>

      {/* Lead Scores Table */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Lead Scores</h3>
          <Button size="sm" variant="outline">
            <Play className="w-4 h-4 mr-2" />
            Recalculate All
          </Button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left p-3">Lead</th>
                <th className="text-left p-3">Company</th>
                <th className="text-left p-3">Score</th>
                <th className="text-left p-3">Qualification</th>
                <th className="text-left p-3">Last Calculated</th>
                <th className="text-left p-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {leadScores.map((score) => (
                <tr key={score.id} className="border-b hover:bg-gray-50">
                  <td className="p-3">
                    <Link href={`/leads/${score.lead.id}`} className="text-blue-600 hover:underline">
                      {score.lead.first_name} {score.lead.last_name}
                    </Link>
                    <div className="text-sm text-gray-500">{score.lead.email}</div>
                  </td>
                  <td className="p-3 text-sm">{score.lead.company || '-'}</td>
                  <td className="p-3">
                    <div className="flex items-center">
                      <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${Math.min(score.total_score, 100)}%` }}
                        />
                      </div>
                      <span className="font-semibold">{score.total_score}</span>
                    </div>
                  </td>
                  <td className="p-3">{getQualificationBadge(score.qualification_status)}</td>
                  <td className="p-3 text-sm text-gray-600">
                    {new Date(score.last_calculated).toLocaleDateString()}
                  </td>
                  <td className="p-3">
                    <Button size="sm" variant="ghost">View Details</Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );

  const renderRules = () => (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Scoring Rules</h3>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Add Rule
        </Button>
      </div>

      <div className="space-y-3">
        {scoringRules.map((rule) => (
          <div key={rule.id} className="border rounded-lg p-4 hover:bg-gray-50">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h4 className="font-semibold">{rule.name}</h4>
                  {rule.is_active ? (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  ) : (
                    <XCircle className="w-4 h-4 text-gray-400" />
                  )}
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  If <span className="font-mono bg-gray-100 px-1 rounded">{rule.field}</span>{' '}
                  <span className="font-mono bg-gray-100 px-1 rounded">{rule.operator}</span>{' '}
                  <span className="font-mono bg-gray-100 px-1 rounded">{rule.value}</span>{' '}
                  → Add <span className="font-semibold">{rule.score}</span> points
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Button size="sm" variant="ghost">
                  <Edit className="w-4 h-4" />
                </Button>
                <Button size="sm" variant="ghost">
                  {rule.is_active ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                </Button>
                <Button size="sm" variant="ghost">
                  <Trash2 className="w-4 h-4 text-red-600" />
                </Button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );

  const renderCriteria = () => (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Qualification Criteria</h3>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Add Criteria
        </Button>
      </div>

      <div className="space-y-3">
        {criteria.map((crit) => (
          <div key={crit.id} className="border rounded-lg p-4 hover:bg-gray-50">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h4 className="font-semibold">{crit.name}</h4>
                  {getQualificationBadge(crit.status_label.toLowerCase())}
                  {crit.is_active ? (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  ) : (
                    <XCircle className="w-4 h-4 text-gray-400" />
                  )}
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  Score Range: <span className="font-semibold">{crit.min_score}</span> to{' '}
                  <span className="font-semibold">{crit.max_score}</span>
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Button size="sm" variant="ghost">
                  <Edit className="w-4 h-4" />
                </Button>
                <Button size="sm" variant="ghost">
                  <Trash2 className="w-4 h-4 text-red-600" />
                </Button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );

  const renderWorkflows = () => (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Automation Workflows</h3>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Create Workflow
        </Button>
      </div>

      <div className="text-center py-12 text-gray-500">
        <Workflow className="w-16 h-16 mx-auto mb-4 text-gray-300" />
        <p>No workflows configured yet</p>
        <p className="text-sm mt-2">Create workflows to automate lead qualification actions</p>
      </div>
    </Card>
  );

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Lead Qualification & Scoring</h1>
        <p className="text-gray-600">
          Automatically score and qualify leads based on their behavior and attributes
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b mb-6">
        <div className="flex space-x-6">
          <button
            className={`pb-3 px-1 ${
              activeTab === 'dashboard'
                ? 'border-b-2 border-blue-600 text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
            onClick={() => setActiveTab('dashboard')}
          >
            <BarChart3 className="w-4 h-4 inline mr-2" />
            Dashboard
          </button>
          <button
            className={`pb-3 px-1 ${
              activeTab === 'rules'
                ? 'border-b-2 border-blue-600 text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
            onClick={() => setActiveTab('rules')}
          >
            <Target className="w-4 h-4 inline mr-2" />
            Scoring Rules
          </button>
          <button
            className={`pb-3 px-1 ${
              activeTab === 'criteria'
                ? 'border-b-2 border-blue-600 text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
            onClick={() => setActiveTab('criteria')}
          >
            <Award className="w-4 h-4 inline mr-2" />
            Qualification Criteria
          </button>
          <button
            className={`pb-3 px-1 ${
              activeTab === 'workflows'
                ? 'border-b-2 border-blue-600 text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
            onClick={() => setActiveTab('workflows')}
          >
            <Workflow className="w-4 h-4 inline mr-2" />
            Workflows
          </button>
        </div>
      </div>

      {/* Content */}
      {loading ? (
        <div className="text-center py-12">Loading...</div>
      ) : (
        <>
          {activeTab === 'dashboard' && renderDashboard()}
          {activeTab === 'rules' && renderRules()}
          {activeTab === 'criteria' && renderCriteria()}
          {activeTab === 'workflows' && renderWorkflows()}
        </>
      )}
    </div>
  );
}
