/**
 * MyCRM Core Type Definitions
 *
 * Comprehensive TypeScript types for the MyCRM platform.
 * This file provides type safety across the frontend application.
 */

// ============================================================================
// Base Types
// ============================================================================

export type UUID = string;
export type ISODateString = string;
export type Currency = 'USD' | 'EUR' | 'GBP' | 'CAD' | 'AUD' | 'JPY' | 'CNY';

export interface Timestamps {
  created_at: ISODateString;
  updated_at: ISODateString;
}

export interface SoftDeletable {
  is_deleted: boolean;
  deleted_at?: ISODateString;
}

export interface Auditable {
  created_by?: UUID;
  modified_by?: UUID;
}

export interface Ownable {
  owner_id?: UUID;
  owner?: User;
}

// ============================================================================
// Pagination & API Response Types
// ============================================================================

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
  ordering?: string;
}

export interface SearchParams extends PaginationParams {
  search?: string;
  [key: string]: unknown;
}

export interface APIResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface APIError {
  message: string;
  code: string;
  details?: Record<string, string[]>;
}

// ============================================================================
// Authentication Types
// ============================================================================

export interface User {
  id: UUID;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone?: string;
  avatar_url?: string;
  role: UserRole;
  job_title?: string;
  department?: string;
  timezone: string;
  locale: string;
  organization_id: UUID;
  organization?: Organization;
  team_id?: UUID;
  team?: Team;
  manager_id?: UUID;
  manager?: User;
  is_active: boolean;
  is_staff: boolean;
  mfa_enabled: boolean;
  last_login?: ISODateString;
  created_at: ISODateString;
  updated_at: ISODateString;
}

export type UserRole =
  | 'super_admin'
  | 'admin'
  | 'manager'
  | 'sales_rep'
  | 'marketing'
  | 'readonly';

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
  mfa_code?: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  organization_name?: string;
  invite_code?: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirm {
  token: string;
  password: string;
  password_confirm: string;
}

export interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// ============================================================================
// Organization Types
// ============================================================================

export interface Organization {
  id: UUID;
  name: string;
  slug: string;
  logo_url?: string;
  plan: OrganizationPlan;
  settings: OrganizationSettings;
  is_active: boolean;
  created_at: ISODateString;
  updated_at: ISODateString;
}

export type OrganizationPlan = 'starter' | 'professional' | 'enterprise';

export interface OrganizationSettings {
  default_currency: Currency;
  default_timezone: string;
  date_format: string;
  enable_email_tracking: boolean;
  enable_call_recording: boolean;
  enable_ai_features: boolean;
  custom_fields: CustomFieldDefinition[];
}

export interface Team {
  id: UUID;
  name: string;
  description?: string;
  organization_id: UUID;
  lead_id?: UUID;
  lead?: User;
  members?: User[];
  created_at: ISODateString;
  updated_at: ISODateString;
}

// ============================================================================
// Contact Types
// ============================================================================

export interface Contact extends Timestamps, SoftDeletable, Auditable, Ownable {
  id: UUID;
  first_name: string;
  last_name: string;
  full_name: string;
  email?: string;
  phone?: string;
  mobile?: string;
  company?: string;
  job_title?: string;
  department?: string;
  website?: string;
  linkedin_url?: string;
  twitter_handle?: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  status: ContactStatus;
  source?: LeadSource;
  lifecycle_stage: LifecycleStage;
  tags: Tag[];
  custom_fields: Record<string, unknown>;
  score: number;
  assigned_to_id?: UUID;
  assigned_to?: User;
  organization_id: UUID;
  company_id?: UUID;
  company_entity?: Company;
  last_activity_at?: ISODateString;
}

export type ContactStatus = 'active' | 'inactive' | 'archived';

export type LifecycleStage =
  | 'subscriber'
  | 'lead'
  | 'marketing_qualified'
  | 'sales_qualified'
  | 'opportunity'
  | 'customer'
  | 'evangelist';

export interface ContactCreatePayload {
  first_name: string;
  last_name: string;
  email?: string;
  phone?: string;
  company?: string;
  job_title?: string;
  source?: LeadSource;
  owner_id?: UUID;
  tags?: string[];
  custom_fields?: Record<string, unknown>;
}

export interface ContactUpdatePayload extends Partial<ContactCreatePayload> {
  status?: ContactStatus;
  lifecycle_stage?: LifecycleStage;
}

