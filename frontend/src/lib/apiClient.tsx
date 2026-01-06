'use client';

import { QueryClient, QueryClientProvider, useQuery, useMutation, useQueryClient, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query';
import { ReactNode } from 'react';

/**
 * API Client Configuration and Hooks
 * 
 * Provides:
 * - Centralized API configuration
 * - Type-safe query hooks
 * - Automatic token handling
 * - Error handling
 * - Request/Response interceptors
 */

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface ApiConfig {
    baseURL: string;
    timeout: number;
    headers: Record<string, string>;
}

const defaultConfig: ApiConfig = {
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
};

// Error types
export class ApiError extends Error {
    status: number;
    data: unknown;

    constructor(message: string, status: number, data?: unknown) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
        this.data = data;
    }
}

// Token management
let accessToken: string | null = null;

export const setAccessToken = (token: string | null) => {
    accessToken = token;
    if (token) {
        localStorage.setItem('access_token', token);
    } else {
        localStorage.removeItem('access_token');
    }
};

export const getAccessToken = (): string | null => {
    if (accessToken) return accessToken;
    if (typeof window !== 'undefined') {
        accessToken = localStorage.getItem('access_token');
    }
    return accessToken;
};

// Base fetch function with interceptors
async function apiFetch<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<T> {
    const token = getAccessToken();

    const headers: Record<string, string> = {
        ...defaultConfig.headers,
        ...(options.headers as Record<string, string> || {}),
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const url = endpoint.startsWith('http') ? endpoint : `${defaultConfig.baseURL}${endpoint}`;

    try {
        const response = await fetch(url, {
            ...options,
            headers,
        });

        // Handle 401 - Token expired
        if (response.status === 401) {
            // Try to refresh token
            const refreshed = await refreshToken();
            if (refreshed) {
                // Retry the request
                headers['Authorization'] = `Bearer ${getAccessToken()}`;
                const retryResponse = await fetch(url, { ...options, headers });
                if (!retryResponse.ok) {
                    throw new ApiError('Request failed after token refresh', retryResponse.status);
                }
                return retryResponse.json();
            }
            // Redirect to login if refresh failed
            if (typeof window !== 'undefined') {
                window.location.href = '/login';
            }
            throw new ApiError('Session expired', 401);
        }

        // Handle other errors
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new ApiError(
                errorData.message || errorData.detail || `HTTP ${response.status}`,
                response.status,
                errorData
            );
        }

        // Handle 204 No Content
        if (response.status === 204) {
            return {} as T;
        }

        return response.json();
    } catch (error) {
        if (error instanceof ApiError) {
            throw error;
        }
        throw new ApiError('Network error', 0, error);
    }
}

