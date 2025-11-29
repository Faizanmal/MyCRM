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

export default apiClient;