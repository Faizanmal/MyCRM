"""
Revenue Intelligence Dashboard Views
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from .dashboard_models import (
    RevenueForecast, CohortAnalysis, RevenueAttribution,
    SalesVelocity, RevenueLeakage, WinLossAnalysis,
    ARRMovement, RevenueIntelligenceSnapshot
)
from .dashboard_serializers import (
    RevenueForecastSerializer, CohortAnalysisSerializer,
    RevenueAttributionSerializer, SalesVelocitySerializer,
    RevenueLeakageSerializer, WinLossAnalysisSerializer,
    ARRMovementSerializer, RevenueIntelligenceSnapshotSerializer,
    GenerateForecastSerializer, CohortAnalysisRequestSerializer,
    AttributionRequestSerializer, VelocityRequestSerializer,
    LeakageAnalysisRequestSerializer, WinLossRequestSerializer,
    ARRMovementRequestSerializer, SnapshotComparisonSerializer
)
from .dashboard_services import (
    ForecastingService, CohortAnalysisService, AttributionService,
    SalesVelocityService, RevenueIntelligenceService
)


class RevenueForecastViewSet(viewsets.ModelViewSet):
    """ViewSet for revenue forecasting"""
    
    serializer_class = RevenueForecastSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return RevenueForecast.objects.filter(
            user=self.request.user
        ).order_by('-period_start')
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate a new forecast"""
        serializer = GenerateForecastSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = ForecastingService(request.user)
        result = service.generate_forecast(
            forecast_type=serializer.validated_data['forecast_type'],
            period_start=serializer.validated_data['period_start'],
            period_end=serializer.validated_data['period_end']
        )
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def current_quarter(self, request):
        """Get current quarter forecast"""
        today = date.today()
        quarter_start = date(today.year, ((today.month - 1) // 3) * 3 + 1, 1)
        quarter_end = quarter_start + relativedelta(months=3) - timedelta(days=1)
        
        forecast = self.get_queryset().filter(
            forecast_type='quarterly',
            period_start=quarter_start
        ).first()
        
        if not forecast:
            service = ForecastingService(request.user)
            result = service.generate_forecast(
                forecast_type='quarterly',
                period_start=quarter_start,
                period_end=quarter_end
            )
            return Response(result)
        
        return Response(RevenueForecastSerializer(forecast).data)
    
    @action(detail=False, methods=['get'])
    def trends(self, request):
        """Get forecast trends over time"""
        months = int(request.query_params.get('months', 6))
        
        forecasts = self.get_queryset().filter(
            forecast_type='monthly'
        ).order_by('-period_start')[:months]
        
        trends = []
        for f in forecasts:
            trends.append({
                'period': f.period_start.isoformat(),
                'predicted': float(f.predicted_revenue),
                'committed': float(f.committed_revenue),
                'actual': float(f.previous_period_actual or 0),
                'accuracy': self._calculate_accuracy(f)
            })
        
        return Response({'trends': trends})
    
    def _calculate_accuracy(self, forecast):
        """Calculate forecast accuracy"""
        if forecast.previous_period_actual and forecast.predicted_revenue:
            error = abs(
                float(forecast.predicted_revenue) - 
                float(forecast.previous_period_actual)
            )
            return max(0, 100 - (error / float(forecast.predicted_revenue) * 100))
        return None


class CohortAnalysisViewSet(viewsets.ModelViewSet):
    """ViewSet for cohort analysis"""
    
    serializer_class = CohortAnalysisSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CohortAnalysis.objects.filter(
            user=self.request.user
        ).order_by('-cohort_date')
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate cohort analysis"""
        serializer = CohortAnalysisRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = CohortAnalysisService(request.user)
        result = service.generate_cohort_analysis(
            cohort_type=serializer.validated_data['cohort_type'],
            metric_type=serializer.validated_data['metric_type'],
            periods=serializer.validated_data.get('periods', 12)
        )
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def retention_matrix(self, request):
        """Get retention matrix"""
        service = CohortAnalysisService(request.user)
        result = service.get_retention_matrix()
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def ltv_by_cohort(self, request):
        """Get LTV analysis by cohort"""
        cohorts = self.get_queryset().filter(
            metric_type='ltv'
        ).order_by('-cohort_date')[:12]
        
        result = []
        for cohort in cohorts:
            result.append({
                'cohort': cohort.cohort_name,
                'size': cohort.cohort_size,
                'avg_ltv': float(cohort.avg_value),
                'total_ltv': float(cohort.total_value)
            })
        
        return Response({'cohorts': result})


class RevenueAttributionViewSet(viewsets.ModelViewSet):
    """ViewSet for revenue attribution"""
    
    serializer_class = RevenueAttributionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return RevenueAttribution.objects.filter(
            user=self.request.user
        ).order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """Calculate attribution for an opportunity"""
        serializer = AttributionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = AttributionService(request.user)
        result = service.calculate_attribution(
            opportunity_id=str(serializer.validated_data['opportunity_id']),
            model=serializer.validated_data.get('model', 'linear')
        )
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def channel_summary(self, request):
        """Get attribution summary by channel"""
        service = AttributionService(request.user)
        result = service.get_channel_roi()
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def model_comparison(self, request):
        """Compare attribution across models"""
        opportunity_id = request.query_params.get('opportunity_id')
        
        if not opportunity_id:
            return Response(
                {'error': 'opportunity_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = AttributionService(request.user)
        models = ['first_touch', 'last_touch', 'linear', 'time_decay', 'position_based']
        
        comparison = {}
        for model in models:
            result = service.calculate_attribution(opportunity_id, model)
            comparison[model] = result.get('channel_attribution', {})
        
        return Response({'comparison': comparison})


class SalesVelocityViewSet(viewsets.ModelViewSet):
    """ViewSet for sales velocity"""
    
    serializer_class = SalesVelocitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SalesVelocity.objects.filter(
            user=self.request.user
        ).order_by('-period_start')
    
    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """Calculate sales velocity for a period"""
        serializer = VelocityRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = SalesVelocityService(request.user)
        result = service.calculate_velocity(
            period_start=serializer.validated_data['period_start'],
            period_end=serializer.validated_data['period_end']
        )
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current velocity metrics"""
        today = date.today()
        period_start = today - timedelta(days=30)
        
        service = SalesVelocityService(request.user)
        result = service.calculate_velocity(
            period_start=period_start,
            period_end=today
        )
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def trends(self, request):
        """Get velocity trends"""
        months = int(request.query_params.get('months', 6))
        
        velocities = self.get_queryset().order_by('-period_start')[:months]
        
        trends = []
        for v in velocities:
            trends.append({
                'period_start': v.period_start.isoformat(),
                'period_end': v.period_end.isoformat(),
                'velocity': float(v.sales_velocity),
                'trend': v.velocity_trend,
                'change': float(v.velocity_change) if v.velocity_change else None
            })
        
        return Response({'trends': trends})
    
    @action(detail=False, methods=['get'])
    def bottlenecks(self, request):
        """Get bottleneck analysis"""
        latest = self.get_queryset().first()
        
        if not latest:
            return Response({'bottlenecks': []})
        
        bottlenecks = []
        if latest.bottleneck_stage:
            bottlenecks.append({
                'stage': latest.bottleneck_stage,
                'impact': float(latest.bottleneck_impact) if latest.bottleneck_impact else None,
                'metrics': latest.stage_metrics.get(latest.bottleneck_stage, {})
            })
        
        return Response({'bottlenecks': bottlenecks})


class RevenueLeakageViewSet(viewsets.ModelViewSet):
    """ViewSet for revenue leakage detection"""
    
    serializer_class = RevenueLeakageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return RevenueLeakage.objects.filter(
            user=self.request.user
        ).order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def analyze(self, request):
        """Analyze revenue leakage"""
        serializer = LeakageAnalysisRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Simplified analysis
        leakages = []
        leakage_types = serializer.validated_data.get('leakage_types', [
            'discount_overuse', 'stalled_deals', 'churn'
        ])
        
        for lt in leakage_types:
            leakage = RevenueLeakage.objects.create(
                user=request.user,
                period_start=serializer.validated_data['period_start'],
                period_end=serializer.validated_data['period_end'],
                leakage_type=lt,
                identified_amount=0,
                recovered_amount=0,
                recovery_rate=0,
                affected_opportunities=[],
                priority='medium'
            )
            leakages.append(RevenueLeakageSerializer(leakage).data)
        
        return Response({'leakages': leakages})
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get leakage summary"""
        today = date.today()
        period_start = today - timedelta(days=90)
        
        leakages = self.get_queryset().filter(
            period_start__gte=period_start
        )
        
        summary = {
            'total_identified': sum(float(l.identified_amount) for l in leakages),
            'total_recovered': sum(float(l.recovered_amount) for l in leakages),
            'by_type': {}
        }
        
        for leakage in leakages:
            lt = leakage.leakage_type
            if lt not in summary['by_type']:
                summary['by_type'][lt] = {'identified': 0, 'recovered': 0}
            summary['by_type'][lt]['identified'] += float(leakage.identified_amount)
            summary['by_type'][lt]['recovered'] += float(leakage.recovered_amount)
        
        return Response(summary)
    
    @action(detail=True, methods=['post'])
    def mark_recovered(self, request, pk=None):
        """Mark leakage as recovered"""
        leakage = self.get_object()
        amount = request.data.get('amount', leakage.identified_amount)
        
        leakage.recovered_amount = amount
        if leakage.identified_amount and leakage.identified_amount > 0:
            leakage.recovery_rate = (
                float(amount) / float(leakage.identified_amount) * 100
            )
        leakage.save()
        
        return Response(RevenueLeakageSerializer(leakage).data)


class WinLossAnalysisViewSet(viewsets.ModelViewSet):
    """ViewSet for win/loss analysis"""
    
    serializer_class = WinLossAnalysisSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return WinLossAnalysis.objects.filter(
            user=self.request.user
        ).order_by('-period_start')
    
    @action(detail=False, methods=['post'])
    def analyze(self, request):
        """Run win/loss analysis"""
        serializer = WinLossRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = RevenueIntelligenceService(request.user)
        result = service.get_win_loss_analysis(
            period_start=serializer.validated_data['period_start'],
            period_end=serializer.validated_data['period_end']
        )
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def patterns(self, request):
        """Get win/loss patterns"""
        latest = self.get_queryset().first()
        
        if not latest:
            return Response({
                'win_patterns': [],
                'loss_patterns': []
            })
        
        return Response({
            'win_patterns': latest.win_patterns,
            'loss_patterns': latest.loss_patterns
        })
    
    @action(detail=False, methods=['get'])
    def competitor_impact(self, request):
        """Get competitor impact analysis"""
        latest = self.get_queryset().first()
        
        if not latest or not latest.competitor_analysis:
            return Response({'competitors': []})
        
        return Response({
            'competitors': latest.competitor_analysis
        })


class ARRMovementViewSet(viewsets.ModelViewSet):
    """ViewSet for ARR movement tracking"""
    
    serializer_class = ARRMovementSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ARRMovement.objects.filter(
            user=self.request.user
        ).order_by('-period_start')
    
    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """Calculate ARR movement for a period"""
        serializer = ARRMovementRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create ARR movement record
        movement = ARRMovement.objects.create(
            user=request.user,
            period_start=serializer.validated_data['period_start'],
            period_end=serializer.validated_data['period_end'],
            period_type=serializer.validated_data.get('period_type', 'monthly'),
            starting_arr=0,
            ending_arr=0
        )
        
        return Response(ARRMovementSerializer(movement).data)
    
    @action(detail=False, methods=['get'])
    def waterfall(self, request):
        """Get ARR waterfall chart data"""
        months = int(request.query_params.get('months', 6))
        
        movements = self.get_queryset().filter(
            period_type='monthly'
        ).order_by('-period_start')[:months]
        
        waterfall = []
        for m in movements:
            waterfall.append({
                'period': m.period_start.isoformat(),
                'starting': float(m.starting_arr),
                'new': float(m.new_arr or 0),
                'expansion': float(m.expansion_arr or 0),
                'contraction': float(m.contraction_arr or 0) * -1,
                'churn': float(m.churn_arr or 0) * -1,
                'reactivation': float(m.reactivation_arr or 0),
                'ending': float(m.ending_arr)
            })
        
        return Response({'waterfall': waterfall})
    
    @action(detail=False, methods=['get'])
    def nrr(self, request):
        """Get Net Revenue Retention"""
        movements = self.get_queryset().filter(
            period_type='monthly'
        ).order_by('-period_start')[:12]
        
        nrr_data = []
        for m in movements:
            if m.starting_arr and m.starting_arr > 0:
                nrr = (
                    (float(m.starting_arr) + 
                     float(m.expansion_arr or 0) - 
                     float(m.contraction_arr or 0) - 
                     float(m.churn_arr or 0)) / 
                    float(m.starting_arr) * 100
                )
            else:
                nrr = 100
            
            nrr_data.append({
                'period': m.period_start.isoformat(),
                'nrr': round(nrr, 1)
            })
        
        return Response({'nrr_trend': nrr_data})


class RevenueIntelligenceSnapshotViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for revenue intelligence snapshots"""
    
    serializer_class = RevenueIntelligenceSnapshotSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return RevenueIntelligenceSnapshot.objects.filter(
            user=self.request.user
        ).order_by('-snapshot_date')
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current dashboard snapshot"""
        service = RevenueIntelligenceService(request.user)
        snapshot = service.get_dashboard_snapshot()
        return Response(snapshot)
    
    @action(detail=False, methods=['post'])
    def compare(self, request):
        """Compare two snapshots"""
        serializer = SnapshotComparisonSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        snapshot_1 = self.get_queryset().filter(
            snapshot_date=serializer.validated_data['snapshot_date_1']
        ).first()
        
        snapshot_2 = self.get_queryset().filter(
            snapshot_date=serializer.validated_data['snapshot_date_2']
        ).first()
        
        if not snapshot_1 or not snapshot_2:
            return Response(
                {'error': 'One or both snapshots not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        comparison = {
            'date_1': snapshot_1.snapshot_date.isoformat(),
            'date_2': snapshot_2.snapshot_date.isoformat(),
            'changes': {}
        }
        
        # Compare key metrics
        metrics = serializer.validated_data.get('metrics', [
            'pipeline', 'forecast', 'velocity', 'health'
        ])
        
        if 'pipeline' in metrics:
            comparison['changes']['pipeline'] = {
                'total': float(snapshot_2.total_pipeline - snapshot_1.total_pipeline),
                'weighted': float(snapshot_2.weighted_pipeline - snapshot_1.weighted_pipeline),
                'coverage_change': float(
                    (snapshot_2.pipeline_coverage or 0) - 
                    (snapshot_1.pipeline_coverage or 0)
                )
            }
        
        if 'velocity' in metrics:
            comparison['changes']['velocity'] = {
                'change': float(
                    (snapshot_2.current_velocity or 0) - 
                    (snapshot_1.current_velocity or 0)
                ),
                'win_rate_change': float(
                    (snapshot_2.win_rate or 0) - 
                    (snapshot_1.win_rate or 0)
                )
            }
        
        return Response(comparison)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get snapshot history"""
        days = int(request.query_params.get('days', 30))
        
        snapshots = self.get_queryset().filter(
            snapshot_date__gte=date.today() - timedelta(days=days)
        )
        
        return Response({
            'snapshots': RevenueIntelligenceSnapshotSerializer(
                snapshots, many=True
            ).data
        })
    
    @action(detail=False, methods=['get'])
    def executive_summary(self, request):
        """Get executive summary"""
        service = RevenueIntelligenceService(request.user)
        snapshot = service.get_dashboard_snapshot()
        
        # Build executive summary
        summary = {
            'headline': self._generate_headline(snapshot),
            'key_metrics': {
                'pipeline': snapshot['pipeline'],
                'forecast': snapshot['forecast'],
                'velocity': snapshot['velocity']
            },
            'alerts': self._generate_alerts(snapshot),
            'recommendations': self._generate_recommendations(snapshot)
        }
        
        return Response(summary)
    
    def _generate_headline(self, snapshot):
        """Generate headline for executive summary"""
        attainment = snapshot['forecast']['attainment']
        
        if attainment >= 100:
            return f"On track - {attainment:.0f}% of quarterly target achieved"
        elif attainment >= 80:
            return f"Trending well - {attainment:.0f}% of quarterly target achieved"
        elif attainment >= 60:
            return f"Attention needed - {attainment:.0f}% of quarterly target achieved"
        else:
            return f"At risk - Only {attainment:.0f}% of quarterly target achieved"
    
    def _generate_alerts(self, snapshot):
        """Generate alerts based on snapshot data"""
        alerts = []
        
        if snapshot['health']['at_risk_deals'] > 0:
            alerts.append({
                'type': 'warning',
                'message': f"{snapshot['health']['at_risk_deals']} deals at risk worth ${snapshot['health']['at_risk_value']:,.0f}"
            })
        
        if snapshot['health']['stalled_deals'] > 0:
            alerts.append({
                'type': 'info',
                'message': f"{snapshot['health']['stalled_deals']} stalled deals need attention"
            })
        
        if snapshot['pipeline']['coverage'] < 200:
            alerts.append({
                'type': 'warning',
                'message': f"Pipeline coverage at {snapshot['pipeline']['coverage']:.0f}% - below 2x target"
            })
        
        return alerts
    
    def _generate_recommendations(self, snapshot):
        """Generate recommendations based on snapshot data"""
        recommendations = []
        
        if snapshot['health']['stalled_deals'] > 3:
            recommendations.append({
                'action': 'Review stalled deals',
                'impact': 'high',
                'details': 'Multiple deals have not progressed in 21+ days'
            })
        
        if snapshot['pipeline']['coverage'] < 300:
            recommendations.append({
                'action': 'Increase pipeline generation',
                'impact': 'medium',
                'details': 'Build pipeline to 3x coverage for target confidence'
            })
        
        return recommendations
