"""
Internationalization (i18n) Services
Translation, currency conversion, and localization utilities
"""

import logging
from datetime import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from .i18n_models import (
    ContentLocalization,
    Currency,
    ExchangeRateHistory,
    Language,
    Locale,
    Timezone,
    Translation,
    TranslationKey,
    UserLocalePreference,
)

logger = logging.getLogger(__name__)
User = get_user_model()


class TranslationService:
    """Service for managing translations"""

    CACHE_PREFIX = 'i18n:translations'
    CACHE_TTL = 3600  # 1 hour

    def get_translations(
        self,
        language_code: str,
        namespace: str = None,
        include_fallback: bool = True
    ) -> dict[str, str]:
        """Get translations for a language"""

        cache_key = f"{self.CACHE_PREFIX}:{language_code}:{namespace or 'all'}"
        cached = cache.get(cache_key)

        if cached:
            return cached

        # Get language
        try:
            language = Language.objects.get(code=language_code, is_active=True)
        except Language.DoesNotExist:
            if include_fallback:
                language = Language.objects.filter(is_default=True).first()
            else:
                return {}

        if not language:
            return {}

        # Build query
        query = Translation.objects.filter(
            language=language,
            status='published'
        ).select_related('key')

        if namespace:
            query = query.filter(key__namespace=namespace)

        translations = {t.key.key: t.value for t in query}

        # Include fallback for missing keys
        if include_fallback and not language.is_default:
            default_lang = Language.objects.filter(is_default=True).first()
            if default_lang:
                default_translations = Translation.objects.filter(
                    language=default_lang,
                    status='published'
                ).select_related('key')

                if namespace:
                    default_translations = default_translations.filter(key__namespace=namespace)

                for t in default_translations:
                    if t.key.key not in translations:
                        translations[t.key.key] = t.value

        cache.set(cache_key, translations, self.CACHE_TTL)
        return translations

    def translate(
        self,
        key: str,
        language_code: str,
        default: str = None,
        **interpolations
    ) -> str:
        """Get a single translation with interpolation support"""

        translations = self.get_translations(language_code)
        value = translations.get(key, default or key)

        # Simple interpolation: {variable_name}
        for var, replacement in interpolations.items():
            value = value.replace(f'{{{var}}}', str(replacement))

        return value

    @transaction.atomic
    def upsert_translation(
        self,
        key: str,
        language_code: str,
        value: str,
        translator_user=None,
        is_machine_translated: bool = False,
        confidence_score: float = None
    ) -> dict:
        """Create or update a translation"""

        language = Language.objects.get(code=language_code)
        translation_key, _ = TranslationKey.objects.get_or_create(
            key=key,
            defaults={
                'namespace': key.split('.')[0] if '.' in key else 'common',
                'default_value': value
            }
        )

        translation, created = Translation.objects.update_or_create(
            key=translation_key,
            language=language,
            defaults={
                'value': value,
                'is_machine_translated': is_machine_translated,
                'confidence_score': confidence_score,
                'translated_by': translator_user,
                'status': 'draft' if is_machine_translated else 'needs_review'
            }
        )

        # Invalidate cache
        self._invalidate_cache(language_code)

        return {
            'translation_id': str(translation.id),
            'key': key,
            'language': language_code,
            'created': created
        }

    def _invalidate_cache(self, language_code: str):
        """Invalidate translation cache"""

        # In production, use cache pattern deletion
        cache.delete_pattern(f"{self.CACHE_PREFIX}:{language_code}:*")

    def get_translation_coverage(self, language_code: str) -> dict:
        """Get translation coverage statistics"""

        language = Language.objects.get(code=language_code)

        total_keys = TranslationKey.objects.filter(is_active=True).count()
        translated = Translation.objects.filter(
            language=language,
            status__in=['approved', 'published']
        ).count()

        coverage = (translated / total_keys * 100) if total_keys else 0

        # By namespace
        by_namespace = {}
        namespaces = TranslationKey.objects.values_list(
            'namespace', flat=True
        ).distinct()

        for ns in namespaces:
            ns_total = TranslationKey.objects.filter(
                namespace=ns, is_active=True
            ).count()
            ns_translated = Translation.objects.filter(
                language=language,
                key__namespace=ns,
                status__in=['approved', 'published']
            ).count()

            by_namespace[ns] = {
                'total': ns_total,
                'translated': ns_translated,
                'coverage': (ns_translated / ns_total * 100) if ns_total else 0
            }

        return {
            'language': language_code,
            'total_keys': total_keys,
            'translated': translated,
            'coverage': round(coverage, 1),
            'by_namespace': by_namespace
        }

    @transaction.atomic
    def bulk_import(
        self,
        language_code: str,
        translations: dict[str, str],
        namespace: str = None,
        auto_approve: bool = False
    ) -> dict:
        """Bulk import translations"""

        language = Language.objects.get(code=language_code)

        created_count = 0
        updated_count = 0

        for key, value in translations.items():
            # Determine namespace
            ns = namespace if namespace else key.split('.')[0] if '.' in key else 'common'

            translation_key, key_created = TranslationKey.objects.get_or_create(
                key=key,
                defaults={
                    'namespace': ns,
                    'default_value': value
                }
            )

            translation, created = Translation.objects.update_or_create(
                key=translation_key,
                language=language,
                defaults={
                    'value': value,
                    'status': 'approved' if auto_approve else 'needs_review'
                }
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        # Invalidate cache
        self._invalidate_cache(language_code)

        # Update language coverage
        coverage = self.get_translation_coverage(language_code)
        language.translation_coverage = coverage['coverage']
        language.save(update_fields=['translation_coverage'])

        return {
            'language': language_code,
            'created': created_count,
            'updated': updated_count,
            'total': created_count + updated_count
        }


class CurrencyService:
    """Service for currency conversion and formatting"""

    def __init__(self):
        self.exchange_rate_api = None  # Configure in production

    def convert(
        self,
        amount: Decimal,
        from_currency: str,
        to_currency: str,
        rate_date: datetime = None
    ) -> dict:
        """Convert amount between currencies"""

        if from_currency == to_currency:
            return {
                'original': float(amount),
                'converted': float(amount),
                'from_currency': from_currency,
                'to_currency': to_currency,
                'rate': 1.0
            }

        from_curr = Currency.objects.get(code=from_currency)
        to_curr = Currency.objects.get(code=to_currency)

        # Get rates (relative to base currency)
        from_rate = float(from_curr.exchange_rate)
        to_rate = float(to_curr.exchange_rate)

        # Convert: amount / from_rate * to_rate
        conversion_rate = to_rate / from_rate
        converted = float(amount) * conversion_rate

        return {
            'original': float(amount),
            'converted': round(converted, to_curr.decimal_places),
            'from_currency': from_currency,
            'to_currency': to_currency,
            'rate': round(conversion_rate, 6)
        }

    def format_currency(
        self,
        amount: Decimal,
        currency_code: str,
        include_symbol: bool = True
    ) -> str:
        """Format amount according to currency rules"""

        try:
            currency = Currency.objects.get(code=currency_code)
        except Currency.DoesNotExist:
            return str(amount)

        # Format number
        abs_amount = abs(float(amount))
        formatted = f"{abs_amount:,.{currency.decimal_places}f}"

        # Apply separators
        formatted = formatted.replace(',', 'THOUSANDS')
        formatted = formatted.replace('.', currency.decimal_separator)
        formatted = formatted.replace('THOUSANDS', currency.thousands_separator)

        # Add symbol
        if include_symbol:
            if currency.symbol_position == 'before':
                formatted = f"{currency.symbol}{formatted}"
            else:
                formatted = f"{formatted}{currency.symbol}"

        # Handle negative
        if amount < 0:
            formatted = f"-{formatted}"

        return formatted

    @transaction.atomic
    def update_exchange_rates(self, rates: dict[str, float], source: str) -> dict:
        """Update exchange rates from external source"""

        updated = []
        now = timezone.now()

        for code, rate in rates.items():
            try:
                currency = Currency.objects.get(code=code)

                # Store history
                ExchangeRateHistory.objects.create(
                    currency=currency,
                    rate=Decimal(str(rate)),
                    source=source,
                    recorded_at=now
                )

                # Update current rate
                currency.exchange_rate = Decimal(str(rate))
                currency.exchange_rate_updated_at = now
                currency.save(update_fields=['exchange_rate', 'exchange_rate_updated_at'])

                updated.append(code)
            except Currency.DoesNotExist:
                logger.warning(f"Currency {code} not found")

        return {
            'updated': updated,
            'count': len(updated),
            'source': source,
            'timestamp': now.isoformat()
        }

    def get_rate_history(
        self,
        currency_code: str,
        days: int = 30
    ) -> list[dict]:
        """Get exchange rate history"""

        currency = Currency.objects.get(code=currency_code)
        cutoff = timezone.now() - timezone.timedelta(days=days)

        history = ExchangeRateHistory.objects.filter(
            currency=currency,
            recorded_at__gte=cutoff
        ).order_by('recorded_at')

        return [
            {
                'date': h.recorded_at.date().isoformat(),
                'rate': float(h.rate),
                'source': h.source
            }
            for h in history
        ]


class LocaleService:
    """Service for user locale management"""

    def get_user_locale(self, user) -> dict:
        """Get user's locale settings"""

        try:
            pref = UserLocalePreference.objects.select_related(
                'language', 'currency', 'timezone', 'locale'
            ).get(user=user)

            return {
                'language': pref.language.code if pref.language else None,
                'language_name': pref.language.name if pref.language else None,
                'currency': pref.currency.code if pref.currency else None,
                'currency_symbol': pref.currency.symbol if pref.currency else None,
                'timezone': pref.timezone.name if pref.timezone else None,
                'timezone_offset': pref.timezone.offset if pref.timezone else None,
                'locale': pref.locale.code if pref.locale else None,
                'date_format': pref.date_format_override or (pref.locale.date_format if pref.locale else 'MM/DD/YYYY'),
                'time_format': pref.time_format_override or (pref.locale.time_format if pref.locale else 'HH:mm:ss'),
                'first_day_of_week': pref.first_day_of_week_override if pref.first_day_of_week_override is not None else (pref.locale.first_day_of_week if pref.locale else 0),
                'is_rtl': pref.language.is_rtl if pref.language else False,
            }
        except UserLocalePreference.DoesNotExist:
            # Return defaults
            default_locale = Locale.objects.filter(is_active=True).first()

            return {
                'language': default_locale.language.code if default_locale else 'en-US',
                'currency': default_locale.currency.code if default_locale else 'USD',
                'timezone': default_locale.timezone.name if default_locale else 'UTC',
                'locale': default_locale.code if default_locale else 'en-US',
                'date_format': default_locale.date_format if default_locale else 'MM/DD/YYYY',
                'time_format': default_locale.time_format if default_locale else 'HH:mm:ss',
                'first_day_of_week': default_locale.first_day_of_week if default_locale else 0,
                'is_rtl': False,
            }

    @transaction.atomic
    def update_user_locale(
        self,
        user,
        language_code: str = None,
        currency_code: str = None,
        timezone_name: str = None,
        date_format: str = None,
        time_format: str = None,
        first_day_of_week: int = None
    ) -> dict:
        """Update user locale preferences"""

        pref, _ = UserLocalePreference.objects.get_or_create(user=user)

        if language_code:
            pref.language = Language.objects.get(code=language_code)

        if currency_code:
            pref.currency = Currency.objects.get(code=currency_code)

        if timezone_name:
            pref.timezone = Timezone.objects.get(name=timezone_name)

        if date_format:
            pref.date_format_override = date_format

        if time_format:
            pref.time_format_override = time_format

        if first_day_of_week is not None:
            pref.first_day_of_week_override = first_day_of_week

        pref.save()

        return self.get_user_locale(user)

    def detect_timezone(self, timezone_name: str, user=None) -> dict:
        """Handle timezone auto-detection"""

        try:
            tz = Timezone.objects.get(name=timezone_name, is_active=True)

            if user:
                pref, _ = UserLocalePreference.objects.get_or_create(user=user)
                if pref.auto_detect_timezone:
                    pref.timezone = tz
                    pref.last_detected_timezone = timezone_name
                    pref.save()

            return {
                'detected': True,
                'timezone': timezone_name,
                'display_name': tz.display_name,
                'offset': tz.offset
            }
        except Timezone.DoesNotExist:
            return {
                'detected': False,
                'timezone': timezone_name,
                'error': 'Timezone not recognized'
            }


class ContentLocalizationService:
    """Service for localizing dynamic content"""

    def get_localized_content(
        self,
        content_type: str,
        content_id: str,
        language_code: str,
        fields: list[str] = None
    ) -> dict:
        """Get localized content for an entity"""

        try:
            language = Language.objects.get(code=language_code)
        except Language.DoesNotExist:
            return {}

        query = ContentLocalization.objects.filter(
            content_type=content_type,
            content_id=content_id,
            language=language,
            is_approved=True
        )

        if fields:
            query = query.filter(field_name__in=fields)

        return {loc.field_name: loc.value for loc in query}

    @transaction.atomic
    def set_localized_content(
        self,
        content_type: str,
        content_id: str,
        language_code: str,
        localizations: dict[str, str],
        auto_approve: bool = False
    ) -> dict:
        """Set localized content for an entity"""

        language = Language.objects.get(code=language_code)

        created = []
        updated = []

        for field_name, value in localizations.items():
            loc, is_created = ContentLocalization.objects.update_or_create(
                content_type=content_type,
                content_id=content_id,
                field_name=field_name,
                language=language,
                defaults={
                    'value': value,
                    'is_approved': auto_approve
                }
            )

            if is_created:
                created.append(field_name)
            else:
                updated.append(field_name)

        return {
            'content_type': content_type,
            'content_id': content_id,
            'language': language_code,
            'created': created,
            'updated': updated
        }


class MachineTranslationService:
    """Service for AI-powered translations"""

    def __init__(self):
        self.provider = None  # Configure in production (Google, AWS, etc.)

    async def translate_text(
        self,
        text: str,
        source_language: str,
        target_language: str
    ) -> dict:
        """Translate text using ML"""

        # In production, call translation API
        # For demo, return placeholder

        return {
            'source_text': text,
            'translated_text': f"[MT:{target_language}] {text}",
            'source_language': source_language,
            'target_language': target_language,
            'confidence': 0.85,
            'provider': 'demo'
        }

    async def translate_batch(
        self,
        texts: list[dict],
        source_language: str,
        target_language: str
    ) -> list[dict]:
        """Batch translate multiple texts"""

        results = []
        for item in texts:
            result = await self.translate_text(
                item['text'],
                source_language,
                target_language
            )
            result['key'] = item.get('key')
            results.append(result)

        return results

    @transaction.atomic
    async def auto_translate_missing(
        self,
        target_language_code: str,
        namespace: str = None,
        save_as_draft: bool = True
    ) -> dict:
        """Auto-translate missing translations"""

        translation_service = TranslationService()

        target_lang = Language.objects.get(code=target_language_code)
        source_lang = Language.objects.filter(is_default=True).first()

        if not source_lang:
            return {'error': 'No default language configured'}

        # Find missing translations
        existing_keys = Translation.objects.filter(
            language=target_lang
        ).values_list('key_id', flat=True)

        missing_keys = TranslationKey.objects.filter(
            is_active=True
        ).exclude(id__in=existing_keys)

        if namespace:
            missing_keys = missing_keys.filter(namespace=namespace)

        # Translate each
        translated_count = 0
        for key in missing_keys[:100]:  # Limit batch size
            # Get source translation
            source_trans = Translation.objects.filter(
                key=key,
                language=source_lang,
                status='published'
            ).first()

            if source_trans:
                result = await self.translate_text(
                    source_trans.value,
                    source_lang.code,
                    target_language_code
                )

                translation_service.upsert_translation(
                    key.key,
                    target_language_code,
                    result['translated_text'],
                    is_machine_translated=True,
                    confidence_score=result['confidence']
                )
                translated_count += 1

        return {
            'target_language': target_language_code,
            'translated': translated_count,
            'remaining': missing_keys.count() - translated_count
        }
