// Enterprise Services for MyCRM Flutter App
// Contains service classes for Customer Success, GDPR, SSO, White-Label,
// AI Chatbot, Data Enrichment, and other enterprise features

import '../core/constants/api_constants.dart';
import '../core/utils/api_client.dart';
import '../models/enterprise_models.dart';
import '../models/advanced_models.dart' as advanced;

/// Service for Customer Success features
class CustomerSuccessService {
  final ApiClient _apiClient;

  CustomerSuccessService(this._apiClient);

  Future<List<advanced.CustomerAccount>> getAccounts() async {
    final response = await _apiClient.get(ApiConstants.csAccounts);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => advanced.CustomerAccount.fromJson(json)).toList();
    }
    throw Exception('Failed to load accounts');
  }

  Future<advanced.CustomerAccount> getAccount(String id) async {
    final response = await _apiClient.get('${ApiConstants.csAccounts}$id/');
    if (response.statusCode == 200) {
      return advanced.CustomerAccount.fromJson(response.data);
    }
    throw Exception('Failed to load account');
  }

  Future<Map<String, dynamic>> getAccountHealth(String id) async {
    final response = await _apiClient.get(ApiConstants.accountHealth(id));
    if (response.statusCode == 200) {
      return response.data;
    }
    throw Exception('Failed to load account health');
  }

  Future<void> recalculateHealth(String id) async {
    final response = await _apiClient.post(ApiConstants.recalculateHealth(id));
    if (response.statusCode != 200) {
      throw Exception('Failed to recalculate health');
    }
  }

  Future<List<HealthScore>> getHealthScores() async {
    final response = await _apiClient.get(ApiConstants.healthScores);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => HealthScore.fromJson(json)).toList();
    }
    throw Exception('Failed to load health scores');
  }

  Future<List<ChurnRisk>> getChurnRisks() async {
    final response = await _apiClient.get(ApiConstants.churnRisks);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => ChurnRisk.fromJson(json)).toList();
    }
    throw Exception('Failed to load churn risks');
  }

  Future<ChurnRisk> predictChurn(String accountId) async {
    final response = await _apiClient.post(ApiConstants.predictChurnCS(accountId));
    if (response.statusCode == 200) {
      return ChurnRisk.fromJson(response.data);
    }
    throw Exception('Failed to predict churn');
  }

  Future<List<Renewal>> getRenewals() async {
    final response = await _apiClient.get(ApiConstants.renewals);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => Renewal.fromJson(json)).toList();
    }
    throw Exception('Failed to load renewals');
  }

  Future<List<Renewal>> getUpcomingRenewals() async {
    final response = await _apiClient.get(ApiConstants.upcomingRenewals);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => Renewal.fromJson(json)).toList();
    }
    throw Exception('Failed to load upcoming renewals');
  }

  Future<List<NPSSurvey>> getNPSSurveys() async {
    final response = await _apiClient.get(ApiConstants.npsSurveys);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => NPSSurvey.fromJson(json)).toList();
    }
    throw Exception('Failed to load NPS surveys');
  }

  Future<Map<String, dynamic>> getNPSAnalytics() async {
    final response = await _apiClient.get(ApiConstants.npsAnalytics);
    if (response.statusCode == 200) {
      return response.data;
    }
    throw Exception('Failed to load NPS analytics');
  }

  Future<List<Playbook>> getPlaybooks() async {
    final response = await _apiClient.get(ApiConstants.playbooks);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => Playbook.fromJson(json)).toList();
    }
    throw Exception('Failed to load playbooks');
  }

  Future<void> executePlaybook(String id, String accountId) async {
    final response = await _apiClient.post(
      ApiConstants.executePlaybook(id),
      data: {'account_id': accountId},
    );
    if (response.statusCode != 200) {
      throw Exception('Failed to execute playbook');
    }
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

/// Service for GDPR Compliance
class GDPRService {
  final ApiClient _apiClient;

  GDPRService(this._apiClient);

  Future<List<GDPRConsent>> getConsents({String? contactId}) async {
    final response = await _apiClient.get(
      ApiConstants.gdprConsents,
      queryParameters: contactId != null ? {'contact_id': contactId} : null,
    );
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => GDPRConsent.fromJson(json)).toList();
    }
    throw Exception('Failed to load consents');
  }

  Future<GDPRConsent> grantConsent(String contactId, String consentType) async {
    final response = await _apiClient.post(ApiConstants.gdprConsents, data: {
      'contact_id': contactId,
      'consent_type': consentType,
      'is_granted': true,
    });
    if (response.statusCode == 201) {
      return GDPRConsent.fromJson(response.data);
    }
    throw Exception('Failed to grant consent');
  }

  Future<void> revokeConsent(String id) async {
    final response = await _apiClient.post('${ApiConstants.gdprConsents}$id/revoke/');
    if (response.statusCode != 200) {
      throw Exception('Failed to revoke consent');
    }
  }

  Future<List<DataSubjectRequest>> getDataSubjectRequests() async {
    final response = await _apiClient.get(ApiConstants.dataSubjectRequests);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => DataSubjectRequest.fromJson(json)).toList();
    }
    throw Exception('Failed to load data subject requests');
  }

  Future<DataSubjectRequest> createDataSubjectRequest({
    required String requestType,
    required String contactEmail,
    String? notes,
  }) async {
    final response = await _apiClient.post(ApiConstants.dataSubjectRequests, data: {
      'request_type': requestType,
      'contact_email': contactEmail,
      if (notes != null) 'notes': notes,
    });
    if (response.statusCode == 201) {
      return DataSubjectRequest.fromJson(response.data);
    }
    throw Exception('Failed to create data subject request');
  }

  Future<void> exportData(String contactId) async {
    final response = await _apiClient.post(ApiConstants.dataExport, data: {
      'contact_id': contactId,
    });
    if (response.statusCode != 200 && response.statusCode != 202) {
      throw Exception('Failed to export data');
    }
  }

  Future<void> deleteData(String contactId) async {
    final response = await _apiClient.post(ApiConstants.dataDelete, data: {
      'contact_id': contactId,
    });
    if (response.statusCode != 200 && response.statusCode != 202) {
      throw Exception('Failed to delete data');
    }
  }
}

