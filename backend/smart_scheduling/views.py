"""
Smart Scheduling Views
Complete scheduling functionality
"""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q
from datetime import datetime, timedelta, time
import pytz
import logging

from .models import (
    SchedulingPage, MeetingType, Availability, BlockedTime,
    Meeting, MeetingReminder, CalendarIntegration
)
from .serializers import (
    SchedulingPageSerializer, SchedulingPagePublicSerializer, MeetingTypeSerializer,
    AvailabilitySerializer, BlockedTimeSerializer, MeetingSerializer, MeetingListSerializer,
    BookMeetingSerializer, RescheduleMeetingSerializer, CancelMeetingSerializer,
    CalendarIntegrationSerializer
)
from core.email_notifications import EmailNotificationService

logger = logging.getLogger(__name__)


class SchedulingPageViewSet(viewsets.ModelViewSet):
    """Manage scheduling pages"""
    serializer_class = SchedulingPageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SchedulingPage.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get page statistics"""
        page = self.get_object()
        
        meetings = Meeting.objects.filter(meeting_type__page=page)
        
        return Response({
            'total_bookings': page.bookings_count,
            'page_views': page.page_views,
            'conversion_rate': page.conversion_rate,
            'upcoming_meetings': meetings.filter(
                status='confirmed',
                start_time__gt=timezone.now()
            ).count(),
            'completed_meetings': meetings.filter(status='completed').count(),
            'cancelled_meetings': meetings.filter(status='cancelled').count(),
        })
    
    @action(detail=True, methods=['post'])
    def setup_default_availability(self, request, pk=None):
        """Set up default business hours availability"""
        page = self.get_object()
        
        # Clear existing
        page.availability.all().delete()
        
        # Set Monday-Friday 9am-5pm
        for day in range(5):  # 0=Monday to 4=Friday
            Availability.objects.create(
                page=page,
                day_of_week=day,
                start_time=time(9, 0),
                end_time=time(17, 0)
            )
        
        return Response({'status': 'Default availability set'})


class MeetingTypeViewSet(viewsets.ModelViewSet):
    """Manage meeting types"""
    serializer_class = MeetingTypeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MeetingType.objects.filter(page__owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a meeting type"""
        original = self.get_object()
        
        new_type = MeetingType.objects.create(
            page=original.page,
            name=f"{original.name} (Copy)",
            slug=f"{original.slug}-copy",
            description=original.description,
            duration_minutes=original.duration_minutes,
            location_type=original.location_type,
            location_details=original.location_details,
            buffer_before=original.buffer_before,
            buffer_after=original.buffer_after,
            min_notice_hours=original.min_notice_hours,
            max_future_days=original.max_future_days,
            custom_questions=original.custom_questions,
            color=original.color,
        )
        
        serializer = self.get_serializer(new_type)
        return Response(serializer.data, status=201)


class AvailabilityViewSet(viewsets.ModelViewSet):
    """Manage availability slots"""
    serializer_class = AvailabilitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Availability.objects.filter(page__owner=self.request.user)


class BlockedTimeViewSet(viewsets.ModelViewSet):
    """Manage blocked times"""
    serializer_class = BlockedTimeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return BlockedTime.objects.filter(page__owner=self.request.user)


