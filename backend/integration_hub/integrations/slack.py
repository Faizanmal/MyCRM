from typing import Any

import requests
from django.conf import settings

from .base import BaseIntegrationClient


class SlackClient(BaseIntegrationClient):
    """Slack integration client"""

    def __init__(self):
        super().__init__()
        self.base_url = 'https://slack.com/api'
        self.client_id = getattr(settings, 'SLACK_CLIENT_ID', '')
        self.client_secret = getattr(settings, 'SLACK_CLIENT_SECRET', '')

    def get_authorization_url(self, redirect_uri: str, state: str = None) -> str:
        """Get Slack OAuth URL"""
        scopes = [
            'channels:read',
            'chat:write',
            'users:read',
            'users:read.email',
        ]

        params = {
            'client_id': self.client_id,
            'redirect_uri': redirect_uri,
            'scope': ','.join(scopes),
        }
        if state:
            params['state'] = state

        query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        return f'https://slack.com/oauth/v2/authorize?{query_string}'

    def exchange_code(self, code: str, redirect_uri: str) -> dict[str, Any]:
        """Exchange code for access token"""
        response = requests.post(
            'https://slack.com/api/oauth.v2.access',
            data={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'redirect_uri': redirect_uri
            }
        )
        data = response.json()

        if data.get('ok'):
            return {
                'access_token': data['access_token'],
                'team_id': data['team']['id'],
                'team_name': data['team']['name'],
            }
        raise Exception(f"Failed to exchange code: {data.get('error')}")

    def refresh_access_token(self) -> dict[str, Any]:
        """Slack tokens don't expire"""
        return {'access_token': self.access_token}

    def test_connection(self) -> bool:
        """Test Slack connection"""
        try:
            response = self.get('auth.test')
            return response.get('ok', False)
        except Exception:
            return False

    def send_notification(self, message: str, channel: str = None) -> bool:
        """Send message to Slack channel"""
        try:
            data = {
                'text': message,
                'channel': channel or '#general'
            }
            response = self.post('chat.postMessage', data)
            return response.get('ok', False)
        except Exception:
            return False

    def sync_contacts(self, crm_contacts: list[dict]) -> dict[str, int]:
        """Slack doesn't have contact sync - notification only"""
        return {'synced': 0}

    def fetch_contacts(self) -> list[dict]:
        """Fetch Slack users"""
        try:
            response = self.get('users.list')
            if response.get('ok'):
                users = response.get('members', [])
                return [
                    {
                        'id': user['id'],
                        'name': user.get('real_name', user['name']),
                        'email': user.get('profile', {}).get('email'),
                        'is_active': not user.get('deleted', False)
                    }
                    for user in users
                    if not user.get('is_bot', False)
                ]
            return []
        except Exception:
            return []

    def create_task(self, task_data: dict) -> dict:
        """Create task reminder in Slack"""
        try:
            message = f"Task: {task_data.get('title')}\nDue: {task_data.get('due_date')}"
            self.send_notification(message, task_data.get('channel'))
            return {'success': True}
        except Exception:
            return {'success': False}

    def post_lead_notification(self, lead_data: dict, channel: str = '#sales'):
        """Post new lead notification"""
        message = f"""
🎯 *New Lead Assigned*
*Name:* {lead_data.get('first_name')} {lead_data.get('last_name')}
*Company:* {lead_data.get('company_name')}
*Email:* {lead_data.get('email')}
*Score:* {lead_data.get('lead_score', 'N/A')}
        """.strip()
        return self.send_notification(message, channel)

    def post_deal_won(self, opportunity_data: dict, channel: str = '#sales'):
        """Post deal won celebration"""
        message = f"""
🎉 *Deal Won!*
*Deal:* {opportunity_data.get('name')}
*Amount:* ${opportunity_data.get('amount', 0):,.2f}
*Owner:* {opportunity_data.get('owner_name')}
        """.strip()
        return self.send_notification(message, channel)
