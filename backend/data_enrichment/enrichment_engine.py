"""
Data Enrichment Engine
Core enrichment processing and provider integrations
"""

import logging
import hashlib
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from django.utils import timezone
import json

logger = logging.getLogger(__name__)


@dataclass
class EnrichmentResult:
    """Result from an enrichment operation"""
    success: bool
    provider: str
    data: Dict
    fields_enriched: List[str]
    error: Optional[str] = None
    response_time_ms: int = 0
    credits_used: int = 1


class EnrichmentEngine:
    """Main engine for data enrichment operations"""
    
    def __init__(self):
        self.providers = {}
        self._load_providers()
    
    def _load_providers(self):
        """Load configured enrichment providers"""
        from .models import EnrichmentProvider
        
        for provider in EnrichmentProvider.objects.filter(is_active=True, is_configured=True):
            self.providers[provider.provider_type] = provider
    
    def enrich_person(self, email: str, domain: Optional[str] = None) -> EnrichmentResult:
        """Enrich person data based on email"""
        
        if not domain:
            domain = email.split('@')[1] if '@' in email else ''
        
        # Try each configured provider
        results = []
        
        for provider_type, provider in self.providers.items():
            if provider.can_enrich_person:
                try:
                    result = self._call_provider(provider, 'person', {
                        'email': email,
                        'domain': domain
                    })
                    if result.success:
                        results.append(result)
                except Exception as e:
                    logger.error(f"Error with provider {provider_type}: {e}")
        
        # Merge results from multiple providers
        if results:
            return self._merge_person_results(results)
        
        return EnrichmentResult(
            success=False,
            provider='none',
            data={},
            fields_enriched=[],
            error='No provider could enrich this person'
        )
    
    def enrich_company(self, domain: str) -> EnrichmentResult:
        """Enrich company data based on domain"""
        
        results = []
        
        for provider_type, provider in self.providers.items():
            if provider.can_enrich_company:
                try:
                    result = self._call_provider(provider, 'company', {
                        'domain': domain
                    })
                    if result.success:
                        results.append(result)
                except Exception as e:
                    logger.error(f"Error with provider {provider_type}: {e}")
        
        if results:
            return self._merge_company_results(results)
        
        return EnrichmentResult(
            success=False,
            provider='none',
            data={},
            fields_enriched=[],
            error='No provider could enrich this company'
        )
    
    def verify_email(self, email: str) -> EnrichmentResult:
        """Verify email deliverability"""
        
        for provider_type, provider in self.providers.items():
            if provider.can_verify_email:
                try:
                    result = self._call_provider(provider, 'email_verify', {
                        'email': email
                    })
                    if result.success:
                        return result
                except Exception as e:
                    logger.error(f"Error verifying email with {provider_type}: {e}")
        
        # Fallback to basic validation
        return self._basic_email_validation(email)
    
    def get_technographics(self, domain: str) -> EnrichmentResult:
        """Get technology stack for a company"""
        
        for provider_type, provider in self.providers.items():
            if provider.can_get_technographics:
                try:
                    result = self._call_provider(provider, 'technographics', {
                        'domain': domain
                    })
                    if result.success:
                        return result
                except Exception as e:
                    logger.error(f"Error getting technographics from {provider_type}: {e}")
        
        return EnrichmentResult(
            success=False,
            provider='none',
            data={},
            fields_enriched=[],
            error='No provider available for technographics'
        )
    
    def get_intent_signals(self, domain: str, topics: List[str] = None) -> EnrichmentResult:
        """Get buyer intent signals for a company"""
        
        for provider_type, provider in self.providers.items():
            if provider.can_get_intent:
                try:
                    result = self._call_provider(provider, 'intent', {
                        'domain': domain,
                        'topics': topics or []
                    })
                    if result.success:
                        return result
                except Exception as e:
                    logger.error(f"Error getting intent from {provider_type}: {e}")
        
        return EnrichmentResult(
            success=False,
            provider='none',
            data={},
            fields_enriched=[],
            error='No provider available for intent signals'
        )
    
    def _call_provider(self, provider, operation: str, params: Dict) -> EnrichmentResult:
        """Call a specific provider's API"""
        
        start_time = timezone.now()
        
        # In production, this would make actual API calls
        # For now, we'll use a mock implementation
        result = self._mock_provider_call(provider.provider_type, operation, params)
        
        elapsed_ms = int((timezone.now() - start_time).total_seconds() * 1000)
        result.response_time_ms = elapsed_ms
        
        # Update provider stats
        provider.total_requests += 1
        if result.success:
            provider.successful_requests += 1
        provider.daily_requests_used += 1
        
        # Update average response time
        if provider.average_response_time == 0:
            provider.average_response_time = elapsed_ms
        else:
            provider.average_response_time = (
                provider.average_response_time * 0.9 + elapsed_ms * 0.1
            )
        provider.save()
        
        return result
    
    def _mock_provider_call(self, provider_type: str, operation: str, params: Dict) -> EnrichmentResult:
        """Mock provider call for development/testing"""
        
        # Generate deterministic mock data based on input
        if operation == 'person':
            email = params.get('email', '')
            domain = params.get('domain', '')
            
            # Generate mock person data
            name_hash = hashlib.md5(email.encode()).hexdigest()[:8]
            
            return EnrichmentResult(
                success=True,
                provider=provider_type,
                data={
                    'first_name': f'John_{name_hash[:4]}',
                    'last_name': f'Doe_{name_hash[4:]}',
                    'title': 'Product Manager',
                    'seniority': 'Manager',
                    'department': 'Product',
                    'phone': f'+1-555-{name_hash[:3]}-{name_hash[3:7]}',
                    'city': 'San Francisco',
                    'state': 'California',
                    'country': 'United States',
                    'linkedin_url': f'https://linkedin.com/in/{name_hash}',
                    'twitter_handle': f'@user_{name_hash[:6]}',
                    'employment_history': [
                        {
                            'company': domain.split('.')[0].title(),
                            'title': 'Product Manager',
                            'start_date': '2022-01',
                            'is_current': True
                        }
                    ],
                    'skills': ['Product Management', 'Agile', 'Data Analysis']
                },
                fields_enriched=[
                    'first_name', 'last_name', 'title', 'seniority', 'department',
                    'phone', 'city', 'state', 'country', 'linkedin_url',
                    'twitter_handle', 'employment_history', 'skills'
                ]
            )
        
        elif operation == 'company':
            domain = params.get('domain', '')
            domain_hash = hashlib.md5(domain.encode()).hexdigest()[:8]
            
            return EnrichmentResult(
                success=True,
                provider=provider_type,
                data={
                    'name': domain.split('.')[0].title() + ' Inc.',
                    'description': f'A leading company in the {domain} space.',
                    'industry': 'Technology',
                    'employee_count': int(domain_hash, 16) % 10000 + 100,
                    'employee_range': '101-500',
                    'annual_revenue': (int(domain_hash, 16) % 100) * 1000000,
                    'founded_year': 2010 + (int(domain_hash[:2], 16) % 10),
                    'headquarters_city': 'San Francisco',
                    'headquarters_state': 'California',
                    'headquarters_country': 'United States',
                    'website': f'https://{domain}',
                    'linkedin_url': f'https://linkedin.com/company/{domain.split(".")[0]}',
                    'logo_url': f'https://logo.clearbit.com/{domain}',
                    'technologies': ['Python', 'React', 'AWS', 'PostgreSQL'],
                    'tech_categories': {
                        'frontend': ['React'],
                        'backend': ['Python'],
                        'hosting': ['AWS'],
                        'database': ['PostgreSQL']
                    }
                },
                fields_enriched=[
                    'name', 'description', 'industry', 'employee_count',
                    'annual_revenue', 'founded_year', 'headquarters_city',
                    'website', 'linkedin_url', 'logo_url', 'technologies'
                ]
            )
        
        elif operation == 'email_verify':
            email = params.get('email', '')
            
            # Basic validation result
            is_valid = '@' in email and '.' in email.split('@')[1]
            domain = email.split('@')[1] if is_valid else ''
            
            return EnrichmentResult(
                success=True,
                provider=provider_type,
                data={
                    'status': 'valid' if is_valid else 'invalid',
                    'is_deliverable': is_valid,
                    'is_smtp_valid': is_valid,
                    'is_free_email': domain in ['gmail.com', 'yahoo.com', 'hotmail.com'],
                    'is_role_email': email.split('@')[0] in ['info', 'support', 'sales', 'admin'],
                    'is_disposable': False,
                    'quality_score': 0.9 if is_valid else 0.1,
                    'domain': domain
                },
                fields_enriched=['status', 'is_deliverable', 'quality_score']
            )
        
        elif operation == 'technographics':
            domain = params.get('domain', '')
            
            return EnrichmentResult(
                success=True,
                provider=provider_type,
                data={
                    'technologies': [
                        {'name': 'Google Analytics', 'category': 'analytics'},
                        {'name': 'Salesforce', 'category': 'crm'},
                        {'name': 'HubSpot', 'category': 'marketing_automation'},
                        {'name': 'AWS', 'category': 'hosting'},
                        {'name': 'Stripe', 'category': 'payment'},
                    ]
                },
                fields_enriched=['technologies']
            )
        
        elif operation == 'intent':
            return EnrichmentResult(
                success=True,
                provider=provider_type,
                data={
                    'signals': [
                        {
                            'topic': 'CRM Software',
                            'type': 'search',
                            'strength': 'strong',
                            'score': 75
                        },
                        {
                            'topic': 'Sales Automation',
                            'type': 'content',
                            'strength': 'moderate',
                            'score': 55
                        }
                    ]
                },
                fields_enriched=['intent_signals']
            )
        
        return EnrichmentResult(
            success=False,
            provider=provider_type,
            data={},
            fields_enriched=[],
            error=f'Unknown operation: {operation}'
        )
    
    def _merge_person_results(self, results: List[EnrichmentResult]) -> EnrichmentResult:
        """Merge results from multiple providers for person enrichment"""
        
        merged_data = {}
        all_fields = set()
        providers_used = []
        
        # Priority merge - later providers override earlier ones
        for result in results:
            for key, value in result.data.items():
                if value:  # Only override with non-empty values
                    merged_data[key] = value
            all_fields.update(result.fields_enriched)
            providers_used.append(result.provider)
        
        return EnrichmentResult(
            success=True,
            provider=','.join(providers_used),
            data=merged_data,
            fields_enriched=list(all_fields)
        )
    
    def _merge_company_results(self, results: List[EnrichmentResult]) -> EnrichmentResult:
        """Merge results from multiple providers for company enrichment"""
        
        merged_data = {}
        all_fields = set()
        providers_used = []
        
        for result in results:
            for key, value in result.data.items():
                if value:
                    merged_data[key] = value
            all_fields.update(result.fields_enriched)
            providers_used.append(result.provider)
        
        return EnrichmentResult(
            success=True,
            provider=','.join(providers_used),
            data=merged_data,
            fields_enriched=list(all_fields)
        )
    
    def _basic_email_validation(self, email: str) -> EnrichmentResult:
        """Basic email validation without external provider"""
        
        # Simple regex validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        is_valid = bool(re.match(email_pattern, email))
        
        domain = email.split('@')[1] if '@' in email else ''
        
        # Check for common free email providers
        free_providers = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com']
        is_free = domain.lower() in free_providers
        
        # Check for role-based emails
        role_prefixes = ['info', 'support', 'sales', 'admin', 'contact', 'help', 'service']
        is_role = email.split('@')[0].lower() in role_prefixes
        
        return EnrichmentResult(
            success=True,
            provider='basic_validation',
            data={
                'status': 'valid' if is_valid else 'invalid',
                'is_deliverable': None,  # Cannot determine without SMTP check
                'is_free_email': is_free,
                'is_role_email': is_role,
                'is_disposable': False,  # Cannot determine without database
                'quality_score': 0.7 if is_valid else 0.0,
                'domain': domain
            },
            fields_enriched=['status', 'is_free_email', 'is_role_email', 'quality_score']
        )


