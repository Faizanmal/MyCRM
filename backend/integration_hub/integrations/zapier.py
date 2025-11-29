from typing import Dict, Any, List
import requests
from django.utils import timezone
from .base import BaseIntegrationClient


class ZapierClient(BaseIntegrationClient):
    """Zapier webhook integration client"""
    
    def __init__(self):
        super().__init__()
        self.base_url = 'https://hooks.zapier.com'
    
    def get_authorization_url(self, redirect_uri: str, state: str = None) -> str:
        """Zapier uses webhook URLs, not OAuth"""
        return ''
    
    def exchange_code(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Not applicable for Zapier"""
        return {}
    
    def refresh_access_token(self) -> Dict[str, Any]:
        """Not applicable for Zapier"""
        return {}
    
    def test_connection(self) -> bool:
        """Test webhook by sending test payload"""
        if not self.access_token:  # webhook URL stored as access_token
            return False
        
        try:
            response = requests.post(
                self.access_token,
                json={'test': True, 'event': 'connection_test'},
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False
            return False
    
    def send_webhook(self, event_type: str, data: Dict) -> bool:
        """Send data to Zapier webhook"""
        if not self.access_token:
            return False
        
        try:
            import requests
            payload = {
                'event_type': event_type,
                'data': data,
                'timestamp': str(timezone.now())
            }
            
            response = requests.post(
                self.access_token,
                json=payload,
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def sync_contacts(self, crm_contacts: List[Dict]) -> Dict[str, int]:
        """Send contacts via webhook"""
        synced = 0
        for contact in crm_contacts:
            if self.send_webhook('contact_created', contact):
                synced += 1
        return {'synced': synced}
    
    def fetch_contacts(self) -> List[Dict]:
        """Zapier is one-way, can't fetch"""
        return []
    
    def create_task(self, task_data: Dict) -> Dict:
        """Send task creation event"""
        success = self.send_webhook('task_created', task_data)
        return {'success': success}
    
    def send_notification(self, message: str, channel: str = None) -> bool:
        """Send notification event"""
        return self.send_webhook('notification', {
            'message': message,
            'channel': channel
        })
    
    def trigger_lead_created(self, lead_data: Dict) -> bool:
        """Trigger lead created zap"""
        return self.send_webhook('lead_created', lead_data)
    
    def trigger_deal_won(self, opportunity_data: Dict) -> bool:
        """Trigger deal won zap"""
        return self.send_webhook('deal_won', opportunity_data)
    
    def trigger_task_completed(self, task_data: Dict) -> bool:
        """Trigger task completed zap"""
        return self.send_webhook('task_completed', task_data)
