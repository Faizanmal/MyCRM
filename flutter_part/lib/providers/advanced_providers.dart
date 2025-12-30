import 'package:flutter/foundation.dart';
import '../core/utils/api_client.dart';
import '../models/advanced_models.dart';
import '../services/advanced_services.dart';

/// Provider for AI Insights state management
class AIInsightsProvider extends ChangeNotifier {
  final AIInsightsService _service;
  
  List<ChurnPrediction> _churnPredictions = [];
  List<NextBestAction> _nextBestActions = [];
  List<AIGeneratedContent> _generatedContent = [];
  Map<String, dynamic>? _churnStatistics;
  
  bool _isLoading = false;
  String? _error;

  AIInsightsProvider(ApiClient apiClient) : _service = AIInsightsService(apiClient);

  List<ChurnPrediction> get churnPredictions => _churnPredictions;
  List<NextBestAction> get nextBestActions => _nextBestActions;
  List<AIGeneratedContent> get generatedContent => _generatedContent;
  Map<String, dynamic>? get churnStatistics => _churnStatistics;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> loadChurnPredictions() async {
    _setLoading(true);
    try {
      _churnPredictions = await _service.getChurnPredictions();
      _error = null;
    } catch (e) {
      _error = e.toString();
    }
    _setLoading(false);
  }