/// Service for SSO Integration
class SSOService {
  final ApiClient _apiClient;

  SSOService(this._apiClient);

  Future<List<SSOProvider>> getProviders() async {
    final response = await _apiClient.get(ApiConstants.ssoProviders);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => SSOProvider.fromJson(json)).toList();
    }
    throw Exception('Failed to load SSO providers');
  }

  Future<SSOProvider> createProvider(Map<String, dynamic> data) async {
    final response = await _apiClient.post(ApiConstants.ssoProviders, data: data);
    if (response.statusCode == 201) {
      return SSOProvider.fromJson(response.data);
    }
    throw Exception('Failed to create SSO provider');
  }

  Future<void> deleteProvider(String id) async {
    final response = await _apiClient.delete('${ApiConstants.ssoProviders}$id/');
    if (response.statusCode != 204) {
      throw Exception('Failed to delete SSO provider');
    }
  }

  Future<Map<String, dynamic>> getSettings() async {
    final response = await _apiClient.get(ApiConstants.ssoSettings);
    if (response.statusCode == 200) {
      return response.data;
    }
    throw Exception('Failed to load SSO settings');
  }

  Future<void> updateSettings(Map<String, dynamic> settings) async {
    final response = await _apiClient.put(ApiConstants.ssoSettings, data: settings);
    if (response.statusCode != 200) {
      throw Exception('Failed to update SSO settings');
    }
  }
}

/// Service for White-Label Management
class WhiteLabelService {
  final ApiClient _apiClient;

  WhiteLabelService(this._apiClient);

