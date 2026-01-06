from django.contrib.auth import get_user_model
from django.db.models import Q, Sum
from django.utils import timezone
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Opportunity, OpportunityActivity, OpportunityProduct, OpportunityStage, Product
from .serializers import (
    OpportunityActivitySerializer,
    OpportunityBulkUpdateSerializer,
    OpportunityCreateSerializer,
    OpportunityProductSerializer,
    OpportunitySerializer,
    OpportunityStageSerializer,
    ProductSerializer,
)

User = get_user_model()


class OpportunityViewSet(viewsets.ModelViewSet):
    """Opportunity management viewset"""
    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'company_name', 'contact__first_name', 'contact__last_name']
    ordering_fields = ['name', 'amount', 'expected_close_date', 'created_at', 'probability']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return OpportunityCreateSerializer
        return OpportunitySerializer

    def get_queryset(self):
        queryset = Opportunity.objects.all()

        # Filter by assigned user if not admin
        user_role = getattr(self.request.user, 'role', None)
        if user_role != 'admin' and not self.request.user.is_superuser:
            queryset = queryset.filter(
                Q(assigned_to=self.request.user) | Q(owner=self.request.user)
            )

        # Apply additional filters
        stage_filter = self.request.query_params.get('stage')
        if stage_filter:
            queryset = queryset.filter(stage=stage_filter)

        assigned_to = self.request.query_params.get('assigned_to')
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)

        min_amount = self.request.query_params.get('min_amount')
        if min_amount:
            queryset = queryset.filter(amount__gte=min_amount)

        max_amount = self.request.query_params.get('max_amount')
        if max_amount:
            queryset = queryset.filter(amount__lte=max_amount)

        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def update_stage(self, request, _pk=None):
        """Update opportunity stage"""
        opportunity = self.get_object()
        new_stage = request.data.get('stage')

        if not new_stage:
            return Response(
                {'error': 'Stage is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        opportunity.stage = new_stage
        opportunity.last_activity_date = timezone.now()
        opportunity.save()

        # Create activity record
        OpportunityActivity.objects.create(
            opportunity=opportunity,
            activity_type='stage_change',
            subject=f'Stage changed to {new_stage}',
            user=request.user
        )

        return Response(OpportunitySerializer(opportunity).data)

    @action(detail=True, methods=['post'])
    def add_product(self, request, _pk=None):
        """Add product to opportunity"""
        opportunity = self.get_object()

        serializer = OpportunityProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = serializer.save(opportunity=opportunity)

        # Update opportunity amount
        opportunity.amount = opportunity.products.aggregate(
            total=Sum('total_price')
        )['total'] or 0
        opportunity.save()

        return Response(OpportunityProductSerializer(product).data)

    @action(detail=True, methods=['post'])
    def add_activity(self, request, _pk=None):
        """Add activity to opportunity"""
        opportunity = self.get_object()

        serializer = OpportunityActivitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        activity = serializer.save(
            opportunity=opportunity,
            user=request.user
        )

        # Update last activity date
        opportunity.last_activity_date = timezone.now()
        opportunity.save()

        return Response(OpportunityActivitySerializer(activity).data)

    @action(detail=False, methods=['get'])
    def pipeline(self, request):
        """Get opportunities grouped by stage for pipeline view"""
        queryset = self.get_queryset()

        # Group by stage
        pipeline_data = {}
        for stage in Opportunity.STAGE_CHOICES:
            stage_name = stage[0]
            stage_opportunities = queryset.filter(stage=stage_name)
            pipeline_data[stage_name] = {
                'name': stage[1],
                'opportunities': OpportunitySerializer(stage_opportunities, many=True).data,
                'count': stage_opportunities.count(),
                'total_value': stage_opportunities.aggregate(
                    total=Sum('amount')
                )['total'] or 0
            }

        return Response(pipeline_data)

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update opportunities"""
        serializer = OpportunityBulkUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        opportunity_ids = serializer.validated_data['opportunity_ids']
        updates = serializer.validated_data['updates']

        # Check permissions
        opportunities = Opportunity.objects.filter(id__in=opportunity_ids)
        user_role = getattr(self.request.user, 'role', None)
        if user_role != 'admin' and not self.request.user.is_superuser:
            opportunities = opportunities.filter(
                Q(assigned_to=self.request.user) | Q(owner=self.request.user)
            )

        updated_count = opportunities.update(**updates)

        return Response({
            'message': f'{updated_count} opportunities updated successfully',
            'updated_count': updated_count
        })


class OpportunityStageViewSet(viewsets.ModelViewSet):
    """Opportunity stage management viewset"""
    queryset = OpportunityStage.objects.all()
    serializer_class = OpportunityStageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return OpportunityStage.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class OpportunityActivityViewSet(viewsets.ModelViewSet):
    """Opportunity activity management viewset"""
    queryset = OpportunityActivity.objects.all()
    serializer_class = OpportunityActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = OpportunityActivity.objects.all()

        # Filter by opportunity if specified
        opportunity_id = self.request.query_params.get('opportunity_id')
        if opportunity_id:
            queryset = queryset.filter(opportunity_id=opportunity_id)

        # Filter by user if not admin
        user_role = getattr(self.request.user, 'role', None)
        if user_role != 'admin' and not self.request.user.is_superuser:
            queryset = queryset.filter(
                Q(user=self.request.user) | Q(opportunity__assigned_to=self.request.user)
            )

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProductViewSet(viewsets.ModelViewSet):
    """Product management viewset"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'sku', 'category']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['name']


class OpportunityProductViewSet(viewsets.ModelViewSet):
    """Opportunity product management viewset"""
    queryset = OpportunityProduct.objects.all()
    serializer_class = OpportunityProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = OpportunityProduct.objects.all()

        # Filter by opportunity if specified
        opportunity_id = self.request.query_params.get('opportunity_id')
        if opportunity_id:
            queryset = queryset.filter(opportunity_id=opportunity_id)

        return queryset
