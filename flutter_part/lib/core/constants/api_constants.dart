/// API Constants for MyCRM Flutter App
/// Contains all API endpoints matching the Django backend
class ApiConstants {
  // Base URL - Change this to your backend URL
  static const String baseUrl = 'http://localhost:8000';
  static const String apiVersion = '/api';
  static const String v1 = '/api/v1';

  // ==================== Auth Endpoints ====================
  static const String login = '$apiVersion/auth/login/';
  static const String register = '$apiVersion/auth/register/';
  static const String logout = '$apiVersion/auth/logout/';
  static const String refreshToken = '$apiVersion/auth/refresh/';
  static const String userProfile = '$apiVersion/auth/users/me/';
  static const String changePassword = '$apiVersion/auth/users/change_password/';
  static const String setup2FA = '$apiVersion/auth/users/setup_2fa/';
  static const String verify2FA = '$apiVersion/auth/users/verify_2fa/';
  static const String disable2FA = '$apiVersion/auth/users/disable_2fa/';

  // ==================== Contacts Endpoints ====================
  static const String contacts = '$apiVersion/contacts/contacts/';
  static String contactDetail(int id) => '$apiVersion/contacts/contacts/$id/';
  static const String contactsBulkUpdate = '$apiVersion/contacts/contacts/bulk_update/';
  static const String contactsBulkDelete = '$apiVersion/contacts/contacts/bulk_delete/';
  static const String contactsExport = '$apiVersion/contacts/contacts/export/';

  // ==================== Leads Endpoints ====================
  static const String leads = '$apiVersion/leads/leads/';
  static String leadDetail(int id) => '$apiVersion/leads/leads/$id/';
  static String convertLead(int id) => '$apiVersion/leads/leads/$id/convert/';

  // ==================== Opportunities Endpoints ====================
  static const String opportunities = '$apiVersion/opportunities/opportunities/';
  static String opportunityDetail(int id) => '$apiVersion/opportunities/opportunities/$id/';

  // ==================== Tasks Endpoints ====================
  static const String tasks = '$apiVersion/tasks/tasks/';
  static String taskDetail(int id) => '$apiVersion/tasks/tasks/$id/';

  // ==================== Communications Endpoints ====================
  static const String communications = '$apiVersion/communications/communications/';
  static String communicationDetail(int id) => '$apiVersion/communications/communications/$id/';

  // ==================== Dashboard Endpoints ====================
  static const String dashboardMetrics = '$apiVersion/reports/analytics/dashboard_metrics/';
  static const String salesPipeline = '$apiVersion/reports/analytics/sales_pipeline/';
  static const String activityFeed = '$apiVersion/activity-feed/';

  // ==================== Reports Endpoints ====================
  static const String reportsDashboard = '$apiVersion/reports/dashboard/';
  static const String reportsKPIs = '$apiVersion/reports/kpis/';
  static const String reportsAnalytics = '$apiVersion/reports/analytics/';
  static const String reports = '$apiVersion/reports/reports/';

  // ==================== Campaign Endpoints ====================
  static const String campaigns = '$apiVersion/campaigns/campaigns/';
  static String campaignDetail(String id) => '$apiVersion/campaigns/campaigns/$id/';
  static String campaignSchedule(String id) => '$apiVersion/campaigns/campaigns/$id/schedule/';
  static String campaignSendNow(String id) => '$apiVersion/campaigns/campaigns/$id/send_now/';
  static String campaignAnalytics(String id) => '$apiVersion/campaigns/campaigns/$id/analytics/';
  static const String campaignStatistics = '$apiVersion/campaigns/campaigns/statistics/';
  static const String segments = '$apiVersion/campaigns/segments/';
  static const String templates = '$apiVersion/campaigns/templates/';

  // ==================== Pipeline Analytics ====================
  static const String pipelineAnalytics = '$apiVersion/core/analytics/pipeline_analytics/';
  static String salesForecast(int months) => '$apiVersion/core/analytics/sales_forecast/?months=$months';
  static const String aiInsightsDashboard = '$apiVersion/core/analytics/ai_insights_dashboard/';

  // ==================== Document Endpoints ====================
  static const String documents = '$apiVersion/documents/documents/';
  static String documentDetail(String id) => '$apiVersion/documents/documents/$id/';
  static String documentDownload(String id) => '$apiVersion/documents/documents/$id/download/';
  static String documentVersions(String id) => '$apiVersion/documents/documents/$id/versions/';
  static String documentShare(String id) => '$apiVersion/documents/documents/$id/share/';
  static const String documentTemplates = '$apiVersion/documents/templates/';
  static const String documentApprovals = '$apiVersion/documents/approvals/';
  static const String documentComments = '$apiVersion/documents/comments/';

