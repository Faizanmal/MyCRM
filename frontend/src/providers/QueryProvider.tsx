/**
 * MyCRM Query Client Provider
 *
 * Configures React Query with optimal settings for the CRM application.
 */

'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { ReactNode, useState } from 'react';

// Default query options
const defaultQueryOptions = {
  queries: {
    // Time before data is considered stale
    staleTime: 30 * 1000, // 30 seconds
    
    // Time before inactive queries are removed from cache
    gcTime: 5 * 60 * 1000, // 5 minutes (formerly cacheTime)
    
    // Retry failed queries
    retry: (failureCount: number, error: unknown) => {
      // Don't retry on 4xx errors
      if (error && typeof error === 'object' && 'status' in error) {
        const status = (error as { status: number }).status;
        if (status >= 400 && status < 500) {
          return false;
        }
      }
      return failureCount < 3;
    },
    
    // Retry delay with exponential backoff
    retryDelay: (attemptIndex: number) => 
      Math.min(1000 * 2 ** attemptIndex, 30000),
    
    // Refetch on window focus (good for real-time data)
    refetchOnWindowFocus: true,
    
    // Don't refetch on mount if data is fresh
    refetchOnMount: true,
    
    // Refetch on reconnect
    refetchOnReconnect: true,
  },
  mutations: {
    // Retry mutations on network errors only
    retry: (failureCount: number, error: unknown) => {
      if (error && typeof error === 'object' && 'status' in error) {
        const status = (error as { status: number }).status;
        // Only retry on network errors (status 0) or server errors (5xx)
        if (status !== 0 && status < 500) {
          return false;
        }
      }
      return failureCount < 2;
    },
  },
};

interface QueryProviderProps {
  children: ReactNode;
}

/**
 * QueryProvider component that wraps the application with React Query
 */
export function QueryProvider({ children }: QueryProviderProps) {
  // Create QueryClient inside component to avoid sharing state between requests in SSR
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: defaultQueryOptions,
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {process.env.NODE_ENV === 'development' && (
        <ReactQueryDevtools 
          initialIsOpen={false} 
          position="bottom"
          buttonPosition="bottom-right"
        />
      )}
    </QueryClientProvider>
  );
}

/**
 * Create a pre-configured QueryClient for server-side rendering
 */
export function createQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        // Disable refetching on SSR
        staleTime: 60 * 1000,
        refetchOnWindowFocus: false,
        refetchOnMount: false,
        refetchOnReconnect: false,
      },
    },
  });
}

export default QueryProvider;
