"""
Revenue Intelligence Views
Premium analytics APIs
"""

from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Avg, F, Sum
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from opportunity_management.models import Opportunity

from .engine import DealScoringEngine, RevenueForecastEngine, RiskAlertEngine
from .models import (
    Competitor,
    DealCompetitor,
    DealRiskAlert,
    DealScore,
    RevenueForecast,
    RevenueTarget,
)
from .serializers import (
    CompetitorSerializer,
    DealCompetitorSerializer,
    DealRiskAlertSerializer,
    DealScoreSerializer,
    DealScoreSummarySerializer,
    RevenueForecastSerializer,
    RevenueTargetSerializer,
)


class RevenueTargetViewSet(viewsets.ModelViewSet):
    """Manage revenue targets and quotas"""
    serializer_class = RevenueTargetSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['target_type', 'period', 'start_date']
    ordering_fields = ['-start_date', 'target_type']

    def get_queryset(self):
        return RevenueTarget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current period target"""
        today = timezone.now().date()
        target = self.get_queryset().filter(
            start_date__lte=today,
            end_date__gte=today
        ).first()

        if target:
            serializer = self.get_serializer(target)
            return Response(serializer.data)
        return Response({'detail': 'No active target found'}, status=404)

    @action(detail=True, methods=['post'])
    def refresh(self, request, _pk=None):
        """Recalculate target actuals"""
        target = self.get_object()

        # Calculate achieved (closed won in period)
        achieved = Opportunity.objects.filter(
            owner=request.user,
            stage='closed_won',
            actual_close_date__gte=target.start_date,
            actual_close_date__lte=target.end_date
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        # Calculate pipeline
        pipeline = Opportunity.objects.filter(
            owner=request.user,
            expected_close_date__gte=target.start_date,
            expected_close_date__lte=target.end_date
        ).exclude(stage__in=['closed_won', 'closed_lost'])

        total_pipeline = pipeline.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        weighted = pipeline.aggregate(
            total=Sum(F('amount') * F('probability') / 100)
        )['total'] or Decimal('0')

        target.achieved_amount = achieved
        target.pipeline_amount = total_pipeline
        target.weighted_pipeline = weighted
        target.save()

        serializer = self.get_serializer(target)
        return Response(serializer.data)


class DealScoreViewSet(viewsets.ReadOnlyModelViewSet):
    """View and analyze deal scores"""
    serializer_class = DealScoreSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['risk_level', 'score_trend']
    ordering_fields = ['-score', '-win_probability', '-calculated_at']

    def get_queryset(self):
        return DealScore.objects.filter(
            opportunity__owner=self.request.user
        ).select_related('opportunity')

    def get_serializer_class(self):
        if self.action == 'list':
            return DealScoreSummarySerializer
        return DealScoreSerializer

    @action(detail=False, methods=['post'])
    def score_deal(self, request):
        """Score a specific deal"""
        opportunity_id = request.data.get('opportunity_id')
        if not opportunity_id:
            return Response({'error': 'opportunity_id required'}, status=400)

        try:
            opportunity = Opportunity.objects.get(
                id=opportunity_id,
                owner=request.user
            )
        except Opportunity.DoesNotExist:
            return Response({'error': 'Opportunity not found'}, status=404)

        engine = DealScoringEngine()
        deal_score = engine.score_deal(opportunity)

        serializer = DealScoreSerializer(deal_score)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def score_all(self, request):
        """Score all open deals"""
        opportunities = Opportunity.objects.filter(
            owner=request.user
        ).exclude(stage__in=['closed_won', 'closed_lost'])

        engine = DealScoringEngine()
        scores = []

        for opp in opportunities:
            try:
                score = engine.score_deal(opp)
                scores.append(score)
            except Exception:
                continue  # Skip failed scores

        serializer = DealScoreSummarySerializer(scores, many=True)
        return Response({
            'scored_count': len(scores),
            'scores': serializer.data
        })

    @action(detail=False, methods=['get'])
    def at_risk(self, request):
        """Get all at-risk deals"""
        scores = self.get_queryset().filter(
            risk_level__in=['high', 'critical']
        ).order_by('risk_level', '-opportunity__amount')

        serializer = DealScoreSerializer(scores, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def insights(self, request):
        """Get deal scoring insights"""
        scores = self.get_queryset()

        return Response({
            'total_deals_scored': scores.count(),
            'avg_score': scores.aggregate(avg=Avg('score'))['avg'] or 0,
            'avg_win_probability': scores.aggregate(avg=Avg('win_probability'))['avg'] or 0,
            'risk_distribution': {
                'critical': scores.filter(risk_level='critical').count(),
                'high': scores.filter(risk_level='high').count(),
                'medium': scores.filter(risk_level='medium').count(),
                'low': scores.filter(risk_level='low').count(),
            },
            'trend_distribution': {
                'improving': scores.filter(score_trend='improving').count(),
                'stable': scores.filter(score_trend='stable').count(),
                'declining': scores.filter(score_trend='declining').count(),
            }
        })


class CompetitorViewSet(viewsets.ModelViewSet):
    """Manage competitive intelligence"""
    serializer_class = CompetitorSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['threat_level', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'threat_level', '-deals_won_against']

    def get_queryset(self):
        return Competitor.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'])
    def battle_card(self, request, _pk=None):
        """Get battle card for competitor"""
        competitor = self.get_object()

        return Response({
            'competitor': CompetitorSerializer(competitor).data,
            'battle_card': {
                'differentiators': competitor.differentiators,
                'objection_handlers': competitor.objection_handlers,
                'strengths_to_counter': competitor.strengths,
                'weaknesses_to_exploit': competitor.weaknesses,
                'pricing_intelligence': competitor.pricing_info,
            },
            'win_loss_stats': {
                'total_encounters': competitor.deals_won_against + competitor.deals_lost_to,
                'wins': competitor.deals_won_against,
                'losses': competitor.deals_lost_to,
                'win_rate': competitor.win_rate_against,
            }
        })


class DealCompetitorViewSet(viewsets.ModelViewSet):
    """Track competitors in deals"""
    serializer_class = DealCompetitorSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['opportunity', 'competitor', 'status', 'threat_level']

    def get_queryset(self):
        return DealCompetitor.objects.filter(
            opportunity__owner=self.request.user
        )


class RevenueForecastViewSet(viewsets.ReadOnlyModelViewSet):
    """View revenue forecasts"""
    serializer_class = RevenueForecastSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['forecast_type', 'period_start']
    ordering_fields = ['-forecast_date', '-period_start']

    def get_queryset(self):
        return RevenueForecast.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate forecasts for a period"""
        period_start = request.data.get('period_start')
        period_end = request.data.get('period_end')

        if not period_start or not period_end:
            # Default to current month
            today = timezone.now().date()
            period_start = today.replace(day=1)
            period_end = (period_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        else:
            period_start = date.fromisoformat(period_start)
            period_end = date.fromisoformat(period_end)

        engine = RevenueForecastEngine()
        forecasts = engine.generate_forecast(request.user, period_start, period_end)

        serializer = RevenueForecastSerializer(forecasts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def comparison(self, request):
        """Compare forecast types for current period"""
        today = timezone.now().date()
        period_start = today.replace(day=1)
        period_end = (period_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        forecasts = self.get_queryset().filter(
            period_start=period_start,
            period_end=period_end
        )

        result = {
            'period_start': period_start,
            'period_end': period_end,
            'commit': 0,
            'best_case': 0,
            'pipeline': 0,
            'ai_predicted': 0,
            'target': None,
            'closed_won': 0,
        }

        for f in forecasts:
            result[f.forecast_type] = f.amount
            if f.closed_won:
                result['closed_won'] = f.closed_won

        # Get target if exists
        try:
            target = RevenueTarget.objects.get(
                user=request.user,
                start_date__lte=today,
                end_date__gte=today
            )
            result['target'] = target.target_amount
        except RevenueTarget.DoesNotExist:
            pass

        return Response(result)


class DealRiskAlertViewSet(viewsets.ModelViewSet):
    """Manage deal risk alerts"""
    serializer_class = DealRiskAlertSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['alert_type', 'severity', 'is_active', 'is_acknowledged']
    ordering_fields = ['-created_at', 'severity']

    def get_queryset(self):
        return DealRiskAlert.objects.filter(
            opportunity__owner=self.request.user
        )

    @action(detail=False, methods=['post'])
    def scan(self, request):
        """Scan deals for new risks"""
        engine = RiskAlertEngine()
        alerts = engine.scan_deals_for_risks(request.user)

        serializer = DealRiskAlertSerializer(alerts, many=True)
        return Response({
            'alerts_created': len(alerts),
            'alerts': serializer.data
        })

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, _pk=None):
        """Acknowledge an alert"""
        alert = self.get_object()
        alert.is_acknowledged = True
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.save()

        serializer = self.get_serializer(alert)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def resolve(self, request, _pk=None):
        """Resolve an alert"""
        alert = self.get_object()
        alert.is_resolved = True
        alert.is_active = False
        alert.resolved_at = timezone.now()
        alert.resolution_notes = request.data.get('notes', '')
        alert.save()

        serializer = self.get_serializer(alert)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get alert summary"""
        alerts = self.get_queryset().filter(is_active=True)

        return Response({
            'total_active': alerts.count(),
            'by_severity': {
                'critical': alerts.filter(severity='critical').count(),
                'warning': alerts.filter(severity='warning').count(),
                'info': alerts.filter(severity='info').count(),
            },
            'by_type': {
                choice[0]: alerts.filter(alert_type=choice[0]).count()
                for choice in DealRiskAlert.ALERT_TYPES
            },
            'unacknowledged': alerts.filter(is_acknowledged=False).count(),
        })


class PipelineHealthView(APIView):
    """Pipeline health dashboard"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get comprehensive pipeline health metrics"""
        user = request.user

        # Get open opportunities
        pipeline = Opportunity.objects.filter(
            owner=user
        ).exclude(stage__in=['closed_won', 'closed_lost'])

        # Get closed deals for benchmarks
        closed_won = Opportunity.objects.filter(
            owner=user,
            stage='closed_won',
            actual_close_date__gte=timezone.now().date() - timedelta(days=365)
        )

        # Calculate metrics
        total_pipeline = pipeline.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        weighted = pipeline.aggregate(
            total=Sum(F('amount') * F('probability') / 100)
        )['total'] or Decimal('0')
        deal_count = pipeline.count()

        avg_deal_size = pipeline.aggregate(avg=Avg('amount'))['avg'] or Decimal('0')

        # Win rate
        closed_all = Opportunity.objects.filter(
            owner=user,
            stage__in=['closed_won', 'closed_lost'],
            actual_close_date__gte=timezone.now().date() - timedelta(days=365)
        )
        won_count = closed_all.filter(stage='closed_won').count()
        total_closed = closed_all.count()
        win_rate = (won_count / total_closed * 100) if total_closed > 0 else 0

        # Stage breakdown
        stage_breakdown = {}
        for stage in ['prospecting', 'qualification', 'proposal', 'negotiation']:
            stage_deals = pipeline.filter(stage=stage)
            stage_breakdown[stage] = {
                'count': stage_deals.count(),
                'value': float(stage_deals.aggregate(total=Sum('amount'))['total'] or 0)
            }

        # At-risk deals
        at_risk_scores = DealScore.objects.filter(
            opportunity__owner=user,
            risk_level__in=['high', 'critical']
        )
        at_risk_count = at_risk_scores.count()
        at_risk_value = Opportunity.objects.filter(
            deal_score__in=at_risk_scores
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        # Avg days to close
        avg_days = 0
        if closed_won.exists():
            days_list = []
            for opp in closed_won:
                if opp.actual_close_date:
                    days = (opp.actual_close_date - opp.created_at.date()).days
                    if days > 0:
                        days_list.append(days)
            avg_days = sum(days_list) / len(days_list) if days_list else 0

        return Response({
            'total_pipeline': total_pipeline,
            'weighted_pipeline': weighted,
            'deal_count': deal_count,
            'avg_deal_size': avg_deal_size,
            'avg_days_to_close': int(avg_days),
            'win_rate': round(win_rate, 1),
            'stage_breakdown': stage_breakdown,
            'at_risk_deals': at_risk_count,
            'at_risk_value': at_risk_value,
        })


class QuotaLeaderboardView(APIView):
    """Team quota attainment leaderboard"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get quota attainment for all users"""
        today = timezone.now().date()

        targets = RevenueTarget.objects.filter(
            start_date__lte=today,
            end_date__gte=today,
            target_type='revenue'
        ).select_related('user')

        leaderboard = []
        for target in targets:
            days_elapsed = (today - target.start_date).days
            days_remaining = (target.end_date - today).days

            leaderboard.append({
                'user_id': target.user.id,
                'user_name': target.user.get_full_name() or target.user.username,
                'target_amount': target.target_amount,
                'achieved_amount': target.achieved_amount,
                'attainment_percentage': target.attainment_percentage,
                'gap_to_target': target.gap_to_target,
                'pipeline_coverage': target.coverage_ratio,
                'forecast_attainment': target.forecast_attainment,
                'days_remaining': days_remaining,
                'pace': round(float(target.achieved_amount) / (days_elapsed + 1) if days_elapsed >= 0 else 0, 2),
                'required_pace': round(float(target.gap_to_target) / (days_remaining + 1) if days_remaining > 0 else 0, 2),
            })

        # Sort by attainment
        leaderboard.sort(key=lambda x: x['attainment_percentage'], reverse=True)

        return Response({
            'period_start': targets.first().start_date if targets.exists() else None,
            'period_end': targets.first().end_date if targets.exists() else None,
            'leaderboard': leaderboard
        })
