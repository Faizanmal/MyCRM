"""
Email Notification Triggers
Automated email notifications for important CRM events
"""

import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


# ==================== Email Templates ====================

def get_email_template(template_name: str, context: dict) -> tuple:
    """
    Render email template and return HTML and plain text versions
    """
    try:
        html_content = render_to_string(f'emails/{template_name}.html', context)
        text_content = strip_tags(html_content)
        return html_content, text_content
    except Exception as e:
        logger.error(f"Failed to render email template {template_name}: {e}")
        # Fallback to simple text
        text_content = str(context.get('message', ''))
        return None, text_content


# ==================== Core Email Sending ====================

def send_crm_email(
    to_email: str,
    subject: str,
    template_name: str = None,
    context: dict = None,
    html_content: str = None,
    text_content: str = None,
    from_email: str = None,
):
    """
    Send an email with proper error handling and logging
    """
    from_email = from_email or settings.DEFAULT_FROM_EMAIL

    try:
        if template_name and context:
            html_content, text_content = get_email_template(template_name, context)

        if html_content:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content or strip_tags(html_content),
                from_email=from_email,
                to=[to_email] if isinstance(to_email, str) else to_email,
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        else:
            send_mail(
                subject=subject,
                message=text_content,
                from_email=from_email,
                recipient_list=[to_email] if isinstance(to_email, str) else to_email,
            )

        logger.info(f"Email sent successfully to {to_email}: {subject}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


# ==================== Notification Event Handlers ====================

class EmailNotificationService:
    """
    Service for sending various types of CRM email notifications
    """

    @staticmethod
    def send_deal_stage_change(user, opportunity, old_stage, new_stage):
        """
        Notify when a deal changes stage
        """
        subject = f"Deal Update: {opportunity.name} moved to {new_stage}"
        context = {
            'user_name': user.get_full_name() or user.username,
            'deal_name': opportunity.name,
            'old_stage': old_stage,
            'new_stage': new_stage,
            'deal_value': f"${opportunity.amount:,.2f}" if opportunity.amount else "N/A",
            'deal_url': f"{settings.FRONTEND_URL}/opportunities/{opportunity.id}",
            'action': 'view_deal',
        }

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2563eb;">🎯 Deal Stage Updated</h2>
            <p>Hi {context['user_name']},</p>
            <p>The deal <strong>{context['deal_name']}</strong> has moved from
               <span style="background: #fef3c7; padding: 2px 8px; border-radius: 4px;">{old_stage}</span>
               to
               <span style="background: #d1fae5; padding: 2px 8px; border-radius: 4px;">{new_stage}</span>
            </p>
            <p><strong>Deal Value:</strong> {context['deal_value']}</p>
            <p style="margin-top: 20px;">
                <a href="{context['deal_url']}"
                   style="background: #2563eb; color: white; padding: 12px 24px;
                          text-decoration: none; border-radius: 6px; display: inline-block;">
                    View Deal
                </a>
            </p>
        </div>
        """

        return send_crm_email(
            to_email=user.email,
            subject=subject,
            html_content=html_content,
            text_content=strip_tags(html_content),
        )

    @staticmethod
    def send_task_due_reminder(user, task, hours_until_due=24):
        """
        Remind user about upcoming task deadline
        """
        subject = f"⏰ Reminder: {task.title} due soon"

        due_text = "tomorrow" if hours_until_due <= 24 else f"in {hours_until_due} hours"

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #f59e0b;">⏰ Task Due {due_text.capitalize()}</h2>
            <p>Hi {user.get_full_name() or user.username},</p>
            <p>This is a reminder that the following task is due {due_text}:</p>
            <div style="background: #fef3c7; padding: 16px; border-radius: 8px; margin: 16px 0;">
                <h3 style="margin: 0 0 8px 0; color: #92400e;">{task.title}</h3>
                <p style="margin: 0; color: #78716c;">{task.description or 'No description'}</p>
                <p style="margin: 8px 0 0 0; font-size: 14px;">
                    <strong>Due:</strong> {task.due_date.strftime('%B %d, %Y at %I:%M %p')}
                </p>
            </div>
            <p style="margin-top: 20px;">
                <a href="{settings.FRONTEND_URL}/tasks/{task.id}"
                   style="background: #f59e0b; color: white; padding: 12px 24px;
                          text-decoration: none; border-radius: 6px; display: inline-block;">
                    View Task
                </a>
            </p>
        </div>
        """

        return send_crm_email(
            to_email=user.email,
            subject=subject,
            html_content=html_content,
            text_content=strip_tags(html_content),
        )

    @staticmethod
    def send_task_overdue_alert(user, task):
        """
        Alert user about overdue task
        """
        subject = f"🚨 Overdue: {task.title}"

        days_overdue = (timezone.now().date() - task.due_date.date()).days

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #dc2626;">🚨 Task Overdue</h2>
            <p>Hi {user.get_full_name() or user.username},</p>
            <p>The following task is now <strong style="color: #dc2626;">{days_overdue} day(s) overdue</strong>:</p>
            <div style="background: #fef2f2; padding: 16px; border-radius: 8px; margin: 16px 0; border-left: 4px solid #dc2626;">
                <h3 style="margin: 0 0 8px 0; color: #991b1b;">{task.title}</h3>
                <p style="margin: 0; color: #78716c;">{task.description or 'No description'}</p>
                <p style="margin: 8px 0 0 0; font-size: 14px;">
                    <strong>Was due:</strong> {task.due_date.strftime('%B %d, %Y')}
                </p>
            </div>
            <p style="margin-top: 20px;">
                <a href="{settings.FRONTEND_URL}/tasks/{task.id}"
                   style="background: #dc2626; color: white; padding: 12px 24px;
                          text-decoration: none; border-radius: 6px; display: inline-block;">
                    Complete Task Now
                </a>
            </p>
        </div>
        """

        return send_crm_email(
            to_email=user.email,
            subject=subject,
            html_content=html_content,
            text_content=strip_tags(html_content),
        )

    @staticmethod
    def send_mention_notification(mentioned_user, mentioner, context_type, context_object, comment_text):
        """
        Notify user when they are mentioned in a comment
        """
        subject = f"{mentioner.get_full_name() or mentioner.username} mentioned you"

        context_name = getattr(context_object, 'name', getattr(context_object, 'title', 'an item'))

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #3b82f6;">💬 You were mentioned</h2>
            <p>Hi {mentioned_user.get_full_name() or mentioned_user.username},</p>
            <p><strong>{mentioner.get_full_name() or mentioner.username}</strong> mentioned you in a comment on {context_type}: <strong>{context_name}</strong></p>
            <div style="background: #eff6ff; padding: 16px; border-radius: 8px; margin: 16px 0; border-left: 4px solid #3b82f6;">
                <p style="margin: 0; font-style: italic;">"{comment_text[:500]}{'...' if len(comment_text) > 500 else ''}"</p>
            </div>
            <p style="margin-top: 20px;">
                <a href="{settings.FRONTEND_URL}/{context_type}s/{context_object.id}"
                   style="background: #3b82f6; color: white; padding: 12px 24px;
                          text-decoration: none; border-radius: 6px; display: inline-block;">
                    View Comment
                </a>
            </p>
        </div>
        """

        return send_crm_email(
            to_email=mentioned_user.email,
            subject=subject,
            html_content=html_content,
            text_content=strip_tags(html_content),
        )

    @staticmethod
    def send_achievement_unlocked(user, achievement):
        """
        Celebrate user achievements
        """
        subject = f"🏆 Achievement Unlocked: {achievement.name}!"

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; text-align: center;">
            <div style="background: linear-gradient(135deg, #8b5cf6, #6366f1); padding: 40px; border-radius: 16px; color: white;">
                <div style="font-size: 64px; margin-bottom: 16px;">🏆</div>
                <h1 style="margin: 0 0 8px 0;">Achievement Unlocked!</h1>
                <h2 style="margin: 0; font-weight: normal; opacity: 0.9;">{achievement.name}</h2>
            </div>
            <div style="padding: 24px;">
                <p style="font-size: 18px; color: #4b5563;">{achievement.description}</p>
                <div style="background: #fef3c7; display: inline-block; padding: 8px 24px; border-radius: 20px; margin: 16px 0;">
                    <strong style="color: #92400e;">+{achievement.xp_reward} XP</strong>
                </div>
                <p style="margin-top: 24px;">
                    <a href="{settings.FRONTEND_URL}/gamification"
                       style="background: #8b5cf6; color: white; padding: 12px 24px;
                              text-decoration: none; border-radius: 6px; display: inline-block;">
                        View All Achievements
                    </a>
                </p>
            </div>
        </div>
        """

        return send_crm_email(
            to_email=user.email,
            subject=subject,
            html_content=html_content,
            text_content=strip_tags(html_content),
        )

    @staticmethod
    def send_ai_recommendation(user, recommendations):
        """
        Send AI-generated recommendations digest
        """
        subject = f"💡 {len(recommendations)} new AI insights for you"

        rec_html = ""
        for rec in recommendations[:5]:
            impact_color = {
                'high': '#dc2626',
                'medium': '#f59e0b',
                'low': '#22c55e'
            }.get(rec.impact, '#6b7280')

            rec_html += f"""
            <div style="background: #f9fafb; padding: 16px; border-radius: 8px; margin: 12px 0;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span style="background: {impact_color}; color: white; padding: 2px 8px;
                                 border-radius: 4px; font-size: 12px; text-transform: uppercase;">
                        {rec.impact} impact
                    </span>
                    <span style="font-weight: bold;">{rec.title}</span>
                </div>
                <p style="margin: 0; color: #4b5563;">{rec.description[:200]}{'...' if len(rec.description) > 200 else ''}</p>
            </div>
            """

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #8b5cf6;">💡 Your AI Insights</h2>
            <p>Hi {user.get_full_name() or user.username},</p>
            <p>Here are your latest AI-powered recommendations to help you close more deals:</p>
            {rec_html}
            <p style="margin-top: 24px;">
                <a href="{settings.FRONTEND_URL}/ai-insights"
                   style="background: #8b5cf6; color: white; padding: 12px 24px;
                          text-decoration: none; border-radius: 6px; display: inline-block;">
                    View All Insights
                </a>
            </p>
        </div>
        """

        return send_crm_email(
            to_email=user.email,
            subject=subject,
            html_content=html_content,
            text_content=strip_tags(html_content),
        )

    # ==================== Scheduling Emails ====================

    @staticmethod
    def send_meeting_confirmation(guest_email, guest_name, meeting, host):
        """
        Send meeting confirmation email to guest
        """
        subject = f"Meeting Confirmed: {meeting.meeting_type.name} with {host.get_full_name()}"

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #22c55e;">✅ Meeting Confirmed</h2>
            <p>Hi {guest_name},</p>
            <p>Your meeting has been successfully booked!</p>

            <div style="background: #f0fdf4; padding: 20px; border-radius: 12px; margin: 20px 0; border-left: 4px solid #22c55e;">
                <h3 style="margin: 0 0 12px 0; color: #166534;">{meeting.meeting_type.name}</h3>
                <p style="margin: 8px 0;"><strong>📅 Date:</strong> {meeting.start_time.strftime('%A, %B %d, %Y')}</p>
                <p style="margin: 8px 0;"><strong>🕐 Time:</strong> {meeting.start_time.strftime('%I:%M %p')} - {meeting.end_time.strftime('%I:%M %p')}</p>
                <p style="margin: 8px 0;"><strong>👤 With:</strong> {host.get_full_name()}</p>
                <p style="margin: 8px 0;"><strong>📍 Location:</strong> {meeting.location or 'To be provided'}</p>
            </div>

            <p>Need to make changes?</p>
            <p>
                <a href="{settings.FRONTEND_URL}/schedule/reschedule/{meeting.reschedule_token}"
                   style="background: #f59e0b; color: white; padding: 10px 20px;
                          text-decoration: none; border-radius: 6px; display: inline-block; margin-right: 10px;">
                    Reschedule
                </a>
                <a href="{settings.FRONTEND_URL}/schedule/cancel/{meeting.cancel_token}"
                   style="background: #dc2626; color: white; padding: 10px 20px;
                          text-decoration: none; border-radius: 6px; display: inline-block;">
                    Cancel
                </a>
            </p>
        </div>
        """

        return send_crm_email(
            to_email=guest_email,
            subject=subject,
            html_content=html_content,
            text_content=strip_tags(html_content),
        )

    @staticmethod
    def send_meeting_cancelled(guest_email, guest_name, meeting, host, reason=''):
        """
        Send meeting cancellation notification
        """
        subject = f"Meeting Cancelled: {meeting.meeting_type.name}"

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #dc2626;">❌ Meeting Cancelled</h2>
            <p>Hi {guest_name},</p>
            <p>Your meeting has been cancelled.</p>

            <div style="background: #fef2f2; padding: 20px; border-radius: 12px; margin: 20px 0; border-left: 4px solid #dc2626;">
                <h3 style="margin: 0 0 12px 0; color: #991b1b;">{meeting.meeting_type.name}</h3>
                <p style="margin: 8px 0;"><strong>Was scheduled for:</strong> {meeting.start_time.strftime('%A, %B %d, %Y at %I:%M %p')}</p>
                {f'<p style="margin: 8px 0;"><strong>Reason:</strong> {reason}</p>' if reason else ''}
            </div>

            <p>Would you like to reschedule?</p>
            <p>
                <a href="{settings.FRONTEND_URL}/schedule/{meeting.meeting_type.page.slug}"
                   style="background: #2563eb; color: white; padding: 12px 24px;
                          text-decoration: none; border-radius: 6px; display: inline-block;">
                    Book New Meeting
                </a>
            </p>
        </div>
        """

        return send_crm_email(
            to_email=guest_email,
            subject=subject,
            html_content=html_content,
            text_content=strip_tags(html_content),
        )

    @staticmethod
    def send_meeting_rescheduled(guest_email, guest_name, meeting, old_time, host):
        """
        Send meeting reschedule notification
        """
        subject = f"Meeting Rescheduled: {meeting.meeting_type.name}"

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #f59e0b;">🔄 Meeting Rescheduled</h2>
            <p>Hi {guest_name},</p>
            <p>Your meeting has been rescheduled to a new time.</p>

            <div style="background: #fef3c7; padding: 20px; border-radius: 12px; margin: 20px 0;">
                <p style="margin: 0 0 12px 0; color: #92400e; text-decoration: line-through;">
                    <strong>Previous:</strong> {old_time.strftime('%A, %B %d, %Y at %I:%M %p')}
                </p>
            </div>

            <div style="background: #f0fdf4; padding: 20px; border-radius: 12px; margin: 20px 0; border-left: 4px solid #22c55e;">
                <h3 style="margin: 0 0 12px 0; color: #166534;">New Time</h3>
                <p style="margin: 8px 0;"><strong>📅 Date:</strong> {meeting.start_time.strftime('%A, %B %d, %Y')}</p>
                <p style="margin: 8px 0;"><strong>🕐 Time:</strong> {meeting.start_time.strftime('%I:%M %p')} - {meeting.end_time.strftime('%I:%M %p')}</p>
            </div>

            <p>Need to make more changes?</p>
            <p>
                <a href="{settings.FRONTEND_URL}/schedule/reschedule/{meeting.reschedule_token}"
                   style="background: #f59e0b; color: white; padding: 10px 20px;
                          text-decoration: none; border-radius: 6px; display: inline-block; margin-right: 10px;">
                    Reschedule Again
                </a>
                <a href="{settings.FRONTEND_URL}/schedule/cancel/{meeting.cancel_token}"
                   style="background: #dc2626; color: white; padding: 10px 20px;
                          text-decoration: none; border-radius: 6px; display: inline-block;">
                    Cancel
                </a>
            </p>
        </div>
        """

        return send_crm_email(
            to_email=guest_email,
            subject=subject,
            html_content=html_content,
            text_content=strip_tags(html_content),
        )

    @staticmethod
    def send_meeting_reminder(guest_email, guest_name, meeting, host, minutes_until):
        """
        Send meeting reminder email
        """
        time_text = f"{minutes_until // 60} hour{'s' if minutes_until > 60 else ''}" if minutes_until >= 60 else f"{minutes_until} minutes"
        subject = f"⏰ Reminder: Meeting in {time_text}"

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #3b82f6;">⏰ Meeting Reminder</h2>
            <p>Hi {guest_name},</p>
            <p>This is a reminder that your meeting is coming up in <strong>{time_text}</strong>.</p>

            <div style="background: #eff6ff; padding: 20px; border-radius: 12px; margin: 20px 0; border-left: 4px solid #3b82f6;">
                <h3 style="margin: 0 0 12px 0; color: #1e40af;">{meeting.meeting_type.name}</h3>
                <p style="margin: 8px 0;"><strong>🕐 Time:</strong> {meeting.start_time.strftime('%I:%M %p')} - {meeting.end_time.strftime('%I:%M %p')}</p>
                <p style="margin: 8px 0;"><strong>👤 With:</strong> {host.get_full_name()}</p>
                <p style="margin: 8px 0;"><strong>📍 Location:</strong> {meeting.location or 'To be provided'}</p>
            </div>
        </div>
        """

        return send_crm_email(
            to_email=guest_email,
            subject=subject,
            html_content=html_content,
            text_content=strip_tags(html_content),
        )

    # ==================== Organization Invitation Emails ====================

    @staticmethod
    def send_organization_invitation(invitation):
        """
        Send organization invitation email
        """
        subject = f"You've been invited to join {invitation.organization.name}"

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2563eb;">🎉 You're Invited!</h2>
            <p>Hi,</p>
            <p><strong>{invitation.invited_by.get_full_name() or invitation.invited_by.username}</strong> has invited you to join <strong>{invitation.organization.name}</strong> on MyCRM.</p>

            <div style="background: #eff6ff; padding: 20px; border-radius: 12px; margin: 20px 0;">
                <p style="margin: 8px 0;"><strong>Organization:</strong> {invitation.organization.name}</p>
                <p style="margin: 8px 0;"><strong>Your Role:</strong> {invitation.role.title()}</p>
                <p style="margin: 8px 0;"><strong>Invited by:</strong> {invitation.invited_by.get_full_name() or invitation.invited_by.username}</p>
            </div>

            <p style="margin-top: 24px;">
                <a href="{settings.FRONTEND_URL}/invite/accept/{invitation.token}"
                   style="background: #22c55e; color: white; padding: 14px 28px;
                          text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
                    Accept Invitation
                </a>
            </p>

            <p style="margin-top: 20px; color: #6b7280; font-size: 14px;">
                This invitation expires on {invitation.expires_at.strftime('%B %d, %Y')}.
            </p>
        </div>
        """

        return send_crm_email(
            to_email=invitation.email,
            subject=subject,
            html_content=html_content,
            text_content=strip_tags(html_content),
        )

    # ==================== Voice Intelligence Notifications ====================

    @staticmethod
    def send_call_analysis_complete(user, call_recording):
        """
        Notify user when call analysis is complete
        """
        subject = f"📞 Call Analysis Complete: {call_recording.title}"

        # Get insights summary
        sentiment = call_recording.sentiment_analysis or {}
        action_items = call_recording.action_items or []

        action_items_html = ""
        for item in action_items[:5]:
            action_items_html += f"<li>{item.get('title', item)}</li>"

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #8b5cf6;">📞 Call Analysis Complete</h2>
            <p>Hi {user.get_full_name() or user.username},</p>
            <p>Your call recording has been analyzed and is ready for review.</p>

            <div style="background: #f5f3ff; padding: 20px; border-radius: 12px; margin: 20px 0;">
                <h3 style="margin: 0 0 12px 0; color: #6d28d9;">{call_recording.title}</h3>
                <p style="margin: 8px 0;"><strong>Duration:</strong> {call_recording.duration_minutes} minutes</p>
                <p style="margin: 8px 0;"><strong>Overall Sentiment:</strong> {sentiment.get('overall', 'Neutral').title()}</p>
            </div>

            {f'''
            <div style="margin: 20px 0;">
                <h4 style="color: #4b5563;">📋 Action Items Identified:</h4>
                <ul style="color: #4b5563;">
                    {action_items_html}
                </ul>
            </div>
            ''' if action_items else ''}

            <p style="margin-top: 24px;">
                <a href="{settings.FRONTEND_URL}/voice-intelligence/{call_recording.id}"
                   style="background: #8b5cf6; color: white; padding: 12px 24px;
                          text-decoration: none; border-radius: 6px; display: inline-block;">
                    View Full Analysis
                </a>
            </p>
        </div>
        """

        return send_crm_email(
            to_email=user.email,
            subject=subject,
            html_content=html_content,
            text_content=strip_tags(html_content),
        )

    @staticmethod
    def send_coaching_insights(user, coaching_data):
        """
        Send sales coaching insights from call analysis
        """
        subject = "🎯 Your Sales Coaching Insights"

        insights_html = ""
        for insight in coaching_data.get('insights', [])[:5]:
            insights_html += f"""
            <div style="background: #f9fafb; padding: 12px; border-radius: 8px; margin: 8px 0;">
                <p style="margin: 0;"><strong>{insight.get('area', '')}:</strong> {insight.get('feedback', '')}</p>
            </div>
            """

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #059669;">🎯 Sales Coaching Insights</h2>
            <p>Hi {user.get_full_name() or user.username},</p>
            <p>Based on your recent calls, here are some coaching insights to help you improve:</p>

            <div style="margin: 20px 0;">
                <div style="display: flex; gap: 16px; margin-bottom: 20px;">
                    <div style="background: #f0fdf4; padding: 16px; border-radius: 8px; flex: 1; text-align: center;">
                        <div style="font-size: 28px; font-weight: bold; color: #059669;">{coaching_data.get('talk_ratio', 50)}%</div>
                        <div style="color: #6b7280; font-size: 14px;">Talk Ratio</div>
                    </div>
                    <div style="background: #eff6ff; padding: 16px; border-radius: 8px; flex: 1; text-align: center;">
                        <div style="font-size: 28px; font-weight: bold; color: #2563eb;">{coaching_data.get('questions_asked', 0)}</div>
                        <div style="color: #6b7280; font-size: 14px;">Questions Asked</div>
                    </div>
                </div>

                {insights_html}
            </div>

            <p style="margin-top: 24px;">
                <a href="{settings.FRONTEND_URL}/voice-intelligence/coaching"
                   style="background: #059669; color: white; padding: 12px 24px;
                          text-decoration: none; border-radius: 6px; display: inline-block;">
                    View Coaching Dashboard
                </a>
            </p>
        </div>
        """

        return send_crm_email(
            to_email=user.email,
            subject=subject,
            html_content=html_content,
            text_content=strip_tags(html_content),
        )

    @staticmethod
    def send_weekly_digest(user, stats):
        """
        Send weekly performance digest
        """
        subject = "📊 Your Weekly CRM Digest"

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2563eb;">📊 Your Weekly Summary</h2>
            <p>Hi {user.get_full_name() or user.username},</p>
            <p>Here's how you performed this week:</p>

            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin: 24px 0;">
                <div style="background: #eff6ff; padding: 20px; border-radius: 12px; text-align: center;">
                    <div style="font-size: 32px; font-weight: bold; color: #2563eb;">{stats.get('deals_won', 0)}</div>
                    <div style="color: #4b5563;">Deals Won</div>
                </div>
                <div style="background: #f0fdf4; padding: 20px; border-radius: 12px; text-align: center;">
                    <div style="font-size: 32px; font-weight: bold; color: #22c55e;">${stats.get('revenue', 0):,.0f}</div>
                    <div style="color: #4b5563;">Revenue</div>
                </div>
                <div style="background: #fef3c7; padding: 20px; border-radius: 12px; text-align: center;">
                    <div style="font-size: 32px; font-weight: bold; color: #f59e0b;">{stats.get('tasks_completed', 0)}</div>
                    <div style="color: #4b5563;">Tasks Done</div>
                </div>
                <div style="background: #fce7f3; padding: 20px; border-radius: 12px; text-align: center;">
                    <div style="font-size: 32px; font-weight: bold; color: #ec4899;">{stats.get('xp_earned', 0)}</div>
                    <div style="color: #4b5563;">XP Earned</div>
                </div>
            </div>

            <p style="margin-top: 24px;">
                <a href="{settings.FRONTEND_URL}/dashboard"
                   style="background: #2563eb; color: white; padding: 12px 24px;
                          text-decoration: none; border-radius: 6px; display: inline-block;">
                    View Full Dashboard
                </a>
            </p>
        </div>
        """

        return send_crm_email(
            to_email=user.email,
            subject=subject,
            html_content=html_content,
            text_content=strip_tags(html_content),
        )


# ==================== Celery Tasks for Async Email Sending ====================

@shared_task
def send_deal_stage_change_email(user_id, opportunity_id, old_stage, new_stage):
    """Async task to send deal stage change email"""
    try:
        from django.contrib.auth import get_user_model

        from opportunity_management.models import Opportunity

        User = get_user_model()
        user = User.objects.get(id=user_id)
        opportunity = Opportunity.objects.get(id=opportunity_id)

        EmailNotificationService.send_deal_stage_change(user, opportunity, old_stage, new_stage)
    except Exception as e:
        logger.error(f"Failed to send deal stage email: {e}")


@shared_task
def send_task_reminder_email(user_id, task_id, hours_until_due):
    """Async task to send task reminder email"""
    try:
        from django.contrib.auth import get_user_model

        from task_management.models import Task

        User = get_user_model()
        user = User.objects.get(id=user_id)
        task = Task.objects.get(id=task_id)

        EmailNotificationService.send_task_due_reminder(user, task, hours_until_due)
    except Exception as e:
        logger.error(f"Failed to send task reminder email: {e}")


@shared_task
def send_overdue_task_emails():
    """Daily task to send overdue task alerts"""
    try:
        from task_management.models import Task

        overdue_tasks = Task.objects.filter(
            status__in=['pending', 'in_progress'],
            due_date__lt=timezone.now()
        ).select_related('assigned_to')

        for task in overdue_tasks:
            if task.assigned_to and task.assigned_to.email:
                EmailNotificationService.send_task_overdue_alert(task.assigned_to, task)

    except Exception as e:
        logger.error(f"Failed to send overdue task emails: {e}")


@shared_task
def send_weekly_digest_emails():
    """Weekly task to send digest emails to all users"""
    try:
        from django.contrib.auth import get_user_model

        from opportunity_management.models import Opportunity
        from task_management.models import Task

        User = get_user_model()

        last_week = timezone.now() - timezone.timedelta(days=7)

        for user in User.objects.filter(is_active=True):
            stats = {
                'deals_won': Opportunity.objects.filter(
                    owner=user,
                    status='won',
                    closed_at__gte=last_week
                ).count(),
                'revenue': Opportunity.objects.filter(
                    owner=user,
                    status='won',
                    closed_at__gte=last_week
                ).aggregate(total=Sum('amount'))['total'] or 0,
                'tasks_completed': Task.objects.filter(
                    assigned_to=user,
                    status='completed',
                    completed_at__gte=last_week
                ).count(),
                'xp_earned': 0,  # Would come from gamification
            }

            # Only send if there's activity
            if any(stats.values()):
                EmailNotificationService.send_weekly_digest(user, stats)

    except Exception as e:
        logger.error(f"Failed to send weekly digest emails: {e}")


@shared_task
def send_ai_recommendation_digest():
    """Daily task to send AI recommendation digests"""
    try:
        from django.contrib.auth import get_user_model

        from .interactive_models import AIRecommendation

        User = get_user_model()

        for user in User.objects.filter(is_active=True):
            # Get unseen high-impact recommendations
            recommendations = AIRecommendation.objects.filter(
                user=user,
                status='active',
                impact__in=['high', 'medium']
            ).order_by('-created_at')[:5]

            if recommendations.exists():
                EmailNotificationService.send_ai_recommendation(user, list(recommendations))

    except Exception as e:
        logger.error(f"Failed to send AI recommendation digest: {e}")
