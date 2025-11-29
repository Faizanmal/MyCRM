"""
AI-Powered Lead Scoring Module
Uses machine learning to score and prioritize leads
"""

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Count, Avg
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import logging
import pickle

User = get_user_model()
logger = logging.getLogger(__name__)


class LeadScoringEngine:
    """ML-based lead scoring"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.model_type = 'random_forest'  # or 'gradient_boosting'
    
    def train_model(self, leads_queryset):
        """
        Train lead scoring model
        
        Args:
            leads_queryset: QuerySet of leads with conversion data
        
        Returns:
            Training metrics
        """
        # Extract features and labels
        X, y = self._prepare_training_data(leads_queryset)
        
        if len(X) < 10:
            raise ValueError("Not enough training data. Need at least 10 leads.")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        if self.model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
        else:
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Calculate metrics
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        # Get feature importance
        feature_importance = dict(zip(
            self.feature_names,
            self.model.feature_importances_
        ))
        
        metrics = {
            'train_accuracy': train_score,
            'test_accuracy': test_score,
            'feature_importance': feature_importance,
            'training_samples': len(X_train),
            'test_samples': len(X_test)
        }
        
        logger.info(f"Model trained with accuracy: {test_score:.2f}")
        return metrics
    
    def score_lead(self, lead):
        """
        Score a single lead
        
        Args:
            lead: Lead instance
        
        Returns:
            Score (0-100)
        """
        if not self.model:
            raise ValueError("Model not trained. Train model first.")
        
        # Extract features
        features = self._extract_features(lead)
        features_array = np.array([features])
        
        # Scale and predict
        features_scaled = self.scaler.transform(features_array)
        probability = self.model.predict_proba(features_scaled)[0][1]  # Probability of conversion
        
        # Convert to 0-100 score
        score = int(probability * 100)
        
        # Get scoring factors
        factors = self._get_scoring_factors(lead, features)
        
        return score, factors
    
    def score_all_leads(self, leads_queryset):
        """
        Score multiple leads
        
        Returns:
            List of (lead, score, factors)
        """
        results = []
        
        for lead in leads_queryset:
            try:
                score, factors = self.score_lead(lead)
                results.append((lead, score, factors))
            except Exception as e:
                logger.error(f"Error scoring lead {lead.id}: {str(e)}")
        
        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results
    
    def _prepare_training_data(self, queryset):
        """Prepare training data from leads"""
        X = []
        y = []
        
        for lead in queryset:
            features = self._extract_features(lead)
            X.append(features)
            
            # Label: 1 if converted, 0 if not
            is_converted = hasattr(lead, 'status') and lead.status == 'converted'
            y.append(1 if is_converted else 0)
        
        return np.array(X), np.array(y)
    
    def _extract_features(self, lead):
        """Extract features from a lead"""
        features = []
        self.feature_names = []
        
        # Lead source quality (encoded)
        source_scores = {
            'website': 5,
            'referral': 8,
            'social_media': 4,
            'email_campaign': 6,
            'event': 7,
            'other': 3
        }
        source = getattr(lead, 'source', 'other')
        features.append(source_scores.get(source, 3))
        self.feature_names.append('source_score')
        
        # Lead age (days since creation)
        if hasattr(lead, 'created_at'):
            age_days = (timezone.now() - lead.created_at).days
            features.append(age_days)
        else:
            features.append(0)
        self.feature_names.append('age_days')
        
        # Company size indicator
        company_size = getattr(lead, 'company_size', 0)
        features.append(company_size if isinstance(company_size, int) else 0)
        self.feature_names.append('company_size')
        
        # Estimated value
        estimated_value = getattr(lead, 'estimated_value', 0)
        features.append(float(estimated_value) if estimated_value else 0)
        self.feature_names.append('estimated_value')
        
        # Engagement score (interactions count)
        engagement = getattr(lead, 'interaction_count', 0)
        features.append(engagement)
        self.feature_names.append('engagement_count')
        
        # Email provided
        has_email = 1 if getattr(lead, 'email', None) else 0
        features.append(has_email)
        self.feature_names.append('has_email')
        
        # Phone provided
        has_phone = 1 if getattr(lead, 'phone', None) else 0
        features.append(has_phone)
        self.feature_names.append('has_phone')
        
        # Title/position indicator
        title = getattr(lead, 'title', '').lower()
        title_score = 0
        if any(kw in title for kw in ['ceo', 'president', 'owner', 'founder']):
            title_score = 10
        elif any(kw in title for kw in ['vp', 'director', 'manager']):
            title_score = 7
        elif any(kw in title for kw in ['lead', 'head']):
            title_score = 5
        features.append(title_score)
        self.feature_names.append('title_score')
        
        return features
    
    def _get_scoring_factors(self, lead, features):
        """Get factors that influenced the score"""
        factors = []
        
        # Get feature importance
        if self.model and hasattr(self.model, 'feature_importances_'):
            importance_dict = dict(zip(
                self.feature_names,
                self.model.feature_importances_
            ))
            
            # Sort by importance
            sorted_factors = sorted(
                importance_dict.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]  # Top 5 factors
            
            factors = [
                {'factor': name, 'importance': float(importance)}
                for name, importance in sorted_factors
            ]
        
        return factors
    
    def save_model(self, filename):
        """Save trained model to file using joblib (safer than pickle)"""
        import joblib
        import hashlib
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'model_type': self.model_type
        }
        
        # Save using joblib (more secure for sklearn objects)
        joblib.dump(model_data, filename)
        
        # Create checksum file for integrity verification
        with open(filename, 'rb') as f:
            checksum = hashlib.sha256(f.read()).hexdigest()
        with open(f"{filename}.sha256", 'w') as f:
            f.write(checksum)
        
        logger.info(f"Model saved to {filename}")
    
    def load_model(self, filename):
        """Load trained model from file with integrity verification"""
        import joblib
        import hashlib
        import os
        
        # Verify file integrity if checksum exists
        checksum_file = f"{filename}.sha256"
        if os.path.exists(checksum_file):
            with open(checksum_file, 'r') as f:
                expected_checksum = f.read().strip()
            with open(filename, 'rb') as f:
                actual_checksum = hashlib.sha256(f.read()).hexdigest()
            if expected_checksum != actual_checksum:
                raise ValueError(f"Model file integrity check failed for {filename}")
        
        # Load using joblib (safer than pickle)
        model_data = joblib.load(filename)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.model_type = model_data['model_type']
        
        logger.info(f"Model loaded from {filename}")


class RuleBasedScoring:
    """Rule-based lead scoring as alternative/complement to ML"""
    
    DEFAULT_RULES = {
        'source_quality': {
            'referral': 20,
            'website': 15,
            'event': 18,
            'social_media': 10,
            'email_campaign': 12,
            'other': 5
        },
        'company_size': {
            'ranges': [
                (0, 10, 5),
                (11, 50, 10),
                (51, 200, 15),
                (201, 1000, 20),
                (1001, float('inf'), 25)
            ]
        },
        'engagement': {
            'per_interaction': 2,
            'max_points': 20
        },
        'title_seniority': {
            'c_level': 25,
            'vp_director': 20,
            'manager': 15,
            'staff': 10,
            'unknown': 5
        },
        'data_completeness': {
            'per_field': 3,
            'required_fields': ['email', 'phone', 'company', 'title']
        }
    }
    
    def __init__(self, custom_rules=None):
        """Initialize with custom or default rules"""
        self.rules = custom_rules or self.DEFAULT_RULES
    
    def score_lead(self, lead):
        """
        Score lead based on rules
        
        Returns:
            Tuple of (score, breakdown)
        """
        breakdown = {}
        total_score = 0
        
        # Source quality
        source = getattr(lead, 'source', 'other')
        source_score = self.rules['source_quality'].get(source, 5)
        breakdown['source'] = source_score
        total_score += source_score
        
        # Company size
        company_size = getattr(lead, 'company_size', 0)
        size_score = self._score_company_size(company_size)
        breakdown['company_size'] = size_score
        total_score += size_score
        
        # Engagement
        engagement_count = getattr(lead, 'interaction_count', 0)
        engagement_score = min(
            engagement_count * self.rules['engagement']['per_interaction'],
            self.rules['engagement']['max_points']
        )
        breakdown['engagement'] = engagement_score
        total_score += engagement_score
        
        # Title seniority
        title = getattr(lead, 'title', '').lower()
        title_score = self._score_title(title)
        breakdown['title'] = title_score
        total_score += title_score
        
        # Data completeness
        completeness_score = self._score_completeness(lead)
        breakdown['completeness'] = completeness_score
        total_score += completeness_score
        
        return total_score, breakdown
    
    def _score_company_size(self, size):
        """Score based on company size"""
        for min_size, max_size, score in self.rules['company_size']['ranges']:
            if min_size <= size <= max_size:
                return score
        return 0
    
    def _score_title(self, title):
        """Score based on job title"""
        if any(kw in title for kw in ['ceo', 'cto', 'cfo', 'president', 'owner']):
            return self.rules['title_seniority']['c_level']
        elif any(kw in title for kw in ['vp', 'vice president', 'director']):
            return self.rules['title_seniority']['vp_director']
        elif any(kw in title for kw in ['manager', 'lead', 'head']):
            return self.rules['title_seniority']['manager']
        elif title:
            return self.rules['title_seniority']['staff']
        return self.rules['title_seniority']['unknown']
    
    def _score_completeness(self, lead):
        """Score based on data completeness"""
        score = 0
        for field in self.rules['data_completeness']['required_fields']:
            if getattr(lead, field, None):
                score += self.rules['data_completeness']['per_field']
        return score


class LeadScoringManager:
    """Manage lead scoring operations"""
    
    @staticmethod
    def update_lead_scores(leads_queryset=None, method='rule_based'):
        """
        Update scores for all leads
        
        Args:
            leads_queryset: QuerySet of leads (None = all leads)
            method: 'rule_based' or 'ml'
        
        Returns:
            Number of leads scored
        """
        from lead_management.models import Lead
        
        if leads_queryset is None:
            leads_queryset = Lead.objects.filter(status__in=['new', 'contacted', 'qualified'])
        
        if method == 'ml':
            engine = LeadScoringEngine()
            # Load or train model
            try:
                engine.load_model('lead_scoring_model.pkl')
            except FileNotFoundError:
                # Train new model
                all_leads = Lead.objects.all()
                engine.train_model(all_leads)
                engine.save_model('lead_scoring_model.pkl')
            
            results = engine.score_all_leads(leads_queryset)
            
            for lead, score, factors in results:
                lead.score = score
                lead.score_factors = factors
                lead.save(update_fields=['score', 'score_factors'])
        
        else:  # rule_based
            scorer = RuleBasedScoring()
            
            for lead in leads_queryset:
                score, breakdown = scorer.score_lead(lead)
                lead.score = min(score, 100)  # Cap at 100
                lead.score_breakdown = breakdown
                lead.save(update_fields=['score', 'score_breakdown'])
        
        count = leads_queryset.count()
        logger.info(f"Updated scores for {count} leads using {method} method")
        return count
    
    @staticmethod
    def get_hot_leads(limit=20, min_score=70):
        """Get high-scoring leads"""
        from lead_management.models import Lead
        
        return Lead.objects.filter(
            score__gte=min_score,
            status__in=['new', 'contacted', 'qualified']
        ).order_by('-score')[:limit]
    
    @staticmethod
    def get_scoring_analytics():
        """Get analytics on lead scoring"""
        from lead_management.models import Lead
        
        scored_leads = Lead.objects.filter(score__isnull=False)
        
        analytics = {
            'total_scored': scored_leads.count(),
            'average_score': scored_leads.aggregate(Avg('score'))['score__avg'],
            'score_distribution': {
                'hot': scored_leads.filter(score__gte=70).count(),
                'warm': scored_leads.filter(score__gte=40, score__lt=70).count(),
                'cold': scored_leads.filter(score__lt=40).count()
            },
            'by_source': list(scored_leads.values('source').annotate(
                count=Count('id'),
                avg_score=Avg('score')
            ))
        }
        
        return analytics
