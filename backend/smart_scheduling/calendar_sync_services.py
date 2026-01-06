"""
Calendar Sync Intelligence Services
Advanced calendar sync with conflict detection, multi-calendar support, and availability broadcasting
"""

import logging
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

logger = logging.getLogger(__name__)
User = get_user_model()


class CalendarSyncService:
    """Service for managing calendar synchronization"""

    def __init__(self, user):
        self.user = user

    def sync_calendar(self, integration_id: str) -> dict:
        """Sync calendar with external provider"""
        from .models import BlockedTime, CalendarIntegration

        try:
            integration = CalendarIntegration.objects.get(
                id=integration_id,
                user=self.user
            )
        except CalendarIntegration.DoesNotExist:
            raise ValueError(f"Integration {integration_id} not found")

        # Get calendar events based on provider
        if integration.provider == 'google':
            events = self._sync_google_calendar(integration)
        elif integration.provider == 'outlook':
            events = self._sync_outlook_calendar(integration)
        elif integration.provider == 'apple':
            events = self._sync_apple_calendar(integration)
        else:
            events = []

        # Convert external events to blocked times for conflict detection
        synced_count = 0
        for event in events:
            # Skip if it's our own event
            if event.get('is_own_meeting'):
                continue

            # Create or update blocked time
            BlockedTime.objects.update_or_create(
                page=self.user.scheduling_pages.first(),
                start_datetime=event['start'],
                end_datetime=event['end'],
                defaults={
                    'title': event.get('title', 'Busy'),
                    'all_day': event.get('all_day', False)
                }
            )
            synced_count += 1

        # Update last synced
        integration.last_synced_at = timezone.now()
        integration.save(update_fields=['last_synced_at'])

        return {
            'integration_id': str(integration.id),
            'provider': integration.provider,
            'events_synced': synced_count,
            'last_synced_at': integration.last_synced_at.isoformat()
        }

    def _sync_google_calendar(self, integration) -> list[dict]:
        """Sync with Google Calendar API"""
        # In production, use Google Calendar API
        # For now, return mock data structure

        logger.info(f"Syncing Google Calendar for {self.user.email}")

        # This would make actual API calls:
        # from google.oauth2.credentials import Credentials
        # from googleapiclient.discovery import build
        #
        # credentials = Credentials(
        #     token=integration.access_token,
        #     refresh_token=integration.refresh_token
        # )
        # service = build('calendar', 'v3', credentials=credentials)
        # events = service.events().list(
        #     calendarId=integration.calendar_id,
        #     timeMin=timezone.now().isoformat(),
        #     timeMax=(timezone.now() + timedelta(days=60)).isoformat(),
        #     singleEvents=True,
        #     orderBy='startTime'
        # ).execute()

        return []

    def _sync_outlook_calendar(self, integration) -> list[dict]:
        """Sync with Outlook/Microsoft Calendar API"""
        logger.info(f"Syncing Outlook Calendar for {self.user.email}")

        # In production, use Microsoft Graph API
        # import requests
        #
        # headers = {'Authorization': f'Bearer {integration.access_token}'}
        # response = requests.get(
        #     'https://graph.microsoft.com/v1.0/me/calendar/events',
        #     headers=headers
        # )

        return []

    def _sync_apple_calendar(self, integration) -> list[dict]:
        """Sync with Apple Calendar (iCloud)"""
        logger.info(f"Syncing Apple Calendar for {self.user.email}")
        return []

    def check_conflicts(
        self,
        start_time: datetime,
        end_time: datetime,
        exclude_meeting_id: str | None = None
    ) -> dict:
        """Check for calendar conflicts"""
        from .models import BlockedTime, Meeting

        conflicts = []

        # Check against scheduled meetings
        meeting_conflicts = Meeting.objects.filter(
            host=self.user,
            status__in=['confirmed', 'pending'],
            start_time__lt=end_time,
            end_time__gt=start_time
        )

        if exclude_meeting_id:
            meeting_conflicts = meeting_conflicts.exclude(id=exclude_meeting_id)

        for meeting in meeting_conflicts:
            conflicts.append({
                'type': 'meeting',
                'id': str(meeting.id),
                'title': meeting.meeting_type.name,
                'start': meeting.start_time.isoformat(),
                'end': meeting.end_time.isoformat(),
                'guest': meeting.guest_name
            })

        # Check against blocked times from all scheduling pages
        pages = self.user.scheduling_pages.all()
        for page in pages:
            blocked_conflicts = BlockedTime.objects.filter(
                page=page,
                start_datetime__lt=end_time,
                end_datetime__gt=start_time
            )

            for blocked in blocked_conflicts:
                conflicts.append({
                    'type': 'blocked',
                    'id': str(blocked.id),
                    'title': blocked.title or 'Busy',
                    'start': blocked.start_datetime.isoformat(),
                    'end': blocked.end_datetime.isoformat()
                })

        return {
            'has_conflicts': len(conflicts) > 0,
            'conflict_count': len(conflicts),
            'conflicts': conflicts
        }

    def get_availability_windows(
        self,
        date: datetime,
        duration_minutes: int = 30
    ) -> list[dict]:
        """Get available time windows for a specific date"""
        from .models import Availability

        windows = []
        day_of_week = date.weekday()

        # Get availability slots for this day
        page = self.user.scheduling_pages.first()
        if not page:
            return windows

        availability_slots = Availability.objects.filter(
            page=page,
            day_of_week=day_of_week,
            is_active=True
        )

        for slot in availability_slots:
            # Create datetime from time
            slot_start = date.replace(
                hour=slot.start_time.hour,
                minute=slot.start_time.minute,
                second=0,
                microsecond=0
            )
            slot_end = date.replace(
                hour=slot.end_time.hour,
                minute=slot.end_time.minute,
                second=0,
                microsecond=0
            )

            # Get conflicts for this window
            conflicts_result = self.check_conflicts(slot_start, slot_end)
            conflicts = conflicts_result['conflicts']

            # Calculate available windows within this slot
            current_start = slot_start

            # Sort conflicts by start time
            conflicts.sort(key=lambda x: x['start'])

            for conflict in conflicts:
                conflict_start = datetime.fromisoformat(conflict['start'])
                conflict_end = datetime.fromisoformat(conflict['end'])

                # If there's a gap before this conflict
                if conflict_start > current_start:
                    gap_minutes = (conflict_start - current_start).total_seconds() / 60
                    if gap_minutes >= duration_minutes:
                        windows.append({
                            'start': current_start.isoformat(),
                            'end': conflict_start.isoformat(),
                            'duration_minutes': int(gap_minutes)
                        })

                # Move current_start past this conflict
                if conflict_end > current_start:
                    current_start = conflict_end

            # Check remaining time after all conflicts
            if current_start < slot_end:
                remaining_minutes = (slot_end - current_start).total_seconds() / 60
                if remaining_minutes >= duration_minutes:
                    windows.append({
                        'start': current_start.isoformat(),
                        'end': slot_end.isoformat(),
                        'duration_minutes': int(remaining_minutes)
                    })

        return windows

    def broadcast_availability(self) -> dict:
        """Generate shareable availability for external use"""
        from .models import SchedulingPage

        page = SchedulingPage.objects.filter(user=self.user, is_active=True).first()

        if not page:
            return {'error': 'No active scheduling page'}

        # Generate availability for next 14 days
        availability_data = []
        current_date = timezone.now().date()

        for i in range(14):
            date = current_date + timedelta(days=i)
            date_dt = timezone.make_aware(
                datetime.combine(date, datetime.min.time())
            )

            windows = self.get_availability_windows(date_dt)
            if windows:
                availability_data.append({
                    'date': date.isoformat(),
                    'day_name': date.strftime('%A'),
                    'windows': windows
                })

        return {
            'scheduling_page_url': f'/book/{page.slug}',
            'timezone': page.timezone,
            'availability': availability_data
        }