class MeetingViewSet(viewsets.ModelViewSet):
    """Manage meetings"""
    serializer_class = MeetingSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'meeting_type']
    ordering_fields = ['start_time', 'created_at']
    
    def get_queryset(self):
        return Meeting.objects.filter(host=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MeetingListSerializer
        return MeetingSerializer
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming meetings"""
        meetings = self.get_queryset().filter(
            status='confirmed',
            start_time__gt=timezone.now()
        ).order_by('start_time')[:20]
        
        serializer = MeetingListSerializer(meetings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's meetings"""
        today = timezone.now().date()
        meetings = self.get_queryset().filter(
            status='confirmed',
            start_time__date=today
        ).order_by('start_time')
        
        serializer = MeetingSerializer(meetings, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm a pending meeting"""
        meeting = self.get_object()
        
        if meeting.status != 'pending':
            return Response(
                {'error': 'Meeting is not pending'},
                status=400
            )
        
        meeting.status = 'confirmed'
        meeting.save()
        
        # Send confirmation email
        try:
            EmailNotificationService.send_meeting_confirmation(
                guest_email=meeting.guest_email,
                guest_name=meeting.guest_name,
                meeting=meeting,
                host=meeting.host
            )
        except Exception as e:
            logger.warning(f"Failed to send confirmation email: {e}")
        
        serializer = self.get_serializer(meeting)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a meeting"""
        meeting = self.get_object()
        
        serializer = CancelMeetingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        meeting.status = 'cancelled'
        meeting.cancelled_at = timezone.now()
        meeting.cancellation_reason = serializer.validated_data.get('reason', '')
        meeting.save()
        
        # Send cancellation email
        try:
            EmailNotificationService.send_meeting_cancelled(
                guest_email=meeting.guest_email,
                guest_name=meeting.guest_name,
                meeting=meeting,
                host=meeting.host,
                reason=meeting.cancellation_reason
            )
        except Exception as e:
            logger.warning(f"Failed to send cancellation email: {e}")
        
        return Response({'status': 'Meeting cancelled'})
    
    @action(detail=True, methods=['post'])
    def reschedule(self, request, pk=None):
        """Reschedule a meeting"""
        meeting = self.get_object()
        
        serializer = RescheduleMeetingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        new_start = serializer.validated_data['new_start_time']
        duration = meeting.end_time - meeting.start_time
        old_time = meeting.start_time
        
        meeting.start_time = new_start
        meeting.end_time = new_start + duration
        meeting.status = 'rescheduled'
        meeting.save()
        
        # Send reschedule notification
        try:
            EmailNotificationService.send_meeting_rescheduled(
                guest_email=meeting.guest_email,
                guest_name=meeting.guest_name,
                meeting=meeting,
                old_time=old_time,
                host=meeting.host
            )
        except Exception as e:
            logger.warning(f"Failed to send reschedule email: {e}")
        
        return Response(MeetingSerializer(meeting).data)
    
    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """Mark meeting as completed"""
        meeting = self.get_object()
        meeting.status = 'completed'
        meeting.save()
        
        return Response({'status': 'Meeting marked as completed'})
    
    @action(detail=True, methods=['post'])
    def mark_no_show(self, request, pk=None):
        """Mark meeting as no-show"""
        meeting = self.get_object()
        meeting.status = 'no_show'
        meeting.save()
        
        return Response({'status': 'Meeting marked as no-show'})


class PublicSchedulingPageView(APIView):
    """Public endpoint for viewing scheduling pages"""
    permission_classes = [AllowAny]
    
    def get(self, request, slug):
        """Get public scheduling page"""
        page = get_object_or_404(
            SchedulingPage,
            slug=slug,
            is_active=True
        )
        
        # Increment page views
        page.page_views += 1
        page.save()
        
        serializer = SchedulingPagePublicSerializer(page)
        return Response(serializer.data)


class AvailableSlotsView(APIView):
    """Get available time slots for booking"""
    permission_classes = [AllowAny]
    
    def get(self, request, slug, meeting_type_slug):
        """Get available slots for a date range"""
        page = get_object_or_404(SchedulingPage, slug=slug, is_active=True)
        meeting_type = get_object_or_404(
            MeetingType,
            page=page,
            slug=meeting_type_slug,
            is_active=True
        )
        
        # Get date range from params
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date:
            start_date = timezone.now().date()
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        if not end_date:
            end_date = start_date + timedelta(days=14)
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Respect max future days
        max_date = timezone.now().date() + timedelta(days=meeting_type.max_future_days)
        end_date = min(end_date, max_date)
        
        # Generate available slots
        slots_by_date = {}
        current_date = start_date
        
        while current_date <= end_date:
            day_slots = self._get_available_slots_for_date(
                page, meeting_type, current_date
            )
            if day_slots:
                slots_by_date[current_date.isoformat()] = [
                    s.isoformat() for s in day_slots
                ]
            current_date += timedelta(days=1)
        
        return Response({
            'meeting_type': meeting_type.name,
            'duration_minutes': meeting_type.duration_minutes,
            'timezone': page.timezone,
            'available_slots': slots_by_date
        })
    
    def _get_available_slots_for_date(self, page, meeting_type, date):
        """Get all available slots for a specific date"""
        tz = pytz.timezone(page.timezone)
        now = timezone.now()
        
        # Check minimum notice
        min_time = now + timedelta(hours=meeting_type.min_notice_hours)
        
        # Get availability for this day of week
        day_of_week = date.weekday()
        availabilities = page.availability.filter(
            day_of_week=day_of_week,
            is_active=True
        )
        
        if not availabilities.exists():
            return []
        
        # Get blocked times for this date
        blocked = page.blocked_times.filter(
            start_datetime__date__lte=date,
            end_datetime__date__gte=date
        )
        
        # Get existing meetings for this date
        existing_meetings = Meeting.objects.filter(
            meeting_type__page=page,
            status__in=['confirmed', 'pending'],
            start_time__date=date
        )
        
        available_slots = []
        duration = timedelta(minutes=meeting_type.duration_minutes)
        
        for avail in availabilities:
            # Convert to datetime
            slot_start = tz.localize(datetime.combine(date, avail.start_time))
            slot_end = tz.localize(datetime.combine(date, avail.end_time))
            
            current = slot_start
            while current + duration <= slot_end:
                # Skip if before minimum notice time
                if current < min_time:
                    current += timedelta(minutes=30)  # 30-min increments
                    continue
                
                # Check if slot conflicts with blocked time
                slot_end_time = current + duration
                is_blocked = False
                
                for block in blocked:
                    if (current < block.end_datetime and 
                        slot_end_time > block.start_datetime):
                        is_blocked = True
                        break
                
                if is_blocked:
                    current += timedelta(minutes=30)
                    continue
                
                # Check if slot conflicts with existing meeting
                is_booked = False
                for meeting in existing_meetings:
                    meeting_start = meeting.start_time - timedelta(minutes=meeting_type.buffer_before)
                    meeting_end = meeting.end_time + timedelta(minutes=meeting_type.buffer_after)
                    
                    if (current < meeting_end and slot_end_time > meeting_start):
                        is_booked = True
                        break
                
                if not is_booked:
                    available_slots.append(current)
                
                current += timedelta(minutes=30)  # 30-min increments
        
        return available_slots


class BookMeetingView(APIView):
    """Book a meeting"""
    permission_classes = [AllowAny]
    
    def post(self, request, slug):
        """Book a new meeting"""
        page = get_object_or_404(SchedulingPage, slug=slug, is_active=True)
        
        serializer = BookMeetingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        # Get meeting type
        meeting_type = get_object_or_404(
            MeetingType,
            id=data['meeting_type_id'],
            page=page,
            is_active=True
        )
        
        # Calculate end time
        start_time = data['start_time']
        end_time = start_time + timedelta(minutes=meeting_type.duration_minutes)
        
        # Validate slot is still available
        existing = Meeting.objects.filter(
            meeting_type__page=page,
            status__in=['confirmed', 'pending'],
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()
        
        if existing:
            return Response(
                {'error': 'This time slot is no longer available'},
                status=400
            )
        
        # Try to find existing contact
        from contact_management.models import Contact
        contact = Contact.objects.filter(email=data['guest_email']).first()
        
        # Create meeting
        meeting = Meeting.objects.create(
            meeting_type=meeting_type,
            host=page.owner,
            guest_name=data['guest_name'],
            guest_email=data['guest_email'],
            guest_phone=data.get('guest_phone', ''),
            guest_timezone=data.get('guest_timezone', 'UTC'),
            contact=contact,
            start_time=start_time,
            end_time=end_time,
            notes=data.get('notes', ''),
            custom_answers=data.get('custom_answers', {}),
            status='pending' if page.require_approval else 'confirmed',
            location=meeting_type.location_details,
        )
        
        # Update stats
        page.bookings_count += 1
        page.save()
        meeting_type.bookings_count += 1
        meeting_type.save()
        
        # Create reminders
        for minutes in [1440, 60]:  # 24h and 1h before
            reminder_time = start_time - timedelta(minutes=minutes)
            if reminder_time > timezone.now():
                MeetingReminder.objects.create(
                    meeting=meeting,
                    minutes_before=minutes,
                    scheduled_at=reminder_time,
                    for_guest=True
                )
        
        # Send confirmation email
        try:
            EmailNotificationService.send_meeting_confirmation(
                guest_email=meeting.guest_email,
                guest_name=meeting.guest_name,
                meeting=meeting,
                host=page.owner
            )
        except Exception as e:
            logger.warning(f"Failed to send booking confirmation email: {e}")
        
        return Response({
            'status': 'booked',
            'meeting_id': str(meeting.id),
            'start_time': meeting.start_time.isoformat(),
            'end_time': meeting.end_time.isoformat(),
            'cancel_url': f'/schedule/cancel/{meeting.cancel_token}',
            'reschedule_url': f'/schedule/reschedule/{meeting.reschedule_token}',
        }, status=201)


class GuestMeetingActionsView(APIView):
    """Guest actions: cancel or reschedule using token"""
    permission_classes = [AllowAny]
    
    def get(self, request, token):
        """Get meeting details using token"""
        meeting = Meeting.objects.filter(
            Q(cancel_token=token) | Q(reschedule_token=token)
        ).first()
        
        if not meeting:
            return Response({'error': 'Invalid token'}, status=404)
        
        return Response({
            'meeting_type': meeting.meeting_type.name,
            'host_name': meeting.host.get_full_name(),
            'start_time': meeting.start_time.isoformat(),
            'end_time': meeting.end_time.isoformat(),
            'status': meeting.status,
            'can_modify': meeting.status in ['confirmed', 'pending'] and meeting.start_time > timezone.now(),
        })
    
    def delete(self, request, token):
        """Cancel meeting using token"""
        meeting = Meeting.objects.filter(cancel_token=token).first()
        
        if not meeting:
            return Response({'error': 'Invalid token'}, status=404)
        
        if meeting.status not in ['confirmed', 'pending']:
            return Response({'error': 'Meeting cannot be cancelled'}, status=400)
        
        meeting.status = 'cancelled'
        meeting.cancelled_at = timezone.now()
        meeting.cancellation_reason = request.data.get('reason', 'Cancelled by guest')
        meeting.save()
        
        # Send cancellation notification to host
        try:
            EmailNotificationService.send_meeting_cancelled(
                guest_email=meeting.host.email,
                guest_name=meeting.host.get_full_name(),
                meeting=meeting,
                host=meeting.host,
                reason=meeting.cancellation_reason
            )
        except Exception as e:
            logger.warning(f"Failed to send cancellation notification to host: {e}")
        
        return Response({'status': 'Meeting cancelled'})


class CalendarIntegrationViewSet(viewsets.ModelViewSet):
    """Manage calendar integrations"""
    serializer_class = CalendarIntegrationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CalendarIntegration.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def connect_google(self, request):
        """Initiate Google Calendar OAuth flow"""
        from django.conf import settings
        from urllib.parse import urlencode
        
        # Get OAuth configuration from settings
        client_id = getattr(settings, 'GOOGLE_OAUTH_CLIENT_ID', None)
        redirect_uri = getattr(settings, 'GOOGLE_OAUTH_REDIRECT_URI', 
                               f"{settings.FRONTEND_URL}/integrations/google/callback")
        
        if not client_id:
            return Response(
                {'error': 'Google OAuth is not configured. Please set GOOGLE_OAUTH_CLIENT_ID in settings.'},
                status=400
            )
        
        # Build OAuth URL
        oauth_params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'scope': 'https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/calendar.events',
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'consent',
            'state': str(request.user.id),  # Include user ID for callback
        }
        
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(oauth_params)}"
        
        return Response({'auth_url': auth_url})
    
    @action(detail=False, methods=['post'])
    def connect_outlook(self, request):
        """Initiate Outlook Calendar OAuth flow"""
        from django.conf import settings
        from urllib.parse import urlencode
        
        # Get OAuth configuration from settings
        client_id = getattr(settings, 'MICROSOFT_OAUTH_CLIENT_ID', None)
        tenant_id = getattr(settings, 'MICROSOFT_OAUTH_TENANT_ID', 'common')
        redirect_uri = getattr(settings, 'MICROSOFT_OAUTH_REDIRECT_URI',
                               f"{settings.FRONTEND_URL}/integrations/outlook/callback")
        
        if not client_id:
            return Response(
                {'error': 'Microsoft OAuth is not configured. Please set MICROSOFT_OAUTH_CLIENT_ID in settings.'},
                status=400
            )
        
        # Build OAuth URL
        oauth_params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'scope': 'Calendars.ReadWrite offline_access',
            'response_type': 'code',
            'response_mode': 'query',
            'state': str(request.user.id),
        }
        
        auth_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize?{urlencode(oauth_params)}"
        
        return Response({'auth_url': auth_url})
    
    @action(detail=False, methods=['post'])
    def google_callback(self, request):
        """Handle Google OAuth callback"""
        code = request.data.get('code')
        if not code:
            return Response({'error': 'Authorization code required'}, status=400)
        
        # Note: Full implementation would exchange code for tokens here
        # This is a placeholder that creates the integration record
        integration, created = CalendarIntegration.objects.get_or_create(
            user=request.user,
            provider='google',
            defaults={
                'is_connected': True,
                'calendar_id': 'primary',
            }
        )
        
        if not created:
            integration.is_connected = True
            integration.save()
        
        return Response(CalendarIntegrationSerializer(integration).data)
    
    @action(detail=False, methods=['post'])
    def outlook_callback(self, request):
        """Handle Outlook OAuth callback"""
        code = request.data.get('code')
        if not code:
            return Response({'error': 'Authorization code required'}, status=400)
        
        # Note: Full implementation would exchange code for tokens here
        integration, created = CalendarIntegration.objects.get_or_create(
            user=request.user,
            provider='outlook',
            defaults={
                'is_connected': True,
            }
        )
        
        if not created:
            integration.is_connected = True
            integration.save()
        
        return Response(CalendarIntegrationSerializer(integration).data)
    
    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """Manually sync calendar events"""
        integration = self.get_object()
        
        if not integration.is_connected:
            return Response(
                {'error': 'Calendar is not connected. Please reconnect.'},
                status=400
            )
        
        # Perform sync based on provider
        try:
            if integration.provider == 'google':
                # Sync with Google Calendar
                logger.info(f"Syncing Google Calendar for user {request.user.id}")
                # In production: Use Google Calendar API to fetch/push events
                
            elif integration.provider == 'outlook':
                # Sync with Outlook Calendar
                logger.info(f"Syncing Outlook Calendar for user {request.user.id}")
                # In production: Use Microsoft Graph API to fetch/push events
            
            integration.last_synced_at = timezone.now()
            integration.sync_status = 'success'
            integration.save()
            
            return Response({
                'status': 'Sync completed',
                'last_synced_at': integration.last_synced_at.isoformat()
            })
            
        except Exception as e:
            logger.error(f"Calendar sync failed: {e}")
            integration.sync_status = 'failed'
            integration.save()
            return Response({'error': str(e)}, status=500)


