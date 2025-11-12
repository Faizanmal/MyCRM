// Enterprise API client extensions
/* eslint-disable @typescript-eslint/no-explicit-any */
import apiClient from './api';

// Core Enterprise APIs
export const coreAPI = {
  // Audit Logs
  getAuditLogs: async (params?: any) => {
    const response = await apiClient.get('/core/audit-logs/', { params });
    return response.data;
  },
  
  getSecuritySummary: async () => {
    const response = await apiClient.get('/core/audit-logs/security_summary/');
    return response.data;
  },

  // System Configuration
  getSystemConfig: async () => {
    const response = await apiClient.get('/core/system-config/');
    return response.data;
  },

  updateSystemConfig: async (key: string, data: any) => {
    const response = await apiClient.put(`/core/system-config/${key}/`, data);
    return response.data;
  },

  // API Keys
  getAPIKeys: async () => {
    const response = await apiClient.get('/core/api-keys/');
    return response.data;
  },

  createAPIKey: async (data: any) => {
    const response = await apiClient.post('/core/api-keys/', data);
    return response.data;
  },

  revokeAPIKey: async (id: string) => {
    const response = await apiClient.post(`/core/api-keys/${id}/revoke/`);
    return response.data;
  },

  // Data Backups
  getBackups: async () => {
    const response = await apiClient.get('/core/data-backups/');
    return response.data;
  },

  createBackup: async (backupType: string = 'full') => {
    const response = await apiClient.post('/core/data-backups/create_backup/', {
      backup_type: backupType
    });
    return response.data;
  },

  // Workflows
  getWorkflows: async () => {
    const response = await apiClient.get('/core/workflows/');
    return response.data;
  },

  createWorkflow: async (data: any) => {
    const response = await apiClient.post('/core/workflows/', data);
    return response.data;
  },

  executeWorkflow: async (id: string, triggerData?: any) => {
    const response = await apiClient.post(`/core/workflows/${id}/execute/`, {
      trigger_data: triggerData
    });
    return response.data;
  },

  // Integrations
  getIntegrations: async () => {
    const response = await apiClient.get('/core/integrations/');
    return response.data;
  },

  createIntegration: async (data: any) => {
    const response = await apiClient.post('/core/integrations/', data);
    return response.data;
  },

  testIntegration: async (id: string) => {
    const response = await apiClient.post(`/core/integrations/${id}/test_connection/`);
    return response.data;
  },

  // System Health
  getSystemHealth: async () => {
    const response = await apiClient.get('/core/system-health/');
    return response.data;
  },

  getHealthDashboard: async () => {
    const response = await apiClient.get('/core/system-health/dashboard/');
    return response.data;
  },

  // Security Dashboard
  getSecurityDashboard: async () => {
    const response = await apiClient.get('/core/security-dashboard/');
    return response.data;
  },

  // Advanced Analytics
  getAdvancedAnalytics: async () => {
    const response = await apiClient.get('/core/advanced-analytics/');
    return response.data;
  },
};

// AI Analytics APIs
export const aiAPI = {
  getSalesForcast: async (period: number = 3) => {
    const response = await apiClient.get('/core/ai-analytics/sales_forecast/', {
      params: { period }
    });
    return response.data;
  },

  calculateLeadScore: async (leadId: number) => {
    const response = await apiClient.post('/core/ai-analytics/lead_scoring/', {
      lead_id: leadId
    });
    return response.data;
  },

  getCustomerSegmentation: async () => {
    const response = await apiClient.get('/core/ai-analytics/customer_segmentation/');
    return response.data;
  },

  getChurnPrediction: async () => {
    const response = await apiClient.get('/core/ai-analytics/churn_prediction/');
    return response.data;
  },

  getNextBestAction: async (recordType: string, recordId: number) => {
    const response = await apiClient.post('/core/ai-analytics/next_best_action/', {
      record_type: recordType,
      record_id: recordId
    });
    return response.data;
  },

  getAIInsightsDashboard: async () => {
    const response = await apiClient.get('/core/ai-analytics/ai_insights_dashboard/');
    return response.data;
  },
};

// Real-time notifications (WebSocket would be ideal)
export const notificationsAPI = {
  getNotifications: async () => {
    const response = await apiClient.get('/core/notification-templates/');
    return response.data;
  },

  markAsRead: async (notificationId: string) => {
    const response = await apiClient.patch(`/core/notification-templates/${notificationId}/`, {
      is_read: true
    });
    return response.data;
  },
};

// Export all enterprise APIs
export const enterpriseAPI = {
  core: coreAPI,
  ai: aiAPI,
  notifications: notificationsAPI,
};