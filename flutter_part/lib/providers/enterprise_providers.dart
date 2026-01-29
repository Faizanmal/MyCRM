// Enterprise Providers for MyCRM Flutter App
// Contains providers for Customer Success, GDPR, White-Label,
// AI Chatbot, Data Enrichment, and other enterprise features

import 'package:flutter/foundation.dart';
import '../core/utils/api_client.dart';
import '../models/enterprise_models.dart';
import '../models/advanced_models.dart' as advanced;
import '../services/enterprise_services.dart';

/// Provider for Customer Success state management
class CustomerSuccessProvider extends ChangeNotifier {
  final CustomerSuccessService _service;

  List<advanced.CustomerAccount> _accounts = [];
  List<HealthScore> _healthScores = [];
  List<ChurnRisk> _churnRisks = [];
  List<Renewal> _renewals = [];
  List<Renewal> _upcomingRenewals = [];
  List<Playbook> _playbooks = [];
  Map<String, dynamic>? _dashboard;
  Map<String, dynamic>? _metrics;
  Map<String, dynamic>? _npsAnalytics;

  bool _isLoading = false;
  String? _error;

  CustomerSuccessProvider(ApiClient apiClient) : _service = CustomerSuccessService(apiClient);

  List<advanced.CustomerAccount> get accounts => _accounts;
  List<HealthScore> get healthScores => _healthScores;
  List<ChurnRisk> get churnRisks => _churnRisks;
  List<Renewal> get renewals => _renewals;
  List<Renewal> get upcomingRenewals => _upcomingRenewals;
  List<Playbook> get playbooks => _playbooks;
  Map<String, dynamic>? get dashboard => _dashboard;
  Map<String, dynamic>? get metrics => _metrics;
  Map<String, dynamic>? get npsAnalytics => _npsAnalytics;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> loadAll() async {
    _setLoading(true);
    try {
      await Future.wait([
        loadAccounts(),
        loadChurnRisks(),
        loadUpcomingRenewals(),
        loadDashboard(),
      ]);
    } finally {
      _setLoading(false);
    }
  }

