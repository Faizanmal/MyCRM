// Advanced services for MyCRM Flutter App
import '../core/constants/api_constants.dart';
import '../core/utils/api_client.dart';
import '../models/advanced_models.dart';

/// Service for Integration Hub features
class IntegrationHubService {
  final ApiClient _apiClient;

  IntegrationHubService(this._apiClient);

  // ==================== Integration Providers ====================
  Future<List<IntegrationProvider>> getProviders() async {
    final response = await _apiClient.get(ApiConstants.integrationHubProviders);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => IntegrationProvider.fromJson(json)).toList();
    }
    throw Exception('Failed to load providers');
  }

  Future<IntegrationProvider> getProvider(String id) async {
    final response = await _apiClient.get('${ApiConstants.integrationHubProviders}$id/');
    if (response.statusCode == 200) {
      return IntegrationProvider.fromJson(response.data);
    }
    throw Exception('Failed to load provider');
  }

  // ==================== Integrations ====================
  Future<List<Integration>> getIntegrations() async {
    final response = await _apiClient.get(ApiConstants.integrationHubIntegrations);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => Integration.fromJson(json)).toList();
    }
    throw Exception('Failed to load integrations');
  }

  Future<Integration> getIntegration(String id) async {
    final response = await _apiClient.get('${ApiConstants.integrationHubIntegrations}$id/');
    if (response.statusCode == 200) {
      return Integration.fromJson(response.data);
    }
    throw Exception('Failed to load integration');
  }

  Future<Integration> createIntegration(Map<String, dynamic> data) async {
    final response = await _apiClient.post(ApiConstants.integrationHubIntegrations, data: data);
    if (response.statusCode == 201) {
      return Integration.fromJson(response.data);
    }
    throw Exception('Failed to create integration');
  }

  Future<void> deleteIntegration(String id) async {
    final response = await _apiClient.delete('${ApiConstants.integrationHubIntegrations}$id/');
    if (response.statusCode != 204) {
      throw Exception('Failed to delete integration');
    }
  }

  Future<Map<String, dynamic>> initiateAuth(String id) async {
    final response = await _apiClient.post(ApiConstants.integrationInitiateAuth(id));
    if (response.statusCode == 200) {
      return response.data;
    }
    throw Exception('Failed to initiate auth');
  }

  Future<Map<String, dynamic>> testConnection(String id) async {
    final response = await _apiClient.post(ApiConstants.integrationTestConnection(id));
    if (response.statusCode == 200) {
      return response.data;
    }
    throw Exception('Failed to test connection');
  }

  Future<void> syncNow(String id) async {
    final response = await _apiClient.post(ApiConstants.integrationSyncNow(id));
    if (response.statusCode != 200 && response.statusCode != 202) {
      throw Exception('Failed to start sync');
    }
  }

  // ==================== Sync History ====================
  Future<List<SyncHistory>> getSyncHistory({String? integrationId}) async {
    final params = integrationId != null ? {'integration': integrationId} : null;
    final response = await _apiClient.get(ApiConstants.syncHistory, queryParameters: params);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => SyncHistory.fromJson(json)).toList();
    }
    throw Exception('Failed to load sync history');
  }
}

/// Service for AI Insights features
class AIInsightsService {
  final ApiClient _apiClient;

  AIInsightsService(this._apiClient);