  // ==================== Integration Endpoints ====================
  static const String webhooks = '$apiVersion/integrations/webhooks/';
  static const String integrations = '$apiVersion/integrations/integrations/';
  static String integrationSync(String id) => '$apiVersion/integrations/integrations/$id/sync/';
  static String integrationTest(String id) => '$apiVersion/integrations/integrations/$id/test/';
  static String integrationLogs(String id) => '$apiVersion/integrations/integrations/$id/logs/';

  // ==================== Activity Feed Endpoints ====================
  static const String activities = '$apiVersion/activity/activities/';
  static const String myFeed = '$apiVersion/activity/activities/my_feed/';
  static const String comments = '$apiVersion/activity/comments/';
  static const String notifications = '$apiVersion/activity/notifications/';
  static const String notificationsUnreadCount = '$apiVersion/activity/notifications/unread_count/';
  static const String mentions = '$apiVersion/activity/mentions/';
  static const String follows = '$apiVersion/activity/follows/';

  // ==================== Lead Qualification Endpoints ====================
  static const String scoringRules = '$apiVersion/lead-qualification/scoring-rules/';
  static const String qualificationCriteria = '$apiVersion/lead-qualification/qualification-criteria/';
  static const String leadScores = '$apiVersion/lead-qualification/lead-scores/';
  static const String leadScoresSummary = '$apiVersion/lead-qualification/lead-scores/summary/';
  static const String qualificationWorkflows = '$apiVersion/lead-qualification/qualification-workflows/';
  static const String leadEnrichment = '$apiVersion/lead-qualification/lead-enrichment/';

  // ==================== Advanced Reporting Endpoints ====================
  static const String advancedDashboards = '$apiVersion/advanced-reporting/dashboards/';
  static const String advancedWidgets = '$apiVersion/advanced-reporting/widgets/';
  static const String advancedReports = '$apiVersion/advanced-reporting/reports/';
  static const String advancedSchedules = '$apiVersion/advanced-reporting/schedules/';
  static const String advancedExecutions = '$apiVersion/advanced-reporting/executions/';
  static const String advancedKPIs = '$apiVersion/advanced-reporting/kpis/';
  static const String kpiValues = '$apiVersion/advanced-reporting/kpi-values/';

  // ==================== Integration Hub (v1) Endpoints ====================
  static const String integrationHubProviders = '$v1/integration-hub/providers/';
  static const String integrationHubIntegrations = '$v1/integration-hub/integrations/';
  static String integrationInitiateAuth(String id) => '$v1/integration-hub/integrations/$id/initiate_auth/';
  static String integrationTestConnection(String id) => '$v1/integration-hub/integrations/$id/test_connection/';
  static String integrationSyncNow(String id) => '$v1/integration-hub/integrations/$id/sync_now/';
  static const String fieldMappings = '$v1/integration-hub/field-mappings/';
  static const String syncHistory = '$v1/integration-hub/sync-history/';

  // ==================== AI Insights (v1) Endpoints ====================
  static const String churnPredictions = '$v1/ai-insights/churn-predictions/';
  static const String churnStatistics = '$v1/ai-insights/churn-predictions/statistics/';
  static const String churnHighRisk = '$v1/ai-insights/churn-predictions/high_risk/';
  static const String churnBulkPredict = '$v1/ai-insights/churn-predictions/bulk_predict/';
  static const String nextBestActions = '$v1/ai-insights/next-best-actions/';
  static String completeAction(String id) => '$v1/ai-insights/next-best-actions/$id/complete/';
  static String dismissAction(String id) => '$v1/ai-insights/next-best-actions/$id/dismiss/';
  static const String generatedContent = '$v1/ai-insights/generated-content/';
  static String regenerateContent(String id) => '$v1/ai-insights/generated-content/$id/regenerate/';
  static String approveContent(String id) => '$v1/ai-insights/generated-content/$id/approve/';
  static const String sentimentAnalysis = '$v1/ai-insights/sentiment-analysis/';
  static const String sentimentTrends = '$v1/ai-insights/sentiment-analysis/trends/';

  // ==================== Gamification (v1) Endpoints ====================
  static const String achievements = '$v1/gamification/achievements/';
  static const String myAchievements = '$v1/gamification/achievements/my_achievements/';
  static String achievementProgress(String id) => '$v1/gamification/achievements/$id/progress/';
  static const String userPoints = '$v1/gamification/user-points/';
  static const String myPoints = '$v1/gamification/user-points/my_points/';
  static const String pointsHistory = '$v1/gamification/user-points/points_history/';
  static const String leaderboards = '$v1/gamification/leaderboards/';
  static String leaderboardRankings(String id) => '$v1/gamification/leaderboards/$id/rankings/';
  static String myRanking(String id) => '$v1/gamification/leaderboards/$id/my_ranking/';
  static const String challenges = '$v1/gamification/challenges/';
  static const String myChallenges = '$v1/gamification/challenges/my_challenges/';
  static String joinChallenge(String id) => '$v1/gamification/challenges/$id/join/';
  static String leaveChallenge(String id) => '$v1/gamification/challenges/$id/leave/';
  static const String activeTeamChallenges = '$v1/gamification/challenges/active_team_challenges/';
  static const String pointTransactions = '$v1/gamification/point-transactions/';
  static const String myTransactions = '$v1/gamification/point-transactions/my_transactions/';

