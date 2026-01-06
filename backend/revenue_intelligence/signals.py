"""
Revenue Intelligence Signals
Auto-update deal scores and snapshots
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone


@receiver(post_save, sender='opportunity_management.Opportunity')
def update_deal_velocity(sender, instance, created, **kwargs):
    """Track stage changes for deal velocity"""
    from .models import DealVelocity

    if not created and hasattr(instance, '_previous_stage'):
        if instance._previous_stage != instance.stage:
            # Calculate days in previous stage
            # This is simplified - in production you'd track this more precisely
            days_in_stage = 1  # Default

            # Get last velocity record
            last_record = DealVelocity.objects.filter(
                opportunity=instance
            ).order_by('-transition_date').first()

            if last_record:
                days_in_stage = (timezone.now() - last_record.transition_date).days

            DealVelocity.objects.create(
                opportunity=instance,
                from_stage=instance._previous_stage,
                to_stage=instance.stage,
                days_in_stage=days_in_stage,
                triggered_by=getattr(instance, '_modified_by', None)
            )


@receiver(pre_save, sender='opportunity_management.Opportunity')
def store_previous_stage(sender, instance, **kwargs):
    """Store previous stage before save"""
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            instance._previous_stage = old_instance.stage
        except sender.DoesNotExist:
            instance._previous_stage = None
    else:
        instance._previous_stage = None


@receiver(post_save, sender='opportunity_management.Opportunity')
def update_competitor_stats(sender, instance, **kwargs):
    """Update competitor win/loss stats when deal closes"""
    from .models import DealCompetitor

    if instance.stage in ['closed_won', 'closed_lost']:
        deal_competitors = DealCompetitor.objects.filter(
            opportunity=instance,
            status='active'
        )

        for dc in deal_competitors:
            if instance.stage == 'closed_won':
                dc.status = 'won'
                dc.competitor.deals_won_against += 1
            else:
                dc.status = 'lost'
                dc.competitor.deals_lost_to += 1

            dc.save()
            dc.competitor.save()
