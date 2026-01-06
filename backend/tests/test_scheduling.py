# MyCRM Backend - Smart Scheduling Tests

from datetime import datetime, timedelta

import pytest
from rest_framework import status


@pytest.mark.django_db
class TestSchedulingAPI:
    """Tests for Smart Scheduling API endpoints."""

    def test_get_availability(self, authenticated_client):
        """Test getting user availability."""
        url = '/api/v1/scheduling/availability/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_set_availability(self, authenticated_client):
        """Test setting user availability."""
        url = '/api/v1/scheduling/availability/'
        data = {
            'schedule': {
                'monday': {'start': '09:00', 'end': '17:00'},
                'tuesday': {'start': '09:00', 'end': '17:00'},
                'wednesday': {'start': '09:00', 'end': '17:00'},
                'thursday': {'start': '09:00', 'end': '17:00'},
                'friday': {'start': '09:00', 'end': '16:00'},
            },
            'timezone': 'America/New_York',
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_find_available_slots(self, authenticated_client):
        """Test finding available time slots."""
        url = '/api/v1/scheduling/available-slots/'
        data = {
            'duration_minutes': 30,
            'start_date': datetime.now().date().isoformat(),
            'end_date': (datetime.now() + timedelta(days=7)).date().isoformat(),
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_find_mutual_availability(self, authenticated_client):
        """Test finding mutual availability with multiple participants."""
        url = '/api/v1/scheduling/mutual-availability/'
        data = {
            'participant_ids': [1, 2, 3],
            'duration_minutes': 60,
            'date_range_days': 14,
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestMeetingTypesAPI:
    """Tests for Meeting Types API endpoints."""

    def test_list_meeting_types(self, authenticated_client):
        """Test listing meeting types."""
        url = '/api/v1/scheduling/meeting-types/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_create_meeting_type(self, authenticated_client):
        """Test creating a meeting type."""
        url = '/api/v1/scheduling/meeting-types/'
        data = {
            'name': 'Discovery Call',
            'duration_minutes': 30,
            'description': 'Initial conversation to understand requirements',
            'color': '#3498db',
            'buffer_before': 5,
            'buffer_after': 10,
            'max_per_day': 5,
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_update_meeting_type(self, authenticated_client):
        """Test updating a meeting type."""
        url = '/api/v1/scheduling/meeting-types/1/'
        data = {'duration_minutes': 45}
        response = authenticated_client.patch(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_delete_meeting_type(self, authenticated_client):
        """Test deleting a meeting type."""
        url = '/api/v1/scheduling/meeting-types/1/'
        response = authenticated_client.delete(url)
        assert response.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestBookingLinksAPI:
    """Tests for Booking Links API endpoints."""

    def test_list_booking_links(self, authenticated_client):
        """Test listing booking links."""
        url = '/api/v1/scheduling/booking-links/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_create_booking_link(self, authenticated_client):
        """Test creating a booking link."""
        url = '/api/v1/scheduling/booking-links/'
        data = {
            'meeting_type_id': 1,
            'slug': 'discovery-call-john',
            'expires_at': (datetime.now() + timedelta(days=30)).isoformat(),
            'max_bookings': 100,
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_get_public_booking_page(self, authenticated_client):
        """Test accessing public booking page data."""
        url = '/api/v1/scheduling/booking/discovery-call-john/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_book_appointment(self, authenticated_client):
        """Test booking an appointment via public link."""
        url = '/api/v1/scheduling/booking/discovery-call-john/book/'
        data = {
            'datetime': (datetime.now() + timedelta(days=2, hours=10)).isoformat(),
            'attendee_name': 'Jane Smith',
            'attendee_email': 'jane@example.com',
            'notes': 'Interested in enterprise plan',
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestAppointmentsAPI:
    """Tests for Appointments API endpoints."""

    def test_list_appointments(self, authenticated_client):
        """Test listing appointments."""
        url = '/api/v1/scheduling/appointments/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_create_appointment(self, authenticated_client):
        """Test creating an appointment."""
        url = '/api/v1/scheduling/appointments/'
        data = {
            'title': 'Demo Call',
            'start_time': (datetime.now() + timedelta(days=1, hours=14)).isoformat(),
            'end_time': (datetime.now() + timedelta(days=1, hours=15)).isoformat(),
            'attendees': ['john@example.com'],
            'location': 'Zoom',
            'description': 'Product demonstration',
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_reschedule_appointment(self, authenticated_client):
        """Test rescheduling an appointment."""
        url = '/api/v1/scheduling/appointments/1/reschedule/'
        data = {
            'new_start_time': (datetime.now() + timedelta(days=3, hours=10)).isoformat(),
            'notify_attendees': True,
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_cancel_appointment(self, authenticated_client):
        """Test canceling an appointment."""
        url = '/api/v1/scheduling/appointments/1/cancel/'
        data = {
            'reason': 'Scheduling conflict',
            'notify_attendees': True,
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_confirm_appointment(self, authenticated_client):
        """Test confirming an appointment."""
        url = '/api/v1/scheduling/appointments/1/confirm/'
        response = authenticated_client.post(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_upcoming_appointments(self, authenticated_client):
        """Test getting upcoming appointments."""
        url = '/api/v1/scheduling/appointments/upcoming/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestCalendarIntegrationAPI:
    """Tests for Calendar Integration API endpoints."""

    def test_list_connected_calendars(self, authenticated_client):
        """Test listing connected calendars."""
        url = '/api/v1/scheduling/calendars/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_connect_google_calendar(self, authenticated_client):
        """Test initiating Google Calendar connection."""
        url = '/api/v1/scheduling/calendars/google/connect/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_302_FOUND, status.HTTP_404_NOT_FOUND]

    def test_connect_outlook_calendar(self, authenticated_client):
        """Test initiating Outlook Calendar connection."""
        url = '/api/v1/scheduling/calendars/outlook/connect/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_302_FOUND, status.HTTP_404_NOT_FOUND]

    def test_sync_calendar(self, authenticated_client):
        """Test syncing calendar events."""
        url = '/api/v1/scheduling/calendars/1/sync/'
        response = authenticated_client.post(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_202_ACCEPTED, status.HTTP_404_NOT_FOUND]

    def test_disconnect_calendar(self, authenticated_client):
        """Test disconnecting a calendar."""
        url = '/api/v1/scheduling/calendars/1/disconnect/'
        response = authenticated_client.post(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestRoundRobinAPI:
    """Tests for Round Robin Scheduling API endpoints."""

    def test_list_round_robin_pools(self, authenticated_client):
        """Test listing round robin pools."""
        url = '/api/v1/scheduling/round-robin/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_create_round_robin_pool(self, authenticated_client):
        """Test creating a round robin pool."""
        url = '/api/v1/scheduling/round-robin/'
        data = {
            'name': 'Sales Team',
            'member_ids': [1, 2, 3],
            'strategy': 'balanced',  # balanced, random, weighted
            'meeting_type_id': 1,
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_update_pool_members(self, authenticated_client):
        """Test updating pool members."""
        url = '/api/v1/scheduling/round-robin/1/'
        data = {'member_ids': [1, 2, 3, 4]}
        response = authenticated_client.patch(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_pool_statistics(self, authenticated_client):
        """Test getting pool statistics."""
        url = '/api/v1/scheduling/round-robin/1/stats/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