  // ==================== Churn Predictions ====================
  Future<List<ChurnPrediction>> getChurnPredictions() async {
    final response = await _apiClient.get(ApiConstants.churnPredictions);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => ChurnPrediction.fromJson(json)).toList();
    }
    throw Exception('Failed to load churn predictions');
  }

  Future<Map<String, dynamic>> getChurnStatistics() async {
    final response = await _apiClient.get(ApiConstants.churnStatistics);
    if (response.statusCode == 200) {
      return response.data;
    }
    throw Exception('Failed to load churn statistics');
  }

  Future<List<ChurnPrediction>> getHighRiskContacts() async {
    final response = await _apiClient.get(ApiConstants.churnHighRisk);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => ChurnPrediction.fromJson(json)).toList();
    }
    throw Exception('Failed to load high risk contacts');
  }

  Future<void> bulkPredictChurn() async {
    final response = await _apiClient.post(ApiConstants.churnBulkPredict);
    if (response.statusCode != 200 && response.statusCode != 202) {
      throw Exception('Failed to run bulk prediction');
    }
  }

  Future<ChurnPrediction> predictChurn(String contactId) async {
    final response = await _apiClient.post(ApiConstants.churnPredictions, data: {'contact_id': contactId});
    if (response.statusCode == 201) {
      return ChurnPrediction.fromJson(response.data);
    }
    throw Exception('Failed to predict churn');
  }

  // ==================== Next Best Actions ====================
  Future<List<NextBestAction>> getNextBestActions() async {
    final response = await _apiClient.get(ApiConstants.nextBestActions);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => NextBestAction.fromJson(json)).toList();
    }
    throw Exception('Failed to load next best actions');
  }

  Future<void> completeAction(String id) async {
    final response = await _apiClient.post(ApiConstants.completeAction(id));
    if (response.statusCode != 200) {
      throw Exception('Failed to complete action');
    }
  }

  Future<void> dismissAction(String id) async {
    final response = await _apiClient.post(ApiConstants.dismissAction(id));
    if (response.statusCode != 200) {
      throw Exception('Failed to dismiss action');
    }
  }

  // ==================== AI Generated Content ====================
  Future<List<AIGeneratedContent>> getGeneratedContent() async {
    final response = await _apiClient.get(ApiConstants.generatedContent);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => AIGeneratedContent.fromJson(json)).toList();
    }
    throw Exception('Failed to load generated content');
  }

  Future<AIGeneratedContent> generateContent({
    required String contentType,
    required Map<String, dynamic> context,
    String? tone,
    String? length,
  }) async {
    final response = await _apiClient.post(ApiConstants.generatedContent, data: {
      'content_type': contentType,
      'context': context,
      if (tone != null) 'tone': tone,
      if (length != null) 'length': length,
    });
    if (response.statusCode == 201) {
      return AIGeneratedContent.fromJson(response.data);
    }
    throw Exception('Failed to generate content');
  }

  Future<AIGeneratedContent> regenerateContent(String id, {String? tone}) async {
    final response = await _apiClient.post(
      ApiConstants.regenerateContent(id),
      data: tone != null ? {'tone': tone} : null,
    );
    if (response.statusCode == 200) {
      return AIGeneratedContent.fromJson(response.data);
    }
    throw Exception('Failed to regenerate content');
  }

  Future<void> approveContent(String id) async {
    final response = await _apiClient.post(ApiConstants.approveContent(id));
    if (response.statusCode != 200) {
      throw Exception('Failed to approve content');
    }
  }

  // ==================== Sentiment Analysis ====================
  Future<List<SentimentAnalysis>> getSentimentAnalysis() async {
    final response = await _apiClient.get(ApiConstants.sentimentAnalysis);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => SentimentAnalysis.fromJson(json)).toList();
    }
    throw Exception('Failed to load sentiment analysis');
  }

  Future<SentimentAnalysis> analyzeSentiment(String text, {String? sourceType, String? sourceId}) async {
    final response = await _apiClient.post(ApiConstants.sentimentAnalysis, data: {
      'text': text,
      if (sourceType != null) 'source_type': sourceType,
      if (sourceId != null) 'source_id': sourceId,
    });
    if (response.statusCode == 201) {
      return SentimentAnalysis.fromJson(response.data);
    }
    throw Exception('Failed to analyze sentiment');
  }
}

/// Service for Gamification features
class GamificationService {
  final ApiClient _apiClient;

  GamificationService(this._apiClient);

