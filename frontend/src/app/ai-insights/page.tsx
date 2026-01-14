'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  SparklesIcon,
  ExclamationTriangleIcon,
  LightBulbIcon,
  DocumentTextIcon,
  ChartBarIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';

import {
  aiInsightsAPI,
  ChurnPrediction,
  NextBestAction,
  AIGeneratedContent,
} from '@/lib/new-features-api';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export interface ChurnStatistics {
  total_predictions: number;
  critical_risk: number;
  high_risk: number;
  medium_risk: number;
  low_risk: number;
  average_probability: number;
  predictions_last_updated: string;
}

export default function Page() {
  const [activeTab, setActiveTab] = useState<'churn' | 'actions' | 'content'>('churn');
  const [loading, setLoading] = useState(true);
  
  // Churn predictions
  const [churnPredictions, setChurnPredictions] = useState<ChurnPrediction[]>([]);
  const [churnStats, setChurnStats] = useState<ChurnStatistics | null>(null);
  
  // Next best actions
  const [nextBestActions, setNextBestActions] = useState<NextBestAction[]>([]);
  
  // AI generated content
  const [generatedContent, setGeneratedContent] = useState<AIGeneratedContent[]>([]);
  const [generating, setGenerating] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      if (activeTab === 'churn') {
        const [predictionsRes, statsRes] = await Promise.all([
          aiInsightsAPI.getChurnPredictions({ ordering: '-churn_probability' }),
          aiInsightsAPI.getChurnStatistics(),
        ]);
        setChurnPredictions(predictionsRes.data.results || predictionsRes.data);
        setChurnStats(statsRes.data);
      } else if (activeTab === 'actions') {
        const response = await aiInsightsAPI.getNextBestActions({ 
          status: 'pending',
          ordering: '-priority'
        });
        setNextBestActions(response.data.results || response.data);
      } else if (activeTab === 'content') {
        const response = await aiInsightsAPI.getGeneratedContent({ 
          ordering: '-created_at'
        });
        setGeneratedContent(response.data.results || response.data);
      }
    } catch (error) {
      console.error('Failed to load AI insights:', error);
    } finally {
      setLoading(false);
    }
  }, [activeTab]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleBulkPredictChurn = async () => {
    if (!confirm('This will analyze all contacts for churn risk. Continue?')) {
      return;
    }
    
    setLoading(true);
    try {
      await aiInsightsAPI.bulkPredictChurn();
      alert('Churn prediction started! This may take a few minutes.');
      await loadData();
    } catch (error) {
      console.error('Failed to predict churn:', error);
      alert('Failed to start churn prediction.');
    } finally {
      setLoading(false);
    }
  };

  const handleCompleteAction = async (id: string) => {
    try {
      await aiInsightsAPI.completeAction(id);
      alert('Action marked as completed!');
      await loadData();
    } catch (error) {
      console.error('Failed to complete action:', error);
      alert('Failed to complete action.');
    }
  };

  const handleDismissAction = async (id: string) => {
    try {
      await aiInsightsAPI.dismissAction(id);
      await loadData();
    } catch (error) {
      console.error('Failed to dismiss action:', error);
      alert('Failed to dismiss action.');
    }
  };

  const handleGenerateContent = async (contentType: string) => {
    setGenerating(true);
    try {
      await aiInsightsAPI.generateContent({
        content_type: contentType,
        context: {},
        tone: 'professional',
        length: 'medium',
      });
      alert('Content generated successfully!');
      await loadData();
    } catch (error) {
      console.error('Failed to generate content:', error);
      alert('Failed to generate content.');
    } finally {
      setGenerating(false);
    }
  };

  const handleApproveContent = async (id: string) => {
    try {
      await aiInsightsAPI.approveContent(id);
      alert('Content approved!');
      await loadData();
    } catch (error) {
      console.error('Failed to approve content:', error);
      alert('Failed to approve content.');
    }
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return 'bg-red-100 text-red-800';
      case 'high':
        return 'bg-orange-100 text-orange-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <ProtectedRoute>
        <MainLayout>
          <div className="flex items-center justify-center h-96">
            <ArrowPathIcon className="w-12 h-12 text-blue-600 animate-spin" />
          </div>
        </MainLayout>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-6 max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                  <SparklesIcon className="w-10 h-10 text-purple-600" />
                  AI Insights
                </h1>
                <p className="text-gray-600 mt-2">
                  AI-powered predictions and recommendations for better decision making
                </p>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200 mb-6">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('churn')}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2 transition-colors ${
                  activeTab === 'churn'
                    ? 'border-purple-500 text-purple-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <ExclamationTriangleIcon className="w-5 h-5" />
                Churn Predictions
              </button>
              <button
                onClick={() => setActiveTab('actions')}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2 transition-colors ${
                  activeTab === 'actions'
                    ? 'border-purple-500 text-purple-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <LightBulbIcon className="w-5 h-5" />
                Next Best Actions
              </button>
              <button
                onClick={() => setActiveTab('content')}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2 transition-colors ${
                  activeTab === 'content'
                    ? 'border-purple-500 text-purple-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <DocumentTextIcon className="w-5 h-5" />
                AI Content
              </button>
            </nav>
          </div>

          {/* Churn Predictions Tab */}
          {activeTab === 'churn' && (
            <div className="space-y-6">
              {/* Stats Cards */}
              {churnStats && (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <Card>
                    <CardHeader className="pb-2">
                      <CardDescription>Total Analyzed</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">{churnStats.total_predictions || 0}</div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-2">
                      <CardDescription>Critical Risk</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold text-red-600">{churnStats.critical_risk || 0}</div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-2">
                      <CardDescription>High Risk</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold text-orange-600">{churnStats.high_risk || 0}</div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-2">
                      <CardDescription>Avg. Risk Score</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">
                        {churnStats.average_probability 
                          ? `${(churnStats.average_probability * 100).toFixed(1)  }%`
                          : '0%'}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}

              {/* Action Button */}
              <div className="flex justify-end">
                <Button onClick={handleBulkPredictChurn}>
                  <ArrowPathIcon className="w-4 h-4 mr-2" />
                  Analyze All Contacts
                </Button>
              </div>

              {/* Predictions List */}
              <div className="space-y-4">
                {churnPredictions.length === 0 ? (
                  <Card className="p-12 text-center">
                    <ChartBarIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">No predictions yet</h3>
                    <p className="text-gray-600 mb-6">
                      Run churn analysis to identify at-risk contacts
                    </p>
                  </Card>
                ) : (
                  churnPredictions.map((prediction) => (
                    <Card key={prediction.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-6">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <h3 className="text-lg font-semibold">{prediction.contact.name}</h3>
                              <Badge className={getRiskColor(prediction.risk_level)}>
                                {prediction.risk_level.toUpperCase()} RISK
                              </Badge>
                            </div>
                            <p className="text-sm text-gray-600 mb-4">{prediction.contact.email}</p>
                            
                            <div className="mb-4">
                              <div className="flex items-center justify-between mb-2">
                                <span className="text-sm font-medium">Churn Probability</span>
                                <span className="text-sm font-bold">
                                  {(prediction.churn_probability * 100).toFixed(1)}%
                                </span>
                              </div>
                              <div className="w-full bg-gray-200 rounded-full h-2">
                                <div
                                  className={`h-2 rounded-full ${
                                    prediction.churn_probability > 0.7
                                      ? 'bg-red-600'
                                      : prediction.churn_probability > 0.5
                                      ? 'bg-orange-500'
                                      : prediction.churn_probability > 0.3
                                      ? 'bg-yellow-500'
                                      : 'bg-green-500'
                                  }`}
                                  style={{ width: `${prediction.churn_probability * 100}%` }}
                                ></div>
                              </div>
                            </div>

                            {prediction.recommended_actions.length > 0 && (
                              <div>
                                <p className="text-sm font-medium mb-2">Recommended Actions:</p>
                                <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                                  {prediction.recommended_actions.slice(0, 3).map((action, idx) => (
                                    <li key={idx}>{action}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))
                )}
              </div>
            </div>
          )}

          {/* Next Best Actions Tab */}
          {activeTab === 'actions' && (
            <div className="space-y-4">
              {nextBestActions.length === 0 ? (
                <Card className="p-12 text-center">
                  <LightBulbIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">No pending actions</h3>
                  <p className="text-gray-600">AI will suggest actions based on contact activity</p>
                </Card>
              ) : (
                nextBestActions.map((action) => (
                  <Card key={action.id} className="hover:shadow-md transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <Badge className={getPriorityColor(action.priority)}>
                              {action.priority.toUpperCase()}
                            </Badge>
                            <h3 className="text-lg font-semibold">{action.title}</h3>
                          </div>
                          <p className="text-sm text-gray-600 mb-2">
                            <strong>Contact:</strong> {action.contact.name} ({action.contact.email})
                          </p>
                          <p className="text-sm text-gray-700 mb-3">{action.description}</p>
                          <div className="bg-blue-50 p-3 rounded-lg mb-3">
                            <p className="text-xs font-semibold text-blue-900 mb-1">AI Reasoning:</p>
                            <p className="text-xs text-blue-800">{action.reasoning}</p>
                          </div>
                          <div className="flex items-center gap-2 text-sm text-gray-600">
                            <ChartBarIcon className="w-4 h-4" />
                            <span>Estimated Impact: {(action.estimated_impact * 100).toFixed(0)}%</span>
                          </div>
                        </div>
                        <div className="flex flex-col gap-2">
                          <Button
                            size="sm"
                            onClick={() => handleCompleteAction(action.id)}
                          >
                            <CheckCircleIcon className="w-4 h-4 mr-1" />
                            Complete
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleDismissAction(action.id)}
                          >
                            <XMarkIcon className="w-4 h-4 mr-1" />
                            Dismiss
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          )}

          {/* AI Content Tab */}
          {activeTab === 'content' && (
            <div className="space-y-6">
              {/* Generate Content Buttons */}
              <div className="flex gap-3 flex-wrap">
                <Button onClick={() => handleGenerateContent('email')} disabled={generating}>
                  <DocumentTextIcon className="w-4 h-4 mr-2" />
                  Generate Email
                </Button>
                <Button onClick={() => handleGenerateContent('social_post')} disabled={generating}>
                  <DocumentTextIcon className="w-4 h-4 mr-2" />
                  Generate Social Post
                </Button>
                <Button onClick={() => handleGenerateContent('proposal')} disabled={generating}>
                  <DocumentTextIcon className="w-4 h-4 mr-2" />
                  Generate Proposal
                </Button>
              </div>

              {/* Generated Content List */}
              <div className="space-y-4">
                {generatedContent.length === 0 ? (
                  <Card className="p-12 text-center">
                    <DocumentTextIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">No generated content</h3>
                    <p className="text-gray-600">Use AI to generate emails, posts, and proposals</p>
                  </Card>
                ) : (
                  generatedContent.map((content) => (
                    <Card key={content.id} className="hover:shadow-md transition-shadow">
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <div>
                            <CardTitle className="capitalize">{content.content_type.replace('_', ' ')}</CardTitle>
                            <CardDescription>
                              Generated {new Date(content.created_at).toLocaleString()} • 
                              {content.tone} tone • {content.length} length
                            </CardDescription>
                          </div>
                          <Badge
                            className={
                              content.status === 'approved'
                                ? 'bg-green-100 text-green-800'
                                : content.status === 'rejected'
                                ? 'bg-red-100 text-red-800'
                                : 'bg-yellow-100 text-yellow-800'
                            }
                          >
                            {content.status}
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="bg-gray-50 p-4 rounded-lg mb-4">
                          <p className="text-sm text-gray-800 whitespace-pre-wrap">{content.content}</p>
                        </div>
                        {content.status === 'draft' && (
                          <div className="flex gap-2">
                            <Button onClick={() => handleApproveContent(content.id)}>
                              <CheckCircleIcon className="w-4 h-4 mr-2" />
                              Approve
                            </Button>
                            <Button variant="outline">
                              <ArrowPathIcon className="w-4 h-4 mr-2" />
                              Regenerate
                            </Button>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}

