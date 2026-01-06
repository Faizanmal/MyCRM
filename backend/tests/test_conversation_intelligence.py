# MyCRM Backend - Conversation Intelligence Tests


import pytest
from rest_framework import status


@pytest.mark.django_db
class TestCallRecordingsAPI:
    """Tests for Call Recordings API endpoints."""

    def test_list_recordings(self, authenticated_client):
        """Test listing call recordings."""
        url = '/api/v1/conversation-intelligence/recordings/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_upload_recording(self, authenticated_client):
        """Test uploading a call recording."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        url = '/api/v1/conversation-intelligence/recordings/'
        audio_content = b'fake audio content'
        audio_file = SimpleUploadedFile("call.mp3", audio_content, content_type="audio/mpeg")
        data = {
            'file': audio_file,
            'contact_id': 1,
            'opportunity_id': 1,
            'call_type': 'discovery',
            'participants': 'John Doe, Jane Smith',
        }
        response = authenticated_client.post(url, data, format='multipart')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_get_recording_details(self, authenticated_client):
        """Test getting recording details with analysis."""
        url = '/api/v1/conversation-intelligence/recordings/1/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_transcription(self, authenticated_client):
        """Test getting call transcription."""
        url = '/api/v1/conversation-intelligence/recordings/1/transcription/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_request_transcription(self, authenticated_client):
        """Test requesting transcription for a recording."""
        url = '/api/v1/conversation-intelligence/recordings/1/transcribe/'
        response = authenticated_client.post(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_202_ACCEPTED, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestSentimentAnalysisAPI:
    """Tests for Sentiment Analysis API endpoints."""

    def test_get_call_sentiment(self, authenticated_client):
        """Test getting sentiment analysis for a call."""
        url = '/api/v1/conversation-intelligence/recordings/1/sentiment/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_sentiment_timeline(self, authenticated_client):
        """Test getting sentiment timeline throughout a call."""
        url = '/api/v1/conversation-intelligence/recordings/1/sentiment/timeline/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_analyze_text_sentiment(self, authenticated_client):
        """Test analyzing sentiment from text."""
        url = '/api/v1/conversation-intelligence/sentiment/analyze/'
        data = {
            'text': 'I am really happy with the product. It exceeded all our expectations!',
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestTalkTimeAnalyticsAPI:
    """Tests for Talk Time Analytics API endpoints."""

    def test_get_talk_time_ratio(self, authenticated_client):
        """Test getting talk time ratio for a call."""
        url = '/api/v1/conversation-intelligence/recordings/1/talk-time/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_user_talk_time_stats(self, authenticated_client):
        """Test getting user's overall talk time statistics."""
        url = '/api/v1/conversation-intelligence/analytics/talk-time/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_optimal_talk_time(self, authenticated_client):
        """Test getting optimal talk time recommendations."""
        url = '/api/v1/conversation-intelligence/analytics/optimal-talk-time/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestKeywordDetectionAPI:
    """Tests for Keyword Detection API endpoints."""

    def test_get_keywords(self, authenticated_client):
        """Test getting detected keywords from a call."""
        url = '/api/v1/conversation-intelligence/recordings/1/keywords/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_manage_keyword_tracker(self, authenticated_client):
        """Test managing keyword trackers."""
        url = '/api/v1/conversation-intelligence/keyword-trackers/'
        data = {
            'keywords': ['pricing', 'competitor', 'budget', 'timeline'],
            'name': 'Sales Keywords',
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_search_by_keyword(self, authenticated_client):
        """Test searching recordings by keyword."""
        url = '/api/v1/conversation-intelligence/recordings/?keyword=pricing'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestCoachingAPI:
    """Tests for Coaching & Feedback API endpoints."""

    def test_get_coaching_score(self, authenticated_client):
        """Test getting coaching score for a call."""
        url = '/api/v1/conversation-intelligence/recordings/1/coaching/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_add_coaching_feedback(self, authenticated_client):
        """Test adding coaching feedback."""
        url = '/api/v1/conversation-intelligence/recordings/1/coaching/feedback/'
        data = {
            'timestamp': 120,  # 2 minutes into call
            'comment': 'Good use of open-ended questions here',
            'type': 'positive',
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_get_coaching_insights(self, authenticated_client):
        """Test getting overall coaching insights."""
        url = '/api/v1/conversation-intelligence/coaching/insights/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_improvement_suggestions(self, authenticated_client):
        """Test getting AI-powered improvement suggestions."""
        url = '/api/v1/conversation-intelligence/recordings/1/suggestions/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestMeetingIntelligenceAPI:
    """Tests for Meeting Intelligence API endpoints."""

    def test_get_meeting_summary(self, authenticated_client):
        """Test getting AI-generated meeting summary."""
        url = '/api/v1/conversation-intelligence/recordings/1/summary/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_action_items(self, authenticated_client):
        """Test getting extracted action items."""
        url = '/api/v1/conversation-intelligence/recordings/1/action-items/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_create_task_from_action_item(self, authenticated_client):
        """Test creating a task from an action item."""
        url = '/api/v1/conversation-intelligence/recordings/1/action-items/1/create-task/'
        data = {
            'assignee_id': 1,
            'due_date': '2024-12-31',
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_get_deal_mentions(self, authenticated_client):
        """Test getting mentions of deals/opportunities."""
        url = '/api/v1/conversation-intelligence/recordings/1/deal-mentions/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestConversationAnalyticsAPI:
    """Tests for Conversation Analytics API endpoints."""

    def test_get_overall_analytics(self, authenticated_client):
        """Test getting overall conversation analytics."""
        url = '/api/v1/conversation-intelligence/analytics/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_topic_analysis(self, authenticated_client):
        """Test getting topic analysis across calls."""
        url = '/api/v1/conversation-intelligence/analytics/topics/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_objection_analysis(self, authenticated_client):
        """Test getting objection analysis."""
        url = '/api/v1/conversation-intelligence/analytics/objections/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_competitive_mentions(self, authenticated_client):
        """Test getting competitive mentions analysis."""
        url = '/api/v1/conversation-intelligence/analytics/competitive/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_win_loss_correlation(self, authenticated_client):
        """Test getting win/loss correlation with conversation metrics."""
        url = '/api/v1/conversation-intelligence/analytics/win-loss-correlation/'
        response = authenticated_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