  // ==================== Achievements ====================
  Future<List<Achievement>> getAchievements() async {
    final response = await _apiClient.get(ApiConstants.achievements);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => Achievement.fromJson(json)).toList();
    }
    throw Exception('Failed to load achievements');
  }

  Future<List<Achievement>> getMyAchievements() async {
    final response = await _apiClient.get(ApiConstants.myAchievements);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => Achievement.fromJson(json)).toList();
    }
    throw Exception('Failed to load my achievements');
  }

  // ==================== User Points ====================
  Future<UserPoints> getMyPoints() async {
    final response = await _apiClient.get(ApiConstants.myPoints);
    if (response.statusCode == 200) {
      return UserPoints.fromJson(response.data);
    }
    throw Exception('Failed to load my points');
  }

  Future<List<PointTransaction>> getPointsHistory() async {
    final response = await _apiClient.get(ApiConstants.pointsHistory);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => PointTransaction.fromJson(json)).toList();
    }
    throw Exception('Failed to load points history');
  }

  // ==================== Leaderboards ====================
  Future<List<Leaderboard>> getLeaderboards() async {
    final response = await _apiClient.get(ApiConstants.leaderboards);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => Leaderboard.fromJson(json)).toList();
    }
    throw Exception('Failed to load leaderboards');
  }

  Future<List<LeaderboardEntry>> getLeaderboardRankings(String id) async {
    final response = await _apiClient.get(ApiConstants.leaderboardRankings(id));
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['rankings'] ?? [];
      return data.map((json) => LeaderboardEntry.fromJson(json)).toList();
    }
    throw Exception('Failed to load rankings');
  }

  Future<LeaderboardEntry?> getMyRanking(String leaderboardId) async {
    final response = await _apiClient.get(ApiConstants.myRanking(leaderboardId));
    if (response.statusCode == 200) {
      return LeaderboardEntry.fromJson(response.data);
    }
    return null;
  }

  // ==================== Challenges ====================
  Future<List<Challenge>> getChallenges() async {
    final response = await _apiClient.get(ApiConstants.challenges);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => Challenge.fromJson(json)).toList();
    }
    throw Exception('Failed to load challenges');
  }

  Future<List<Challenge>> getMyChallenges() async {
    final response = await _apiClient.get(ApiConstants.myChallenges);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => Challenge.fromJson(json)).toList();
    }
    throw Exception('Failed to load my challenges');
  }

  Future<void> joinChallenge(String id) async {
    final response = await _apiClient.post(ApiConstants.joinChallenge(id));
    if (response.statusCode != 200) {
      throw Exception('Failed to join challenge');
    }
  }

  Future<void> leaveChallenge(String id) async {
    final response = await _apiClient.post(ApiConstants.leaveChallenge(id));
    if (response.statusCode != 200) {
      throw Exception('Failed to leave challenge');
    }
  }

  // ==================== Transactions ====================
  Future<List<PointTransaction>> getMyTransactions() async {
    final response = await _apiClient.get(ApiConstants.myTransactions);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => PointTransaction.fromJson(json)).toList();
    }
    throw Exception('Failed to load transactions');
  }
}

/// Service for Revenue Intelligence features
class RevenueIntelligenceService {
  final ApiClient _apiClient;

  RevenueIntelligenceService(this._apiClient);

  Future<List<RevenueTarget>> getTargets() async {
    final response = await _apiClient.get(ApiConstants.revenueTargets);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => RevenueTarget.fromJson(json)).toList();
    }
    throw Exception('Failed to load targets');
  }

  Future<List<DealScore>> getDealScores() async {
    final response = await _apiClient.get(ApiConstants.dealScores);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => DealScore.fromJson(json)).toList();
    }
    throw Exception('Failed to load deal scores');
  }

  Future<void> bulkScoreDeals() async {
    final response = await _apiClient.post(ApiConstants.dealScoresBulkScore);
    if (response.statusCode != 200 && response.statusCode != 202) {
      throw Exception('Failed to score deals');
    }
  }

  Future<List<DealRiskAlert>> getRiskAlerts() async {
    final response = await _apiClient.get(ApiConstants.riskAlerts);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => DealRiskAlert.fromJson(json)).toList();
    }
    throw Exception('Failed to load risk alerts');
  }

  Future<void> acknowledgeAlert(String id) async {
    final response = await _apiClient.post(ApiConstants.acknowledgeAlert(id));
    if (response.statusCode != 200) {
      throw Exception('Failed to acknowledge alert');
    }
  }

  Future<void> resolveAlert(String id, String resolutionNotes) async {
    final response = await _apiClient.post(
      ApiConstants.resolveAlert(id),
      data: {'resolution_notes': resolutionNotes},
    );
    if (response.statusCode != 200) {
      throw Exception('Failed to resolve alert');
    }
  }

  Future<Map<String, dynamic>> getWinLossAnalysis({String? period}) async {
    final response = await _apiClient.get(
      ApiConstants.winLossAnalysis,
      queryParameters: period != null ? {'period': period} : null,
    );
    if (response.statusCode == 200) {
      return response.data;
    }
    throw Exception('Failed to load win/loss analysis');
  }
}

/// Service for Campaign Management
class CampaignService {
  final ApiClient _apiClient;

  CampaignService(this._apiClient);