class MultiCalendarService:
    """Service for managing multiple calendar integrations"""

    def __init__(self, user):
        self.user = user

    def get_unified_calendar(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> dict:
        """Get unified view across all calendars"""
        from .models import BlockedTime, CalendarIntegration, Meeting

        events = []

        # Get CRM meetings
        meetings = Meeting.objects.filter(
            host=self.user,
            start_time__gte=start_date,
            end_time__lte=end_date
        ).order_by('start_time')

        for meeting in meetings:
            events.append({
                'type': 'crm_meeting',
                'id': str(meeting.id),
                'title': meeting.meeting_type.name,
                'description': f"Meeting with {meeting.guest_name}",
                'start': meeting.start_time.isoformat(),
                'end': meeting.end_time.isoformat(),
                'status': meeting.status,
                'location': meeting.location or meeting.video_link,
                'guest_name': meeting.guest_name,
                'guest_email': meeting.guest_email,
                'color': meeting.meeting_type.color
            })

        # Get blocked times (synced from external calendars)
        page = self.user.scheduling_pages.first()
        if page:
            blocked_times = BlockedTime.objects.filter(
                page=page,
                start_datetime__gte=start_date,
                end_datetime__lte=end_date
            )

            for blocked in blocked_times:
                events.append({
                    'type': 'external',
                    'id': str(blocked.id),
                    'title': blocked.title or 'Busy',
                    'start': blocked.start_datetime.isoformat(),
                    'end': blocked.end_datetime.isoformat(),
                    'all_day': blocked.all_day,
                    'color': '#94A3B8'  # Gray for external events
                })

        # Get calendar integrations status
        integrations = CalendarIntegration.objects.filter(
            user=self.user,
            is_active=True
        )

        return {
            'events': sorted(events, key=lambda x: x['start']),
            'event_count': len(events),
            'integrations': [
                {
                    'provider': i.provider,
                    'calendar_name': i.calendar_name,
                    'last_synced': i.last_synced_at.isoformat() if i.last_synced_at else None
                }
                for i in integrations
            ]
        }

    def find_common_free_time(
        self,
        participant_emails: list[str],
        duration_minutes: int,
        date_range_days: int = 7
    ) -> list[dict]:
        """Find common free time slots across multiple participants"""

        # This would integrate with external calendars via FreeBusy API
        # For now, return the user's available slots

        sync_service = CalendarSyncService(self.user)
        common_slots = []

        for i in range(date_range_days):
            date = timezone.now() + timedelta(days=i)
            date_dt = timezone.make_aware(
                datetime.combine(date.date(), datetime.min.time())
            )

            windows = sync_service.get_availability_windows(date_dt, duration_minutes)

            for window in windows:
                if window['duration_minutes'] >= duration_minutes:
                    common_slots.append({
                        'date': date.date().isoformat(),
                        'start': window['start'],
                        'end': window['end'],
                        'available_for_all': True,  # Would check against participant calendars
                        'participants_available': participant_emails
                    })

        return common_slots[:10]  # Return top 10 slots


class CalendarIntelligenceService:
    """AI-powered calendar intelligence and insights"""

    def __init__(self, user):
        self.user = user

    def analyze_calendar_patterns(self, days: int = 30) -> dict:
        """Analyze calendar patterns and provide insights"""
        from .models import Meeting

        start_date = timezone.now() - timedelta(days=days)
        meetings = Meeting.objects.filter(
            host=self.user,
            start_time__gte=start_date
        )

        if not meetings.exists():
            return {'message': 'Not enough data for pattern analysis'}

        # Analyze by day of week
        meetings_by_day = {}
        for i in range(7):
            meetings_by_day[i] = 0

        for meeting in meetings:
            day = meeting.start_time.weekday()
            meetings_by_day[day] = meetings_by_day.get(day, 0) + 1

        # Analyze by hour
        meetings_by_hour = {}
        for i in range(24):
            meetings_by_hour[i] = 0

        for meeting in meetings:
            hour = meeting.start_time.hour
            meetings_by_hour[hour] = meetings_by_hour.get(hour, 0) + 1

        # Find busiest day and hour
        busiest_day = max(meetings_by_day.items(), key=lambda x: x[1])
        busiest_hour = max(meetings_by_hour.items(), key=lambda x: x[1])

        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        # Calculate meeting load
        total_meetings = meetings.count()
        avg_per_day = total_meetings / days

        # Meeting type distribution
        type_distribution = {}
        for meeting in meetings:
            type_name = meeting.meeting_type.name
            type_distribution[type_name] = type_distribution.get(type_name, 0) + 1

        # Calculate meeting hours
        total_meeting_minutes = sum(m.duration_minutes for m in meetings)
        meeting_hours_per_week = (total_meeting_minutes / 60) / (days / 7)

        # Generate insights
        insights = []

        if meeting_hours_per_week > 20:
            insights.append({
                'type': 'warning',
                'title': 'High Meeting Load',
                'description': f'You spend {meeting_hours_per_week:.1f} hours per week in meetings. Consider protecting focus time.'
            })

        if meetings_by_day.get(0, 0) > meetings_by_day.get(4, 0) * 2:
            insights.append({
                'type': 'pattern',
                'title': 'Monday Heavy',
                'description': 'Mondays are significantly busier than Fridays. Consider spreading meetings more evenly.'
            })

        if meetings_by_hour.get(12, 0) > avg_per_day * 3:
            insights.append({
                'type': 'suggestion',
                'title': 'Lunch Meetings',
                'description': 'Many meetings scheduled during lunch hour. Consider protecting this time.'
            })

        return {
            'period_days': days,
            'total_meetings': total_meetings,
            'meetings_per_day_avg': round(avg_per_day, 1),
            'meeting_hours_per_week': round(meeting_hours_per_week, 1),
            'busiest_day': {
                'day': day_names[busiest_day[0]],
                'meeting_count': busiest_day[1]
            },
            'busiest_hour': {
                'hour': f"{busiest_hour[0]:02d}:00",
                'meeting_count': busiest_hour[1]
            },
            'distribution_by_day': {
                day_names[k]: v for k, v in meetings_by_day.items()
            },
            'distribution_by_hour': meetings_by_hour,
            'type_distribution': type_distribution,
            'insights': insights
        }

    def get_productivity_score(self) -> dict:
        """Calculate calendar productivity score"""
        from .models import Meeting

        # Analyze last 7 days
        week_ago = timezone.now() - timedelta(days=7)
        meetings = Meeting.objects.filter(
            host=self.user,
            start_time__gte=week_ago
        )

        if not meetings.exists():
            return {
                'score': 100,
                'message': 'No meetings this week - full focus time available'
            }

        total_minutes = sum(m.duration_minutes for m in meetings)
        work_hours_per_week = 40 * 60  # 40 hours in minutes

        # Meeting percentage
        meeting_percentage = (total_minutes / work_hours_per_week) * 100

        # Context switches (meetings with < 1 hour gap)
        meetings_list = list(meetings.order_by('start_time'))
        context_switches = 0
        for i in range(len(meetings_list) - 1):
            gap = (meetings_list[i + 1].start_time - meetings_list[i].end_time).total_seconds() / 60
            if 0 < gap < 60:
                context_switches += 1

        # Calculate score (higher is better)
        # Ideal: ~25% meeting time, low context switches
        base_score = 100

        # Penalize for too many meetings
        if meeting_percentage > 50:
            base_score -= (meeting_percentage - 50) * 0.5
        elif meeting_percentage > 30:
            base_score -= (meeting_percentage - 30) * 0.3

        # Penalize for context switches
        base_score -= context_switches * 2

        score = max(0, min(100, base_score))

        # Generate recommendations
        recommendations = []

        if meeting_percentage > 40:
            recommendations.append('Consider declining some meetings or shortening meeting durations')

        if context_switches > 5:
            recommendations.append('Try to batch meetings together to reduce context switching')

        return {
            'score': round(score),
            'meeting_percentage': round(meeting_percentage, 1),
            'total_meeting_hours': round(total_minutes / 60, 1),
            'context_switches': context_switches,
            'recommendations': recommendations,
            'rating': self._get_rating(score)
        }

    def _get_rating(self, score: float) -> str:
        """Convert score to rating"""
        if score >= 80:
            return 'excellent'
        elif score >= 60:
            return 'good'
        elif score >= 40:
            return 'needs_improvement'
        else:
            return 'overloaded'

    def suggest_meeting_free_blocks(self) -> list[dict]:
        """Suggest optimal meeting-free focus blocks"""
        from .models import Meeting

        suggestions = []
        page = self.user.scheduling_pages.first()

        if not page:
            return suggestions

        # Analyze meeting patterns to find natural gaps
        week_ago = timezone.now() - timedelta(days=7)
        meetings = Meeting.objects.filter(
            host=self.user,
            start_time__gte=week_ago
        ).order_by('start_time')

        # Find hours with fewest meetings historically
        meeting_by_hour = {}
        for meeting in meetings:
            hour = meeting.start_time.hour
            meeting_by_hour[hour] = meeting_by_hour.get(hour, 0) + 1

        # Find 2-4 hour blocks with low meeting density
        for start_hour in range(8, 16):
            block_count = sum(
                meeting_by_hour.get(h, 0)
                for h in range(start_hour, start_hour + 2)
            )

            if block_count < 2:  # Low meeting density
                suggestions.append({
                    'start_hour': start_hour,
                    'end_hour': start_hour + 2,
                    'time_label': f"{start_hour:02d}:00 - {start_hour + 2:02d}:00",
                    'historical_meeting_count': block_count,
                    'recommendation': 'Good time for focus work',
                    'days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
                })

        return suggestions[:3]  # Return top 3 suggestions
