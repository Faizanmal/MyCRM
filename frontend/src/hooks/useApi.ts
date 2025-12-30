/**
 * MyCRM React Query Hooks
 *
 * Comprehensive data fetching hooks using TanStack React Query.
 * Provides caching, optimistic updates, and error handling.
 */

import {
  useQuery,
  useMutation,
  useQueryClient,
  useInfiniteQuery,
  UseMutationOptions,
  UseQueryOptions,
} from '@tanstack/react-query';
import { toast } from 'sonner';
import api from '@/lib/api';
import type {
  Contact,
  ContactCreatePayload,
  ContactUpdatePayload,
  Lead,
  LeadConvertPayload,
  Opportunity,
  OpportunityCreatePayload,
  OpportunityMovePayload,
  Task,
  TaskCreatePayload,
  Pipeline,
  PipelineStage,
  DashboardMetrics,
  PaginatedResponse,
  SearchParams,
  User,
  Team,
} from '@/types';

// ============================================================================
// Query Keys Factory
// ============================================================================

export const queryKeys = {
  // Contacts
  contacts: {
    all: ['contacts'] as const,
    lists: () => [...queryKeys.contacts.all, 'list'] as const,
    list: (params: SearchParams) => [...queryKeys.contacts.lists(), params] as const,
    details: () => [...queryKeys.contacts.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.contacts.details(), id] as const,
    analytics: () => [...queryKeys.contacts.all, 'analytics'] as const,
  },

  // Leads
  leads: {
    all: ['leads'] as const,
    lists: () => [...queryKeys.leads.all, 'list'] as const,
    list: (params: SearchParams) => [...queryKeys.leads.lists(), params] as const,
    details: () => [...queryKeys.leads.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.leads.details(), id] as const,
    analytics: () => [...queryKeys.leads.all, 'analytics'] as const,
  },

  // Opportunities
  opportunities: {
    all: ['opportunities'] as const,
    lists: () => [...queryKeys.opportunities.all, 'list'] as const,
    list: (params: SearchParams) => [...queryKeys.opportunities.lists(), params] as const,
    details: () => [...queryKeys.opportunities.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.opportunities.details(), id] as const,
    byPipeline: (pipelineId: string) => [...queryKeys.opportunities.all, 'pipeline', pipelineId] as const,
  },

  // Pipelines
  pipelines: {
    all: ['pipelines'] as const,
    lists: () => [...queryKeys.pipelines.all, 'list'] as const,
    detail: (id: string) => [...queryKeys.pipelines.all, 'detail', id] as const,
    stages: (pipelineId: string) => [...queryKeys.pipelines.all, pipelineId, 'stages'] as const,
  },

  // Tasks
  tasks: {
    all: ['tasks'] as const,
    lists: () => [...queryKeys.tasks.all, 'list'] as const,
    list: (params: SearchParams) => [...queryKeys.tasks.lists(), params] as const,
    details: () => [...queryKeys.tasks.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.tasks.details(), id] as const,
    myTasks: () => [...queryKeys.tasks.all, 'my'] as const,
    overdue: () => [...queryKeys.tasks.all, 'overdue'] as const,
  },

  // Dashboard
  dashboard: {
    all: ['dashboard'] as const,
    metrics: () => [...queryKeys.dashboard.all, 'metrics'] as const,
    activities: () => [...queryKeys.dashboard.all, 'activities'] as const,
    performance: () => [...queryKeys.dashboard.all, 'performance'] as const,
  },

  // Users & Teams
  users: {
    all: ['users'] as const,
    list: () => [...queryKeys.users.all, 'list'] as const,
    detail: (id: string) => [...queryKeys.users.all, 'detail', id] as const,
    me: () => [...queryKeys.users.all, 'me'] as const,
  },
  teams: {
    all: ['teams'] as const,
    list: () => [...queryKeys.teams.all, 'list'] as const,
    detail: (id: string) => [...queryKeys.teams.all, 'detail', id] as const,
  },
} as const;

// ============================================================================
// Contact Hooks
// ============================================================================

export function useContacts(params: SearchParams = {}) {
  return useQuery({
    queryKey: queryKeys.contacts.list(params),
    queryFn: () => api.get<PaginatedResponse<Contact>>('/contacts/', { params }).then(res => res.data),
    staleTime: 30000, // 30 seconds
  });
}

export function useContact(id: string, options?: UseQueryOptions<Contact>) {
  return useQuery({
    queryKey: queryKeys.contacts.detail(id),
    queryFn: () => api.get<Contact>(`/contacts/${id}/`).then(res => res.data),
    enabled: !!id,
    ...options,
  });
}

