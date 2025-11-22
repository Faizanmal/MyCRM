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

          originalRequest.headers.Authorization = `Bearer ${access}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// ==================== Integration Hub API ====================
export const integrationHubAPI = {
  // Integration Providers
  getProviders: (params?: Record<string, unknown>) => 
    apiClient.get('/v1/integration-hub/providers/', { params }),
  getProvider: (id: string) => 
    apiClient.get(`/v1/integration-hub/providers/${id}/`),
  
  // Integrations
  getIntegrations: (params?: Record<string, unknown>) => 
    apiClient.get('/v1/integration-hub/integrations/', { params }),
  getIntegration: (id: string) => 
    apiClient.get(`/v1/integration-hub/integrations/${id}/`),
  createIntegration: (data: Record<string, unknown>) => 
    apiClient.post('/v1/integration-hub/integrations/', data),
  updateIntegration: (id: string, data: Record<string, unknown>) => 
    apiClient.patch(`/v1/integration-hub/integrations/${id}/`, data),
  deleteIntegration: (id: string) => 
    apiClient.delete(`/v1/integration-hub/integrations/${id}/`),
  
  // Integration Actions
  initiateAuth: (id: string) => 
    apiClient.post(`/v1/integration-hub/integrations/${id}/initiate_auth/`),
  testConnection: (id: string) => 
    apiClient.post(`/v1/integration-hub/integrations/${id}/test_connection/`),
  syncNow: (id: string) => 
    apiClient.post(`/v1/integration-hub/integrations/${id}/sync_now/`),
  getLogs: (id: string, params?: Record<string, unknown>) => 
    apiClient.get(`/v1/integration-hub/integrations/${id}/logs/`, { params }),
  
  // Field Mappings
  getFieldMappings: (integrationId: string) => 
    apiClient.get('/v1/integration-hub/field-mappings/', { params: { integration: integrationId } }),
  createFieldMapping: (data: Record<string, unknown>) => 
    apiClient.post('/v1/integration-hub/field-mappings/', data),
  updateFieldMapping: (id: string, data: Record<string, unknown>) => 
    apiClient.patch(`/v1/integration-hub/field-mappings/${id}/`, data),
  deleteFieldMapping: (id: string) => 
    apiClient.delete(`/v1/integration-hub/field-mappings/${id}/`),
  
  // Sync History
  getSyncHistory: (params?: Record<string, unknown>) => 
    apiClient.get('/v1/integration-hub/sync-history/', { params }),
  getSyncDetails: (id: string) => 
    apiClient.get(`/v1/integration-hub/sync-history/${id}/`),
  retrySyncRecord: (id: string, recordId: string) => 
    apiClient.post(`/v1/integration-hub/sync-history/${id}/retry_record/`, { record_id: recordId }),
};

// ==================== AI Insights API ====================
export const aiInsightsAPI = {
  // Churn Predictions
  getChurnPredictions: (params?: Record<string, unknown>) => 
    apiClient.get('/v1/ai-insights/churn-predictions/', { params }),
  getChurnPrediction: (id: string) => 
    apiClient.get(`/v1/ai-insights/churn-predictions/${id}/`),
  predictChurn: (contactId: string) => 
    apiClient.post('/v1/ai-insights/churn-predictions/', { contact_id: contactId }),
  bulkPredictChurn: () => 
    apiClient.post('/v1/ai-insights/churn-predictions/bulk_predict/'),
  getChurnStatistics: () => 
    apiClient.get('/v1/ai-insights/churn-predictions/statistics/'),
  getHighRiskContacts: () => 
    apiClient.get('/v1/ai-insights/churn-predictions/high_risk/'),
  
  // Next Best Actions
  getNextBestActions: (params?: Record<string, unknown>) => 
    apiClient.get('/v1/ai-insights/next-best-actions/', { params }),
  getNextBestAction: (id: string) => 
    apiClient.get(`/v1/ai-insights/next-best-actions/${id}/`),
  generateActions: (contactId: string) => 
    apiClient.post('/v1/ai-insights/next-best-actions/', { contact_id: contactId }),
  completeAction: (id: string) => 
    apiClient.post(`/v1/ai-insights/next-best-actions/${id}/complete/`),
  dismissAction: (id: string) => 
    apiClient.post(`/v1/ai-insights/next-best-actions/${id}/dismiss/`),
  getActionsByPriority: (priority: string) => 
    apiClient.get(`/v1/ai-insights/next-best-actions/by_priority/?priority=${priority}`),
  
  // AI Generated Content
  getGeneratedContent: (params?: Record<string, unknown>) => 
    apiClient.get('/v1/ai-insights/generated-content/', { params }),
  getContentItem: (id: string) => 
    apiClient.get(`/v1/ai-insights/generated-content/${id}/`),
  generateContent: (data: {
    content_type: string;
    context: Record<string, unknown>;
    tone?: string;
    length?: string;
  }) => apiClient.post('/v1/ai-insights/generated-content/', data),
  regenerateContent: (id: string, tone?: string) => 
    apiClient.post(`/v1/ai-insights/generated-content/${id}/regenerate/`, { tone }),
  approveContent: (id: string) => 
    apiClient.post(`/v1/ai-insights/generated-content/${id}/approve/`),
  
  // Sentiment Analysis
  getSentimentAnalysis: (params?: Record<string, unknown>) => 
    apiClient.get('/v1/ai-insights/sentiment-analysis/', { params }),
  analyzeSentiment: (data: {
    text: string;
    source_type?: string;
    source_id?: string;
  }) => apiClient.post('/v1/ai-insights/sentiment-analysis/', data),
  getSentimentTrends: (params?: Record<string, unknown>) => 
    apiClient.get('/v1/ai-insights/sentiment-analysis/trends/', { params }),
};

// ==================== Gamification API ====================
export const gamificationAPI = {
  // Achievements
  getAchievements: (params?: Record<string, unknown>) => 
    apiClient.get('/v1/gamification/achievements/', { params }),
  getAchievement: (id: string) => 
    apiClient.get(`/v1/gamification/achievements/${id}/`),
  getMyAchievements: () => 
    apiClient.get('/v1/gamification/achievements/my_achievements/'),
  getAchievementProgress: (id: string) => 
    apiClient.get(`/v1/gamification/achievements/${id}/progress/`),
  
  // User Points
  getUserPoints: (params?: Record<string, unknown>) => 
    apiClient.get('/v1/gamification/user-points/', { params }),
  getMyPoints: () => 
    apiClient.get('/v1/gamification/user-points/my_points/'),
  getPointsHistory: (userId?: string) => 
    apiClient.get('/v1/gamification/user-points/points_history/', { 
      params: userId ? { user_id: userId } : {} 
    }),
  
  // Leaderboards
  getLeaderboards: (params?: Record<string, unknown>) => 
    apiClient.get('/v1/gamification/leaderboards/', { params }),
  getLeaderboard: (id: string) => 
    apiClient.get(`/v1/gamification/leaderboards/${id}/`),
  getLeaderboardRankings: (id: string) => 
    apiClient.get(`/v1/gamification/leaderboards/${id}/rankings/`),
  getMyRanking: (id: string) => 
    apiClient.get(`/v1/gamification/leaderboards/${id}/my_ranking/`),
  
  // Challenges
  getChallenges: (params?: Record<string, unknown>) => 
    apiClient.get('/v1/gamification/challenges/', { params }),
  getChallenge: (id: string) => 
    apiClient.get(`/v1/gamification/challenges/${id}/`),
  getMyChallenges: () => 
    apiClient.get('/v1/gamification/challenges/my_challenges/'),
  joinChallenge: (id: string) => 
    apiClient.post(`/v1/gamification/challenges/${id}/join/`),
  leaveChallenge: (id: string) => 
    apiClient.post(`/v1/gamification/challenges/${id}/leave/`),
  getActiveTeamChallenges: () => 
    apiClient.get('/v1/gamification/challenges/active_team_challenges/'),
  
  // Point Transactions
  getPointTransactions: (params?: Record<string, unknown>) => 
    apiClient.get('/v1/gamification/point-transactions/', { params }),
  getMyTransactions: () => 
    apiClient.get('/v1/gamification/point-transactions/my_transactions/'),
};

// TypeScript Interfaces
export interface IntegrationProvider {
  id: string;
  name: string;
  slug: string;
  description: string;
  logo_url?: string;
  auth_type: 'oauth2' | 'api_key' | 'basic';
  is_active: boolean;
  supported_features: string[];
}

export interface Integration {
  id: string;
  provider: IntegrationProvider;
  name: string;
  is_active: boolean;
  status: 'pending' | 'connected' | 'error' | 'disconnected';
  auth_data: Record<string, unknown>;
  config: Record<string, unknown>;
  last_sync_at?: string;
  next_sync_at?: string;
  sync_frequency: number;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface ChurnPrediction {
  id: string;
  contact: {
    id: string;
    name: string;
    email: string;
  };
  churn_probability: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  contributing_factors: Record<string, unknown>;
  recommended_actions: string[];
  prediction_date: string;
  model_version: string;
}

export interface NextBestAction {
  id: string;
  contact: {
    id: string;
    name: string;
    email: string;
  };
  action_type: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  title: string;
  description: string;
  reasoning: string;
  estimated_impact: number;
  status: 'pending' | 'completed' | 'dismissed';
  due_date?: string;
  created_at: string;
}

export interface AIGeneratedContent {
  id: string;
  content_type: string;
  content: string;
  context: Record<string, unknown>;
  tone: string;
  length: string;
  status: 'draft' | 'approved' | 'rejected';
  model_used: string;
  generation_time: number;
  created_at: string;
}

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: string;
  difficulty: 'easy' | 'medium' | 'hard' | 'legendary';
  points: number;
  criteria: Record<string, unknown>;
  is_active: boolean;
  is_repeatable: boolean;
  earned_by_count: number;
}

export interface UserPoints {
  id: string;
  user: {
    id: string;
    username: string;
    email: string;
  };
  total_points: number;
  current_level: number;
  points_to_next_level: number;
  streak_days: number;
  longest_streak: number;
  achievements_count: number;
  rank?: number;
}

export interface Leaderboard {
  id: string;
  name: string;
  description: string;
  metric_type: 'points' | 'deals_closed' | 'revenue' | 'tasks_completed' | 'custom';
  time_period: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly' | 'all_time';
  is_active: boolean;
  created_at: string;
}

export interface Challenge {
  id: string;
  name: string;
  description: string;
  challenge_type: 'individual' | 'team';
  goal_type: string;
  goal_value: number;
  start_date: string;
  end_date: string;
  reward_points: number;
  status: 'upcoming' | 'active' | 'completed' | 'cancelled';
  participants_count: number;
  is_participating?: boolean;
}

export default apiClient;
