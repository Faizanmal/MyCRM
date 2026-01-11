"""
Customer Portal Authentication
"""

from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import PortalSession


class CustomerTokenAuthentication(BaseAuthentication):
    """
    Custom authentication for customer portal using session tokens.
    """
    
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        try:
            session = PortalSession.objects.select_related('customer').get(
                session_token=token,
                is_active=True
            )
        except PortalSession.DoesNotExist:
            raise AuthenticationFailed('Invalid or expired token')
        
        if session.is_expired():
            session.is_active = False
            session.save()
            raise AuthenticationFailed('Token has expired')
        
        if not session.customer.is_active:
            raise AuthenticationFailed('Customer account is inactive')
        
        if session.customer.is_locked():
            raise AuthenticationFailed('Customer account is locked')
        
        # Update last activity
        session.last_activity = timezone.now()
        session.save(update_fields=['last_activity'])
        
        # Attach customer and session to request
        request.customer = session.customer
        request.portal_session = session
        
        return (session.customer, session)

    def authenticate_header(self, request):
        return 'Bearer'
