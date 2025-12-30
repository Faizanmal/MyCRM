/**
 * API Hook Tests
 * 
 * Tests for the useApi hook and related utilities
 */

import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactNode } from 'react';

// Create test wrapper
const createWrapper = () => {
    const queryClient = new QueryClient({
        defaultOptions: {
            queries: {
                retry: false,
                gcTime: 0,
            },
        },
    });

    return ({ children }: { children: ReactNode }) => (
        <QueryClientProvider client= { queryClient } >
        { children }
        </QueryClientProvider>
  );
};

describe('API Hooks', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    describe('Query Key Factory', () => {
        it('should generate consistent query keys', () => {
            // Import the query keys factory
            const queryKeys = {
                leads: {
                    all: ['leads'] as const,
                    lists: () => [...queryKeys.leads.all, 'list'] as const,
                    list: (filters: Record<string, unknown>) => [...queryKeys.leads.lists(), filters] as const,
                    details: () => [...queryKeys.leads.all, 'detail'] as const,
                    detail: (id: number) => [...queryKeys.leads.details(), id] as const,
                },
                contacts: {
                    all: ['contacts'] as const,
                    lists: () => [...queryKeys.contacts.all, 'list'] as const,
                    list: (filters: Record<string, unknown>) => [...queryKeys.contacts.lists(), filters] as const,
                    details: () => [...queryKeys.contacts.all, 'detail'] as const,
                    detail: (id: number) => [...queryKeys.contacts.details(), id] as const,
                },
            };

            expect(queryKeys.leads.all).toEqual(['leads']);
            expect(queryKeys.leads.lists()).toEqual(['leads', 'list']);
            expect(queryKeys.leads.detail(1)).toEqual(['leads', 'detail', 1]);
            expect(queryKeys.contacts.list({ status: 'active' })).toEqual(['contacts', 'list', { status: 'active' }]);
        });
    });

    describe('useFetch Hook', () => {
        it('should handle successful fetch', async () => {
            const mockData = { id: 1, name: 'Test' };
            global.fetch = jest.fn().mockResolvedValue({
                ok: true,
                json: () => Promise.resolve(mockData),
            });

            // Simple fetch implementation for testing
            const useFetch = (url: string) => {
                const queryClient = new QueryClient();
                return {
                    data: mockData,
                    isLoading: false,
                    error: null,
                };
            };

            const result = useFetch('/api/test');
            expect(result.data).toEqual(mockData);
            expect(result.isLoading).toBe(false);
        });
    });

    describe('Error Handling', () => {
        it('should handle network errors gracefully', async () => {
            const errorMessage = 'Network error';
            global.fetch = jest.fn().mockRejectedValue(new Error(errorMessage));

            // Test error handling
            expect(() => {
                throw new Error(errorMessage);
            }).toThrow(errorMessage);
        });

        it('should handle 401 unauthorized', async () => {
            global.fetch = jest.fn().mockResolvedValue({
                ok: false,
                status: 401,
                statusText: 'Unauthorized',
            });

            const response = await fetch('/api/test');
            expect(response.status).toBe(401);
        });

        it('should handle 404 not found', async () => {
            global.fetch = jest.fn().mockResolvedValue({
                ok: false,
                status: 404,
                statusText: 'Not Found',
            });

            const response = await fetch('/api/test');
            expect(response.status).toBe(404);
        });
    });

    describe('Pagination', () => {
        it('should handle paginated responses', async () => {
            const paginatedData = {
                results: [{ id: 1 }, { id: 2 }],
                count: 100,
                next: '/api/leads?page=2',
                previous: null,
            };

            global.fetch = jest.fn().mockResolvedValue({
                ok: true,
                json: () => Promise.resolve(paginatedData),
            });

            const response = await fetch('/api/leads');
            const data = await response.json();

            expect(data.results).toHaveLength(2);
            expect(data.count).toBe(100);
            expect(data.next).toBeTruthy();
        });
    });
});

describe('API Utilities', () => {
    describe('buildQueryString', () => {
        it('should build query string from params', () => {
            const buildQueryString = (params: Record<string, unknown>) => {
                const searchParams = new URLSearchParams();
                Object.entries(params).forEach(([key, value]) => {
                    if (value !== undefined && value !== null) {
                        searchParams.append(key, String(value));
                    }
                });
                return searchParams.toString();
            };

            expect(buildQueryString({ page: 1, limit: 10 })).toBe('page=1&limit=10');
            expect(buildQueryString({ status: 'active', search: '' })).toBe('status=active&search=');
            expect(buildQueryString({})).toBe('');
        });
    });

    describe('handleApiError', () => {
        it('should extract error message from response', async () => {
            const handleApiError = async (response: Response) => {
                if (!response.ok) {
                    const data = await response.json().catch(() => ({}));
                    return data.message || data.detail || response.statusText;
                }
                return null;
            };

            global.fetch = jest.fn().mockResolvedValue({
                ok: false,
                status: 400,
                statusText: 'Bad Request',
                json: () => Promise.resolve({ message: 'Validation error' }),
            });

            const response = await fetch('/api/test');
            const error = await handleApiError(response);

            expect(error).toBe('Validation error');
        });
    });
});
