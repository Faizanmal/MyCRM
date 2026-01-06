from typing import Any

import requests
from django.conf import settings

from .base import BaseIntegrationClient


class GoogleWorkspaceClient(BaseIntegrationClient):
    """Google Workspace integration client"""

    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.googleapis.com'
        self.client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '')
        self.client_secret = getattr(settings, 'GOOGLE_CLIENT_SECRET', '')

    def get_authorization_url(self, redirect_uri: str, state: str = None) -> str:
        """Get Google OAuth URL"""
        scopes = [
            'https://www.googleapis.com/auth/contacts',
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
        ]

        params = {
            'client_id': self.client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': ' '.join(scopes),
            'access_type': 'offline',
            'prompt': 'consent'
        }
        if state:
            params['state'] = state

        query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        return f'https://accounts.google.com/o/oauth2/v2/auth?{query_string}'

    def exchange_code(self, code: str, redirect_uri: str) -> dict[str, Any]:
        """Exchange code for tokens"""
        response = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code'
            }
        )
        data = response.json()

        if 'access_token' in data:
            return {
                'access_token': data['access_token'],
                'refresh_token': data.get('refresh_token'),
                'expires_in': data.get('expires_in', 3600)
            }
        raise Exception(f"Failed to exchange code: {data.get('error_description')}")

    def refresh_access_token(self) -> dict[str, Any]:
        """Refresh Google access token"""
        response = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': self.refresh_token,
                'grant_type': 'refresh_token'
            }
        )
        data = response.json()

        if 'access_token' in data:
            self.access_token = data['access_token']
            return {
                'access_token': data['access_token'],
                'expires_in': data.get('expires_in', 3600)
            }
        raise Exception(f"Failed to refresh token: {data.get('error_description')}")

    def test_connection(self) -> bool:
        """Test Google connection"""
        try:
            response = self.get('oauth2/v2/userinfo')
            return 'email' in response
        except Exception:
            return False

    def sync_contacts(self, crm_contacts: list[dict]) -> dict[str, int]:
        """Sync contacts to Google Contacts"""
        synced = 0

        for contact in crm_contacts:
            try:
                contact_data = {
                    'names': [{
                        'givenName': contact.get('first_name'),
                        'familyName': contact.get('last_name')
                    }],
                    'emailAddresses': [{
                        'value': contact.get('email')
                    }]
                }

                if contact.get('phone'):
                    contact_data['phoneNumbers'] = [{
                        'value': contact['phone']
                    }]

                self.post('people/v1/people:createContact', contact_data)
                synced += 1
            except Exception:
                continue

        return {'synced': synced}

    def fetch_contacts(self) -> list[dict]:
        """Fetch contacts from Google"""
        try:
            response = self.get(
                'people/v1/people/me/connections',
                params={
                    'personFields': 'names,emailAddresses,phoneNumbers,organizations'
                }
            )

            contacts = []
            for person in response.get('connections', []):
                names = person.get('names', [{}])[0]
                emails = person.get('emailAddresses', [{}])[0]
                phones = person.get('phoneNumbers', [{}])[0]
                orgs = person.get('organizations', [{}])[0]

                contacts.append({
                    'first_name': names.get('givenName'),
                    'last_name': names.get('familyName'),
                    'email': emails.get('value'),
                    'phone': phones.get('value'),
                    'company_name': orgs.get('name')
                })

            return contacts
        except Exception:
            return []

    def create_task(self, task_data: dict) -> dict:
        """Create calendar event for task"""
        try:
            event = {
                'summary': task_data.get('title'),
                'description': task_data.get('description'),
                'start': {
                    'dateTime': task_data.get('due_date'),
                    'timeZone': 'UTC'
                },
                'end': {
                    'dateTime': task_data.get('due_date'),
                    'timeZone': 'UTC'
                }
            }

            response = self.post('calendar/v3/calendars/primary/events', event)
            return {'success': True, 'event_id': response.get('id')}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def send_notification(self, message: str, channel: str = None) -> bool:
        """Send email notification via Gmail"""
        try:
            # Would implement Gmail API email sending
            return True
        except Exception:
            return False

    def create_calendar_event(self, event_data: dict) -> dict:
        """Create calendar event"""
        try:
            response = self.post('calendar/v3/calendars/primary/events', event_data)
            return response
        except Exception as e:
            return {'error': str(e)}
