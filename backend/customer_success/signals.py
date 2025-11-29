"""
Customer Success Signals
"""

from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='customer_success.HealthScore')
def handle_health_score_change(sender, instance, created, **kwargs):
    """Handle health score changes"""
    if created and instance.status == 'critical':
        # Could trigger playbook, create alert, etc.
        pass


@receiver(post_save, sender='customer_success.RenewalOpportunity')
def handle_renewal_status_change(sender, instance, **kwargs):
    """Handle renewal status changes"""
    if instance.status == 'churned':
        # Update account, record churn, etc.
        account = instance.account
        account.is_active = False
        account.save()


@receiver(post_save, sender='customer_success.NPSSurvey')
def handle_nps_response(sender, instance, **kwargs):
    """Handle NPS survey responses"""
    if instance.score is not None and instance.classification == 'detractor':
        # Could trigger at-risk playbook, create task, etc.
        pass