  // Partners
  Future<List<Partner>> getPartners() async {
    final response = await _apiClient.get(ApiConstants.partners);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => Partner.fromJson(json)).toList();
    }
    throw Exception('Failed to load partners');
  }

  Future<Partner> getPartner(String id) async {
    final response = await _apiClient.get('${ApiConstants.partners}$id/');
    if (response.statusCode == 200) {
      return Partner.fromJson(response.data);
    }
    throw Exception('Failed to load partner');
  }

  // Organizations
  Future<List<Organization>> getOrganizations() async {
    final response = await _apiClient.get(ApiConstants.organizations);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => Organization.fromJson(json)).toList();
    }
    throw Exception('Failed to load organizations');
  }

  // Subscription Plans
  Future<List<SubscriptionPlan>> getPlans() async {
    final response = await _apiClient.get(ApiConstants.subscriptionPlans);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => SubscriptionPlan.fromJson(json)).toList();
    }
    throw Exception('Failed to load subscription plans');
  }

  // Current Subscription
  Future<Subscription?> getCurrentSubscription() async {
    try {
      final response = await _apiClient.get(ApiConstants.subscription);
      if (response.statusCode == 200) {
        return Subscription.fromJson(response.data);
      }
    } catch (e) {
      // No subscription found
    }
    return null;
  }

  Future<void> changePlan(String planId) async {
    final response = await _apiClient.post(ApiConstants.changePlan, data: {
      'plan_id': planId,
    });
    if (response.statusCode != 200) {
      throw Exception('Failed to change plan');
    }
  }

  Future<void> cancelSubscription() async {
    final response = await _apiClient.post(ApiConstants.cancelSubscription);
    if (response.statusCode != 200) {
      throw Exception('Failed to cancel subscription');
    }
  }

  // Invoices
  Future<List<Invoice>> getInvoices() async {
    final response = await _apiClient.get(ApiConstants.invoices);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => Invoice.fromJson(json)).toList();
    }
    throw Exception('Failed to load invoices');
  }

  // Branding
  Future<BrandingConfig> getBranding() async {
    final response = await _apiClient.get(ApiConstants.branding);
    if (response.statusCode == 200) {
      return BrandingConfig.fromJson(response.data);
    }
    throw Exception('Failed to load branding');
  }

  Future<void> updateBranding(Map<String, dynamic> branding) async {
    final response = await _apiClient.put(ApiConstants.branding, data: branding);
    if (response.statusCode != 200) {
      throw Exception('Failed to update branding');
    }
  }

  // Usage
  Future<Map<String, dynamic>> getUsage() async {
    final response = await _apiClient.get(ApiConstants.usage);
    if (response.statusCode == 200) {
      return response.data;
    }
    throw Exception('Failed to load usage');
  }
}

/// Service for AI Chatbot
class AIChatbotService {
  final ApiClient _apiClient;

  AIChatbotService(this._apiClient);

  static const String _chatEndpoint = '/api/v1/ai-chatbot/conversations/';
  static const String _messageEndpoint = '/api/v1/ai-chatbot/messages/';

  Future<List<ChatConversation>> getConversations() async {
    final response = await _apiClient.get(_chatEndpoint);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => ChatConversation.fromJson(json)).toList();
    }
    throw Exception('Failed to load conversations');
  }

  Future<ChatConversation> getConversation(String id) async {
    final response = await _apiClient.get('$_chatEndpoint$id/');
    if (response.statusCode == 200) {
      return ChatConversation.fromJson(response.data);
    }
    throw Exception('Failed to load conversation');
  }

  Future<ChatConversation> createConversation({String? title}) async {
    final response = await _apiClient.post(_chatEndpoint, data: {
      if (title != null) 'title': title,
    });
    if (response.statusCode == 201) {
      return ChatConversation.fromJson(response.data);
    }
    throw Exception('Failed to create conversation');
  }

  Future<ChatMessage> sendMessage(String conversationId, String content) async {
    final response = await _apiClient.post(_messageEndpoint, data: {
      'conversation_id': conversationId,
      'content': content,
    });
    if (response.statusCode == 201) {
      return ChatMessage.fromJson(response.data);
    }
    throw Exception('Failed to send message');
  }

  Future<void> deleteConversation(String id) async {
    final response = await _apiClient.delete('$_chatEndpoint$id/');
    if (response.statusCode != 204) {
      throw Exception('Failed to delete conversation');
    }
  }
}

