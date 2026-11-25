'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { contactsAPI } from '@/lib/api';

export interface ContactItem {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  mobile?: string;
  account?: number;
  account_name?: string;
  company?: string;
  job_title?: string;
  score?: number;
  lifecycle_stage?: string;
  is_merged?: boolean;
  merged_into?: number;
  created_at?: string;
  updated_at?: string;
}

export function useContacts(params?: Record<string, unknown>) {
  return useQuery({
    queryKey: ['contacts', params],
    queryFn: () => contactsAPI.getContacts(params),
  });
}

export function useContact(id: number) {
  return useQuery({
    queryKey: ['contacts', id],
    queryFn: () => contactsAPI.getContact(id),
    enabled: !!id,
  });
}

export function useContactDuplicates() {
  return useQuery({
    queryKey: ['contacts', 'duplicates'],
    queryFn: () => contactsAPI.getDuplicates(),
  });
}

export function useCreateContact() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Record<string, unknown>) => contactsAPI.createContact(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contacts'] });
    },
  });
}

export function useUpdateContact() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Record<string, unknown> }) =>
      contactsAPI.updateContact(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['contacts'] });
      queryClient.invalidateQueries({ queryKey: ['contacts', variables.id] });
    },
  });
}

export function useDeleteContact() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => contactsAPI.deleteContact(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contacts'] });
    },
  });
}

export function useMergeContacts() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ primaryId, secondaryId, fieldChoices }: { primaryId: number; secondaryId: number; fieldChoices?: Record<string, string> }) =>
      contactsAPI.mergeContacts(primaryId, secondaryId, fieldChoices),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contacts'] });
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
    },
  });
}

export function useUnmergeContact() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (auditLogId: number) => contactsAPI.unmergeContact(auditLogId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contacts'] });
    },
  });
}

export function useContactActivities(contactId: number) {
  return useQuery({
    queryKey: ['contacts', contactId, 'activities'],
    queryFn: () => contactsAPI.getActivities(contactId),
    enabled: !!contactId,
  });
}

export function useCreateContactActivity(contactId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Record<string, unknown>) => contactsAPI.createActivity(contactId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contacts', contactId, 'activities'] });
    },
  });
}
