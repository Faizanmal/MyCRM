'use client';

import { useState, useEffect } from 'react';
import { GlobeAltIcon, CloudIcon, BoltIcon, CheckCircleIcon } from '@heroicons/react/24/outline';

import { carbonTrackingAPI } from '@/lib/new-features-api';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
// import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface CarbonFootprint {
  id: string;
  timestamp: string;
  activity: string;
  carbon_impact: number;
  category: string;
  interaction_type: string;
  carbon_grams: number;
  offset_applied: boolean;
}

interface CarbonStatistics {
  total_footprint: number;
  monthly_average: number;
  reduction_percentage: number;
  offset_amount: number;
  total_carbon_grams: number;
  offset_percentage: number;
  carbon_saved_grams: number;
}

export default function CarbonFootprintPage() {
  const [footprints, setFootprints] = useState<CarbonFootprint[]>([]);
  const [statistics, setStatistics] = useState<CarbonStatistics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [footprintsRes, statsRes] = await Promise.all([
        carbonTrackingAPI.getFootprints({ ordering: '-timestamp' }),
        carbonTrackingAPI.getStatistics().catch(() => ({ data: null }))
      ]);
      setFootprints(footprintsRes.data.results || footprintsRes.data);
      setStatistics(statsRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-6 space-y-6">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-2">
              <GlobeAltIcon className="w-8 h-8 text-green-600" />
              Carbon-Neutral Interaction Tracking
            </h1>
            <p className="text-gray-600 mt-1">
              Track and offset your digital carbon footprint
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-3">
                <CardDescription>Total Carbon</CardDescription>
                <CardTitle className="text-3xl">
                  {statistics?.total_carbon_grams ? `${statistics.total_carbon_grams.toFixed(2)}g` : '0g'}
                </CardTitle>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader className="pb-3">
                <CardDescription>Offset Applied</CardDescription>
                <CardTitle className="text-3xl text-green-600">
                  {statistics?.offset_percentage || 0}%
                </CardTitle>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader className="pb-3">
                <CardDescription>Carbon Savings</CardDescription>
                <CardTitle className="text-3xl text-blue-600">
                  {statistics?.carbon_saved_grams ? `${statistics.carbon_saved_grams.toFixed(2)}g` : '0g'}
                </CardTitle>
              </CardHeader>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Recent Interactions</CardTitle>
              <CardDescription>Carbon footprint by interaction type</CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8">Loading...</div>
              ) : footprints.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <CloudIcon className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                  <p>No carbon footprint data yet</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {footprints.map((fp, idx) => (
                    <div key={idx} className="flex items-center justify-between border-b pb-3">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                          <BoltIcon className="w-5 h-5 text-green-600" />
                        </div>
                        <div>
                          <div className="font-medium capitalize">{fp.interaction_type.replace('_', ' ')}</div>
                          <div className="text-sm text-gray-500">
                            {new Date(fp.timestamp).toLocaleString()}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold">{fp.carbon_grams.toFixed(2)}g CO₂</div>
                        {fp.offset_applied && (
                          <Badge className="bg-green-600 mt-1">
                            <CheckCircleIcon className="w-3 h-3 mr-1" />
                            Offset
                          </Badge>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="bg-linear-to-r from-green-50 to-blue-50 border-green-200">
            <CardContent className="pt-6">
              <h3 className="font-semibold text-lg mb-3">Carbon Tracking Benefits</h3>
              <ul className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-gray-700">
                <li>• Real-time carbon footprint monitoring</li>
                <li>• Automated offset suggestions</li>
                <li>• Low-impact alternative recommendations</li>
                <li>• Partnership with carbon credit marketplaces</li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}

