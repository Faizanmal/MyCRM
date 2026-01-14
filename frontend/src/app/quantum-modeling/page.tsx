'use client';

import { useState, useEffect } from 'react';
import { 
  CpuChipIcon, 
  SparklesIcon, 
  ChartBarIcon, 
  ArrowPathIcon,
  BeakerIcon,
  RocketLaunchIcon
} from '@heroicons/react/24/outline';

import { quantumModelingAPI } from '@/lib/new-features-api';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface QuantumSimulation {
  id: string;
  name: string;
  status: string;
  progress: number;
  results?: Record<string, unknown>;
  simulation_type_display: string;
  description: string;
  qubits_requested: number;
  paths_simulated?: number;
  quantum_advantage_factor?: number;
  execution_time_ms?: number;
}

interface QuantumStatistics {
  total_simulations: number;
  success_rate: number;
  average_runtime: number;
  total_paths_simulated: number;
  average_quantum_advantage: number;
  running_simulations: number;
}

export default function QuantumModelingPage() {
  const [simulations, setSimulations] = useState<QuantumSimulation[]>([]);
  const [statistics, setStatistics] = useState<QuantumStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [simsRes, statsRes] = await Promise.all([
        quantumModelingAPI.getSimulations({ ordering: '-created_at' }),
        quantumModelingAPI.getStatistics()
      ]);
      setSimulations(simsRes.data.results || simsRes.data);
      setStatistics(statsRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const runQuickSimulation = async () => {
    setRunning(true);
    try {
      const result = await quantumModelingAPI.simulateCustomerPaths({
        customer_data: {
          engagement_score: 0.75,
          purchase_history: 3,
          interaction_frequency: 0.6
        },
        touchpoints: ['Email', 'Phone Call', 'Demo', 'Proposal', 'Follow-up', 'Meeting', 'Contract'],
        max_path_length: 8,
        num_qubits: 20,
        shot_count: 1000
      });
      
      alert(`Simulation Complete!\n\nPaths Simulated: ${result.data.paths_simulated.toLocaleString()}\nQuantum Advantage: ${result.data.quantum_advantage_factor.toFixed(1)}x faster\nExecution Time: ${result.data.execution_time_ms}ms`);
      loadData();
    } catch (error) {
      console.error('Error running simulation:', error);
      alert('Failed to run simulation');
    } finally {
      setRunning(false);
    }
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-6 space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold flex items-center gap-2">
                <CpuChipIcon className="w-8 h-8 text-purple-600" />
                Quantum-Accelerated Predictive Modeling
              </h1>
              <p className="text-gray-600 mt-1">
                Harness quantum computing for ultra-fast scenario modeling
              </p>
            </div>
            <Button 
              onClick={runQuickSimulation} 
              disabled={running}
              className="bg-purple-600 hover:bg-purple-700"
            >
              {running ? (
                <>
                  <ArrowPathIcon className="w-5 h-5 mr-2 animate-spin" />
                  Running...
                </>
              ) : (
                <>
                  <BeakerIcon className="w-5 h-5 mr-2" />
                  Quick Simulation
                </>
              )}
            </Button>
          </div>

          {/* Statistics Cards */}
          {statistics && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>Total Simulations</CardDescription>
                  <CardTitle className="text-3xl">{statistics.total_simulations || 0}</CardTitle>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>Paths Simulated</CardDescription>
                  <CardTitle className="text-3xl text-purple-600">
                    {(statistics.total_paths_simulated || 0).toLocaleString()}
                  </CardTitle>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>Avg Quantum Advantage</CardDescription>
                  <CardTitle className="text-3xl text-green-600">
                    {(statistics.average_quantum_advantage || 0).toFixed(1)}x
                  </CardTitle>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>Running Simulations</CardDescription>
                  <CardTitle className="text-3xl text-blue-600">
                    {statistics.running_simulations || 0}
                  </CardTitle>
                </CardHeader>
              </Card>
            </div>
          )}

          {/* Simulations List */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Simulations</CardTitle>
              <CardDescription>Your quantum computing simulations</CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8">Loading simulations...</div>
              ) : simulations.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <SparklesIcon className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                  <p>No simulations yet. Run your first quantum simulation!</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {simulations.map((sim) => (
                    <div key={sim.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h3 className="font-semibold text-lg">{sim.name}</h3>
                            <Badge variant={
                              sim.status === 'completed' ? 'default' :
                              sim.status === 'running' ? 'secondary' :
                              sim.status === 'failed' ? 'destructive' : 'outline'
                            }>
                              {sim.status}
                            </Badge>
                            <Badge variant="outline">{sim.simulation_type_display}</Badge>
                          </div>
                          <p className="text-sm text-gray-600 mb-3">{sim.description}</p>
                          <div className="grid grid-cols-4 gap-4 text-sm">
                            <div>
                              <span className="text-gray-500">Qubits:</span>
                              <span className="ml-2 font-medium">{sim.qubits_requested}</span>
                            </div>
                            <div>
                              <span className="text-gray-500">Paths:</span>
                              <span className="ml-2 font-medium">{(sim.paths_simulated || 0).toLocaleString()}</span>
                            </div>
                            <div>
                              <span className="text-gray-500">Advantage:</span>
                              <span className="ml-2 font-medium text-green-600">
                                {sim.quantum_advantage_factor ? `${sim.quantum_advantage_factor.toFixed(1)}x` : 'N/A'}
                              </span>
                            </div>
                            <div>
                              <span className="text-gray-500">Time:</span>
                              <span className="ml-2 font-medium">{sim.execution_time_ms || 0}ms</span>
                            </div>
                          </div>
                        </div>
                        <div className="ml-4">
                          {sim.status === 'completed' && (
                            <Button variant="outline" size="sm">
                              <ChartBarIcon className="w-4 h-4 mr-2" />
                              View Results
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Info Card */}
          <Card className="bg-linear-to-r from-purple-50 to-blue-50 border-purple-200">
            <CardContent className="pt-6">
              <div className="flex items-start gap-4">
                <RocketLaunchIcon className="w-12 h-12 text-purple-600 shrink-0" />
                <div>
                  <h3 className="font-semibold text-lg mb-2">Quantum Computing Advantage</h3>
                  <p className="text-gray-700 mb-3">
                    Quantum algorithms can explore millions of customer interaction paths simultaneously,
                    providing insights that classical computers would take hours or days to compute.
                  </p>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• Simulate complex scenario modeling in seconds</li>
                    <li>• Forecast deal closures with exponential path exploration</li>
                    <li>• Analyze market shifts using quantum interference patterns</li>
                    <li>• Run what-if analyses at unprecedented scale</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}

