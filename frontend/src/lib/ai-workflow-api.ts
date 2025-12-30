/**
 * AI Workflow Automation API - Email Sequence Automation, Predictive Lead Routing,
 * Smart Scheduling AI, Data Enrichment, and Voice Intelligence
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

// ==================== Email Sequence Automation API ====================
export const emailSequenceAPI = {
  // Sequences
  getSequences: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/email-sequences/sequences/', { params }),
  getSequence: (id: string) =>
    apiClient.get(`/v1/email-sequences/sequences/${id}/`),
  createSequence: (data: Record<string, unknown>) =>
    apiClient.post('/v1/email-sequences/sequences/', data),
  updateSequence: (id: string, data: Record<string, unknown>) =>
    apiClient.patch(`/v1/email-sequences/sequences/${id}/`, data),
  deleteSequence: (id: string) =>
    apiClient.delete(`/v1/email-sequences/sequences/${id}/`),
  activateSequence: (id: string) =>
    apiClient.post(`/v1/email-sequences/sequences/${id}/activate/`),
  pauseSequence: (id: string) =>
    apiClient.post(`/v1/email-sequences/sequences/${id}/pause/`),
  cloneSequence: (id: string) =>
    apiClient.post(`/v1/email-sequences/sequences/${id}/clone/`),
  getSequenceAnalytics: (id: string) =>
    apiClient.get(`/v1/email-sequences/sequences/${id}/analytics/`),

  // Sequence Steps
  getSteps: (sequenceId: string) =>
    apiClient.get(`/v1/email-sequences/sequences/${sequenceId}/steps/`),
  createStep: (sequenceId: string, data: Record<string, unknown>) =>
    apiClient.post(`/v1/email-sequences/sequences/${sequenceId}/steps/`, data),
  updateStep: (sequenceId: string, stepId: string, data: Record<string, unknown>) =>
    apiClient.patch(`/v1/email-sequences/sequences/${sequenceId}/steps/${stepId}/`, data),
  deleteStep: (sequenceId: string, stepId: string) =>
    apiClient.delete(`/v1/email-sequences/sequences/${sequenceId}/steps/${stepId}/`),
  reorderSteps: (sequenceId: string, data: { step_ids: string[] }) =>
    apiClient.post(`/v1/email-sequences/sequences/${sequenceId}/reorder_steps/`, data),

  // Enrollments
  getEnrollments: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/email-sequences/enrollments/', { params }),
  enrollContact: (data: { sequence_id: string; contact_id?: string; lead_id?: string }) =>
    apiClient.post('/v1/email-sequences/enrollments/', data),
  bulkEnroll: (data: { sequence_id: string; contact_ids?: string[]; lead_ids?: string[] }) =>
    apiClient.post('/v1/email-sequences/enrollments/bulk_enroll/', data),
  unenroll: (enrollmentId: string) =>
    apiClient.post(`/v1/email-sequences/enrollments/${enrollmentId}/unenroll/`),
  pauseEnrollment: (enrollmentId: string) =>
    apiClient.post(`/v1/email-sequences/enrollments/${enrollmentId}/pause/`),
  resumeEnrollment: (enrollmentId: string) =>
    apiClient.post(`/v1/email-sequences/enrollments/${enrollmentId}/resume/`),

  // A/B Tests
  getABTests: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/email-sequences/ab-tests/', { params }),
  createABTest: (data: Record<string, unknown>) =>
    apiClient.post('/v1/email-sequences/ab-tests/', data),
  getABTestResults: (id: string) =>
    apiClient.get(`/v1/email-sequences/ab-tests/${id}/results/`),
  selectWinner: (id: string, data: { variant: 'A' | 'B' }) =>
    apiClient.post(`/v1/email-sequences/ab-tests/${id}/select_winner/`, data),

  // Automated Triggers
  getTriggers: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/email-sequences/triggers/', { params }),
  createTrigger: (data: Record<string, unknown>) =>
    apiClient.post('/v1/email-sequences/triggers/', data),
  updateTrigger: (id: string, data: Record<string, unknown>) =>
    apiClient.patch(`/v1/email-sequences/triggers/${id}/`, data),
  deleteTrigger: (id: string) =>
    apiClient.delete(`/v1/email-sequences/triggers/${id}/`),

  // AI Content
  generateContent: (data: { step_id: string; context?: Record<string, unknown> }) =>
    apiClient.post('/v1/email-sequences/generate-content/', data),
  previewPersonalization: (data: { template: string; contact_id?: string; lead_id?: string }) =>
    apiClient.post('/v1/email-sequences/preview-personalization/', data),
};

// ==================== Predictive Lead Routing API ====================
export const leadRoutingAPI = {
  // Sales Rep Profiles
  getRepProfiles: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/lead-routing/rep-profiles/', { params }),
  getRepProfile: (id: string) =>
    apiClient.get(`/v1/lead-routing/rep-profiles/${id}/`),
  createRepProfile: (data: Record<string, unknown>) =>
    apiClient.post('/v1/lead-routing/rep-profiles/', data),
  updateRepProfile: (id: string, data: Record<string, unknown>) =>
    apiClient.patch(`/v1/lead-routing/rep-profiles/${id}/`, data),
  getRepPerformance: (id: string) =>
    apiClient.get(`/v1/lead-routing/rep-profiles/${id}/performance/`),
  updateAvailability: (id: string, data: { is_available: boolean }) =>
    apiClient.post(`/v1/lead-routing/rep-profiles/${id}/update_availability/`, data),

  // Routing Rules
  getRoutingRules: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/lead-routing/rules/', { params }),
  getRoutingRule: (id: string) =>
    apiClient.get(`/v1/lead-routing/rules/${id}/`),
  createRoutingRule: (data: Record<string, unknown>) =>
    apiClient.post('/v1/lead-routing/rules/', data),
  updateRoutingRule: (id: string, data: Record<string, unknown>) =>
    apiClient.patch(`/v1/lead-routing/rules/${id}/`, data),
  deleteRoutingRule: (id: string) =>
    apiClient.delete(`/v1/lead-routing/rules/${id}/`),
  testRule: (id: string, data: { lead_id: string }) =>
    apiClient.post(`/v1/lead-routing/rules/${id}/test/`, data),
  reorderRules: (data: { rule_ids: string[] }) =>
    apiClient.post('/v1/lead-routing/rules/reorder/', data),

  // Lead Assignments
  getAssignments: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/lead-routing/assignments/', { params }),
  getAssignment: (id: string) =>
    apiClient.get(`/v1/lead-routing/assignments/${id}/`),
  routeLead: (data: { lead_id: string }) =>
    apiClient.post('/v1/lead-routing/assignments/route_lead/', data),
  reassignLead: (id: string, data: { new_rep_id: string; reason?: string }) =>
    apiClient.post(`/v1/lead-routing/assignments/${id}/reassign/`, data),
  acceptAssignment: (id: string) =>
    apiClient.post(`/v1/lead-routing/assignments/${id}/accept/`),
  rejectAssignment: (id: string, data: { reason: string }) =>
    apiClient.post(`/v1/lead-routing/assignments/${id}/reject/`, data),

  // Escalation Rules
  getEscalationRules: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/lead-routing/escalations/', { params }),
  createEscalationRule: (data: Record<string, unknown>) =>
    apiClient.post('/v1/lead-routing/escalations/', data),
  updateEscalationRule: (id: string, data: Record<string, unknown>) =>
    apiClient.patch(`/v1/lead-routing/escalations/${id}/`, data),

  // Analytics
  getRoutingAnalytics: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/lead-routing/analytics/', { params }),
  getRoutingDashboard: () =>
    apiClient.get('/v1/lead-routing/dashboard/'),
};

// ==================== Smart Scheduling AI API ====================
export const schedulingAIAPI = {
  // AI Preferences
  getAIPreferences: () =>
    apiClient.get('/v1/scheduling/ai/preferences/'),
  getPreferences: () =>
    apiClient.get('/v1/scheduling/ai/preferences/'),
  updatePreferences: (data: Record<string, unknown>) =>
    apiClient.patch('/v1/scheduling/ai/preferences/', data),

  // Optimal Time Finder
  findOptimalSlots: (duration: number, date: string) =>
    apiClient.get('/v1/scheduling/ai/find-optimal-slots/', { params: { duration, date } }),
  findOptimalTimes: (data: {
    contact_id?: string;
    lead_id?: string;
    meeting_type?: string;
    duration_minutes?: number;
    date_range_days?: number;
  }) => apiClient.post('/v1/scheduling/ai/find-optimal-times/', data),

  // Meeting Prep
  getMeetingPreps: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/scheduling/ai/meeting-prep/', { params }),
  getMeetingPrep: (meetingId: string) =>
    apiClient.get(`/v1/scheduling/ai/meeting-prep/${meetingId}/`),
  generateMeetingPrep: (meetingId: number) =>
    apiClient.post(`/v1/scheduling/ai/meeting-prep/${meetingId}/generate/`),
  regenerateMeetingPrep: (meetingId: string) =>
    apiClient.post(`/v1/scheduling/ai/meeting-prep/${meetingId}/regenerate/`),

  // No-Show Predictions
  getNoShowPredictions: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/scheduling/ai/no-show-predictions/', { params }),
  predictNoShow: (meetingId: string) =>
    apiClient.post(`/v1/scheduling/ai/no-show-predictions/predict/${meetingId}/`),

  // Smart Reminders
  getSmartReminders: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/scheduling/ai/smart-reminders/', { params }),
  sendReminder: (reminderId: string) =>
    apiClient.post(`/v1/scheduling/ai/smart-reminders/${reminderId}/send/`),

  // Meeting Insights
  getMeetingInsights: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/scheduling/ai/insights/', { params }),
  getMeetingInsight: (id: string) =>
    apiClient.get(`/v1/scheduling/ai/insights/${id}/`),
  generateInsights: (meetingId: string, data: { notes?: string }) =>
    apiClient.post(`/v1/scheduling/ai/insights/generate/${meetingId}/`, data),

  // Meeting Follow-Ups
  getFollowUps: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/scheduling/ai/follow-ups/', { params }),
  generateFollowUp: (meetingId: string) =>
    apiClient.post(`/v1/scheduling/ai/follow-ups/generate/${meetingId}/`),
  sendFollowUp: (followUpId: string) =>
    apiClient.post(`/v1/scheduling/ai/follow-ups/${followUpId}/send/`),

  // Schedule Optimization
  getOptimizations: () =>
    apiClient.get('/v1/scheduling/ai/optimizations/'),
  applyOptimization: (id: string) =>
    apiClient.post(`/v1/scheduling/ai/optimizations/${id}/apply/`),

  // Booking Suggestions
  getBookingSuggestions: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/scheduling/ai/booking-suggestions/', { params }),
};

// ==================== Data Enrichment API ====================
export const dataEnrichmentAPI = {
  // Providers
  getProviders: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/data-enrichment/providers/', { params }),
  getProvider: (id: string) =>
    apiClient.get(`/v1/data-enrichment/providers/${id}/`),
  configureProvider: (id: string, data: Record<string, unknown>) =>
    apiClient.patch(`/v1/data-enrichment/providers/${id}/`, data),
  testProvider: (id: string) =>
    apiClient.post(`/v1/data-enrichment/providers/${id}/test/`),

  // Enrichment Profiles
  getProfiles: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/data-enrichment/profiles/', { params }),
  getEnrichmentProfiles: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/data-enrichment/profiles/', { params }),
  getEnrichmentProfile: (id: string) =>
    apiClient.get(`/v1/data-enrichment/profiles/${id}/`),
  createProfile: (data: Record<string, unknown>) =>
    apiClient.post('/v1/data-enrichment/profiles/', data),
  updateProfile: (id: string, data: Record<string, unknown>) =>
    apiClient.patch(`/v1/data-enrichment/profiles/${id}/`, data),
  deleteProfile: (id: string) =>
    apiClient.delete(`/v1/data-enrichment/profiles/${id}/`),
  triggerEnrichment: (profileId: number, recordType: string, recordIds: number[]) =>
    apiClient.post(`/v1/data-enrichment/profiles/${profileId}/trigger/`, { record_type: recordType, record_ids: recordIds }),
  enrichContact: (contactId: string) =>
    apiClient.post(`/v1/data-enrichment/profiles/enrich-contact/${contactId}/`),
  enrichLead: (leadId: string) =>
    apiClient.post(`/v1/data-enrichment/profiles/enrich-lead/${leadId}/`),
  bulkEnrich: (data: { contact_ids?: string[]; lead_ids?: string[] }) =>
    apiClient.post('/v1/data-enrichment/profiles/bulk-enrich/', data),
  refreshEnrichment: (id: string) =>
    apiClient.post(`/v1/data-enrichment/profiles/${id}/refresh/`),

  // Enrichment Jobs
  getJobs: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/data-enrichment/jobs/', { params }),
  getEnrichmentJobs: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/data-enrichment/jobs/', { params }),
  getEnrichmentJob: (id: string) =>
    apiClient.get(`/v1/data-enrichment/jobs/${id}/`),
  createEnrichmentJob: (data: Record<string, unknown>) =>
    apiClient.post('/v1/data-enrichment/jobs/', data),
  cancelJob: (id: string) =>
    apiClient.post(`/v1/data-enrichment/jobs/${id}/cancel/`),

  // Company Enrichment
  getCompanyEnrichments: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/data-enrichment/companies/', { params }),
  getCompanyEnrichment: (id: string) =>
    apiClient.get(`/v1/data-enrichment/companies/${id}/`),
  enrichCompany: (data: { domain?: string; company_name?: string }) =>
    apiClient.post('/v1/data-enrichment/companies/enrich/', data),

  // Technographics
  getTechnographics: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/data-enrichment/technographics/', { params }),
  getTechnographic: (id: string) =>
    apiClient.get(`/v1/data-enrichment/technographics/${id}/`),

  // Intent Signals
  getIntentSignals: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/data-enrichment/intent-signals/', { params }),
  getIntentSignal: (id: string) =>
    apiClient.get(`/v1/data-enrichment/intent-signals/${id}/`),
  markSignalActioned: (id: string) =>
    apiClient.post(`/v1/data-enrichment/intent-signals/${id}/mark-actioned/`),

  // News Alerts
  getNewsAlerts: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/data-enrichment/news/', { params }),
  dismissAlert: (id: string) =>
    apiClient.post(`/v1/data-enrichment/news/${id}/dismiss/`),

  // Social Profiles
  getSocialProfiles: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/data-enrichment/social/', { params }),

  // Data Quality
  getDataQualityScores: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/data-enrichment/quality-scores/', { params }),
  getDataQualityScore: (id: string) =>
    apiClient.get(`/v1/data-enrichment/quality-scores/${id}/`),
  calculateQualityScore: (data: { contact_id?: string; lead_id?: string }) =>
    apiClient.post('/v1/data-enrichment/quality-scores/calculate/', data),

  // Dashboard & Analytics
  getDashboard: () =>
    apiClient.get('/v1/data-enrichment/dashboard/'),
  getAnalytics: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/data-enrichment/analytics/', { params }),
};

// ==================== Voice Intelligence API ====================
export const voiceIntelligenceAPI = {
  // Recordings
  getRecordings: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/voice-intelligence/recordings/', { params }),
  getRecording: (id: string) =>
    apiClient.get(`/v1/voice-intelligence/recordings/${id}/`),
  uploadRecording: (formData: FormData) =>
    apiClient.post('/v1/voice-intelligence/recordings/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  deleteRecording: (id: string) =>
    apiClient.delete(`/v1/voice-intelligence/recordings/${id}/`),
  processRecording: (id: string, options?: Record<string, boolean>) =>
    apiClient.post(`/v1/voice-intelligence/recordings/${id}/process/`, options),
  transcribeRecording: (id: string) =>
    apiClient.post(`/v1/voice-intelligence/recordings/${id}/transcribe/`),
  analyzeRecording: (id: string) =>
    apiClient.post(`/v1/voice-intelligence/recordings/${id}/analyze/`),

  // Transcription
  getTranscription: (recordingId: string) =>
    apiClient.get(`/v1/voice-intelligence/recordings/${recordingId}/transcription/`),
  editTranscription: (recordingId: string, data: { full_text: string; segments?: Record<string, unknown>[] }) =>
    apiClient.patch(`/v1/voice-intelligence/recordings/${recordingId}/edit_transcription/`, data),

  // Summaries
  getSummaries: (recordingId: string) =>
    apiClient.get(`/v1/voice-intelligence/recordings/${recordingId}/summaries/`),
  generateSummary: (recordingId: string, data: { summary_type: string }) =>
    apiClient.post(`/v1/voice-intelligence/recordings/${recordingId}/generate_summary/`, data),

  // Action Items
  getActionItems: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/voice-intelligence/action-items/', { params }),
  getRecordingActionItems: (recordingId: string) =>
    apiClient.get(`/v1/voice-intelligence/recordings/${recordingId}/action_items/`),
  updateActionItem: (id: string, data: Record<string, unknown>) =>
    apiClient.patch(`/v1/voice-intelligence/action-items/${id}/`, data),
  confirmActionItem: (id: string) =>
    apiClient.post(`/v1/voice-intelligence/action-items/${id}/confirm/`),
  createTaskFromActionItem: (id: string) =>
    apiClient.post(`/v1/voice-intelligence/action-items/${id}/create_task/`),
  bulkUpdateActionItems: (data: {
    action_item_ids: string[];
    status?: string;
    priority?: string;
    assigned_to?: string;
  }) => apiClient.post('/v1/voice-intelligence/action-items/bulk_update/', data),

  // Key Moments
  getKeyMoments: (recordingId: string) =>
    apiClient.get(`/v1/voice-intelligence/recordings/${recordingId}/key_moments/`),
  addKeyMoment: (recordingId: string, data: Record<string, unknown>) =>
    apiClient.post(`/v1/voice-intelligence/recordings/${recordingId}/add_key_moment/`, data),

  // Call Scores
  getCallScore: (recordingId: string) =>
    apiClient.get(`/v1/voice-intelligence/recordings/${recordingId}/call_score/`),

  // Voice Notes
  getVoiceNotes: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/voice-intelligence/voice-notes/', { params }),
  getVoiceNote: (id: string) =>
    apiClient.get(`/v1/voice-intelligence/voice-notes/${id}/`),
  createVoiceNote: (formData: FormData) =>
    apiClient.post('/v1/voice-intelligence/voice-notes/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  deleteVoiceNote: (id: string) =>
    apiClient.delete(`/v1/voice-intelligence/voice-notes/${id}/`),
  getVoiceNotesForContact: (contactId: string) =>
    apiClient.get('/v1/voice-intelligence/voice-notes/for_contact/', { params: { contact_id: contactId } }),
  getVoiceNotesForLead: (leadId: string) =>
    apiClient.get('/v1/voice-intelligence/voice-notes/for_lead/', { params: { lead_id: leadId } }),

  // Categories
  getCategories: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/voice-intelligence/categories/', { params }),
  createCategory: (data: Record<string, unknown>) =>
    apiClient.post('/v1/voice-intelligence/categories/', data),
  getCategoryTree: () =>
    apiClient.get('/v1/voice-intelligence/categories/tree/'),
  categorizeRecording: (recordingId: string, data: { category_ids: string[] }) =>
    apiClient.post(`/v1/voice-intelligence/recordings/${recordingId}/categorize/`, data),

  // Settings
  getSettings: () =>
    apiClient.get('/v1/voice-intelligence/settings/'),
  updateSettings: (data: Record<string, unknown>) =>
    apiClient.patch('/v1/voice-intelligence/settings/', data),

  // Search & Analytics
  searchRecordings: (params: Record<string, unknown>) =>
    apiClient.get('/v1/voice-intelligence/recordings/search/', { params }),
  getAnalytics: (params?: Record<string, unknown>) =>
    apiClient.get('/v1/voice-intelligence/recordings/analytics/', { params }),
};

// Alias for backward compatibility
export const smartSchedulingAIAPI = schedulingAIAPI;

const api = {
  emailSequence: emailSequenceAPI,
  leadRouting: leadRoutingAPI,
  schedulingAI: schedulingAIAPI,
  smartSchedulingAI: schedulingAIAPI,
  dataEnrichment: dataEnrichmentAPI,
  voiceIntelligence: voiceIntelligenceAPI,
};

export default api;
