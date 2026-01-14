import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
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
  (error) => {
    return Promise.reject(error);
  }
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

          // Retry original request
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError: unknown) {
        // Refresh failed - log error and redirect to login
        const errorMessage = refreshError instanceof Error ? refreshError.message : 'Token refresh failed';
        console.error('Token refresh error:', errorMessage);

        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (credentials: { username: string; password: string }) => {
    const response = await apiClient.post('/auth/login/', credentials);
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/users/me/');
    return response.data;
  },

  changePassword: async (passwordData: {
    old_password: string;
    new_password: string;
    new_password_confirm: string;
  }) => {
    const response = await apiClient.post('/auth/users/change_password/', passwordData);
    return response.data;
  },

  setup2FA: async () => {
    const response = await apiClient.post('/auth/users/setup_2fa/');
    return response.data;
  },

  verify2FA: async (token: string) => {
    const response = await apiClient.post('/auth/users/verify_2fa/', { token });
    return response.data;
  },

  disable2FA: async () => {
    const response = await apiClient.post('/auth/users/disable_2fa/');
    return response.data;
  },
};

// Contacts API
export const contactsAPI = {
  getContacts: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get('/contacts/contacts/', { params });
    return response.data;
  },

  getContact: async (id: number) => {
    const response = await apiClient.get(`/contacts/contacts/${id}/`);
    return response.data;
  },

  createContact: async (contactData: Record<string, unknown>) => {
    const response = await apiClient.post('/contacts/contacts/', contactData);
    return response.data;
  },

  updateContact: async (id: number, contactData: Record<string, unknown>) => {
    const response = await apiClient.patch(`/contacts/contacts/${id}/`, contactData);
    return response.data;
  },

  deleteContact: async (id: number) => {
    const response = await apiClient.delete(`/contacts/contacts/${id}/`);
    return response.data;
  },

  bulkUpdate: async (contactIds: number[], updates: Record<string, unknown>) => {
    const response = await apiClient.post('/contacts/contacts/bulk_update/', {
      contact_ids: contactIds,
      updates,
    });
    return response.data;
  },

  bulkDelete: async (contactIds: number[]) => {
    const response = await apiClient.post('/contacts/contacts/bulk_delete/', {
      contact_ids: contactIds,
    });
    return response.data;
  },

  exportContacts: async (format: string, options?: Record<string, unknown>) => {
    const response = await apiClient.post('/contacts/contacts/export/', {
      format,
      ...options,
    });
    return response.data;
  },
};

// Leads API
export const leadsAPI = {
  getLeads: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get('/leads/leads/', { params });
    return response.data;
  },

  getLead: async (id: number) => {
    const response = await apiClient.get(`/leads/leads/${id}/`);
    return response.data;
  },

  createLead: async (leadData: Record<string, unknown>) => {
    const response = await apiClient.post('/leads/leads/', leadData);
    return response.data;
  },

  updateLead: async (id: number, leadData: Record<string, unknown>) => {
    const response = await apiClient.patch(`/leads/leads/${id}/`, leadData);
    return response.data;
  },

  deleteLead: async (id: number) => {
    const response = await apiClient.delete(`/leads/leads/${id}/`);
    return response.data;
  },

  convertLead: async (id: number, opportunityData?: Record<string, unknown>) => {
    const response = await apiClient.post(`/leads/leads/${id}/convert/`, opportunityData);
    return response.data;
  },
};

// Opportunities API
export const opportunitiesAPI = {
  getOpportunities: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get('/opportunities/opportunities/', { params });
    return response.data;
  },

  getOpportunity: async (id: number) => {
    const response = await apiClient.get(`/opportunities/opportunities/${id}/`);
    return response.data;
  },

  createOpportunity: async (opportunityData: Record<string, unknown>) => {
    const response = await apiClient.post('/opportunities/opportunities/', opportunityData);
    return response.data;
  },

  updateOpportunity: async (id: number, opportunityData: Record<string, unknown>) => {
    const response = await apiClient.patch(`/opportunities/opportunities/${id}/`, opportunityData);
    return response.data;
  },

  deleteOpportunity: async (id: number) => {
    const response = await apiClient.delete(`/opportunities/opportunities/${id}/`);
    return response.data;
  },

  updateStage: async (id: number, stage: string) => {
    const response = await apiClient.patch(`/opportunities/opportunities/${id}/`, { stage });
    return response.data;
  },
};

// Tasks API
export const tasksAPI = {
  getTasks: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get('/tasks/tasks/', { params });
    return response.data;
  },

  getTask: async (id: number) => {
    const response = await apiClient.get(`/tasks/tasks/${id}/`);
    return response.data;
  },

  createTask: async (taskData: Record<string, unknown>) => {
    const response = await apiClient.post('/tasks/tasks/', taskData);
    return response.data;
  },

  updateTask: async (id: number, taskData: Record<string, unknown>) => {
    const response = await apiClient.patch(`/tasks/tasks/${id}/`, taskData);
    return response.data;
  },

  deleteTask: async (id: number) => {
    const response = await apiClient.delete(`/tasks/tasks/${id}/`);
    return response.data;
  },

  completeTask: async (id: number) => {
    const response = await apiClient.patch(`/tasks/tasks/${id}/`, {
      status: 'completed',
      completed_at: new Date().toISOString()
    });
    return response.data;
  },
};

// Communications API
export const communicationsAPI = {
  getCommunications: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get('/communications/communications/', { params });
    return response.data;
  },

  getCommunication: async (id: number) => {
    const response = await apiClient.get(`/communications/communications/${id}/`);
    return response.data;
  },

  createCommunication: async (communicationData: Record<string, unknown>) => {
    const response = await apiClient.post('/communications/communications/', communicationData);
    return response.data;
  },

  updateCommunication: async (id: number, communicationData: Record<string, unknown>) => {
    const response = await apiClient.patch(`/communications/communications/${id}/`, communicationData);
    return response.data;
  },

  deleteCommunication: async (id: number) => {
    const response = await apiClient.delete(`/communications/communications/${id}/`);
    return response.data;
  },
};

