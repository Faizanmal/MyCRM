"""
Prediction Services
ML model training and inference.
"""

import json
import hashlib
from datetime import timedelta
from django.utils import timezone
from django.db.models import Avg, Sum, Count

from .models import (
    PredictiveModel, ModelFeature, Prediction, LeadScore,
    ChurnPrediction, RevenueForecast, DealPrediction
)


class PredictionService:
    """Service for ML predictions"""

    @staticmethod
    def train_model(model, training_data_query, validation_split, hyperparameters):
        """Train a predictive model"""
        model.status = 'training'
        model.save()
        
        try:
            # In production, this would:
            # 1. Fetch training data from database
            # 2. Prepare features
            # 3. Train model using sklearn/xgboost/etc.
            # 4. Save model file
            # 5. Calculate metrics
            
            # Simulated training results
            import random
            
            model.accuracy = random.uniform(0.75, 0.95)
            model.precision = random.uniform(0.70, 0.90)
            model.recall = random.uniform(0.70, 0.90)
            model.f1_score = 2 * (model.precision * model.recall) / (model.precision + model.recall)
            model.auc_roc = random.uniform(0.80, 0.95)
            
            model.training_samples = 10000
            model.validation_samples = 2000
            model.training_duration_seconds = random.randint(60, 600)
            model.last_trained_at = timezone.now()
            
            model.status = 'active'
            model.save()
            
            return {
                'success': True,
                'metrics': {
                    'accuracy': model.accuracy,
                    'precision': model.precision,
                    'recall': model.recall,
                    'f1_score': model.f1_score,
                    'auc_roc': model.auc_roc
                }
            }
            
        except Exception as e:
            model.status = 'failed'
            model.save()
            return {'success': False, 'error': str(e)}

    @staticmethod
    def predict(model, entity_type, entity_id):
        """Make a single prediction"""
        # Extract features
        features = PredictionService._extract_features(model, entity_type, entity_id)
        
        # Make prediction (simulated)
        import random
        prediction_value = random.uniform(0, 1)
        confidence = random.uniform(0.7, 0.99)
        
        # Determine label based on threshold
        if model.model_type == 'lead_scoring':
            if prediction_value >= 0.7:
                label = 'hot'
            elif prediction_value >= 0.4:
                label = 'warm'
            else:
                label = 'cold'
        elif model.model_type == 'churn_prediction':
            if prediction_value >= 0.7:
                label = 'high_risk'
            elif prediction_value >= 0.4:
                label = 'medium_risk'
            else:
                label = 'low_risk'
        else:
            label = 'positive' if prediction_value >= 0.5 else 'negative'
        
        # Generate explanation
        top_factors = PredictionService._get_top_factors(features)
        explanation = PredictionService._generate_explanation(model.model_type, prediction_value, top_factors)
        
        # Save prediction
        prediction = Prediction.objects.create(
            model=model,
            entity_type=entity_type,
            entity_id=entity_id,
            prediction_value=prediction_value,
            prediction_label=label,
            confidence=confidence,
            feature_values=features,
            feature_contributions={f: random.uniform(-0.2, 0.2) for f in features.keys()},
            explanation=explanation,
            top_factors=top_factors
        )
        
        # Update model stats
        model.prediction_count += 1
        model.last_prediction_at = timezone.now()
        model.save()
        
        return prediction

    @staticmethod
    def batch_predict(model, entity_type, entity_ids):
        """Make batch predictions"""
        predictions = []
        for entity_id in entity_ids:
            prediction = PredictionService.predict(model, entity_type, entity_id)
            predictions.append(prediction)
        return predictions

    @staticmethod
    def score_all_leads(model):
        """Score all leads"""
        from leads.models import Lead
        
        leads = Lead.objects.filter(status__in=['new', 'contacted', 'qualified'])
        scored = 0
        
        for lead in leads:
            prediction = PredictionService.predict(model, 'lead', lead.id)
            
            # Convert to LeadScore
            score = int(prediction.prediction_value * 100)
            
            if score >= 70:
                tier = 'hot'
            elif score >= 40:
                tier = 'warm'
            else:
                tier = 'cold'
            
            LeadScore.objects.update_or_create(
                lead=lead,
                defaults={
                    'model': model,
                    'score': score,
                    'tier': tier,
                    'fit_score': int(prediction.feature_contributions.get('fit', 0.5) * 100),
                    'engagement_score': int(prediction.feature_contributions.get('engagement', 0.5) * 100),
                    'intent_score': int(prediction.feature_contributions.get('intent', 0.5) * 100),
                    'conversion_probability': prediction.prediction_value,
                    'recommended_actions': prediction.top_factors[:3]
                }
            )
            scored += 1
        
        return {'scored': scored}

    @staticmethod
    def generate_revenue_forecast(model, forecast_type, periods):
        """Generate revenue forecasts"""
        from decimal import Decimal
        import random
        
        forecasts = []
        today = timezone.now().date()
        
        if forecast_type == 'monthly':
            delta = timedelta(days=30)
        elif forecast_type == 'quarterly':
            delta = timedelta(days=90)
        else:  # annual
            delta = timedelta(days=365)
        
        base_revenue = Decimal('100000')
        
        for i in range(periods):
            period_start = today + (delta * i)
            period_end = period_start + delta - timedelta(days=1)
            
            # Simulate forecast with some variance
            growth = Decimal(str(random.uniform(-0.1, 0.2)))
            forecasted = base_revenue * (1 + growth)
            variance = forecasted * Decimal('0.15')
            
            forecast = RevenueForecast.objects.create(
                model=model,
                forecast_type=forecast_type,
                period_start=period_start,
                period_end=period_end,
                scenario='expected',
                forecasted_revenue=forecasted,
                confidence_lower=forecasted - variance,
                confidence_upper=forecasted + variance,
                growth_rate=float(growth) * 100
            )
            forecasts.append(forecast)
            
            base_revenue = forecasted
        
        return forecasts

    @staticmethod
    def _extract_features(model, entity_type, entity_id):
        """Extract features for an entity"""
        # In production, this would query the database
        # and compute features based on model.features
        
        features = {}
        for feature in model.model_features.filter(is_active=True):
            # Simulated feature values
            if feature.feature_type == 'numeric':
                features[feature.name] = 0.5
            elif feature.feature_type == 'categorical':
                features[feature.name] = 'category_a'
            elif feature.feature_type == 'boolean':
                features[feature.name] = True
        
        return features

    @staticmethod
    def _get_top_factors(features):
        """Get top contributing factors"""
        import random
        
        factor_names = [
            'Email engagement rate',
            'Website visit frequency',
            'Content downloads',
            'Company size match',
            'Industry fit score',
            'Decision maker level',
            'Budget indicators',
            'Timing signals'
        ]
        
        return random.sample(factor_names, min(5, len(factor_names)))

    @staticmethod
    def _generate_explanation(model_type, value, factors):
        """Generate human-readable explanation"""
        if model_type == 'lead_scoring':
            if value >= 0.7:
                return f"This lead shows strong buying signals based on {', '.join(factors[:3])}. Recommended for immediate follow-up."
            elif value >= 0.4:
                return f"This lead shows moderate interest. Key factors: {', '.join(factors[:2])}. Consider nurturing campaigns."
            else:
                return f"This lead requires more nurturing. Low engagement observed in {factors[0]}."
        
        elif model_type == 'churn_prediction':
            if value >= 0.7:
                return f"High churn risk detected. Warning signs: {', '.join(factors[:3])}. Immediate intervention recommended."
            elif value >= 0.4:
                return f"Moderate churn risk. Monitor {', '.join(factors[:2])} closely."
            else:
                return "Low churn risk. Customer appears engaged and satisfied."
        
        elif model_type == 'deal_probability':
            pct = int(value * 100)
            if value >= 0.7:
                return f"{pct}% win probability. Strong indicators: {', '.join(factors[:2])}."
            else:
                return f"{pct}% win probability. Focus on improving {factors[0]} to increase chances."
        
        return f"Prediction score: {value:.2f}. Key factors: {', '.join(factors[:3])}"


class FeatureEngineeringService:
    """Service for feature engineering"""

    @staticmethod
    def compute_engagement_features(entity_type, entity_id, days=30):
        """Compute engagement-based features"""
        # Would compute from activity logs, email opens, etc.
        return {
            'email_open_rate': 0.45,
            'email_click_rate': 0.12,
            'website_visits': 15,
            'content_downloads': 3,
            'meeting_attendance': 2
        }

    @staticmethod
    def compute_demographic_features(entity_type, entity_id):
        """Compute demographic/firmographic features"""
        return {
            'company_size_score': 0.8,
            'industry_match': 0.9,
            'job_title_score': 0.75,
            'location_score': 1.0
        }

    @staticmethod
    def compute_behavioral_features(entity_type, entity_id):
        """Compute behavioral features"""
        return {
            'recency': 5,  # days since last activity
            'frequency': 12,  # activities in last 30 days
            'monetary': 0,  # value of purchases
            'velocity': 0.8  # rate of engagement change
        }
