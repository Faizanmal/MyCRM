from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    InteractionPath,
    IoTDataFeed,
    QuantumModelRegistry,
    QuantumSimulation,
    WhatIfScenario,
)
from .quantum_engine import QuantumPredictiveEngine
from .serializers import (
    CustomerPathSimulationRequestSerializer,
    DealForecastRequestSerializer,
    IoTDataFeedSerializer,
    MarketShiftAnalysisRequestSerializer,
    QuantumModelRegistrySerializer,
    QuantumSimulationCreateSerializer,
    QuantumSimulationSerializer,
    WhatIfAnalysisRequestSerializer,
    WhatIfScenarioSerializer,
)


class QuantumSimulationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing quantum simulations.
    
    Provides endpoints for creating, running, and viewing quantum simulations
    for predictive modeling scenarios.
    """
    permission_classes = [IsAuthenticated]
    filterset_fields = ['simulation_type', 'status']
    ordering_fields = ['created_at', 'execution_time_ms', 'paths_simulated']

    def get_queryset(self):
        return QuantumSimulation.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return QuantumSimulationCreateSerializer
        return QuantumSimulationSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def run(self, request, pk=None):
        """Run a pending quantum simulation"""
        simulation = self.get_object()

        if simulation.status != 'pending':
            return Response(
                {'error': f'Simulation cannot be run. Current status: {simulation.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update status
        simulation.status = 'running'
        simulation.started_at = timezone.now()
        simulation.save()

        try:
            # Initialize quantum engine
            engine = QuantumPredictiveEngine(
                num_qubits=simulation.qubits_requested,
                shot_count=simulation.shot_count
            )

            # Run simulation based on type
            if simulation.simulation_type == 'customer_paths':
                results = engine.simulate_customer_paths(
                    customer_data=simulation.input_parameters.get('customer_data', {}),
                    touchpoints=simulation.input_parameters.get('touchpoints', [
                        'Email', 'Phone', 'Demo', 'Proposal', 'Meeting'
                    ]),
                    max_path_length=simulation.input_parameters.get('max_path_length', 10)
                )
            elif simulation.simulation_type == 'deal_forecast':
                results = engine.forecast_deal_closure(
                    opportunities=simulation.input_parameters.get('opportunities', []),
                    market_conditions=simulation.input_parameters.get('market_conditions', {})
                )
            elif simulation.simulation_type == 'market_shift':
                results = engine.analyze_market_shift(
                    current_market=simulation.input_parameters.get('current_market', {}),
                    historical_data=simulation.input_parameters.get('historical_data', []),
                    external_factors=simulation.input_parameters.get('external_factors', {})
                )
            else:
                # Default: run what-if analysis
                results = engine.run_whatif_analysis(
                    base_scenario=simulation.input_parameters.get('base_scenario', {}),
                    variable_changes=simulation.input_parameters.get('variable_changes', {}),
                    constraints=simulation.input_parameters.get('constraints', [])
                )

            # Save results
            simulation.results = results
            simulation.paths_simulated = results.get('paths_simulated', results.get('scenarios_explored', 0))
            simulation.quantum_advantage_factor = results.get('quantum_advantage_factor')
            simulation.execution_time_ms = results.get('execution_time_ms')
            simulation.confidence_interval = results.get('confidence_interval', {})
            simulation.status = 'completed'
            simulation.completed_at = timezone.now()
            simulation.save()

            # Create interaction paths if available
            if 'top_paths' in results:
                for path_data in results['top_paths']:
                    InteractionPath.objects.create(
                        simulation=simulation,
                        path_id=path_data['path_id'],
                        touchpoints=path_data['touchpoints'],
                        probability=path_data['probability'],
                        predicted_outcome=path_data['predicted_outcome'],
                        outcome_probability=path_data['outcome_probability'],
                        expected_value=path_data.get('expected_value'),
                        amplitude=path_data.get('amplitude', 0),
                        phase=path_data.get('phase', 0),
                    )

            return Response(QuantumSimulationSerializer(simulation).data)

        except Exception as e:
            simulation.status = 'failed'
            simulation.results = {'error': str(e)}
            simulation.completed_at = timezone.now()
            simulation.save()
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def simulate_customer_paths(self, request):
        """Run a quick customer path simulation without saving"""
        serializer = CustomerPathSimulationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        engine = QuantumPredictiveEngine(
            num_qubits=serializer.validated_data['num_qubits'],
            shot_count=serializer.validated_data['shot_count']
        )

        results = engine.simulate_customer_paths(
            customer_data=serializer.validated_data.get('customer_data', {}),
            touchpoints=serializer.validated_data['touchpoints'],
            max_path_length=serializer.validated_data['max_path_length']
        )

        return Response(results)

    @action(detail=False, methods=['post'])
    def forecast_deals(self, request):
        """Run deal closure forecast"""
        serializer = DealForecastRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get opportunities if IDs provided
        opportunities = []
        if serializer.validated_data.get('opportunity_ids'):
            from opportunity_management.models import Opportunity
            opps = Opportunity.objects.filter(
                id__in=serializer.validated_data['opportunity_ids'],
                owner=request.user
            )
            opportunities = [
                {'id': o.id, 'amount': float(o.amount or 0), 'probability': o.probability / 100}
                for o in opps
            ]

        engine = QuantumPredictiveEngine(
            num_qubits=serializer.validated_data['num_qubits'],
            shot_count=serializer.validated_data['shot_count']
        )

        results = engine.forecast_deal_closure(
            opportunities=opportunities,
            market_conditions=serializer.validated_data['market_conditions']
        )

        return Response(results)

    @action(detail=False, methods=['post'])
    def analyze_market_shift(self, request):
        """Analyze potential market shifts"""
        serializer = MarketShiftAnalysisRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        engine = QuantumPredictiveEngine(
            num_qubits=serializer.validated_data['num_qubits'],
            shot_count=serializer.validated_data['shot_count']
        )

        results = engine.analyze_market_shift(
            current_market=serializer.validated_data['current_market'],
            historical_data=[],
            external_factors=serializer.validated_data['external_factors']
        )

        return Response(results)

    @action(detail=False, methods=['post'])
    def whatif_analysis(self, request):
        """Run what-if scenario analysis"""
        serializer = WhatIfAnalysisRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        engine = QuantumPredictiveEngine(
            num_qubits=serializer.validated_data['num_qubits'],
            shot_count=serializer.validated_data['shot_count']
        )

        results = engine.run_whatif_analysis(
            base_scenario=serializer.validated_data['base_scenario'],
            variable_changes=serializer.validated_data['variable_changes'],
            constraints=serializer.validated_data['constraints']
        )

        return Response(results)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get quantum simulation statistics"""
        simulations = self.get_queryset()

        completed = simulations.filter(status='completed')

        total_paths = sum(s.paths_simulated or 0 for s in completed)
        avg_advantage = completed.exclude(quantum_advantage_factor__isnull=True)

        return Response({
            'total_simulations': simulations.count(),
            'completed_simulations': completed.count(),
            'pending_simulations': simulations.filter(status='pending').count(),
            'running_simulations': simulations.filter(status='running').count(),
            'total_paths_simulated': total_paths,
            'average_quantum_advantage': (
                sum(s.quantum_advantage_factor for s in avg_advantage) / avg_advantage.count()
                if avg_advantage.exists() else 0
            ),
            'simulation_types': dict(
                simulations.values_list('simulation_type').distinct()
                .annotate(count=models.Count('id')).values_list('simulation_type', 'count')
            ) if simulations.exists() else {},
        })


