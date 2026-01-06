import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from multi_tenant.permissions import IsOrganizationAdmin, IsOrganizationMember

from .models import SSOLoginAttempt, SSOProvider, SSOSession
from .serializers import (
    SSOLoginAttemptSerializer,
    SSOProviderListSerializer,
    SSOProviderSerializer,
    SSOProviderStatisticsSerializer,
    SSOProviderTestSerializer,
    SSOSessionSerializer,
)
from .services import OAuth2Service, SAMLService, SSOAuthenticationService

logger = logging.getLogger(__name__)


class SSOProviderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing SSO providers.
    Only organization admins can create/update/delete providers.
    Members can view active providers.
    """
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    serializer_class = SSOProviderSerializer

    def get_queryset(self):
        user = self.request.user
        organization = getattr(user, 'organization', None)
        if not organization:
            return SSOProvider.objects.none()
        return SSOProvider.objects.filter(organization=organization)

    def get_serializer_class(self):
        if self.action == 'list':
            return SSOProviderListSerializer
        return SSOProviderSerializer

    def get_permissions(self):
        """Only admins can create/update/delete providers."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOrganizationAdmin()]
        return [IsAuthenticated(), IsOrganizationMember()]

    def perform_create(self, serializer):
        organization = self.request.user.organization
        serializer.save(
            organization=organization,
            created_by=self.request.user
        )

    @action(detail=True, methods=['post'])
    def test_connection(self, request, _pk=None):
        """
        Test SSO provider connection by generating auth URL.
        """
        provider = self.get_object()
        serializer = SSOProviderTestSerializer(
            data=request.data,
            context={'provider': provider}
        )
        serializer.is_valid(raise_exception=True)

        try:
            if provider.is_oauth2:
                oauth2_service = OAuth2Service(provider)
                auth_url, code_verifier = oauth2_service.generate_authorization_url()

                # Store code_verifier in session for callback
                request.session[f'oauth2_code_verifier_{provider.id}'] = code_verifier

                return Response({
                    'status': 'success',
                    'message': 'OAuth2 provider configuration is valid',
                    'authorization_url': auth_url,
                    'test_mode': True
                })

            elif provider.is_saml:
                saml_service = SAMLService(provider)
                authn_request = saml_service.generate_authn_request()

                return Response({
                    'status': 'success',
                    'message': 'SAML provider configuration is valid',
                    'saml_request': authn_request,
                    'sso_url': provider.sso_url,
                    'test_mode': True
                })

        except Exception as e:
            logger.error(f"SSO test failed for provider {provider.id}: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def statistics(self, request, _pk=None):
        """
        Get statistics for SSO provider.
        """
        provider = self.get_object()

        # Calculate statistics
        thirty_days_ago = timezone.now() - timedelta(days=30)

        attempts = SSOLoginAttempt.objects.filter(provider=provider)
        recent_attempts = attempts.filter(created_at__gte=thirty_days_ago)

        successful = recent_attempts.filter(status='success').count()
        failed = recent_attempts.filter(status__in=['failed', 'error']).count()
        unique_users = recent_attempts.filter(status='success').values('user').distinct().count()

        last_login = attempts.filter(status='success').order_by('-created_at').first()

        # Average logins per day
        if recent_attempts.exists():
            days = (timezone.now() - recent_attempts.earliest('created_at').created_at).days or 1
            avg_per_day = recent_attempts.count() / days
        else:
            avg_per_day = 0

        # Recent attempts for display
        recent_list = attempts.order_by('-created_at')[:10]

        data = {
            'total_logins': provider.total_logins,
            'successful_logins': successful,
            'failed_logins': failed,
            'unique_users': unique_users,
            'last_login_at': last_login.created_at if last_login else None,
            'avg_logins_per_day': round(avg_per_day, 2),
            'recent_attempts': SSOLoginAttemptSerializer(recent_list, many=True).data
        }

        serializer = SSOProviderStatisticsSerializer(data)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def activate(self, request, _pk=None):
        """
        Activate SSO provider (set status to active).
        """
        provider = self.get_object()
        provider.status = 'active'
        provider.save()

        return Response({
            'status': 'success',
            'message': f'Provider {provider.provider_name} activated'
        })

    @action(detail=True, methods=['post'])
    def deactivate(self, request, _pk=None):
        """
        Deactivate SSO provider (set status to inactive).
        """
        provider = self.get_object()
        provider.status = 'inactive'
        provider.save()

        # End all active sessions
        SSOSession.objects.filter(
            provider=provider,
            is_active=True
        ).update(is_active=False, ended_at=timezone.now())

        return Response({
            'status': 'success',
            'message': f'Provider {provider.provider_name} deactivated'
        })

    @action(detail=False, methods=['get'])
    def available_types(self, request):
        """
        Get list of available SSO provider types.
        """
        types = [
            {
                'value': choice[0],
                'label': choice[1],
                'type': 'oauth2' if choice[0].startswith('oauth2_') else 'saml'
            }
            for choice in SSOProvider.PROVIDER_TYPE_CHOICES
        ]

        return Response(types)


class SSOSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing SSO sessions.
    Organization admins can view all sessions.
    Regular users can only view their own sessions.
    """
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    serializer_class = SSOSessionSerializer

    def get_queryset(self):
        user = self.request.user
        organization = getattr(user, 'organization', None)
        if not organization:
            return SSOSession.objects.none()

        # Admins see all sessions, users see only their own
        queryset = SSOSession.objects.filter(provider__organization=organization)

        if not user.is_staff and not self.request.user.organizationmember_set.filter(
            role__in=['owner', 'admin']
        ).exists():
            queryset = queryset.filter(user=user)

        return queryset.order_by('-created_at')

    @action(detail=True, methods=['post'])
    def end_session(self, request, _pk=None):
        """
        End an SSO session (logout).
        """
        session = self.get_object()

        # Users can only end their own sessions, admins can end any
        if session.user != request.user and not request.user.is_staff:
            return Response({
                'error': 'You can only end your own sessions'
            }, status=status.HTTP_403_FORBIDDEN)

        SSOAuthenticationService.end_session(session)

        return Response({
            'status': 'success',
            'message': 'Session ended'
        })

    @action(detail=False, methods=['get'])
    def my_sessions(self, request):
        """
        Get all active sessions for current user.
        """
        sessions = SSOSession.objects.filter(
            user=request.user,
            is_active=True
        ).order_by('-created_at')

        serializer = self.get_serializer(sessions, many=True)
        return Response(serializer.data)


class SSOLoginAttemptViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing SSO login attempts (audit log).
    Only organization admins can view attempts.
    """
    permission_classes = [IsAuthenticated, IsOrganizationAdmin]
    serializer_class = SSOLoginAttemptSerializer

    def get_queryset(self):
        user = self.request.user
        organization = getattr(user, 'organization', None)
        if not organization:
            return SSOLoginAttempt.objects.none()

        queryset = SSOLoginAttempt.objects.filter(
            provider__organization=organization
        ).order_by('-created_at')

        # Filter by provider if specified
        provider_id = self.request.query_params.get('provider')
        if provider_id:
            queryset = queryset.filter(provider_id=provider_id)

        # Filter by status if specified
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset


class SSOCallbackView(viewsets.ViewSet):
    """
    Handle OAuth2 callbacks from SSO providers.
    This is a public endpoint that receives auth codes.
    """
    permission_classes = []  # Public endpoint

    @action(detail=True, methods=['get', 'post'])
    def callback(self, request, _pk=None):
        """
        Handle OAuth2 callback after user authorization.
        """
        provider = get_object_or_404(SSOProvider, id=pk)

        if not provider.is_oauth2:
            return Response({
                'error': 'This endpoint is only for OAuth2 providers'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get authorization code from query params
        code = request.GET.get('code')
        error = request.GET.get('error')

        if error:
            logger.error(f"OAuth2 error from provider {provider.id}: {error}")
            return HttpResponseRedirect(
                f"{settings.FRONTEND_URL}/sso-error?error={error}"
            )

        if not code:
            return Response({
                'error': 'Authorization code not provided'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get code_verifier from session
            code_verifier = request.session.get(f'oauth2_code_verifier_{provider.id}')
            if not code_verifier:
                raise ValueError("Code verifier not found in session")

            # Exchange code for token
            oauth2_service = OAuth2Service(provider)
            token_data = oauth2_service.exchange_code_for_token(code, code_verifier)

            # Get user info
            access_token = token_data.get('access_token')
            user_info = oauth2_service.get_user_info(access_token)

            # Map user attributes
            user_data = oauth2_service.map_user_attributes(user_info)

            # Authenticate or create user
            user, created = SSOAuthenticationService.authenticate_user(
                provider=provider,
                user_data=user_data,
                request_meta=request.META
            )

            # Create session
            session_data = {
                'access_token': access_token,
                'refresh_token': token_data.get('refresh_token'),
                'expires_in': token_data.get('expires_in'),
            }
            SSOAuthenticationService.create_session(
                provider=provider,
                user=user,
                session_data=session_data,
                request_meta=request.META
            )

            # Log user in
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            # Redirect to frontend
            redirect_url = f"{settings.FRONTEND_URL}/dashboard?sso=success&new_user={created}"
            return HttpResponseRedirect(redirect_url)

        except Exception as e:
            logger.error(f"SSO authentication failed: {str(e)}")

            # Log failed attempt
            SSOLoginAttempt.objects.create(
                provider=provider,
                email=user_data.get('email', 'unknown'),
                status='error',
                error_message=str(e),
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
            )

            return HttpResponseRedirect(
                f"{settings.FRONTEND_URL}/sso-error?error=authentication_failed"
            )
