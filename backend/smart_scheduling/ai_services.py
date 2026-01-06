"""
Smart Scheduling AI Services
Core service layer for AI-enhanced scheduling features
"""

import logging
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from .ai_time_finder import AITimeFinder, NoShowPredictor
from .meeting_prep_ai import MeetingPrepGenerator, SmartReminderOptimizer

logger = logging.getLogger(__name__)
User = get_user_model()


class AISchedulingService:
    """Main service for AI-enhanced scheduling operations"""

    def __init__(self, user):
        self.user = user

    @transaction.atomic
    def find_optimal_times(
        self,
        meeting_type_id: str,
        duration_minutes: int,
        date_range_days: int = 14,
        participant_email: str | None = None,
        num_suggestions: int = 5
    ) -> list[dict]:
        """Find optimal meeting times using AI"""
        from .ai_models import AITimeSuggestion
        from .models import MeetingType

        try:
            meeting_type = MeetingType.objects.get(id=meeting_type_id)
        except MeetingType.DoesNotExist:
            raise ValueError(f"Meeting type {meeting_type_id} not found")

        # Calculate date range
        start_date = timezone.now()
        end_date = start_date + timedelta(days=date_range_days)

        # Use AI Time Finder
        finder = AITimeFinder(self.user)
        suggestions = finder.find_optimal_times(
            meeting_type=meeting_type,
            duration_minutes=duration_minutes,
            date_range_start=start_date,
            date_range_end=end_date,
            participant_email=participant_email,
            num_suggestions=num_suggestions
        )

        # Save suggestions to database
        saved_suggestions = []
        for suggestion in suggestions:
            ai_suggestion = AITimeSuggestion.objects.create(
                user=self.user,
                meeting_type=meeting_type,
                suggestion_type='optimal',
                suggested_start=suggestion.start,
                suggested_end=suggestion.end,
                overall_score=suggestion.overall_score,
                preference_score=suggestion.preference_score,
                availability_score=suggestion.availability_score,
                energy_score=suggestion.energy_score,
                context_switch_score=suggestion.context_switch_score,
                reasoning="; ".join(suggestion.reasons),
                factors={'reasons': suggestion.reasons},
                participant_email=participant_email or '',
                expires_at=timezone.now() + timedelta(days=7)
            )
            saved_suggestions.append({
                'id': str(ai_suggestion.id),
                'start': suggestion.start.isoformat(),
                'end': suggestion.end.isoformat(),
                'overall_score': suggestion.overall_score,
                'scores': {
                    'preference': suggestion.preference_score,
                    'availability': suggestion.availability_score,
                    'energy': suggestion.energy_score,
                    'context_switch': suggestion.context_switch_score
                },
                'reasons': suggestion.reasons
            })

        return saved_suggestions

    @transaction.atomic
    def predict_no_show(self, meeting_id: str) -> dict:
        """Predict no-show probability for a meeting"""
        from .ai_models import NoShowPrediction
        from .models import Meeting

        try:
            meeting = Meeting.objects.get(id=meeting_id)
        except Meeting.DoesNotExist:
            raise ValueError(f"Meeting {meeting_id} not found")

        # Run prediction
        predictor = NoShowPredictor()
        prediction_data = predictor.predict(meeting)

        # Save or update prediction
        prediction, created = NoShowPrediction.objects.update_or_create(
            meeting=meeting,
            defaults={
                'no_show_probability': prediction_data['no_show_probability'],
                'risk_score': prediction_data['risk_score'],
                'risk_factors': prediction_data['risk_factors'],
                'recommended_actions': prediction_data['recommended_actions'],
                'extra_reminder_suggested': prediction_data['extra_reminder_suggested'],
                'confirmation_call_suggested': prediction_data['confirmation_call_suggested'],
                'days_until_meeting': (meeting.start_time - timezone.now()).days,
                'meeting_time_of_day': self._get_time_of_day(meeting.start_time.hour),
                'day_of_week': meeting.start_time.weekday()
            }
        )

        return {
            'id': str(prediction.id),
            'meeting_id': str(meeting.id),
            'no_show_probability': prediction.no_show_probability,
            'risk_score': prediction.risk_score,
            'risk_factors': prediction.risk_factors,
            'recommended_actions': prediction.recommended_actions,
            'extra_reminder_suggested': prediction.extra_reminder_suggested,
            'confirmation_call_suggested': prediction.confirmation_call_suggested
        }

    def _get_time_of_day(self, hour: int) -> str:
        """Get time of day category"""
        if hour < 9:
            return 'early_morning'
        elif hour < 12:
            return 'morning'
        elif hour < 14:
            return 'lunch'
        elif hour < 17:
            return 'afternoon'
        else:
            return 'evening'

    @transaction.atomic
    def generate_meeting_prep(self, meeting_id: str) -> dict:
        """Generate AI meeting preparation materials"""
        from .ai_models import MeetingPrepAI
        from .models import Meeting

        try:
            meeting = Meeting.objects.get(id=meeting_id)
        except Meeting.DoesNotExist:
            raise ValueError(f"Meeting {meeting_id} not found")

        # Generate prep materials
        generator = MeetingPrepGenerator(meeting)
        prep_data = generator.generate_prep_materials()

        # Save to database
        prep, created = MeetingPrepAI.objects.update_or_create(
            meeting=meeting,
            defaults={
                'participant_summary': prep_data['participant_summary'],
                'company_info': prep_data['company_info'],
                'crm_contact_summary': prep_data['crm_context'].get('contact_summary', ''),
                'previous_interactions': prep_data['crm_context'].get('previous_interactions', []),
                'open_opportunities': prep_data['crm_context'].get('open_opportunities', []),
                'pending_tasks': prep_data['crm_context'].get('pending_tasks', []),
                'meeting_history_with_contact': prep_data['meeting_history'].get('meetings_list', []),
                'last_meeting_summary': prep_data['meeting_history'].get('last_meeting', {}).get('notes', '') if prep_data['meeting_history'].get('last_meeting') else '',
                'suggested_agenda': prep_data['suggested_agenda'],
                'talking_points': prep_data['talking_points'],
                'questions_to_ask': prep_data['questions_to_ask'],
                'potential_objections': prep_data['potential_objections'],
                'personalization_tips': prep_data['personalization_tips'],
                'ice_breakers': prep_data['ice_breakers'],
                'deal_stage': prep_data['deal_context'].get('stage', ''),
                'deal_value': prep_data['deal_context'].get('value') or None,
                'win_probability': prep_data['deal_context'].get('probability'),
                'recommended_next_steps': prep_data['recommended_next_steps']
            }
        )

        return {
            'id': str(prep.id),
            'meeting_id': str(meeting.id),
            **prep_data
        }

    @transaction.atomic
    def setup_smart_reminders(self, meeting_id: str) -> list[dict]:
        """Setup AI-optimized reminders for a meeting"""
        from .ai_models import SmartReminder
        from .models import Meeting

        try:
            meeting = Meeting.objects.get(id=meeting_id)
        except Meeting.DoesNotExist:
            raise ValueError(f"Meeting {meeting_id} not found")

        # Get optimal reminders
        optimizer = SmartReminderOptimizer(meeting)
        optimal_reminders = optimizer.get_optimal_reminders()

        # Delete existing smart reminders
        SmartReminder.objects.filter(meeting=meeting).delete()

        # Create new reminders
        created_reminders = []
        for reminder_data in optimal_reminders:
            scheduled_at = datetime.fromisoformat(reminder_data['scheduled_at'])

            reminder = SmartReminder.objects.create(
                meeting=meeting,
                scheduled_at=scheduled_at,
                minutes_before=reminder_data['minutes_before'],
                is_ai_optimized=True,
                optimization_reason=reminder_data['optimization_reason'],
                optimal_channel=reminder_data['channel'],
                subject=f"Reminder: {meeting.meeting_type.name} with {meeting.host.get_full_name()}",
                message=self._generate_reminder_message(meeting, reminder_data['minutes_before']),
                include_prep_material=reminder_data.get('include_prep_material', False),
                include_agenda=reminder_data.get('include_agenda', True),
                recipient_type='guest',
                recipient_email=meeting.guest_email
            )

            created_reminders.append({
                'id': str(reminder.id),
                'scheduled_at': reminder.scheduled_at.isoformat(),
                'minutes_before': reminder.minutes_before,
                'channel': reminder.optimal_channel,
                'optimization_reason': reminder.optimization_reason
            })

        return created_reminders

    def _generate_reminder_message(self, meeting, minutes_before: int) -> str:
        """Generate reminder message content"""

        if minutes_before >= 1440:
            time_str = f"{minutes_before // 1440} day(s)"
        elif minutes_before >= 60:
            time_str = f"{minutes_before // 60} hour(s)"
        else:
            time_str = f"{minutes_before} minutes"

        message = f"""Hi {meeting.guest_name},

This is a friendly reminder that you have a meeting scheduled in {time_str}.

Meeting Details:
- Type: {meeting.meeting_type.name}
- Date: {meeting.start_time.strftime('%A, %B %d, %Y')}
- Time: {meeting.start_time.strftime('%I:%M %p')} ({meeting.guest_timezone})
- Duration: {meeting.duration_minutes} minutes

"""

        if meeting.video_link:
            message += f"Join Meeting: {meeting.video_link}\n\n"

        message += "See you there!"

        return message

    @transaction.atomic
    def suggest_reschedule(
        self,
        meeting_id: str,
        trigger_type: str = 'optimization',
        trigger_reason: str = ''
    ) -> dict:
        """Generate reschedule suggestions for a meeting"""
        from .ai_models import SmartReschedule
        from .models import Meeting

        try:
            meeting = Meeting.objects.get(id=meeting_id)
        except Meeting.DoesNotExist:
            raise ValueError(f"Meeting {meeting_id} not found")

        # Find alternative times
        finder = AITimeFinder(self.user)
        alternatives = finder.find_optimal_times(
            meeting_type=meeting.meeting_type,
            duration_minutes=meeting.duration_minutes,
            date_range_start=timezone.now(),
            date_range_end=timezone.now() + timedelta(days=14),
            participant_email=meeting.guest_email,
            num_suggestions=5
        )

        # Convert to dict format
        alt_list = [slot.to_dict() for slot in alternatives]

        # Get best suggestion
        best = alternatives[0] if alternatives else None

        # Create reschedule suggestion
        reschedule = SmartReschedule.objects.create(
            meeting=meeting,
            trigger_type=trigger_type,
            trigger_reason=trigger_reason,
            original_start=meeting.start_time,
            original_end=meeting.end_time,
            alternatives=alt_list,
            suggested_start=best.start if best else None,
            suggested_end=best.end if best else None,
            suggestion_score=best.overall_score if best else 0,
            expires_at=timezone.now() + timedelta(days=3)
        )

        return {
            'id': str(reschedule.id),
            'meeting_id': str(meeting.id),
            'original_start': reschedule.original_start.isoformat(),
            'original_end': reschedule.original_end.isoformat(),
            'suggested_start': reschedule.suggested_start.isoformat() if reschedule.suggested_start else None,
            'suggested_end': reschedule.suggested_end.isoformat() if reschedule.suggested_end else None,
            'suggestion_score': reschedule.suggestion_score,
            'alternatives': alt_list
        }

    @transaction.atomic
    def learn_preferences(self) -> dict:
        """Learn user's scheduling preferences from historical data"""
        from .ai_models import AISchedulingPreference
        from .models import Meeting

        # Get completed meetings from last 90 days
        ninety_days_ago = timezone.now() - timedelta(days=90)
        meetings = Meeting.objects.filter(
            host=self.user,
            status='completed',
            start_time__gte=ninety_days_ago
        )

        if not meetings.exists():
            return {'message': 'Not enough data to learn preferences'}

        # Analyze meeting patterns
        time_counts = {}
        day_counts = {}

        for meeting in meetings:
            hour = meeting.start_time.hour
            day = meeting.start_time.weekday()

            time_counts[hour] = time_counts.get(hour, 0) + 1
            day_counts[day] = day_counts.get(day, 0) + 1

        # Convert to preference scores (normalize)
        total_meetings = meetings.count()

        time_prefs = {
            str(hour): round(count / total_meetings, 2)
            for hour, count in time_counts.items()
        }

        day_prefs = {
            str(day): round(count / total_meetings, 2)
            for day, count in day_counts.items()
        }

        # Find high/low energy hours based on meeting success
        # (Would use more sophisticated analysis in production)
        high_energy = [h for h, c in time_counts.items() if c >= total_meetings * 0.15]

        # Update or create preferences
        prefs, created = AISchedulingPreference.objects.update_or_create(
            user=self.user,
            defaults={
                'preferred_meeting_times': time_prefs,
                'preferred_days': day_prefs,
                'high_energy_hours': high_energy,
                'data_points_count': total_meetings,
                'last_learning_at': timezone.now(),
                'preference_confidence': min(total_meetings / 50, 1.0)  # Max confidence at 50 meetings
            }
        )

        return {
            'preferences_updated': True,
            'data_points_analyzed': total_meetings,
            'preferred_times': time_prefs,
            'preferred_days': day_prefs,
            'high_energy_hours': high_energy,
            'confidence': prefs.preference_confidence
        }

    @transaction.atomic
    def optimize_schedule(
        self,
        start_date: datetime,
        end_date: datetime,
        optimization_type: str = 'create_focus_time'
    ) -> dict:
        """Suggest schedule optimizations"""
        from .ai_models import ScheduleOptimization
        from .models import Meeting

        # Get meetings in range
        meetings = Meeting.objects.filter(
            host=self.user,
            start_time__gte=start_date,
            end_time__lte=end_date,
            status='confirmed'
        ).order_by('start_time')

        # Analyze current schedule
        current_metrics = self._analyze_schedule_metrics(meetings)

        # Generate optimization suggestions based on type
        if optimization_type == 'create_focus_time':
            suggestions = self._optimize_for_focus_time(meetings)
        elif optimization_type == 'batch_meetings':
            suggestions = self._optimize_for_batching(meetings)
        elif optimization_type == 'reduce_context_switch':
            suggestions = self._optimize_for_context_switching(meetings)
        else:
            suggestions = {'recommendations': [], 'optimized_metrics': current_metrics}

        # Create optimization record
        optimization = ScheduleOptimization.objects.create(
            user=self.user,
            optimization_type=optimization_type,
            analysis_start=start_date.date(),
            analysis_end=end_date.date(),
            current_schedule=[{
                'id': str(m.id),
                'start': m.start_time.isoformat(),
                'end': m.end_time.isoformat(),
                'title': m.meeting_type.name
            } for m in meetings],
            current_metrics=current_metrics,
            optimized_schedule=suggestions.get('optimized_schedule', []),
            optimized_metrics=suggestions.get('optimized_metrics', {}),
            meetings_affected=suggestions.get('meetings_affected', 0),
            time_saved_minutes=suggestions.get('time_saved_minutes', 0),
            focus_time_gained_minutes=suggestions.get('focus_time_gained_minutes', 0),
            context_switches_reduced=suggestions.get('context_switches_reduced', 0),
            current_score=current_metrics.get('overall_score', 0),
            optimized_score=suggestions.get('optimized_metrics', {}).get('overall_score', 0),
            improvement_percentage=suggestions.get('improvement_percentage', 0),
            recommendations=suggestions.get('recommendations', []),
            explanation=suggestions.get('explanation', '')
        )

        return {
            'id': str(optimization.id),
            'optimization_type': optimization_type,
            'current_metrics': current_metrics,
            'optimized_metrics': suggestions.get('optimized_metrics', {}),
            'recommendations': suggestions.get('recommendations', []),
            'meetings_affected': suggestions.get('meetings_affected', 0),
            'time_saved_minutes': suggestions.get('time_saved_minutes', 0),
            'focus_time_gained_minutes': suggestions.get('focus_time_gained_minutes', 0),
            'improvement_percentage': suggestions.get('improvement_percentage', 0)
        }

    def _analyze_schedule_metrics(self, meetings) -> dict:
        """Analyze schedule metrics"""

        if not meetings.exists():
            return {
                'total_meetings': 0,
                'total_meeting_hours': 0,
                'context_switches': 0,
                'focus_blocks': 0,
                'overall_score': 100
            }

        total_meeting_minutes = sum(m.duration_minutes for m in meetings)

        # Count context switches (meetings with < 2 hours between)
        context_switches = 0
        meetings_list = list(meetings)
        for i in range(len(meetings_list) - 1):
            gap = (meetings_list[i + 1].start_time - meetings_list[i].end_time).total_seconds() / 60
            if 0 < gap < 120:
                context_switches += 1

        # Estimate focus blocks (2+ hour gaps)
        focus_blocks = 0
        for i in range(len(meetings_list) - 1):
            gap = (meetings_list[i + 1].start_time - meetings_list[i].end_time).total_seconds() / 60
            if gap >= 120:
                focus_blocks += 1

        # Calculate overall score
        # Higher is better: fewer context switches, more focus blocks
        meeting_count = meetings.count()
        score = 100 - (context_switches * 10) + (focus_blocks * 5)
        score = max(0, min(100, score))

        return {
            'total_meetings': meeting_count,
            'total_meeting_hours': round(total_meeting_minutes / 60, 1),
            'context_switches': context_switches,
            'focus_blocks': focus_blocks,
            'overall_score': score
        }

    def _optimize_for_focus_time(self, meetings) -> dict:
        """Generate optimization suggestions for creating focus time"""

        recommendations = []

        # Analyze meetings and suggest batching on specific days
        meetings_by_day = {}
        for meeting in meetings:
            day = meeting.start_time.date()
            meetings_by_day.setdefault(day, []).append(meeting)

        # Find days with sparse meetings that could be consolidated
        sparse_days = [day for day, mlist in meetings_by_day.items() if len(mlist) == 1]

        if sparse_days:
            recommendations.append({
                'type': 'batch_meetings',
                'priority': 'medium',
                'description': f'Consider moving {len(sparse_days)} isolated meetings to create full focus days',
                'impact': 'Creates 4-8 hour focus blocks'
            })

        # Find days that could become meeting-free
        recommendations.append({
            'type': 'meeting_free_day',
            'priority': 'high',
            'description': 'Consider designating 1-2 days per week as meeting-free',
            'impact': 'Creates guaranteed deep work time'
        })

        return {
            'recommendations': recommendations,
            'optimized_metrics': {
                'focus_blocks': len(sparse_days) + 2,
                'context_switches': max(0, len(list(meetings)) - len(sparse_days)),
                'overall_score': 85
            },
            'focus_time_gained_minutes': len(sparse_days) * 180,
            'improvement_percentage': 20,
            'explanation': 'Consolidating sparse meetings can create larger focus blocks'
        }

    def _optimize_for_batching(self, meetings) -> dict:
        """Generate optimization for meeting batching"""

        recommendations = [{
            'type': 'batch_similar',
            'priority': 'high',
            'description': 'Group similar meeting types together',
            'impact': 'Reduces context switching by 50%'
        }]

        return {
            'recommendations': recommendations,
            'optimized_metrics': {'overall_score': 80},
            'context_switches_reduced': 3,
            'improvement_percentage': 15
        }

    def _optimize_for_context_switching(self, meetings) -> dict:
        """Generate optimization to reduce context switching"""

        recommendations = [{
            'type': 'add_buffers',
            'priority': 'medium',
            'description': 'Add 15-minute buffers between meetings',
            'impact': 'Allows mental transition between topics'
        }]

        return {
            'recommendations': recommendations,
            'optimized_metrics': {'overall_score': 75},
            'time_saved_minutes': 30,
            'improvement_percentage': 10
        }


