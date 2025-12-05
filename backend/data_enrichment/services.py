"""
Data Enrichment Services
Business logic for data enrichment operations
"""

import logging
from typing import Dict, List, Optional
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from .models import (
    EnrichmentProfile, CompanyEnrichment, TechnographicData,
    IntentSignal, NewsAlert, EmailVerification, EnrichmentJob,
    EnrichmentActivity, EnrichmentProvider, SocialProfile, FinancialData
)
from .enrichment_engine import (
    EnrichmentEngine, NewsEnrichmentEngine, SocialProfileEngine,
    calculate_enrichment_score, calculate_company_enrichment_score
)

logger = logging.getLogger(__name__)


class EnrichmentService:
    """Main service for data enrichment operations"""
    
    def __init__(self):
        self.engine = EnrichmentEngine()
        self.news_engine = NewsEnrichmentEngine()
        self.social_engine = SocialProfileEngine()
    
    @transaction.atomic
    def enrich_contact_or_lead(
        self,
        email: str,
        contact=None,
        lead=None,
        enrich_company: bool = True,
        verify_email: bool = True,
        get_social: bool = True
    ) -> Dict:
        """Full enrichment for a contact or lead"""
        
        domain = email.split('@')[1] if '@' in email else ''
        
        # Get or create enrichment profile
        profile, created = EnrichmentProfile.objects.get_or_create(
            email=email,
            defaults={
                'contact': contact,
                'lead': lead,
                'domain': domain,
                'status': 'enriching'
            }
        )
        
        if not created:
            profile.status = 'enriching'
            profile.save()
        
        results = {
            'profile_id': str(profile.id),
            'email': email,
            'person_enriched': False,
            'company_enriched': False,
            'email_verified': False,
            'fields_enriched': [],
            'errors': []
        }
        
        try:
            # 1. Enrich person data
            person_result = self.engine.enrich_person(email, domain)
            
            if person_result.success:
                self._update_profile_from_person_data(profile, person_result.data)
                results['person_enriched'] = True
                results['fields_enriched'].extend(person_result.fields_enriched)
                
                # Log activity
                self._log_activity(
                    'enrich_person', profile=profile,
                    success=True, data=person_result.data,
                    fields=person_result.fields_enriched,
                    response_time=person_result.response_time_ms
                )
            else:
                results['errors'].append(f"Person enrichment: {person_result.error}")
            
            # 2. Enrich company data
            if enrich_company and domain:
                company_result = self._enrich_company(domain)
                if company_result:
                    results['company_enriched'] = True
                    results['fields_enriched'].append('company_data')
            
            # 3. Verify email
            if verify_email:
                verification = self._verify_email(email)
                if verification:
                    results['email_verified'] = True
                    results['fields_enriched'].append('email_verification')
            
            # 4. Get social profiles
            if get_social and profile.linkedin_profile:
                linkedin_url = profile.linkedin_profile.get('url', '')
                if linkedin_url:
                    self._enrich_social_profile(profile, 'linkedin', linkedin_url)
            
            if get_social and profile.twitter_handle:
                self._enrich_social_profile(profile, 'twitter', profile.twitter_handle)
            
            # Calculate enrichment score
            profile.enrichment_score = calculate_enrichment_score(profile)
            profile.status = 'enriched' if results['person_enriched'] else 'partial'
            profile.last_enriched_at = timezone.now()
            profile.save()
            
            results['enrichment_score'] = profile.enrichment_score
            
        except Exception as e:
            logger.error(f"Error enriching {email}: {e}")
            profile.status = 'failed'
            profile.save()
            results['errors'].append(str(e))
        
        return results
    
    def _update_profile_from_person_data(self, profile: EnrichmentProfile, data: Dict):
        """Update profile with person enrichment data"""
        
        field_mapping = {
            'first_name': 'first_name',
            'last_name': 'last_name',
            'full_name': 'full_name',
            'title': 'title',
            'seniority': 'seniority',
            'department': 'department',
            'phone': 'phone',
            'mobile_phone': 'mobile_phone',
            'work_email': 'work_email',
            'personal_email': 'personal_email',
            'city': 'city',
            'state': 'state',
            'country': 'country',
            'timezone': 'timezone',
            'twitter_handle': 'twitter_handle',
            'github_username': 'github_username',
        }
        
        for data_field, model_field in field_mapping.items():
            if data_field in data and data[data_field]:
                setattr(profile, model_field, data[data_field])
        
        # Handle complex fields
        if 'linkedin_url' in data:
            profile.linkedin_profile = {'url': data['linkedin_url']}
        
        if 'employment_history' in data:
            profile.employment_history = data['employment_history']
        
        if 'education' in data:
            profile.education = data['education']
        
        if 'skills' in data:
            profile.skills = data['skills']
        
        profile.save()
    
    @transaction.atomic
    def _enrich_company(self, domain: str) -> Optional[CompanyEnrichment]:
        """Enrich company data"""
        
        # Check if we have recent data
        try:
            existing = CompanyEnrichment.objects.get(domain=domain)
            # Return existing if less than 30 days old
            if existing.last_enriched_at and (timezone.now() - existing.last_enriched_at).days < 30:
                return existing
        except CompanyEnrichment.DoesNotExist:
            existing = None
        
        # Fetch new data
        result = self.engine.enrich_company(domain)
        
        if not result.success:
            return existing
        
        data = result.data
        
        company, created = CompanyEnrichment.objects.update_or_create(
            domain=domain,
            defaults={
                'name': data.get('name', ''),
                'description': data.get('description', ''),
                'industry': data.get('industry', ''),
                'employee_count': data.get('employee_count'),
                'employee_range': data.get('employee_range', ''),
                'annual_revenue': data.get('annual_revenue'),
                'founded_year': data.get('founded_year'),
                'headquarters_city': data.get('headquarters_city', ''),
                'headquarters_state': data.get('headquarters_state', ''),
                'headquarters_country': data.get('headquarters_country', ''),
                'website': data.get('website', ''),
                'linkedin_url': data.get('linkedin_url', ''),
                'logo_url': data.get('logo_url', ''),
                'technologies': data.get('technologies', []),
                'tech_categories': data.get('tech_categories', {}),
                'last_enriched_at': timezone.now(),
                'enrichment_sources': [result.provider]
            }
        )
        
        company.enrichment_score = calculate_company_enrichment_score(company)
        company.save()
        
        # Log activity
        self._log_activity(
            'enrich_company', company=company,
            success=True, data=data,
            fields=result.fields_enriched,
            response_time=result.response_time_ms
        )
        
        # Process technographics
        if data.get('technologies'):
            self._process_technographics(company, data['technologies'])
        
        return company
    
    def _process_technographics(self, company: CompanyEnrichment, technologies: List):
        """Process and store technographic data"""
        
        for tech in technologies:
            if isinstance(tech, dict):
                name = tech.get('name', '')
                category = tech.get('category', 'other')
            else:
                name = str(tech)
                category = 'other'
            
            TechnographicData.objects.update_or_create(
                company=company,
                technology_name=name,
                defaults={
                    'category': category,
                    'confidence_score': 0.8
                }
            )
    
    @transaction.atomic
    def _verify_email(self, email: str) -> Optional[EmailVerification]:
        """Verify email address"""
        
        # Check cache
        try:
            existing = EmailVerification.objects.get(email=email)
            # Return if less than 7 days old
            if (timezone.now() - existing.verified_at).days < 7:
                return existing
        except EmailVerification.DoesNotExist:
            pass
        
        result = self.engine.verify_email(email)
        
        if not result.success:
            return None
        
        data = result.data
        domain = email.split('@')[1] if '@' in email else ''
        
        verification, _ = EmailVerification.objects.update_or_create(
            email=email,
            defaults={
                'status': data.get('status', 'unknown'),
                'is_deliverable': data.get('is_deliverable'),
                'is_smtp_valid': data.get('is_smtp_valid'),
                'is_free_email': data.get('is_free_email'),
                'is_role_email': data.get('is_role_email'),
                'is_disposable': data.get('is_disposable'),
                'quality_score': data.get('quality_score', 0),
                'domain': domain,
                'verification_provider': result.provider
            }
        )
        
        return verification
    
    def _enrich_social_profile(self, profile: EnrichmentProfile, platform: str, identifier: str):
        """Enrich social media profile"""
        
        if platform == 'linkedin':
            data = self.social_engine.enrich_linkedin(identifier)
        elif platform == 'twitter':
            data = self.social_engine.enrich_twitter(identifier)
        else:
            return
        
        SocialProfile.objects.update_or_create(
            enrichment_profile=profile,
            platform=platform,
            defaults={
                'profile_url': data.get('profile_url', identifier),
                'username': data.get('username', ''),
                'display_name': data.get('display_name', ''),
                'headline': data.get('headline', ''),
                'bio': data.get('bio', ''),
                'followers_count': data.get('followers_count'),
                'following_count': data.get('following_count'),
                'connections_count': data.get('connections_count'),
                'recent_posts': data.get('recent_posts', []),
                'interests': data.get('interests', [])
            }
        )
    
    def _log_activity(
        self,
        activity_type: str,
        profile: EnrichmentProfile = None,
        company: CompanyEnrichment = None,
        success: bool = True,
        data: Dict = None,
        fields: List = None,
        response_time: int = 0,
        error: str = ''
    ):
        """Log enrichment activity"""
        
        EnrichmentActivity.objects.create(
            activity_type=activity_type,
            enrichment_profile=profile,
            company=company,
            success=success,
            error_message=error,
            fields_enriched=fields or [],
            data_returned=data or {},
            response_time_ms=response_time
        )
    
    @transaction.atomic
    def fetch_company_news(self, domain: str, days_back: int = 30) -> List[NewsAlert]:
        """Fetch news for a company"""
        
        try:
            company = CompanyEnrichment.objects.get(domain=domain)
        except CompanyEnrichment.DoesNotExist:
            # Enrich company first
            company = self._enrich_company(domain)
            if not company:
                return []
        
        news_items = self.news_engine.fetch_company_news(
            company.name, domain, days_back
        )
        
        alerts = []
        for item in news_items:
            alert, created = NewsAlert.objects.get_or_create(
                company=company,
                title=item['title'],
                source_url=item.get('source_url', ''),
                defaults={
                    'alert_type': item.get('alert_type', 'general'),
                    'summary': item.get('summary', ''),
                    'source_name': item.get('source_name', ''),
                    'published_at': item.get('published_at'),
                    'sentiment': item.get('sentiment', 'neutral'),
                    'is_sales_trigger': item.get('is_sales_trigger', False)
                }
            )
            alerts.append(alert)
        
        return alerts
    
    @transaction.atomic
    def get_intent_signals(self, domain: str, topics: List[str] = None) -> List[IntentSignal]:
        """Get intent signals for a company"""
        
        try:
            company = CompanyEnrichment.objects.get(domain=domain)
        except CompanyEnrichment.DoesNotExist:
            company = self._enrich_company(domain)
            if not company:
                return []
        
        result = self.engine.get_intent_signals(domain, topics)
        
        if not result.success:
            return []
        
        signals = []
        for signal_data in result.data.get('signals', []):
            signal = IntentSignal.objects.create(
                company=company,
                intent_type=signal_data.get('type', 'search'),
                topic=signal_data.get('topic', ''),
                strength=signal_data.get('strength', 'moderate'),
                score=signal_data.get('score', 50),
                expires_at=timezone.now() + timedelta(days=30)
            )
            signals.append(signal)
        
        return signals


