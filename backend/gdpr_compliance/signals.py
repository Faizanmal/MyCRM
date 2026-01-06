from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserPrivacyPreference


@receiver(post_save, sender=User)
def create_privacy_preferences(sender, instance, created, **kwargs):
    """Create default privacy preferences for new users."""
    if created:
        UserPrivacyPreference.objects.get_or_create(
            user=instance,
            defaults={
                'allow_data_processing': True,
                'allow_marketing_emails': False,
                'allow_analytics': True,
                'allow_third_party_sharing': False,
                'allow_profiling': False,
            }
        )
