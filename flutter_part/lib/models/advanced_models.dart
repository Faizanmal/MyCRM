// Advanced Models for MyCRM Flutter App
// Contains data models for AI Insights, Gamification, Integration Hub,
// Revenue Intelligence, Email Tracking, and other premium features

// ==================== Integration Hub Models ====================

class IntegrationProvider {
  final String id;
  final String name;
  final String slug;
  final String description;
  final String? logoUrl;
  final String authType;
  final bool isActive;
  final List<String> supportedFeatures;

  IntegrationProvider({
    required this.id,
    required this.name,
    required this.slug,
    required this.description,
    this.logoUrl,
    required this.authType,
    required this.isActive,
    required this.supportedFeatures,
  });

  factory IntegrationProvider.fromJson(Map<String, dynamic> json) {
    return IntegrationProvider(
      id: json['id']?.toString() ?? '',
      name: json['name'] ?? '',
      slug: json['slug'] ?? '',
      description: json['description'] ?? '',
      logoUrl: json['logo_url'],
      authType: json['auth_type'] ?? 'oauth2',
      isActive: json['is_active'] ?? false,
      supportedFeatures: List<String>.from(json['supported_features'] ?? []),
    );
  }
}

class Integration {
  final String id;
  final IntegrationProvider? provider;
  final String name;
  final bool isActive;
  final String status;
  final Map<String, dynamic> authData;
  final Map<String, dynamic> config;
  final DateTime? lastSyncAt;
  final DateTime? nextSyncAt;
  final int syncFrequency;
  final String? errorMessage;
  final DateTime createdAt;
  final DateTime updatedAt;