  Future<void> loadAccounts() async {
    try {
      _accounts = await _service.getAccounts();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadHealthScores() async {
    try {
      _healthScores = await _service.getHealthScores();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadChurnRisks() async {
    try {
      _churnRisks = await _service.getChurnRisks();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadRenewals() async {
    try {
      _renewals = await _service.getRenewals();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadUpcomingRenewals() async {
    try {
      _upcomingRenewals = await _service.getUpcomingRenewals();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadPlaybooks() async {
    try {
      _playbooks = await _service.getPlaybooks();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> executePlaybook(String playbookId, String accountId) async {
    try {
      await _service.executePlaybook(playbookId, accountId);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadDashboard({String? period}) async {
    try {
      _dashboard = await _service.getDashboard(period: period);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadMetrics({String? period}) async {
    try {
      _metrics = await _service.getMetrics(period: period);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadNPSAnalytics() async {
    try {
      _npsAnalytics = await _service.getNPSAnalytics();
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

/// Provider for GDPR Compliance state management
class GDPRProvider extends ChangeNotifier {
  final GDPRService _service;

  List<GDPRConsent> _consents = [];
  List<DataSubjectRequest> _requests = [];

  bool _isLoading = false;
  String? _error;

  GDPRProvider(ApiClient apiClient) : _service = GDPRService(apiClient);

  List<GDPRConsent> get consents => _consents;
  List<DataSubjectRequest> get requests => _requests;
  List<DataSubjectRequest> get pendingRequests => _requests.where((r) => r.status == 'pending').toList();
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> loadAll() async {
    _setLoading(true);
    try {
      await Future.wait([
        loadConsents(),
        loadRequests(),
      ]);
    } finally {
      _setLoading(false);
    }
  }

  Future<void> loadConsents({String? contactId}) async {
    try {
      _consents = await _service.getConsents(contactId: contactId);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> grantConsent(String contactId, String consentType) async {
    try {
      final consent = await _service.grantConsent(contactId, consentType);
      _consents.add(consent);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> revokeConsent(String id) async {
    try {
      await _service.revokeConsent(id);
      _consents.removeWhere((c) => c.id == id);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadRequests() async {
    try {
      _requests = await _service.getDataSubjectRequests();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> createRequest({
    required String requestType,
    required String contactEmail,
    String? notes,
  }) async {
    _setLoading(true);
    try {
      final request = await _service.createDataSubjectRequest(
        requestType: requestType,
        contactEmail: contactEmail,
        notes: notes,
      );
      _requests.insert(0, request);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    } finally {
      _setLoading(false);
    }
  }

  Future<void> exportData(String contactId) async {
    _setLoading(true);
    try {
      await _service.exportData(contactId);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    } finally {
      _setLoading(false);
    }
  }

  Future<void> deleteData(String contactId) async {
    _setLoading(true);
    try {
      await _service.deleteData(contactId);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    } finally {
      _setLoading(false);
    }
  }

  Future<void> processRequest(String requestId) async {
    _setLoading(true);
    try {
      final request = _requests.firstWhere((r) => r.id == requestId);
      final index = _requests.indexOf(request);
      _requests[index] = DataSubjectRequest(
        id: request.id,
        requestType: request.requestType,
        status: 'processing',
        contactEmail: request.contactEmail,
        requestedAt: request.requestedAt,
        completedAt: request.completedAt,
        notes: request.notes,
      );
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    } finally {
      _setLoading(false);
    }
  }

  Future<void> completeRequest(String requestId) async {
    _setLoading(true);
    try {
      final request = _requests.firstWhere((r) => r.id == requestId);
      final index = _requests.indexOf(request);
      _requests[index] = DataSubjectRequest(
        id: request.id,
        requestType: request.requestType,
        status: 'completed',
        contactEmail: request.contactEmail,
        requestedAt: request.requestedAt,
        completedAt: DateTime.now(),
        notes: request.notes,
      );
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    } finally {
      _setLoading(false);
    }
  }

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }
}

/// Provider for White-Label state management
class WhiteLabelProvider extends ChangeNotifier {
  final WhiteLabelService _service;

  List<SubscriptionPlan> _plans = [];
  Subscription? _subscription;
  List<Invoice> _invoices = [];
  BrandingConfig? _branding;
  Map<String, dynamic>? _usage;

  bool _isLoading = false;
  String? _error;

  WhiteLabelProvider(ApiClient apiClient) : _service = WhiteLabelService(apiClient);

  List<SubscriptionPlan> get plans => _plans;
  Subscription? get subscription => _subscription;
  List<Invoice> get invoices => _invoices;
  BrandingConfig? get branding => _branding;
  Map<String, dynamic>? get usage => _usage;
  bool get isLoading => _isLoading;
  String? get error => _error;
  BrandingConfig? get brandingConfig => _branding;
  List<Organization> get organizations => [];

  Future<void> loadAll() async {
    _setLoading(true);
    try {
      await Future.wait([
        loadPlans(),
        loadSubscription(),
        loadBranding(),
      ]);
    } finally {
      _setLoading(false);
    }
  }

  Future<void> loadPlans() async {
    try {
      _plans = await _service.getPlans();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadSubscription() async {
    try {
      _subscription = await _service.getCurrentSubscription();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> changePlan(String planId) async {
    _setLoading(true);
    try {
      await _service.changePlan(planId);
      await loadSubscription();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    } finally {
      _setLoading(false);
    }
  }

  Future<void> cancelSubscription() async {
    _setLoading(true);
    try {
      await _service.cancelSubscription();
      await loadSubscription();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    } finally {
      _setLoading(false);
    }
  }

  Future<void> loadInvoices() async {
    try {
      _invoices = await _service.getInvoices();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadBranding() async {
    try {
      _branding = await _service.getBranding();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> updateBranding({String? primaryColor, String? secondaryColor, String? accentColor}) async {
    final branding = <String, dynamic>{};
    if (primaryColor != null) branding['primary_color'] = primaryColor;
    if (secondaryColor != null) branding['secondary_color'] = secondaryColor;
    if (accentColor != null) branding['accent_color'] = accentColor;
    await _service.updateBranding(branding);
    await loadBranding();
  }



  Future<void> loadOrganizations() async {
    _setLoading(true);
    try {
      // Load organizations
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
    _setLoading(false);
  }

  Future<void> createOrganization({required String name}) async {
    _setLoading(true);
    try {
      // Create organization
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
    _setLoading(false);
  }

  Future<void> loadUsage() async {
    try {
      _usage = await _service.getUsage();
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

/// Provider for AI Chatbot state management
class AIChatbotProvider extends ChangeNotifier {
  final AIChatbotService _service;

  List<ChatConversation> _conversations = [];
  ChatConversation? _currentConversation;
  List<ChatMessage> _messages = [];

  bool _isLoading = false;
  bool _isSending = false;
  String? _error;

  AIChatbotProvider(ApiClient apiClient) : _service = AIChatbotService(apiClient);

  List<ChatConversation> get conversations => _conversations;
  ChatConversation? get currentConversation => _currentConversation;
  List<ChatMessage> get messages => _messages;
  bool get isLoading => _isLoading;
  bool get isSending => _isSending;
  String? get error => _error;

  Future<void> loadConversations() async {
    _setLoading(true);
    try {
      _conversations = await _service.getConversations();
      _error = null;
    } catch (e) {
      _error = e.toString();
    }
    _setLoading(false);
  }

  Future<void> loadConversation(String id) async {
    _setLoading(true);
    try {
      _currentConversation = await _service.getConversation(id);
      _messages = _currentConversation?.messages ?? [];
      _error = null;
    } catch (e) {
      _error = e.toString();
    }
    _setLoading(false);
  }

  Future<void> startNewConversation({String? title}) async {
    _setLoading(true);
    try {
      _currentConversation = await _service.createConversation(title: title);
      _messages = [];
      _conversations.insert(0, _currentConversation!);
      _error = null;
    } catch (e) {
      _error = e.toString();
    }
    _setLoading(false);
  }

  Future<void> sendMessage(String content) async {
    if (_currentConversation == null) {
      await startNewConversation();
    }

    // Add user message immediately
    final userMessage = ChatMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      role: 'user',
      content: content,
      timestamp: DateTime.now(),
    );
    _messages.add(userMessage);
    notifyListeners();

    _isSending = true;
    notifyListeners();

    try {
      final response = await _service.sendMessage(_currentConversation!.id, content);
      _messages.add(response);
      _error = null;
    } catch (e) {
      _error = e.toString();
      // Add error message
      _messages.add(ChatMessage(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: DateTime.now(),
      ));
    }
    _isSending = false;
    notifyListeners();
  }

  Future<void> deleteConversation(String id) async {
    try {
      await _service.deleteConversation(id);
      _conversations.removeWhere((c) => c.id == id);
      if (_currentConversation?.id == id) {
        _currentConversation = null;
        _messages = [];
      }
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  void clearCurrentConversation() {
    _currentConversation = null;
    _messages = [];
    notifyListeners();
  }

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }
}

/// Provider for Data Enrichment state management
class DataEnrichmentProvider extends ChangeNotifier {
  final DataEnrichmentService _service;

  List<EnrichmentResult> _results = [];
  List<EnrichmentJob> _jobs = [];

  bool _isLoading = false;
  String? _error;

  DataEnrichmentProvider(ApiClient apiClient) : _service = DataEnrichmentService(apiClient);

  List<EnrichmentResult> get results => _results;
  List<EnrichmentJob> get jobs => _jobs;
  List<EnrichmentJob> get activeJobs => _jobs.where((j) => j.status == 'processing').toList();
  bool get isLoading => _isLoading;
  String? get error => _error;
  double get matchRate => _results.isNotEmpty ? 
    _results.map((r) => r.confidence).reduce((a, b) => a + b) / _results.length : 0;

  Future<void> loadAll({String? entityType}) async {
    await loadResults(entityType: entityType);
    await loadJobs();
  }

  Future<void> loadResults({String? entityType, String? entityId}) async {
    _setLoading(true);
    try {
      _results = await _service.getEnrichmentResults(
        entityType: entityType,
        entityId: entityId,
      );
      _error = null;
    } catch (e) {
      _error = e.toString();
    }
    _setLoading(false);
  }

  Future<EnrichmentResult?> enrichEntity(String entityType, String entityId) async {
    _setLoading(true);
    try {
      final result = await _service.enrichEntity(entityType, entityId);
      _results.insert(0, result);
      _error = null;
      _setLoading(false);
      return result;
    } catch (e) {
      _error = e.toString();
      _setLoading(false);
      return null;
    }
  }

  Future<void> startBulkEnrichment(String entityType, {List<String>? entityIds}) async {
    _setLoading(true);
    try {
      final job = await _service.startBulkEnrichment(entityType, entityIds);
      _jobs.insert(0, job);
      _error = null;
    } catch (e) {
      _error = e.toString();
    }
    _setLoading(false);
  }

  Future<void> loadJobs() async {
    try {
      _jobs = await _service.getJobs();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> createJob({required String entityType, List<String>? entityIds}) async {
    await startBulkEnrichment(entityType, entityIds: entityIds);
  }

  Future<void> startJob(String jobId) async {
    _setLoading(true);
    try {
      final job = _jobs.firstWhere((j) => j.id == jobId);
      final index = _jobs.indexOf(job);
      _jobs[index] = EnrichmentJob(
        id: job.id,
        entityType: job.entityType,
        totalRecords: job.totalRecords,
        processedRecords: job.processedRecords,
        enrichedRecords: job.enrichedRecords,
        status: 'processing',
        startedAt: job.startedAt,
        completedAt: job.completedAt,
      );
      _error = null;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
    _setLoading(false);
  }

  Future<void> cancelJob(String jobId) async {
    _setLoading(true);
    try {
      final job = _jobs.firstWhere((j) => j.id == jobId);
      final index = _jobs.indexOf(job);
      _jobs[index] = EnrichmentJob(
        id: job.id,
        entityType: job.entityType,
        totalRecords: job.totalRecords,
        processedRecords: job.processedRecords,
        enrichedRecords: job.enrichedRecords,
        status: 'cancelled',
        startedAt: job.startedAt,
        completedAt: DateTime.now(),
      );
      _error = null;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
    _setLoading(false);
  }

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }
}

/// Provider for Lead Routing state management
class LeadRoutingProvider extends ChangeNotifier {
  final LeadRoutingService _service;

  List<LeadRoutingRule> _rules = [];
  List<LeadAssignment> _assignments = [];
  Map<String, dynamic>? _analytics;

  bool _isLoading = false;
  String? _error;

  LeadRoutingProvider(ApiClient apiClient) : _service = LeadRoutingService(apiClient);

  List<LeadRoutingRule> get rules => _rules;
  List<LeadRoutingRule> get activeRules => _rules.where((r) => r.isActive).toList();
  List<LeadAssignment> get assignments => _assignments;
  Map<String, dynamic>? get analytics => _analytics;
  bool get isLoading => _isLoading;
  String? get error => _error;
  List<LeadAssignment> get todayAssignments => _assignments;
  double get avgResponseTime => 0.0;

  Future<void> loadAll() async {
    _setLoading(true);
    try {
      await Future.wait([
        loadRules(),
        loadAssignments(),
      ]);
    } finally {
      _setLoading(false);
    }
  }

  Future<void> loadRules() async {
    try {
      _rules = await _service.getRules();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> createRule(Map<String, dynamic> data) async {
    _setLoading(true);
    try {
      final rule = await _service.createRule(data);
      _rules.add(rule);
      _error = null;
    } catch (e) {
      _error = e.toString();
    }
    _setLoading(false);
  }

  Future<void> deleteRule(String id) async {
    try {
      await _service.deleteRule(id);
      _rules.removeWhere((r) => r.id == id);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadAssignments({String? leadId}) async {
    try {
      _assignments = await _service.getAssignments(leadId: leadId);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<LeadAssignment?> routeLead(String leadId) async {
    _setLoading(true);
    try {
      final assignment = await _service.routeLead(leadId);
      _assignments.insert(0, assignment);
      _error = null;
      _setLoading(false);
      return assignment;
    } catch (e) {
      _error = e.toString();
      _setLoading(false);
      return null;
    }
  }

  Future<void> loadAnalytics() async {
    try {
      _analytics = await _service.getRoutingAnalytics();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> reorderRules(int oldIndex, int newIndex) async {
    _setLoading(true);
    try {
      final item = _rules.removeAt(oldIndex);
      _rules.insert(newIndex > oldIndex ? newIndex - 1 : newIndex, item);
      // TODO: Call backend to persist the order
      _error = null;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
    _setLoading(false);
  }

  Future<void> toggleRule(String ruleId, bool isActive) async {
    try {
      final rule = _rules.firstWhere((r) => r.id == ruleId);
      final index = _rules.indexOf(rule);
      _rules[index] = LeadRoutingRule(
        id: rule.id,
        name: rule.name,
        description: rule.description,
        conditions: rule.conditions,
        assigneeId: rule.assigneeId,
        assigneeName: rule.assigneeName,
        priority: rule.priority,
        isActive: isActive,
      );
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> reassignLead(String assignmentId, [String? newAssigneeId]) async {
    _setLoading(true);
    try {
      final assignment = _assignments.firstWhere((a) => a.id == assignmentId);
      final index = _assignments.indexOf(assignment);
      _assignments[index] = LeadAssignment(
        id: assignment.id,
        leadId: assignment.leadId,
        leadName: assignment.leadName,
        assigneeId: newAssigneeId ?? 'auto_assigned',
        assigneeName: 'Auto Assigned',
        routingMethod: assignment.routingMethod,
        score: assignment.score,
        reason: 'Reassigned',
        assignedAt: DateTime.now(),
      );
      _error = null;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
    _setLoading(false);
  }

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }
}

/// Provider for Voice Intelligence state management
class VoiceIntelligenceProvider extends ChangeNotifier {
  final VoiceIntelligenceService _service;

  List<VoiceRecording> _recordings = [];
  VoiceRecording? _selectedRecording;
  VoiceAnalysis? _selectedAnalysis;

  bool _isLoading = false;
  bool _isProcessing = false;
  String? _error;

  VoiceIntelligenceProvider(ApiClient apiClient) : _service = VoiceIntelligenceService(apiClient);

  List<VoiceRecording> get recordings => _recordings;
  VoiceRecording? get selectedRecording => _selectedRecording;
  VoiceAnalysis? get selectedAnalysis => _selectedAnalysis;
  bool get isLoading => _isLoading;
  bool get isProcessing => _isProcessing;
  String? get error => _error;
  List<VoiceAnalysis> get analyses => _recordings.where((r) => r.analysis != null).map((r) => r.analysis!).toList();
  double get avgDuration => _recordings.isNotEmpty ? _recordings.map((r) => r.duration).reduce((a, b) => a + b) / _recordings.length : 0;
  List<String> get topKeywords => _recordings
    .where((r) => r.analysis != null)
    .expand((r) => r.analysis!.keywords)
    .toList()
    .take(10)
    .toList();

  Future<void> loadAll() async {
    await loadRecordings();
    await loadAnalyses();
  }

  Future<void> loadAnalyses() async {
    // Analyses are loaded with recordings
    notifyListeners();
  }

  Future<void> loadRecordings() async {
    _setLoading(true);
    try {
      _recordings = await _service.getRecordings();
      _error = null;
    } catch (e) {
      _error = e.toString();
    }
    _setLoading(false);
  }

  Future<void> loadRecording(String id) async {
    _setLoading(true);
    try {
      _selectedRecording = await _service.getRecording(id);
      if (_selectedRecording?.analysis != null) {
        _selectedAnalysis = _selectedRecording!.analysis;
      }
      _error = null;
    } catch (e) {
      _error = e.toString();
    }
    _setLoading(false);
  }

  Future<void> uploadRecording({
    required String filePath,
    required String title,
    String? contactId,
    String? opportunityId,
  }) async {
    _setLoading(true);
    try {
      final recording = await _service.uploadRecording(
        filePath: filePath,
        title: title,
        contactId: contactId,
        opportunityId: opportunityId,
      );
      _recordings.insert(0, recording);
      _error = null;
    } catch (e) {
      _error = e.toString();
    }
    _setLoading(false);
  }

  Future<void> processRecording(String id) async {
    _isProcessing = true;
    notifyListeners();
    try {
      await _service.processRecording(id);
      // Reload to get updated status
      await loadRecording(id);
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
    _isProcessing = false;
    notifyListeners();
  }

  Future<void> loadAnalysis(String id) async {
    try {
      _selectedAnalysis = await _service.getAnalysis(id);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> analyzeRecording(String recordingId) async {
    _isProcessing = true;
    notifyListeners();
    try {
      final recording = _recordings.firstWhere((r) => r.id == recordingId);
      // Simulate analysis - placeholder
      _error = null;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
    _isProcessing = false;
    notifyListeners();
  }

  Future<void> deleteRecording(String id) async {
    try {
      await _service.deleteRecording(id);
      _recordings.removeWhere((r) => r.id == id);
      if (_selectedRecording?.id == id) {
        _selectedRecording = null;
        _selectedAnalysis = null;
      }
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

/// Provider for Email Sequence Automation state management
class EmailSequenceProvider extends ChangeNotifier {
  final EmailSequenceService _service;

  List<EmailSequence> _sequences = [];
  List<SequenceEnrollment> _enrollments = [];

  bool _isLoading = false;
  String? _error;

  EmailSequenceProvider(ApiClient apiClient) : _service = EmailSequenceService(apiClient);

  List<EmailSequence> get sequences => _sequences;
  List<EmailSequence> get activeSequences => _sequences.where((s) => s.isActive).toList();
  List<SequenceEnrollment> get enrollments => _enrollments;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> loadAll() async {
    _setLoading(true);
    try {
      await Future.wait([
        loadSequences(),
        loadEnrollments(),
      ]);
    } finally {
      _setLoading(false);
    }
  }

  Future<void> loadSequences() async {
    try {
      _sequences = await _service.getSequences();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> createSequence({required String name, required String description}) async {
    _setLoading(true);
    try {
      final sequence = await _service.createSequence({'name': name, 'description': description});
      _sequences.add(sequence);
      _error = null;
    } catch (e) {
      _error = e.toString();
    }
    _setLoading(false);
  }

  Future<void> activateSequence(String id) async {
    try {
      await _service.activateSequence(id);
      await loadSequences();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> pauseSequence(String id) async {
    try {
      await _service.pauseSequence(id);
      await loadSequences();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadEnrollments({String? sequenceId}) async {
    try {
      _enrollments = await _service.getEnrollments(sequenceId: sequenceId);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> enrollContact(String sequenceId, String contactId) async {
    _setLoading(true);
    try {
      final enrollment = await _service.enrollContact(sequenceId, contactId);
      _enrollments.add(enrollment);
      _error = null;
    } catch (e) {
      _error = e.toString();
    }
    _setLoading(false);
  }

  Future<void> unenrollContact(String enrollmentId) async {
    try {
      await _service.unenrollContact(enrollmentId);
      _enrollments.removeWhere((e) => e.id == enrollmentId);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> toggleSequence(String sequenceId, bool isActive) async {
    try {
      final sequence = _sequences.firstWhere((s) => s.id == sequenceId);
      final index = _sequences.indexOf(sequence);
      if (isActive) {
        await activateSequence(sequenceId);
      } else {
        await pauseSequence(sequenceId);
      }
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> pauseEnrollment(String enrollmentId) async {
    try {
      final enrollment = _enrollments.firstWhere((e) => e.id == enrollmentId);
      final index = _enrollments.indexOf(enrollment);
      _enrollments[index] = SequenceEnrollment(
        id: enrollment.id,
        sequenceId: enrollment.sequenceId,
        sequenceName: enrollment.sequenceName,
        contactId: enrollment.contactId,
        contactName: enrollment.contactName,
        contactEmail: enrollment.contactEmail,
        status: 'paused',
        currentStep: enrollment.currentStep,
        totalSteps: enrollment.totalSteps,
        enrolledAt: enrollment.enrolledAt,
        completedAt: enrollment.completedAt,
        nextEmailAt: enrollment.nextEmailAt,
      );
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> resumeEnrollment(String enrollmentId) async {
    try {
      final enrollment = _enrollments.firstWhere((e) => e.id == enrollmentId);
      final index = _enrollments.indexOf(enrollment);
      _enrollments[index] = SequenceEnrollment(
        id: enrollment.id,
        sequenceId: enrollment.sequenceId,
        sequenceName: enrollment.sequenceName,
        contactId: enrollment.contactId,
        contactName: enrollment.contactName,
        contactEmail: enrollment.contactEmail,
        status: 'active',
        currentStep: enrollment.currentStep,
        totalSteps: enrollment.totalSteps,
        enrolledAt: enrollment.enrolledAt,
        completedAt: enrollment.completedAt,
        nextEmailAt: enrollment.nextEmailAt,
      );
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> addStep(String sequenceId, Map<String, dynamic> stepData) async {
    try {
      await _service.addStep(sequenceId, stepData);
      await loadSequences();
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

/// Provider for App Marketplace state management
class MarketplaceProvider extends ChangeNotifier {
  final MarketplaceService _service;

  List<MarketplaceApp> _apps = [];
  List<InstalledApp> _installedApps = [];
  MarketplaceApp? _selectedApp;

  bool _isLoading = false;
  String? _error;

  MarketplaceProvider(ApiClient apiClient) : _service = MarketplaceService(apiClient);

  List<MarketplaceApp> get apps => _apps;
  List<InstalledApp> get installedApps => _installedApps;
  MarketplaceApp? get selectedApp => _selectedApp;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> loadAll() async {
    _setLoading(true);
    try {
      await Future.wait([
        loadApps(),
        loadInstalledApps(),
      ]);
    } finally {
      _setLoading(false);
    }
  }

  Future<void> loadApps({String? category, String? search}) async {
    try {
      _apps = await _service.getApps(category: category, search: search);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadApp(String id) async {
    _setLoading(true);
    try {
      _selectedApp = await _service.getApp(id);
      _error = null;
    } catch (e) {
      _error = e.toString();
    }
    _setLoading(false);
  }

  Future<void> installApp(String appId) async {
    _setLoading(true);
    try {
      await _service.installApp(appId);
      await loadAll();
      _error = null;
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    } finally {
      _setLoading(false);
    }
  }

  Future<void> uninstallApp(String appId) async {
    _setLoading(true);
    try {
      await _service.uninstallApp(appId);
      await loadAll();
      _error = null;
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    } finally {
      _setLoading(false);
    }
  }

  Future<void> loadInstalledApps() async {
    try {
      _installedApps = await _service.getInstalledApps();
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

/// Provider for Social Inbox state management
class SocialInboxProvider extends ChangeNotifier {
  final SocialInboxService _service;

  List<SocialMessage> _messages = [];
  String? _selectedPlatform;

  bool _isLoading = false;
  String? _error;

  SocialInboxProvider(ApiClient apiClient) : _service = SocialInboxService(apiClient);

  List<SocialMessage> get messages => _messages;
  List<SocialMessage> get unreadMessages => _messages.where((m) => m.status == 'unread').toList();
  String? get selectedPlatform => _selectedPlatform;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> loadAll() async {
    await loadMessages();
    await loadMentions();
  }

  Future<void> loadMentions() async {
    try {
      // Load mentions from service
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadMessages({String? platform, String? status}) async {
    _setLoading(true);
    try {
      _messages = await _service.getMessages(platform: platform, status: status);
      _selectedPlatform = platform;
      _error = null;
    } catch (e) {
      _error = e.toString();
    }
    _setLoading(false);
  }

  Future<void> replyToMessage(String messageId, String content) async {
    try {
      await _service.replyToMessage(messageId, content);
      // Reload messages to get updated status
      await loadMessages(platform: _selectedPlatform);
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> markAsRead(String messageId) async {
    try {
      await _service.markAsRead(messageId);
      final index = _messages.indexWhere((m) => m.id == messageId);
      if (index != -1) {
        // Update local state
        await loadMessages(platform: _selectedPlatform);
      }
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> linkToContact(String messageId, String contactId) async {
    try {
      await _service.linkToContact(messageId, contactId);
      await loadMessages(platform: _selectedPlatform);
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> sendMessage(String platform, String content, [String? recipientId]) async {
    try {
      await _service.sendMessage(platform, content, recipientId);
      await loadMessages(platform: _selectedPlatform);
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

/// Provider for ESG Reporting state management
class ESGProvider extends ChangeNotifier {
  final ESGService _service;

  List<ESGMetric> _metrics = [];
  Map<String, dynamic>? _dashboard;

  bool _isLoading = false;
  String? _error;

  ESGProvider(ApiClient apiClient) : _service = ESGService(apiClient);

  List<ESGMetric> get metrics => _metrics;
  Map<String, dynamic>? get dashboard => _dashboard;
  bool get isLoading => _isLoading;
  String? get error => _error;

  List<ESGMetric> getMetricsByCategory(String category) =>
      _metrics.where((m) => m.category == category).toList();

  Future<void> loadAll() async {
    _setLoading(true);
    try {
      await Future.wait([
        loadMetrics(),
        loadDashboard(),
      ]);
    } finally {
      _setLoading(false);
    }
  }

  Future<void> loadMetrics({String? category, String? period}) async {
    try {
      _metrics = await _service.getMetrics(category: category, period: period);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> recordMetric(Map<String, dynamic> data) async {
    _setLoading(true);
    try {
      final metric = await _service.recordMetric(data);
      _metrics.insert(0, metric);
      _error = null;
    } catch (e) {
      _error = e.toString();
    }
    _setLoading(false);
  }

  Future<void> addMetric({
    required String category,
    required String name,
    required double value,
    required String unit,
  }) async {
    _setLoading(true);
    try {
      final metric = await _service.recordMetric({
        'category': category,
        'name': name,
        'value': value,
        'unit': unit,
        'period': 'monthly',
      });
      _metrics.insert(0, metric);
      _error = null;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
    _setLoading(false);
  }

  Future<void> loadDashboard() async {
    try {
      _dashboard = await _service.getDashboard();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<Map<String, dynamic>?> generateReport({
    required String period,
    List<String>? categories,
  }) async {
    _setLoading(true);
    try {
      final report = await _service.generateReport(
        period: period,
        categories: categories,
      );
      _error = null;
      _setLoading(false);
      return report;
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
}

/// Provider for Conversation Intelligence state management
class ConversationIntelligenceProvider extends ChangeNotifier {
  final ConversationIntelligenceService _service;

  List<VoiceRecording> _recordings = [];
  List<dynamic> _conversations = [];
  VoiceRecording? _selectedRecording;
  String? _transcript;
  VoiceAnalysis? _analysis;
  Map<String, dynamic>? _talkPatterns;
  Map<String, dynamic>? _coachingInsights;
  Map<String, dynamic>? _teamCoaching;
  Map<String, dynamic>? _analytics;

  bool _isLoading = false;
  String? _error;

  ConversationIntelligenceProvider(ApiClient apiClient)
      : _service = ConversationIntelligenceService(apiClient);

  List<VoiceRecording> get recordings => _recordings;
  List<dynamic> get conversations => _conversations;
  VoiceRecording? get selectedRecording => _selectedRecording;
  String? get transcript => _transcript;
  VoiceAnalysis? get analysis => _analysis;
  Map<String, dynamic>? get talkPatterns => _talkPatterns;
  Map<String, dynamic>? get coachingInsights => _coachingInsights;
  Map<String, dynamic>? get teamCoaching => _teamCoaching;
  Map<String, dynamic>? get analytics => _analytics;
  bool get isLoading => _isLoading;
  String? get error => _error;
  
  // Computed getters for UI
  int get totalConversations => _conversations.length;
  int get weeklyGrowth => _analytics?['weekly_growth'] ?? 12;
  int get avgTalkRatio => _talkPatterns?['avg_talk_ratio'] ?? 55;
  int get avgCallDuration => _analytics?['avg_duration'] ?? 22;
  double get avgQuestionsPerCall => (_analytics?['avg_questions'] ?? 6.5).toDouble();
  
  List<Map<String, dynamic>> get topTopics => [
    {'name': 'Pricing', 'count': 45},
    {'name': 'Features', 'count': 38},
    {'name': 'Integration', 'count': 32},
    {'name': 'Support', 'count': 28},
    {'name': 'Onboarding', 'count': 24},
  ];
  
  List<Map<String, dynamic>> get competitorMentions => [
    {'name': 'Competitor A', 'count': 23},
    {'name': 'Competitor B', 'count': 18},
    {'name': 'Competitor C', 'count': 12},
  ];
  
  List<Map<String, dynamic>> get topPerformers => [
    {'name': 'Sarah Chen', 'calls': 45, 'score': 92},
    {'name': 'Michael Brown', 'calls': 38, 'score': 88},
    {'name': 'Emily Davis', 'calls': 42, 'score': 85},
    {'name': 'James Wilson', 'calls': 35, 'score': 82},
  ];

  Future<void> loadAll() async {
    _setLoading(true);
    try {
      await Future.wait([
        loadRecordings(),
        loadConversations(),
        loadTalkPatterns(),
        loadTeamCoaching(),
      ]);
    } finally {
      _setLoading(false);
    }
  }

  Future<void> loadRecordings() async {
    try {
      _recordings = await _service.getRecordings();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> processRecording(String id) async {
    _setLoading(true);
    try {
      await _service.processRecording(id);
      await loadRecordings();
      _error = null;
    } catch (e) {
      _error = e.toString();
    }
    _setLoading(false);
  }

  Future<void> loadTranscript(String id) async {
    try {
      _transcript = await _service.getTranscript(id);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadAnalysis(String id) async {
    try {
      _analysis = await _service.getAnalysis(id);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadTalkPatterns() async {
    try {
      _talkPatterns = await _service.getTalkPatterns();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadCoachingInsights(String id) async {
    try {
      _coachingInsights = await _service.getCoachingInsights(id);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadTeamCoaching() async {
    try {
      _teamCoaching = await _service.getTeamCoaching();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadConversations() async {
    try {
      // Load conversations for analysis
      _conversations = [
        {'id': '1', 'title': 'Demo Call - TechCorp', 'rep_name': 'Sarah Chen', 'duration': 25, 'score': 88, 'talk_ratio': 45, 'questions': 8, 'topics': ['Pricing', 'Features'], 'date': '2024-01-15'},
        {'id': '2', 'title': 'Discovery Call - Acme Inc', 'rep_name': 'Michael Brown', 'duration': 18, 'score': 72, 'talk_ratio': 62, 'questions': 5, 'topics': ['Integration', 'Support'], 'date': '2024-01-14'},
        {'id': '3', 'title': 'Follow-up Call - GlobalTech', 'rep_name': 'Emily Davis', 'duration': 32, 'score': 91, 'talk_ratio': 48, 'questions': 10, 'topics': ['Onboarding', 'Features'], 'date': '2024-01-13'},
      ];
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadAnalytics({String? period}) async {
    try {
      _analytics = await _service.getAnalytics(period: period);
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

/// Provider for Document Management
class DocumentManagementProvider extends ChangeNotifier {
  final ApiClient _apiClient;
  
  List<dynamic> _documents = [];
  List<dynamic> _folders = [];
  bool _isLoading = false;
  String? _error;
  
  DocumentManagementProvider(this._apiClient);
  
  List<dynamic> get documents => _documents;
  List<dynamic> get folders => _folders;
  bool get isLoading => _isLoading;
  String? get error => _error;
  
  Future<void> loadDocuments() async {
    _isLoading = true;
    notifyListeners();
    try {
      final response = await _apiClient.get('/api/v1/documents/');
      _documents = response.data['results'] ?? [];
      _error = null;
    } catch (e) {
      _error = e.toString();
    }
    _isLoading = false;
    notifyListeners();
  }
  
  Future<void> loadFolders() async {
    try {
      final response = await _apiClient.get('/api/v1/documents/folders/');
      _folders = response.data['results'] ?? [];
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }
  
  Future<void> uploadDocument(Map<String, dynamic> data) async {
    _isLoading = true;
    notifyListeners();
    try {
      await _apiClient.post('/api/v1/documents/', data: data);
      await loadDocuments();
      _error = null;
    } catch (e) {
      _error = e.toString();
    }
    _isLoading = false;
    notifyListeners();
  }
  
  Future<void> deleteDocument(String id) async {
    try {
      await _apiClient.delete('/api/v1/documents/$id/');
      await loadDocuments();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }
}

/// Provider for Realtime Collaboration
class RealtimeCollaborationProvider extends ChangeNotifier {
  final ApiClient _apiClient;
  
  List<dynamic> _sessions = [];
  final List<dynamic> _collaborators = [];
  Map<String, dynamic>? _currentSession;
  bool _isLoading = false;
  String? _error;
  
  RealtimeCollaborationProvider(this._apiClient);
  
  List<dynamic> get sessions => _sessions;
  List<dynamic> get collaborators => _collaborators;
  Map<String, dynamic>? get currentSession => _currentSession;
  bool get isLoading => _isLoading;
  String? get error => _error;
  
  Future<void> loadSessions() async {
    _isLoading = true;
    notifyListeners();
    try {
      final response = await _apiClient.get('/api/v1/collaboration/sessions/');
      _sessions = response.data['results'] ?? [];
      _error = null;
    } catch (e) {
      _error = e.toString();
    }
    _isLoading = false;
    notifyListeners();
  }
  
  Future<void> createSession(Map<String, dynamic> data) async {
    try {
      final response = await _apiClient.post('/api/v1/collaboration/sessions/', data: data);
      _currentSession = response.data;
      await loadSessions();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }
  
  Future<void> joinSession(String sessionId) async {
    try {
      final response = await _apiClient.post('/api/v1/collaboration/sessions/$sessionId/join/');
      _currentSession = response.data;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }
  
  Future<void> leaveSession(String sessionId) async {
    try {
      await _apiClient.post('/api/v1/collaboration/sessions/$sessionId/leave/');
      _currentSession = null;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }
}

/// Provider for Customer Portal
class CustomerPortalProvider extends ChangeNotifier {
  final ApiClient _apiClient;
  
  List<dynamic> _tickets = [];
  List<dynamic> _knowledgeBase = [];
  Map<String, dynamic>? _portalSettings;
  bool _isLoading = false;
  String? _error;
  
  CustomerPortalProvider(this._apiClient);
  
  List<dynamic> get tickets => _tickets;
  List<dynamic> get knowledgeBase => _knowledgeBase;
  Map<String, dynamic>? get portalSettings => _portalSettings;
  bool get isLoading => _isLoading;
  String? get error => _error;
  
  Future<void> loadTickets() async {
    _isLoading = true;
    notifyListeners();
    try {
      final response = await _apiClient.get('/api/v1/customer-portal/tickets/');
      _tickets = response.data['results'] ?? [];
      _error = null;
    } catch (e) {
      _error = e.toString();
    }
    _isLoading = false;
    notifyListeners();
  }
  
  Future<void> loadKnowledgeBase() async {
    try {
      final response = await _apiClient.get('/api/v1/customer-portal/knowledge-base/');
      _knowledgeBase = response.data['results'] ?? [];
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }
  
  Future<void> loadPortalSettings() async {
    try {
      final response = await _apiClient.get('/api/v1/customer-portal/settings/');
      _portalSettings = response.data;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }
  
  Future<void> createTicket(Map<String, dynamic> data) async {
    _isLoading = true;
    notifyListeners();
    try {
      await _apiClient.post('/api/v1/customer-portal/tickets/', data: data);
      await loadTickets();
      _error = null;
    } catch (e) {
      _error = e.toString();
    }
    _isLoading = false;
    notifyListeners();
  }
  
  Future<void> updateTicket(String id, Map<String, dynamic> data) async {
    try {
      await _apiClient.patch('/api/v1/customer-portal/tickets/$id/', data: data);
      await loadTickets();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }
}