  // ==================== Revenue Intelligence (v1) Endpoints ====================
  static const String revenueTargets = '$v1/revenue-intelligence/targets/';
  static const String dealScores = '$v1/revenue-intelligence/deal-scores/';
  static const String dealScoresBulkScore = '$v1/revenue-intelligence/deal-scores/bulk_score/';
  static const String pipelineSnapshots = '$v1/revenue-intelligence/snapshots/';
  static const String createSnapshot = '$v1/revenue-intelligence/snapshots/create_snapshot/';
  static const String forecasts = '$v1/revenue-intelligence/forecasts/';
  static const String riskAlerts = '$v1/revenue-intelligence/risk-alerts/';
  static String acknowledgeAlert(String id) => '$v1/revenue-intelligence/risk-alerts/$id/acknowledge/';
  static String resolveAlert(String id) => '$v1/revenue-intelligence/risk-alerts/$id/resolve/';
  static const String competitors = '$v1/revenue-intelligence/competitors/';
  static const String winLossAnalysis = '$v1/revenue-intelligence/win-loss-analysis/';

  // ==================== Email Tracking (v1) Endpoints ====================
  static const String trackedEmails = '$v1/email-tracking/emails/';
  static String emailEvents(String id) => '$v1/email-tracking/emails/$id/events/';
  static const String emailTemplates = '$v1/email-tracking/templates/';
  static const String emailSequences = '$v1/email-tracking/sequences/';
  static String activateSequence(String id) => '$v1/email-tracking/sequences/$id/activate/';
  static String pauseSequence(String id) => '$v1/email-tracking/sequences/$id/pause/';
  static const String sequenceEnrollments = '$v1/email-tracking/enrollments/';
  static const String emailAnalytics = '$v1/email-tracking/analytics/';

  // ==================== Smart Scheduling (v1) Endpoints ====================
  static const String schedulingPages = '$v1/scheduling/pages/';
  static const String meetingTypes = '$v1/scheduling/meeting-types/';
  static const String availability = '$v1/scheduling/availability/';
  static const String scheduledMeetings = '$v1/scheduling/meetings/';
  static String cancelMeeting(String id) => '$v1/scheduling/meetings/$id/cancel/';
  static String rescheduleMeeting(String id) => '$v1/scheduling/meetings/$id/reschedule/';
  static const String calendarIntegrations = '$v1/scheduling/calendar-integrations/';
  static const String schedulingAnalytics = '$v1/scheduling/analytics/';

  // ==================== AI Sales Assistant (v1) Endpoints ====================
  // AI-powered email generation, coaching, objection handling, and call scripts
  static const String emailDrafts = '$v1/ai-assistant/email-drafts/';
  static String regenerateDraft(String id) => '$v1/ai-assistant/email-drafts/$id/regenerate/';
  static const String coaching = '$v1/ai-assistant/coaching/';
  static const String objections = '$v1/ai-assistant/objections/';
  static const String callScripts = '$v1/ai-assistant/call-scripts/';
  static const String dealInsights = '$v1/ai-assistant/deal-insights/';
  static const String winLossAnalysisSales = '$v1/ai-assistant/win-loss-analysis/';
  static const String personas = '$v1/ai-assistant/personas/';

  // ==================== Social Selling (v1) Endpoints ====================
  static const String socialProfiles = '$v1/social-selling/profiles/';
  static String refreshSocialProfile(String id) => '$v1/social-selling/profiles/$id/refresh/';
  static const String socialPosts = '$v1/social-selling/posts/';
  static const String socialEngagements = '$v1/social-selling/engagements/';
  static const String socialScores = '$v1/social-selling/scores/';
  static const String socialContent = '$v1/social-selling/content/';
  static const String socialCampaigns = '$v1/social-selling/campaigns/';
  static const String linkedInConnect = '$v1/social-selling/linkedin/connect/';
  static const String linkedInStatus = '$v1/social-selling/linkedin/status/';

