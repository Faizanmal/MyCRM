"""
Authentication Views
JWT authentication, registration, and account management
"""

from datetime import timedelta

from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class RegisterView(APIView):
    """
    User registration endpoint
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        data = request.data
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return Response(
                    {'error': f'{field} is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Check if email already exists
        if User.objects.filter(email=data['email']).exists():
            return Response(
                {'error': 'Email already registered'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if username exists
        username = data.get('username', data['email'])
        if User.objects.filter(username=username).exists():
            username = f"{data['email'].split('@')[0]}_{timezone.now().timestamp()}"
        
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
            )
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            # Create default preferences (signals should handle this)
            from .settings_models import UserPreference, NotificationPreference
            UserPreference.objects.get_or_create(user=user)
            NotificationPreference.objects.get_or_create(user=user)
            
            # Log registration
            from .models import AuditLog
            AuditLog.objects.create(
                user=user,
                action='user_registered',
                resource=f'user:{user.id}',
                ip_address=self._get_client_ip(request),
                metadata={'email': user.email},
            )
            
            logger.info(f"New user registered: {user.email}")
            
            return Response({
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'username': user.username,
                },
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                },
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            return Response(
                {'error': 'Registration failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LoginView(APIView):
    """
    User login endpoint with JWT tokens
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'Email and password required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Try to find user by email
        try:
            user = User.objects.get(email=email)
            username = user.username
        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Authenticate
        user = authenticate(username=username, password=password)
        
        if user is None:
            # Log failed attempt
            from .models import AuditLog
            AuditLog.objects.create(
                action='login_failed',
                resource=f'email:{email}',
                ip_address=self._get_client_ip(request),
                risk_level='medium',
                metadata={'email': email},
            )
            
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_active:
            return Response(
                {'error': 'Account is disabled'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # Log successful login
        from .models import AuditLog
        AuditLog.objects.create(
            user=user,
            action='login_success',
            resource=f'user:{user.id}',
            ip_address=self._get_client_ip(request),
            metadata={'method': 'password'},
        )
        
        # Get user permissions
        from .rbac_middleware import get_user_permissions
        permissions = list(get_user_permissions(user))
        
        return Response({
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'is_staff': user.is_staff,
            },
            'permissions': permissions,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
        })
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LogoutView(APIView):
    """
    User logout - blacklist refresh token
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Log logout
            from .models import AuditLog
            AuditLog.objects.create(
                user=request.user,
                action='logout',
                resource=f'user:{request.user.id}',
                ip_address=self._get_client_ip(request),
            )
            
            return Response({'status': 'success'})
        except Exception as e:
            return Response({'status': 'success'})  # Still return success
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserProfileView(APIView):
    """
    Get/Update current user profile
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get user roles and permissions
        from .rbac_middleware import get_user_permissions
        from .settings_models import UserRoleAssignment
        
        permissions = list(get_user_permissions(user))
        roles = list(UserRoleAssignment.objects.filter(user=user).values_list('role__name', flat=True))
        
        return Response({
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.get_full_name(),
            'date_joined': user.date_joined,
            'last_login': user.last_login,
            'is_staff': user.is_staff,
            'is_active': user.is_active,
            'roles': roles,
            'permissions': permissions,
        })
    
    def patch(self, request):
        user = request.user
        data = request.data
        
        allowed_fields = ['first_name', 'last_name']
        
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        user.save()
        
        return Response({
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.get_full_name(),
        })


class ChangePasswordView(APIView):
    """
    Change user password
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        
        if not current_password or not new_password:
            return Response(
                {'error': 'Current and new password required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not user.check_password(current_password):
            return Response(
                {'error': 'Current password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(new_password) < 8:
            return Response(
                {'error': 'Password must be at least 8 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        # Log password change
        from .models import AuditLog
        AuditLog.objects.create(
            user=user,
            action='password_changed',
            resource=f'user:{user.id}',
            ip_address=self._get_client_ip(request),
            risk_level='high',
        )
        
        return Response({'status': 'success', 'message': 'Password changed successfully'})
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class PasswordResetRequestView(APIView):
    """
    Request password reset email
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
            
            # Generate token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Send reset email
            reset_url = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"
            
            from .notification_service import notification_service
            notification_service.send(
                user=user,
                notification_type='security_alert',
                title='Password Reset Request',
                message='A password reset was requested for your account.',
                context={
                    'alert_type': 'Password Reset',
                    'timestamp': timezone.now(),
                    'reset_url': reset_url,
                },
                action_url=reset_url,
                priority='high',
            )
            
            logger.info(f"Password reset requested for: {email}")
            
        except User.DoesNotExist:
            # Don't reveal if email exists
            pass
        
        return Response({
            'status': 'success',
            'message': 'If the email exists, a reset link has been sent.',
        })


class PasswordResetConfirmView(APIView):
    """
    Confirm password reset with token
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        
        if not all([uid, token, new_password]):
            return Response(
                {'error': 'Missing required fields'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, User.DoesNotExist):
            return Response(
                {'error': 'Invalid reset link'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not default_token_generator.check_token(user, token):
            return Response(
                {'error': 'Invalid or expired token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(new_password) < 8:
            return Response(
                {'error': 'Password must be at least 8 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        # Log password reset
        from .models import AuditLog
        AuditLog.objects.create(
            user=user,
            action='password_reset_completed',
            resource=f'user:{user.id}',
            ip_address=self._get_client_ip(request),
            risk_level='high',
        )
        
        logger.info(f"Password reset completed for: {user.email}")
        
        return Response({
            'status': 'success',
            'message': 'Password has been reset successfully',
        })
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RefreshTokenView(APIView):
    """
    Refresh JWT access token
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response(
                {'error': 'Refresh token required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            refresh = RefreshToken(refresh_token)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            })
        except Exception as e:
            return Response(
                {'error': 'Invalid refresh token'},
                status=status.HTTP_401_UNAUTHORIZED
            )
