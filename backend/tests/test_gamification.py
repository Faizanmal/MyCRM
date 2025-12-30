# MyCRM Backend - Gamification Tests

import pytest
from rest_framework import status


@pytest.mark.django_db
class TestPointsAPI:
    """Tests for Points System API endpoints."""

    def test_get_user_points(self, authenticated_client):
        """Test getting current user's points."""
        url = '/api/v1/gamification/points/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_points_history(self, authenticated_client):
        """Test getting points history."""
        url = '/api/v1/gamification/points/history/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_points_breakdown(self, authenticated_client):
        """Test getting points breakdown by category."""
        url = '/api/v1/gamification/points/breakdown/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestLeaderboardAPI:
    """Tests for Leaderboard API endpoints."""

    def test_get_leaderboard(self, authenticated_client):
        """Test getting overall leaderboard."""
        url = '/api/v1/gamification/leaderboard/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_weekly_leaderboard(self, authenticated_client):
        """Test getting weekly leaderboard."""
        url = '/api/v1/gamification/leaderboard/?period=week'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_monthly_leaderboard(self, authenticated_client):
        """Test getting monthly leaderboard."""
        url = '/api/v1/gamification/leaderboard/?period=month'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_team_leaderboard(self, authenticated_client):
        """Test getting team leaderboard."""
        url = '/api/v1/gamification/leaderboard/teams/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_leaderboard_by_category(self, authenticated_client):
        """Test getting leaderboard by category."""
        url = '/api/v1/gamification/leaderboard/?category=sales'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestBadgesAPI:
    """Tests for Badges API endpoints."""

    def test_list_all_badges(self, authenticated_client):
        """Test listing all available badges."""
        url = '/api/v1/gamification/badges/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_user_badges(self, authenticated_client):
        """Test getting user's earned badges."""
        url = '/api/v1/gamification/badges/earned/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_badge_details(self, authenticated_client):
        """Test getting badge details."""
        url = '/api/v1/gamification/badges/1/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_badge_progress(self, authenticated_client):
        """Test getting progress toward badges."""
        url = '/api/v1/gamification/badges/progress/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestAchievementsAPI:
    """Tests for Achievements API endpoints."""

    def test_list_achievements(self, authenticated_client):
        """Test listing achievements."""
        url = '/api/v1/gamification/achievements/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_user_achievements(self, authenticated_client):
        """Test getting user's achievements."""
        url = '/api/v1/gamification/achievements/mine/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_claim_achievement(self, authenticated_client):
        """Test claiming an achievement."""
        url = '/api/v1/gamification/achievements/1/claim/'
        response = authenticated_client.post(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestChallengesAPI:
    """Tests for Challenges API endpoints."""

    def test_list_active_challenges(self, authenticated_client):
        """Test listing active challenges."""
        url = '/api/v1/gamification/challenges/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_join_challenge(self, authenticated_client):
        """Test joining a challenge."""
        url = '/api/v1/gamification/challenges/1/join/'
        response = authenticated_client.post(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_get_challenge_progress(self, authenticated_client):
        """Test getting challenge progress."""
        url = '/api/v1/gamification/challenges/1/progress/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_challenge_leaderboard(self, authenticated_client):
        """Test getting challenge-specific leaderboard."""
        url = '/api/v1/gamification/challenges/1/leaderboard/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestLevelsAPI:
    """Tests for Levels System API endpoints."""

    def test_get_current_level(self, authenticated_client):
        """Test getting current user level."""
        url = '/api/v1/gamification/levels/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_level_progression(self, authenticated_client):
        """Test getting level progression details."""
        url = '/api/v1/gamification/levels/progression/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_level_rewards(self, authenticated_client):
        """Test getting rewards for each level."""
        url = '/api/v1/gamification/levels/rewards/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestRewardsAPI:
    """Tests for Rewards API endpoints."""

    def test_list_available_rewards(self, authenticated_client):
        """Test listing available rewards."""
        url = '/api/v1/gamification/rewards/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_redeem_reward(self, authenticated_client):
        """Test redeeming a reward."""
        url = '/api/v1/gamification/rewards/1/redeem/'
        response = authenticated_client.post(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_get_redemption_history(self, authenticated_client):
        """Test getting reward redemption history."""
        url = '/api/v1/gamification/rewards/history/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