  // ==================== Document E-Sign (v1) Endpoints ====================
  static const String esignTemplates = '$v1/documents/templates/';
  static const String esignDocuments = '$v1/documents/documents/';
  static String sendForSignature(String id) => '$v1/documents/documents/$id/send/';
  static String downloadEsignDocument(String id) => '$v1/documents/documents/$id/download/';
  static String voidDocument(String id) => '$v1/documents/documents/$id/void/';
  static String getSignatures(String id) => '$v1/documents/documents/$id/signatures/';
  static String signDocument(String id) => '$v1/documents/documents/$id/sign/';
  static String auditLog(String id) => '$v1/documents/documents/$id/audit-log/';
  static const String esignAnalytics = '$v1/documents/analytics/';

  // ==================== Conversation Intelligence (v1) Endpoints ====================
  static const String callRecordings = '$v1/conversation-intelligence/recordings/';
  static String processRecording(String id) => '$v1/conversation-intelligence/recordings/$id/process/';
  static String getTranscript(String id) => '$v1/conversation-intelligence/recordings/$id/transcript/';
  static const String searchTranscripts = '$v1/conversation-intelligence/transcripts/search/';
  static String getAnalysis(String id) => '$v1/conversation-intelligence/recordings/$id/analysis/';
  static String getKeyMoments(String id) => '$v1/conversation-intelligence/recordings/$id/key-moments/';
  static const String talkPatterns = '$v1/conversation-intelligence/talk-patterns/';
  static String coachingInsights(String id) => '$v1/conversation-intelligence/recordings/$id/coaching/';
  static const String teamCoaching = '$v1/conversation-intelligence/coaching/team/';
  static const String callLibrary = '$v1/conversation-intelligence/library/';
  static const String conversationAnalytics = '$v1/conversation-intelligence/analytics/';

  // ==================== White-Label (v1) Endpoints ====================
  static const String partners = '$v1/white-label/partners/';
  static const String organizations = '$v1/white-label/organizations/';
  static String organizationMembers(String orgId) => '$v1/white-label/organizations/$orgId/members/';
  static const String subscriptionPlans = '$v1/white-label/plans/';
  static const String subscription = '$v1/white-label/subscription/';
  static const String cancelSubscription = '$v1/white-label/subscription/cancel/';
  static const String changePlan = '$v1/white-label/subscription/change-plan/';
  static const String invoices = '$v1/white-label/invoices/';
  static const String paymentMethods = '$v1/white-label/payment-methods/';
  static const String usage = '$v1/white-label/usage/';
  static const String branding = '$v1/white-label/branding/';

  // ==================== Customer Success (v1) Endpoints ====================
  static const String csAccounts = '$v1/customer-success/accounts/';
  static String accountHealth(String id) => '$v1/customer-success/accounts/$id/health/';
  static String recalculateHealth(String id) => '$v1/customer-success/accounts/$id/recalculate-health/';
  static String healthTrends(String id) => '$v1/customer-success/accounts/$id/health-trends/';
  static const String healthScores = '$v1/customer-success/health-scores/';
  static const String healthConfig = '$v1/customer-success/health-config/';
  static String customerJourney(String id) => '$v1/customer-success/accounts/$id/journey/';
  static String customerMilestones(String id) => '$v1/customer-success/accounts/$id/milestones/';
  static const String churnRisks = '$v1/customer-success/churn-risks/';
  static String accountChurnRisk(String id) => '$v1/customer-success/accounts/$id/churn-risk/';
  static String predictChurnCS(String id) => '$v1/customer-success/accounts/$id/predict-churn/';
  static const String expansionOpportunities = '$v1/customer-success/expansion-opportunities/';
  static const String playbooks = '$v1/customer-success/playbooks/';
  static String executePlaybook(String id) => '$v1/customer-success/playbooks/$id/execute/';
  static String customerNotes(String id) => '$v1/customer-success/accounts/$id/notes/';
  static const String npsSurveys = '$v1/customer-success/nps-surveys/';
  static const String npsAnalytics = '$v1/customer-success/nps-analytics/';
  static const String renewals = '$v1/customer-success/renewals/';
  static const String upcomingRenewals = '$v1/customer-success/renewals/upcoming/';
  static const String csDashboard = '$v1/customer-success/dashboard/';
  static const String csMetrics = '$v1/customer-success/metrics/';

  // ==================== GDPR Compliance Endpoints ====================
  static const String gdprConsents = '$apiVersion/gdpr/consents/';
  static const String dataSubjectRequests = '$apiVersion/gdpr/data-subject-requests/';
  static const String dataExport = '$apiVersion/gdpr/data-export/';
  static const String dataDelete = '$apiVersion/gdpr/data-delete/';

  // ==================== SSO Settings Endpoints ====================
  static const String ssoProviders = '$apiVersion/sso/providers/';
  static const String ssoSettings = '$apiVersion/sso/settings/';
}