/// Service for Data Enrichment
class DataEnrichmentService {
  final ApiClient _apiClient;

  DataEnrichmentService(this._apiClient);

  static const String _enrichmentEndpoint = '/api/v1/data-enrichment/';

  Future<List<EnrichmentResult>> getEnrichmentResults({
    String? entityType,
    String? entityId,
  }) async {
    final response = await _apiClient.get(
      '${_enrichmentEndpoint}results/',
      queryParameters: {
        if (entityType != null) 'entity_type': entityType,
        if (entityId != null) 'entity_id': entityId,
      },
    );
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => EnrichmentResult.fromJson(json)).toList();
    }
    throw Exception('Failed to load enrichment results');
  }

  Future<EnrichmentResult> enrichEntity(String entityType, String entityId) async {
    final response = await _apiClient.post('${_enrichmentEndpoint}enrich/', data: {
      'entity_type': entityType,
      'entity_id': entityId,
    });
    if (response.statusCode == 200 || response.statusCode == 201) {
      return EnrichmentResult.fromJson(response.data);
    }
    throw Exception('Failed to enrich entity');
  }

  Future<EnrichmentJob> startBulkEnrichment(String entityType, List<String>? entityIds) async {
    final response = await _apiClient.post('${_enrichmentEndpoint}bulk-enrich/', data: {
      'entity_type': entityType,
      if (entityIds != null) 'entity_ids': entityIds,
    });
    if (response.statusCode == 200 || response.statusCode == 202) {
      return EnrichmentJob.fromJson(response.data);
    }
    throw Exception('Failed to start bulk enrichment');
  }

  Future<List<EnrichmentJob>> getJobs() async {
    final response = await _apiClient.get('${_enrichmentEndpoint}jobs/');
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => EnrichmentJob.fromJson(json)).toList();
    }
    throw Exception('Failed to load enrichment jobs');
  }
}

/// Service for Predictive Lead Routing
class LeadRoutingService {
  final ApiClient _apiClient;

  LeadRoutingService(this._apiClient);

  static const String _routingEndpoint = '/api/v1/lead-routing/';

  Future<List<LeadRoutingRule>> getRules() async {
    final response = await _apiClient.get('${_routingEndpoint}rules/');
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => LeadRoutingRule.fromJson(json)).toList();
    }
    throw Exception('Failed to load routing rules');
  }

  Future<LeadRoutingRule> createRule(Map<String, dynamic> data) async {
    final response = await _apiClient.post('${_routingEndpoint}rules/', data: data);
    if (response.statusCode == 201) {
      return LeadRoutingRule.fromJson(response.data);
    }
    throw Exception('Failed to create routing rule');
  }

  Future<void> deleteRule(String id) async {
    final response = await _apiClient.delete('${_routingEndpoint}rules/$id/');
    if (response.statusCode != 204) {
      throw Exception('Failed to delete routing rule');
    }
  }

  Future<List<LeadAssignment>> getAssignments({String? leadId}) async {
    final response = await _apiClient.get(
      '${_routingEndpoint}assignments/',
      queryParameters: leadId != null ? {'lead_id': leadId} : null,
    );
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => LeadAssignment.fromJson(json)).toList();
    }
    throw Exception('Failed to load assignments');
  }

  Future<LeadAssignment> routeLead(String leadId) async {
    final response = await _apiClient.post('${_routingEndpoint}route/', data: {
      'lead_id': leadId,
    });
    if (response.statusCode == 200) {
      return LeadAssignment.fromJson(response.data);
    }
    throw Exception('Failed to route lead');
  }

  Future<Map<String, dynamic>> getRoutingAnalytics() async {
    final response = await _apiClient.get('${_routingEndpoint}analytics/');
    if (response.statusCode == 200) {
      return response.data;
    }
    throw Exception('Failed to load routing analytics');
  }
}

/// Service for Voice Intelligence
class VoiceIntelligenceService {
  final ApiClient _apiClient;

  VoiceIntelligenceService(this._apiClient);