// Dashboard API - for main CRM dashboard metrics
export const dashboardAPI = {
  getMetrics: async () => {
    const response = await apiClient.get('/reports/analytics/dashboard_metrics/');
    return response.data;
  },

  getSalesPipeline: async () => {
    const response = await apiClient.get('/reports/analytics/sales_pipeline/');
    return response.data;
  },

  getRecentActivities: async (limit: number = 10) => {
    const response = await apiClient.get('/activity-feed/', { params: { limit } });
    return response.data;
  },

  getRecentOpportunities: async (status?: string, limit: number = 5) => {
    const response = await apiClient.get('/opportunities/opportunities/', {
      params: { status, page_size: limit, ordering: '-created_at' }
    });
    return response.data;
  },

  getUpcomingTasks: async (limit: number = 5) => {
    const response = await apiClient.get('/tasks/tasks/', {
      params: {
        status__in: 'pending,in_progress',
        ordering: 'due_date',
        page_size: limit
      }
    });
    return response.data;
  },

  // Get aggregated dashboard analytics data
  getDashboardAnalytics: async () => {
    const response = await apiClient.get('/v1/analytics/dashboard/');
    return response.data;
  },
};

// Reports API
export const reportsAPI = {
  getDashboard: async () => {
    const response = await apiClient.get('/reports/dashboard/');
    return response.data;
  },

  getKPIs: async () => {
    const response = await apiClient.get('/reports/kpis/');
    return response.data;
  },

  getAnalytics: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get('/reports/analytics/', { params });
    return response.data;
  },

  createReport: async (reportData: Record<string, unknown>) => {
    const response = await apiClient.post('/reports/reports/', reportData);
    return response.data;
  },

  getReports: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get('/reports/reports/', { params });
    return response.data;
  },

  exportReport: async (id: number, format: string) => {
    const response = await apiClient.get(`/reports/reports/${id}/export/?format=${format}`);
    return response.data;
  },
};

// Meetings API
export const meetingsAPI = {
  list: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get('/meetings/meetings/', { params });
    return response.data;
  },

  get: async (id: string) => {
    const response = await apiClient.get(`/meetings/meetings/${id}/`);
    return response.data;
  },

  create: async (meetingData: Record<string, unknown> | FormData) => {
    // Support both JSON payloads and FormData uploads (e.g., attachments).
    if (typeof FormData !== 'undefined' && meetingData instanceof FormData) {
      const response = await apiClient.post('/meetings/meetings/', meetingData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data;
    }

    const response = await apiClient.post('/meetings/meetings/', meetingData as Record<string, unknown>);
    return response.data;
  },

  update: async (id: string, meetingData: Record<string, unknown>) => {
    const response = await apiClient.patch(`/meetings/meetings/${id}/`, meetingData);
    return response.data;
  },

  delete: async (id: string) => {
    const response = await apiClient.delete(`/meetings/meetings/${id}/`);
    return response.data;
  },

  getStats: async () => {
    const response = await apiClient.get('/meetings/meetings/stats/');
    return response.data;
  },

  getAnalytics: async (days?: number) => {
    const response = await apiClient.get('/meetings/meetings/analytics/', { params: { days } });
    return response.data;
  },

  share: async (id: string) => {
    const response = await apiClient.post(`/meetings/meetings/${id}/share/`);
    return response.data;
  },

  toggleFavorite: async (id: string) => {
    const response = await apiClient.post(`/meetings/meetings/${id}/toggle_favorite/`);
    return response.data;
  },

  getFavorites: async () => {
    const response = await apiClient.get('/meetings/meetings/favorites/');
    return response.data;
  },
};

// Action Items API
export const actionItemsAPI = {
  list: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get('/action-items/action-items/', { params });
    return response.data;
  },

  get: async (id: string) => {
    const response = await apiClient.get(`/action-items/action-items/${id}/`);
    return response.data;
  },

  create: async (actionItemData: Record<string, unknown>) => {
    const response = await apiClient.post('/action-items/action-items/', actionItemData);
    return response.data;
  },

  update: async (id: string, actionItemData: Record<string, unknown>) => {
    const response = await apiClient.patch(`/action-items/action-items/${id}/`, actionItemData);
    return response.data;
  },

  delete: async (id: string) => {
    const response = await apiClient.delete(`/action-items/action-items/${id}/`);
    return response.data;
  },

  complete: async (id: string) => {
    const response = await apiClient.patch(`/action-items/action-items/${id}/`, { status: 'completed' });
    return response.data;
  },
};

// Notes API
export const notesAPI = {
  list: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get('/notes/notes/', { params });
    return response.data;
  },

  get: async (id: string) => {
    const response = await apiClient.get(`/notes/notes/${id}/`);
    return response.data;
  },

  create: async (noteData: Record<string, unknown>) => {
    const response = await apiClient.post('/notes/notes/', noteData);
    return response.data;
  },

  update: async (id: string, noteData: Record<string, unknown>) => {
    const response = await apiClient.patch(`/notes/notes/${id}/`, noteData);
    return response.data;
  },

  delete: async (id: string) => {
    const response = await apiClient.delete(`/notes/notes/${id}/`);
    return response.data;
  },
};

// Tags API
export const tagsAPI = {
  list: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get('/tags/tags/', { params });
    return response.data;
  },

  get: async (id: string) => {
    const response = await apiClient.get(`/tags/tags/${id}/`);
    return response.data;
  },

  create: async (tagData: Record<string, unknown>) => {
    const response = await apiClient.post('/tags/tags/', tagData);
    return response.data;
  },

  update: async (id: string, tagData: Record<string, unknown>) => {
    const response = await apiClient.patch(`/tags/tags/${id}/`, tagData);
    return response.data;
  },

  delete: async (id: string) => {
    const response = await apiClient.delete(`/tags/tags/${id}/`);
    return response.data;
  },
};

// Types
export type Meeting = {
  id: string;
  title: string;
  description?: string;
  date: string;
  attendees: string[];
  status: string;
};

export type ActionItem = {
  id: string;
  title: string;
  description?: string;
  assigned_to?: string;
  due_date?: string;
  status: string;
  meeting_id?: string;
};

export type Tag = {
  id: string;
  name: string;
  color: string;
};

// ==================== New Features API ====================

// Campaign Management API
export const campaignAPI = {
  // Campaigns
  getCampaigns: () => apiClient.get('/campaigns/campaigns/'),
  getCampaign: (id: string) => apiClient.get(`/campaigns/campaigns/${id}/`),
  createCampaign: (data: Record<string, unknown>) => apiClient.post('/campaigns/campaigns/', data),
  updateCampaign: (id: string, data: Record<string, unknown>) => apiClient.put(`/campaigns/campaigns/${id}/`, data),
  deleteCampaign: (id: string) => apiClient.delete(`/campaigns/campaigns/${id}/`),
  scheduleCampaign: (id: string, scheduledAt: string) =>
    apiClient.post(`/campaigns/campaigns/${id}/schedule/`, { scheduled_at: scheduledAt }),
  sendCampaignNow: (id: string) => apiClient.post(`/campaigns/campaigns/${id}/send_now/`),
  getCampaignAnalytics: (id: string) => apiClient.get(`/campaigns/campaigns/${id}/analytics/`),
  getCampaignStatistics: () => apiClient.get('/campaigns/campaigns/statistics/'),

  // Segments
  getSegments: () => apiClient.get('/campaigns/segments/'),
  createSegment: (data: Record<string, unknown>) => apiClient.post('/campaigns/segments/', data),
  previewSegment: (id: string) => apiClient.get(`/campaigns/segments/${id}/preview/`),

  // Templates
  getTemplates: () => apiClient.get('/campaigns/templates/'),
  createTemplate: (data: Record<string, unknown>) => apiClient.post('/campaigns/templates/', data),
  duplicateTemplate: (id: string) => apiClient.post(`/campaigns/templates/${id}/duplicate/`),
};

