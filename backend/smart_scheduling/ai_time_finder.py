"""
AI Time Finder Engine
Finds optimal meeting times using AI analysis
"""

import logging
from datetime import datetime, timedelta, time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from django.utils import timezone
from django.db.models import Avg, Count, Q
import json

logger = logging.getLogger(__name__)


@dataclass
class TimeSlot:
    """Represents a potential meeting time slot"""
    start: datetime
    end: datetime
    overall_score: float = 0.0
    preference_score: float = 0.0
    availability_score: float = 0.0
    energy_score: float = 0.0
    context_switch_score: float = 0.0
    reasons: List[str] = None
    
    def __post_init__(self):
        if self.reasons is None:
            self.reasons = []
    
    def to_dict(self):
        return {
            'start': self.start.isoformat(),
            'end': self.end.isoformat(),
            'overall_score': self.overall_score,
            'preference_score': self.preference_score,
            'availability_score': self.availability_score,
            'energy_score': self.energy_score,
            'context_switch_score': self.context_switch_score,
            'reasons': self.reasons
        }


class AITimeFinder:
    """AI-powered optimal meeting time finder"""
    
    # Default preference scores by time of day
    DEFAULT_TIME_PREFERENCES = {
        9: 0.8, 10: 0.9, 11: 0.85,  # Morning - high productivity
        12: 0.5,  # Lunch - lower
        13: 0.6, 14: 0.75, 15: 0.7, 16: 0.65,  # Afternoon
        17: 0.5, 18: 0.3  # End of day
    }
    
    # Default day preferences (0=Monday)
    DEFAULT_DAY_PREFERENCES = {
        0: 0.7,  # Monday - recover from weekend
        1: 0.9,  # Tuesday - peak
        2: 0.9,  # Wednesday - peak
        3: 0.85,  # Thursday
        4: 0.6,  # Friday - wind down
        5: 0.2,  # Saturday
        6: 0.1,  # Sunday
    }
    
    def __init__(self, user):
        self.user = user
        self.preferences = self._load_preferences()
    
    def _load_preferences(self):
        """Load user's AI scheduling preferences"""
        from .ai_models import AISchedulingPreference
        
        try:
            return AISchedulingPreference.objects.get(user=self.user)
        except AISchedulingPreference.DoesNotExist:
            return None
    
    def find_optimal_times(
        self,
        meeting_type,
        duration_minutes: int,
        date_range_start: datetime,
        date_range_end: datetime,
        participant_email: Optional[str] = None,
        num_suggestions: int = 5
    ) -> List[TimeSlot]:
        """Find optimal meeting times within the date range"""
        
        # Get all available slots
        available_slots = self._get_available_slots(
            meeting_type,
            duration_minutes,
            date_range_start,
            date_range_end
        )
        
        # Score each slot
        scored_slots = []
        for slot in available_slots:
            scored_slot = self._score_time_slot(slot, meeting_type, participant_email)
            scored_slots.append(scored_slot)
        
        # Sort by score and return top suggestions
        scored_slots.sort(key=lambda x: x.overall_score, reverse=True)
        
        return scored_slots[:num_suggestions]
    
    def _get_available_slots(
        self,
        meeting_type,
        duration_minutes: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[TimeSlot]:
        """Get all available time slots from user's availability"""
        from .models import Availability, BlockedTime, Meeting
        
        slots = []
        current_date = start_date.date()
        end_date_only = end_date.date()
        
        # Get user's availability rules
        availability_rules = Availability.objects.filter(
            page__owner=self.user,
            is_active=True
        )
        
        # Get blocked times
        blocked_times = BlockedTime.objects.filter(
            page__owner=self.user,
            start_datetime__lte=end_date,
            end_datetime__gte=start_date
        )
        
        # Get existing meetings
        existing_meetings = Meeting.objects.filter(
            host=self.user,
            start_time__gte=start_date,
            end_time__lte=end_date,
            status__in=['confirmed', 'pending']
        )
        
        while current_date <= end_date_only:
            day_of_week = current_date.weekday()
            
            # Get availability for this day
            day_availability = availability_rules.filter(day_of_week=day_of_week)
            
            for avail in day_availability:
                # Generate slots within this availability window
                slot_start = timezone.make_aware(
                    datetime.combine(current_date, avail.start_time)
                )
                window_end = timezone.make_aware(
                    datetime.combine(current_date, avail.end_time)
                )
                
                while slot_start + timedelta(minutes=duration_minutes) <= window_end:
                    slot_end = slot_start + timedelta(minutes=duration_minutes)
                    
                    # Check if slot is blocked
                    is_blocked = self._is_time_blocked(
                        slot_start, slot_end, blocked_times, existing_meetings
                    )
                    
                    # Check buffer times
                    if meeting_type.buffer_before > 0:
                        buffer_start = slot_start - timedelta(minutes=meeting_type.buffer_before)
                        if self._is_time_blocked(buffer_start, slot_start, blocked_times, existing_meetings):
                            is_blocked = True
                    
                    if meeting_type.buffer_after > 0:
                        buffer_end = slot_end + timedelta(minutes=meeting_type.buffer_after)
                        if self._is_time_blocked(slot_end, buffer_end, blocked_times, existing_meetings):
                            is_blocked = True
                    
                    if not is_blocked:
                        # Check minimum notice
                        if slot_start > timezone.now() + timedelta(hours=meeting_type.min_notice_hours):
                            slots.append(TimeSlot(start=slot_start, end=slot_end))
                    
                    # Move to next slot (30-minute increments)
                    slot_start += timedelta(minutes=30)
            
            current_date += timedelta(days=1)
        
        return slots
    
    def _is_time_blocked(self, start, end, blocked_times, existing_meetings) -> bool:
        """Check if a time slot conflicts with blocked times or existing meetings"""
        
        # Check blocked times
        for blocked in blocked_times:
            if start < blocked.end_datetime and end > blocked.start_datetime:
                return True
        
        # Check existing meetings
        for meeting in existing_meetings:
            if start < meeting.end_time and end > meeting.start_time:
                return True
        
        return False
    
    def _score_time_slot(
        self,
        slot: TimeSlot,
        meeting_type,
        participant_email: Optional[str] = None
    ) -> TimeSlot:
        """Score a time slot based on various factors"""
        
        reasons = []
        
        # 1. Preference Score (user's learned preferences)
        preference_score = self._calculate_preference_score(slot, reasons)
        
        # 2. Availability Score (how open the day is)
        availability_score = self._calculate_availability_score(slot, reasons)
        
        # 3. Energy Score (alignment with energy levels)
        energy_score = self._calculate_energy_score(slot, reasons)
        
        # 4. Context Switch Score (meeting batching/spacing)
        context_switch_score = self._calculate_context_switch_score(slot, reasons)
        
        # 5. Participant Score (if participant info available)
        participant_score = 1.0
        if participant_email:
            participant_score = self._calculate_participant_score(
                slot, participant_email, reasons
            )
        
        # Calculate overall score (weighted average)
        weights = {
            'preference': 0.25,
            'availability': 0.20,
            'energy': 0.20,
            'context_switch': 0.20,
            'participant': 0.15
        }
        
        overall_score = (
            preference_score * weights['preference'] +
            availability_score * weights['availability'] +
            energy_score * weights['energy'] +
            context_switch_score * weights['context_switch'] +
            participant_score * weights['participant']
        ) * 100  # Convert to 0-100 scale
        
        slot.overall_score = round(overall_score, 2)
        slot.preference_score = round(preference_score * 100, 2)
        slot.availability_score = round(availability_score * 100, 2)
        slot.energy_score = round(energy_score * 100, 2)
        slot.context_switch_score = round(context_switch_score * 100, 2)
        slot.reasons = reasons
        
        return slot
    
    def _calculate_preference_score(self, slot: TimeSlot, reasons: List[str]) -> float:
        """Calculate score based on user preferences"""
        
        hour = slot.start.hour
        day = slot.start.weekday()
        
        # Use learned preferences if available
        if self.preferences and self.preferences.preferred_meeting_times:
            time_pref = self.preferences.preferred_meeting_times.get(str(hour), 0.5)
        else:
            time_pref = self.DEFAULT_TIME_PREFERENCES.get(hour, 0.5)
        
        if self.preferences and self.preferences.preferred_days:
            day_pref = self.preferences.preferred_days.get(str(day), 0.5)
        else:
            day_pref = self.DEFAULT_DAY_PREFERENCES.get(day, 0.5)
        
        score = (time_pref + day_pref) / 2
        
        if score >= 0.8:
            reasons.append(f"Highly preferred time ({slot.start.strftime('%A %I:%M %p')})")
        elif score >= 0.6:
            reasons.append(f"Good time slot based on preferences")
        
        return score
    
    def _calculate_availability_score(self, slot: TimeSlot, reasons: List[str]) -> float:
        """Calculate score based on how busy the day is"""
        from .models import Meeting
        
        # Count meetings on the same day
        day_start = slot.start.replace(hour=0, minute=0, second=0)
        day_end = slot.start.replace(hour=23, minute=59, second=59)
        
        meetings_count = Meeting.objects.filter(
            host=self.user,
            start_time__range=(day_start, day_end),
            status__in=['confirmed', 'pending']
        ).count()
        
        max_meetings = self.preferences.max_meetings_per_day if self.preferences else 8
        
        if meetings_count == 0:
            score = 1.0
            reasons.append("Open day - no other meetings scheduled")
        elif meetings_count < max_meetings / 2:
            score = 0.8
            reasons.append(f"Light day ({meetings_count} meetings scheduled)")
        elif meetings_count < max_meetings:
            score = 0.5
            reasons.append(f"Moderate day ({meetings_count} meetings scheduled)")
        else:
            score = 0.2
            reasons.append(f"Busy day ({meetings_count} meetings already)")
        
        return score
    
    def _calculate_energy_score(self, slot: TimeSlot, reasons: List[str]) -> float:
        """Calculate score based on energy level alignment"""
        
        hour = slot.start.hour
        
        if self.preferences:
            if hour in self.preferences.high_energy_hours:
                reasons.append("Aligned with high energy period")
                return 1.0
            elif hour in self.preferences.low_energy_hours:
                reasons.append("During lower energy period")
                return 0.4
        
        # Default energy curve
        if 9 <= hour <= 11:
            reasons.append("Morning - typically high energy")
            return 0.9
        elif 14 <= hour <= 16:
            reasons.append("Afternoon - good focus time")
            return 0.7
        elif hour == 12 or hour == 13:
            reasons.append("Post-lunch - may have lower energy")
            return 0.5
        elif hour >= 17:
            reasons.append("End of day")
            return 0.4
        
        return 0.6
    
    def _calculate_context_switch_score(self, slot: TimeSlot, reasons: List[str]) -> float:
        """Calculate score based on context switching impact"""
        from .models import Meeting
        
        # Check meetings before and after
        buffer_window = timedelta(hours=2)
        
        nearby_meetings = Meeting.objects.filter(
            host=self.user,
            start_time__range=(slot.start - buffer_window, slot.end + buffer_window),
            status__in=['confirmed', 'pending']
        ).order_by('start_time')
        
        if not nearby_meetings.exists():
            reasons.append("Good spacing from other meetings")
            return 1.0
        
        # Check for batching preference
        if self.preferences and self.preferences.prefer_batched_meetings:
            # Higher score for meetings close together
            min_gap = self.preferences.min_gap_between_meetings
            has_adjacent = any(
                abs((m.end_time - slot.start).total_seconds()) < (min_gap + 30) * 60 or
                abs((slot.end - m.start_time).total_seconds()) < (min_gap + 30) * 60
                for m in nearby_meetings
            )
            if has_adjacent:
                reasons.append("Batched with nearby meetings (per preference)")
                return 0.9
        
        # Check minimum gap
        min_gap_minutes = self.preferences.min_gap_between_meetings if self.preferences else 15
        
        for meeting in nearby_meetings:
            gap_before = (slot.start - meeting.end_time).total_seconds() / 60
            gap_after = (meeting.start_time - slot.end).total_seconds() / 60
            
            if 0 < gap_before < min_gap_minutes or 0 < gap_after < min_gap_minutes:
                reasons.append("Tight spacing with adjacent meetings")
                return 0.4
        
        return 0.7
    
    def _calculate_participant_score(
        self,
        slot: TimeSlot,
        participant_email: str,
        reasons: List[str]
    ) -> float:
        """Calculate score based on participant intelligence"""
        from .ai_models import AttendeeIntelligence
        
        try:
            intel = AttendeeIntelligence.objects.get(email=participant_email)
            
            # Check preferred times
            if intel.preferred_meeting_times:
                slot_hour = slot.start.hour
                if slot_hour in intel.preferred_meeting_times:
                    reasons.append(f"Matches participant's preferred meeting time")
                    return 1.0
            
            # Consider reliability
            if intel.reliability_score > 0.8:
                reasons.append("High reliability participant")
                return 0.9
            elif intel.reliability_score < 0.5:
                reasons.append("Lower reliability participant - consider confirmation")
                return 0.6
            
            return 0.7
            
        except AttendeeIntelligence.DoesNotExist:
            return 0.7  # Neutral score for unknown participants


class NoShowPredictor:
    """Predicts no-show probability for meetings"""
    
    def __init__(self):
        self.risk_factors = []
    
    def predict(self, meeting) -> Dict:
        """Predict no-show probability for a meeting"""
        from .ai_models import AttendeeIntelligence
        
        self.risk_factors = []
        risk_score = 0
        
        # Factor 1: Historical no-show rate for this guest
        guest_score = self._analyze_guest_history(meeting)
        risk_score += guest_score
        
        # Factor 2: Time until meeting
        timing_score = self._analyze_timing(meeting)
        risk_score += timing_score
        
        # Factor 3: Meeting time of day
        time_score = self._analyze_meeting_time(meeting)
        risk_score += time_score
        
        # Factor 4: Day of week
        day_score = self._analyze_day_of_week(meeting)
        risk_score += day_score
        
        # Factor 5: Confirmation status
        confirmation_score = self._analyze_confirmation(meeting)
        risk_score += confirmation_score
        
        # Factor 6: Reschedule history
        reschedule_score = self._analyze_reschedules(meeting)
        risk_score += reschedule_score
        
        # Normalize to 0-100
        risk_score = min(100, max(0, risk_score))
        probability = risk_score / 100
        
        # Recommended actions
        recommended_actions = self._get_recommended_actions(risk_score)
        
        return {
            'no_show_probability': probability,
            'risk_score': risk_score,
            'risk_factors': self.risk_factors,
            'recommended_actions': recommended_actions,
            'extra_reminder_suggested': risk_score > 50,
            'confirmation_call_suggested': risk_score > 70
        }
    
    def _analyze_guest_history(self, meeting) -> int:
        """Analyze guest's historical meeting behavior"""
        from .ai_models import AttendeeIntelligence
        
        try:
            intel = AttendeeIntelligence.objects.get(email=meeting.guest_email)
            
            if intel.total_meetings_scheduled > 0:
                no_show_rate = intel.no_show_rate
                
                if no_show_rate > 0.3:
                    self.risk_factors.append({
                        'factor': 'High historical no-show rate',
                        'detail': f'{no_show_rate*100:.0f}% no-show rate',
                        'impact': 'high'
                    })
                    return 30
                elif no_show_rate > 0.1:
                    self.risk_factors.append({
                        'factor': 'Moderate historical no-show rate',
                        'detail': f'{no_show_rate*100:.0f}% no-show rate',
                        'impact': 'medium'
                    })
                    return 15
                else:
                    self.risk_factors.append({
                        'factor': 'Good attendance history',
                        'detail': f'{intel.attendance_rate*100:.0f}% attendance rate',
                        'impact': 'positive'
                    })
                    return -10
        except AttendeeIntelligence.DoesNotExist:
            self.risk_factors.append({
                'factor': 'First-time guest',
                'detail': 'No historical data available',
                'impact': 'neutral'
            })
            return 10
        
        return 0
    
    def _analyze_timing(self, meeting) -> int:
        """Analyze time until meeting"""
        
        days_until = (meeting.start_time - timezone.now()).days
        
        if days_until > 14:
            self.risk_factors.append({
                'factor': 'Far future meeting',
                'detail': f'Meeting is {days_until} days away',
                'impact': 'medium'
            })
            return 15
        elif days_until > 7:
            return 10
        elif days_until < 1:
            self.risk_factors.append({
                'factor': 'Meeting is tomorrow or today',
                'detail': 'Short notice increases commitment',
                'impact': 'positive'
            })
            return -5
        
        return 0
    
    def _analyze_meeting_time(self, meeting) -> int:
        """Analyze meeting time of day"""
        
        hour = meeting.start_time.hour
        
        if hour < 9:
            self.risk_factors.append({
                'factor': 'Early morning meeting',
                'detail': f'Meeting at {hour}:00',
                'impact': 'medium'
            })
            return 15
        elif hour >= 17:
            self.risk_factors.append({
                'factor': 'Late day meeting',
                'detail': f'Meeting at {hour}:00',
                'impact': 'low'
            })
            return 10
        elif 10 <= hour <= 15:
            return -5  # Prime hours
        
        return 0
    
    def _analyze_day_of_week(self, meeting) -> int:
        """Analyze day of week"""
        
        day = meeting.start_time.weekday()
        
        if day == 0:  # Monday
            self.risk_factors.append({
                'factor': 'Monday meeting',
                'detail': 'Mondays tend to have higher no-show rates',
                'impact': 'low'
            })
            return 10
        elif day == 4:  # Friday
            self.risk_factors.append({
                'factor': 'Friday meeting',
                'detail': 'Fridays tend to have higher cancellation rates',
                'impact': 'low'
            })
            return 10
        
        return 0
    
    def _analyze_confirmation(self, meeting) -> int:
        """Analyze confirmation status"""
        
        if meeting.status == 'pending':
            self.risk_factors.append({
                'factor': 'Pending confirmation',
                'detail': 'Meeting not yet confirmed by host',
                'impact': 'medium'
            })
            return 15
        
        # Check if reminders were acknowledged
        if hasattr(meeting, 'smart_reminders'):
            opened_reminders = meeting.smart_reminders.filter(opened=True).count()
            sent_reminders = meeting.smart_reminders.filter(sent=True).count()
            
            if sent_reminders > 0 and opened_reminders == 0:
                self.risk_factors.append({
                    'factor': 'Reminders not opened',
                    'detail': f'{sent_reminders} reminders sent, none opened',
                    'impact': 'high'
                })
                return 20
            elif opened_reminders > 0:
                self.risk_factors.append({
                    'factor': 'Reminders acknowledged',
                    'detail': f'{opened_reminders}/{sent_reminders} reminders opened',
                    'impact': 'positive'
                })
                return -10
        
        return 0
    
    def _analyze_reschedules(self, meeting) -> int:
        """Analyze previous reschedule attempts"""
        
        reschedule_count = meeting.reschedule_suggestions.count() if hasattr(meeting, 'reschedule_suggestions') else 0
        
        if reschedule_count > 2:
            self.risk_factors.append({
                'factor': 'Multiple reschedules',
                'detail': f'Meeting has been rescheduled {reschedule_count} times',
                'impact': 'high'
            })
            return 25
        elif reschedule_count > 0:
            self.risk_factors.append({
                'factor': 'Previously rescheduled',
                'detail': f'Meeting has been rescheduled {reschedule_count} time(s)',
                'impact': 'low'
            })
            return 10
        
        return 0
    
    def _get_recommended_actions(self, risk_score: int) -> List[Dict]:
        """Get recommended actions based on risk score"""
        
        actions = []
        
        if risk_score > 70:
            actions.extend([
                {
                    'action': 'Send personalized reminder',
                    'priority': 'high',
                    'description': 'Send a personalized email or SMS reminder'
                },
                {
                    'action': 'Confirmation call',
                    'priority': 'high',
                    'description': 'Consider a brief confirmation call'
                },
                {
                    'action': 'Offer rescheduling',
                    'priority': 'medium',
                    'description': 'Proactively offer to reschedule if timing is an issue'
                }
            ])
        elif risk_score > 50:
            actions.extend([
                {
                    'action': 'Extra reminder',
                    'priority': 'medium',
                    'description': 'Send an additional reminder closer to meeting time'
                },
                {
                    'action': 'Calendar invite check',
                    'priority': 'medium',
                    'description': 'Verify calendar invite was received'
                }
            ])
        elif risk_score > 30:
            actions.append({
                'action': 'Standard reminders',
                'priority': 'low',
                'description': 'Ensure standard reminders are scheduled'
            })
        
        return actions
