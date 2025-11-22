from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Organization, OrganizationMember, OrganizationInvitation
from .serializers import (
    OrganizationSerializer,
    OrganizationMemberSerializer,
    OrganizationInvitationSerializer,
    SwitchOrganizationSerializer
)
from .permissions import IsOrganizationOwner, IsOrganizationAdmin


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing organizations (tenants).
    
    List: GET /api/v1/organizations/
    Retrieve: GET /api/v1/organizations/{id}/
    Create: POST /api/v1/organizations/
    Update: PUT/PATCH /api/v1/organizations/{id}/
    Delete: DELETE /api/v1/organizations/{id}/
    
    Custom actions:
    - switch: Switch current user to this organization
    - statistics: Get organization statistics
    - upgrade_plan: Upgrade organization plan
    """
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Organization.objects.all()
        
        # Return organizations the user is a member of
        return Organization.objects.filter(
            members__user=user,
            members__is_active=True
        ).distinct()

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'upgrade_plan']:
            return [IsAuthenticated(), IsOrganizationOwner()]
        return [IsAuthenticated()]

    @transaction.atomic
    def perform_create(self, serializer):
        organization = serializer.save()
        # Owner membership is created by signal

    @action(detail=True, methods=['post'])
    def switch(self, request, pk=None):
        """Switch the current user's active organization."""
        serializer = SwitchOrganizationSerializer(
            data={'organization_id': pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        request.session['organization_id'] = str(pk)
        organization = Organization.objects.get(id=pk)
        
        return Response({
            'message': f'Switched to organization: {organization.name}',
            'organization': OrganizationSerializer(organization).data
        })

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get organization statistics."""
        organization = self.get_object()
        
        stats = {
            'total_members': organization.members.filter(is_active=True).count(),
            'members_by_role': {
                role[0]: organization.members.filter(role=role[0], is_active=True).count()
                for role in OrganizationMember.ROLE_CHOICES
            },
            'pending_invitations': organization.invitations.filter(status='pending').count(),
            'storage_used_mb': organization.storage_used_mb,
            'storage_limit_mb': organization.max_storage_mb,
            'storage_percentage': (organization.storage_used_mb / organization.max_storage_mb * 100) if organization.max_storage_mb > 0 else 0,
            'subscription_status': organization.status,
            'plan': organization.plan,
        }
        
        return Response(stats)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsOrganizationOwner])
    def upgrade_plan(self, request, pk=None):
        """Upgrade organization plan."""
        organization = self.get_object()
        new_plan = request.data.get('plan')
        
        if new_plan not in dict(Organization.PLAN_CHOICES):
            return Response(
                {'error': 'Invalid plan'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        organization.plan = new_plan
        
        # Update limits based on plan
        plan_limits = {
            'free': {'max_users': 5, 'max_contacts': 1000, 'max_storage_mb': 500},
            'starter': {'max_users': 10, 'max_contacts': 5000, 'max_storage_mb': 2000},
            'professional': {'max_users': 50, 'max_contacts': 25000, 'max_storage_mb': 10000},
            'enterprise': {'max_users': 999, 'max_contacts': 999999, 'max_storage_mb': 100000},
        }
        
        limits = plan_limits.get(new_plan, plan_limits['free'])
        organization.max_users = limits['max_users']
        organization.max_contacts = limits['max_contacts']
        organization.max_storage_mb = limits['max_storage_mb']
        organization.status = 'active'
        organization.save()
        
        return Response({
            'message': f'Plan upgraded to {new_plan}',
            'organization': OrganizationSerializer(organization).data
        })


class OrganizationMemberViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing organization members.
    
    List: GET /api/v1/organization-members/
    Retrieve: GET /api/v1/organization-members/{id}/
    Create: POST /api/v1/organization-members/
    Update: PUT/PATCH /api/v1/organization-members/{id}/
    Delete: DELETE /api/v1/organization-members/{id}/
    
    Custom actions:
    - my_memberships: Get current user's organization memberships
    - update_role: Update member role
    - deactivate: Deactivate a member
    """
    serializer_class = OrganizationMemberSerializer
    permission_classes = [IsAuthenticated, IsOrganizationAdmin]

    def get_queryset(self):
        user = self.request.user
        organization_id = self.request.query_params.get('organization')
        
        if user.is_superuser:
            queryset = OrganizationMember.objects.all()
        else:
            # Show members of organizations the user is an admin of
            admin_org_ids = OrganizationMember.objects.filter(
                user=user,
                role__in=['owner', 'admin'],
                is_active=True
            ).values_list('organization_id', flat=True)
            queryset = OrganizationMember.objects.filter(organization_id__in=admin_org_ids)
        
        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)
        
        return queryset.select_related('user', 'organization', 'invited_by')

    @action(detail=False, methods=['get'])
    def my_memberships(self, request):
        """Get all organizations the current user is a member of."""
        memberships = OrganizationMember.objects.filter(
            user=request.user,
            is_active=True
        ).select_related('organization')
        serializer = self.get_serializer(memberships, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsOrganizationOwner])
    def update_role(self, request, pk=None):
        """Update a member's role."""
        member = self.get_object()
        new_role = request.data.get('role')
        
        if new_role not in dict(OrganizationMember.ROLE_CHOICES):
            return Response(
                {'error': 'Invalid role'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prevent changing own role
        if member.user == request.user:
            return Response(
                {'error': 'Cannot change your own role'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        member.role = new_role
        member.save()
        
        return Response({
            'message': 'Role updated successfully',
            'member': self.get_serializer(member).data
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsOrganizationAdmin])
    def deactivate(self, request, pk=None):
        """Deactivate a member."""
        member = self.get_object()
        
        # Prevent deactivating self
        if member.user == request.user:
            return Response(
                {'error': 'Cannot deactivate yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prevent deactivating last owner
        if member.role == 'owner':
            owner_count = OrganizationMember.objects.filter(
                organization=member.organization,
                role='owner',
                is_active=True
            ).count()
            if owner_count <= 1:
                return Response(
                    {'error': 'Cannot deactivate the last owner'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        member.is_active = False
        member.save()
        
        return Response({'message': 'Member deactivated successfully'})


class OrganizationInvitationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing organization invitations.
    
    List: GET /api/v1/organization-invitations/
    Retrieve: GET /api/v1/organization-invitations/{id}/
    Create: POST /api/v1/organization-invitations/
    Delete: DELETE /api/v1/organization-invitations/{id}/
    
    Custom actions:
    - accept: Accept an invitation
    - decline: Decline an invitation
    - resend: Resend an invitation email
    """
    serializer_class = OrganizationInvitationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        organization_id = self.request.query_params.get('organization')
        
        # Admins can see invitations for their organizations
        if user.is_superuser:
            queryset = OrganizationInvitation.objects.all()
        else:
            admin_org_ids = OrganizationMember.objects.filter(
                user=user,
                role__in=['owner', 'admin'],
                is_active=True
            ).values_list('organization_id', flat=True)
            queryset = OrganizationInvitation.objects.filter(organization_id__in=admin_org_ids)
        
        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)
        
        return queryset.select_related('organization', 'invited_by')

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'resend']:
            return [IsAuthenticated(), IsOrganizationAdmin()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def accept(self, request):
        """Accept an invitation using the token."""
        token = request.data.get('token')
        
        try:
            invitation = OrganizationInvitation.objects.get(token=token)
        except OrganizationInvitation.DoesNotExist:
            return Response(
                {'error': 'Invalid invitation token'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if invitation.status != 'pending':
            return Response(
                {'error': 'Invitation has already been processed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if invitation.is_expired:
            invitation.status = 'expired'
            invitation.save()
            return Response(
                {'error': 'Invitation has expired'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user email matches invitation
        if request.user.email != invitation.email:
            return Response(
                {'error': 'This invitation is for a different email address'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create membership
        with transaction.atomic():
            OrganizationMember.objects.create(
                organization=invitation.organization,
                user=request.user,
                role=invitation.role,
                invited_by=invitation.invited_by
            )
            
            invitation.status = 'accepted'
            invitation.accepted_at = timezone.now()
            invitation.save()
        
        return Response({
            'message': f'Successfully joined {invitation.organization.name}',
            'organization': OrganizationSerializer(invitation.organization).data
        })

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def decline(self, request):
        """Decline an invitation using the token."""
        token = request.data.get('token')
        
        try:
            invitation = OrganizationInvitation.objects.get(token=token)
        except OrganizationInvitation.DoesNotExist:
            return Response(
                {'error': 'Invalid invitation token'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if invitation.status != 'pending':
            return Response(
                {'error': 'Invitation has already been processed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        invitation.status = 'declined'
        invitation.save()
        
        return Response({'message': 'Invitation declined'})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsOrganizationAdmin])
    def resend(self, request, pk=None):
        """Resend an invitation email."""
        invitation = self.get_object()
        
        if invitation.status != 'pending':
            return Response(
                {'error': 'Can only resend pending invitations'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Extend expiration
        from datetime import timedelta
        invitation.expires_at = timezone.now() + timedelta(days=7)
        invitation.save()
        
        # TODO: Resend email
        
        return Response({'message': 'Invitation resent successfully'})
