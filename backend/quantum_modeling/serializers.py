from rest_framework import serializers

from .models import (
    InteractionPath,
    IoTDataFeed,
    QuantumModelRegistry,
    QuantumSimulation,
    WhatIfScenario,
)


class InteractionPathSerializer(serializers.ModelSerializer):
    class Meta:
        model = InteractionPath
        fields = [
            'id', 'path_id', 'touchpoints', 'probability',
            'predicted_outcome', 'outcome_probability', 'expected_value',
            'amplitude', 'phase', 'interference_pattern', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class QuantumSimulationSerializer(serializers.ModelSerializer):
    paths = InteractionPathSerializer(many=True, read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    simulation_type_display = serializers.CharField(source='get_simulation_type_display', read_only=True)

    class Meta:
        model = QuantumSimulation
        fields = [
            'id', 'user', 'user_email', 'name', 'description',
            'simulation_type', 'simulation_type_display', 'status', 'status_display',
            'input_parameters', 'data_sources', 'qubits_requested',
            'quantum_gates', 'entanglement_depth', 'shot_count',
            'paths_simulated', 'quantum_advantage_factor', 'coherence_time_used',
            'error_rate', 'results', 'confidence_interval',
            'created_at', 'started_at', 'completed_at', 'execution_time_ms',
            'paths'
        ]
        read_only_fields = [
            'id', 'user', 'status', 'paths_simulated', 'quantum_advantage_factor',
            'coherence_time_used', 'error_rate', 'results', 'confidence_interval',
            'created_at', 'started_at', 'completed_at', 'execution_time_ms'
        ]


class QuantumSimulationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuantumSimulation
        fields = [
            'name', 'description', 'simulation_type',
            'input_parameters', 'data_sources', 'qubits_requested',
            'entanglement_depth', 'shot_count'
        ]

    def validate_qubits_requested(self, value):
        if value < 5 or value > 50:
            raise serializers.ValidationError("Qubits must be between 5 and 50")
        return value

    def validate_shot_count(self, value):
        if value < 100 or value > 10000:
            raise serializers.ValidationError("Shot count must be between 100 and 10000")
        return value


class WhatIfScenarioSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = WhatIfScenario
        fields = [
            'id', 'user', 'user_email', 'name', 'description',
            'base_simulation', 'variable_changes', 'constraints',
            'baseline_metrics', 'scenario_metrics', 'impact_analysis',
            'optimal_actions', 'risk_assessment',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'baseline_metrics', 'scenario_metrics',
            'impact_analysis', 'optimal_actions', 'risk_assessment',
            'created_at', 'updated_at'
        ]


class QuantumModelRegistrySerializer(serializers.ModelSerializer):
    class Meta:
        model = QuantumModelRegistry
        fields = [
            'id', 'name', 'version', 'description', 'model_type',
            'supported_simulation_types', 'min_qubits', 'max_qubits',
            'avg_execution_time_ms', 'accuracy_score', 'default_parameters',
            'gate_set', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class IoTDataFeedSerializer(serializers.ModelSerializer):
    feed_type_display = serializers.CharField(source='get_feed_type_display', read_only=True)

    class Meta:
        model = IoTDataFeed
        fields = [
            'id', 'name', 'feed_type', 'feed_type_display',
            'endpoint_url', 'connection_config', 'data_schema',
            'sampling_rate_hz', 'data_retention_days', 'is_active',
            'last_data_received', 'records_received',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'last_data_received', 'records_received', 'created_at', 'updated_at']


class CustomerPathSimulationRequestSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField(required=False)
    customer_data = serializers.JSONField(required=False, default=dict)
    touchpoints = serializers.ListField(
        child=serializers.CharField(),
        default=['Email', 'Phone Call', 'Demo', 'Proposal', 'Follow-up', 'Meeting', 'Contract Review']
    )
    max_path_length = serializers.IntegerField(default=10, min_value=3, max_value=20)
    num_qubits = serializers.IntegerField(default=20, min_value=5, max_value=50)
    shot_count = serializers.IntegerField(default=1000, min_value=100, max_value=10000)


class DealForecastRequestSerializer(serializers.Serializer):
    opportunity_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    market_conditions = serializers.JSONField(default=dict)
    num_qubits = serializers.IntegerField(default=20, min_value=5, max_value=50)
    shot_count = serializers.IntegerField(default=1000, min_value=100, max_value=10000)


class MarketShiftAnalysisRequestSerializer(serializers.Serializer):
    current_market = serializers.JSONField(default=dict)
    external_factors = serializers.JSONField(default=dict)
    num_qubits = serializers.IntegerField(default=20, min_value=5, max_value=50)
    shot_count = serializers.IntegerField(default=1000, min_value=100, max_value=10000)


class WhatIfAnalysisRequestSerializer(serializers.Serializer):
    base_scenario = serializers.JSONField(default=dict)
    variable_changes = serializers.JSONField(default=dict)
    constraints = serializers.ListField(
        child=serializers.JSONField(),
        default=[]
    )
    num_qubits = serializers.IntegerField(default=20, min_value=5, max_value=50)
    shot_count = serializers.IntegerField(default=1000, min_value=100, max_value=10000)