  Future<List<Campaign>> getCampaigns() async {
    final response = await _apiClient.get(ApiConstants.campaigns);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => Campaign.fromJson(json)).toList();
    }
    throw Exception('Failed to load campaigns');
  }

  Future<Campaign> getCampaign(String id) async {
    final response = await _apiClient.get(ApiConstants.campaignDetail(id));
    if (response.statusCode == 200) {
      return Campaign.fromJson(response.data);
    }
    throw Exception('Failed to load campaign');
  }

  Future<Campaign> createCampaign(Map<String, dynamic> data) async {
    final response = await _apiClient.post(ApiConstants.campaigns, data: data);
    if (response.statusCode == 201) {
      return Campaign.fromJson(response.data);
    }
    throw Exception('Failed to create campaign');
  }

  Future<void> scheduleCampaign(String id, DateTime scheduledAt) async {
    final response = await _apiClient.post(
      ApiConstants.campaignSchedule(id),
      data: {'scheduled_at': scheduledAt.toIso8601String()},
    );
    if (response.statusCode != 200) {
      throw Exception('Failed to schedule campaign');
    }
  }

  Future<void> sendCampaignNow(String id) async {
    final response = await _apiClient.post(ApiConstants.campaignSendNow(id));
    if (response.statusCode != 200) {
      throw Exception('Failed to send campaign');
    }
  }

  Future<Map<String, dynamic>> getCampaignAnalytics(String id) async {
    final response = await _apiClient.get(ApiConstants.campaignAnalytics(id));
    if (response.statusCode == 200) {
      return response.data;
    }
    throw Exception('Failed to load analytics');
  }
}

/// Service for Email Tracking
class EmailTrackingService {
  final ApiClient _apiClient;

  EmailTrackingService(this._apiClient);

  Future<List<TrackedEmail>> getTrackedEmails() async {
    final response = await _apiClient.get(ApiConstants.trackedEmails);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => TrackedEmail.fromJson(json)).toList();
    }
    throw Exception('Failed to load tracked emails');
  }

  Future<TrackedEmail> sendEmail({
    required String toEmail,
    required String subject,
    required String body,
    String? templateId,
  }) async {
    final response = await _apiClient.post(ApiConstants.trackedEmails, data: {
      'to_email': toEmail,
      'subject': subject,
      'body': body,
      if (templateId != null) 'template_id': templateId,
    });
    if (response.statusCode == 201) {
      return TrackedEmail.fromJson(response.data);
    }
    throw Exception('Failed to send email');
  }

  Future<List<EmailSequence>> getSequences() async {
    final response = await _apiClient.get(ApiConstants.emailSequences);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => EmailSequence.fromJson(json)).toList();
    }
    throw Exception('Failed to load sequences');
  }

  Future<void> activateSequence(String id) async {
    final response = await _apiClient.post(ApiConstants.activateSequence(id));
    if (response.statusCode != 200) {
      throw Exception('Failed to activate sequence');
    }
  }

  Future<void> pauseSequence(String id) async {
    final response = await _apiClient.post(ApiConstants.pauseSequence(id));
    if (response.statusCode != 200) {
      throw Exception('Failed to pause sequence');
    }
  }

  Future<Map<String, dynamic>> getAnalytics({String? period}) async {
    final response = await _apiClient.get(
      ApiConstants.emailAnalytics,
      queryParameters: period != null ? {'period': period} : null,
    );
    if (response.statusCode == 200) {
      return response.data;
    }
    throw Exception('Failed to load analytics');
  }
}

/// Service for Smart Scheduling
class SchedulingService {
  final ApiClient _apiClient;

  SchedulingService(this._apiClient);

  Future<List<SchedulingPage>> getPages() async {
    final response = await _apiClient.get(ApiConstants.schedulingPages);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => SchedulingPage.fromJson(json)).toList();
    }
    throw Exception('Failed to load scheduling pages');
  }

  Future<List<ScheduledMeeting>> getMeetings() async {
    final response = await _apiClient.get(ApiConstants.scheduledMeetings);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => ScheduledMeeting.fromJson(json)).toList();
    }
    throw Exception('Failed to load meetings');
  }

  Future<ScheduledMeeting> bookMeeting({
    required String meetingTypeId,
    required DateTime startTime,
    required String attendeeName,
    required String attendeeEmail,
    String? notes,
  }) async {
    final response = await _apiClient.post(ApiConstants.scheduledMeetings, data: {
      'meeting_type_id': meetingTypeId,
      'start_time': startTime.toIso8601String(),
      'attendee_name': attendeeName,
      'attendee_email': attendeeEmail,
      if (notes != null) 'notes': notes,
    });
    if (response.statusCode == 201) {
      return ScheduledMeeting.fromJson(response.data);
    }
    throw Exception('Failed to book meeting');
  }

  Future<void> cancelMeeting(String id, {String? reason}) async {
    final response = await _apiClient.post(
      ApiConstants.cancelMeeting(id),
      data: reason != null ? {'reason': reason} : null,
    );
    if (response.statusCode != 200) {
      throw Exception('Failed to cancel meeting');
    }
  }
}

