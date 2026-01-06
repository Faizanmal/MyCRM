"""
AI-powered churn prediction engine
"""
import logging
from datetime import timedelta

import numpy as np
from django.db.models import Sum
from django.utils import timezone
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler

from contact_management.models import Contact
from task_management.models import Task

from .models import ChurnPrediction

logger = logging.getLogger(__name__)


class ChurnPredictionEngine:
    """Predict customer churn using machine learning"""

    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.model_version = '1.0'

    def extract_features(self, contact):
        """Extract features for churn prediction"""
        now = timezone.now()

        # Time-based features
        days_since_creation = (now - contact.created_at).days if contact.created_at else 0
        days_since_last_contact = (now - contact.last_contacted_at).days if contact.last_contacted_at else 999

        # Engagement features
        total_opportunities = contact.opportunities.count()
        open_opportunities = contact.opportunities.filter(stage__in=['prospecting', 'qualification', 'proposal']).count()
        won_opportunities = contact.opportunities.filter(stage='won').count()
        lost_opportunities = contact.opportunities.filter(stage='lost').count()

        total_revenue = contact.opportunities.filter(stage='won').aggregate(
            total=Sum('amount')
        )['total'] or 0

        # Task/Activity features
        overdue_tasks = Task.objects.filter(
            contact=contact,
            due_date__lt=now,
            status='pending'
        ).count()

        completed_tasks = Task.objects.filter(
            contact=contact,
            status='completed'
        ).count()

        # Communication frequency
        recent_interactions = contact.activities.filter(
            created_at__gte=now - timedelta(days=30)
        ).count()

        # Calculate engagement score
        engagement_score = (
            (recent_interactions * 2) +
            (completed_tasks) +
            (won_opportunities * 5) -
            (overdue_tasks * 3) -
            (lost_opportunities * 2)
        )

        # Win rate
        total_closed = won_opportunities + lost_opportunities
        win_rate = won_opportunities / total_closed if total_closed > 0 else 0

        # Revenue trend (simplified)
        recent_revenue = contact.opportunities.filter(
            stage='won',
            close_date__gte=now - timedelta(days=90)
        ).aggregate(total=Sum('amount'))['total'] or 0

        features = {
            'days_since_creation': days_since_creation,
            'days_since_last_contact': days_since_last_contact,
            'total_opportunities': total_opportunities,
            'open_opportunities': open_opportunities,
            'won_opportunities': won_opportunities,
            'lost_opportunities': lost_opportunities,
            'total_revenue': float(total_revenue),
            'recent_revenue': float(recent_revenue),
            'overdue_tasks': overdue_tasks,
            'completed_tasks': completed_tasks,
            'recent_interactions': recent_interactions,
            'engagement_score': engagement_score,
            'win_rate': win_rate,
        }

        return features

    def train_model(self, contacts=None):
        """Train churn prediction model"""
        if contacts is None:
            contacts = Contact.objects.all()

        # Prepare training data
        X_data = []
        y_data = []

        for contact in contacts:
            features = self.extract_features(contact)
            X_data.append(list(features.values()))

            # Define churn (simplified: no activity in 90 days)
            churned = contact.last_contacted_at and \
                     (timezone.now() - contact.last_contacted_at).days > 90
            y_data.append(1 if churned else 0)

        if len(X_data) < 10:
            logger.warning("Insufficient data for training churn model")
            return False

        X = np.array(X_data)
        y = np.array(y_data)

        # Store feature names
        first_contact = contacts.first()
        if first_contact:
            self.feature_names = list(self.extract_features(first_contact).keys())

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Train model
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=3,
            random_state=42
        )

        self.model.fit(X_scaled, y)

        logger.info(f"Churn prediction model trained with {len(X)} samples")
        return True

    def predict_churn(self, contact):
        """Predict churn probability for a contact"""
        if self.model is None:
            self.train_model()

        features = self.extract_features(contact)
        X = np.array([list(features.values())])
        X_scaled = self.scaler.transform(X)

        # Get prediction probability
        churn_prob = self.model.predict_proba(X_scaled)[0][1]

        # Determine risk level
        if churn_prob >= 0.75:
            risk_level = 'critical'
        elif churn_prob >= 0.5:
            risk_level = 'high'
        elif churn_prob >= 0.25:
            risk_level = 'medium'
        else:
            risk_level = 'low'

        # Get feature importance
        feature_importance = dict(zip(
            self.feature_names,
            self.model.feature_importances_, strict=False
        ))

        # Generate recommendations
        recommendations = self._generate_churn_recommendations(
            contact, features, churn_prob
        )

        # Create or update prediction
        prediction, created = ChurnPrediction.objects.update_or_create(
            contact=contact,
            defaults={
                'churn_probability': churn_prob,
                'risk_level': risk_level,
                'factors': feature_importance,
                'confidence_score': 0.85,  # Simplified
                'recommended_actions': recommendations,
                'model_version': self.model_version,
                'expires_at': timezone.now() + timedelta(days=7)
            }
        )

        return prediction

    def _generate_churn_recommendations(self, contact, features, churn_prob):
        """Generate action recommendations based on churn risk"""
        recommendations = []

        if features['days_since_last_contact'] > 30:
            recommendations.append({
                'action': 'Schedule immediate check-in call',
                'priority': 'high',
                'reason': 'No recent contact'
            })

        if features['overdue_tasks'] > 0:
            recommendations.append({
                'action': 'Complete overdue tasks',
                'priority': 'high',
                'reason': f'{features["overdue_tasks"]} overdue tasks'
            })

        if features['open_opportunities'] == 0 and features['won_opportunities'] > 0:
            recommendations.append({
                'action': 'Explore upsell/cross-sell opportunities',
                'priority': 'medium',
                'reason': 'No active opportunities for existing customer'
            })

        if features['recent_interactions'] < 2:
            recommendations.append({
                'action': 'Increase engagement frequency',
                'priority': 'medium',
                'reason': 'Low recent engagement'
            })

        if churn_prob > 0.7:
            recommendations.append({
                'action': 'Offer retention incentive',
                'priority': 'critical',
                'reason': 'High churn risk'
            })

        return recommendations

    def bulk_predict(self, contacts=None):
        """Predict churn for multiple contacts"""
        if contacts is None:
            contacts = Contact.objects.filter(
                contact_type='customer'
            )

        predictions = []
        for contact in contacts:
            try:
                prediction = self.predict_churn(contact)
                predictions.append(prediction)
            except Exception as e:
                logger.error(f"Failed to predict churn for contact {contact.id}: {e}")

        return predictions
