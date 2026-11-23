/**
 * Product Positioning, ICP, JTBD, and Buyer Tasks API Client
 */
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export interface BuyerTaskItem {
  key: string;
  title: string;
  description: string;
  completed: boolean;
}

export interface ProductPositioningData {
  id?: string;
  organization?: string;
  organization_name?: string;
  target_market: string;
  ideal_customer_profile: string;
  team_size_tier: string;
  primary_jtbd: string;
  buyer_tasks_completed?: string[];
  all_tasks?: BuyerTaskItem[];
  completion_percentage?: number;
  value_metrics?: Record<string, number | string>;
  onboarding_status?: 'pending' | 'in_progress' | 'completed' | 'skipped';
  activated_features?: string[];
  completed_at?: string | null;
}

export interface ValueMetricsResponse {
  hours_saved_monthly: number;
  win_rate_percentage: number;
  administrative_time_reduction_pct: number;
  pipeline_velocity_days: number;
  active_leads_count: number;
  active_opportunities_count: number;
  tenant_sla_uptime_pct: number;
  api_average_latency_ms: number;
}

export interface PrioritizedSpecItem {
  priority: 'P0' | 'P1' | 'P2';
  capability: string;
  target_user_outcome: string;
  status: 'shipped' | 'active' | 'in_development' | 'planned';
  metrics: string;
}

export interface ProductSpecResponse {
  product_name: string;
  strategic_vision: string;
  prioritized_roadmap: PrioritizedSpecItem[];
}

const getHeaders = () => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  };
};

export const productPositioningApi = {
  /**
   * Fetch current tenant product positioning profile
   */
  getProfile: async (): Promise<ProductPositioningData> => {
    const res = await axios.get(`${API_BASE_URL}/v1/product-position/`, { headers: getHeaders() });
    return res.data;
  },

  /**
   * Update tenant ICP, JTBD, and market positioning
   */
  updateProfile: async (data: Partial<ProductPositioningData>): Promise<ProductPositioningData> => {
    const res = await axios.post(`${API_BASE_URL}/v1/product-position/`, data, { headers: getHeaders() });
    return res.data;
  },

  /**
   * Complete one of the 5 buyer tasks
   */
  completeBuyerTask: async (taskKey: string, metadata: Record<string, any> = {}): Promise<{
    status: string;
    task_key: string;
    buyer_tasks_completed: string[];
    completion_percentage: number;
    onboarding_status: string;
  }> => {
    const res = await axios.post(
      `${API_BASE_URL}/v1/product-position/complete-task/`,
      { task_key: taskKey, metadata },
      { headers: getHeaders() }
    );
    return res.data;
  },

  /**
   * Get the prioritized product roadmap and specs
   */
  getProductSpec: async (): Promise<ProductSpecResponse> => {
    const res = await axios.get(`${API_BASE_URL}/v1/product-position/spec/`, { headers: getHeaders() });
    return res.data;
  },

  /**
   * Get tenant live value metrics
   */
  getValueMetrics: async (): Promise<ValueMetricsResponse> => {
    const res = await axios.get(`${API_BASE_URL}/v1/product-position/metrics/`, { headers: getHeaders() });
    return res.data;
  }
};
