'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { accountsAPI } from '@/lib/api';

export interface AccountItem {
  id: number;
  name: string;
  domain?: string;
  industry?: string;
  tier?: string;
  account_type?: string;
  phone?: string;
  website?: string;
  city?: string;
  state?: string;
  country?: string;
  annual_revenue?: number;
  employee_count?: number;
  health_score?: number;
  is_merged?: boolean;
  contacts_count?: number;
  created_at?: string;
  updated_at?: string;
}

export function useAccounts(params?: Record<string, unknown>) {
  return useQuery({
    queryKey: ['accounts', params],
    queryFn: () => accountsAPI.getAccounts(params),
  });
}

export function useAccount(id: number) {
  return useQuery({
    queryKey: ['accounts', id],
    queryFn: () => accountsAPI.getAccount(id),
    enabled: !!id,
  });
}

export function useAccountStats() {
  return useQuery({
    queryKey: ['accounts', 'statistics'],
    queryFn: () => accountsAPI.getStatistics(),
  });
}

export function useCreateAccount() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Record<string, unknown>) => accountsAPI.createAccount(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
    },
  });
}

export function useUpdateAccount() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Record<string, unknown> }) =>
      accountsAPI.updateAccount(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
      queryClient.invalidateQueries({ queryKey: ['accounts', variables.id] });
    },
  });
}

export function useDeleteAccount() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => accountsAPI.deleteAccount(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
    },
  });
}

export function useMergeAccounts() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ primaryId, secondaryId, fieldChoices }: { primaryId: number; secondaryId: number; fieldChoices?: Record<string, string> }) =>
      accountsAPI.mergeAccounts(primaryId, secondaryId, fieldChoices),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
      queryClient.invalidateQueries({ queryKey: ['contacts'] });
    },
  });
}

export function useUnmergeAccount() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (auditLogId: number) => accountsAPI.unmergeAccount(auditLogId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
      queryClient.invalidateQueries({ queryKey: ['contacts'] });
    },
  });
}
