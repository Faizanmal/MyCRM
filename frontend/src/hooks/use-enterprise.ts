/**
 * Enterprise Hooks for MyCRM
 * ==========================
 * 
 * Custom React hooks for enterprise features:
 * - GraphQL data fetching with React Query
 * - Real-time subscriptions
 * - Optimistic updates
 * - Error handling
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { useMutation, useQuery, useQueryClient, UseQueryOptions } from '@tanstack/react-query';

import graphqlClient, {
  QUERIES,
  MUTATIONS,
  SUBSCRIPTIONS,
  GraphQLRequestError,
} from '@/lib/graphql-client';

// =============================================================================
// Types
// =============================================================================

export interface Lead {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  phone?: string;
  company?: string;
  status: LeadStatus;
  source?: string;
  score: number;
  notes?: string;
  customFields?: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
  assignedTo?: User;
  aiInsights?: LeadInsights;
  activities?: Activity[];
}

export interface LeadInsights {
  id: string;
  conversionProbability: number;
  recommendedActions: string[];
  engagementScore: number;
  bestContactTime?: string;
  sentiment?: string;
  generatedAt: string;
}

export interface Contact {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  phone?: string;
  mobile?: string;
  jobTitle?: string;
  department?: string;
  type: ContactType;
  tags: string[];
  createdAt: string;
  updatedAt: string;
  company?: Company;
}

export interface Company {
  id: string;
  name: string;
  domain?: string;
  industry?: string;
  size?: string;
  website?: string;
}

export interface Opportunity {
  id: string;
  name: string;
  value: number;
  stage: OpportunityStage;
  probability: number;
  expectedCloseDate?: string;
  actualCloseDate?: string;
  description?: string;
  weightedValue: number;
  createdAt: string;
  updatedAt: string;
  contact?: Contact;
  owner?: User;
}

export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  fullName: string;
  isActive: boolean;
  dateJoined: string;
  lastLogin?: string;
}

export interface Activity {
  id: string;
  type: string;
  title: string;
  description?: string;
  relatedToType: string;
  relatedToId: string;
  createdAt: string;
  user?: User;
}

export interface Task {
  id: string;
  title: string;
  description?: string;
  dueDate?: string;
  completedAt?: string;
  priority: TaskPriority;
  isCompleted: boolean;
  assignedTo?: User;
  createdBy?: User;
}

export interface DashboardMetrics {
  totalLeads: number;
  leadsThisMonth: number;
  leadConversionRate: number;
  totalOpportunities: number;
  pipelineValue: number;
  weightedPipeline: number;
  totalContacts: number;
  contactsThisMonth: number;
  wonDealsCount: number;
  wonDealsValue: number;
  tasksDueToday: number;
  overdueTasks: number;
  activitiesThisWeek: number;
}

export interface SalesAnalytics {
  period: string;
  revenue: number;
  dealsWon: number;
  dealsLost: number;
  avgDealSize: number;
  avgSalesCycleDays: number;
  winRate: number;
  pipelineByStage: Record<string, number>;
  revenueBySource: Record<string, number>;
  topPerformers: SalesPerformer[];
}

export interface SalesPerformer {
  user: User;
  dealsWon: number;
  revenue: number;
  conversionRate: number;
}

export interface PageInfo {
  page: number;
  pageSize: number;
  totalPages: number;
  totalCount: number;
  hasNext: boolean;
  hasPrevious: boolean;
}

export interface Connection<T> {
  items: T[];
  pageInfo: PageInfo;
}

export interface MutationResult<T = unknown> {
  success: boolean;
  message?: string;
  errors?: string[];
  lead?: T;
  contact?: T;
  opportunity?: T;
  task?: T;
}

export type LeadStatus =
  | 'NEW'
  | 'CONTACTED'
  | 'QUALIFIED'
  | 'PROPOSAL'
  | 'NEGOTIATION'
  | 'WON'
  | 'LOST';

export type ContactType = 'LEAD' | 'CUSTOMER' | 'PARTNER' | 'VENDOR';

export type OpportunityStage =
  | 'PROSPECTING'
  | 'QUALIFICATION'
  | 'NEEDS_ANALYSIS'
  | 'VALUE_PROPOSITION'
  | 'DECISION_MAKERS'
  | 'PERCEPTION_ANALYSIS'
  | 'PROPOSAL'
  | 'NEGOTIATION'
  | 'CLOSED_WON'
  | 'CLOSED_LOST';

export type TaskPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';

export interface FilterInput {
  search?: string;
  status?: string[];
  source?: string[];
  assignedTo?: string[];
  scoreMin?: number;
  scoreMax?: number;
  createdAt?: { start?: string; end?: string };
}

export interface PaginationInput {
  page?: number;
  pageSize?: number;
}

export interface SortInput {
  field: string;
  direction: 'ASC' | 'DESC';
}

// =============================================================================
// Dashboard Hooks
// =============================================================================

export function useDashboardMetrics(
  options?: Omit<UseQueryOptions<{ dashboardMetrics: DashboardMetrics }>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['dashboardMetrics'],
    queryFn: () => graphqlClient.request<{ dashboardMetrics: DashboardMetrics }>(
      QUERIES.DASHBOARD_METRICS
    ),
    ...options,
  });
}

export function useSalesAnalytics(
  period: string = 'month',
  options?: Omit<UseQueryOptions<{ salesAnalytics: SalesAnalytics }>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['salesAnalytics', period],
    queryFn: () => graphqlClient.request<{ salesAnalytics: SalesAnalytics }>(
      QUERIES.SALES_ANALYTICS,
      { variables: { period } }
    ),
    ...options,
  });
}

// =============================================================================
// Lead Hooks
// =============================================================================

export function useLeads(
  filter?: FilterInput,
  pagination?: PaginationInput,
  sort?: SortInput,
  options?: Omit<UseQueryOptions<{ leads: Connection<Lead> }>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['leads', filter, pagination, sort],
    queryFn: () => graphqlClient.request<{ leads: Connection<Lead> }>(
      QUERIES.GET_LEADS,
      { variables: { filter, pagination, sort } }
    ),
    ...options,
  });
}

export function useLead(
  id: string,
  options?: Omit<UseQueryOptions<{ lead: Lead }>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['lead', id],
    queryFn: () => graphqlClient.request<{ lead: Lead }>(
      QUERIES.GET_LEAD,
      { variables: { id } }
    ),
    enabled: !!id,
    ...options,
  });
}

export function useCreateLead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: Partial<Lead>) =>
      graphqlClient.request<{ createLead: MutationResult<Lead> }>(
        MUTATIONS.CREATE_LEAD,
        { variables: { input } }
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardMetrics'] });
    },
  });
}

export function useUpdateLead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, input }: { id: string; input: Partial<Lead> }) =>
      graphqlClient.request<{ updateLead: MutationResult<Lead> }>(
        MUTATIONS.UPDATE_LEAD,
        { variables: { id, input } }
      ),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
      queryClient.invalidateQueries({ queryKey: ['lead', id] });
    },
  });
}

export function useDeleteLead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) =>
      graphqlClient.request<{ deleteLead: MutationResult }>(
        MUTATIONS.DELETE_LEAD,
        { variables: { id } }
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardMetrics'] });
    },
  });
}

export function useConvertLead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      leadId,
      createOpportunity = false,
      opportunityValue,
    }: {
      leadId: string;
      createOpportunity?: boolean;
      opportunityValue?: number;
    }) =>
      graphqlClient.request<{ convertLeadToContact: MutationResult<Contact> }>(
        MUTATIONS.CONVERT_LEAD,
        { variables: { leadId, createOpportunity, opportunityValue } }
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
      queryClient.invalidateQueries({ queryKey: ['contacts'] });
      queryClient.invalidateQueries({ queryKey: ['opportunities'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardMetrics'] });
    },
  });
}

// =============================================================================
// Contact Hooks
// =============================================================================

export function useContacts(
  filter?: FilterInput,
  pagination?: PaginationInput,
  sort?: SortInput,
  options?: Omit<UseQueryOptions<{ contacts: Connection<Contact> }>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['contacts', filter, pagination, sort],
    queryFn: () => graphqlClient.request<{ contacts: Connection<Contact> }>(
      QUERIES.GET_CONTACTS,
      { variables: { filter, pagination, sort } }
    ),
    ...options,
  });
}

// =============================================================================
// Opportunity Hooks
// =============================================================================

export function useOpportunities(
  filter?: FilterInput,
  pagination?: PaginationInput,
  sort?: SortInput,
  options?: Omit<UseQueryOptions<{ opportunities: Connection<Opportunity> }>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['opportunities', filter, pagination, sort],
    queryFn: () => graphqlClient.request<{ opportunities: Connection<Opportunity> }>(
      QUERIES.GET_OPPORTUNITIES,
      { variables: { filter, pagination, sort } }
    ),
    ...options,
  });
}

// =============================================================================
// Task Hooks
// =============================================================================

export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: Partial<Task>) =>
      graphqlClient.request<{ createTask: MutationResult<Task> }>(
        MUTATIONS.CREATE_TASK,
        { variables: { input } }
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardMetrics'] });
    },
  });
}

export function useCompleteTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) =>
      graphqlClient.request<{ completeTask: MutationResult<Task> }>(
        MUTATIONS.COMPLETE_TASK,
        { variables: { id } }
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardMetrics'] });
    },
  });
}

// =============================================================================
// User Hooks
// =============================================================================

export function useCurrentUser(
  options?: Omit<UseQueryOptions<{ me: User }>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['currentUser'],
    queryFn: () => graphqlClient.request<{ me: User }>(QUERIES.ME),
    staleTime: 10 * 60 * 1000, // 10 minutes
    ...options,
  });
}

// =============================================================================
// Real-time Subscription Hooks
// =============================================================================

export function useLeadUpdates(onUpdate: (lead: Lead) => void) {
  const unsubscribeRef = useRef<(() => void) | null>(null);

  useEffect(() => {
    unsubscribeRef.current = graphqlClient.subscribe<{ leadUpdates: Lead }>({
      query: SUBSCRIPTIONS.LEAD_UPDATES,
      onData: (data) => onUpdate(data.leadUpdates),
      onError: (error) => console.error('Lead subscription error:', error),
    });

    return () => {
      unsubscribeRef.current?.();
    };
  }, [onUpdate]);
}

export function useOpportunityUpdates(onUpdate: (opportunity: Opportunity) => void) {
  const unsubscribeRef = useRef<(() => void) | null>(null);

  useEffect(() => {
    unsubscribeRef.current = graphqlClient.subscribe<{ opportunityUpdates: Opportunity }>({
      query: SUBSCRIPTIONS.OPPORTUNITY_UPDATES,
      onData: (data) => onUpdate(data.opportunityUpdates),
      onError: (error) => console.error('Opportunity subscription error:', error),
    });

    return () => {
      unsubscribeRef.current?.();
    };
  }, [onUpdate]);
}

export function useActivityFeed(onActivity: (activity: Activity) => void) {
  const unsubscribeRef = useRef<(() => void) | null>(null);

  useEffect(() => {
    unsubscribeRef.current = graphqlClient.subscribe<{ activityFeed: Activity }>({
      query: SUBSCRIPTIONS.ACTIVITY_FEED,
      onData: (data) => onActivity(data.activityFeed),
      onError: (error) => console.error('Activity subscription error:', error),
    });

    return () => {
      unsubscribeRef.current?.();
    };
  }, [onActivity]);
}

export function useNotifications(onNotification: (notification: Record<string, unknown>) => void) {
  const unsubscribeRef = useRef<(() => void) | null>(null);

  useEffect(() => {
    unsubscribeRef.current = graphqlClient.subscribe<{ notifications: Record<string, unknown> }>({
      query: SUBSCRIPTIONS.NOTIFICATIONS,
      onData: (data) => onNotification(data.notifications),
      onError: (error) => console.error('Notification subscription error:', error),
    });

    return () => {
      unsubscribeRef.current?.();
    };
  }, [onNotification]);
}

// =============================================================================
// Infinite Query Hooks
// =============================================================================

export function useInfiniteLeads(
  filter?: FilterInput,
  sort?: SortInput
) {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [pageInfo, setPageInfo] = useState<PageInfo | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchLeads = useCallback(
    async (page: number = 1) => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await graphqlClient.request<{ leads: Connection<Lead> }>(
          QUERIES.GET_LEADS,
          { variables: { filter, pagination: { page, pageSize: 20 }, sort } }
        );

        const { items, pageInfo: newPageInfo } = response.leads;

        if (page === 1) {
          setLeads(items);
        } else {
          setLeads((prev) => [...prev, ...items]);
        }

        setPageInfo(newPageInfo);
      } catch (err) {
        setError(err as Error);
      } finally {
        setIsLoading(false);
      }
    },
    [filter, sort]
  );

  const loadMore = useCallback(() => {
    if (pageInfo?.hasNext && !isLoading) {
      fetchLeads(pageInfo.page + 1);
    }
  }, [pageInfo, isLoading, fetchLeads]);

  const refresh = useCallback(() => {
    fetchLeads(1);
  }, [fetchLeads]);

  useEffect(() => {
    fetchLeads(1);
  }, [fetchLeads]);

  return {
    leads,
    pageInfo,
    isLoading,
    error,
    loadMore,
    refresh,
    hasMore: pageInfo?.hasNext ?? false,
  };
}

// =============================================================================
// Optimistic Update Hooks
// =============================================================================

export function useOptimisticUpdateLead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, input }: { id: string; input: Partial<Lead> }) =>
      graphqlClient.request<{ updateLead: MutationResult<Lead> }>(
        MUTATIONS.UPDATE_LEAD,
        { variables: { id, input } }
      ),
    onMutate: async ({ id, input }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['lead', id] });
      await queryClient.cancelQueries({ queryKey: ['leads'] });

      // Snapshot previous values
      const previousLead = queryClient.getQueryData<{ lead: Lead }>(['lead', id]);
      const previousLeads = queryClient.getQueryData<{ leads: Connection<Lead> }>(['leads']);

      // Optimistically update
      if (previousLead) {
        queryClient.setQueryData(['lead', id], {
          lead: { ...previousLead.lead, ...input, updatedAt: new Date().toISOString() },
        });
      }

      return { previousLead, previousLeads };
    },
    onError: (_, __, context) => {
      // Rollback on error
      if (context?.previousLead) {
        queryClient.setQueryData(['lead', context.previousLead.lead.id], context.previousLead);
      }
    },
    onSettled: (_, __, { id }) => {
      // Refetch to ensure consistency
      queryClient.invalidateQueries({ queryKey: ['lead', id] });
      queryClient.invalidateQueries({ queryKey: ['leads'] });
    },
  });
}

// =============================================================================
// Error Handling Hook
// =============================================================================

export function useGraphQLError() {
  const [error, setError] = useState<GraphQLRequestError | null>(null);

  const handleError = useCallback((err: unknown) => {
    if (err instanceof GraphQLRequestError) {
      setError(err);
    } else if (err instanceof Error) {
      setError(new GraphQLRequestError([{ message: err.message }]));
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return { error, handleError, clearError };
}

