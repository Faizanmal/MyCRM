from django.contrib import admin
from .models import (
    QuantumSimulation,
    InteractionPath,
    WhatIfScenario,
    QuantumModelRegistry,
    IoTDataFeed
)


@admin.register(QuantumSimulation)
class QuantumSimulationAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'simulation_type', 'status', 'paths_simulated', 'created_at']
    list_filter = ['simulation_type', 'status', 'created_at']
    search_fields = ['name', 'description', 'user__email']
    readonly_fields = ['id', 'created_at', 'started_at', 'completed_at']
    ordering = ['-created_at']


@admin.register(InteractionPath)
class InteractionPathAdmin(admin.ModelAdmin):
    list_display = ['path_id', 'simulation', 'probability', 'predicted_outcome', 'created_at']
    list_filter = ['predicted_outcome', 'created_at']
    search_fields = ['path_id', 'simulation__name']


@admin.register(WhatIfScenario)
class WhatIfScenarioAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'base_simulation', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description', 'user__email']


@admin.register(QuantumModelRegistry)
class QuantumModelRegistryAdmin(admin.ModelAdmin):
    list_display = ['name', 'version', 'model_type', 'is_active', 'accuracy_score']
    list_filter = ['model_type', 'is_active']
    search_fields = ['name', 'description']


@admin.register(IoTDataFeed)
class IoTDataFeedAdmin(admin.ModelAdmin):
    list_display = ['name', 'feed_type', 'is_active', 'last_data_received', 'records_received']
    list_filter = ['feed_type', 'is_active']
    search_fields = ['name']
