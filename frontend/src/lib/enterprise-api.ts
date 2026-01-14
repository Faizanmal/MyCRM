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

// ============ Custom Fields API ============
export interface CustomFieldOption {
  value: string;
  label: string;
}

export interface CustomField {
  id: string;
  name: string;
  label: string;
  field_type: string;
  help_text: string;
  placeholder: string;
  content_type: number;
  content_type_name?: string;
  is_required: boolean;
  min_length?: number;
  max_length?: number;
  min_value?: number;
  max_value?: number;
  regex_pattern?: string;
  regex_error_message?: string;
  options: CustomFieldOption[];
  default_value: string;
  order: number;
  is_visible: boolean;
  is_searchable: boolean;
  is_filterable: boolean;
  is_public: boolean;
  visible_to_roles: string[];
  editable_by_roles: string[];
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

export interface CustomFieldGroup {
  id: string;
  name: string;
  description: string;
  entity_type: string;
  order: number;
  is_collapsed: boolean;
  fields: CustomField[];
}

export const customFieldsAPI = {
  list: async (entityType?: string) => {
    const params = entityType ? { entity_type: entityType } : {};
    const response = await apiClient.get('/v1/custom-fields/', { params });
    return response.data;
  },
  get: async (id: string) => {
    const response = await apiClient.get(`/v1/custom-fields/${id}/`);
    return response.data;
  },
  create: async (data: Partial<CustomField>) => {
    const response = await apiClient.post('/v1/custom-fields/', data);
    return response.data;
  },
  update: async (id: string, data: Partial<CustomField>) => {
    const response = await apiClient.patch(`/v1/custom-fields/${id}/`, data);
    return response.data;
  },
  delete: async (id: string) => {
    const response = await apiClient.delete(`/v1/custom-fields/${id}/`);
    return response.data;
  },
  reorder: async (fieldIds: string[]) => {
    const response = await apiClient.post('/v1/custom-fields/reorder/', { field_ids: fieldIds });
    return response.data;
  },
  listGroups: async (entityType?: string) => {
    const params = entityType ? { entity_type: entityType } : {};
    const response = await apiClient.get('/v1/custom-field-groups/', { params });
    return response.data;
  },
  createGroup: async (data: Partial<CustomFieldGroup>) => {
    const response = await apiClient.post('/v1/custom-field-groups/', data);
    return response.data;
  },
  getContentTypes: async () => {
    const response = await apiClient.get('/v1/content-types/');
    return response.data;
  },
};

// ============ Activity Timeline API ============
export interface Activity {
  id: string;
  actor: {
    id: number;
    username: string;
    first_name: string;
    last_name: string;
    avatar?: string;
  };
  action: string;
  content_type: string;
  object_id: string;
  target_name?: string;
  description: string;
  metadata: Record<string, unknown>;
  is_public: boolean;
  created_at: string;
}

export interface Comment {
  id: string;
  author: {
    id: number;
    username: string;
    first_name: string;
    last_name: string;
    avatar?: string;
  };
  content: string;
  parent?: string;
  replies?: Comment[];
  mentions: { id: number; username: string }[];
  created_at: string;
  updated_at: string;
  is_edited: boolean;
}

export const activityTimelineAPI = {
  list: async (params?: {
    action?: string;
    actor?: number;
    content_type?: string;
    page?: number;
    page_size?: number;
  }) => {
    const response = await apiClient.get('/activity/activities/', { params });
    return response.data;
  },
  myFeed: async () => {
    const response = await apiClient.get('/activity/activities/my_feed/');
    return response.data;
  },
  forEntity: async (model: string, id: string) => {
    const response = await apiClient.get('/activity/activities/for_entity/', {
      params: { model, id },
    });
    return response.data;
  },
  listComments: async (model: string, id: string) => {
    const response = await apiClient.get('/activity/comments/', {
      params: { model, object_id: id },
    });
    return response.data;
  },
  createComment: async (data: { content_type: string; object_id: string; content: string; parent?: string }) => {
    const response = await apiClient.post('/activity/comments/', data);
    return response.data;
  },
  listNotifications: async (unreadOnly?: boolean) => {
    const params = unreadOnly ? { is_read: false } : {};
    const response = await apiClient.get('/activity/notifications/', { params });
    return response.data;
  },
  markNotificationRead: async (id: string) => {
    const response = await apiClient.post(`/activity/notifications/${id}/mark_read/`);
    return response.data;
  },
  markAllRead: async () => {
    const response = await apiClient.post('/activity/notifications/mark_all_read/');
    return response.data;
  },
  follow: async (contentType: string, objectId: string) => {
    const response = await apiClient.post('/activity/follows/', {
      content_type: contentType,
      object_id: objectId,
    });
    return response.data;
  },
  unfollow: async (id: string) => {
    const response = await apiClient.delete(`/activity/follows/${id}/`);
    return response.data;
  },
};

// ============ Dashboard Widgets API ============
export interface DashboardWidget {
  id: string;
  name: string;
  description: string;
  widget_type: string;
  data_source: string;
  query_params: Record<string, unknown>;
  size: string;
  color_scheme: string;
  icon: string;
  chart_config: Record<string, unknown>;
  value_format: string;
  value_prefix: string;
  value_suffix: string;
  refresh_interval: number;
  is_public: boolean;
  created_at: string;
}

export interface DashboardWidgetPlacement {
  id: string;
  widget: DashboardWidget;
  x: number;
  y: number;
  width: number;
  height: number;
  is_visible: boolean;
}

export interface UserDashboard {
  id: string;
  name: string;
  description: string;
  layout_config: Record<string, unknown>;
  is_default: boolean;
  widget_placements: DashboardWidgetPlacement[];
  created_at: string;
}

export const dashboardWidgetsAPI = {
  listWidgets: async () => {
    const response = await apiClient.get('/v1/widgets/');
    return response.data;
  },
  getWidget: async (id: string) => {
    const response = await apiClient.get(`/v1/widgets/${id}/`);
    return response.data;
  },
  createWidget: async (data: Partial<DashboardWidget>) => {
    const response = await apiClient.post('/v1/widgets/', data);
    return response.data;
  },
  updateWidget: async (id: string, data: Partial<DashboardWidget>) => {
    const response = await apiClient.patch(`/v1/widgets/${id}/`, data);
    return response.data;
  },
  deleteWidget: async (id: string) => {
    const response = await apiClient.delete(`/v1/widgets/${id}/`);
    return response.data;
  },
  getWidgetData: async (id: string) => {
    const response = await apiClient.get(`/v1/widgets/${id}/data/`);
    return response.data;
  },
  listDashboards: async () => {
    const response = await apiClient.get('/v1/dashboards/');
    return response.data;
  },
  getDashboard: async (id: string) => {
    const response = await apiClient.get(`/v1/dashboards/${id}/`);
    return response.data;
  },
  createDashboard: async (data: Partial<UserDashboard>) => {
    const response = await apiClient.post('/v1/dashboards/', data);
    return response.data;
  },
  updateDashboard: async (id: string, data: Partial<UserDashboard>) => {
    const response = await apiClient.patch(`/v1/dashboards/${id}/`, data);
    return response.data;
  },
  deleteDashboard: async (id: string) => {
    const response = await apiClient.delete(`/v1/dashboards/${id}/`);
    return response.data;
  },
  updatePlacement: async (dashboardId: string, placements: Partial<DashboardWidgetPlacement>[]) => {
    const response = await apiClient.post(`/v1/dashboards/${dashboardId}/update_layout/`, {
      placements,
    });
    return response.data;
  },
  addWidgetToDashboard: async (dashboardId: string, widgetId: string, placement: { x: number; y: number; width: number; height: number }) => {
    const response = await apiClient.post(`/v1/dashboards/${dashboardId}/add_widget/`, {
      widget_id: widgetId,
      ...placement,
    });
    return response.data;
  },
  removeWidgetFromDashboard: async (dashboardId: string, placementId: string) => {
    const response = await apiClient.delete(`/v1/dashboards/${dashboardId}/remove_widget/${placementId}/`);
    return response.data;
  },
};

// ============ Global Search API ============
export interface SearchResult {
  id: string;
  entity_type: string;
  title: string;
  subtitle?: string;
  description?: string;
  url: string;
  score: number;
  highlights: Record<string, string[]>;
  created_at: string;
  metadata?: Record<string, any>;
}

export interface SearchFilters {
  types?: string[];
  entity_types?: string[];
  date_from?: string;
  date_to?: string;
  date_range?: string;
  owner?: number;
  status?: string[];
}

export interface SavedSearch {
  id: string;
  name: string;
  query: string;
  filters: SearchFilters;
  created_at: string;
}

export const globalSearchAPI = {
  search: async (query: string, filters?: SearchFilters, page?: number, pageSize?: number) => {
    const response = await apiClient.get('/v1/search/', {
      params: { q: query, ...filters, page, page_size: pageSize },
    });
    return response.data;
  },
  quickSearch: async (query: string, limit?: number) => {
    const response = await apiClient.get('/v1/search/quick/', {
      params: { q: query, limit: limit || 10 },
    });
    return response.data;
  },
  suggest: async (query: string) => {
    const response = await apiClient.get('/v1/search/suggest/', {
      params: { q: query },
    });
    return response.data;
  },
  listSavedSearches: async () => {
    const response = await apiClient.get('/v1/saved-searches/');
    return response.data;
  },
  saveSearch: async (data: { name: string; query: string; filters: SearchFilters }) => {
    const response = await apiClient.post('/v1/saved-searches/', data);
    return response.data;
  },
  deleteSavedSearch: async (id: string) => {
    const response = await apiClient.delete(`/v1/saved-searches/${id}/`);
    return response.data;
  },
};

// ============ Developer/Webhooks API ============
export interface Webhook {
  id: string;
  name: string;
  url: string;
  events: string[];
  secret?: string;
  is_active: boolean;
  last_triggered_at?: string;
  consecutive_failures: number;
  created_at: string;
}

export interface APIKey {
  id: string;
  name: string;
  key_prefix: string;
  scopes: string[];
  last_used_at?: string;
  expires_at?: string;
  is_active: boolean;
  created_at: string;
}

export const developerAPI = {
  listAPIKeys: async () => {
    const response = await apiClient.get('/v1/api-keys/');
    return response.data;
  },
  createAPIKey: async (data: { name: string; scopes: string[]; expires_at?: string }) => {
    const response = await apiClient.post('/v1/api-keys/', data);
    return response.data;
  },
  revokeAPIKey: async (id: string) => {
    const response = await apiClient.post(`/v1/api-keys/${id}/revoke/`);
    return response.data;
  },
  listWebhooks: async () => {
    const response = await apiClient.get('/v1/webhooks/');
    return response.data;
  },
  createWebhook: async (data: Partial<Webhook>) => {
    const response = await apiClient.post('/v1/webhooks/', data);
    return response.data;
  },
  updateWebhook: async (id: string, data: Partial<Webhook>) => {
    const response = await apiClient.patch(`/v1/webhooks/${id}/`, data);
    return response.data;
  },
  deleteWebhook: async (id: string) => {
    const response = await apiClient.delete(`/v1/webhooks/${id}/`);
    return response.data;
  },
  testWebhook: async (id: string) => {
    const response = await apiClient.post(`/v1/webhooks/${id}/test/`);
    return response.data;
  },
  listDeliveries: async (webhookId: string) => {
    const response = await apiClient.get(`/v1/webhooks/${webhookId}/deliveries/`);
    return response.data;
  },
};

// Export all enterprise APIs
export const enterpriseAPI = {
  core: coreAPI,
  ai: aiAPI,
  notifications: notificationsAPI,
  customFields: customFieldsAPI,
  activityTimeline: activityTimelineAPI,
  dashboardWidgets: dashboardWidgetsAPI,
  globalSearch: globalSearchAPI,
  developer: developerAPI,
};
