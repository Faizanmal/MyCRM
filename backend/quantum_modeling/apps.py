from django.apps import AppConfig


class QuantumModelingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'quantum_modeling'
    verbose_name = 'Quantum-Accelerated Predictive Modeling'

    def ready(self):
        # Import signals if any
        pass
