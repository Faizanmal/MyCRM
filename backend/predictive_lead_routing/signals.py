"""
Signals for Predictive Lead Routing
Handles automatic routing triggers and performance updates
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone


@receiver(post_save, sender='lead_management.Lead')
def auto_route_new_lead(sender, instance, created, **kwargs):
    """Automatically route new leads"""
    if created and not instance.assigned_to:
        from .services import LeadRoutingService
        
        try:
            service = LeadRoutingService()
            service.route_lead(instance)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to auto-route lead {instance.id}: {e}")


@receiver(post_save, sender='lead_management.Lead')
def update_rep_stats_on_conversion(sender, instance, created, **kwargs):
    """Update rep stats when lead converts"""
    if not created and instance.status == 'converted':
        from .models import SalesRepProfile, LeadAssignment
        from .services import RepPerformanceService
        
        # Find the assignment
        assignment = LeadAssignment.objects.filter(
            lead=instance,
            assigned_to=instance.assigned_to
        ).order_by('-assigned_at').first()
        
        if assignment:
            assignment.status = 'converted'
            assignment.outcome = 'converted'
            assignment.outcome_at = timezone.now()
            assignment.save(update_fields=['status', 'outcome', 'outcome_at'])
        
        # Update rep performance
        profile = SalesRepProfile.objects.filter(user=instance.assigned_to).first()
        if profile:
            service = RepPerformanceService()
            service.update_rep_performance(profile)


@receiver(pre_save, sender='lead_management.Lead')
def track_assignment_changes(sender, instance, **kwargs):
    """Track when lead assignment changes"""
    if instance.pk:
        try:
            original = sender.objects.get(pk=instance.pk)
            instance._original_assignee = original.assigned_to
        except sender.DoesNotExist:
            instance._original_assignee = None


@receiver(post_save, sender='lead_management.Lead')
def handle_assignment_change(sender, instance, created, **kwargs):
    """Handle lead assignment changes"""
    if not created and hasattr(instance, '_original_assignee'):
        if instance._original_assignee != instance.assigned_to:
            from .models import SalesRepProfile
            from django.db.models import F
            
            # Decrement old assignee count
            if instance._original_assignee:
                SalesRepProfile.objects.filter(
                    user=instance._original_assignee
                ).update(current_lead_count=F('current_lead_count') - 1)
            
            # Increment new assignee count
            if instance.assigned_to:
                SalesRepProfile.objects.filter(
                    user=instance.assigned_to
                ).update(current_lead_count=F('current_lead_count') + 1)