export function useContactsInfinite(params: Omit<SearchParams, 'page'> = {}) {
  return useInfiniteQuery({
    queryKey: queryKeys.contacts.list(params),
    queryFn: ({ pageParam = 1 }) =>
      api.get<PaginatedResponse<Contact>>('/contacts/', {
        params: { ...params, page: pageParam },
      }).then(res => res.data),
    getNextPageParam: (lastPage, allPages) => {
      if (!lastPage.next) return undefined;
      return allPages.length + 1;
    },
    initialPageParam: 1,
  });
}

export function useCreateContact(
  options?: UseMutationOptions<Contact, Error, ContactCreatePayload>
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ContactCreatePayload) =>
      api.post<Contact>('/contacts/', data).then(res => res.data),
    onSuccess: (newContact) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.contacts.lists() });
      queryClient.setQueryData(
        queryKeys.contacts.detail(newContact.id),
        newContact
      );
      toast.success('Contact created successfully');
    },
    onError: (error) => {
      toast.error(`Failed to create contact: ${error.message}`);
    },
    ...options,
  });
}

export function useUpdateContact(
  options?: UseMutationOptions<Contact, Error, { id: string; data: ContactUpdatePayload }, { previousContact: Contact | undefined }>
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }) =>
      api.patch<Contact>(`/contacts/${id}/`, data).then(res => res.data),
    onMutate: async ({ id, data }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: queryKeys.contacts.detail(id) });

      // Snapshot previous value
      const previousContact = queryClient.getQueryData<Contact>(
        queryKeys.contacts.detail(id)
      );

      // Optimistically update
      if (previousContact) {
        queryClient.setQueryData(queryKeys.contacts.detail(id), {
          ...previousContact,
          ...data,
        });
      }

      return { previousContact };
    },
    onError: (error, variables, context) => {
      // Rollback on error
      if (context?.previousContact) {
        queryClient.setQueryData(
          queryKeys.contacts.detail(variables.id),
          context.previousContact
        );
      }
      toast.error(`Failed to update contact: ${error.message}`);
    },
    onSettled: (_, __, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.contacts.detail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.contacts.lists() });
    },
    ...options,
  });
}

export function useDeleteContact(
  options?: UseMutationOptions<void, Error, string>
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => api.delete(`/contacts/${id}/`).then(() => { }),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.contacts.lists() });
      queryClient.removeQueries({ queryKey: queryKeys.contacts.detail(id) });
      toast.success('Contact deleted successfully');
    },
    onError: (error) => {
      toast.error(`Failed to delete contact: ${error.message}`);
    },
    ...options,
  });
}

export function useContactAnalytics() {
  return useQuery({
    queryKey: queryKeys.contacts.analytics(),
    queryFn: () => api.get('/contacts/analytics/').then(res => res.data),
    staleTime: 60000, // 1 minute
  });
}

// ============================================================================
// Lead Hooks
// ============================================================================

export function useLeads(params: SearchParams = {}) {
  return useQuery({
    queryKey: queryKeys.leads.list(params),
    queryFn: () => api.get<PaginatedResponse<Lead>>('/leads/', { params }).then(res => res.data),
    staleTime: 30000,
  });
}

export function useLead(id: string) {
  return useQuery({
    queryKey: queryKeys.leads.detail(id),
    queryFn: () => api.get<Lead>(`/leads/${id}/`).then(res => res.data),
    enabled: !!id,
  });
}

export function useCreateLead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<Lead>) => api.post<Lead>('/leads/', data).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.leads.lists() });
      toast.success('Lead created successfully');
    },
    onError: (error: Error) => {
      toast.error(`Failed to create lead: ${error.message}`);
    },
  });
}

export function useUpdateLead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Lead> }) =>
      api.patch<Lead>(`/leads/${id}/`, data).then(res => res.data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.leads.detail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.leads.lists() });
      toast.success('Lead updated successfully');
    },
    onError: (error: Error) => {
      toast.error(`Failed to update lead: ${error.message}`);
    },
  });
}

export function useConvertLead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: LeadConvertPayload }) =>
      api.post(`/leads/${id}/convert/`, data).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.leads.lists() });
      queryClient.invalidateQueries({ queryKey: queryKeys.contacts.lists() });
      queryClient.invalidateQueries({ queryKey: queryKeys.opportunities.lists() });
      toast.success('Lead converted successfully');
    },
    onError: (error: Error) => {
      toast.error(`Failed to convert lead: ${error.message}`);
    },
  });
}

