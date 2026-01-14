'use client';

import { useState, useEffect } from 'react';
import { ShieldCheckIcon, ExclamationTriangleIcon, CheckCircleIcon, Cog6ToothIcon } from '@heroicons/react/24/outline';

import { ethicalAIAPI } from '@/lib/new-features-api';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface BiasDetection {
  id: string;
  model_name: string;
  bias_score: number;
  detected_at: string;
  status: string;
  severity: string;
  bias_type: string;
  detection_date: string;
  confidence_score: number;
  is_resolved: boolean;
  affected_groups?: string[];
  mitigation_recommendations?: string[];
}

interface DecisionAudit {
  id: string;
  decision: string;
  confidence: number;
  ethical_score: number;
  audited_at: string;
  model_name: string;
  decision_type: string;
  flagged_for_review: boolean;
  timestamp: string;
  confidence_score: number;
  explanation: string;
}

export default function EthicalAIPage() {
  const [biasDetections, setBiasDetections] = useState<BiasDetection[]>([]);
  const [audits, setAudits] = useState<DecisionAudit[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [biasRes, auditRes] = await Promise.all([
        ethicalAIAPI.getBiasDetections({ ordering: '-detection_date' }),
        ethicalAIAPI.getDecisionAudits({ ordering: '-timestamp' })
      ]);
      setBiasDetections(biasRes.data.results || biasRes.data);
      setAudits(auditRes.data.results || auditRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-600';
      case 'high': return 'bg-orange-600';
      case 'medium': return 'bg-yellow-600';
      default: return 'bg-blue-600';
    }
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-6 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold flex items-center gap-2">
                <ShieldCheckIcon className="w-8 h-8 text-blue-600" />
                Ethical AI Oversight Dashboard
              </h1>
              <p className="text-gray-600 mt-1">
                Monitor AI decisions for bias and ensure fair, explainable outcomes
              </p>
            </div>
            <Button variant="outline">
              <Cog6ToothIcon className="w-5 h-5 mr-2" />
              Configure Ethics Settings
            </Button>
          </div>

          {/* Bias Detections */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ExclamationTriangleIcon className="w-5 h-5 text-orange-600" />
                Bias Detections
              </CardTitle>
              <CardDescription>AI models flagged for potential bias</CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8">Loading...</div>
              ) : biasDetections.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <CheckCircleIcon className="w-16 h-16 mx-auto mb-4 text-green-500" />
                  <p>No bias detected in AI models</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {biasDetections.map((detection) => (
                    <div key={detection.id} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <h3 className="font-semibold">{detection.model_name}</h3>
                            <Badge className={getSeverityColor(detection.severity)}>
                              {detection.severity}
                            </Badge>
                            <Badge variant="outline">{detection.bias_type}</Badge>
                          </div>
                          <p className="text-sm text-gray-600 mb-2">
                            Detected: {new Date(detection.detection_date).toLocaleString()}
                          </p>
                          <div className="text-sm">
                            <span className="font-medium">Confidence: </span>
                            {(detection.confidence_score * 100).toFixed(1)}%
                          </div>
                        </div>
                        {detection.is_resolved ? (
                          <Badge className="bg-green-600">Resolved</Badge>
                        ) : (
                          <Button size="sm">Review</Button>
                        )}
                      </div>
                      
                      {detection.affected_groups && detection.affected_groups.length > 0 && (
                        <div className="mt-3 p-3 bg-orange-50 rounded">
                          <div className="text-sm font-medium mb-1">Affected Groups:</div>
                          <div className="flex flex-wrap gap-2">
                            {detection.affected_groups.map((group: string, idx: number) => (
                              <Badge key={idx} variant="secondary">{group}</Badge>
                            ))}
                          </div>
                        </div>
                      )}

                      {detection.mitigation_recommendations && detection.mitigation_recommendations.length > 0 && (
                        <div className="mt-3">
                          <div className="text-sm font-medium mb-2">Recommendations:</div>
                          <ul className="text-sm text-gray-600 space-y-1">
                            {detection.mitigation_recommendations.map((rec: string, idx: number) => (
                              <li key={idx}>• {rec}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Decision Audits */}
          <Card>
            <CardHeader>
              <CardTitle>Recent AI Decision Audits</CardTitle>
              <CardDescription>Explainable AI decisions with transparency</CardDescription>
            </CardHeader>
            <CardContent>
              {audits.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No decision audits available
                </div>
              ) : (
                <div className="space-y-3">
                  {audits.slice(0, 5).map((audit) => (
                    <div key={audit.id} className="border-b pb-3 last:border-0">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-medium">{audit.model_name}</span>
                            <Badge variant="outline">{audit.decision_type}</Badge>
                            {audit.flagged_for_review && (
                              <Badge variant="destructive">Flagged</Badge>
                            )}
                          </div>
                          <div className="text-sm text-gray-600">
                            {new Date(audit.timestamp).toLocaleString()}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm">
                            Confidence: {(audit.confidence_score * 100).toFixed(1)}%
                          </div>
                        </div>
                      </div>
                      <div className="text-sm text-gray-700 bg-gray-50 p-2 rounded">
                        {audit.explanation}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Info */}
          <Card className="bg-linear-to-r from-blue-50 to-purple-50 border-blue-200">
            <CardContent className="pt-6">
              <h3 className="font-semibold text-lg mb-3">Ethical AI Features</h3>
              <ul className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-gray-700">
                <li className="flex items-start gap-2">
                  <CheckCircleIcon className="w-5 h-5 text-green-600 shrink-0" />
                  <span>Real-time bias detection across all AI models</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircleIcon className="w-5 h-5 text-green-600 shrink-0" />
                  <span>Explainable AI decisions with full transparency</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircleIcon className="w-5 h-5 text-green-600 shrink-0" />
                  <span>User-controlled ethics sliders for model sensitivity</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircleIcon className="w-5 h-5 text-green-600 shrink-0" />
                  <span>Compliance with AI fairness regulations</span>
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}

