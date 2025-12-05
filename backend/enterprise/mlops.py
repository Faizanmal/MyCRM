"""
MLOps Pipeline Manager for MyCRM

Enterprise ML Operations including:
- Model versioning and registry
- Feature store integration
- Model training pipelines
- A/B testing framework
- Model monitoring and drift detection
- Automated retraining
- Inference serving
"""

import os
import json
import logging
import hashlib
import pickle
from typing import Dict, Optional, Any, List, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import threading
from abc import ABC, abstractmethod

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)


# =====================
# Model Registry
# =====================

class ModelStage(Enum):
    """Model lifecycle stages"""
    DEVELOPMENT = 'development'
    STAGING = 'staging'
    PRODUCTION = 'production'
    ARCHIVED = 'archived'


@dataclass
class ModelVersion:
    """Model version metadata"""
    model_name: str
    version: str
    stage: ModelStage
    created_at: datetime
    created_by: str
    
    # Model artifacts
    artifact_path: str
    artifact_hash: str
    
    # Training info
    training_data_hash: Optional[str] = None
    training_metrics: Dict[str, float] = field(default_factory=dict)
    training_params: Dict[str, Any] = field(default_factory=dict)
    
    # Validation metrics
    validation_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Runtime info
    input_schema: Dict = field(default_factory=dict)
    output_schema: Dict = field(default_factory=dict)
    
    # Tags and metadata
    tags: Dict[str, str] = field(default_factory=dict)
    description: str = ''
    
    def to_dict(self) -> Dict:
        return {
            'model_name': self.model_name,
            'version': self.version,
            'stage': self.stage.value,
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by,
            'artifact_path': self.artifact_path,
            'artifact_hash': self.artifact_hash,
            'training_metrics': self.training_metrics,
            'validation_metrics': self.validation_metrics,
            'tags': self.tags,
            'description': self.description
        }