export function useLeadAnalytics() {
  return useQuery({
    queryKey: queryKeys.leads.analytics(),
    queryFn: () => api.get('/leads/analytics/').then(res => res.data),
    staleTime: 60000,
  });
}

// ============================================================================
// Opportunity Hooks
// ============================================================================

export function useOpportunities(params: SearchParams = {}) {
  return useQuery({
    queryKey: queryKeys.opportunities.list(params),
    queryFn: () =>
      api.get<PaginatedResponse<Opportunity>>('/opportunities/', { params }).then(res => res.data),
    staleTime: 30000,
  });
}

export function useOpportunity(id: string) {
  return useQuery({
    queryKey: queryKeys.opportunities.detail(id),
    queryFn: () => api.get<Opportunity>(`/opportunities/${id}/`).then(res => res.data),
    enabled: !!id,
  });
}

export function useOpportunitiesByPipeline(pipelineId: string) {
  return useQuery({
    queryKey: queryKeys.opportunities.byPipeline(pipelineId),
    queryFn: () =>
      api.get<Opportunity[]>(`/pipelines/${pipelineId}/opportunities/`).then(res => res.data),
    enabled: !!pipelineId,
  });
}

export function useCreateOpportunity() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: OpportunityCreatePayload) =>
      api.post<Opportunity>('/opportunities/', data).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.opportunities.lists() });
      queryClient.invalidateQueries({ queryKey: queryKeys.pipelines.all });
      toast.success('Opportunity created successfully');
    },
    onError: (error: Error) => {
      toast.error(`Failed to create opportunity: ${error.message}`);
    },
  });
}

export function useMoveOpportunity() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: OpportunityMovePayload }) =>
      api.patch<Opportunity>(`/opportunities/${id}/move/`, data).then(res => res.data),
    onMutate: async ({ id, data }) => {
      await queryClient.cancelQueries({
        queryKey: queryKeys.opportunities.detail(id),
      });

      const previousOpportunity = queryClient.getQueryData<Opportunity>(
        queryKeys.opportunities.detail(id)
      );

      // Optimistic update
      if (previousOpportunity) {
        queryClient.setQueryData(queryKeys.opportunities.detail(id), {
          ...previousOpportunity,
          stage_id: data.stage_id,
          status: data.status || previousOpportunity.status,
        });
      }

      return { previousOpportunity };
    },
    onError: (error: Error, variables, context) => {
      if (context?.previousOpportunity) {
        queryClient.setQueryData(
          queryKeys.opportunities.detail(variables.id),
          context.previousOpportunity
        );
      }
      toast.error(`Failed to move opportunity: ${error.message}`);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.opportunities.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.pipelines.all });
    },
  });
}

export function useDeleteOpportunity() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => api.delete(`/opportunities/${id}/`).then(() => { }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.opportunities.lists() });
      toast.success('Opportunity deleted successfully');
    },
    onError: (error: Error) => {
      toast.error(`Failed to delete opportunity: ${error.message}`);
    },
  });
}

// ============================================================================
// Pipeline Hooks
// ============================================================================

export function usePipelines() {
  return useQuery({
    queryKey: queryKeys.pipelines.lists(),
    queryFn: () => api.get<Pipeline[]>('/pipelines/').then(res => res.data),
    staleTime: 60000,
  });
}

export function usePipeline(id: string) {
  return useQuery({
    queryKey: queryKeys.pipelines.detail(id),
    queryFn: () => api.get<Pipeline>(`/pipelines/${id}/`).then(res => res.data),
    enabled: !!id,
  });
}

export function usePipelineStages(pipelineId: string) {
  return useQuery({
    queryKey: queryKeys.pipelines.stages(pipelineId),
    queryFn: () => api.get<PipelineStage[]>(`/pipelines/${pipelineId}/stages/`).then(res => res.data),
    enabled: !!pipelineId,
  });
}

// ============================================================================
// Task Hooks
// ============================================================================

export function useTasks(params: SearchParams = {}) {
  return useQuery({
    queryKey: queryKeys.tasks.list(params),
    queryFn: () => api.get<PaginatedResponse<Task>>('/tasks/', { params }).then(res => res.data),
    staleTime: 30000,
  });
}

export function useTask(id: string) {
  return useQuery({
    queryKey: queryKeys.tasks.detail(id),
    queryFn: () => api.get<Task>(`/tasks/${id}/`).then(res => res.data),
    enabled: !!id,
  });
}

export function useMyTasks() {
  return useQuery({
    queryKey: queryKeys.tasks.myTasks(),
    queryFn: () => api.get<Task[]>('/tasks/my/').then(res => res.data),
    staleTime: 30000,
  });
}