export interface ContactFilters {
  status?: ContactStatus;
  lifecycle_stage?: LifecycleStage;
  owner_id?: UUID;
  company?: string;
  tags?: string[];
  created_after?: ISODateString;
  created_before?: ISODateString;
  score_min?: number;
  score_max?: number;
}

// ============================================================================
// Company (Account) Types
// ============================================================================

export interface Company extends Timestamps, SoftDeletable, Ownable {
  id: UUID;
  name: string;
  domain?: string;
  industry?: string;
  company_size?: CompanySize;
  annual_revenue?: number;
  founded_year?: number;
  description?: string;
  logo_url?: string;
  website?: string;
  linkedin_url?: string;
  address_line1?: string;
  city?: string;
  state?: string;
  country?: string;
  phone?: string;
  employee_count?: number;
  type: CompanyType;
  tier?: CompanyTier;
  health_score?: number;
  organization_id: UUID;
  custom_fields: Record<string, unknown>;
  contacts_count?: number;
  opportunities_count?: number;
  total_revenue?: number;
}

export type CompanySize =
  | '1-10'
  | '11-50'
  | '51-200'
  | '201-500'
  | '501-1000'
  | '1001-5000'
  | '5001+';

export type CompanyType =
  | 'prospect'
  | 'customer'
  | 'partner'
  | 'competitor'
  | 'vendor'
  | 'other';

export type CompanyTier = 'enterprise' | 'mid_market' | 'smb' | 'startup';

// ============================================================================
// Lead Types
// ============================================================================

export interface Lead extends Timestamps, SoftDeletable, Ownable {
  id: UUID;
  name: string;
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  company?: string;
  job_title?: string;
  website?: string;
  source: LeadSource;
  source_detail?: string;
  status: LeadStatus;
  substatus?: string;
  score: number;
  score_breakdown?: LeadScoreBreakdown;
  grade?: LeadGrade;
  estimated_value?: number;
  probability?: number;
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
  referrer_url?: string;
  landing_page?: string;
  notes?: string;
  tags: Tag[];
  custom_fields: Record<string, unknown>;
  assigned_to_id?: UUID;
  assigned_to?: User;
  converted_contact_id?: UUID;
  converted_contact?: Contact;
  converted_opportunity_id?: UUID;
  campaign_id?: UUID;
  organization_id: UUID;
  last_activity_at?: ISODateString;
  first_responded_at?: ISODateString;
  qualified_at?: ISODateString;
  converted_at?: ISODateString;
}

export type LeadSource =
  | 'website'
  | 'referral'
  | 'cold_call'
  | 'cold_email'
  | 'event'
  | 'social'
  | 'paid_ads'
  | 'organic'
  | 'partner'
  | 'other';

export type LeadStatus =
  | 'new'
  | 'contacted'
  | 'engaged'
  | 'qualified'
  | 'converted'
  | 'disqualified'
  | 'nurturing';

export type LeadGrade = 'A' | 'B' | 'C' | 'D' | 'F';

export interface LeadScoreBreakdown {
  engagement: number;
  fit: number;
  intent: number;
  timing: number;
  budget: number;
}

export interface LeadConvertPayload {
  create_contact: boolean;
  create_opportunity: boolean;
  opportunity_name?: string;
  opportunity_value?: number;
  opportunity_stage_id?: UUID;
  owner_id?: UUID;
}

// ============================================================================
// Opportunity Types
// ============================================================================

export interface Opportunity extends Timestamps, SoftDeletable, Ownable {
  id: UUID;
  name: string;
  description?: string;
  value: number;
  currency: Currency;
  probability: number;
  weighted_value: number;
  expected_close_date?: string;
  actual_close_date?: string;
  stage_id: UUID;
  stage?: PipelineStage;
  pipeline_id: UUID;
  pipeline?: Pipeline;
  contact_id?: UUID;
  contact?: Contact;
  company_id?: UUID;
  company?: Company;
  lead_id?: UUID;
  lead?: Lead;
  status: OpportunityStatus;
  loss_reason?: string;
  competitor?: string;
  next_step?: string;
  tags: Tag[];
  custom_fields: Record<string, unknown>;
  organization_id: UUID;
  last_activity_at?: ISODateString;
  days_in_stage: number;
  stage_changed_at?: ISODateString;
}

export type OpportunityStatus = 'open' | 'won' | 'lost';