// Pipeline Analytics API
export const analyticsAPI = {
  getPipelineAnalytics: () => apiClient.get('/core/analytics/pipeline_analytics/'),
  getSalesForecast: (months: number = 3) =>
    apiClient.get(`/core/analytics/sales_forecast/?months=${months}`),
  getAIInsights: () => apiClient.get('/core/analytics/ai_insights_dashboard/'),
};

// Document Management API
export const documentAPI = {
  // Documents
  getDocuments: (params?: Record<string, unknown>) => apiClient.get('/documents/documents/', { params }),
  getDocument: (id: string) => apiClient.get(`/documents/documents/${id}/`),
  uploadDocument: (formData: FormData) =>
    apiClient.post('/documents/documents/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  downloadDocument: (id: string) =>
    apiClient.get(`/documents/documents/${id}/download/`, { responseType: 'blob' }),
  createDocumentVersion: (id: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post(`/documents/documents/${id}/create_version/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getDocumentVersions: (id: string) => apiClient.get(`/documents/documents/${id}/versions/`),
  shareDocument: (id: string, data: Record<string, unknown>) =>
    apiClient.post(`/documents/documents/${id}/share/`, data),
  requestApproval: (id: string, approverId: string) =>
    apiClient.post(`/documents/documents/${id}/request_approval/`, { approver_id: approverId }),

  // Templates
  getDocumentTemplates: () => apiClient.get('/documents/templates/'),
  generateFromTemplate: (id: string, data: Record<string, unknown>) =>
    apiClient.post(`/documents/templates/${id}/generate/`, data),

  // Approvals
  getApprovals: () => apiClient.get('/documents/approvals/'),
  approveDocument: (id: string, comments: string = '') =>
    apiClient.post(`/documents/approvals/${id}/approve/`, { comments }),
  rejectDocument: (id: string, comments: string) =>
    apiClient.post(`/documents/approvals/${id}/reject/`, { comments }),

  // Comments
  getDocumentComments: (documentId: string) =>
    apiClient.get(`/documents/comments/?document=${documentId}`),
  addComment: (data: Record<string, unknown>) => apiClient.post('/documents/comments/', data),
};

// Integration Hub API
export const integrationAPI = {
  // Webhooks
  getWebhooks: () => apiClient.get('/integrations/webhooks/'),
  createWebhook: (data: Record<string, unknown>) => apiClient.post('/integrations/webhooks/', data),
  testWebhook: (id: string) => apiClient.post(`/integrations/webhooks/${id}/test/`),
  getWebhookDeliveries: (id: string) =>
    apiClient.get(`/integrations/webhooks/${id}/deliveries/`),
  activateWebhook: (id: string) => apiClient.post(`/integrations/webhooks/${id}/activate/`),
  deactivateWebhook: (id: string) => apiClient.post(`/integrations/webhooks/${id}/deactivate/`),

  // Integrations
  getIntegrations: () => apiClient.get('/integrations/integrations/'),
  createIntegration: (data: Record<string, unknown>) => apiClient.post('/integrations/integrations/', data),
  syncIntegration: (id: string) => apiClient.post(`/integrations/integrations/${id}/sync/`),
  testIntegration: (id: string) => apiClient.post(`/integrations/integrations/${id}/test/`),
  getIntegrationLogs: (id: string) =>
    apiClient.get(`/integrations/integrations/${id}/logs/`),
};

// Activity Feed API
export const activityAPI = {
  // Activities
  getActivities: (params?: Record<string, unknown>) => apiClient.get('/activity/activities/', { params }),
  getMyFeed: () => apiClient.get('/activity/activities/my_feed/'),
  getEntityActivities: (model: string, id: string) =>
    apiClient.get(`/activity/activities/for_entity/?model=${model}&id=${id}`),

  // Comments
  getComments: (model: string, id: string) =>
    apiClient.get(`/activity/comments/for_entity/?model=${model}&id=${id}`),
  addComment: (data: Record<string, unknown>) => apiClient.post('/activity/comments/', data),
  getReplies: (commentId: string) => apiClient.get(`/activity/comments/${commentId}/replies/`),

  // Notifications
  getNotifications: () => apiClient.get('/activity/notifications/'),
  markNotificationRead: (id: string) =>
    apiClient.post(`/activity/notifications/${id}/mark_read/`),
  markAllNotificationsRead: () =>
    apiClient.post('/activity/notifications/mark_all_read/'),
  getUnreadCount: () => apiClient.get('/activity/notifications/unread_count/'),

  // Mentions
  getMentions: () => apiClient.get('/activity/mentions/'),
  markMentionRead: (id: string) => apiClient.post(`/activity/mentions/${id}/mark_read/`),
  markAllMentionsRead: () => apiClient.post('/activity/mentions/mark_all_read/'),

  // Follows
  followEntity: (model: string, id: string) =>
    apiClient.post('/activity/follows/follow_entity/', { model, id }),
  unfollowEntity: (model: string, id: string) =>
    apiClient.post('/activity/follows/unfollow_entity/', { model, id }),
  getFollows: () => apiClient.get('/activity/follows/'),
};

// Lead Qualification API
export const leadQualificationAPI = {
  // Scoring Rules
  getScoringRules: () => apiClient.get('/lead-qualification/scoring-rules/'),
  createScoringRule: (data: Record<string, unknown>) => apiClient.post('/lead-qualification/scoring-rules/', data),
  updateScoringRule: (id: string, data: Record<string, unknown>) =>
    apiClient.patch(`/lead-qualification/scoring-rules/${id}/`, data),
  deleteScoringRule: (id: string) => apiClient.delete(`/lead-qualification/scoring-rules/${id}/`),
  activateRule: (id: string) => apiClient.post(`/lead-qualification/scoring-rules/${id}/activate/`),
  deactivateRule: (id: string) => apiClient.post(`/lead-qualification/scoring-rules/${id}/deactivate/`),

  // Qualification Criteria
  getQualificationCriteria: () => apiClient.get('/lead-qualification/qualification-criteria/'),
  createQualificationCriteria: (data: Record<string, unknown>) =>
    apiClient.post('/lead-qualification/qualification-criteria/', data),
  updateQualificationCriteria: (id: string, data: Record<string, unknown>) =>
    apiClient.patch(`/lead-qualification/qualification-criteria/${id}/`, data),
  deleteQualificationCriteria: (id: string) =>
    apiClient.delete(`/lead-qualification/qualification-criteria/${id}/`),

  // Lead Scores
  getLeadScores: (params?: Record<string, unknown>) => apiClient.get('/lead-qualification/lead-scores/', { params }),
  getLeadScore: (leadId: string) =>
    apiClient.get(`/lead-qualification/lead-scores/by_lead/?lead_id=${leadId}`),
  calculateScore: (leadId: string) =>
    apiClient.post(`/lead-qualification/lead-scores/calculate/`, { lead_id: leadId }),
  recalculateAll: () => apiClient.post('/lead-qualification/lead-scores/recalculate_all/'),
  getScoreBreakdown: (id: string) =>
    apiClient.get(`/lead-qualification/lead-scores/${id}/breakdown/`),
  getHistory: (id: string) => apiClient.get(`/lead-qualification/lead-scores/${id}/history/`),
  getSummary: () => apiClient.get('/lead-qualification/lead-scores/summary/'),

  // Qualification Workflows
  getWorkflows: () => apiClient.get('/lead-qualification/qualification-workflows/'),
  createWorkflow: (data: Record<string, unknown>) => apiClient.post('/lead-qualification/qualification-workflows/', data),
  updateWorkflow: (id: string, data: Record<string, unknown>) =>
    apiClient.patch(`/lead-qualification/qualification-workflows/${id}/`, data),
  deleteWorkflow: (id: string) =>
    apiClient.delete(`/lead-qualification/qualification-workflows/${id}/`),
  activateWorkflow: (id: string) =>
    apiClient.post(`/lead-qualification/qualification-workflows/${id}/activate/`),
  deactivateWorkflow: (id: string) =>
    apiClient.post(`/lead-qualification/qualification-workflows/${id}/deactivate/`),
  getWorkflowExecutions: (id: string) =>
    apiClient.get(`/lead-qualification/qualification-workflows/${id}/executions/`),

  // Lead Enrichment
  enrichLead: (leadId: string) =>
    apiClient.post(`/lead-qualification/lead-enrichment/enrich/`, { lead_id: leadId }),
  getEnrichmentData: (leadId: string) =>
    apiClient.get(`/lead-qualification/lead-enrichment/by_lead/?lead_id=${leadId}`),
};

// Advanced Reporting API
export const advancedReportingAPI = {
  // Dashboards
  getDashboards: () => apiClient.get('/advanced-reporting/dashboards/'),
  createDashboard: (data: Record<string, unknown>) => apiClient.post('/advanced-reporting/dashboards/', data),
  getDashboard: (id: string) => apiClient.get(`/advanced-reporting/dashboards/${id}/`),
  updateDashboard: (id: string, data: Record<string, unknown>) =>
    apiClient.patch(`/advanced-reporting/dashboards/${id}/`, data),
  deleteDashboard: (id: string) => apiClient.delete(`/advanced-reporting/dashboards/${id}/`),
  duplicateDashboard: (id: string) =>
    apiClient.post(`/advanced-reporting/dashboards/${id}/duplicate/`),
  shareDashboard: (id: string, data: Record<string, unknown>) =>
    apiClient.post(`/advanced-reporting/dashboards/${id}/share/`, data),
  getDashboardData: (id: string) => apiClient.get(`/advanced-reporting/dashboards/${id}/data/`),

  // Dashboard Widgets
  getWidgets: (dashboardId?: string) => {
    const params = dashboardId ? { dashboard: dashboardId } : {};
    return apiClient.get('/advanced-reporting/widgets/', { params });
  },
  createWidget: (data: Record<string, unknown>) => apiClient.post('/advanced-reporting/widgets/', data),
  updateWidget: (id: string, data: Record<string, unknown>) =>
    apiClient.patch(`/advanced-reporting/widgets/${id}/`, data),
  deleteWidget: (id: string) => apiClient.delete(`/advanced-reporting/widgets/${id}/`),
  getWidgetData: (id: string) => apiClient.get(`/advanced-reporting/widgets/${id}/data/`),

  // Reports
  getReports: () => apiClient.get('/advanced-reporting/reports/'),
  createReport: (data: Record<string, unknown>) => apiClient.post('/advanced-reporting/reports/', data),
  getReport: (id: string) => apiClient.get(`/advanced-reporting/reports/${id}/`),
  updateReport: (id: string, data: Record<string, unknown>) =>
    apiClient.patch(`/advanced-reporting/reports/${id}/`, data),
  deleteReport: (id: string) => apiClient.delete(`/advanced-reporting/reports/${id}/`),
  executeReport: (id: string) => apiClient.post(`/advanced-reporting/reports/${id}/execute/`),
  previewReport: (id: string) => apiClient.get(`/advanced-reporting/reports/${id}/preview/`),
  scheduleReport: (id: string, data: Record<string, unknown>) =>
    apiClient.post(`/advanced-reporting/reports/${id}/schedule/`, data),

  // Report Schedules
  getSchedules: (reportId?: string) => {
    const params = reportId ? { report: reportId } : {};
    return apiClient.get('/advanced-reporting/schedules/', { params });
  },
  createSchedule: (data: Record<string, unknown>) => apiClient.post('/advanced-reporting/schedules/', data),
  updateSchedule: (id: string, data: Record<string, unknown>) =>
    apiClient.patch(`/advanced-reporting/schedules/${id}/`, data),
  deleteSchedule: (id: string) => apiClient.delete(`/advanced-reporting/schedules/${id}/`),
  activateSchedule: (id: string) =>
    apiClient.post(`/advanced-reporting/schedules/${id}/activate/`),
  deactivateSchedule: (id: string) =>
    apiClient.post(`/advanced-reporting/schedules/${id}/deactivate/`),

  // Report Executions
  getExecutions: (reportId?: string) => {
    const params = reportId ? { report: reportId } : {};
    return apiClient.get('/advanced-reporting/executions/', { params });
  },
  getExecution: (id: string) => apiClient.get(`/advanced-reporting/executions/${id}/`),
  downloadExecution: (id: string) =>
    apiClient.get(`/advanced-reporting/executions/${id}/download/`),

  // KPIs
  getKPIs: () => apiClient.get('/advanced-reporting/kpis/'),
  createKPI: (data: Record<string, unknown>) => apiClient.post('/advanced-reporting/kpis/', data),
  getKPI: (id: string) => apiClient.get(`/advanced-reporting/kpis/${id}/`),
  updateKPI: (id: string, data: Record<string, unknown>) => apiClient.patch(`/advanced-reporting/kpis/${id}/`, data),
  deleteKPI: (id: string) => apiClient.delete(`/advanced-reporting/kpis/${id}/`),
  calculateKPI: (id: string) => apiClient.post(`/advanced-reporting/kpis/${id}/calculate/`),
  getKPIHistory: (id: string, days?: number) =>
    apiClient.get(`/advanced-reporting/kpis/${id}/history/`, { params: { days } }),
  getKPISummary: () => apiClient.get('/advanced-reporting/kpis/summary/'),

  // KPI Values
  getKPIValues: (kpiId?: string) => {
    const params = kpiId ? { kpi: kpiId } : {};
    return apiClient.get('/advanced-reporting/kpi-values/', { params });
  },
};

// ==================== Interactive Features API ====================

// User Preferences API
export const preferencesAPI = {
  // Get current user preferences
  getPreferences: async () => {
    const response = await apiClient.get('/v1/interactive/preferences/me/');
    return response.data;
  },

  // Update preferences
  updatePreferences: async (data: Record<string, unknown>) => {
    const response = await apiClient.patch('/v1/interactive/preferences/me/', data);
    return response.data;
  },

  // Save dashboard layout
  saveDashboardLayout: async (widgets: Array<{ widget_id: string; visible: boolean; order: number; size?: string }>) => {
    const response = await apiClient.post('/v1/interactive/preferences/dashboard/', { widgets });
    return response.data;
  },

  // Add recent item
  addRecentItem: async (type: string, id: string, title: string) => {
    const response = await apiClient.post('/v1/interactive/preferences/recent-item/', { type, id, title });
    return response.data;
  },

  // Get recent items
  getRecentItems: async () => {
    const prefs = await apiClient.get('/v1/interactive/preferences/me/');
    return prefs.data.recent_items || [];
  },
};

// Onboarding API
export const onboardingAPI = {
  // Get onboarding status
  getStatus: async () => {
    const response = await apiClient.get('/v1/interactive/onboarding/status/');
    return response.data;
  },

  // Complete a step
  completeStep: async (stepId: string, xpReward: number = 50) => {
    const response = await apiClient.post('/v1/interactive/onboarding/step/', {
      step_id: stepId,
      xp_reward: xpReward,
    });
    return response.data;
  },

  // Complete the product tour
  completeTour: async () => {
    const response = await apiClient.post('/v1/interactive/onboarding/tour/complete/');
    return response.data;
  },

  // Dismiss the tour
  dismissTour: async () => {
    const response = await apiClient.post('/v1/interactive/onboarding/tour/dismiss/');
    return response.data;
  },

  // Reset onboarding (for testing)
  reset: async () => {
    const response = await apiClient.post('/v1/interactive/onboarding/reset/');
    return response.data;
  },
};

// AI Recommendations API
export const recommendationsAPI = {
  // Get active recommendations
  getActive: async (params?: { type?: string; impact?: string; limit?: number }) => {
    const response = await apiClient.get('/v1/interactive/recommendations/active/', { params });
    return response.data;
  },

  // Dismiss a recommendation
  dismiss: async (id: string) => {
    const response = await apiClient.post(`/v1/interactive/recommendations/${id}/dismiss/`);
    return response.data;
  },

  // Complete a recommendation
  complete: async (id: string) => {
    const response = await apiClient.post(`/v1/interactive/recommendations/${id}/complete/`);
    return response.data;
  },

  // Generate new recommendations
  generate: async () => {
    const response = await apiClient.post('/v1/interactive/recommendations/generate/');
    return response.data;
  },
};

// Global Search API
export const globalSearchAPI = {
  // Perform global search
  search: async (query: string, options?: { types?: string[]; limit?: number }) => {
    const response = await apiClient.post('/v1/interactive/search/', {
      query,
      types: options?.types || ['contact', 'company', 'lead', 'opportunity', 'task'],
      limit: options?.limit || 10,
    });
    return response.data;
  },

  // Get recent searches
  getRecentSearches: async (limit: number = 10) => {
    const response = await apiClient.get('/v1/interactive/search/recent/', { params: { limit } });
    return response.data;
  },

  // Clear search history
  clearHistory: async () => {
    const response = await apiClient.delete('/v1/interactive/search/recent/');
    return response.data;
  },
};

// Smart Filters API
export const smartFiltersAPI = {
  // Get all filters
  getFilters: async (entityType?: string) => {
    const params = entityType ? { entity_type: entityType } : {};
    const response = await apiClient.get('/v1/interactive/smart-filters/', { params });
    return response.data;
  },

  // Create a filter
  createFilter: async (data: {
    name: string;
    entity_type: string;
    filter_config: Record<string, unknown>;
    icon?: string;
    color?: string;
  }) => {
    const response = await apiClient.post('/v1/interactive/smart-filters/', data);
    return response.data;
  },

  // Update a filter
  updateFilter: async (id: string, data: Record<string, unknown>) => {
    const response = await apiClient.patch(`/v1/interactive/smart-filters/${id}/`, data);
    return response.data;
  },

  // Delete a filter
  deleteFilter: async (id: string) => {
    const response = await apiClient.delete(`/v1/interactive/smart-filters/${id}/`);
    return response.data;
  },

  // Record filter usage
  useFilter: async (id: string) => {
    const response = await apiClient.post(`/v1/interactive/smart-filters/${id}/use/`);
    return response.data;
  },
};

// Quick Actions API
export const quickActionsAPI = {
  // Get all quick actions
  getActions: async () => {
    const response = await apiClient.get('/v1/interactive/quick-actions/');
    return response.data;
  },

  // Get pinned actions
  getPinnedActions: async () => {
    const response = await apiClient.get('/v1/interactive/quick-actions/pinned/');
    return response.data;
  },

  // Create a quick action
  createAction: async (data: {
    name: string;
    action_type: string;
    action_config?: Record<string, unknown>;
    url?: string;
    icon?: string;
    color?: string;
    shortcut?: string;
  }) => {
    const response = await apiClient.post('/v1/interactive/quick-actions/', data);
    return response.data;
  },

  // Update a quick action
  updateAction: async (id: string, data: Record<string, unknown>) => {
    const response = await apiClient.patch(`/v1/interactive/quick-actions/${id}/`, data);
    return response.data;
  },

  // Delete a quick action
  deleteAction: async (id: string) => {
    const response = await apiClient.delete(`/v1/interactive/quick-actions/${id}/`);
    return response.data;
  },

  // Toggle pin status
  togglePin: async (id: string) => {
    const response = await apiClient.post(`/v1/interactive/quick-actions/${id}/toggle_pin/`);
    return response.data;
  },

  // Record action usage
  recordUse: async (id: string) => {
    const response = await apiClient.post(`/v1/interactive/quick-actions/${id}/record_use/`);
    return response.data;
  },
};

// Data Enrichment API (for AI features)
export const dataEnrichmentAPI = {
  // Get enrichment suggestions
  getSuggestions: async (entityType: string, entityId: string) => {
    const response = await apiClient.get('/data-enrichment/suggestions/', {
      params: { entity_type: entityType, entity_id: entityId },
    });
    return response.data;
  },

  // Enrich entity data
  enrichEntity: async (entityType: string, entityId: string) => {
    const response = await apiClient.post('/data-enrichment/enrich/', {
      entity_type: entityType,
      entity_id: entityId,
    });
    return response.data;
  },

  // Get company insights
  getCompanyInsights: async (companyId: string) => {
    const response = await apiClient.get(`/data-enrichment/company-insights/${companyId}/`);
    return response.data;
  },
};

// AI Chatbot API
export const aiChatbotAPI = {
  // Chat
  sendMessage: async (sessionId: string, message: string) => {
    const response = await apiClient.post('/v1/ai-chatbot/chat/', { session_id: sessionId, message });
    return response.data;
  },

  // Sessions
  getSessions: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get('/v1/ai-chatbot/sessions/', { params });
    return response.data;
  },

  createSession: async (name?: string) => {
    const response = await apiClient.post('/v1/ai-chatbot/sessions/', { name });
    return response.data;
  },

  getSession: async (id: string) => {
    const response = await apiClient.get(`/v1/ai-chatbot/sessions/${id}/`);
    return response.data;
  },

  deleteSession: async (id: string) => {
    const response = await apiClient.delete(`/v1/ai-chatbot/sessions/${id}/`);
    return response.data;
  },

  // Email Generation
  generateEmail: async (data: { context: string; tone?: string; recipient_id?: string }) => {
    const response = await apiClient.post('/v1/ai-chatbot/generate-email/', data);
    return response.data;
  },

  // Data Query
  queryData: async (query: string) => {
    const response = await apiClient.post('/v1/ai-chatbot/query/', { query });
    return response.data;
  },

  // Suggestions
  suggestActions: async (context?: Record<string, unknown>) => {
    const response = await apiClient.post('/v1/ai-chatbot/suggest-actions/', context);
    return response.data;
  },

  // Feedback
  submitFeedback: async (messageId: string, rating: number, comment?: string) => {
    const response = await apiClient.post(`/v1/ai-chatbot/messages/${messageId}/feedback/`, { rating, comment });
    return response.data;
  },

  // Quick Actions
  getQuickActions: async () => {
    const response = await apiClient.get('/v1/ai-chatbot/quick-actions/');
    return response.data;
  },

  createQuickAction: async (data: Record<string, unknown>) => {
    const response = await apiClient.post('/v1/ai-chatbot/quick-actions/', data);
    return response.data;
  },

  // Email Templates
  getEmailTemplates: async () => {
    const response = await apiClient.get('/v1/ai-chatbot/email-templates/');
    return response.data;
  },

  createEmailTemplate: async (data: Record<string, unknown>) => {
    const response = await apiClient.post('/v1/ai-chatbot/email-templates/', data);
    return response.data;
  },
};

// App Marketplace API
export const appMarketplaceAPI = {
  // Dashboard
  getDashboard: async () => {
    const response = await apiClient.get('/v1/marketplace/dashboard/');
    return response.data;
  },

  // Categories
  getCategories: async () => {
    const response = await apiClient.get('/v1/marketplace/categories/');
    return response.data;
  },

  // Apps
  getApps: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get('/v1/marketplace/apps/', { params });
    return response.data;
  },

  getApp: async (id: string) => {
    const response = await apiClient.get(`/v1/marketplace/apps/${id}/`);
    return response.data;
  },

  searchApps: async (query: string) => {
    const response = await apiClient.get('/v1/marketplace/apps/', { params: { search: query } });
    return response.data;
  },

  // Install/Uninstall
  installApp: async (appId: string) => {
    const response = await apiClient.post(`/v1/marketplace/apps/${appId}/install/`);
    return response.data;
  },

  uninstallApp: async (appId: string) => {
    const response = await apiClient.post(`/v1/marketplace/apps/${appId}/uninstall/`);
    return response.data;
  },

  // My Apps
  getMyApps: async () => {
    const response = await apiClient.get('/v1/marketplace/my-apps/');
    return response.data;
  },

  getAppSettings: async (id: string) => {
    const response = await apiClient.get(`/v1/marketplace/my-apps/${id}/settings/`);
    return response.data;
  },

  updateAppSettings: async (id: string, data: Record<string, unknown>) => {
    const response = await apiClient.patch(`/v1/marketplace/my-apps/${id}/settings/`, data);
    return response.data;
  },

  // Developer Portal
  getDeveloperApps: async () => {
    const response = await apiClient.get('/v1/marketplace/developer/');
    return response.data;
  },

  submitApp: async (data: FormData) => {
    const response = await apiClient.post('/v1/marketplace/developer/', data);
    return response.data;
  },

  updateAppSubmission: async (id: string, data: Record<string, unknown>) => {
    const response = await apiClient.patch(`/v1/marketplace/developer/${id}/`, data);
    return response.data;
  },
};

// ESG Reporting API
export const esgReportingAPI = {
  // Dashboard
  getDashboard: async () => {
    const response = await apiClient.get('/v1/esg/dashboard/');
    return response.data;
  },

  // Frameworks
  getFrameworks: async () => {
    const response = await apiClient.get('/v1/esg/frameworks/');
    return response.data;
  },

  getFramework: async (id: string) => {
    const response = await apiClient.get(`/v1/esg/frameworks/${id}/`);
    return response.data;
  },

  // Categories
  getCategories: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get('/v1/esg/categories/', { params });
    return response.data;
  },

  // Metrics
  getMetrics: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get('/v1/esg/metrics/', { params });
    return response.data;
  },

  getMetric: async (id: string) => {
    const response = await apiClient.get(`/v1/esg/metrics/${id}/`);
    return response.data;
  },

  createMetric: async (data: Record<string, unknown>) => {
    const response = await apiClient.post('/v1/esg/metrics/', data);
    return response.data;
  },

  // Data Entries
  getDataEntries: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get('/v1/esg/data/', { params });
    return response.data;
  },

  createDataEntry: async (data: Record<string, unknown>) => {
    const response = await apiClient.post('/v1/esg/data/', data);
    return response.data;
  },

  updateDataEntry: async (id: string, data: Record<string, unknown>) => {
    const response = await apiClient.patch(`/v1/esg/data/${id}/`, data);
    return response.data;
  },

  // Targets
  getTargets: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get('/v1/esg/targets/', { params });
    return response.data;
  },

  createTarget: async (data: Record<string, unknown>) => {
    const response = await apiClient.post('/v1/esg/targets/', data);
    return response.data;
  },

  updateTarget: async (id: string, data: Record<string, unknown>) => {
    const response = await apiClient.patch(`/v1/esg/targets/${id}/`, data);
    return response.data;
  },

  // Reports
  getReports: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get('/v1/esg/reports/', { params });
    return response.data;
  },

  createReport: async (data: Record<string, unknown>) => {
    const response = await apiClient.post('/v1/esg/reports/', data);
    return response.data;
  },

  generateReport: async (id: string) => {
    const response = await apiClient.post(`/v1/esg/reports/${id}/generate/`);
    return response.data;
  },

  downloadReport: async (id: string) => {
    const response = await apiClient.get(`/v1/esg/reports/${id}/download/`, { responseType: 'blob' });
    return response.data;
  },

  // Carbon Footprint
  getCarbonData: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get('/v1/esg/carbon/', { params });
    return response.data;
  },

  createCarbonEntry: async (data: Record<string, unknown>) => {
    const response = await apiClient.post('/v1/esg/carbon/', data);
    return response.data;
  },

  // Supplier Assessments
  getSupplierAssessments: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get('/v1/esg/suppliers/', { params });
    return response.data;
  },

  createSupplierAssessment: async (data: Record<string, unknown>) => {
    const response = await apiClient.post('/v1/esg/suppliers/', data);
    return response.data;
  },
};

// Realtime Collaboration API
export const realtimeCollabAPI = {
  // Documents
  getDocuments: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get('/v1/realtime-collab/documents/', { params });
    return response.data;
  },

  getDocument: async (id: string) => {
    const response = await apiClient.get(`/v1/realtime-collab/documents/${id}/`);
    return response.data;
  },

  createDocument: async (data: Record<string, unknown>) => {
    const response = await apiClient.post('/v1/realtime-collab/documents/', data);
    return response.data;
  },

  updateDocument: async (id: string, data: Record<string, unknown>) => {
    const response = await apiClient.patch(`/v1/realtime-collab/documents/${id}/`, data);
    return response.data;
  },

  deleteDocument: async (id: string) => {
    const response = await apiClient.delete(`/v1/realtime-collab/documents/${id}/`);
    return response.data;
  },

  // Sharing
  shareDocument: async (id: string, data: { users: string[]; permission: string }) => {
    const response = await apiClient.post(`/v1/realtime-collab/documents/${id}/share/`, data);
    return response.data;
  },

  getSharedDocument: async (token: string) => {
    const response = await apiClient.get(`/v1/realtime-collab/shared/${token}/`);
    return response.data;
  },

  // My Collaborations
  getMyCollaborations: async () => {
    const response = await apiClient.get('/v1/realtime-collab/my-collaborations/');
    return response.data;
  },

  // Templates
  getTemplates: async () => {
    const response = await apiClient.get('/v1/realtime-collab/templates/');
    return response.data;
  },

  createTemplate: async (data: Record<string, unknown>) => {
    const response = await apiClient.post('/v1/realtime-collab/templates/', data);
    return response.data;
  },

  createFromTemplate: async (templateId: string, data: Record<string, unknown>) => {
    const response = await apiClient.post(`/v1/realtime-collab/templates/${templateId}/use/`, data);
    return response.data;
  },

  // Cursors & Presence
  updateCursor: async (docId: string, position: { line: number; column: number }) => {
    const response = await apiClient.post(`/v1/realtime-collab/documents/${docId}/cursor/`, position);
    return response.data;
  },
};

// Customer Portal API
export const customerPortalAPI = {
  // Authentication
  login: async (credentials: { email: string; password: string }) => {
    const response = await apiClient.post('/v1/customer-portal/auth/login/', credentials);
    return response.data;
  },

  logout: async () => {
    const response = await apiClient.post('/v1/customer-portal/auth/logout/');
    return response.data;
  },

  resetPassword: async (email: string) => {
    const response = await apiClient.post('/v1/customer-portal/auth/password-reset/', { email });
    return response.data;
  },

  // Profile
  getProfile: async () => {
    const response = await apiClient.get('/v1/customer-portal/profile/');
    return response.data;
  },

  updateProfile: async (data: Record<string, unknown>) => {
    const response = await apiClient.put('/v1/customer-portal/profile/', data);
    return response.data;
  },

  // Dashboard
  getDashboard: async () => {
    const response = await apiClient.get('/v1/customer-portal/dashboard/');
    return response.data;
  },

  // Support Tickets
  getTickets: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get('/v1/customer-portal/tickets/', { params });
    return response.data;
  },

  getTicket: async (id: string) => {
    const response = await apiClient.get(`/v1/customer-portal/tickets/${id}/`);
    return response.data;
  },

  createTicket: async (data: { subject: string; description: string; priority?: string }) => {
    const response = await apiClient.post('/v1/customer-portal/tickets/', data);
    return response.data;
  },

  updateTicket: async (id: string, data: Record<string, unknown>) => {
    const response = await apiClient.patch(`/v1/customer-portal/tickets/${id}/`, data);
    return response.data;
  },

  addTicketComment: async (id: string, message: string) => {
    const response = await apiClient.post(`/v1/customer-portal/tickets/${id}/comments/`, { message });
    return response.data;
  },

  // Orders
  getOrders: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get('/v1/customer-portal/orders/', { params });
    return response.data;
  },

  getOrder: async (id: string) => {
    const response = await apiClient.get(`/v1/customer-portal/orders/${id}/`);
    return response.data;
  },

  // Knowledge Base
  getKnowledgeBase: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get('/v1/customer-portal/knowledge-base/', { params });
    return response.data;
  },

  getArticle: async (id: string) => {
    const response = await apiClient.get(`/v1/customer-portal/knowledge-base/${id}/`);
    return response.data;
  },

  searchKnowledgeBase: async (query: string) => {
    const response = await apiClient.get('/v1/customer-portal/knowledge-base/', { params: { search: query } });
    return response.data;
  },

  // Notifications
  getNotifications: async () => {
    const response = await apiClient.get('/v1/customer-portal/notifications/');
    return response.data;
  },

  markNotificationRead: async (id: string) => {
    const response = await apiClient.post(`/v1/customer-portal/notifications/${id}/mark-read/`);
    return response.data;
  },
};

// Social Inbox API
export const socialInboxAPI = {
  // Dashboard
  getDashboard: async () => {
    const response = await apiClient.get('/v1/social-inbox/dashboard/');
    return response.data;
  },

  // Social Accounts
  getAccounts: async () => {
    const response = await apiClient.get('/v1/social-inbox/accounts/');
    return response.data;
  },

  connectAccount: async (platform: string, authData: Record<string, unknown>) => {
    const response = await apiClient.post('/v1/social-inbox/accounts/', { platform, ...authData });
    return response.data;
  },

  disconnectAccount: async (id: string) => {
    const response = await apiClient.delete(`/v1/social-inbox/accounts/${id}/`);
    return response.data;
  },

  refreshAccount: async (id: string) => {
    const response = await apiClient.post(`/v1/social-inbox/accounts/${id}/refresh/`);
    return response.data;
  },

  // Conversations
  getConversations: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get('/v1/social-inbox/conversations/', { params });
    return response.data;
  },

  getConversation: async (id: string) => {
    const response = await apiClient.get(`/v1/social-inbox/conversations/${id}/`);
    return response.data;
  },

  replyToConversation: async (id: string, message: string) => {
    const response = await apiClient.post(`/v1/social-inbox/conversations/${id}/reply/`, { message });
    return response.data;
  },

  assignConversation: async (id: string, userId: string) => {
    const response = await apiClient.post(`/v1/social-inbox/conversations/${id}/assign/`, { user_id: userId });
    return response.data;
  },

  archiveConversation: async (id: string) => {
    const response = await apiClient.post(`/v1/social-inbox/conversations/${id}/archive/`);
    return response.data;
  },

  // Monitoring Rules
  getMonitoringRules: async () => {
    const response = await apiClient.get('/v1/social-inbox/monitoring-rules/');
    return response.data;
  },

  createMonitoringRule: async (data: Record<string, unknown>) => {
    const response = await apiClient.post('/v1/social-inbox/monitoring-rules/', data);
    return response.data;
  },

  updateMonitoringRule: async (id: string, data: Record<string, unknown>) => {
    const response = await apiClient.patch(`/v1/social-inbox/monitoring-rules/${id}/`, data);
    return response.data;
  },

  deleteMonitoringRule: async (id: string) => {
    const response = await apiClient.delete(`/v1/social-inbox/monitoring-rules/${id}/`);
    return response.data;
  },

  // Posts
  getPosts: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get('/v1/social-inbox/posts/', { params });
    return response.data;
  },

  createPost: async (data: { content: string; platforms: string[]; scheduled_at?: string }) => {
    const response = await apiClient.post('/v1/social-inbox/posts/', data);
    return response.data;
  },

  schedulePost: async (id: string, scheduledAt: string) => {
    const response = await apiClient.post(`/v1/social-inbox/posts/${id}/schedule/`, { scheduled_at: scheduledAt });
    return response.data;
  },

  publishPost: async (id: string) => {
    const response = await apiClient.post(`/v1/social-inbox/posts/${id}/publish/`);
    return response.data;
  },
};

// Enterprise Security API
export const enterpriseSecurityAPI = {
  // Dashboard
  getDashboard: async () => {
    const response = await apiClient.get('/v1/security/dashboard/');
    return response.data;
  },

  getRiskAssessment: async () => {
    const response = await apiClient.get('/v1/security/risk-assessment/');
    return response.data;
  },

  // Device Management
  getDevices: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get('/v1/security/devices/', { params });
    return response.data;
  },

  getDevice: async (id: string) => {
    const response = await apiClient.get(`/v1/security/devices/${id}/`);
    return response.data;
  },

  trustDevice: async (id: string) => {
    const response = await apiClient.post(`/v1/security/devices/${id}/trust/`);
    return response.data;
  },

  blockDevice: async (id: string) => {
    const response = await apiClient.post(`/v1/security/devices/${id}/block/`);
    return response.data;
  },

  // Sessions
  getSessions: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get('/v1/security/sessions/', { params });
    return response.data;
  },

  terminateSession: async (id: string) => {
    const response = await apiClient.delete(`/v1/security/sessions/${id}/`);
    return response.data;
  },

  terminateAllSessions: async () => {
    const response = await apiClient.post('/v1/security/sessions/terminate-all/');
    return response.data;
  },

  // Audit Logs
  getAuditLogs: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get('/v1/security/audit-logs/', { params });
    return response.data;
  },

  exportAuditLogs: async (params?: { start_date?: string; end_date?: string }) => {
    const response = await apiClient.get('/v1/security/audit-logs/export/', { params, responseType: 'blob' });
    return response.data;
  },

  // Access Policies
  getPolicies: async () => {
    const response = await apiClient.get('/v1/security/policies/');
    return response.data;
  },

  getPolicy: async (id: string) => {
    const response = await apiClient.get(`/v1/security/policies/${id}/`);
    return response.data;
  },

  createPolicy: async (data: Record<string, unknown>) => {
    const response = await apiClient.post('/v1/security/policies/', data);
    return response.data;
  },

  updatePolicy: async (id: string, data: Record<string, unknown>) => {
    const response = await apiClient.patch(`/v1/security/policies/${id}/`, data);
    return response.data;
  },

  deletePolicy: async (id: string) => {
    const response = await apiClient.delete(`/v1/security/policies/${id}/`);
    return response.data;
  },

  // Threat Indicators
  getThreats: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get('/v1/security/threats/', { params });
    return response.data;
  },

  acknowledgeThreat: async (id: string) => {
    const response = await apiClient.post(`/v1/security/threats/${id}/acknowledge/`);
    return response.data;
  },

  // Security Incidents
  getIncidents: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get('/v1/security/incidents/', { params });
    return response.data;
  },

  getIncident: async (id: string) => {
    const response = await apiClient.get(`/v1/security/incidents/${id}/`);
    return response.data;
  },

  createIncident: async (data: Record<string, unknown>) => {
    const response = await apiClient.post('/v1/security/incidents/', data);
    return response.data;
  },

  resolveIncident: async (id: string, data: { resolution: string }) => {
    const response = await apiClient.post(`/v1/security/incidents/${id}/resolve/`, data);
    return response.data;
  },

  // Data Classifications
  getClassifications: async () => {
    const response = await apiClient.get('/v1/security/classifications/');
    return response.data;
  },

  createClassification: async (data: Record<string, unknown>) => {
    const response = await apiClient.post('/v1/security/classifications/', data);
    return response.data;
  },
};

export default apiClient;