class AttendeeIntelligenceService:
    """Service for managing attendee intelligence"""

    @staticmethod
    @transaction.atomic
    def update_attendee_intelligence(email: str, meeting_outcome: str):
        """Update intelligence based on meeting outcome"""
        from .ai_models import AttendeeIntelligence

        intel, created = AttendeeIntelligence.objects.get_or_create(
            email=email,
            defaults={'name': ''}
        )

        intel.total_meetings_scheduled += 1

        if meeting_outcome == 'completed':
            intel.meetings_attended += 1
        elif meeting_outcome == 'no_show':
            intel.meetings_no_show += 1
        elif meeting_outcome == 'cancelled':
            intel.meetings_cancelled += 1
        elif meeting_outcome == 'rescheduled':
            intel.meetings_rescheduled += 1

        # Recalculate reliability score
        if intel.total_meetings_scheduled > 0:
            intel.reliability_score = intel.meetings_attended / intel.total_meetings_scheduled

        intel.last_meeting_at = timezone.now()
        intel.save()

        return intel

    @staticmethod
    def get_attendee_insights(email: str) -> dict | None:
        """Get insights about an attendee"""
        from .ai_models import AttendeeIntelligence

        try:
            intel = AttendeeIntelligence.objects.get(email=email)
            return {
                'email': intel.email,
                'name': intel.name,
                'total_meetings': intel.total_meetings_scheduled,
                'attendance_rate': intel.attendance_rate,
                'no_show_rate': intel.no_show_rate,
                'reliability_score': intel.reliability_score,
                'preferred_meeting_times': intel.preferred_meeting_times,
                'best_communication_channel': intel.best_communication_channel,
                'last_meeting_at': intel.last_meeting_at.isoformat() if intel.last_meeting_at else None
            }
        except AttendeeIntelligence.DoesNotExist:
            return None