export interface Pipeline {
  id: UUID;
  name: string;
  description?: string;
  is_default: boolean;
  is_active: boolean;
  organization_id: UUID;
  stages?: PipelineStage[];
  created_at: ISODateString;
  updated_at: ISODateString;
}

export interface PipelineStage {
  id: UUID;
  name: string;
  probability: number;
  order: number;
  color: string;
  description?: string;
  is_won: boolean;
  is_lost: boolean;
  pipeline_id: UUID;
  organization_id: UUID;
  opportunities_count?: number;
  opportunities_value?: number;
}

export interface OpportunityCreatePayload {
  name: string;
  value: number;
  currency?: Currency;
  pipeline_id: UUID;
  stage_id: UUID;
  expected_close_date?: string;
  contact_id?: UUID;
  company_id?: UUID;
  owner_id?: UUID;
  description?: string;
  tags?: string[];
}

export interface OpportunityMovePayload {
  stage_id: UUID;
  status?: OpportunityStatus;
  loss_reason?: string;
  competitor?: string;
}

// ============================================================================
// Task Types
// ============================================================================

export interface Task extends Timestamps {
  id: UUID;
  title: string;
  description?: string;
  task_type: TaskType;
  priority: TaskPriority;
  status: TaskStatus;
  due_date?: ISODateString;
  reminder_at?: ISODateString;
  completed_at?: ISODateString;
  outcome?: string;
  notes?: string;
  assigned_to_id?: UUID;
  assigned_to?: User;
  created_by_id: UUID;
  created_by?: User;
  contact_id?: UUID;
  contact?: Contact;
  lead_id?: UUID;
  lead?: Lead;
  opportunity_id?: UUID;
  opportunity?: Opportunity;
  company_id?: UUID;
  company?: Company;
  organization_id: UUID;
  is_recurring: boolean;
  recurrence_rule?: string;
  parent_task_id?: UUID;
}

export type TaskType =
  | 'call'
  | 'email'
  | 'meeting'
  | 'follow_up'
  | 'demo'
  | 'proposal'
  | 'other';

export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';

export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled';

export interface TaskCreatePayload {
  title: string;
  description?: string;
  task_type: TaskType;
  priority?: TaskPriority;
  due_date?: ISODateString;
  reminder_at?: ISODateString;
  assigned_to_id?: UUID;
  contact_id?: UUID;
  lead_id?: UUID;
  opportunity_id?: UUID;
}

// ============================================================================
// Activity & Note Types
// ============================================================================

export interface Activity extends Timestamps {
  id: UUID;
  activity_type: ActivityType;
  subject: string;
  description?: string;
  outcome?: string;
  duration_minutes?: number;
  occurred_at: ISODateString;
  user_id: UUID;
  user?: User;
  contact_id?: UUID;
  contact?: Contact;
  lead_id?: UUID;
  opportunity_id?: UUID;
  company_id?: UUID;
  organization_id: UUID;
  metadata: Record<string, unknown>;
}

export type ActivityType =
  | 'call'
  | 'email'
  | 'meeting'
  | 'note'
  | 'task_completed'
  | 'stage_change'
  | 'deal_won'
  | 'deal_lost'
  | 'lifecycle_change'
  | 'document_sent'
  | 'document_signed';

export interface Note extends Timestamps, Auditable {
  id: UUID;
  content: string;
  is_pinned: boolean;
  contact_id?: UUID;
  lead_id?: UUID;
  opportunity_id?: UUID;
  company_id?: UUID;
  organization_id: UUID;
}

// ============================================================================
// Communication Types
// ============================================================================

export interface EmailTracking {
  id: UUID;
  subject: string;
  body_preview?: string;
  from_email: string;
  to_email: string;
  message_id: string;
  thread_id?: string;
  sent_at: ISODateString;
  opened_at?: ISODateString;
  open_count: number;
  clicked_at?: ISODateString;
  click_count: number;
  replied_at?: ISODateString;
  bounced_at?: ISODateString;
  bounce_type?: 'hard' | 'soft';
  status: EmailStatus;
  contact_id?: UUID;
  lead_id?: UUID;
  opportunity_id?: UUID;
  user_id: UUID;
  sequence_id?: UUID;
  sequence_step?: number;
  organization_id: UUID;
  created_at: ISODateString;
}