class BulkEnrichmentService:
    """Service for bulk enrichment operations"""
    
    def __init__(self):
        self.enrichment_service = EnrichmentService()
    
    @transaction.atomic
    def create_bulk_job(
        self,
        emails: List[str],
        user,
        enrichment_types: List[str] = None
    ) -> EnrichmentJob:
        """Create a bulk enrichment job"""
        
        if enrichment_types is None:
            enrichment_types = ['person', 'company', 'email_verify']
        
        job = EnrichmentJob.objects.create(
            job_type='bulk',
            total_records=len(emails),
            initiated_by=user,
            enrichment_types=enrichment_types
        )
        
        return job
    
    def process_bulk_job(self, job_id: str):
        """Process a bulk enrichment job (called by Celery)"""
        
        job = EnrichmentJob.objects.get(id=job_id)
        job.status = 'in_progress'
        job.started_at = timezone.now()
        job.save()
        
        # Get profiles to enrich
        profiles = EnrichmentProfile.objects.filter(
            status__in=['pending', 'stale']
        )[:job.total_records]
        
        for profile in profiles:
            try:
                self.enrichment_service.enrich_contact_or_lead(
                    email=profile.email,
                    enrich_company='company' in job.enrichment_types,
                    verify_email='email_verify' in job.enrichment_types
                )
                job.successful_records += 1
            except Exception as e:
                job.failed_records += 1
                job.error_log.append({
                    'email': profile.email,
                    'error': str(e)
                })
            
            job.processed_records += 1
            job.save()
        
        job.status = 'completed' if job.failed_records == 0 else 'partial'
        job.completed_at = timezone.now()
        job.save()
        
        return job