  static const String _voiceEndpoint = '/api/v1/voice-intelligence/';

  Future<List<VoiceRecording>> getRecordings() async {
    final response = await _apiClient.get('${_voiceEndpoint}recordings/');
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => VoiceRecording.fromJson(json)).toList();
    }
    throw Exception('Failed to load recordings');
  }

  Future<VoiceRecording> getRecording(String id) async {
    final response = await _apiClient.get('${_voiceEndpoint}recordings/$id/');
    if (response.statusCode == 200) {
      return VoiceRecording.fromJson(response.data);
    }
    throw Exception('Failed to load recording');
  }

  Future<VoiceRecording> uploadRecording({
    required String filePath,
    required String title,
    String? contactId,
    String? opportunityId,
  }) async {
    final response = await _apiClient.uploadFile(
      '${_voiceEndpoint}recordings/',
      filePath,
      data: {
        'title': title,
        if (contactId != null) 'contact_id': contactId,
        if (opportunityId != null) 'opportunity_id': opportunityId,
      },
    );
    if (response.statusCode == 201) {
      return VoiceRecording.fromJson(response.data);
    }
    throw Exception('Failed to upload recording');
  }

  Future<void> processRecording(String id) async {
    final response = await _apiClient.post('${_voiceEndpoint}recordings/$id/process/');
    if (response.statusCode != 200 && response.statusCode != 202) {
      throw Exception('Failed to process recording');
    }
  }

  Future<String> getTranscription(String id) async {
    final response = await _apiClient.get('${_voiceEndpoint}recordings/$id/transcription/');
    if (response.statusCode == 200) {
      return response.data['transcription'] ?? '';
    }
    throw Exception('Failed to get transcription');
  }

  Future<VoiceAnalysis> getAnalysis(String id) async {
    final response = await _apiClient.get('${_voiceEndpoint}recordings/$id/analysis/');
    if (response.statusCode == 200) {
      return VoiceAnalysis.fromJson(response.data);
    }
    throw Exception('Failed to get analysis');
  }

  Future<void> deleteRecording(String id) async {
    final response = await _apiClient.delete('${_voiceEndpoint}recordings/$id/');
    if (response.statusCode != 204) {
      throw Exception('Failed to delete recording');
    }
  }
}

/// Service for Email Sequence Automation
class EmailSequenceService {
  final ApiClient _apiClient;

  EmailSequenceService(this._apiClient);

  static const String _sequenceEndpoint = '/api/v1/email-sequences/';

  Future<List<EmailSequence>> getSequences() async {
    final response = await _apiClient.get('${_sequenceEndpoint}sequences/');
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => EmailSequence.fromJson(json)).toList();
    }
    throw Exception('Failed to load sequences');
  }

  Future<EmailSequence> createSequence(Map<String, dynamic> data) async {
    final response = await _apiClient.post('${_sequenceEndpoint}sequences/', data: data);
    if (response.statusCode == 201) {
      return EmailSequence.fromJson(response.data);
    }
    throw Exception('Failed to create sequence');
  }

  Future<void> activateSequence(String id) async {
    final response = await _apiClient.post('${_sequenceEndpoint}sequences/$id/activate/');
    if (response.statusCode != 200) {
      throw Exception('Failed to activate sequence');
    }
  }

  Future<void> pauseSequence(String id) async {
    final response = await _apiClient.post('${_sequenceEndpoint}sequences/$id/pause/');
    if (response.statusCode != 200) {
      throw Exception('Failed to pause sequence');
    }
  }

  Future<List<SequenceEnrollment>> getEnrollments({String? sequenceId}) async {
    final response = await _apiClient.get(
      '${_sequenceEndpoint}enrollments/',
      queryParameters: sequenceId != null ? {'sequence_id': sequenceId} : null,
    );
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => SequenceEnrollment.fromJson(json)).toList();
    }
    throw Exception('Failed to load enrollments');
  }

  Future<SequenceEnrollment> enrollContact(String sequenceId, String contactId) async {
    final response = await _apiClient.post('${_sequenceEndpoint}enrollments/', data: {
      'sequence_id': sequenceId,
      'contact_id': contactId,
    });
    if (response.statusCode == 201) {
      return SequenceEnrollment.fromJson(response.data);
    }
    throw Exception('Failed to enroll contact');
  }

  Future<void> unenrollContact(String enrollmentId) async {
    final response = await _apiClient.delete('${_sequenceEndpoint}enrollments/$enrollmentId/');
    if (response.statusCode != 204) {
      throw Exception('Failed to unenroll contact');
    }
  }

  Future<void> addStep(String sequenceId, Map<String, dynamic> stepData) async {
    final response = await _apiClient.post('${_sequenceEndpoint}sequences/$sequenceId/steps/', data: stepData);
    if (response.statusCode != 201) {
      throw Exception('Failed to add step');
    }
  }
}

