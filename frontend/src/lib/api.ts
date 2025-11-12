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
      } catch (_refreshError: unknown) {
        // Refresh failed, redirect to login
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

  create: async (meetingData: Record<string, unknown>) => {
    const response = await apiClient.post('/meetings/meetings/', meetingData);
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

export default apiClient;