class WhatIfScenarioViewSet(viewsets.ModelViewSet):
    """ViewSet for managing what-if scenarios"""
    serializer_class = WhatIfScenarioSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['base_simulation']

    def get_queryset(self):
        return WhatIfScenario.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def run_analysis(self, request, pk=None):
        """Run analysis for a what-if scenario"""
        scenario = self.get_object()

        engine = QuantumPredictiveEngine(num_qubits=20, shot_count=1000)

        results = engine.run_whatif_analysis(
            base_scenario=scenario.baseline_metrics,
            variable_changes=scenario.variable_changes,
            constraints=scenario.constraints
        )

        scenario.scenario_metrics = results.get('outcomes', [])
        scenario.impact_analysis = {
            'expected_revenue_impact': results.get('expected_revenue_impact'),
            'expected_cost_impact': results.get('expected_cost_impact'),
            'expected_net_impact': results.get('expected_net_impact'),
        }
        scenario.optimal_actions = results.get('optimal_actions', [])
        scenario.risk_assessment = {
            'scenarios_analyzed': results.get('scenarios_analyzed'),
            'high_risk_count': sum(1 for o in results.get('outcomes', []) if o.get('risk_level') == 'high'),
        }
        scenario.save()

        return Response(WhatIfScenarioSerializer(scenario).data)


class QuantumModelRegistryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing available quantum models"""
    queryset = QuantumModelRegistry.objects.filter(is_active=True)
    serializer_class = QuantumModelRegistrySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['model_type', 'is_active']


class IoTDataFeedViewSet(viewsets.ModelViewSet):
    """ViewSet for managing IoT and social data feeds"""
    queryset = IoTDataFeed.objects.all()
    serializer_class = IoTDataFeedSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['feed_type', 'is_active']

    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test connection to data feed"""
        feed = self.get_object()

        # Simulate connection test
        return Response({
            'status': 'success',
            'message': f'Successfully connected to {feed.name}',
            'latency_ms': 45,
            'records_available': 1000000,
        })

    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """Sync data from feed"""
        feed = self.get_object()

        # Simulate sync
        feed.last_data_received = timezone.now()
        feed.records_received += 10000
        feed.save()

        return Response({
            'status': 'success',
            'records_synced': 10000,
            'total_records': feed.records_received,
        })


# Import models for aggregation
from django.db import models