/// Service for App Marketplace
class MarketplaceService {
  final ApiClient _apiClient;

  MarketplaceService(this._apiClient);

  static const String _marketplaceEndpoint = '/api/v1/marketplace/';

  Future<List<MarketplaceApp>> getApps({String? category, String? search}) async {
    final response = await _apiClient.get(
      '${_marketplaceEndpoint}apps/',
      queryParameters: {
        if (category != null) 'category': category,
        if (search != null) 'search': search,
      },
    );
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => MarketplaceApp.fromJson(json)).toList();
    }
    throw Exception('Failed to load marketplace apps');
  }

  Future<MarketplaceApp> getApp(String id) async {
    final response = await _apiClient.get('${_marketplaceEndpoint}apps/$id/');
    if (response.statusCode == 200) {
      return MarketplaceApp.fromJson(response.data);
    }
    throw Exception('Failed to load app');
  }

  Future<InstalledApp> installApp(String appId) async {
    final response = await _apiClient.post('${_marketplaceEndpoint}apps/$appId/install/');
    if (response.statusCode == 200 || response.statusCode == 201) {
      return InstalledApp.fromJson(response.data);
    }
    throw Exception('Failed to install app');
  }

  Future<void> uninstallApp(String appId) async {
    final response = await _apiClient.post('${_marketplaceEndpoint}apps/$appId/uninstall/');
    if (response.statusCode != 200) {
      throw Exception('Failed to uninstall app');
    }
  }

  Future<List<InstalledApp>> getInstalledApps() async {
    final response = await _apiClient.get('${_marketplaceEndpoint}installed/');
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => InstalledApp.fromJson(json)).toList();
    }
    throw Exception('Failed to load installed apps');
  }
}

/// Service for Realtime Collaboration
class CollaborationService {
  final ApiClient _apiClient;

  CollaborationService(this._apiClient);

  static const String _collabEndpoint = '/api/v1/realtime-collab/';

  Future<CollaborationSession?> getSession(String entityType, String entityId) async {
    try {
      final response = await _apiClient.get(
        '${_collabEndpoint}sessions/',
        queryParameters: {
          'entity_type': entityType,
          'entity_id': entityId,
        },
      );
      if (response.statusCode == 200) {
        final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
        if (data.isNotEmpty) {
          return CollaborationSession.fromJson(data.first);
        }
      }
    } catch (e) {
      // No session found
    }
    return null;
  }

  Future<CollaborationSession> joinSession(String entityType, String entityId) async {
    final response = await _apiClient.post('${_collabEndpoint}sessions/join/', data: {
      'entity_type': entityType,
      'entity_id': entityId,
    });
    if (response.statusCode == 200 || response.statusCode == 201) {
      return CollaborationSession.fromJson(response.data);
    }
    throw Exception('Failed to join collaboration session');
  }

  Future<void> leaveSession(String sessionId) async {
    final response = await _apiClient.post('${_collabEndpoint}sessions/$sessionId/leave/');
    if (response.statusCode != 200) {
      throw Exception('Failed to leave session');
    }
  }

  Future<void> updateCursor(String sessionId, String? fieldName) async {
    await _apiClient.post('${_collabEndpoint}sessions/$sessionId/cursor/', data: {
      'field': fieldName,
    });
  }
}

