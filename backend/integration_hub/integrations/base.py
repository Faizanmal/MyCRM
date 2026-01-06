from abc import ABC, abstractmethod
from typing import Any

import requests


class BaseIntegrationClient(ABC):
    """Base class for all integration clients"""

    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.base_url = None

    def set_credentials(self, access_token: str, refresh_token: str = None):
        """Set authentication credentials"""
        self.access_token = access_token
        self.refresh_token = refresh_token

    @abstractmethod
    def get_authorization_url(self, redirect_uri: str, state: str = None) -> str:
        """Get OAuth authorization URL"""
        pass

    @abstractmethod
    def exchange_code(self, code: str, redirect_uri: str) -> dict[str, Any]:
        """Exchange authorization code for access token"""
        pass

    @abstractmethod
    def refresh_access_token(self) -> dict[str, Any]:
        """Refresh expired access token"""
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """Test if connection is working"""
        pass

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: dict = None,
        params: dict = None,
        headers: dict = None
    ) -> requests.Response:
        """Make HTTP request to API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        request_headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        if headers:
            request_headers.update(headers)

        response = requests.request(
            method=method,
            url=url,
            json=data,
            params=params,
            headers=request_headers
        )
        response.raise_for_status()
        return response

    def get(self, endpoint: str, params: dict = None) -> dict:
        """GET request"""
        response = self._make_request('GET', endpoint, params=params)
        return response.json()

    def post(self, endpoint: str, data: dict = None) -> dict:
        """POST request"""
        response = self._make_request('POST', endpoint, data=data)
        return response.json()

    def put(self, endpoint: str, data: dict = None) -> dict:
        """PUT request"""
        response = self._make_request('PUT', endpoint, data=data)
        return response.json()

    def delete(self, endpoint: str) -> dict:
        """DELETE request"""
        response = self._make_request('DELETE', endpoint)
        return response.json() if response.content else {}

    # Common CRM operations
    @abstractmethod
    def sync_contacts(self, crm_contacts: list[dict]) -> dict[str, int]:
        """Sync contacts to external system"""
        pass

    @abstractmethod
    def fetch_contacts(self) -> list[dict]:
        """Fetch contacts from external system"""
        pass

    @abstractmethod
    def create_task(self, task_data: dict) -> dict:
        """Create task in external system"""
        pass

    @abstractmethod
    def send_notification(self, message: str, channel: str = None) -> bool:
        """Send notification"""
        pass