class EnrichmentStatsService:
    """Service for enrichment statistics and analytics"""
    
    @staticmethod
    def get_enrichment_stats() -> Dict:
        """Get overall enrichment statistics"""
        
        total_profiles = EnrichmentProfile.objects.count()
        enriched_profiles = EnrichmentProfile.objects.filter(status='enriched').count()
        
        total_companies = CompanyEnrichment.objects.count()
        
        verified_emails = EmailVerification.objects.filter(status='valid').count()
        
        intent_signals = IntentSignal.objects.filter(
            detected_at__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        news_alerts = NewsAlert.objects.filter(
            is_sales_trigger=True,
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        return {
            'total_profiles': total_profiles,
            'enriched_profiles': enriched_profiles,
            'enrichment_rate': enriched_profiles / total_profiles * 100 if total_profiles > 0 else 0,
            'total_companies': total_companies,
            'verified_emails': verified_emails,
            'recent_intent_signals': intent_signals,
            'recent_sales_triggers': news_alerts
        }
    
    @staticmethod
    def get_provider_stats() -> List[Dict]:
        """Get statistics for each enrichment provider"""
        
        providers = EnrichmentProvider.objects.filter(is_active=True)
        
        stats = []
        for provider in providers:
            success_rate = (
                provider.successful_requests / provider.total_requests * 100
                if provider.total_requests > 0 else 0
            )
            
            stats.append({
                'provider': provider.name,
                'provider_type': provider.provider_type,
                'total_requests': provider.total_requests,
                'successful_requests': provider.successful_requests,
                'success_rate': round(success_rate, 1),
                'average_response_time': round(provider.average_response_time, 0),
                'daily_usage': provider.daily_requests_used,
                'daily_limit': provider.requests_per_day
            })
        
        return stats
    
    @staticmethod
    def get_recent_enrichments(limit: int = 10) -> List[Dict]:
        """Get recent enrichment activities"""
        
        activities = EnrichmentActivity.objects.select_related(
            'enrichment_profile', 'company'
        ).order_by('-created_at')[:limit]
        
        return [
            {
                'type': activity.activity_type,
                'email': activity.enrichment_profile.email if activity.enrichment_profile else None,
                'company': activity.company.name if activity.company else None,
                'success': activity.success,
                'fields_enriched': activity.fields_enriched,
                'created_at': activity.created_at.isoformat()
            }
            for activity in activities
        ]
