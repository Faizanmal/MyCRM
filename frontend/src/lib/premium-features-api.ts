/**
 * Premium Features API - Revenue Intelligence, Email Tracking, Smart Scheduling,
 * AI Sales Assistant, Social Selling, Document E-Sign, Conversation Intelligence,
 * White-Label, and Customer Success
 */

import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Create axios instance with interceptors
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
            refresh: refreshToken,
          });
          const { access } = response.data;
          localStorage.setItem('access_token', access);
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return apiClient(originalRequest);
        }
      } catch {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// ==================== Revenue Intelligence API ====================
export const revenueIntelligenceAPI = {
  // Revenue Targets
  getTargets: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/revenue-intelligence/targets/', { params }),
  getTarget: (id: string) =>
    apiClient.get(`/v1/revenue-intelligence/targets/${id}/`),
  createTarget: (data: Record<string, unknown>) =>
    apiClient.post('/v1/revenue-intelligence/targets/', data),
  updateTarget: (id: string, data: Record<string, unknown>) =>
    apiClient.patch(`/v1/revenue-intelligence/targets/${id}/`, data),

  // Deal Scores
  getDealScores: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/revenue-intelligence/deal-scores/', { params }),
  getDealScore: (id: string) =>
    apiClient.get(`/v1/revenue-intelligence/deal-scores/${id}/`),
  scoreDeal: (opportunityId: string) =>
    apiClient.post('/v1/revenue-intelligence/deal-scores/', { opportunity_id: opportunityId }),
  bulkScoreDeals: () =>
    apiClient.post('/v1/revenue-intelligence/deal-scores/bulk_score/'),

  // Pipeline Snapshots
  getSnapshots: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/revenue-intelligence/snapshots/', { params }),
  createSnapshot: () =>
    apiClient.post('/v1/revenue-intelligence/snapshots/create_snapshot/'),

  // Forecasts
  getForecasts: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/revenue-intelligence/forecasts/', { params }),
  generateForecast: (data: { period: string; method?: string }) =>
    apiClient.post('/v1/revenue-intelligence/forecasts/', data),

  // Deal Risk Alerts
  getRiskAlerts: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/revenue-intelligence/risk-alerts/', { params }),
  acknowledgeAlert: (id: string) =>
    apiClient.post(`/v1/revenue-intelligence/risk-alerts/${id}/acknowledge/`),
  resolveAlert: (id: string, data: { resolution_notes: string }) =>
    apiClient.post(`/v1/revenue-intelligence/risk-alerts/${id}/resolve/`, data),

  // Competitors
  getCompetitors: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/revenue-intelligence/competitors/', { params }),
  createCompetitor: (data: Record<string, unknown>) =>
    apiClient.post('/v1/revenue-intelligence/competitors/', data),

  // Win/Loss Analysis
  getWinLossAnalysis: (params?: { period?: string }) =>
    apiClient.get('/v1/revenue-intelligence/win-loss-analysis/', { params }),
};

// ==================== Email Tracking API ====================
export const emailTrackingAPI = {
  // Tracked Emails
  getEmails: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/email-tracking/emails/', { params }),
  getEmail: (id: string) =>
    apiClient.get(`/v1/email-tracking/emails/${id}/`),
  sendEmail: (data: {
    to_email: string;
    subject: string;
    body: string;
    template_id?: string;
  }) => apiClient.post('/v1/email-tracking/emails/', data),
  getEmailEvents: (id: string) =>
    apiClient.get(`/v1/email-tracking/emails/${id}/events/`),

  // Email Templates
  getTemplates: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/email-tracking/templates/', { params }),
  getTemplate: (id: string) =>
    apiClient.get(`/v1/email-tracking/templates/${id}/`),
  createTemplate: (data: Record<string, unknown>) =>
    apiClient.post('/v1/email-tracking/templates/', data),
  updateTemplate: (id: string, data: Record<string, unknown>) =>
    apiClient.patch(`/v1/email-tracking/templates/${id}/`, data),
  deleteTemplate: (id: string) =>
    apiClient.delete(`/v1/email-tracking/templates/${id}/`),
  duplicateTemplate: (id: string) =>
    apiClient.post(`/v1/email-tracking/templates/${id}/duplicate/`),

  // Email Sequences
  getSequences: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/email-tracking/sequences/', { params }),
  getSequence: (id: string) =>
    apiClient.get(`/v1/email-tracking/sequences/${id}/`),
  createSequence: (data: Record<string, unknown>) =>
    apiClient.post('/v1/email-tracking/sequences/', data),
  updateSequence: (id: string, data: Record<string, unknown>) =>
    apiClient.patch(`/v1/email-tracking/sequences/${id}/`, data),
  activateSequence: (id: string) =>
    apiClient.post(`/v1/email-tracking/sequences/${id}/activate/`),
  pauseSequence: (id: string) =>
    apiClient.post(`/v1/email-tracking/sequences/${id}/pause/`),

  // Sequence Enrollments
  getEnrollments: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/email-tracking/enrollments/', { params }),
  enrollContact: (data: { sequence_id: string; contact_id: string }) =>
    apiClient.post('/v1/email-tracking/enrollments/', data),
  unenrollContact: (id: string) =>
    apiClient.post(`/v1/email-tracking/enrollments/${id}/unenroll/`),

  // Analytics
  getAnalytics: (params?: { period?: string }) =>
    apiClient.get('/v1/email-tracking/analytics/', { params }),
};

// ==================== Smart Scheduling API ====================
export const smartSchedulingAPI = {
  // Scheduling Pages
  getPages: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/scheduling/pages/', { params }),
  getPage: (id: string) =>
    apiClient.get(`/v1/scheduling/pages/${id}/`),
  createPage: (data: Record<string, unknown>) =>
    apiClient.post('/v1/scheduling/pages/', data),
  updatePage: (id: string, data: Record<string, unknown>) =>
    apiClient.patch(`/v1/scheduling/pages/${id}/`, data),
  getPublicPage: (slug: string) =>
    apiClient.get(`/v1/scheduling/pages/public/${slug}/`),

  // Meeting Types
  getMeetingTypes: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/scheduling/meeting-types/', { params }),
  getMeetingType: (id: string) =>
    apiClient.get(`/v1/scheduling/meeting-types/${id}/`),
  createMeetingType: (data: Record<string, unknown>) =>
    apiClient.post('/v1/scheduling/meeting-types/', data),
  updateMeetingType: (id: string, data: Record<string, unknown>) =>
    apiClient.patch(`/v1/scheduling/meeting-types/${id}/`, data),

  // Availability
  getAvailability: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/scheduling/availability/', { params }),
  setAvailability: (data: Record<string, unknown>) =>
    apiClient.post('/v1/scheduling/availability/', data),
  updateAvailability: (id: string, data: Record<string, unknown>) =>
    apiClient.patch(`/v1/scheduling/availability/${id}/`, data),

  // Meetings
  getMeetings: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/scheduling/meetings/', { params }),
  getMeeting: (id: string) =>
    apiClient.get(`/v1/scheduling/meetings/${id}/`),
  bookMeeting: (data: {
    meeting_type_id: string;
    start_time: string;
    attendee_name: string;
    attendee_email: string;
    notes?: string;
  }) => apiClient.post('/v1/scheduling/meetings/', data),
  cancelMeeting: (id: string, reason?: string) =>
    apiClient.post(`/v1/scheduling/meetings/${id}/cancel/`, { reason }),
  rescheduleMeeting: (id: string, newTime: string) =>
    apiClient.post(`/v1/scheduling/meetings/${id}/reschedule/`, { new_start_time: newTime }),

  // Calendar Integrations
  getCalendarIntegrations: () =>
    apiClient.get('/v1/scheduling/calendar-integrations/'),
  connectCalendar: (provider: string) =>
    apiClient.post('/v1/scheduling/calendar-integrations/', { provider }),
  disconnectCalendar: (id: string) =>
    apiClient.delete(`/v1/scheduling/calendar-integrations/${id}/`),
  syncCalendar: (id: string) =>
    apiClient.post(`/v1/scheduling/calendar-integrations/${id}/sync/`),

  // Analytics
  getSchedulingAnalytics: (params?: { period?: string }) =>
    apiClient.get('/v1/scheduling/analytics/', { params }),
};

// ==================== AI Sales Assistant API ====================
export const aiSalesAssistantAPI = {
  // Email Drafts
  generateEmailDraft: (data: {
    contact_id?: string;
    opportunity_id?: string;
    email_type: string;
    context?: string;
    tone?: string;
  }) => apiClient.post('/v1/ai-assistant/email-drafts/', data),
  getEmailDrafts: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/ai-assistant/email-drafts/', { params }),
  getEmailDraft: (id: string) =>
    apiClient.get(`/v1/ai-assistant/email-drafts/${id}/`),
  regenerateDraft: (id: string, feedback?: string) =>
    apiClient.post(`/v1/ai-assistant/email-drafts/${id}/regenerate/`, { feedback }),

  // Sales Coaching
  getCoachingAdvice: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/ai-assistant/coaching/', { params }),
  requestCoaching: (data: {
    opportunity_id?: string;
    situation: string;
    coaching_type: string;
  }) => apiClient.post('/v1/ai-assistant/coaching/', data),
  markHelpful: (id: string, helpful: boolean) =>
    apiClient.post(`/v1/ai-assistant/coaching/${id}/feedback/`, { helpful }),

  // Objection Handling
  getObjectionResponses: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/ai-assistant/objections/', { params }),
  generateObjectionResponse: (data: {
    objection: string;
    context?: string;
    product?: string;
  }) => apiClient.post('/v1/ai-assistant/objections/', data),

  // Call Scripts
  getCallScripts: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/ai-assistant/call-scripts/', { params }),
  generateCallScript: (data: {
    call_type: string;
    contact_id?: string;
    talking_points?: string[];
  }) => apiClient.post('/v1/ai-assistant/call-scripts/', data),

  // Deal Insights
  getDealInsights: (opportunityId: string) =>
    apiClient.get(`/v1/ai-assistant/deal-insights/${opportunityId}/`),
  generateDealInsights: (opportunityId: string) =>
    apiClient.post('/v1/ai-assistant/deal-insights/', { opportunity_id: opportunityId }),

  // Win/Loss Analysis
  analyzeWinLoss: (opportunityId: string) =>
    apiClient.post('/v1/ai-assistant/win-loss-analysis/', { opportunity_id: opportunityId }),
  getWinLossAnalyses: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/ai-assistant/win-loss-analysis/', { params }),

  // Persona Profiles
  getPersonaProfiles: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/ai-assistant/personas/', { params }),
  analyzePersona: (contactId: string) =>
    apiClient.post('/v1/ai-assistant/personas/', { contact_id: contactId }),
};

// ==================== Social Selling API ====================
export const socialSellingAPI = {
  // Social Profiles
  getProfiles: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/social-selling/profiles/', { params }),
  getProfile: (id: string) =>
    apiClient.get(`/v1/social-selling/profiles/${id}/`),
  linkProfile: (data: { contact_id: string; platform: string; profile_url: string }) =>
    apiClient.post('/v1/social-selling/profiles/', data),
  refreshProfile: (id: string) =>
    apiClient.post(`/v1/social-selling/profiles/${id}/refresh/`),

  // Social Posts
  getPosts: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/social-selling/posts/', { params }),
  trackPost: (data: Record<string, unknown>) =>
    apiClient.post('/v1/social-selling/posts/', data),

  // Engagements
  getEngagements: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/social-selling/engagements/', { params }),
  recordEngagement: (data: Record<string, unknown>) =>
    apiClient.post('/v1/social-selling/engagements/', data),

  // Social Selling Score
  getScores: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/social-selling/scores/', { params }),
  calculateScore: (userId: string) =>
    apiClient.post('/v1/social-selling/scores/', { user_id: userId }),

  // Content Library
  getContentLibrary: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/social-selling/content/', { params }),
  createContent: (data: Record<string, unknown>) =>
    apiClient.post('/v1/social-selling/content/', data),
  updateContent: (id: string, data: Record<string, unknown>) =>
    apiClient.patch(`/v1/social-selling/content/${id}/`, data),

  // Social Campaigns
  getCampaigns: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/social-selling/campaigns/', { params }),
  createCampaign: (data: Record<string, unknown>) =>
    apiClient.post('/v1/social-selling/campaigns/', data),

  // LinkedIn Integration
  connectLinkedIn: () =>
    apiClient.post('/v1/social-selling/linkedin/connect/'),
  getLinkedInStatus: () =>
    apiClient.get('/v1/social-selling/linkedin/status/'),
};

// ==================== Document E-Sign API ====================
export const documentEsignAPI = {
  // Document Templates
  getTemplates: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/documents/templates/', { params }),
  getTemplate: (id: string) =>
    apiClient.get(`/v1/documents/templates/${id}/`),
  createTemplate: (data: FormData) =>
    apiClient.post('/v1/documents/templates/', data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  updateTemplate: (id: string, data: Record<string, unknown>) =>
    apiClient.patch(`/v1/documents/templates/${id}/`, data),
  deleteTemplate: (id: string) =>
    apiClient.delete(`/v1/documents/templates/${id}/`),

  // Documents
  getDocuments: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/documents/documents/', { params }),
  getDocument: (id: string) =>
    apiClient.get(`/v1/documents/documents/${id}/`),
  createDocument: (data: { template_id: string; name: string; data?: Record<string, unknown> }) =>
    apiClient.post('/v1/documents/documents/', data),
  sendForSignature: (id: string, recipients: Array<{ email: string; name: string; role: string }>) =>
    apiClient.post(`/v1/documents/documents/${id}/send/`, { recipients }),
  downloadDocument: (id: string) =>
    apiClient.get(`/v1/documents/documents/${id}/download/`, { responseType: 'blob' }),
  voidDocument: (id: string, reason: string) =>
    apiClient.post(`/v1/documents/documents/${id}/void/`, { reason }),

  // Signatures
  getSignatures: (documentId: string) =>
    apiClient.get(`/v1/documents/documents/${documentId}/signatures/`),
  signDocument: (documentId: string, signatureData: { signature_image: string; ip_address?: string }) =>
    apiClient.post(`/v1/documents/documents/${documentId}/sign/`, signatureData),

  // Audit Log
  getAuditLog: (documentId: string) =>
    apiClient.get(`/v1/documents/documents/${documentId}/audit-log/`),

  // Analytics
  getAnalytics: (params?: { period?: string }) =>
    apiClient.get('/v1/documents/analytics/', { params }),
};

// ==================== Conversation Intelligence API ====================
export const conversationIntelligenceAPI = {
  // Call Recordings
  getRecordings: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/conversation-intelligence/recordings/', { params }),
  getRecording: (id: string) =>
    apiClient.get(`/v1/conversation-intelligence/recordings/${id}/`),
  uploadRecording: (data: FormData) =>
    apiClient.post('/v1/conversation-intelligence/recordings/', data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  deleteRecording: (id: string) =>
    apiClient.delete(`/v1/conversation-intelligence/recordings/${id}/`),
  processRecording: (id: string) =>
    apiClient.post(`/v1/conversation-intelligence/recordings/${id}/process/`),

  // Transcripts
  getTranscript: (recordingId: string) =>
    apiClient.get(`/v1/conversation-intelligence/recordings/${recordingId}/transcript/`),
  searchTranscripts: (query: string, params?: Record<string, unknown>) =>
    apiClient.get('/v1/conversation-intelligence/transcripts/search/', { params: { q: query, ...params } }),

  // Call Analysis
  getAnalysis: (recordingId: string) =>
    apiClient.get(`/v1/conversation-intelligence/recordings/${recordingId}/analysis/`),
  getKeyMoments: (recordingId: string) =>
    apiClient.get(`/v1/conversation-intelligence/recordings/${recordingId}/key-moments/`),

  // Talk Patterns
  getTalkPatterns: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/conversation-intelligence/talk-patterns/', { params }),
  getUserTalkPatterns: (userId: string, params?: Record<string, unknown>) =>
    apiClient.get(`/v1/conversation-intelligence/talk-patterns/user/${userId}/`, { params }),

  // Coaching
  getCoachingInsights: (recordingId: string) =>
    apiClient.get(`/v1/conversation-intelligence/recordings/${recordingId}/coaching/`),
  getTeamCoaching: (params?: { period?: string }) =>
    apiClient.get('/v1/conversation-intelligence/coaching/team/', { params }),

  // Call Library
  getCallLibrary: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/conversation-intelligence/library/', { params }),
  addToLibrary: (recordingId: string, data: { category: string; tags?: string[] }) =>
    apiClient.post('/v1/conversation-intelligence/library/', { recording_id: recordingId, ...data }),

  // Analytics
  getAnalytics: (params?: { period?: string; team_id?: string }) =>
    apiClient.get('/v1/conversation-intelligence/analytics/', { params }),
};

// ==================== White-Label & Billing API ====================
export const whiteLabelAPI = {
  // Partner Management (admin only)
  getPartners: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/white-label/partners/', { params }),
  getPartner: (id: string) =>
    apiClient.get(`/v1/white-label/partners/${id}/`),
  createPartner: (data: Record<string, unknown>) =>
    apiClient.post('/v1/white-label/partners/', data),
  updatePartner: (id: string, data: Record<string, unknown>) =>
    apiClient.patch(`/v1/white-label/partners/${id}/`, data),

  // Organizations
  getOrganizations: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/white-label/organizations/', { params }),
  getOrganization: (id: string) =>
    apiClient.get(`/v1/white-label/organizations/${id}/`),
  createOrganization: (data: Record<string, unknown>) =>
    apiClient.post('/v1/white-label/organizations/', data),
  updateOrganization: (id: string, data: Record<string, unknown>) =>
    apiClient.patch(`/v1/white-label/organizations/${id}/`, data),

  // Organization Members
  getMembers: (orgId: string) =>
    apiClient.get(`/v1/white-label/organizations/${orgId}/members/`),
  inviteMember: (orgId: string, data: { email: string; role: string }) =>
    apiClient.post(`/v1/white-label/organizations/${orgId}/members/`, data),
  updateMember: (orgId: string, memberId: string, data: Record<string, unknown>) =>
    apiClient.patch(`/v1/white-label/organizations/${orgId}/members/${memberId}/`, data),
  removeMember: (orgId: string, memberId: string) =>
    apiClient.delete(`/v1/white-label/organizations/${orgId}/members/${memberId}/`),

  // Subscription Plans
  getPlans: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/white-label/plans/', { params }),
  getPlan: (id: string) =>
    apiClient.get(`/v1/white-label/plans/${id}/`),

  // Subscriptions
  getSubscription: () =>
    apiClient.get('/v1/white-label/subscription/'),
  createSubscription: (planId: string) =>
    apiClient.post('/v1/white-label/subscription/', { plan_id: planId }),
  cancelSubscription: (reason?: string) =>
    apiClient.post('/v1/white-label/subscription/cancel/', { reason }),
  changePlan: (newPlanId: string) =>
    apiClient.post('/v1/white-label/subscription/change-plan/', { plan_id: newPlanId }),

  // Invoices
  getInvoices: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/white-label/invoices/', { params }),
  getInvoice: (id: string) =>
    apiClient.get(`/v1/white-label/invoices/${id}/`),
  downloadInvoice: (id: string) =>
    apiClient.get(`/v1/white-label/invoices/${id}/download/`, { responseType: 'blob' }),

  // Payment Methods
  getPaymentMethods: () =>
    apiClient.get('/v1/white-label/payment-methods/'),
  addPaymentMethod: (data: Record<string, unknown>) =>
    apiClient.post('/v1/white-label/payment-methods/', data),
  setDefaultPaymentMethod: (id: string) =>
    apiClient.post(`/v1/white-label/payment-methods/${id}/set-default/`),
  deletePaymentMethod: (id: string) =>
    apiClient.delete(`/v1/white-label/payment-methods/${id}/`),

  // Usage
  getUsage: (params?: { period?: string }) =>
    apiClient.get('/v1/white-label/usage/', { params }),

  // Branding (for white-label partners)
  getBranding: () =>
    apiClient.get('/v1/white-label/branding/'),
  updateBranding: (data: FormData) =>
    apiClient.patch('/v1/white-label/branding/', data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
};

// ==================== Customer Success API ====================
export const customerSuccessAPI = {
  // Customer Accounts
  getAccounts: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/customer-success/accounts/', { params }),
  getAccount: (id: string) =>
    apiClient.get(`/v1/customer-success/accounts/${id}/`),
  createAccount: (data: Record<string, unknown>) =>
    apiClient.post('/v1/customer-success/accounts/', data),
  updateAccount: (id: string, data: Record<string, unknown>) =>
    apiClient.patch(`/v1/customer-success/accounts/${id}/`, data),

  // Health Scores
  getHealthScores: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/customer-success/health-scores/', { params }),
  getAccountHealth: (accountId: string) =>
    apiClient.get(`/v1/customer-success/accounts/${accountId}/health/`),
  recalculateHealth: (accountId: string) =>
    apiClient.post(`/v1/customer-success/accounts/${accountId}/recalculate-health/`),
  getHealthTrends: (accountId: string, params?: { period?: string }) =>
    apiClient.get(`/v1/customer-success/accounts/${accountId}/health-trends/`, { params }),

  // Health Score Config
  getHealthConfig: () =>
    apiClient.get('/v1/customer-success/health-config/'),
  updateHealthConfig: (data: Record<string, unknown>) =>
    apiClient.patch('/v1/customer-success/health-config/', data),

  // Customer Journey
  getJourney: (accountId: string) =>
    apiClient.get(`/v1/customer-success/accounts/${accountId}/journey/`),
  getMilestones: (accountId: string) =>
    apiClient.get(`/v1/customer-success/accounts/${accountId}/milestones/`),
  completeMilestone: (accountId: string, milestoneId: string) =>
    apiClient.post(`/v1/customer-success/accounts/${accountId}/milestones/${milestoneId}/complete/`),

  // Churn Risk
  getChurnRisks: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/customer-success/churn-risks/', { params }),
  getAccountChurnRisk: (accountId: string) =>
    apiClient.get(`/v1/customer-success/accounts/${accountId}/churn-risk/`),
  predictChurn: (accountId: string) =>
    apiClient.post(`/v1/customer-success/accounts/${accountId}/predict-churn/`),

  // Expansion Opportunities
  getExpansionOpportunities: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/customer-success/expansion-opportunities/', { params }),
  getAccountExpansions: (accountId: string) =>
    apiClient.get(`/v1/customer-success/accounts/${accountId}/expansions/`),
  createExpansionOpportunity: (data: Record<string, unknown>) =>
    apiClient.post('/v1/customer-success/expansion-opportunities/', data),

  // Playbooks
  getPlaybooks: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/customer-success/playbooks/', { params }),
  getPlaybook: (id: string) =>
    apiClient.get(`/v1/customer-success/playbooks/${id}/`),
  createPlaybook: (data: Record<string, unknown>) =>
    apiClient.post('/v1/customer-success/playbooks/', data),
  executePlaybook: (playbookId: string, accountId: string) =>
    apiClient.post(`/v1/customer-success/playbooks/${playbookId}/execute/`, { account_id: accountId }),

  // Customer Notes
  getNotes: (accountId: string, params?: Record<string, unknown>) =>
    apiClient.get(`/v1/customer-success/accounts/${accountId}/notes/`, { params }),
  createNote: (accountId: string, data: { content: string; note_type?: string }) =>
    apiClient.post(`/v1/customer-success/accounts/${accountId}/notes/`, data),

  // NPS Surveys
  getSurveys: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/customer-success/nps-surveys/', { params }),
  sendSurvey: (accountId: string) =>
    apiClient.post(`/v1/customer-success/accounts/${accountId}/send-nps/`),
  getNPSAnalytics: (params?: { period?: string }) =>
    apiClient.get('/v1/customer-success/nps-analytics/', { params }),

  // Renewals
  getRenewals: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/customer-success/renewals/', { params }),
  getUpcomingRenewals: (days?: number) =>
    apiClient.get('/v1/customer-success/renewals/upcoming/', { params: { days } }),

  // Analytics Dashboard
  getDashboard: (params?: { period?: string }) =>
    apiClient.get('/v1/customer-success/dashboard/', { params }),
  getMetrics: (params?: { period?: string }) =>
    apiClient.get('/v1/customer-success/metrics/', { params }),
};

// Export all APIs
const api = {
  revenueIntelligence: revenueIntelligenceAPI,
  emailTracking: emailTrackingAPI,
  smartScheduling: smartSchedulingAPI,
  aiSalesAssistant: aiSalesAssistantAPI,
  socialSelling: socialSellingAPI,
  documentEsign: documentEsignAPI,
  conversationIntelligence: conversationIntelligenceAPI,
  whiteLabel: whiteLabelAPI,
  customerSuccess: customerSuccessAPI,
};

export default api;