class NewsEnrichmentEngine:
    """Engine for fetching and analyzing news"""
    
    def fetch_company_news(self, company_name: str, domain: str, days_back: int = 30) -> List[Dict]:
        """Fetch recent news for a company"""
        
        # In production, this would call a news API
        # For now, return mock data
        return [
            {
                'title': f'{company_name} Announces New Product Launch',
                'summary': f'{company_name} has announced a new product targeting enterprise customers.',
                'source_name': 'TechCrunch',
                'source_url': f'https://techcrunch.com/{domain}-news',
                'published_at': (timezone.now() - timedelta(days=5)).isoformat(),
                'alert_type': 'product_launch',
                'sentiment': 'positive',
                'is_sales_trigger': True
            },
            {
                'title': f'{company_name} Expands to European Market',
                'summary': f'{company_name} opens new office in London as part of European expansion.',
                'source_name': 'Business Insider',
                'source_url': f'https://businessinsider.com/{domain}-expansion',
                'published_at': (timezone.now() - timedelta(days=12)).isoformat(),
                'alert_type': 'expansion',
                'sentiment': 'positive',
                'is_sales_trigger': True
            }
        ]
    
    def analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of news text"""
        
        # Simple keyword-based sentiment analysis
        positive_words = ['growth', 'success', 'launch', 'expansion', 'profit', 'award']
        negative_words = ['layoff', 'decline', 'loss', 'lawsuit', 'problem', 'crisis']
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        return 'neutral'
    
    def is_sales_trigger(self, alert_type: str, sentiment: str) -> bool:
        """Determine if news is a sales trigger"""
        
        trigger_types = ['funding', 'expansion', 'product_launch', 'executive_change', 'acquisition']
        
        return alert_type in trigger_types and sentiment in ['positive', 'neutral']


class SocialProfileEngine:
    """Engine for social media profile enrichment"""
    
    def enrich_linkedin(self, linkedin_url: str) -> Dict:
        """Enrich from LinkedIn profile"""
        
        # In production, this would use LinkedIn API or scraping service
        return {
            'platform': 'linkedin',
            'profile_url': linkedin_url,
            'display_name': 'Professional User',
            'headline': 'Building amazing products',
            'connections_count': 500,
            'recent_posts': [],
            'interests': ['Technology', 'Sales', 'Marketing']
        }
    
    def enrich_twitter(self, twitter_handle: str) -> Dict:
        """Enrich from Twitter profile"""
        
        return {
            'platform': 'twitter',
            'username': twitter_handle,
            'display_name': 'Twitter User',
            'bio': 'Tweets about tech and business',
            'followers_count': 1000,
            'following_count': 500,
            'recent_posts': []
        }


def calculate_enrichment_score(profile) -> int:
    """Calculate enrichment completeness score (0-100)"""
    
    fields_weights = {
        'first_name': 5,
        'last_name': 5,
        'title': 10,
        'phone': 5,
        'city': 3,
        'country': 3,
        'linkedin_profile': 10,
        'twitter_handle': 5,
        'employment_history': 15,
        'education': 10,
        'skills': 10,
        'work_email': 8,
        'seniority': 6,
        'department': 5
    }
    
    score = 0
    
    for field, weight in fields_weights.items():
        value = getattr(profile, field, None)
        if value:
            if isinstance(value, (list, dict)):
                if value:  # Non-empty list/dict
                    score += weight
            else:
                score += weight
    
    return min(100, score)


def calculate_company_enrichment_score(company) -> int:
    """Calculate company enrichment completeness score (0-100)"""
    
    fields_weights = {
        'name': 10,
        'description': 5,
        'industry': 8,
        'employee_count': 8,
        'annual_revenue': 10,
        'founded_year': 5,
        'headquarters_city': 5,
        'headquarters_country': 5,
        'website': 5,
        'linkedin_url': 5,
        'logo_url': 3,
        'technologies': 10,
        'key_people': 8,
        'funding_total': 8,
        'phone': 5
    }
    
    score = 0
    
    for field, weight in fields_weights.items():
        value = getattr(company, field, None)
        if value:
            if isinstance(value, (list, dict)):
                if value:
                    score += weight
            else:
                score += weight
    
    return min(100, score)