  Integration({
    required this.id,
    this.provider,
    required this.name,
    required this.isActive,
    required this.status,
    required this.authData,
    required this.config,
    this.lastSyncAt,
    this.nextSyncAt,
    required this.syncFrequency,
    this.errorMessage,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Integration.fromJson(Map<String, dynamic> json) {
    return Integration(
      id: json['id']?.toString() ?? '',
      provider: json['provider'] != null ? IntegrationProvider.fromJson(json['provider']) : null,
      name: json['name'] ?? '',
      isActive: json['is_active'] ?? false,
      status: json['status'] ?? 'pending',
      authData: Map<String, dynamic>.from(json['auth_data'] ?? {}),
      config: Map<String, dynamic>.from(json['config'] ?? {}),
      lastSyncAt: json['last_sync_at'] != null ? DateTime.parse(json['last_sync_at']) : null,
      nextSyncAt: json['next_sync_at'] != null ? DateTime.parse(json['next_sync_at']) : null,
      syncFrequency: json['sync_frequency'] ?? 60,
      errorMessage: json['error_message'],
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      updatedAt: DateTime.parse(json['updated_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  String get statusColor {
    switch (status) {
      case 'connected':
        return 'green';
      case 'error':
        return 'red';
      case 'pending':
        return 'orange';
      default:
        return 'gray';
    }
  }
}

class SyncHistory {
  final String id;
  final String integrationId;
  final String syncType;
  final String status;
  final int recordsProcessed;
  final int recordsFailed;
  final List<String> errors;
  final DateTime startedAt;
  final DateTime? completedAt;

  SyncHistory({
    required this.id,
    required this.integrationId,
    required this.syncType,
    required this.status,
    required this.recordsProcessed,
    required this.recordsFailed,
    required this.errors,
    required this.startedAt,
    this.completedAt,
  });

  factory SyncHistory.fromJson(Map<String, dynamic> json) {
    return SyncHistory(
      id: json['id']?.toString() ?? '',
      integrationId: json['integration_id']?.toString() ?? '',
      syncType: json['sync_type'] ?? '',
      status: json['status'] ?? '',
      recordsProcessed: json['records_processed'] ?? 0,
      recordsFailed: json['records_failed'] ?? 0,
      errors: List<String>.from(json['errors'] ?? []),
      startedAt: DateTime.parse(json['started_at'] ?? DateTime.now().toIso8601String()),
      completedAt: json['completed_at'] != null ? DateTime.parse(json['completed_at']) : null,
    );
  }
}

// ==================== AI Insights Models ====================

class ChurnPrediction {
  final String id;
  final ContactInfo contact;
  final double churnProbability;
  final String riskLevel;
  final Map<String, dynamic> contributingFactors;
  final List<String> recommendedActions;
  final DateTime predictionDate;
  final String modelVersion;

  ChurnPrediction({
    required this.id,
    required this.contact,
    required this.churnProbability,
    required this.riskLevel,
    required this.contributingFactors,
    required this.recommendedActions,
    required this.predictionDate,
    required this.modelVersion,
  });

  factory ChurnPrediction.fromJson(Map<String, dynamic> json) {
    return ChurnPrediction(
      id: json['id']?.toString() ?? '',
      contact: ContactInfo.fromJson(json['contact'] ?? {}),
      churnProbability: (json['churn_probability'] ?? 0).toDouble(),
      riskLevel: json['risk_level'] ?? 'low',
      contributingFactors: Map<String, dynamic>.from(json['contributing_factors'] ?? {}),
      recommendedActions: List<String>.from(json['recommended_actions'] ?? []),
      predictionDate: DateTime.parse(json['prediction_date'] ?? DateTime.now().toIso8601String()),
      modelVersion: json['model_version'] ?? '1.0',
    );
  }

  String get riskColor {
    switch (riskLevel) {
      case 'critical':
        return 'red';
      case 'high':
        return 'orange';
      case 'medium':
        return 'yellow';
      default:
        return 'green';
    }
  }
}

class ContactInfo {
  final String id;
  final String name;
  final String email;

  ContactInfo({
    required this.id,
    required this.name,
    required this.email,
  });

  factory ContactInfo.fromJson(Map<String, dynamic> json) {
    return ContactInfo(
      id: json['id']?.toString() ?? '',
      name: json['name'] ?? 'Unknown',
      email: json['email'] ?? '',
    );
  }
}

class NextBestAction {
  final String id;
  final ContactInfo contact;
  final String actionType;
  final String priority;
  final String title;
  final String description;
  final String reasoning;
  final double estimatedImpact;
  final String status;
  final DateTime? dueDate;
  final DateTime createdAt;

  NextBestAction({
    required this.id,
    required this.contact,
    required this.actionType,
    required this.priority,
    required this.title,
    required this.description,
    required this.reasoning,
    required this.estimatedImpact,
    required this.status,
    this.dueDate,
    required this.createdAt,
  });

  factory NextBestAction.fromJson(Map<String, dynamic> json) {
    return NextBestAction(
      id: json['id']?.toString() ?? '',
      contact: ContactInfo.fromJson(json['contact'] ?? {}),
      actionType: json['action_type'] ?? '',
      priority: json['priority'] ?? 'low',
      title: json['title'] ?? '',
      description: json['description'] ?? '',
      reasoning: json['reasoning'] ?? '',
      estimatedImpact: (json['estimated_impact'] ?? 0).toDouble(),
      status: json['status'] ?? 'pending',
      dueDate: json['due_date'] != null ? DateTime.parse(json['due_date']) : null,
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  String get priorityColor {
    switch (priority) {
      case 'urgent':
        return 'red';
      case 'high':
        return 'orange';
      case 'medium':
        return 'yellow';
      default:
        return 'blue';
    }
  }
}

class AIGeneratedContent {
  final String id;
  final String contentType;
  final String content;
  final Map<String, dynamic> context;
  final String tone;
  final String length;
  final String status;
  final String modelUsed;
  final double generationTime;
  final DateTime createdAt;

  AIGeneratedContent({
    required this.id,
    required this.contentType,
    required this.content,
    required this.context,
    required this.tone,
    required this.length,
    required this.status,
    required this.modelUsed,
    required this.generationTime,
    required this.createdAt,
  });

  factory AIGeneratedContent.fromJson(Map<String, dynamic> json) {
    return AIGeneratedContent(
      id: json['id']?.toString() ?? '',
      contentType: json['content_type'] ?? '',
      content: json['content'] ?? '',
      context: Map<String, dynamic>.from(json['context'] ?? {}),
      tone: json['tone'] ?? 'professional',
      length: json['length'] ?? 'medium',
      status: json['status'] ?? 'draft',
      modelUsed: json['model_used'] ?? '',
      generationTime: (json['generation_time'] ?? 0).toDouble(),
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
    );
  }
}

class SentimentAnalysis {
  final String id;
  final String text;
  final String sentiment;
  final double score;
  final String sourceType;
  final String? sourceId;
  final DateTime analyzedAt;

  SentimentAnalysis({
    required this.id,
    required this.text,
    required this.sentiment,
    required this.score,
    required this.sourceType,
    this.sourceId,
    required this.analyzedAt,
  });

  factory SentimentAnalysis.fromJson(Map<String, dynamic> json) {
    return SentimentAnalysis(
      id: json['id']?.toString() ?? '',
      text: json['text'] ?? '',
      sentiment: json['sentiment'] ?? 'neutral',
      score: (json['score'] ?? 0).toDouble(),
      sourceType: json['source_type'] ?? '',
      sourceId: json['source_id'],
      analyzedAt: DateTime.parse(json['analyzed_at'] ?? DateTime.now().toIso8601String()),
    );
  }
}

// ==================== Gamification Models ====================

class Achievement {
  final String id;
  final String name;
  final String description;
  final String icon;
  final String category;
  final String difficulty;
  final int points;
  final Map<String, dynamic> criteria;
  final bool isActive;
  final bool isRepeatable;
  final int earnedByCount;
  final bool? isEarned;
  final DateTime? earnedAt;

  Achievement({
    required this.id,
    required this.name,
    required this.description,
    required this.icon,
    required this.category,
    required this.difficulty,
    required this.points,
    required this.criteria,
    required this.isActive,
    required this.isRepeatable,
    required this.earnedByCount,
    this.isEarned,
    this.earnedAt,
  });

  factory Achievement.fromJson(Map<String, dynamic> json) {
    return Achievement(
      id: json['id']?.toString() ?? '',
      name: json['name'] ?? '',
      description: json['description'] ?? '',
      icon: json['icon'] ?? '🏆',
      category: json['category'] ?? '',
      difficulty: json['difficulty'] ?? 'easy',
      points: json['points'] ?? 0,
      criteria: Map<String, dynamic>.from(json['criteria'] ?? {}),
      isActive: json['is_active'] ?? true,
      isRepeatable: json['is_repeatable'] ?? false,
      earnedByCount: json['earned_by_count'] ?? 0,
      isEarned: json['is_earned'],
      earnedAt: json['earned_at'] != null ? DateTime.parse(json['earned_at']) : null,
    );
  }

  String get difficultyColor {
    switch (difficulty) {
      case 'legendary':
        return 'purple';
      case 'hard':
        return 'red';
      case 'medium':
        return 'orange';
      default:
        return 'green';
    }
  }
}

class UserPoints {
  final String id;
  final UserInfo user;
  final int totalPoints;
  final int currentLevel;
  final int pointsToNextLevel;
  final int streakDays;
  final int longestStreak;
  final int achievementsCount;
  final int? rank;

  UserPoints({
    required this.id,
    required this.user,
    required this.totalPoints,
    required this.currentLevel,
    required this.pointsToNextLevel,
    required this.streakDays,
    required this.longestStreak,
    required this.achievementsCount,
    this.rank,
  });

  factory UserPoints.fromJson(Map<String, dynamic> json) {
    return UserPoints(
      id: json['id']?.toString() ?? '',
      user: UserInfo.fromJson(json['user'] ?? {}),
      totalPoints: json['total_points'] ?? 0,
      currentLevel: json['current_level'] ?? 1,
      pointsToNextLevel: json['points_to_next_level'] ?? 100,
      streakDays: json['streak_days'] ?? 0,
      longestStreak: json['longest_streak'] ?? 0,
      achievementsCount: json['achievements_count'] ?? 0,
      rank: json['rank'],
    );
  }

  double get levelProgress {
    if (pointsToNextLevel == 0) return 1.0;
    final current = totalPoints % 100;
    return current / pointsToNextLevel;
  }
}

class UserInfo {
  final String id;
  final String username;
  final String email;
  final String? avatar;

  UserInfo({
    required this.id,
    required this.username,
    required this.email,
    this.avatar,
  });

  factory UserInfo.fromJson(Map<String, dynamic> json) {
    return UserInfo(
      id: json['id']?.toString() ?? '',
      username: json['username'] ?? 'User',
      email: json['email'] ?? '',
      avatar: json['avatar'],
    );
  }
}

class Leaderboard {
  final String id;
  final String name;
  final String description;
  final String metricType;
  final String timePeriod;
  final bool isActive;
  final DateTime createdAt;
  final List<LeaderboardEntry>? entries;

  Leaderboard({
    required this.id,
    required this.name,
    required this.description,
    required this.metricType,
    required this.timePeriod,
    required this.isActive,
    required this.createdAt,
    this.entries,
  });

  factory Leaderboard.fromJson(Map<String, dynamic> json) {
    return Leaderboard(
      id: json['id']?.toString() ?? '',
      name: json['name'] ?? '',
      description: json['description'] ?? '',
      metricType: json['metric_type'] ?? 'points',
      timePeriod: json['time_period'] ?? 'weekly',
      isActive: json['is_active'] ?? true,
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      entries: json['entries'] != null
          ? (json['entries'] as List).map((e) => LeaderboardEntry.fromJson(e)).toList()
          : null,
    );
  }
}

class LeaderboardEntry {
  final int rank;
  final UserInfo user;
  final int score;
  final int change;

  LeaderboardEntry({
    required this.rank,
    required this.user,
    required this.score,
    required this.change,
  });

  factory LeaderboardEntry.fromJson(Map<String, dynamic> json) {
    return LeaderboardEntry(
      rank: json['rank'] ?? 0,
      user: UserInfo.fromJson(json['user'] ?? {}),
      score: json['score'] ?? 0,
      change: json['change'] ?? 0,
    );
  }
}

class Challenge {
  final String id;
  final String name;
  final String description;
  final String challengeType;
  final String goalType;
  final int goalValue;
  final DateTime startDate;
  final DateTime endDate;
  final int rewardPoints;
  final String status;
  final int participantsCount;
  final bool? isParticipating;
  final int? currentProgress;

  Challenge({
    required this.id,
    required this.name,
    required this.description,
    required this.challengeType,
    required this.goalType,
    required this.goalValue,
    required this.startDate,
    required this.endDate,
    required this.rewardPoints,
    required this.status,
    required this.participantsCount,
    this.isParticipating,
    this.currentProgress,
  });

  factory Challenge.fromJson(Map<String, dynamic> json) {
    return Challenge(
      id: json['id']?.toString() ?? '',
      name: json['name'] ?? '',
      description: json['description'] ?? '',
      challengeType: json['challenge_type'] ?? 'individual',
      goalType: json['goal_type'] ?? '',
      goalValue: json['goal_value'] ?? 0,
      startDate: DateTime.parse(json['start_date'] ?? DateTime.now().toIso8601String()),
      endDate: DateTime.parse(json['end_date'] ?? DateTime.now().toIso8601String()),
      rewardPoints: json['reward_points'] ?? 0,
      status: json['status'] ?? 'upcoming',
      participantsCount: json['participants_count'] ?? 0,
      isParticipating: json['is_participating'],
      currentProgress: json['current_progress'],
    );
  }

  double get progressPercent {
    if (currentProgress == null || goalValue == 0) return 0;
    return (currentProgress! / goalValue).clamp(0.0, 1.0);
  }
}

class PointTransaction {
  final String id;
  final int points;
  final String transactionType;
  final String reason;
  final String? referenceType;
  final String? referenceId;
  final DateTime createdAt;

  PointTransaction({
    required this.id,
    required this.points,
    required this.transactionType,
    required this.reason,
    this.referenceType,
    this.referenceId,
    required this.createdAt,
  });

  factory PointTransaction.fromJson(Map<String, dynamic> json) {
    return PointTransaction(
      id: json['id']?.toString() ?? '',
      points: json['points'] ?? 0,
      transactionType: json['transaction_type'] ?? 'earn',
      reason: json['reason'] ?? '',
      referenceType: json['reference_type'],
      referenceId: json['reference_id']?.toString(),
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
    );
  }
}

// ==================== Revenue Intelligence Models ====================

class RevenueTarget {
  final String id;
  final String period;
  final double targetAmount;
  final double currentAmount;
  final String status;
  final DateTime createdAt;

  RevenueTarget({
    required this.id,
    required this.period,
    required this.targetAmount,
    required this.currentAmount,
    required this.status,
    required this.createdAt,
  });

  factory RevenueTarget.fromJson(Map<String, dynamic> json) {
    return RevenueTarget(
      id: json['id']?.toString() ?? '',
      period: json['period'] ?? '',
      targetAmount: (json['target_amount'] ?? 0).toDouble(),
      currentAmount: (json['current_amount'] ?? 0).toDouble(),
      status: json['status'] ?? 'in_progress',
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  double get progressPercent => targetAmount > 0 ? (currentAmount / targetAmount).clamp(0.0, 1.0) : 0;
}

class DealScore {
  final String id;
  final String opportunityId;
  final String opportunityName;
  final int score;
  final String riskLevel;
  final Map<String, dynamic> factors;
  final List<String> recommendations;
  final DateTime scoredAt;

  DealScore({
    required this.id,
    required this.opportunityId,
    required this.opportunityName,
    required this.score,
    required this.riskLevel,
    required this.factors,
    required this.recommendations,
    required this.scoredAt,
  });

  factory DealScore.fromJson(Map<String, dynamic> json) {
    return DealScore(
      id: json['id']?.toString() ?? '',
      opportunityId: json['opportunity_id']?.toString() ?? '',
      opportunityName: json['opportunity_name'] ?? '',
      score: json['score'] ?? 0,
      riskLevel: json['risk_level'] ?? 'medium',
      factors: Map<String, dynamic>.from(json['factors'] ?? {}),
      recommendations: List<String>.from(json['recommendations'] ?? []),
      scoredAt: DateTime.parse(json['scored_at'] ?? DateTime.now().toIso8601String()),
    );
  }
}

class DealRiskAlert {
  final String id;
  final String opportunityId;
  final String alertType;
  final String severity;
  final String message;
  final bool isAcknowledged;
  final bool isResolved;
  final DateTime createdAt;

  DealRiskAlert({
    required this.id,
    required this.opportunityId,
    required this.alertType,
    required this.severity,
    required this.message,
    required this.isAcknowledged,
    required this.isResolved,
    required this.createdAt,
  });

  factory DealRiskAlert.fromJson(Map<String, dynamic> json) {
    return DealRiskAlert(
      id: json['id']?.toString() ?? '',
      opportunityId: json['opportunity_id']?.toString() ?? '',
      alertType: json['alert_type'] ?? '',
      severity: json['severity'] ?? 'medium',
      message: json['message'] ?? '',
      isAcknowledged: json['is_acknowledged'] ?? false,
      isResolved: json['is_resolved'] ?? false,
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
    );
  }
}

// ==================== Campaign Models ====================

class Campaign {
  final String id;
  final String name;
  final String description;
  final String status;
  final String campaignType;
  final DateTime? scheduledAt;
  final DateTime? sentAt;
  final int recipientCount;
  final int openCount;
  final int clickCount;
  final DateTime createdAt;

  Campaign({
    required this.id,
    required this.name,
    required this.description,
    required this.status,
    required this.campaignType,
    this.scheduledAt,
    this.sentAt,
    required this.recipientCount,
    required this.openCount,
    required this.clickCount,
    required this.createdAt,
  });

  factory Campaign.fromJson(Map<String, dynamic> json) {
    return Campaign(
      id: json['id']?.toString() ?? '',
      name: json['name'] ?? '',
      description: json['description'] ?? '',
      status: json['status'] ?? 'draft',
      campaignType: json['campaign_type'] ?? 'email',
      scheduledAt: json['scheduled_at'] != null ? DateTime.parse(json['scheduled_at']) : null,
      sentAt: json['sent_at'] != null ? DateTime.parse(json['sent_at']) : null,
      recipientCount: json['recipient_count'] ?? 0,
      openCount: json['open_count'] ?? 0,
      clickCount: json['click_count'] ?? 0,
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  double get openRate => recipientCount > 0 ? (openCount / recipientCount) : 0;
  double get clickRate => openCount > 0 ? (clickCount / openCount) : 0;
}

// ==================== Email Tracking Models ====================

class TrackedEmail {
  final String id;
  final String toEmail;
  final String subject;
  final String status;
  final int openCount;
  final int clickCount;
  final DateTime? lastOpenedAt;
  final DateTime sentAt;

  TrackedEmail({
    required this.id,
    required this.toEmail,
    required this.subject,
    required this.status,
    required this.openCount,
    required this.clickCount,
    this.lastOpenedAt,
    required this.sentAt,
  });

  factory TrackedEmail.fromJson(Map<String, dynamic> json) {
    return TrackedEmail(
      id: json['id']?.toString() ?? '',
      toEmail: json['to_email'] ?? '',
      subject: json['subject'] ?? '',
      status: json['status'] ?? 'sent',
      openCount: json['open_count'] ?? 0,
      clickCount: json['click_count'] ?? 0,
      lastOpenedAt: json['last_opened_at'] != null ? DateTime.parse(json['last_opened_at']) : null,
      sentAt: DateTime.parse(json['sent_at'] ?? DateTime.now().toIso8601String()),
    );
  }
}

class EmailSequence {
  final String id;
  final String name;
  final String description;
  final String status;
  final int stepsCount;
  final int enrolledCount;
  final DateTime createdAt;

  EmailSequence({
    required this.id,
    required this.name,
    required this.description,
    required this.status,
    required this.stepsCount,
    required this.enrolledCount,
    required this.createdAt,
  });

  factory EmailSequence.fromJson(Map<String, dynamic> json) {
    return EmailSequence(
      id: json['id']?.toString() ?? '',
      name: json['name'] ?? '',
      description: json['description'] ?? '',
      status: json['status'] ?? 'draft',
      stepsCount: json['steps_count'] ?? 0,
      enrolledCount: json['enrolled_count'] ?? 0,
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
    );
  }
}

// ==================== Scheduling Models ====================

class SchedulingPage {
  final String id;
  final String name;
  final String slug;
  final String description;
  final bool isActive;
  final DateTime createdAt;

  SchedulingPage({
    required this.id,
    required this.name,
    required this.slug,
    required this.description,
    required this.isActive,
    required this.createdAt,
  });

  factory SchedulingPage.fromJson(Map<String, dynamic> json) {
    return SchedulingPage(
      id: json['id']?.toString() ?? '',
      name: json['name'] ?? '',
      slug: json['slug'] ?? '',
      description: json['description'] ?? '',
      isActive: json['is_active'] ?? true,
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
    );
  }
}

class ScheduledMeeting {
  final String id;
  final String title;
  final String attendeeName;
  final String attendeeEmail;
  final DateTime startTime;
  final DateTime endTime;
  final String status;
  final String? notes;

  ScheduledMeeting({
    required this.id,
    required this.title,
    required this.attendeeName,
    required this.attendeeEmail,
    required this.startTime,
    required this.endTime,
    required this.status,
    this.notes,
  });

  factory ScheduledMeeting.fromJson(Map<String, dynamic> json) {
    return ScheduledMeeting(
      id: json['id']?.toString() ?? '',
      title: json['title'] ?? '',
      attendeeName: json['attendee_name'] ?? '',
      attendeeEmail: json['attendee_email'] ?? '',
      startTime: DateTime.parse(json['start_time'] ?? DateTime.now().toIso8601String()),
      endTime: DateTime.parse(json['end_time'] ?? DateTime.now().toIso8601String()),
      status: json['status'] ?? 'scheduled',
      notes: json['notes'],
    );
  }
}

// ==================== Customer Success Models ====================

class CustomerAccount {
  final String id;
  final String name;
  final String status;
  final int healthScore;
  final String tier;
  final double annualValue;
  final DateTime renewalDate;
  final DateTime createdAt;

  CustomerAccount({
    required this.id,
    required this.name,
    required this.status,
    required this.healthScore,
    required this.tier,
    required this.annualValue,
    required this.renewalDate,
    required this.createdAt,
  });

  factory CustomerAccount.fromJson(Map<String, dynamic> json) {
    return CustomerAccount(
      id: json['id']?.toString() ?? '',
      name: json['name'] ?? '',
      status: json['status'] ?? 'active',
      healthScore: json['health_score'] ?? 0,
      tier: json['tier'] ?? 'standard',
      annualValue: (json['annual_value'] ?? 0).toDouble(),
      renewalDate: DateTime.parse(json['renewal_date'] ?? DateTime.now().toIso8601String()),
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  String get healthColor {
    if (healthScore >= 80) return 'green';
    if (healthScore >= 60) return 'yellow';
    if (healthScore >= 40) return 'orange';
    return 'red';
  }
}

// ==================== Document E-Sign Models ====================

class EsignDocument {
  final String id;
  final String name;
  final String status;
  final int signersCount;
  final int signedCount;
  final DateTime? sentAt;
  final DateTime? completedAt;
  final DateTime createdAt;

  EsignDocument({
    required this.id,
    required this.name,
    required this.status,
    required this.signersCount,
    required this.signedCount,
    this.sentAt,
    this.completedAt,
    required this.createdAt,
  });

  factory EsignDocument.fromJson(Map<String, dynamic> json) {
    return EsignDocument(
      id: json['id']?.toString() ?? '',
      name: json['name'] ?? '',
      status: json['status'] ?? 'draft',
      signersCount: json['signers_count'] ?? 0,
      signedCount: json['signed_count'] ?? 0,
      sentAt: json['sent_at'] != null ? DateTime.parse(json['sent_at']) : null,
      completedAt: json['completed_at'] != null ? DateTime.parse(json['completed_at']) : null,
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  double get signProgress => signersCount > 0 ? (signedCount / signersCount) : 0;
}

// ==================== Notification Model ====================

class AppNotification {
  final String id;
  final String title;
  final String message;
  final String notificationType;
  final bool isRead;
  final String? actionUrl;
  final DateTime createdAt;

  AppNotification({
    required this.id,
    required this.title,
    required this.message,
    required this.notificationType,
    required this.isRead,
    this.actionUrl,
    required this.createdAt,
  });

  factory AppNotification.fromJson(Map<String, dynamic> json) {
    return AppNotification(
      id: json['id']?.toString() ?? '',
      title: json['title'] ?? '',
      message: json['message'] ?? '',
      notificationType: json['notification_type'] ?? 'info',
      isRead: json['is_read'] ?? false,
      actionUrl: json['action_url'],
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
    );
  }
}
