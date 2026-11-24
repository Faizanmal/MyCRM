import base64
import io

import pyotp
import qrcode
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import permissions, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .authentication import clear_auth_cookies, set_auth_cookies
from .models import AuditLog, Permission, RolePermission, UserProfile
from .serializers import (
    AuditLogSerializer,
    LoginSerializer,
    PasswordChangeSerializer,
    PermissionSerializer,
    RolePermissionSerializer,
    TwoFactorVerifySerializer,
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
)

User = get_user_model()


@method_decorator(ratelimit(key='ip', rate='10/h', block=False), name='post')
class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token view with 2FA gating and secure HttpOnly cookie support"""

    def post(self, request, *_args, **_kwargs):
        if getattr(request, 'limited', False):
            return Response(
                {'error': 'Too many requests. Please try again later.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        profile, _ = UserProfile.objects.get_or_create(user=user)
        is_admin = (
            getattr(user, 'role', None) == 'admin' or
            getattr(user, 'is_staff', False) or
            getattr(user, 'is_superuser', False)
        )
        two_factor_enabled = getattr(user, 'two_factor_enabled', False) or profile.two_factor_enabled

        if is_admin and not two_factor_enabled:
            return Response(
                {'error': 'Admin accounts must have 2FA enabled. Please set up 2FA before logging in.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # 2FA Gate: Issue a restricted ephemeral 2FA challenge token
        if two_factor_enabled:
            refresh = RefreshToken.for_user(user)
            refresh['2fa_pending'] = True
            return Response({
                'message': '2FA verification required',
                'temp_token': str(refresh.access_token),
                'user_id': user.id
            }, status=status.HTTP_200_OK)

        # Generate full JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        # Audit log
        AuditLog.objects.create(
            user=user,
            action='login',
            model_name='User',
            object_id=str(user.id),
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        resp = Response({
            'access': str(access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        })
        set_auth_cookies(resp, str(access_token), str(refresh))
        return resp

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        return ip


class CustomTokenRefreshView(TokenRefreshView):
    """
    Token refresh endpoint that accepts refresh token from body or HttpOnly cookie,
    rotates refresh token, blacklists previous token, and updates HttpOnly cookies.
    """

    def post(self, request, *args, **kwargs):
        # Fall back to HttpOnly cookie if refresh not in body
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        if not data.get('refresh'):
            cookie_refresh = request.COOKIES.get('refresh_token')
            if cookie_refresh:
                data['refresh'] = cookie_refresh

        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        token_data = serializer.validated_data
        access = token_data.get('access')
        refresh = token_data.get('refresh')

        resp = Response(token_data, status=status.HTTP_200_OK)
        set_auth_cookies(resp, access, refresh)
        return resp


class LogoutView(views.APIView):
    """
    Immediate token revocation & multi-tab logout:
    Blacklists refresh token and clears HttpOnly session cookies.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh') or request.COOKIES.get('refresh_token')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass

        resp = Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
        clear_auth_cookies(resp)
        return resp


class TwoFactorLoginVerifyView(views.APIView):
    """
    Validates TOTP token against 2FA challenge token to complete login.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user_id = request.data.get('user_id')
        temp_token = request.data.get('temp_token')
        code = request.data.get('code') or request.data.get('token')

        if not (user_id and code and temp_token):
            return Response(
                {'error': 'user_id, temp_token, and 6-digit code are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            UntypedToken(temp_token)
            user = User.objects.get(id=user_id)
        except Exception:
            return Response({'error': 'Invalid or expired 2FA temporary token.'}, status=status.HTTP_401_UNAUTHORIZED)

        profile, _ = UserProfile.objects.get_or_create(user=user)
        secret = getattr(user, 'two_factor_secret', None) or profile.two_factor_secret
        if not secret:
            return Response({'error': '2FA is not configured for this user.'}, status=status.HTTP_400_BAD_REQUEST)

        totp = pyotp.TOTP(secret)
        if not totp.verify(str(code), valid_window=1):
            return Response({'error': 'Invalid 2FA verification code.'}, status=status.HTTP_400_BAD_REQUEST)

        # Success: Issue full authentication tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        resp = Response({
            'access': str(access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        })
        set_auth_cookies(resp, str(access_token), str(refresh))
        return resp


class UserViewSet(viewsets.ModelViewSet):
    """User management viewset"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    def get_queryset(self):
        # Users can only see users in their organization or themselves
        if getattr(self.request.user, 'role', None) == 'admin' or self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change user password"""
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        if not user.check_password(old_password):
            return Response(
                {'error': 'Current password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        # Log password change
        AuditLog.objects.create(
            user=user,
            action='update',
            model_name='User',
            object_id=str(user.id),
            details={'field': 'password'},
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        return Response({'message': 'Password changed successfully'})

    @action(detail=False, methods=['post'])
    def setup_2fa(self, request):
        """Setup 2FA for user"""
        user = request.user

        if getattr(user, 'two_factor_enabled', False):
            return Response(
                {'error': '2FA is already enabled'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate secret key
        secret = pyotp.random_base32()
        user.two_factor_secret = secret
        user.save()

        # Generate QR code
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.email,
            issuer_name="MyCRM"
        )

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_code = base64.b64encode(buffer.getvalue()).decode()

        return Response({
            'secret': secret,
            'qr_code': f"data:image/png;base64,{qr_code}"
        })

    @action(detail=False, methods=['post'])
    def verify_2fa(self, request):
        """Verify 2FA token and enable 2FA"""
        serializer = TwoFactorVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        token = serializer.validated_data['token']

        if not getattr(user, 'two_factor_secret', None):
            return Response(
                {'error': '2FA setup not initiated'},
                status=status.HTTP_400_BAD_REQUEST
            )

        totp = pyotp.TOTP(user.two_factor_secret)
        if not totp.verify(token, valid_window=1):
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.two_factor_enabled = True
        user.save()

        # Log 2FA enablement
        AuditLog.objects.create(
            user=user,
            action='update',
            model_name='User',
            object_id=str(user.id),
            details={'field': 'two_factor_enabled', 'value': True},
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        return Response({'message': '2FA enabled successfully'})

    @action(detail=False, methods=['post'])
    def disable_2fa(self, request):
        """Disable 2FA for user"""
        user = request.user
        user.two_factor_enabled = False
        user.two_factor_secret = None
        user.save()

        # Log 2FA disablement
        AuditLog.objects.create(
            user=user,
            action='update',
            model_name='User',
            object_id=str(user.id),
            details={'field': 'two_factor_enabled', 'value': False},
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        return Response({'message': '2FA disabled successfully'})

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        return ip


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """Permission management viewset"""
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]


class RolePermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """Role permission management viewset"""
    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer
    permission_classes = [permissions.IsAuthenticated]


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Audit log viewset"""
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own audit logs unless they're admin
        if getattr(self.request.user, 'role', None) == 'admin' or self.request.user.is_superuser:
            return AuditLog.objects.all()
        return AuditLog.objects.filter(user=self.request.user)
