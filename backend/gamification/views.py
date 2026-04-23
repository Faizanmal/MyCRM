from rest_framework.response import Response
from rest_framework.views import APIView


def _safe_user_id(request):
    return getattr(request.user, 'id', None) if request.user.is_authenticated else None


def _safe_user_info(request):
    if request.user.is_authenticated:
        return {
            'id': str(getattr(request.user, 'id', '0')),
            'username': getattr(request.user, 'username', 'anonymous'),
            'email': getattr(request.user, 'email', 'anonymous@example.com'),
        }
    return {
        'id': '0',
        'username': 'Guest',
        'email': 'guest@example.com',
    }


class UserPointsView(APIView):
    def get(self, request):
        return Response({
            'id': 'user-point-summary',
            'user': _safe_user_info(request),
            'total_points': 3200,
            'current_level': 8,
            'points_to_next_level': 800,
            'streak_days': 12,
            'longest_streak': 15,
            'achievements_count': 9,
            'rank': 14,
        })


class MyPointsView(APIView):
    def get(self, request):
        return Response({
            'id': 'my-points-summary',
            'user': _safe_user_info(request),
            'total_points': 3200,
            'current_level': 8,
            'points_to_next_level': 800,
            'streak_days': 12,
            'longest_streak': 15,
            'achievements_count': 9,
            'rank': 14,
        })


class PointsHistoryView(APIView):
    def get(self, request):
        return Response([
            {'date': '2026-04-03', 'points': 150, 'description': 'Closed deal'},
            {'date': '2026-04-01', 'points': 100, 'description': 'Completed training'},
            {'date': '2026-03-28', 'points': 75, 'description': 'Customer follow-up'},
        ])


class AchievementListView(APIView):
    def get(self, request):
        return Response([
            {
                'id': '1',
                'name': 'First Win',
                'description': 'Complete your first sale.',
                'icon': '🏆',
                'category': 'sales',
                'difficulty': 'easy',
                'points': 50,
                'criteria': {'type': 'deal', 'count': 1},
                'is_active': True,
                'is_repeatable': False,
                'earned_by_count': 112,
            },
            {
                'id': '2',
                'name': 'Sales Streak',
                'description': 'Win 3 deals in a row.',
                'icon': '🔥',
                'category': 'performance',
                'difficulty': 'medium',
                'points': 120,
                'criteria': {'type': 'streak', 'count': 3},
                'is_active': True,
                'is_repeatable': True,
                'earned_by_count': 44,
            },
        ])


class MyAchievementsView(APIView):
    def get(self, request):
        return Response([
            {
                'id': '1',
                'name': 'First Win',
                'description': 'Complete your first sale.',
                'icon': '🏆',
                'category': 'sales',
                'difficulty': 'easy',
                'points': 50,
                'criteria': {'type': 'deal', 'count': 1},
                'is_active': True,
                'is_repeatable': False,
                'earned_by_count': 112,
                'earned_at': '2026-04-03',
            },
        ])


class AchievementProgressView(APIView):
    def get(self, request, pk):
        return Response({
            'achievement_id': pk,
            'progress': 65,
            'goal': 100,
            'status': 'in_progress',
        })


class LeaderboardListView(APIView):
    def get(self, request):
        return Response([
            {
                'id': '1',
                'name': 'Top Sellers',
                'description': 'Highest performing sales reps this month.',
                'metric_type': 'points',
                'time_period': 'monthly',
                'is_active': True,
                'created_at': '2026-03-01T00:00:00Z',
            },
            {
                'id': '2',
                'name': 'Engagement Champions',
                'description': 'Most active reps in customer engagement.',
                'metric_type': 'tasks_completed',
                'time_period': 'weekly',
                'is_active': True,
                'created_at': '2026-04-01T00:00:00Z',
            },
        ])


class LeaderboardRankingsView(APIView):
    def get(self, request, pk):
        return Response([
            {
                'rank': 1,
                'user': {'id': '100', 'username': 'sales_star', 'email': 'star@example.com'},
                'score': 9800,
            },
            {
                'rank': 2,
                'user': {'id': '101', 'username': 'deal_maker', 'email': 'deal@example.com'},
                'score': 8750,
            },
            {
                'rank': 3,
                'user': {'id': '102', 'username': 'closer', 'email': 'closer@example.com'},
                'score': 7650,
            },
        ])


class ChallengeListView(APIView):
    def get(self, request):
        return Response([
            {
                'id': '1',
                'name': 'Monthly Revenue Challenge',
                'description': 'Close $50k in revenue this month.',
                'challenge_type': 'individual',
                'goal_type': 'Revenue',
                'goal_value': 50000,
                'reward_points': 500,
                'status': 'active',
                'start_date': '2026-04-01',
                'end_date': '2026-04-30',
                'participants_count': 12,
            },
            {
                'id': '2',
                'name': 'Customer Outreach Sprint',
                'description': 'Reach 30 new contacts.',
                'challenge_type': 'team',
                'goal_type': 'Contacts',
                'goal_value': 30,
                'reward_points': 300,
                'status': 'active',
                'start_date': '2026-04-05',
                'end_date': '2026-04-25',
                'participants_count': 8,
            },
        ])


class MyChallengesView(APIView):
    def get(self, request):
        return Response([
            {
                'id': '1',
                'name': 'Monthly Revenue Challenge',
                'description': 'Close $50k in revenue this month.',
                'challenge_type': 'individual',
                'goal_type': 'Revenue',
                'goal_value': 50000,
                'reward_points': 500,
                'status': 'in_progress',
                'start_date': '2026-04-01',
                'end_date': '2026-04-30',
                'participants_count': 12,
                'is_participating': True,
            },
        ])


class ChallengeJoinView(APIView):
    def post(self, request, pk):
        return Response({'detail': f'Joined challenge {pk}.'})


class ChallengeLeaveView(APIView):
    def post(self, request, pk):
        return Response({'detail': f'Left challenge {pk}.'})


class ActiveTeamChallengesView(APIView):
    def get(self, request):
        return Response([
            {
                'id': '3',
                'name': 'Team Collaboration Challenge',
                'description': 'Close 5 shared deals with your team.',
                'challenge_type': 'team',
                'goal_type': 'Deals',
                'goal_value': 5,
                'reward_points': 400,
                'status': 'active',
                'start_date': '2026-04-10',
                'end_date': '2026-05-10',
                'participants_count': 6,
            },
        ])


class PointTransactionsView(APIView):
    def get(self, request):
        return Response([
            {'id': 'tx1', 'date': '2026-04-03', 'points': 150, 'description': 'Deal closed'},
            {'id': 'tx2', 'date': '2026-04-01', 'points': 100, 'description': 'Training completed'},
        ])


class MyTransactionsView(APIView):
    def get(self, request):
        return Response([
            {'id': 'tx1', 'date': '2026-04-03', 'points': 150, 'description': 'Deal closed'},
        ])
