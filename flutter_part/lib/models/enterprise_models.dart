// Enterprise Models for MyCRM Flutter App
// Contains data models for Customer Success, GDPR, SSO, White-Label,
// AI Chatbot, Data Enrichment, and other enterprise features

// ==================== Customer Success Models ====================

class HealthScore {
  final String id;
  final String accountId;
  final int score;
  final String category;
  final Map<String, dynamic> metrics;
  final String trend;
  final DateTime calculatedAt;

  HealthScore({
    required this.id,
    required this.accountId,
    required this.score,
    required this.category,
    required this.metrics,
    required this.trend,
    required this.calculatedAt,
  });

  factory HealthScore.fromJson(Map<String, dynamic> json) {
    return HealthScore(
      id: json['id']?.toString() ?? '',
      accountId: json['account_id']?.toString() ?? '',
      score: json['score'] ?? 0,
      category: json['category'] ?? 'medium',
      metrics: Map<String, dynamic>.from(json['metrics'] ?? {}),
      trend: json['trend'] ?? 'stable',
      calculatedAt: DateTime.parse(json['calculated_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  String get scoreColor {
    if (score >= 80) return 'green';
    if (score >= 60) return 'yellow';
    if (score >= 40) return 'orange';
    return 'red';
  }
}

class ChurnRisk {
  final String id;
  final String accountId;
  final String accountName;
  final double riskScore;
  final String riskLevel;
  final List<String> riskFactors;
  final List<String> recommendedActions;
  final DateTime predictedAt;

  ChurnRisk({
    required this.id,
    required this.accountId,
    required this.accountName,
    required this.riskScore,
    required this.riskLevel,
    required this.riskFactors,
    required this.recommendedActions,
    required this.predictedAt,
  });

  factory ChurnRisk.fromJson(Map<String, dynamic> json) {
    return ChurnRisk(
      id: json['id']?.toString() ?? '',
      accountId: json['account_id']?.toString() ?? '',
      accountName: json['account_name'] ?? '',
      riskScore: (json['risk_score'] ?? 0).toDouble(),
      riskLevel: json['risk_level'] ?? 'low',
      riskFactors: List<String>.from(json['risk_factors'] ?? []),
      recommendedActions: List<String>.from(json['recommended_actions'] ?? []),
      predictedAt: DateTime.parse(json['predicted_at'] ?? DateTime.now().toIso8601String()),
    );
  }
}

class Renewal {
  final String id;
  final String accountId;
  final String accountName;
  final double amount;
  final DateTime renewalDate;
  final String status;
  final double probability;
  final String? notes;

  Renewal({
    required this.id,
    required this.accountId,
    required this.accountName,
    required this.amount,
    required this.renewalDate,
    required this.status,
    required this.probability,
    this.notes,
  });

  factory Renewal.fromJson(Map<String, dynamic> json) {
    return Renewal(
      id: json['id']?.toString() ?? '',
      accountId: json['account_id']?.toString() ?? '',
      accountName: json['account_name'] ?? '',
      amount: (json['amount'] ?? 0).toDouble(),
      renewalDate: DateTime.parse(json['renewal_date'] ?? DateTime.now().toIso8601String()),
      status: json['status'] ?? 'upcoming',
      probability: (json['probability'] ?? 0).toDouble(),
      notes: json['notes'],
    );
  }
}

class NPSSurvey {
  final String id;
  final String accountId;
  final int score;
  final String? feedback;
  final String category;
  final DateTime submittedAt;

  NPSSurvey({
    required this.id,
    required this.accountId,
    required this.score,
    this.feedback,
    required this.category,
    required this.submittedAt,
  });

  factory NPSSurvey.fromJson(Map<String, dynamic> json) {
    return NPSSurvey(
      id: json['id']?.toString() ?? '',
      accountId: json['account_id']?.toString() ?? '',
      score: json['score'] ?? 0,
      feedback: json['feedback'],
      category: _getNPSCategory(json['score'] ?? 0),
      submittedAt: DateTime.parse(json['submitted_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  static String _getNPSCategory(int score) {
    if (score >= 9) return 'promoter';
    if (score >= 7) return 'passive';
    return 'detractor';
  }
}

class Playbook {
  final String id;
  final String name;
  final String description;
  final String triggerType;
  final Map<String, dynamic> triggerConditions;
  final List<PlaybookStep> steps;
  final bool isActive;
  final int executionCount;

  Playbook({
    required this.id,
    required this.name,
    required this.description,
    required this.triggerType,
    required this.triggerConditions,
    required this.steps,
    required this.isActive,
    required this.executionCount,
  });

  factory Playbook.fromJson(Map<String, dynamic> json) {
    return Playbook(
      id: json['id']?.toString() ?? '',
      name: json['name'] ?? '',
      description: json['description'] ?? '',
      triggerType: json['trigger_type'] ?? '',
      triggerConditions: Map<String, dynamic>.from(json['trigger_conditions'] ?? {}),
      steps: (json['steps'] as List?)?.map((s) => PlaybookStep.fromJson(s)).toList() ?? [],
      isActive: json['is_active'] ?? false,
      executionCount: json['execution_count'] ?? 0,
    );
  }
}

class PlaybookStep {
  final int order;
  final String actionType;
  final String description;
  final Map<String, dynamic> actionConfig;
  final int delayDays;

  PlaybookStep({
    required this.order,
    required this.actionType,
    required this.description,
    required this.actionConfig,
    required this.delayDays,
  });

  factory PlaybookStep.fromJson(Map<String, dynamic> json) {
    return PlaybookStep(
      order: json['order'] ?? 0,
      actionType: json['action_type'] ?? '',
      description: json['description'] ?? '',
      actionConfig: Map<String, dynamic>.from(json['action_config'] ?? {}),
      delayDays: json['delay_days'] ?? 0,
    );
  }
}

// ==================== GDPR Models ====================

class GDPRConsent {
  final String id;
  final String consentType;
  final bool isGranted;
  final DateTime? grantedAt;
  final DateTime? revokedAt;
  final String? ipAddress;
  final String source;

  GDPRConsent({
    required this.id,
    required this.consentType,
    required this.isGranted,
    this.grantedAt,
    this.revokedAt,
    this.ipAddress,
    required this.source,
  });

  factory GDPRConsent.fromJson(Map<String, dynamic> json) {
    return GDPRConsent(
      id: json['id']?.toString() ?? '',
      consentType: json['consent_type'] ?? '',
      isGranted: json['is_granted'] ?? false,
      grantedAt: json['granted_at'] != null ? DateTime.parse(json['granted_at']) : null,
      revokedAt: json['revoked_at'] != null ? DateTime.parse(json['revoked_at']) : null,
      ipAddress: json['ip_address'],
      source: json['source'] ?? '',
    );
  }
}

class DataSubjectRequest {
  final String id;
  final String requestType;
  final String status;
  final String? contactEmail;
  final DateTime requestedAt;
  final DateTime? completedAt;
  final String? notes;

  DataSubjectRequest({
    required this.id,
    required this.requestType,
    required this.status,
    this.contactEmail,
    required this.requestedAt,
    this.completedAt,
    this.notes,
  });

  factory DataSubjectRequest.fromJson(Map<String, dynamic> json) {
    return DataSubjectRequest(
      id: json['id']?.toString() ?? '',
      requestType: json['request_type'] ?? '',
      status: json['status'] ?? 'pending',
      contactEmail: json['contact_email'],
      requestedAt: DateTime.parse(json['requested_at'] ?? DateTime.now().toIso8601String()),
      completedAt: json['completed_at'] != null ? DateTime.parse(json['completed_at']) : null,
      notes: json['notes'],
    );
  }
}

// ==================== SSO Models ====================

class SSOProvider {
  final String id;
  final String name;
  final String providerType;
  final bool isActive;
  final Map<String, dynamic> config;
  final DateTime createdAt;

  SSOProvider({
    required this.id,
    required this.name,
    required this.providerType,
    required this.isActive,
    required this.config,
    required this.createdAt,
  });

  factory SSOProvider.fromJson(Map<String, dynamic> json) {
    return SSOProvider(
      id: json['id']?.toString() ?? '',
      name: json['name'] ?? '',
      providerType: json['provider_type'] ?? 'saml',
      isActive: json['is_active'] ?? false,
      config: Map<String, dynamic>.from(json['config'] ?? {}),
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
    );
  }
}

// ==================== White-Label Models ====================

class Partner {
  final String id;
  final String name;
  final String slug;
  final BrandingConfig branding;
  final bool isActive;
  final int organizationCount;
  final DateTime createdAt;

  Partner({
    required this.id,
    required this.name,
    required this.slug,
    required this.branding,
    required this.isActive,
    required this.organizationCount,
    required this.createdAt,
  });

  factory Partner.fromJson(Map<String, dynamic> json) {
    return Partner(
      id: json['id']?.toString() ?? '',
      name: json['name'] ?? '',
      slug: json['slug'] ?? '',
      branding: BrandingConfig.fromJson(json['branding'] ?? {}),
      isActive: json['is_active'] ?? false,
      organizationCount: json['organization_count'] ?? 0,
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
    );
  }
}

class BrandingConfig {
  final String? logoUrl;
  final String primaryColor;
  final String secondaryColor;
  final String? faviconUrl;
  final String? customDomain;
  final Map<String, String> customLabels;

  BrandingConfig({
    this.logoUrl,
    required this.primaryColor,
    required this.secondaryColor,
    this.faviconUrl,
    this.customDomain,
    required this.customLabels,
  });

  factory BrandingConfig.fromJson(Map<String, dynamic> json) {
    return BrandingConfig(
      logoUrl: json['logo_url'],
      primaryColor: json['primary_color'] ?? '#2196F3',
      secondaryColor: json['secondary_color'] ?? '#FFC107',
      faviconUrl: json['favicon_url'],
      customDomain: json['custom_domain'],
      customLabels: Map<String, String>.from(json['custom_labels'] ?? {}),
    );
  }
}

class Organization {
  final String id;
  final String name;
  final String? partnerId;
  final String plan;
  final int memberCount;
  final int seatLimit;
  final bool isActive;
  final DateTime createdAt;

  Organization({
    required this.id,
    required this.name,
    this.partnerId,
    required this.plan,
    required this.memberCount,
    required this.seatLimit,
    required this.isActive,
    required this.createdAt,
  });

  factory Organization.fromJson(Map<String, dynamic> json) {
    return Organization(
      id: json['id']?.toString() ?? '',
      name: json['name'] ?? '',
      partnerId: json['partner_id']?.toString(),
      plan: json['plan'] ?? 'free',
      memberCount: json['member_count'] ?? 0,
      seatLimit: json['seat_limit'] ?? 5,
      isActive: json['is_active'] ?? false,
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
    );
  }
}

class SubscriptionPlan {
  final String id;
  final String name;
  final String description;
  final double monthlyPrice;
  final double annualPrice;
  final Map<String, dynamic> features;
  final int seatLimit;
  final bool isPopular;

  SubscriptionPlan({
    required this.id,
    required this.name,
    required this.description,
    required this.monthlyPrice,
    required this.annualPrice,
    required this.features,
    required this.seatLimit,
    required this.isPopular,
  });

  factory SubscriptionPlan.fromJson(Map<String, dynamic> json) {
    return SubscriptionPlan(
      id: json['id']?.toString() ?? '',
      name: json['name'] ?? '',
      description: json['description'] ?? '',
      monthlyPrice: (json['monthly_price'] ?? 0).toDouble(),
      annualPrice: (json['annual_price'] ?? 0).toDouble(),
      features: Map<String, dynamic>.from(json['features'] ?? {}),
      seatLimit: json['seat_limit'] ?? 5,
      isPopular: json['is_popular'] ?? false,
    );
  }
}

class Subscription {
  final String id;
  final String planId;
  final String planName;
  final String status;
  final String billingCycle;
  final DateTime currentPeriodStart;
  final DateTime currentPeriodEnd;
  final double amount;
  final bool autoRenew;

  Subscription({
    required this.id,
    required this.planId,
    required this.planName,
    required this.status,
    required this.billingCycle,
    required this.currentPeriodStart,
    required this.currentPeriodEnd,
    required this.amount,
    required this.autoRenew,
  });

  factory Subscription.fromJson(Map<String, dynamic> json) {
    return Subscription(
      id: json['id']?.toString() ?? '',
      planId: json['plan_id']?.toString() ?? '',
      planName: json['plan_name'] ?? '',
      status: json['status'] ?? 'active',
      billingCycle: json['billing_cycle'] ?? 'monthly',
      currentPeriodStart: DateTime.parse(json['current_period_start'] ?? DateTime.now().toIso8601String()),
      currentPeriodEnd: DateTime.parse(json['current_period_end'] ?? DateTime.now().toIso8601String()),
      amount: (json['amount'] ?? 0).toDouble(),
      autoRenew: json['auto_renew'] ?? true,
    );
  }
}

class Invoice {
  final String id;
  final String invoiceNumber;
  final double amount;
  final String status;
  final DateTime issuedAt;
  final DateTime dueDate;
  final DateTime? paidAt;
  final String? downloadUrl;

  Invoice({
    required this.id,
    required this.invoiceNumber,
    required this.amount,
    required this.status,
    required this.issuedAt,
    required this.dueDate,
    this.paidAt,
    this.downloadUrl,
  });

  factory Invoice.fromJson(Map<String, dynamic> json) {
    return Invoice(
      id: json['id']?.toString() ?? '',
      invoiceNumber: json['invoice_number'] ?? '',
      amount: (json['amount'] ?? 0).toDouble(),
      status: json['status'] ?? 'pending',
      issuedAt: DateTime.parse(json['issued_at'] ?? DateTime.now().toIso8601String()),
      dueDate: DateTime.parse(json['due_date'] ?? DateTime.now().toIso8601String()),
      paidAt: json['paid_at'] != null ? DateTime.parse(json['paid_at']) : null,
      downloadUrl: json['download_url'],
    );
  }
}

// ==================== AI Chatbot Models ====================

class ChatConversation {
  final String id;
  final String title;
  final List<ChatMessage> messages;
  final String status;
  final DateTime createdAt;
  final DateTime updatedAt;

  ChatConversation({
    required this.id,
    required this.title,
    required this.messages,
    required this.status,
    required this.createdAt,
    required this.updatedAt,
  });

  factory ChatConversation.fromJson(Map<String, dynamic> json) {
    return ChatConversation(
      id: json['id']?.toString() ?? '',
      title: json['title'] ?? 'New Conversation',
      messages: (json['messages'] as List?)?.map((m) => ChatMessage.fromJson(m)).toList() ?? [],
      status: json['status'] ?? 'active',
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      updatedAt: DateTime.parse(json['updated_at'] ?? DateTime.now().toIso8601String()),
    );
  }
}

class ChatMessage {
  final String id;
  final String role;
  final String content;
  final Map<String, dynamic>? metadata;
  final DateTime timestamp;

  ChatMessage({
    required this.id,
    required this.role,
    required this.content,
    this.metadata,
    required this.timestamp,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id']?.toString() ?? '',
      role: json['role'] ?? 'user',
      content: json['content'] ?? '',
      metadata: json['metadata'] != null ? Map<String, dynamic>.from(json['metadata']) : null,
      timestamp: DateTime.parse(json['timestamp'] ?? DateTime.now().toIso8601String()),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'role': role,
      'content': content,
      'metadata': metadata,
      'timestamp': timestamp.toIso8601String(),
    };
  }
}

// ==================== Data Enrichment Models ====================

class EnrichmentResult {
  final String id;
  final String entityType;
  final String entityId;
  final Map<String, dynamic> enrichedData;
  final String source;
  final double confidence;
  final DateTime enrichedAt;

  EnrichmentResult({
    required this.id,
    required this.entityType,
    required this.entityId,
    required this.enrichedData,
    required this.source,
    required this.confidence,
    required this.enrichedAt,
  });

  factory EnrichmentResult.fromJson(Map<String, dynamic> json) {
    return EnrichmentResult(
      id: json['id']?.toString() ?? '',
      entityType: json['entity_type'] ?? '',
      entityId: json['entity_id']?.toString() ?? '',
      enrichedData: Map<String, dynamic>.from(json['enriched_data'] ?? {}),
      source: json['source'] ?? '',
      confidence: (json['confidence'] ?? 0).toDouble(),
      enrichedAt: DateTime.parse(json['enriched_at'] ?? DateTime.now().toIso8601String()),
    );
  }
}

class EnrichmentJob {
  final String id;
  final String entityType;
  final int totalRecords;
  final int processedRecords;
  final int enrichedRecords;
  final String status;
  final DateTime startedAt;
  final DateTime? completedAt;

  EnrichmentJob({
    required this.id,
    required this.entityType,
    required this.totalRecords,
    required this.processedRecords,
    required this.enrichedRecords,
    required this.status,
    required this.startedAt,
    this.completedAt,
  });

  factory EnrichmentJob.fromJson(Map<String, dynamic> json) {
    return EnrichmentJob(
      id: json['id']?.toString() ?? '',
      entityType: json['entity_type'] ?? '',
      totalRecords: json['total_records'] ?? 0,
      processedRecords: json['processed_records'] ?? 0,
      enrichedRecords: json['enriched_records'] ?? 0,
      status: json['status'] ?? 'pending',
      startedAt: DateTime.parse(json['started_at'] ?? DateTime.now().toIso8601String()),
      completedAt: json['completed_at'] != null ? DateTime.parse(json['completed_at']) : null,
    );
  }

  double get progress => totalRecords > 0 ? processedRecords / totalRecords : 0;
}

// ==================== Predictive Lead Routing Models ====================

class LeadRoutingRule {
  final String id;
  final String name;
  final String description;
  final Map<String, dynamic> conditions;
  final String assigneeId;
  final String? assigneeName;
  final int priority;
  final bool isActive;

  LeadRoutingRule({
    required this.id,
    required this.name,
    required this.description,
    required this.conditions,
    required this.assigneeId,
    this.assigneeName,
    required this.priority,
    required this.isActive,
  });

  factory LeadRoutingRule.fromJson(Map<String, dynamic> json) {
    return LeadRoutingRule(
      id: json['id']?.toString() ?? '',
      name: json['name'] ?? '',
      description: json['description'] ?? '',
      conditions: Map<String, dynamic>.from(json['conditions'] ?? {}),
      assigneeId: json['assignee_id']?.toString() ?? '',
      assigneeName: json['assignee_name'],
      priority: json['priority'] ?? 0,
      isActive: json['is_active'] ?? false,
    );
  }
}

class LeadAssignment {
  final String id;
  final String leadId;
  final String leadName;
  final String assigneeId;
  final String assigneeName;
  final String routingMethod;
  final double score;
  final String reason;
  final DateTime assignedAt;

  LeadAssignment({
    required this.id,
    required this.leadId,
    required this.leadName,
    required this.assigneeId,
    required this.assigneeName,
    required this.routingMethod,
    required this.score,
    required this.reason,
    required this.assignedAt,
  });

  factory LeadAssignment.fromJson(Map<String, dynamic> json) {
    return LeadAssignment(
      id: json['id']?.toString() ?? '',
      leadId: json['lead_id']?.toString() ?? '',
      leadName: json['lead_name'] ?? '',
      assigneeId: json['assignee_id']?.toString() ?? '',
      assigneeName: json['assignee_name'] ?? '',
      routingMethod: json['routing_method'] ?? 'round_robin',
      score: (json['score'] ?? 0).toDouble(),
      reason: json['reason'] ?? '',
      assignedAt: DateTime.parse(json['assigned_at'] ?? DateTime.now().toIso8601String()),
    );
  }
}

// ==================== Voice Intelligence Models ====================

class VoiceRecording {
  final String id;
  final String title;
  final String? contactId;
  final String? contactName;
  final String? opportunityId;
  final int duration;
  final String status;
  final String? transcription;
  final VoiceAnalysis? analysis;
  final DateTime recordedAt;

  VoiceRecording({
    required this.id,
    required this.title,
    this.contactId,
    this.contactName,
    this.opportunityId,
    required this.duration,
    required this.status,
    this.transcription,
    this.analysis,
    required this.recordedAt,
  });

  factory VoiceRecording.fromJson(Map<String, dynamic> json) {
    return VoiceRecording(
      id: json['id']?.toString() ?? '',
      title: json['title'] ?? '',
      contactId: json['contact_id']?.toString(),
      contactName: json['contact_name'],
      opportunityId: json['opportunity_id']?.toString(),
      duration: json['duration'] ?? 0,
      status: json['status'] ?? 'uploaded',
      transcription: json['transcription'],
      analysis: json['analysis'] != null ? VoiceAnalysis.fromJson(json['analysis']) : null,
      recordedAt: DateTime.parse(json['recorded_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  String get formattedDuration {
    final minutes = duration ~/ 60;
    final seconds = duration % 60;
    return '${minutes.toString().padLeft(2, '0')}:${seconds.toString().padLeft(2, '0')}';
  }
}

class VoiceAnalysis {
  final String sentiment;
  final double sentimentScore;
  final List<String> keywords;
  final List<String> topics;
  final double talkRatio;
  final List<String> actionItems;
  final List<KeyMoment> keyMoments;

  VoiceAnalysis({
    required this.sentiment,
    required this.sentimentScore,
    required this.keywords,
    required this.topics,
    required this.talkRatio,
    required this.actionItems,
    required this.keyMoments,
  });

  factory VoiceAnalysis.fromJson(Map<String, dynamic> json) {
    return VoiceAnalysis(
      sentiment: json['sentiment'] ?? 'neutral',
      sentimentScore: (json['sentiment_score'] ?? 0).toDouble(),
      keywords: List<String>.from(json['keywords'] ?? []),
      topics: List<String>.from(json['topics'] ?? []),
      talkRatio: (json['talk_ratio'] ?? 0.5).toDouble(),
      actionItems: List<String>.from(json['action_items'] ?? []),
      keyMoments: (json['key_moments'] as List?)?.map((m) => KeyMoment.fromJson(m)).toList() ?? [],
    );
  }
}

class KeyMoment {
  final int timestamp;
  final String type;
  final String description;
  final double importance;

  KeyMoment({
    required this.timestamp,
    required this.type,
    required this.description,
    required this.importance,
  });

  factory KeyMoment.fromJson(Map<String, dynamic> json) {
    return KeyMoment(
      timestamp: json['timestamp'] ?? 0,
      type: json['type'] ?? '',
      description: json['description'] ?? '',
      importance: (json['importance'] ?? 0).toDouble(),
    );
  }

  String get formattedTimestamp {
    final minutes = timestamp ~/ 60;
    final seconds = timestamp % 60;
    return '${minutes.toString().padLeft(2, '0')}:${seconds.toString().padLeft(2, '0')}';
  }
}

// ==================== Email Sequence Automation Models ====================

class EmailSequenceStep {
  final String id;
  final int stepNumber;
  final String subject;
  final String body;
  final int delayDays;
  final int delayHours;
  final String? templateId;

  EmailSequenceStep({
    required this.id,
    required this.stepNumber,
    required this.subject,
    required this.body,
    required this.delayDays,
    required this.delayHours,
    this.templateId,
  });

  factory EmailSequenceStep.fromJson(Map<String, dynamic> json) {
    return EmailSequenceStep(
      id: json['id']?.toString() ?? '',
      stepNumber: json['step_number'] ?? 0,
      subject: json['subject'] ?? '',
      body: json['body'] ?? '',
      delayDays: json['delay_days'] ?? 0,
      delayHours: json['delay_hours'] ?? 0,
      templateId: json['template_id']?.toString(),
    );
  }
}

class SequenceEnrollment {
  final String id;
  final String sequenceId;
  final String sequenceName;
  final String contactId;
  final String contactName;
  final String contactEmail;
  final String status;
  final int currentStep;
  final int totalSteps;
  final DateTime enrolledAt;
  final DateTime? completedAt;
  final DateTime? nextEmailAt;

  SequenceEnrollment({
    required this.id,
    required this.sequenceId,
    required this.sequenceName,
    required this.contactId,
    required this.contactName,
    required this.contactEmail,
    required this.status,
    required this.currentStep,
    required this.totalSteps,
    required this.enrolledAt,
    this.completedAt,
    this.nextEmailAt,
  });

  factory SequenceEnrollment.fromJson(Map<String, dynamic> json) {
    return SequenceEnrollment(
      id: json['id']?.toString() ?? '',
      sequenceId: json['sequence_id']?.toString() ?? '',
      sequenceName: json['sequence_name'] ?? '',
      contactId: json['contact_id']?.toString() ?? '',
      contactName: json['contact_name'] ?? '',
      contactEmail: json['contact_email'] ?? '',
      status: json['status'] ?? 'active',
      currentStep: json['current_step'] ?? 1,
      totalSteps: json['total_steps'] ?? 1,
      enrolledAt: DateTime.parse(json['enrolled_at'] ?? DateTime.now().toIso8601String()),
      completedAt: json['completed_at'] != null ? DateTime.parse(json['completed_at']) : null,
      nextEmailAt: json['next_email_at'] != null ? DateTime.parse(json['next_email_at']) : null,
    );
  }

  double get progress => totalSteps > 0 ? currentStep / totalSteps : 0;
}

// ==================== App Marketplace Models ====================

class MarketplaceApp {
  final String id;
  final String name;
  final String slug;
  final String description;
  final String? iconUrl;
  final String category;
  final String developer;
  final double rating;
  final int installCount;
  final double? price;
  final bool isInstalled;
  final List<String> features;

  MarketplaceApp({
    required this.id,
    required this.name,
    required this.slug,
    required this.description,
    this.iconUrl,
    required this.category,
    required this.developer,
    required this.rating,
    required this.installCount,
    this.price,
    required this.isInstalled,
    required this.features,
  });

  factory MarketplaceApp.fromJson(Map<String, dynamic> json) {
    return MarketplaceApp(
      id: json['id']?.toString() ?? '',
      name: json['name'] ?? '',
      slug: json['slug'] ?? '',
      description: json['description'] ?? '',
      iconUrl: json['icon_url'],
      category: json['category'] ?? 'other',
      developer: json['developer'] ?? '',
      rating: (json['rating'] ?? 0).toDouble(),
      installCount: json['install_count'] ?? 0,
      price: json['price'] != null ? (json['price']).toDouble() : null,
      isInstalled: json['is_installed'] ?? false,
      features: List<String>.from(json['features'] ?? []),
    );
  }

  bool get isFree => price == null || price == 0;
}

class InstalledApp {
  final String id;
  final String appId;
  final String appName;
  final bool isActive;
  final Map<String, dynamic> settings;
  final DateTime installedAt;

  InstalledApp({
    required this.id,
    required this.appId,
    required this.appName,
    required this.isActive,
    required this.settings,
    required this.installedAt,
  });

  factory InstalledApp.fromJson(Map<String, dynamic> json) {
    return InstalledApp(
      id: json['id']?.toString() ?? '',
      appId: json['app_id']?.toString() ?? '',
      appName: json['app_name'] ?? '',
      isActive: json['is_active'] ?? true,
      settings: Map<String, dynamic>.from(json['settings'] ?? {}),
      installedAt: DateTime.parse(json['installed_at'] ?? DateTime.now().toIso8601String()),
    );
  }
}

// ==================== Realtime Collaboration Models ====================

class CollaborationSession {
  final String id;
  final String entityType;
  final String entityId;
  final List<Collaborator> collaborators;
  final bool isActive;
  final DateTime startedAt;

  CollaborationSession({
    required this.id,
    required this.entityType,
    required this.entityId,
    required this.collaborators,
    required this.isActive,
    required this.startedAt,
  });

  factory CollaborationSession.fromJson(Map<String, dynamic> json) {
    return CollaborationSession(
      id: json['id']?.toString() ?? '',
      entityType: json['entity_type'] ?? '',
      entityId: json['entity_id']?.toString() ?? '',
      collaborators: (json['collaborators'] as List?)?.map((c) => Collaborator.fromJson(c)).toList() ?? [],
      isActive: json['is_active'] ?? true,
      startedAt: DateTime.parse(json['started_at'] ?? DateTime.now().toIso8601String()),
    );
  }
}

class Collaborator {
  final String id;
  final String name;
  final String? avatarUrl;
  final String status;
  final String? currentField;
  final DateTime joinedAt;

  Collaborator({
    required this.id,
    required this.name,
    this.avatarUrl,
    required this.status,
    this.currentField,
    required this.joinedAt,
  });

  factory Collaborator.fromJson(Map<String, dynamic> json) {
    return Collaborator(
      id: json['id']?.toString() ?? '',
      name: json['name'] ?? '',
      avatarUrl: json['avatar_url'],
      status: json['status'] ?? 'viewing',
      currentField: json['current_field'],
      joinedAt: DateTime.parse(json['joined_at'] ?? DateTime.now().toIso8601String()),
    );
  }
}

// ==================== Social Inbox Models ====================

class SocialMessage {
  final String id;
  final String platform;
  final String senderName;
  final String? senderAvatar;
  final String content;
  final bool isIncoming;
  final String status;
  final String? contactId;
  final DateTime receivedAt;

  SocialMessage({
    required this.id,
    required this.platform,
    required this.senderName,
    this.senderAvatar,
    required this.content,
    required this.isIncoming,
    required this.status,
    this.contactId,
    required this.receivedAt,
  });

  factory SocialMessage.fromJson(Map<String, dynamic> json) {
    return SocialMessage(
      id: json['id']?.toString() ?? '',
      platform: json['platform'] ?? '',
      senderName: json['sender_name'] ?? '',
      senderAvatar: json['sender_avatar'],
      content: json['content'] ?? '',
      isIncoming: json['is_incoming'] ?? true,
      status: json['status'] ?? 'unread',
      contactId: json['contact_id']?.toString(),
      receivedAt: DateTime.parse(json['received_at'] ?? DateTime.now().toIso8601String()),
    );
  }
}

// ==================== Customer Portal Models ====================

class PortalUser {
  final String id;
  final String email;
  final String name;
  final String? contactId;
  final bool isActive;
  final DateTime? lastLoginAt;
  final DateTime createdAt;

  PortalUser({
    required this.id,
    required this.email,
    required this.name,
    this.contactId,
    required this.isActive,
    this.lastLoginAt,
    required this.createdAt,
  });

  factory PortalUser.fromJson(Map<String, dynamic> json) {
    return PortalUser(
      id: json['id']?.toString() ?? '',
      email: json['email'] ?? '',
      name: json['name'] ?? '',
      contactId: json['contact_id']?.toString(),
      isActive: json['is_active'] ?? true,
      lastLoginAt: json['last_login_at'] != null ? DateTime.parse(json['last_login_at']) : null,
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
    );
  }
}

class SupportTicket {
  final String id;
  final String subject;
  final String description;
  final String status;
  final String priority;
  final String? assigneeId;
  final String? assigneeName;
  final String createdById;
  final String createdByName;
  final DateTime createdAt;
  final DateTime? resolvedAt;

  SupportTicket({
    required this.id,
    required this.subject,
    required this.description,
    required this.status,
    required this.priority,
    this.assigneeId,
    this.assigneeName,
    required this.createdById,
    required this.createdByName,
    required this.createdAt,
    this.resolvedAt,
  });

  factory SupportTicket.fromJson(Map<String, dynamic> json) {
    return SupportTicket(
      id: json['id']?.toString() ?? '',
      subject: json['subject'] ?? '',
      description: json['description'] ?? '',
      status: json['status'] ?? 'open',
      priority: json['priority'] ?? 'medium',
      assigneeId: json['assignee_id']?.toString(),
      assigneeName: json['assignee_name'],
      createdById: json['created_by_id']?.toString() ?? '',
      createdByName: json['created_by_name'] ?? '',
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      resolvedAt: json['resolved_at'] != null ? DateTime.parse(json['resolved_at']) : null,
    );
  }
}

// ==================== ESG Reporting Models ====================

class ESGMetric {
  final String id;
  final String category;
  final String name;
  final double value;
  final String unit;
  final String period;
  final double? targetValue;
  final double? previousValue;
  final DateTime recordedAt;

  ESGMetric({
    required this.id,
    required this.category,
    required this.name,
    required this.value,
    required this.unit,
    required this.period,
    this.targetValue,
    this.previousValue,
    required this.recordedAt,
  });

  factory ESGMetric.fromJson(Map<String, dynamic> json) {
    return ESGMetric(
      id: json['id']?.toString() ?? '',
      category: json['category'] ?? '',
      name: json['name'] ?? '',
      value: (json['value'] ?? 0).toDouble(),
      unit: json['unit'] ?? '',
      period: json['period'] ?? '',
      targetValue: json['target_value'] != null ? (json['target_value']).toDouble() : null,
      previousValue: json['previous_value'] != null ? (json['previous_value']).toDouble() : null,
      recordedAt: DateTime.parse(json['recorded_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  double? get changePercent {
    if (previousValue == null || previousValue == 0) return null;
    return ((value - previousValue!) / previousValue!) * 100;
  }

  double? get targetProgress {
    if (targetValue == null || targetValue == 0) return null;
    return (value / targetValue!).clamp(0.0, 1.0);
  }
}