export type EmailStatus =
  | 'draft'
  | 'scheduled'
  | 'sending'
  | 'sent'
  | 'delivered'
  | 'opened'
  | 'clicked'
  | 'replied'
  | 'bounced'
  | 'failed';

export interface EmailSequence {
  id: UUID;
  name: string;
  description?: string;
  status: 'draft' | 'active' | 'paused' | 'archived';
  steps: EmailSequenceStep[];
  enrolled_count: number;
  completed_count: number;
  organization_id: UUID;
  created_at: ISODateString;
  updated_at: ISODateString;
}

export interface EmailSequenceStep {
  id: UUID;
  order: number;
  subject: string;
  body: string;
  delay_days: number;
  delay_hours: number;
  sequence_id: UUID;
}

// ============================================================================
// Analytics Types
// ============================================================================

export interface DashboardMetrics {
  contacts: {
    total: number;
    active: number;
    created_this_month: number;
    growth_percentage: number;
  };
  leads: {
    total: number;
    new: number;
    qualified: number;
    conversion_rate: number;
  };
  opportunities: {
    total_open: number;
    total_value: number;
    weighted_value: number;
    won_this_month: number;
    lost_this_month: number;
    win_rate: number;
  };
  tasks: {
    overdue: number;
    due_today: number;
    due_this_week: number;
    completed_this_week: number;
  };
  activities: {
    calls_today: number;
    emails_sent_today: number;
    meetings_scheduled: number;
  };
}

export interface PipelineAnalytics {
  pipeline_id: UUID;
  pipeline_name: string;
  stages: StageAnalytics[];
  total_value: number;
  weighted_value: number;
  opportunities_count: number;
  average_deal_size: number;
  average_sales_cycle_days: number;
  win_rate: number;
}

export interface StageAnalytics {
  stage_id: UUID;
  stage_name: string;
  opportunities_count: number;
  total_value: number;
  average_days_in_stage: number;
  conversion_rate: number;
}

export interface LeadSourceAnalytics {
  source: LeadSource;
  leads_count: number;
  converted_count: number;
  conversion_rate: number;
  total_value: number;
  average_score: number;
}

export interface TeamPerformance {
  user_id: UUID;
  user_name: string;
  avatar_url?: string;
  deals_won: number;
  deals_lost: number;
  revenue_won: number;
  activities_count: number;
  tasks_completed: number;
  win_rate: number;
  rank: number;
}

// ============================================================================
// Utility Types
// ============================================================================

export interface Tag {
  id: UUID;
  name: string;
  color: string;
  organization_id: UUID;
}

export interface CustomFieldDefinition {
  id: UUID;
  name: string;
  field_key: string;
  field_type: CustomFieldType;
  entity_type: 'contact' | 'lead' | 'opportunity' | 'company';
  is_required: boolean;
  default_value?: unknown;
  options?: string[];
  order: number;
}

export type CustomFieldType =
  | 'text'
  | 'number'
  | 'email'
  | 'phone'
  | 'url'
  | 'date'
  | 'datetime'
  | 'boolean'
  | 'select'
  | 'multiselect'
  | 'textarea';

export interface AuditLog {
  id: UUID;
  action: string;
  entity_type: string;
  entity_id: UUID;
  old_values?: Record<string, unknown>;
  new_values?: Record<string, unknown>;
  user_id: UUID;
  user?: User;
  ip_address?: string;
  user_agent?: string;
  organization_id: UUID;
  created_at: ISODateString;
}

// ============================================================================
// Form Types
// ============================================================================

export interface FormField<T = unknown> {
  value: T;
  error?: string;
  touched: boolean;
  dirty: boolean;
}

export interface FormState<T extends Record<string, unknown>> {
  values: T;
  errors: Partial<Record<keyof T, string>>;
  touched: Partial<Record<keyof T, boolean>>;
  isSubmitting: boolean;
  isValid: boolean;
}

// ============================================================================
// Notification Types
// ============================================================================

export interface Notification {
  id: UUID;
  type: NotificationType;
  title: string;
  message: string;
  link?: string;
  is_read: boolean;
  user_id: UUID;
  created_at: ISODateString;
}

export type NotificationType =
  | 'task_due'
  | 'task_assigned'
  | 'deal_won'
  | 'deal_lost'
  | 'lead_assigned'
  | 'email_opened'
  | 'email_replied'
  | 'meeting_reminder'
  | 'mention'
  | 'system';

// ============================================================================
// Export All Types
// ============================================================================