  Future<void> loadChurnStatistics() async {
    try {
      _churnStatistics = await _service.getChurnStatistics();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> runBulkChurnPrediction() async {
    _setLoading(true);
    try {
      await _service.bulkPredictChurn();
      await loadChurnPredictions();
      _error = null;
    } catch (e) {
      _error = e.toString();
    }
    _setLoading(false);
  }

  Future<void> loadNextBestActions() async {
    _setLoading(true);
    try {
      _nextBestActions = await _service.getNextBestActions();
      _error = null;
    } catch (e) {
      _error = e.toString();
    }
    _setLoading(false);
  }

  Future<void> completeAction(String id) async {
    try {
      await _service.completeAction(id);
      _nextBestActions = _nextBestActions.where((a) => a.id != id).toList();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> dismissAction(String id) async {
    try {
      await _service.dismissAction(id);
      _nextBestActions = _nextBestActions.where((a) => a.id != id).toList();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadGeneratedContent() async {
    _setLoading(true);
    try {
      _generatedContent = await _service.getGeneratedContent();
      _error = null;
    } catch (e) {
      _error = e.toString();
    }
    _setLoading(false);
  }

  Future<AIGeneratedContent?> generateContent({
    required String contentType,
    required Map<String, dynamic> context,
    String? tone,
    String? length,
  }) async {
    _setLoading(true);
    try {
      final content = await _service.generateContent(
        contentType: contentType,
        context: context,
        tone: tone,
        length: length,
      );
      _generatedContent.insert(0, content);
      _error = null;
      _setLoading(false);
      return content;
    } catch (e) {
      _error = e.toString();
      _setLoading(false);
      return null;
    }
  }

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }

  Future<void> regenerateContent(String id, {String? tone}) async {
    _setLoading(true);
    try {
      final content = await _service.regenerateContent(id, tone: tone);
      final index = _generatedContent.indexWhere((c) => c.id == id);
      if (index != -1) {
        _generatedContent[index] = content;
      }
      _error = null;
    } catch (e) {
      _error = e.toString();
    }
    _setLoading(false);
  }

  Future<void> approveContent(String id) async {
    try {
      await _service.approveContent(id);
      await loadGeneratedContent();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }
}

/// Provider for Gamification state management
class GamificationProvider extends ChangeNotifier {
  final GamificationService _service;
  
  List<Achievement> _achievements = [];
  List<Achievement> _myAchievements = [];
  UserPoints? _myPoints;
  List<Leaderboard> _leaderboards = [];
  List<Challenge> _challenges = [];
  List<Challenge> _myChallenges = [];
  List<PointTransaction> _transactions = [];
  
  bool _isLoading = false;
  String? _error;

  GamificationProvider(ApiClient apiClient) : _service = GamificationService(apiClient);

  List<Achievement> get achievements => _achievements;
  List<Achievement> get myAchievements => _myAchievements;
  UserPoints? get myPoints => _myPoints;
  List<Leaderboard> get leaderboards => _leaderboards;
  List<Challenge> get challenges => _challenges;
  List<Challenge> get myChallenges => _myChallenges;
  List<PointTransaction> get transactions => _transactions;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> loadAll() async {
    _setLoading(true);
    try {
      await Future.wait([
        loadMyPoints(),
        loadAchievements(),
        loadLeaderboards(),
        loadChallenges(),
      ]);
    } finally {
      _setLoading(false);
    }
  }

  Future<void> loadMyPoints() async {
    try {
      _myPoints = await _service.getMyPoints();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadAchievements() async {
    try {
      _achievements = await _service.getAchievements();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadMyAchievements() async {
    try {
      _myAchievements = await _service.getMyAchievements();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadLeaderboards() async {
    try {
      _leaderboards = await _service.getLeaderboards();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<List<LeaderboardEntry>> loadLeaderboardRankings(String id) async {
    try {
      return await _service.getLeaderboardRankings(id);
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return [];
    }
  }

  Future<void> loadChallenges() async {
    try {
      _challenges = await _service.getChallenges();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadMyChallenges() async {
    try {
      _myChallenges = await _service.getMyChallenges();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> joinChallenge(String id) async {
    try {
      await _service.joinChallenge(id);
      await loadChallenges();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> leaveChallenge(String id) async {
    try {
      await _service.leaveChallenge(id);
      await loadChallenges();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadTransactions() async {
    try {
      _transactions = await _service.getMyTransactions();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }
}

/// Provider for Integration Hub state management
class IntegrationHubProvider extends ChangeNotifier {
  final IntegrationHubService _service;
  
  List<IntegrationProvider> _providers = [];
  List<Integration> _integrations = [];
  List<SyncHistory> _syncHistory = [];
  
  bool _isLoading = false;
  String? _error;

  IntegrationHubProvider(ApiClient apiClient) : _service = IntegrationHubService(apiClient);

  List<IntegrationProvider> get providers => _providers;
  List<Integration> get integrations => _integrations;
  List<SyncHistory> get syncHistory => _syncHistory;
  bool get isLoading => _isLoading;
  String? get error => _error;

  List<Integration> get activeIntegrations => 
      _integrations.where((i) => i.status == 'connected').toList();
  
  List<IntegrationProvider> get availableProviders {
    final connectedSlugs = _integrations.map((i) => i.provider?.slug).toSet();
    return _providers.where((p) => !connectedSlugs.contains(p.slug)).toList();
  }

  Future<void> loadAll() async {
    _setLoading(true);
    try {
      await Future.wait([
        loadProviders(),
        loadIntegrations(),
      ]);
    } finally {
      _setLoading(false);
    }
  }

  Future<void> loadProviders() async {
    try {
      _providers = await _service.getProviders();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadIntegrations() async {
    try {
      _integrations = await _service.getIntegrations();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<String?> connectIntegration(String providerId, String name) async {
    try {
      final integration = await _service.createIntegration({
        'provider': providerId,
        'name': name,
      });
      
      // Try to get auth URL
      final authResult = await _service.initiateAuth(integration.id);
      await loadIntegrations();
      return authResult['auth_url'] as String?;
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return null;
    }
  }

  Future<void> disconnectIntegration(String id) async {
    try {
      await _service.deleteIntegration(id);
      _integrations = _integrations.where((i) => i.id != id).toList();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<bool> testConnection(String id) async {
    try {
      final result = await _service.testConnection(id);
      return result['success'] == true;
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return false;
    }
  }

  Future<void> syncNow(String id) async {
    try {
      await _service.syncNow(id);
      await loadIntegrations();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadSyncHistory({String? integrationId}) async {
    try {
      _syncHistory = await _service.getSyncHistory(integrationId: integrationId);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }
}

/// Provider for Revenue Intelligence
class RevenueIntelligenceProvider extends ChangeNotifier {
  final RevenueIntelligenceService _service;
  
  List<RevenueTarget> _targets = [];
  List<DealScore> _dealScores = [];
  List<DealRiskAlert> _riskAlerts = [];
  Map<String, dynamic>? _winLossAnalysis;
  
  bool _isLoading = false;
  String? _error;

  RevenueIntelligenceProvider(ApiClient apiClient) : _service = RevenueIntelligenceService(apiClient);

  List<RevenueTarget> get targets => _targets;
  List<DealScore> get dealScores => _dealScores;
  List<DealRiskAlert> get riskAlerts => _riskAlerts;
  List<DealRiskAlert> get activeAlerts => _riskAlerts.where((a) => !a.isResolved).toList();
  Map<String, dynamic>? get winLossAnalysis => _winLossAnalysis;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> loadAll() async {
    _setLoading(true);
    try {
      await Future.wait([
        loadTargets(),
        loadDealScores(),
        loadRiskAlerts(),
      ]);
    } finally {
      _setLoading(false);
    }
  }

  Future<void> loadTargets() async {
    try {
      _targets = await _service.getTargets();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadDealScores() async {
    try {
      _dealScores = await _service.getDealScores();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadRiskAlerts() async {
    try {
      _riskAlerts = await _service.getRiskAlerts();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> bulkScoreDeals() async {
    _setLoading(true);
    try {
      await _service.bulkScoreDeals();
      await loadDealScores();
    } finally {
      _setLoading(false);
    }
  }

  Future<void> acknowledgeAlert(String id) async {
    try {
      await _service.acknowledgeAlert(id);
      await loadRiskAlerts();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadWinLossAnalysis({String? period}) async {
    try {
      _winLossAnalysis = await _service.getWinLossAnalysis(period: period);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }
}

/// Provider for Campaign Management
class CampaignProvider extends ChangeNotifier {
  final CampaignService _service;
  
  List<Campaign> _campaigns = [];
  Campaign? _selectedCampaign;
  Map<String, dynamic>? _campaignAnalytics;
  
  bool _isLoading = false;
  String? _error;

  CampaignProvider(ApiClient apiClient) : _service = CampaignService(apiClient);

  List<Campaign> get campaigns => _campaigns;
  Campaign? get selectedCampaign => _selectedCampaign;
  Map<String, dynamic>? get campaignAnalytics => _campaignAnalytics;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> loadCampaigns() async {
    _setLoading(true);
    try {
      _campaigns = await _service.getCampaigns();
      _error = null;
    } catch (e) {
      _error = e.toString();
    }
    _setLoading(false);
  }

  Future<void> loadCampaign(String id) async {
    _setLoading(true);
    try {
      _selectedCampaign = await _service.getCampaign(id);
      _error = null;
    } catch (e) {
      _error = e.toString();
    }
    _setLoading(false);
  }

  Future<Campaign?> createCampaign(Map<String, dynamic> data) async {
    _setLoading(true);
    try {
      final campaign = await _service.createCampaign(data);
      _campaigns.insert(0, campaign);
      _error = null;
      _setLoading(false);
      return campaign;
    } catch (e) {
      _error = e.toString();
      _setLoading(false);
      return null;
    }
  }

  Future<void> sendCampaign(String id) async {
    try {
      await _service.sendCampaignNow(id);
      await loadCampaigns();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadCampaignAnalytics(String id) async {
    try {
      _campaignAnalytics = await _service.getCampaignAnalytics(id);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }
}

/// Provider for Notifications
class NotificationProvider extends ChangeNotifier {
  final NotificationService _service;
  
  List<AppNotification> _notifications = [];
  int _unreadCount = 0;
  
  bool _isLoading = false;
  String? _error;

  NotificationProvider(ApiClient apiClient) : _service = NotificationService(apiClient);

  List<AppNotification> get notifications => _notifications;
  int get unreadCount => _unreadCount;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> loadNotifications() async {
    _setLoading(true);
    try {
      _notifications = await _service.getNotifications();
      _error = null;
    } catch (e) {
      _error = e.toString();
    }
    _setLoading(false);
  }

  Future<void> loadUnreadCount() async {
    try {
      _unreadCount = await _service.getUnreadCount();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> markAsRead(String id) async {
    try {
      await _service.markAsRead(id);
      final index = _notifications.indexWhere((n) => n.id == id);
      if (index != -1 && !_notifications[index].isRead) {
        _unreadCount = (_unreadCount - 1).clamp(0, _unreadCount);
      }
      await loadNotifications();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> markAllAsRead() async {
    try {
      await _service.markAllAsRead();
      _unreadCount = 0;
      await loadNotifications();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }
}
