import uuid

from django.contrib.auth.models import User
from django.db import models


class QuantumSimulation(models.Model):
    """Quantum computing simulation for scenario modeling"""

    SIMULATION_TYPES = [
        ('customer_paths', 'Customer Interaction Paths'),
        ('deal_forecast', 'Deal Closure Forecast'),
        ('market_shift', 'Market Shift Analysis'),
        ('churn_cascade', 'Churn Cascade Modeling'),
        ('revenue_projection', 'Revenue Projection'),
        ('competitive_analysis', 'Competitive Analysis'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('queued', 'Queued for Processing'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quantum_simulations')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    simulation_type = models.CharField(max_length=50, choices=SIMULATION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Input parameters
    input_parameters = models.JSONField(default=dict, help_text="Input parameters for simulation")
    data_sources = models.JSONField(default=list, help_text="Data sources included in simulation")

    # Quantum-specific settings
    qubits_requested = models.IntegerField(default=20, help_text="Number of qubits for simulation")
    quantum_gates = models.JSONField(default=list, help_text="Quantum gates configuration")
    entanglement_depth = models.IntegerField(default=5, help_text="Depth of entanglement circuits")
    shot_count = models.IntegerField(default=1000, help_text="Number of measurement shots")

    # Performance metrics
    paths_simulated = models.BigIntegerField(default=0, help_text="Number of paths/scenarios simulated")
    quantum_advantage_factor = models.FloatField(blank=True,
        help_text="Speed improvement vs classical computing")
    coherence_time_used = models.FloatField(blank=True, help_text="Quantum coherence time in microseconds")
    error_rate = models.FloatField(blank=True, help_text="Quantum error rate")

    # Results
    results = models.JSONField(default=dict, help_text="Simulation results")
    confidence_interval = models.JSONField(default=dict, help_text="Confidence intervals for predictions")

    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True)
    completed_at = models.DateTimeField(blank=True)
    execution_time_ms = models.IntegerField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Quantum Simulation'
        verbose_name_plural = 'Quantum Simulations'

    def __str__(self):
        return f"{self.name} ({self.get_simulation_type_display()})"


class InteractionPath(models.Model):
    """Individual customer interaction path from quantum simulation"""

    simulation = models.ForeignKey(QuantumSimulation, on_delete=models.CASCADE, related_name='paths')
    path_id = models.CharField(max_length=100)

    # Path definition
    touchpoints = models.JSONField(default=list, help_text="Sequence of interaction touchpoints")
    probability = models.FloatField(help_text="Probability of this path occurring")

    # Outcomes
    predicted_outcome = models.CharField(max_length=100)
    outcome_probability = models.FloatField()
    expected_value = models.DecimalField(max_digits=15, decimal_places=2, blank=True)

    # Quantum metrics
    amplitude = models.FloatField(help_text="Quantum amplitude of this path")
    phase = models.FloatField(help_text="Phase of the quantum state")
    interference_pattern = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-probability']
        unique_together = ['simulation', 'path_id']


class WhatIfScenario(models.Model):
    """What-if scenario analysis using quantum computing"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='whatif_scenarios')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Base simulation
    base_simulation = models.ForeignKey(QuantumSimulation, on_delete=models.SET_NULL,
        related_name='whatif_scenarios')

    # Scenario modifications
    variable_changes = models.JSONField(default=dict, help_text="Variables modified in this scenario")
    constraints = models.JSONField(default=list, help_text="Constraints applied")

    # Results comparison
    baseline_metrics = models.JSONField(default=dict)
    scenario_metrics = models.JSONField(default=dict)
    impact_analysis = models.JSONField(default=dict, help_text="Impact of changes vs baseline")

    # Recommendations
    optimal_actions = models.JSONField(default=list, help_text="Recommended actions based on analysis")
    risk_assessment = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'What-If Scenario'
        verbose_name_plural = 'What-If Scenarios'


class QuantumModelRegistry(models.Model):
    """Registry of quantum models available for simulations"""

    name = models.CharField(max_length=255, unique=True)
    version = models.CharField(max_length=50)
    description = models.TextField()

    # Model specifications
    model_type = models.CharField(max_length=100)
    supported_simulation_types = models.JSONField(default=list)
    min_qubits = models.IntegerField(default=5)
    max_qubits = models.IntegerField(default=100)

    # Performance characteristics
    avg_execution_time_ms = models.IntegerField(blank=True)
    accuracy_score = models.FloatField(blank=True)

    # Configuration
    default_parameters = models.JSONField(default=dict)
    gate_set = models.JSONField(default=list)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-version', 'name']
        verbose_name = 'Quantum Model'
        verbose_name_plural = 'Quantum Models'

    def __str__(self):
        return f"{self.name} v{self.version}"


class IoTDataFeed(models.Model):
    """IoT and social data feeds for quantum simulations"""

    FEED_TYPES = [
        ('iot_sensor', 'IoT Sensor Data'),
        ('social_media', 'Social Media Stream'),
        ('market_data', 'Market Data Feed'),
        ('customer_behavior', 'Customer Behavior Stream'),
        ('competitive_intel', 'Competitive Intelligence'),
    ]

    name = models.CharField(max_length=255)
    feed_type = models.CharField(max_length=50, choices=FEED_TYPES)

    # Connection settings
    endpoint_url = models.URLField(blank=True)
    connection_config = models.JSONField(default=dict)

    # Data characteristics
    data_schema = models.JSONField(default=dict)
    sampling_rate_hz = models.FloatField(default=1.0)
    data_retention_days = models.IntegerField(default=30)

    # Status
    is_active = models.BooleanField(default=True)
    last_data_received = models.DateTimeField(blank=True)
    records_received = models.BigIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_data_received']
        verbose_name = 'IoT Data Feed'
        verbose_name_plural = 'IoT Data Feeds'

    def __str__(self):
        return f"{self.name} ({self.get_feed_type_display()})"