/// Service for Social Inbox
class SocialInboxService {
  final ApiClient _apiClient;

  SocialInboxService(this._apiClient);

  static const String _inboxEndpoint = '/api/v1/social-inbox/';

  Future<List<SocialMessage>> getMessages({String? platform, String? status}) async {
    final response = await _apiClient.get(
      '${_inboxEndpoint}messages/',
      queryParameters: {
        if (platform != null) 'platform': platform,
        if (status != null) 'status': status,
      },
    );
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => SocialMessage.fromJson(json)).toList();
    }
    throw Exception('Failed to load social messages');
  }

  Future<void> replyToMessage(String messageId, String content) async {
    final response = await _apiClient.post('${_inboxEndpoint}messages/$messageId/reply/', data: {
      'content': content,
    });
    if (response.statusCode != 200 && response.statusCode != 201) {
      throw Exception('Failed to reply to message');
    }
  }

  Future<void> markAsRead(String messageId) async {
    final response = await _apiClient.post('${_inboxEndpoint}messages/$messageId/read/');
    if (response.statusCode != 200) {
      throw Exception('Failed to mark message as read');
    }
  }

  Future<void> linkToContact(String messageId, String contactId) async {
    final response = await _apiClient.post('${_inboxEndpoint}messages/$messageId/link/', data: {
      'contact_id': contactId,
    });
    if (response.statusCode != 200) {
      throw Exception('Failed to link message to contact');
    }
  }

  Future<void> sendMessage(String platform, String content, [String? recipientId]) async {
    final response = await _apiClient.post('${_inboxEndpoint}messages/', data: {
      'platform': platform,
      'recipient_id': recipientId ?? '',
      'content': content,
    });
    if (response.statusCode != 201) {
      throw Exception('Failed to send message');
    }
  }
}

/// Service for Customer Portal
class CustomerPortalService {
  final ApiClient _apiClient;

  CustomerPortalService(this._apiClient);

  static const String _portalEndpoint = '/api/v1/customer-portal/';

  Future<List<PortalUser>> getPortalUsers() async {
    final response = await _apiClient.get('${_portalEndpoint}users/');
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => PortalUser.fromJson(json)).toList();
    }
    throw Exception('Failed to load portal users');
  }

  Future<PortalUser> inviteUser(String email, String name, String? contactId) async {
    final response = await _apiClient.post('${_portalEndpoint}users/invite/', data: {
      'email': email,
      'name': name,
      if (contactId != null) 'contact_id': contactId,
    });
    if (response.statusCode == 201) {
      return PortalUser.fromJson(response.data);
    }
    throw Exception('Failed to invite user');
  }

  Future<void> deactivateUser(String userId) async {
    final response = await _apiClient.post('${_portalEndpoint}users/$userId/deactivate/');
    if (response.statusCode != 200) {
      throw Exception('Failed to deactivate user');
    }
  }

  Future<List<SupportTicket>> getTickets({String? status}) async {
    final response = await _apiClient.get(
      '${_portalEndpoint}tickets/',
      queryParameters: status != null ? {'status': status} : null,
    );
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => SupportTicket.fromJson(json)).toList();
    }
    throw Exception('Failed to load tickets');
  }

  Future<SupportTicket> createTicket({
    required String subject,
    required String description,
    String priority = 'medium',
  }) async {
    final response = await _apiClient.post('${_portalEndpoint}tickets/', data: {
      'subject': subject,
      'description': description,
      'priority': priority,
    });
    if (response.statusCode == 201) {
      return SupportTicket.fromJson(response.data);
    }
    throw Exception('Failed to create ticket');
  }

  Future<void> assignTicket(String ticketId, String assigneeId) async {
    final response = await _apiClient.post('${_portalEndpoint}tickets/$ticketId/assign/', data: {
      'assignee_id': assigneeId,
    });
    if (response.statusCode != 200) {
      throw Exception('Failed to assign ticket');
    }
  }
}

/// Service for ESG Reporting
class ESGService {
  final ApiClient _apiClient;

