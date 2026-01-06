"""
Social Selling Service Layer
Business logic for social selling features
"""

import os
from datetime import timedelta

from django.conf import settings
from django.utils import timezone


class SocialSellingService:
    """Service for social selling operations"""

    def __init__(self):
        self.linkedin_client_id = os.environ.get('LINKEDIN_CLIENT_ID', '')
        self.linkedin_client_secret = os.environ.get('LINKEDIN_CLIENT_SECRET', '')
        self.openai_available = bool(os.environ.get('OPENAI_API_KEY'))

    def sync_profile(self, profile):
        """Sync profile data from social network"""
        # In production, this would use platform APIs
        # For now, return mock success

        profile.last_synced = timezone.now()
        profile.save()

        return True, "Profile synced successfully"

    def get_linkedin_auth_url(self, user):
        """Generate LinkedIn OAuth URL"""
        redirect_uri = f"{settings.SITE_URL}/api/social-selling/linkedin/callback/"
        scope = "r_liteprofile r_emailaddress w_member_social"

        return (
            f"https://www.linkedin.com/oauth/v2/authorization?"
            f"response_type=code&client_id={self.linkedin_client_id}"
            f"&redirect_uri={redirect_uri}&scope={scope}"
        )

    def handle_linkedin_callback(self, user, code):
        """Handle LinkedIn OAuth callback"""
        from .models import LinkedInIntegration

        # In production, exchange code for tokens
        # For now, mock the integration

        integration, _ = LinkedInIntegration.objects.get_or_create(user=user)
        integration.access_token = "mock_token"
        integration.token_expires_at = timezone.now() + timedelta(days=60)
        integration.is_active = True
        integration.save()

        return True, "LinkedIn connected successfully"

    def bulk_schedule_engagements(self, user, profile_ids, engagement_type,
                                   content='', use_ai_personalization=True,
                                   scheduled_for=None):
        """Bulk schedule engagements"""
        from .models import SocialEngagement, SocialProfile

        engagements = []
        profiles = SocialProfile.objects.filter(id__in=profile_ids)

        for profile in profiles:
            engagement_content = content
            ai_suggestion = ''

            if use_ai_personalization and self.openai_available:
                ai_suggestion = self._generate_personalized_content(
                    profile, engagement_type
                )
                engagement_content = ai_suggestion

            engagement = SocialEngagement.objects.create(
                user=user,
                profile=profile,
                engagement_type=engagement_type,
                content=engagement_content,
                ai_suggested=use_ai_personalization,
                ai_suggestion_text=ai_suggestion,
                scheduled_for=scheduled_for or timezone.now()
            )
            engagements.append(engagement)

        return engagements

    def execute_engagement(self, engagement):
        """Execute a scheduled engagement"""
        # In production, this would use platform APIs
        # For now, mark as completed

        engagement.status = 'completed'
        engagement.completed_at = timezone.now()
        engagement.save()

        # Update analytics
        self._update_analytics(engagement)

        return True, "Engagement completed"

    def _generate_personalized_content(self, profile, engagement_type):
        """Generate AI-personalized content"""
        if engagement_type == 'comment':
            return self._generate_comment(profile)
        elif engagement_type == 'connection_request':
            return self._generate_connection_request(profile)
        elif engagement_type == 'message':
            return self._generate_message(profile)
        return ''

    def _generate_comment(self, profile):
        """Generate personalized comment"""
        contact = profile.contact
        templates = [
            f"Great insights here! This aligns with what we're seeing at {contact.company or 'companies in your space'}.",
            "Couldn't agree more. What's your take on how this will evolve over the next year?",
            "This is valuable perspective. Have you seen this play out differently in specific industries?",
        ]
        import random
        return random.choice(templates)

    def _generate_connection_request(self, profile):
        """Generate connection request message"""
        contact = profile.contact
        name = contact.first_name or "there"

        templates = [
            f"Hi {name}, I came across your profile and was impressed by your work at {contact.company or 'your company'}. Would love to connect and learn more about your approach to {profile.job_title or 'your field'}.",
            f"Hi {name}, We share mutual interests in this space and I'd value having you in my network. Looking forward to connecting!",
            f"Hi {name}, Your recent post caught my attention. I'd love to connect and exchange ideas.",
        ]
        import random
        return random.choice(templates)

    def _generate_message(self, profile):
        """Generate personalized DM"""
        contact = profile.contact
        name = contact.first_name or "there"

        return f"Hi {name}, thanks for connecting! I noticed you're working on some interesting things at {contact.company or 'your company'}. Would love to hear more about what challenges you're facing right now."

    def _update_analytics(self, engagement):
        """Update engagement analytics"""
        from .models import EngagementAnalytics

        today = timezone.now().date()
        analytics, _ = EngagementAnalytics.objects.get_or_create(
            user=engagement.user,
            date=today
        )

        if engagement.engagement_type == 'like':
            analytics.posts_liked += 1
        elif engagement.engagement_type == 'comment':
            analytics.posts_commented += 1
        elif engagement.engagement_type == 'connection_request':
            analytics.connections_sent += 1
        elif engagement.engagement_type == 'message':
            analytics.messages_sent += 1

        analytics.save()

    def process_sequence_step(self, prospect_in_sequence):
        """Process the next step in a sequence for a prospect"""
        from .models import SocialEngagement, SocialSellingStep

        sequence = prospect_in_sequence.sequence
        current_step = prospect_in_sequence.current_step

        # Get next step
        try:
            step = sequence.steps.get(order=current_step)
        except SocialSellingStep.DoesNotExist:
            # Sequence completed
            prospect_in_sequence.status = 'completed'
            prospect_in_sequence.completed_at = timezone.now()
            prospect_in_sequence.save()
            return None

        # Create engagement for this step
        content = step.message_template
        if step.use_ai_personalization:
            content = self._generate_personalized_content(
                prospect_in_sequence.profile,
                step.action_type
            )

        engagement = SocialEngagement.objects.create(
            user=sequence.user,
            profile=prospect_in_sequence.profile,
            engagement_type=step.action_type,
            content=content,
            ai_suggested=step.use_ai_personalization,
            scheduled_for=timezone.now()
        )

        # Update prospect's position
        prospect_in_sequence.current_step += 1
        prospect_in_sequence.next_action_at = timezone.now() + timedelta(days=step.delay_days)
        prospect_in_sequence.save()

        return engagement

    def analyze_profile_for_insights(self, profile):
        """Analyze a profile for sales insights"""
        from .models import SocialInsight

        insights = []

        # Check for job change
        if self._detect_job_change(profile):
            insights.append(
                SocialInsight.objects.create(
                    profile=profile,
                    insight_type='job_change',
                    title=f"{profile.contact.first_name} may have changed jobs",
                    description=f"Recent activity suggests {profile.contact.full_name} may have a new role at {profile.company}.",
                    recommended_action="Reach out to congratulate and explore new opportunities",
                    suggested_message=f"Congratulations on the new role at {profile.company}! Would love to catch up and hear about your new challenges.",
                    urgency='high'
                )
            )

        # Check for buying signals
        recent_posts = profile.posts.order_by('-posted_at')[:10]
        for post in recent_posts:
            if self._is_buying_signal(post):
                insights.append(
                    SocialInsight.objects.create(
                        profile=profile,
                        insight_type='buying_signal',
                        title="Potential buying signal detected",
                        description=f"Post mentions challenges that align with our solution: {post.content[:200]}",
                        related_post=post,
                        recommended_action="Engage with the post and offer value",
                        urgency='high'
                    )
                )

        return insights

    def _detect_job_change(self, profile):
        """Detect if profile has changed jobs"""
        # Simple heuristic - in production, compare with stored data
        return False

    def _is_buying_signal(self, post):
        """Check if post contains buying signals"""
        buying_keywords = [
            'looking for', 'searching for', 'need help', 'recommendation',
            'evaluating', 'considering', 'pain point', 'challenge',
            'struggling with', 'anyone know', 'suggestions for'
        ]

        content_lower = post.content.lower()
        return any(keyword in content_lower for keyword in buying_keywords)