/// Service for Customer Success
class CustomerSuccessService {
  final ApiClient _apiClient;

  CustomerSuccessService(this._apiClient);

  Future<List<CustomerAccount>> getAccounts() async {
    final response = await _apiClient.get(ApiConstants.csAccounts);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => CustomerAccount.fromJson(json)).toList();
    }
    throw Exception('Failed to load accounts');
  }

  Future<Map<String, dynamic>> getAccountHealth(String id) async {
    final response = await _apiClient.get(ApiConstants.accountHealth(id));
    if (response.statusCode == 200) {
      return response.data;
    }
    throw Exception('Failed to load account health');
  }

  Future<Map<String, dynamic>> getDashboard({String? period}) async {
    final response = await _apiClient.get(
      ApiConstants.csDashboard,
      queryParameters: period != null ? {'period': period} : null,
    );
    if (response.statusCode == 200) {
      return response.data;
    }
    throw Exception('Failed to load dashboard');
  }

  Future<Map<String, dynamic>> getMetrics({String? period}) async {
    final response = await _apiClient.get(
      ApiConstants.csMetrics,
      queryParameters: period != null ? {'period': period} : null,
    );
    if (response.statusCode == 200) {
      return response.data;
    }
    throw Exception('Failed to load metrics');
  }
}

/// Service for Document E-Sign
class DocumentEsignService {
  final ApiClient _apiClient;

  DocumentEsignService(this._apiClient);

  Future<List<EsignDocument>> getDocuments() async {
    final response = await _apiClient.get(ApiConstants.esignDocuments);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => EsignDocument.fromJson(json)).toList();
    }
    throw Exception('Failed to load documents');
  }

  Future<EsignDocument> createDocument({
    required String templateId,
    required String name,
    Map<String, dynamic>? data,
  }) async {
    final response = await _apiClient.post(ApiConstants.esignDocuments, data: {
      'template_id': templateId,
      'name': name,
      if (data != null) 'data': data,
    });
    if (response.statusCode == 201) {
      return EsignDocument.fromJson(response.data);
    }
    throw Exception('Failed to create document');
  }

  Future<void> sendForSignature(String id, List<Map<String, String>> recipients) async {
    final response = await _apiClient.post(
      ApiConstants.sendForSignature(id),
      data: {'recipients': recipients},
    );
    if (response.statusCode != 200) {
      throw Exception('Failed to send for signature');
    }
  }

  Future<Map<String, dynamic>> getAnalytics({String? period}) async {
    final response = await _apiClient.get(
      ApiConstants.esignAnalytics,
      queryParameters: period != null ? {'period': period} : null,
    );
    if (response.statusCode == 200) {
      return response.data;
    }
    throw Exception('Failed to load analytics');
  }
}

/// Service for Notifications
class NotificationService {
  final ApiClient _apiClient;

  NotificationService(this._apiClient);

  Future<List<AppNotification>> getNotifications() async {
    final response = await _apiClient.get(ApiConstants.notifications);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => AppNotification.fromJson(json)).toList();
    }
    throw Exception('Failed to load notifications');
  }

  Future<int> getUnreadCount() async {
    final response = await _apiClient.get(ApiConstants.notificationsUnreadCount);
    if (response.statusCode == 200) {
      return response.data['count'] ?? 0;
    }
    throw Exception('Failed to load unread count');
  }

  Future<void> markAsRead(String id) async {
    final response = await _apiClient.post('${ApiConstants.notifications}$id/mark_read/');
    if (response.statusCode != 200) {
      throw Exception('Failed to mark as read');
    }
  }

  Future<void> markAllAsRead() async {
    final response = await _apiClient.post('${ApiConstants.notifications}mark_all_read/');
    if (response.statusCode != 200) {
      throw Exception('Failed to mark all as read');
    }
  }
}