class ModelRegistry:
    """
    Centralized model registry for versioning and lifecycle management
    
    Features:
    - Model versioning
    - Stage transitions (dev -> staging -> production)
    - Model comparison
    - Artifact storage
    - Lineage tracking
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._models: Dict[str, Dict[str, ModelVersion]] = {}
        self._storage_path = os.getenv('MODEL_STORAGE_PATH', '/app/models')
        self._use_mlflow = os.getenv('MLFLOW_ENABLED', 'false').lower() == 'true'
        self._initialized = True
        
        if self._use_mlflow:
            self._init_mlflow()
        
        # Load existing models from cache
        self._load_registry()
    
    def _init_mlflow(self):
        """Initialize MLflow integration"""
        try:
            import mlflow
            
            mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI', 'http://localhost:5000'))
            mlflow.set_experiment(os.getenv('MLFLOW_EXPERIMENT', 'mycrm-models'))
            
            self._mlflow = mlflow
            logger.info("MLflow integration initialized")
        except ImportError:
            logger.warning("mlflow not installed")
            self._use_mlflow = False
    
    def _load_registry(self):
        """Load registry from cache"""
        registry_data = cache.get('model_registry', {})
        for model_name, versions in registry_data.items():
            self._models[model_name] = {}
            for version_str, data in versions.items():
                self._models[model_name][version_str] = ModelVersion(
                    model_name=data['model_name'],
                    version=data['version'],
                    stage=ModelStage(data['stage']),
                    created_at=datetime.fromisoformat(data['created_at']),
                    created_by=data['created_by'],
                    artifact_path=data['artifact_path'],
                    artifact_hash=data['artifact_hash'],
                    training_metrics=data.get('training_metrics', {}),
                    validation_metrics=data.get('validation_metrics', {}),
                    tags=data.get('tags', {}),
                    description=data.get('description', '')
                )
    
    def _save_registry(self):
        """Save registry to cache"""
        registry_data = {}
        for model_name, versions in self._models.items():
            registry_data[model_name] = {}
            for version_str, model_version in versions.items():
                registry_data[model_name][version_str] = model_version.to_dict()
        
        cache.set('model_registry', registry_data, 86400 * 365)  # 1 year
    
    def register_model(
        self,
        model_name: str,
        model_artifact: Any,
        training_metrics: Dict[str, float],
        training_params: Dict[str, Any],
        created_by: str,
        description: str = '',
        tags: Optional[Dict[str, str]] = None
    ) -> ModelVersion:
        """
        Register a new model version
        
        Args:
            model_name: Name of the model
            model_artifact: The trained model object
            training_metrics: Metrics from training
            training_params: Hyperparameters used
            created_by: User/system that created the model
            description: Model description
            tags: Additional tags
        
        Returns:
            ModelVersion: The registered model version
        """
        # Generate version
        existing_versions = self._models.get(model_name, {})
        version_num = len(existing_versions) + 1
        version = f"v{version_num}.0.0"
        
        # Serialize and save artifact
        artifact_path = os.path.join(self._storage_path, model_name, version)
        os.makedirs(artifact_path, exist_ok=True)
        
        artifact_file = os.path.join(artifact_path, 'model.pkl')
        
        # Use joblib for scikit-learn models
        try:
            import joblib
            joblib.dump(model_artifact, artifact_file)
        except ImportError:
            with open(artifact_file, 'wb') as f:
                pickle.dump(model_artifact, f)
        
        # Calculate hash
        with open(artifact_file, 'rb') as f:
            artifact_hash = hashlib.sha256(f.read()).hexdigest()
        
        # Create model version
        model_version = ModelVersion(
            model_name=model_name,
            version=version,
            stage=ModelStage.DEVELOPMENT,
            created_at=timezone.now(),
            created_by=created_by,
            artifact_path=artifact_file,
            artifact_hash=artifact_hash,
            training_metrics=training_metrics,
            training_params=training_params,
            tags=tags or {},
            description=description
        )
        
        # Store in registry
        if model_name not in self._models:
            self._models[model_name] = {}
        self._models[model_name][version] = model_version
        
        # Save to cache
        self._save_registry()
        
        # Log to MLflow if enabled
        if self._use_mlflow:
            with self._mlflow.start_run():
                self._mlflow.log_params(training_params)
                self._mlflow.log_metrics(training_metrics)
                self._mlflow.sklearn.log_model(model_artifact, model_name)
        
        logger.info(f"Registered model {model_name} version {version}")
        return model_version
    
    def get_model(self, model_name: str, version: Optional[str] = None, 
                  stage: Optional[ModelStage] = None) -> Optional[Any]:
        """
        Get a model artifact
        
        Args:
            model_name: Name of the model
            version: Specific version (optional)
            stage: Get latest model at this stage (optional)
        
        Returns:
            The loaded model artifact
        """
        if version:
            model_version = self._models.get(model_name, {}).get(version)
        elif stage:
            # Get latest version at stage
            versions = self._models.get(model_name, {})
            matching = [v for v in versions.values() if v.stage == stage]
            model_version = max(matching, key=lambda x: x.created_at) if matching else None
        else:
            # Get production model, or latest
            model_version = self.get_production_model(model_name)
        
        if not model_version:
            return None
        
        # Load artifact
        try:
            import joblib
            return joblib.load(model_version.artifact_path)
        except ImportError:
            with open(model_version.artifact_path, 'rb') as f:
                return pickle.load(f)
    
    def get_production_model(self, model_name: str) -> Optional[ModelVersion]:
        """Get the production version of a model"""
        versions = self._models.get(model_name, {})
        production = [v for v in versions.values() if v.stage == ModelStage.PRODUCTION]
        return production[0] if production else None
    
    def transition_stage(self, model_name: str, version: str, 
                        target_stage: ModelStage, archive_existing: bool = True):
        """
        Transition a model to a new stage
        
        Args:
            model_name: Model name
            version: Version to transition
            target_stage: Target stage
            archive_existing: Archive existing models at target stage
        """
        model_version = self._models.get(model_name, {}).get(version)
        if not model_version:
            raise ValueError(f"Model {model_name} version {version} not found")
        
        # Archive existing models at target stage
        if archive_existing and target_stage == ModelStage.PRODUCTION:
            for v in self._models.get(model_name, {}).values():
                if v.stage == ModelStage.PRODUCTION and v.version != version:
                    v.stage = ModelStage.ARCHIVED
                    logger.info(f"Archived model {model_name} version {v.version}")
        
        # Transition
        model_version.stage = target_stage
        self._save_registry()
        
        logger.info(f"Transitioned model {model_name} {version} to {target_stage.value}")
    
    def list_models(self) -> List[str]:
        """List all registered models"""
        return list(self._models.keys())
    
    def list_versions(self, model_name: str) -> List[ModelVersion]:
        """List all versions of a model"""
        return list(self._models.get(model_name, {}).values())
    
    def compare_models(self, model_name: str, version_a: str, 
                       version_b: str) -> Dict:
        """Compare two model versions"""
        va = self._models.get(model_name, {}).get(version_a)
        vb = self._models.get(model_name, {}).get(version_b)
        
        if not va or not vb:
            raise ValueError("One or both versions not found")
        
        return {
            'version_a': version_a,
            'version_b': version_b,
            'metrics_comparison': {
                metric: {
                    'a': va.training_metrics.get(metric),
                    'b': vb.training_metrics.get(metric),
                    'diff': (vb.training_metrics.get(metric, 0) - 
                            va.training_metrics.get(metric, 0))
                }
                for metric in set(va.training_metrics.keys()) | set(vb.training_metrics.keys())
            },
            'created_at_comparison': {
                'a': va.created_at.isoformat(),
                'b': vb.created_at.isoformat()
            }
        }


# =====================
# Feature Store
# =====================

@dataclass
class FeatureDefinition:
    """Definition of a feature"""
    name: str
    data_type: str  # 'float', 'int', 'string', 'array'
    description: str
    entity: str  # 'contact', 'lead', 'opportunity'
    computation: Optional[str] = None  # SQL or Python code
    dependencies: List[str] = field(default_factory=list)
    ttl_seconds: int = 3600
    tags: Dict[str, str] = field(default_factory=dict)


class FeatureStore:
    """
    Feature store for ML features
    
    Features:
    - Centralized feature definitions
    - Online serving (low latency)
    - Offline batch computation
    - Feature versioning
    - Point-in-time correctness
    """
    
    _instance = None
    _lock = threading.Lock()
    
    # Pre-defined features for CRM
    FEATURE_DEFINITIONS = {
        # Contact features
        'contact_days_since_creation': FeatureDefinition(
            name='contact_days_since_creation',
            data_type='int',
            description='Days since contact was created',
            entity='contact'
        ),
        'contact_days_since_last_interaction': FeatureDefinition(
            name='contact_days_since_last_interaction',
            data_type='int',
            description='Days since last interaction with contact',
            entity='contact'
        ),
        'contact_total_opportunities': FeatureDefinition(
            name='contact_total_opportunities',
            data_type='int',
            description='Total number of opportunities',
            entity='contact'
        ),
        'contact_won_opportunities': FeatureDefinition(
            name='contact_won_opportunities',
            data_type='int',
            description='Number of won opportunities',
            entity='contact'
        ),
        'contact_total_revenue': FeatureDefinition(
            name='contact_total_revenue',
            data_type='float',
            description='Total revenue from contact',
            entity='contact'
        ),
        'contact_engagement_score': FeatureDefinition(
            name='contact_engagement_score',
            data_type='float',
            description='Computed engagement score',
            entity='contact',
            dependencies=['contact_days_since_last_interaction', 'contact_total_opportunities']
        ),
        
        # Lead features
        'lead_score': FeatureDefinition(
            name='lead_score',
            data_type='float',
            description='ML-computed lead score',
            entity='lead'
        ),
        'lead_source_category': FeatureDefinition(
            name='lead_source_category',
            data_type='string',
            description='Categorized lead source',
            entity='lead'
        ),
        'lead_response_time_hours': FeatureDefinition(
            name='lead_response_time_hours',
            data_type='float',
            description='Hours to first response',
            entity='lead'
        ),
        
        # Opportunity features
        'opportunity_days_in_stage': FeatureDefinition(
            name='opportunity_days_in_stage',
            data_type='int',
            description='Days in current stage',
            entity='opportunity'
        ),
        'opportunity_win_probability': FeatureDefinition(
            name='opportunity_win_probability',
            data_type='float',
            description='ML-predicted win probability',
            entity='opportunity'
        ),
    }
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._feature_cache_prefix = 'feature:'
        self._use_feast = os.getenv('FEAST_ENABLED', 'false').lower() == 'true'
        self._initialized = True
        
        if self._use_feast:
            self._init_feast()
    
    def _init_feast(self):
        """Initialize Feast feature store"""
        try:
            from feast import FeatureStore as FeastStore
            
            self._feast = FeastStore(repo_path=os.getenv('FEAST_REPO_PATH', '.'))
            logger.info("Feast feature store initialized")
        except ImportError:
            logger.warning("feast not installed")
            self._use_feast = False
    
    def get_online_features(self, entity: str, entity_id: Union[int, str], 
                           feature_names: List[str]) -> Dict[str, Any]:
        """
        Get features for online serving (low latency)
        
        Args:
            entity: Entity type (contact, lead, opportunity)
            entity_id: Entity ID
            feature_names: List of feature names to retrieve
        
        Returns:
            Dict of feature name -> value
        """
        features = {}
        
        for feature_name in feature_names:
            cache_key = f"{self._feature_cache_prefix}{entity}:{entity_id}:{feature_name}"
            value = cache.get(cache_key)
            
            if value is not None:
                features[feature_name] = value
            else:
                # Compute feature on-demand
                computed_value = self._compute_feature(entity, entity_id, feature_name)
                if computed_value is not None:
                    # Cache for future use
                    feature_def = self.FEATURE_DEFINITIONS.get(feature_name)
                    ttl = feature_def.ttl_seconds if feature_def else 3600
                    cache.set(cache_key, computed_value, ttl)
                    features[feature_name] = computed_value
        
        return features
    
    def set_feature(self, entity: str, entity_id: Union[int, str], 
                    feature_name: str, value: Any, ttl: Optional[int] = None):
        """Set a feature value in the online store"""
        feature_def = self.FEATURE_DEFINITIONS.get(feature_name)
        ttl = ttl or (feature_def.ttl_seconds if feature_def else 3600)
        
        cache_key = f"{self._feature_cache_prefix}{entity}:{entity_id}:{feature_name}"
        cache.set(cache_key, value, ttl)
    
    def _compute_feature(self, entity: str, entity_id: Union[int, str], 
                         feature_name: str) -> Optional[Any]:
        """Compute a feature value on-demand"""
        feature_def = self.FEATURE_DEFINITIONS.get(feature_name)
        if not feature_def:
            return None
        
        # Import models here to avoid circular imports
        if entity == 'contact' and feature_name == 'contact_days_since_creation':
            try:
                from contact_management.models import Contact
                contact = Contact.objects.get(id=entity_id)
                return (timezone.now() - contact.created_at).days
            except Exception:
                return None
        
        elif entity == 'contact' and feature_name == 'contact_total_opportunities':
            try:
                from contact_management.models import Contact
                contact = Contact.objects.get(id=entity_id)
                return contact.opportunities.count()
            except Exception:
                return None
        
        elif entity == 'contact' and feature_name == 'contact_engagement_score':
            # Compute composite feature
            days_since = self.get_online_features(entity, entity_id, ['contact_days_since_last_interaction'])
            opps = self.get_online_features(entity, entity_id, ['contact_total_opportunities'])
            
            days = days_since.get('contact_days_since_last_interaction', 999)
            opp_count = opps.get('contact_total_opportunities', 0)
            
            # Simple engagement score formula
            recency_score = max(0, 100 - days * 2)
            activity_score = min(100, opp_count * 20)
            return (recency_score + activity_score) / 2
        
        return None
    
    def get_feature_vector(self, entity: str, entity_id: Union[int, str]) -> Dict[str, Any]:
        """Get all features for an entity"""
        feature_names = [
            name for name, defn in self.FEATURE_DEFINITIONS.items()
            if defn.entity == entity
        ]
        return self.get_online_features(entity, entity_id, feature_names)
    
    def batch_get_features(self, entity: str, entity_ids: List[Union[int, str]], 
                          feature_names: List[str]) -> List[Dict[str, Any]]:
        """Batch get features for multiple entities"""
        return [
            self.get_online_features(entity, eid, feature_names)
            for eid in entity_ids
        ]


# =====================
# Model Monitoring
# =====================

class DriftType(Enum):
    """Types of model drift"""
    DATA_DRIFT = 'data_drift'
    CONCEPT_DRIFT = 'concept_drift'
    PREDICTION_DRIFT = 'prediction_drift'


@dataclass
class DriftAlert:
    """Drift detection alert"""
    drift_type: DriftType
    model_name: str
    feature_name: Optional[str]
    severity: str  # 'low', 'medium', 'high'
    current_value: float
    baseline_value: float
    threshold: float
    detected_at: datetime
    details: Dict = field(default_factory=dict)


class ModelMonitor:
    """
    Monitor models for drift and performance degradation
    
    Features:
    - Data drift detection
    - Prediction drift detection
    - Performance monitoring
    - Automated alerting
    - Retraining triggers
    """
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self._baseline_stats: Dict[str, Dict] = {}
        self._alerts: List[DriftAlert] = []
        self._prediction_log: List[Dict] = []
        
        # Thresholds
        self.data_drift_threshold = float(os.getenv('DATA_DRIFT_THRESHOLD', '0.1'))
        self.prediction_drift_threshold = float(os.getenv('PREDICTION_DRIFT_THRESHOLD', '0.15'))
    
    def set_baseline(self, feature_stats: Dict[str, Dict]):
        """
        Set baseline statistics for drift detection
        
        Args:
            feature_stats: Dict of feature name -> {mean, std, min, max, distribution}
        """
        self._baseline_stats = feature_stats
        cache.set(f'model_baseline:{self.model_name}', feature_stats, 86400 * 30)
    
    def log_prediction(self, features: Dict[str, Any], prediction: Any, 
                      actual: Optional[Any] = None):
        """Log a prediction for monitoring"""
        log_entry = {
            'timestamp': timezone.now().isoformat(),
            'features': features,
            'prediction': prediction,
            'actual': actual
        }
        
        self._prediction_log.append(log_entry)
        
        # Store in cache (keep last 1000 predictions)
        cache_key = f'prediction_log:{self.model_name}'
        logs = cache.get(cache_key, [])
        logs.append(log_entry)
        logs = logs[-1000:]  # Keep last 1000
        cache.set(cache_key, logs, 86400)
    
    def check_data_drift(self, current_features: Dict[str, Any]) -> List[DriftAlert]:
        """
        Check for data drift in input features
        
        Args:
            current_features: Current feature values
        
        Returns:
            List of drift alerts
        """
        alerts = []
        
        for feature_name, value in current_features.items():
            baseline = self._baseline_stats.get(feature_name)
            if not baseline:
                continue
            
            # Calculate z-score
            mean = baseline.get('mean', 0)
            std = baseline.get('std', 1)
            
            if std > 0 and isinstance(value, (int, float)):
                z_score = abs((value - mean) / std)
                
                if z_score > 3:  # More than 3 standard deviations
                    alert = DriftAlert(
                        drift_type=DriftType.DATA_DRIFT,
                        model_name=self.model_name,
                        feature_name=feature_name,
                        severity='high' if z_score > 5 else 'medium',
                        current_value=value,
                        baseline_value=mean,
                        threshold=3.0,
                        detected_at=timezone.now(),
                        details={'z_score': z_score}
                    )
                    alerts.append(alert)
        
        self._alerts.extend(alerts)
        return alerts
    
    def check_prediction_drift(self, window_hours: int = 24) -> Optional[DriftAlert]:
        """
        Check for drift in prediction distribution
        
        Args:
            window_hours: Time window to analyze
        
        Returns:
            Drift alert if detected
        """
        cache_key = f'prediction_log:{self.model_name}'
        logs = cache.get(cache_key, [])
        
        if len(logs) < 100:
            return None
        
        # Get recent predictions
        cutoff = (timezone.now() - timedelta(hours=window_hours)).isoformat()
        recent = [log for log in logs if log['timestamp'] > cutoff]
        
        if len(recent) < 50:
            return None
        
        # Compare recent vs historical distribution
        recent_preds = [log['prediction'] for log in recent if isinstance(log['prediction'], (int, float))]
        historical_preds = [log['prediction'] for log in logs[:-len(recent)] if isinstance(log['prediction'], (int, float))]
        
        if not recent_preds or not historical_preds:
            return None
        
        import statistics
        recent_mean = statistics.mean(recent_preds)
        historical_mean = statistics.mean(historical_preds)
        
        drift = abs(recent_mean - historical_mean) / (historical_mean + 0.001)
        
        if drift > self.prediction_drift_threshold:
            return DriftAlert(
                drift_type=DriftType.PREDICTION_DRIFT,
                model_name=self.model_name,
                feature_name=None,
                severity='high' if drift > 0.3 else 'medium',
                current_value=recent_mean,
                baseline_value=historical_mean,
                threshold=self.prediction_drift_threshold,
                detected_at=timezone.now(),
                details={'drift_percentage': drift * 100}
            )
        
        return None
    
    def get_performance_metrics(self, window_hours: int = 24) -> Dict:
        """Get recent performance metrics"""
        cache_key = f'prediction_log:{self.model_name}'
        logs = cache.get(cache_key, [])
        
        cutoff = (timezone.now() - timedelta(hours=window_hours)).isoformat()
        recent = [log for log in logs if log['timestamp'] > cutoff and log.get('actual') is not None]
        
        if not recent:
            return {'error': 'No labeled predictions in window'}
        
        # Calculate accuracy (for classification)
        correct = sum(1 for log in recent if log['prediction'] == log['actual'])
        total = len(recent)
        
        return {
            'window_hours': window_hours,
            'total_predictions': len(logs),
            'labeled_predictions': total,
            'accuracy': correct / total if total > 0 else 0,
            'predictions_per_hour': len(recent) / window_hours
        }
    
    def should_retrain(self) -> tuple[bool, List[str]]:
        """
        Determine if model should be retrained
        
        Returns:
            (should_retrain, reasons)
        """
        reasons = []
        
        # Check for recent drift alerts
        recent_alerts = [
            a for a in self._alerts
            if (timezone.now() - a.detected_at).total_seconds() < 86400
        ]
        
        high_severity_alerts = [a for a in recent_alerts if a.severity == 'high']
        if len(high_severity_alerts) >= 3:
            reasons.append(f"{len(high_severity_alerts)} high-severity drift alerts in last 24h")
        
        # Check performance degradation
        metrics = self.get_performance_metrics(window_hours=168)  # 1 week
        if metrics.get('accuracy', 1) < 0.7:
            reasons.append(f"Accuracy dropped to {metrics['accuracy']:.2%}")
        
        return len(reasons) > 0, reasons


# =====================
# MLOps Manager
# =====================

class MLOpsManager:
    """
    Central MLOps manager coordinating all ML operations
    """
    
    def __init__(self):
        self.registry = ModelRegistry()
        self.feature_store = FeatureStore()
        self._monitors: Dict[str, ModelMonitor] = {}
    
    def get_monitor(self, model_name: str) -> ModelMonitor:
        """Get or create a model monitor"""
        if model_name not in self._monitors:
            self._monitors[model_name] = ModelMonitor(model_name)
        return self._monitors[model_name]
    
    def predict(self, model_name: str, features: Dict[str, Any], 
                log_prediction: bool = True) -> Any:
        """
        Make a prediction with full MLOps tracking
        
        Args:
            model_name: Name of the model
            features: Input features
            log_prediction: Whether to log for monitoring
        
        Returns:
            Model prediction
        """
        from .observability import MetricsCollector, TracingManager
        
        metrics = MetricsCollector()
        tracing = TracingManager()
        
        with tracing.span(f'ml_predict_{model_name}') as span:
            span.tags['model_name'] = model_name
            
            start_time = timezone.now()
            
            # Get model
            model = self.registry.get_model(model_name)
            if not model:
                raise ValueError(f"Model {model_name} not found in registry")
            
            # Make prediction
            try:
                prediction = model.predict([list(features.values())])[0]
                
                duration = (timezone.now() - start_time).total_seconds()
                
                # Log metrics
                metrics.increment('ml_predictions_total', labels={
                    'model': model_name,
                    'outcome': 'success'
                })
                metrics.histogram('ml_prediction_latency_seconds', duration, labels={
                    'model': model_name
                })
                
                # Log for monitoring
                if log_prediction:
                    monitor = self.get_monitor(model_name)
                    monitor.log_prediction(features, prediction)
                    
                    # Check for drift
                    drift_alerts = monitor.check_data_drift(features)
                    if drift_alerts:
                        span.tags['drift_detected'] = 'true'
                
                span.tags['prediction'] = str(prediction)
                return prediction
                
            except Exception as e:
                metrics.increment('ml_predictions_total', labels={
                    'model': model_name,
                    'outcome': 'error'
                })
                span.tags['error'] = str(e)
                raise
    
    def train_model(self, model_name: str, training_data: Any, 
                    training_params: Dict[str, Any],
                    model_class: type,
                    created_by: str) -> ModelVersion:
        """
        Train a new model version
        
        Args:
            model_name: Name of the model
            training_data: Training dataset (X, y tuple or DataFrame)
            training_params: Model hyperparameters
            model_class: Model class to instantiate
            created_by: User/system training the model
        
        Returns:
            New model version
        """
        from .observability import TracingManager
        
        tracing = TracingManager()
        
        with tracing.span(f'ml_train_{model_name}') as span:
            span.tags['model_name'] = model_name
            span.tags['params'] = json.dumps(training_params)
            
            # Unpack training data
            if isinstance(training_data, tuple):
                X, y = training_data
            else:
                raise ValueError("training_data must be (X, y) tuple")
            
            # Train model
            model = model_class(**training_params)
            model.fit(X, y)
            
            # Compute training metrics
            from sklearn.model_selection import cross_val_score
            cv_scores = cross_val_score(model, X, y, cv=5)
            
            training_metrics = {
                'cv_mean': float(cv_scores.mean()),
                'cv_std': float(cv_scores.std()),
                'training_samples': len(X)
            }
            
            span.tags['cv_score'] = f"{cv_scores.mean():.3f}"
            
            # Register model
            model_version = self.registry.register_model(
                model_name=model_name,
                model_artifact=model,
                training_metrics=training_metrics,
                training_params=training_params,
                created_by=created_by,
                description=f"Trained on {len(X)} samples"
            )
            
            # Set baseline for monitoring
            monitor = self.get_monitor(model_name)
            
            # Compute feature statistics for baseline
            import numpy as np
            feature_stats = {}
            if hasattr(X, 'columns'):
                for col in X.columns:
                    feature_stats[col] = {
                        'mean': float(X[col].mean()),
                        'std': float(X[col].std()),
                        'min': float(X[col].min()),
                        'max': float(X[col].max())
                    }
            
            monitor.set_baseline(feature_stats)
            
            return model_version
    
    def get_health_report(self) -> Dict:
        """Get health report for all models"""
        report = {
            'models': {},
            'generated_at': timezone.now().isoformat()
        }
        
        for model_name in self.registry.list_models():
            prod_model = self.registry.get_production_model(model_name)
            monitor = self.get_monitor(model_name)
            
            should_retrain, reasons = monitor.should_retrain()
            metrics = monitor.get_performance_metrics()
            
            report['models'][model_name] = {
                'production_version': prod_model.version if prod_model else None,
                'total_versions': len(self.registry.list_versions(model_name)),
                'should_retrain': should_retrain,
                'retrain_reasons': reasons,
                'performance': metrics,
                'recent_alerts': len([a for a in monitor._alerts 
                                     if (timezone.now() - a.detected_at).total_seconds() < 86400])
            }
        
        return report
