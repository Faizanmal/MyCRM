"""
Gamification Signals
Handle gamification logic when certain events occur
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Achievement, UserAchievement


@receiver(post_save, sender='task_management.Task')
def check_task_completion_achievement(sender, instance, created, **kwargs):
    """Check for task completion achievements"""
    if not created and hasattr(instance, 'status') and instance.status == 'completed':
        if hasattr(instance, 'assigned_to') and instance.assigned_to:
            user = instance.assigned_to
            # Check for "Tasks Completed" achievement
            achievement = Achievement.objects.filter(
                criteria_type='tasks_completed',
                is_active=True
            ).first()

            if achievement:
                # Count completed tasks for this user
                completed_tasks = sender.objects.filter(
                    assigned_to=user,
                    status='completed'
                ).count()

                # Check if user has earned this achievement
                user_achievement, created = UserAchievement.objects.get_or_create(
                    user=user,
                    achievement=achievement,
                    defaults={'progress_value': completed_tasks}
                )

                if not created:
                    user_achievement.progress_value = completed_tasks
                    user_achievement.save()

                # Mark as completed if criteria met
                if user_achievement.progress_value >= achievement.criteria_value and not user_achievement.is_completed:
                    user_achievement.is_completed = True
                    user_achievement.save()


@receiver(post_save, sender='opportunity_management.Opportunity')
def check_deal_won_achievement(sender, instance, created, **kwargs):
    """Check for deals won achievements"""
    if not created and hasattr(instance, 'stage') and instance.stage == 'won':
        if hasattr(instance, 'owner') and instance.owner:
            user = instance.owner
            # Check for "Deals Won" achievement
            achievement = Achievement.objects.filter(
                criteria_type='deals_won',
                is_active=True
            ).first()

            if achievement:
                # Count won deals for this user
                won_deals = sender.objects.filter(
                    owner=user,
                    stage='won'
                ).count()

                # Check if user has earned this achievement
                user_achievement, created = UserAchievement.objects.get_or_create(
                    user=user,
                    achievement=achievement,
                    defaults={'progress_value': won_deals}
                )

                if not created:
                    user_achievement.progress_value = won_deals
                    user_achievement.save()

                # Mark as completed if criteria met
                if user_achievement.progress_value >= achievement.criteria_value and not user_achievement.is_completed:
                    user_achievement.is_completed = True
                    user_achievement.save()