// Token refresh function
async function refreshToken(): Promise<boolean> {
    const refreshTokenValue = typeof window !== 'undefined'
        ? localStorage.getItem('refresh_token')
        : null;

    if (!refreshTokenValue) return false;

    try {
        const response = await fetch(`${defaultConfig.baseURL}/auth/token/refresh/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: refreshTokenValue }),
        });

        if (response.ok) {
            const data = await response.json();
            setAccessToken(data.access);
            return true;
        }
    } catch {
        // Ignore refresh errors
    }

    return false;
}

// API methods
export const api = {
    get: <T,>(endpoint: string) => apiFetch<T>(endpoint),

    post: <T,>(endpoint: string, data?: unknown) =>
        apiFetch<T>(endpoint, {
            method: 'POST',
            body: data ? JSON.stringify(data) : undefined,
        }),

    put: <T,>(endpoint: string, data?: unknown) =>
        apiFetch<T>(endpoint, {
            method: 'PUT',
            body: data ? JSON.stringify(data) : undefined,
        }),

    patch: <T,>(endpoint: string, data?: unknown) =>
        apiFetch<T>(endpoint, {
            method: 'PATCH',
            body: data ? JSON.stringify(data) : undefined,
        }),

    delete: <T,>(endpoint: string) =>
        apiFetch<T>(endpoint, { method: 'DELETE' }),
};

// Query Key Factory
export const queryKeys = {
    // Leads
    leads: {
        all: ['leads'] as const,
        lists: () => [...queryKeys.leads.all, 'list'] as const,
        list: (filters: Record<string, unknown>) => [...queryKeys.leads.lists(), filters] as const,
        details: () => [...queryKeys.leads.all, 'detail'] as const,
        detail: (id: number | string) => [...queryKeys.leads.details(), id] as const,
    },

    // Contacts
    contacts: {
        all: ['contacts'] as const,
        lists: () => [...queryKeys.contacts.all, 'list'] as const,
        list: (filters: Record<string, unknown>) => [...queryKeys.contacts.lists(), filters] as const,
        details: () => [...queryKeys.contacts.all, 'detail'] as const,
        detail: (id: number | string) => [...queryKeys.contacts.details(), id] as const,
    },

    // Opportunities
    opportunities: {
        all: ['opportunities'] as const,
        lists: () => [...queryKeys.opportunities.all, 'list'] as const,
        list: (filters: Record<string, unknown>) => [...queryKeys.opportunities.lists(), filters] as const,
        details: () => [...queryKeys.opportunities.all, 'detail'] as const,
        detail: (id: number | string) => [...queryKeys.opportunities.details(), id] as const,
    },

    // Tasks
    tasks: {
        all: ['tasks'] as const,
        lists: () => [...queryKeys.tasks.all, 'list'] as const,
        list: (filters: Record<string, unknown>) => [...queryKeys.tasks.lists(), filters] as const,
        details: () => [...queryKeys.tasks.all, 'detail'] as const,
        detail: (id: number | string) => [...queryKeys.tasks.details(), id] as const,
    },

    // User
    user: {
        current: ['user', 'current'] as const,
        preferences: ['user', 'preferences'] as const,
        notifications: ['user', 'notifications'] as const,
    },

    // Dashboard
    dashboard: {
        stats: ['dashboard', 'stats'] as const,
        activities: ['dashboard', 'activities'] as const,
        charts: (type: string) => ['dashboard', 'charts', type] as const,
    },
};

// Generic Types
interface PaginatedResponse<T> {
    results: T[];
    count: number;
    next: string | null;
    previous: string | null;
}

interface ListParams {
    page?: number;
    page_size?: number;
    search?: string;
    ordering?: string;
    [key: string]: unknown;
}

// Generic List Hook
export function useList<T>(
    resource: string,
    params: ListParams = {},
    options?: Omit<UseQueryOptions<PaginatedResponse<T>>, 'queryKey' | 'queryFn'>
) {
    const queryString = new URLSearchParams(
        Object.entries(params).reduce((acc, [key, value]) => {
            if (value !== undefined && value !== null && value !== '') {
                acc[key] = String(value);
            }
            return acc;
        }, {} as Record<string, string>)
    ).toString();

    const endpoint = queryString ? `/${resource}/?${queryString}` : `/${resource}/`;

    return useQuery({
        queryKey: [resource, 'list', params],
        queryFn: () => api.get<PaginatedResponse<T>>(endpoint),
        ...options,
    });
}

// Generic Detail Hook
export function useDetail<T>(
    resource: string,
    id: number | string | undefined,
    options?: Omit<UseQueryOptions<T>, 'queryKey' | 'queryFn'>
) {
    return useQuery({
        queryKey: [resource, 'detail', id],
        queryFn: () => api.get<T>(`/${resource}/${id}/`),
        enabled: id !== undefined,
        ...options,
    });
}

// Generic Create Hook
export function useCreate<T, TData = Partial<T>>(
    resource: string,
    options?: UseMutationOptions<T, ApiError, TData>
) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (data: TData) => api.post<T>(`/${resource}/`, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: [resource] });
        },
        ...options,
    });
}

// Generic Update Hook
export function useUpdate<T, TData = Partial<T>>(
    resource: string,
    id: number | string,
    options?: UseMutationOptions<T, ApiError, TData>
) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (data: TData) => api.patch<T>(`/${resource}/${id}/`, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: [resource] });
            queryClient.invalidateQueries({ queryKey: [resource, 'detail', id] });
        },
        ...options,
    });
}

// Generic Delete Hook
export function useDelete(
    resource: string,
    options?: UseMutationOptions<void, ApiError, number | string>
) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (id: number | string) => api.delete<void>(`/${resource}/${id}/`),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: [resource] });
        },
        ...options,
    });
}

// Query Client configuration
export const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            staleTime: 1000 * 60 * 5, // 5 minutes
            gcTime: 1000 * 60 * 30, // 30 minutes
            retry: (failureCount, error) => {
                if ((error as ApiError).status === 401 || (error as ApiError).status === 403) {
                    return false;
                }
                return failureCount < 3;
            },
            refetchOnWindowFocus: false,
        },
        mutations: {
            retry: false,
        },
    },
});

// API Provider Component
interface ApiProviderProps {
    children: ReactNode;
}

export function ApiProvider({ children }: ApiProviderProps) {
    return (
        <QueryClientProvider client= { queryClient } >
        { children }
        </QueryClientProvider>
  );
}

export default {
    api,
    queryKeys,
    useList,
    useDetail,
    useCreate,
    useUpdate,
    useDelete,
    ApiProvider,
    queryClient,
    setAccessToken,
    getAccessToken,
};