export function useOverdueTasks() {
  return useQuery({
    queryKey: queryKeys.tasks.overdue(),
    queryFn: () => api.get<Task[]>('/tasks/overdue/').then(res => res.data),
    staleTime: 30000,
    refetchInterval: 60000, // Refetch every minute
  });
}

export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: TaskCreatePayload) => api.post<Task>('/tasks/', data).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.all });
      toast.success('Task created successfully');
    },
    onError: (error: Error) => {
      toast.error(`Failed to create task: ${error.message}`);
    },
  });
}

export function useUpdateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Task> }) =>
      api.patch<Task>(`/tasks/${id}/`, data).then(res => res.data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.detail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.lists() });
    },
    onError: (error: Error) => {
      toast.error(`Failed to update task: ${error.message}`);
    },
  });
}

export function useCompleteTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, outcome }: { id: string; outcome?: string }) =>
      api.post(`/tasks/${id}/complete/`, { outcome }).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.all });
      toast.success('Task completed');
    },
    onError: (error: Error) => {
      toast.error(`Failed to complete task: ${error.message}`);
    },
  });
}

// ============================================================================
// Dashboard Hooks
// ============================================================================

export function useDashboardMetrics() {
  return useQuery({
    queryKey: queryKeys.dashboard.metrics(),
    queryFn: () => api.get<DashboardMetrics>('/dashboard/metrics/').then(res => res.data),
    staleTime: 60000,
    refetchInterval: 300000, // Refetch every 5 minutes
  });
}

export function useDashboardAnalytics() {
  return useQuery({
    queryKey: [...queryKeys.dashboard.all, 'analytics'],
    queryFn: async () => {
      const response = await api.get('/v1/analytics/dashboard/');
      return response.data;
    },
    staleTime: 60000,
    refetchInterval: 300000, // Refetch every 5 minutes
  });
}

export function useRecentActivities(limit = 10) {
  return useQuery({
    queryKey: [...queryKeys.dashboard.activities(), limit],
    queryFn: () => api.get('/activities/recent/', { params: { limit } }).then(res => res.data),
    staleTime: 30000,
  });
}

export function useTeamPerformance(period: 'week' | 'month' | 'quarter' = 'month') {
  return useQuery({
    queryKey: [...queryKeys.dashboard.performance(), period],
    queryFn: () => api.get('/reports/team-performance/', { params: { period } }).then(res => res.data),
    staleTime: 60000,
  });
}

// ============================================================================
// User & Team Hooks
// ============================================================================

export function useCurrentUser() {
  return useQuery({
    queryKey: queryKeys.users.me(),
    queryFn: () => api.get<User>('/users/me/').then(res => res.data),
    staleTime: 300000, // 5 minutes
  });
}

export function useUsers() {
  return useQuery({
    queryKey: queryKeys.users.list(),
    queryFn: () => api.get<User[]>('/users/').then(res => res.data),
    staleTime: 60000,
  });
}

export function useTeams() {
  return useQuery({
    queryKey: queryKeys.teams.list(),
    queryFn: () => api.get<Team[]>('/teams/').then(res => res.data),
    staleTime: 60000,
  });
}

export function useTeam(id: string) {
  return useQuery({
    queryKey: queryKeys.teams.detail(id),
    queryFn: () => api.get<Team>(`/teams/${id}/`).then(res => res.data),
    enabled: !!id,
  });
}

// ============================================================================
// Utility Hooks
// ============================================================================

/**
 * Hook to prefetch data for better UX
 */
export function usePrefetch() {
  const queryClient = useQueryClient();

  return {
    prefetchContact: (id: string) => {
      queryClient.prefetchQuery({
        queryKey: queryKeys.contacts.detail(id),
        queryFn: () => api.get<Contact>(`/contacts/${id}/`).then(res => res.data),
      });
    },
    prefetchLead: (id: string) => {
      queryClient.prefetchQuery({
        queryKey: queryKeys.leads.detail(id),
        queryFn: () => api.get<Lead>(`/leads/${id}/`).then(res => res.data),
      });
    },
    prefetchOpportunity: (id: string) => {
      queryClient.prefetchQuery({
        queryKey: queryKeys.opportunities.detail(id),
        queryFn: () => api.get<Opportunity>(`/opportunities/${id}/`).then(res => res.data),
      });
    },
  };
}

/**
 * Hook to invalidate related queries after bulk operations
 */
export function useInvalidateRelated() {
  const queryClient = useQueryClient();

  return {
    invalidateAll: () => {
      queryClient.invalidateQueries();
    },
    invalidateSalesData: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.contacts.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.leads.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.opportunities.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboard.all });
    },
  };
}
