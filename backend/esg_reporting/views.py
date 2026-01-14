"""
ESG Reporting Views
"""

from django.db.models import Avg, Q, Sum
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    CarbonFootprint,
    ESGDataEntry,
    ESGFramework,
    ESGMetricCategory,
    ESGMetricDefinition,
    ESGReport,
    ESGTarget,
    SupplierESGAssessment,
)
from .serializers import (
    CarbonFootprintSerializer,
    ESGDataEntrySerializer,
    ESGFrameworkSerializer,
    ESGMetricCategorySerializer,
    ESGMetricDefinitionSerializer,
    ESGReportSerializer,
    ESGTargetSerializer,
    SupplierESGAssessmentSerializer,
)


class ESGFrameworkViewSet(viewsets.ReadOnlyModelViewSet):
    """Available ESG reporting frameworks"""
    queryset = ESGFramework.objects.filter(is_active=True)
    serializer_class = ESGFrameworkSerializer
    permission_classes = [IsAuthenticated]


class ESGMetricCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ESG metric categories by pillar"""
    queryset = ESGMetricCategory.objects.all()
    serializer_class = ESGMetricCategorySerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def by_pillar(self, request):
        """Get categories grouped by pillar"""
        pillars = {}
        for pillar, label in ESGMetricCategory.ESG_PILLAR:
            categories = self.queryset.filter(pillar=pillar)
            pillars[pillar] = {
                'label': label,
                'categories': ESGMetricCategorySerializer(categories, many=True).data
            }
        return Response(pillars)


class ESGMetricDefinitionViewSet(viewsets.ReadOnlyModelViewSet):
    """ESG metric definitions"""
    queryset = ESGMetricDefinition.objects.filter(is_active=True)
    serializer_class = ESGMetricDefinitionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)

        pillar = self.request.query_params.get('pillar')
        if pillar:
            queryset = queryset.filter(category__pillar=pillar)

        framework = self.request.query_params.get('framework')
        if framework:
            queryset = queryset.filter(frameworks__id=framework)

        return queryset


class ESGDataEntryViewSet(viewsets.ModelViewSet):
    """CRUD for ESG data entries"""
    serializer_class = ESGDataEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = ESGDataEntry.objects.select_related('metric', 'entered_by')

        # Filters
        metric = self.request.query_params.get('metric')
        if metric:
            queryset = queryset.filter(metric_id=metric)

        fiscal_year = self.request.query_params.get('year')
        if fiscal_year:
            queryset = queryset.filter(fiscal_year=fiscal_year)

        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        pillar = self.request.query_params.get('pillar')
        if pillar:
            queryset = queryset.filter(metric__category__pillar=pillar)

        return queryset

    def perform_create(self, serializer):
        serializer.save(entered_by=self.request.user)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit entry for approval"""
        entry = self.get_object()
        entry.status = 'submitted'
        entry.save()
        return Response(ESGDataEntrySerializer(entry).data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve data entry"""
        entry = self.get_object()
        entry.status = 'approved'
        entry.approved_by = request.user
        entry.approved_at = timezone.now()
        entry.save()
        return Response(ESGDataEntrySerializer(entry).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject data entry"""
        entry = self.get_object()
        entry.status = 'rejected'
        entry.save()
        return Response(ESGDataEntrySerializer(entry).data)

    @action(detail=False, methods=['get'])
    def pending_approval(self, request):
        """Get entries pending approval"""
        entries = self.get_queryset().filter(status='submitted')
        return Response(ESGDataEntrySerializer(entries, many=True).data)


class ESGTargetViewSet(viewsets.ModelViewSet):
    """ESG targets and goals"""
    serializer_class = ESGTargetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ESGTarget.objects.select_related('metric')

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get targets summary by status"""
        targets = self.get_queryset()
        return Response({
            'total': targets.count(),
            'on_track': targets.filter(status='on_track').count(),
            'at_risk': targets.filter(status='at_risk').count(),
            'behind': targets.filter(status='behind').count(),
            'achieved': targets.filter(status='achieved').count(),
            'not_started': targets.filter(status='not_started').count(),
        })

    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """Update target progress"""
        target = self.get_object()
        current_value = request.data.get('current_value')

        if current_value is not None:
            target.current_value = current_value

            # Calculate progress
            total_change_needed = target.target_value - target.baseline_value
            current_change = current_value - target.baseline_value

            if total_change_needed != 0:
                target.progress_percentage = (current_change / total_change_needed) * 100

            # Update status based on progress
            years_total = target.target_year - target.baseline_year
            years_elapsed = timezone.now().year - target.baseline_year
            expected_progress = (years_elapsed / years_total) * 100 if years_total > 0 else 0

            if target.progress_percentage >= 100:
                target.status = 'achieved'
            elif target.progress_percentage >= expected_progress * 0.9:
                target.status = 'on_track'
            elif target.progress_percentage >= expected_progress * 0.7:
                target.status = 'at_risk'
            else:
                target.status = 'behind'

            target.save()

        return Response(ESGTargetSerializer(target).data)


class ESGReportViewSet(viewsets.ModelViewSet):
    """ESG report generation and management"""
    serializer_class = ESGReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ESGReport.objects.select_related('framework', 'created_by')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def generate_pdf(self, request, pk=None):
        """Generate PDF report"""
        report = self.get_object()
        # PDF generation logic would go here
        return Response({"message": "PDF generation started", "report_id": str(report.id)})

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish report"""
        report = self.get_object()
        report.status = 'published'
        report.published_at = timezone.now()
        report.approved_by = request.user
        report.save()
        return Response(ESGReportSerializer(report).data)


class CarbonFootprintViewSet(viewsets.ModelViewSet):
    """Carbon emissions tracking"""
    serializer_class = CarbonFootprintSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CarbonFootprint.objects.all()

        scope = self.request.query_params.get('scope')
        if scope:
            queryset = queryset.filter(scope=scope)

        year = self.request.query_params.get('year')
        if year:
            queryset = queryset.filter(period_start__year=year)

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get carbon footprint summary"""
        year = request.query_params.get('year', timezone.now().year)
        entries = self.get_queryset().filter(period_start__year=year)

        total = entries.aggregate(total=Sum('total_co2e'))['total'] or 0
        scope1 = entries.filter(scope='scope1').aggregate(total=Sum('total_co2e'))['total'] or 0
        scope2 = entries.filter(scope='scope2').aggregate(total=Sum('total_co2e'))['total'] or 0
        scope3 = entries.filter(scope='scope3').aggregate(total=Sum('total_co2e'))['total'] or 0

        # Previous year for comparison
        prev_year_total = self.get_queryset().filter(
            period_start__year=int(year) - 1
        ).aggregate(total=Sum('total_co2e'))['total'] or 0

        yoy_change = ((total - prev_year_total) / prev_year_total * 100) if prev_year_total > 0 else 0

        # By category
        by_category = {}
        for entry in entries.values('category').annotate(total=Sum('total_co2e')):
            by_category[entry['category']] = entry['total']

        return Response({
            'year': year,
            'total_co2e': round(total, 2),
            'scope1_total': round(scope1, 2),
            'scope2_total': round(scope2, 2),
            'scope3_total': round(scope3, 2),
            'scope_breakdown': {
                'scope1_percentage': round((scope1 / total * 100) if total > 0 else 0, 1),
                'scope2_percentage': round((scope2 / total * 100) if total > 0 else 0, 1),
                'scope3_percentage': round((scope3 / total * 100) if total > 0 else 0, 1),
            },
            'by_category': by_category,
            'year_over_year_change': round(yoy_change, 1),
        })

    @action(detail=False, methods=['get'])
    def trends(self, request):
        """Get emissions trends over time"""
        years_back = int(request.query_params.get('years', 5))
        current_year = timezone.now().year

        trends = []
        for year in range(current_year - years_back + 1, current_year + 1):
            year_data = self.get_queryset().filter(
                period_start__year=year
            ).aggregate(
                total=Sum('total_co2e'),
                scope1=Sum('total_co2e', filter=Q(scope='scope1')),
                scope2=Sum('total_co2e', filter=Q(scope='scope2')),
                scope3=Sum('total_co2e', filter=Q(scope='scope3')),
            )
            trends.append({
                'year': year,
                'total': year_data['total'] or 0,
                'scope1': year_data['scope1'] or 0,
                'scope2': year_data['scope2'] or 0,
                'scope3': year_data['scope3'] or 0,
            })

        return Response(trends)


class SupplierESGAssessmentViewSet(viewsets.ModelViewSet):
    """Supplier ESG assessments"""
    serializer_class = SupplierESGAssessmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = SupplierESGAssessment.objects.all()

        risk = self.request.query_params.get('risk')
        if risk:
            queryset = queryset.filter(risk_level=risk)

        rating = self.request.query_params.get('rating')
        if rating:
            queryset = queryset.filter(overall_rating=rating)

        return queryset

    def perform_create(self, serializer):
        serializer.save(assessed_by=self.request.user)

    @action(detail=False, methods=['get'])
    def risk_summary(self, request):
        """Get risk summary across suppliers"""
        assessments = self.get_queryset()

        return Response({
            'total_suppliers': assessments.count(),
            'by_risk_level': {
                'low': assessments.filter(risk_level='low').count(),
                'medium': assessments.filter(risk_level='medium').count(),
                'high': assessments.filter(risk_level='high').count(),
                'critical': assessments.filter(risk_level='critical').count(),
            },
            'by_rating': {
                'A': assessments.filter(overall_rating='A').count(),
                'B': assessments.filter(overall_rating='B').count(),
                'C': assessments.filter(overall_rating='C').count(),
                'D': assessments.filter(overall_rating='D').count(),
                'F': assessments.filter(overall_rating='F').count(),
            },
            'average_scores': {
                'environmental': assessments.aggregate(avg=Avg('environmental_score'))['avg'],
                'social': assessments.aggregate(avg=Avg('social_score'))['avg'],
                'governance': assessments.aggregate(avg=Avg('governance_score'))['avg'],
                'overall': assessments.aggregate(avg=Avg('overall_score'))['avg'],
            }
        })


class ESGDashboardView(APIView):
    """ESG dashboard overview"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        current_year = timezone.now().year

        # Carbon summary
        carbon_entries = CarbonFootprint.objects.filter(period_start__year=current_year)
        total_carbon = carbon_entries.aggregate(total=Sum('total_co2e'))['total'] or 0

        # Targets
        targets = ESGTarget.objects.all()

        # Pending entries
        pending = ESGDataEntry.objects.filter(status='submitted').count()

        # Recent reports
        reports = ESGReport.objects.order_by('-created_at')[:5]

        # Calculate overall ESG scores (simplified)
        supplier_assessments = SupplierESGAssessment.objects.all()
        avg_scores = supplier_assessments.aggregate(
            env=Avg('environmental_score'),
            soc=Avg('social_score'),
            gov=Avg('governance_score'),
            overall=Avg('overall_score')
        )

        return Response({
            'overall_score': int(avg_scores['overall'] or 0),
            'environmental_score': int(avg_scores['env'] or 0),
            'social_score': int(avg_scores['soc'] or 0),
            'governance_score': int(avg_scores['gov'] or 0),
            'carbon_footprint': {
                'total_co2e': round(total_carbon, 2),
                'scope1_total': round(carbon_entries.filter(scope='scope1').aggregate(t=Sum('total_co2e'))['t'] or 0, 2),
                'scope2_total': round(carbon_entries.filter(scope='scope2').aggregate(t=Sum('total_co2e'))['t'] or 0, 2),
                'scope3_total': round(carbon_entries.filter(scope='scope3').aggregate(t=Sum('total_co2e'))['t'] or 0, 2),
            },
            'targets_on_track': targets.filter(status='on_track').count(),
            'targets_at_risk': targets.filter(status__in=['at_risk', 'behind']).count(),
            'pending_data_entries': pending,
            'recent_reports': ESGReportSerializer(reports, many=True).data
        })