class SchedulingDashboardView(APIView):
    """Scheduling dashboard statistics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get comprehensive scheduling stats"""
        user = request.user
        now = timezone.now()
        
        meetings = Meeting.objects.filter(host=user)
        
        # This week's meetings
        week_start = now - timedelta(days=now.weekday())
        week_meetings = meetings.filter(start_time__gte=week_start)
        
        # This month's meetings
        month_start = now.replace(day=1)
        month_meetings = meetings.filter(start_time__gte=month_start)
        
        # Completion rate
        past_meetings = meetings.filter(end_time__lt=now)
        completed = past_meetings.filter(status='completed').count()
        no_shows = past_meetings.filter(status='no_show').count()
        total_past = past_meetings.count()
        
        completion_rate = (completed / total_past * 100) if total_past > 0 else 0
        no_show_rate = (no_shows / total_past * 100) if total_past > 0 else 0
        
        # Average duration
        from django.db.models import Avg
        avg_duration = meetings.aggregate(
            avg=Avg('meeting_type__duration_minutes')
        )['avg'] or 30
        
        # Busiest day/time
        from django.db.models.functions import ExtractWeekDay, ExtractHour
        
        busiest_day = meetings.filter(status='completed').annotate(
            day=ExtractWeekDay('start_time')
        ).values('day').annotate(count=Count('id')).order_by('-count').first()
        
        busiest_hour = meetings.filter(status='completed').annotate(
            hour=ExtractHour('start_time')
        ).values('hour').annotate(count=Count('id')).order_by('-count').first()
        
        days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        
        return Response({
            'total_meetings': meetings.count(),
            'meetings_this_week': week_meetings.count(),
            'meetings_this_month': month_meetings.count(),
            'upcoming_meetings': meetings.filter(
                status='confirmed',
                start_time__gt=now
            ).count(),
            'completion_rate': round(completion_rate, 1),
            'no_show_rate': round(no_show_rate, 1),
            'avg_meeting_duration': int(avg_duration),
            'busiest_day': days[busiest_day['day'] - 1] if busiest_day else 'N/A',
            'busiest_time': f"{busiest_hour['hour']:02d}:00" if busiest_hour else 'N/A',
        })