  ESGService(this._apiClient);

  static const String _esgEndpoint = '/api/v1/esg/';

  Future<List<ESGMetric>> getMetrics({String? category, String? period}) async {
    final response = await _apiClient.get(
      '${_esgEndpoint}metrics/',
      queryParameters: {
        if (category != null) 'category': category,
        if (period != null) 'period': period,
      },
    );
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => ESGMetric.fromJson(json)).toList();
    }
    throw Exception('Failed to load ESG metrics');
  }

  Future<ESGMetric> recordMetric(Map<String, dynamic> data) async {
    final response = await _apiClient.post('${_esgEndpoint}metrics/', data: data);
    if (response.statusCode == 201) {
      return ESGMetric.fromJson(response.data);
    }
    throw Exception('Failed to record metric');
  }

  Future<Map<String, dynamic>> getDashboard() async {
    final response = await _apiClient.get('${_esgEndpoint}dashboard/');
    if (response.statusCode == 200) {
      return response.data;
    }
    throw Exception('Failed to load ESG dashboard');
  }

  Future<Map<String, dynamic>> generateReport({
    required String period,
    List<String>? categories,
  }) async {
    final response = await _apiClient.post('${_esgEndpoint}reports/generate/', data: {
      'period': period,
      if (categories != null) 'categories': categories,
    });
    if (response.statusCode == 200) {
      return response.data;
    }
    throw Exception('Failed to generate ESG report');
  }
}

/// Service for Conversation Intelligence (extends advanced services)
class ConversationIntelligenceService {
  final ApiClient _apiClient;

  ConversationIntelligenceService(this._apiClient);

  Future<List<VoiceRecording>> getRecordings() async {
    final response = await _apiClient.get(ApiConstants.callRecordings);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => VoiceRecording.fromJson(json)).toList();
    }
    throw Exception('Failed to load recordings');
  }

  Future<void> processRecording(String id) async {
    final response = await _apiClient.post(ApiConstants.processRecording(id));
    if (response.statusCode != 200 && response.statusCode != 202) {
      throw Exception('Failed to process recording');
    }
  }

  Future<String> getTranscript(String id) async {
    final response = await _apiClient.get(ApiConstants.getTranscript(id));
    if (response.statusCode == 200) {
      return response.data['transcript'] ?? '';
    }
    throw Exception('Failed to get transcript');
  }

  Future<VoiceAnalysis> getAnalysis(String id) async {
    final response = await _apiClient.get(ApiConstants.getAnalysis(id));
    if (response.statusCode == 200) {
      return VoiceAnalysis.fromJson(response.data);
    }
    throw Exception('Failed to get analysis');
  }

  Future<List<KeyMoment>> getKeyMoments(String id) async {
    final response = await _apiClient.get(ApiConstants.getKeyMoments(id));
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['moments'] ?? [];
      return data.map((json) => KeyMoment.fromJson(json)).toList();
    }
    throw Exception('Failed to get key moments');
  }

  Future<Map<String, dynamic>> getTalkPatterns() async {
    final response = await _apiClient.get(ApiConstants.talkPatterns);
    if (response.statusCode == 200) {
      return response.data;
    }
    throw Exception('Failed to get talk patterns');
  }

  Future<Map<String, dynamic>> getCoachingInsights(String id) async {
    final response = await _apiClient.get(ApiConstants.coachingInsights(id));
    if (response.statusCode == 200) {
      return response.data;
    }
    throw Exception('Failed to get coaching insights');
  }

  Future<Map<String, dynamic>> getTeamCoaching() async {
    final response = await _apiClient.get(ApiConstants.teamCoaching);
    if (response.statusCode == 200) {
      return response.data;
    }
    throw Exception('Failed to get team coaching');
  }

  Future<Map<String, dynamic>> getAnalytics({String? period}) async {
    final response = await _apiClient.get(
      ApiConstants.conversationAnalytics,
      queryParameters: period != null ? {'period': period} : null,
    );
    if (response.statusCode == 200) {
      return response.data;
    }
    throw Exception('Failed to get conversation analytics');
  }
}
