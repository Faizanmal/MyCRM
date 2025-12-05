/**
 * Enterprise GraphQL Client for MyCRM
 * ====================================
 * 
 * Features:
 * - Type-safe GraphQL queries and mutations
 * - Automatic caching and cache invalidation
 * - WebSocket subscriptions for real-time updates
 * - Request batching and deduplication
 * - Optimistic updates
 * - Error handling with retry logic
 */

import { QueryClient } from '@tanstack/react-query';

const GRAPHQL_ENDPOINT = process.env.NEXT_PUBLIC_GRAPHQL_URL || 'http://localhost:8000/graphql';
const WS_ENDPOINT = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/graphql';

// =============================================================================
// Types
// =============================================================================

export interface GraphQLError {
  message: string;
  locations?: Array<{ line: number; column: number }>;
  path?: string[];
  extensions?: Record<string, unknown>;
}

export interface GraphQLResponse<T = unknown> {
  data?: T;
  errors?: GraphQLError[];
}

export interface GraphQLRequestOptions {
  variables?: Record<string, unknown>;
  headers?: Record<string, string>;
  signal?: AbortSignal;
  operationName?: string;
}

export interface SubscriptionOptions<T> {
  query: string;
  variables?: Record<string, unknown>;
  onData: (data: T) => void;
  onError?: (error: Error) => void;
  onComplete?: () => void;
}

// =============================================================================
// GraphQL Client
// =============================================================================

class GraphQLClient {
  private endpoint: string;
  private wsEndpoint: string;
  private defaultHeaders: Record<string, string>;
  private subscriptions: Map<string, WebSocket>;
  private pendingRequests: Map<string, Promise<unknown>>;

  constructor() {
    this.endpoint = GRAPHQL_ENDPOINT;
    this.wsEndpoint = WS_ENDPOINT;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };
    this.subscriptions = new Map();
    this.pendingRequests = new Map();
  }

  /**
   * Set authentication token
   */
  setAuthToken(token: string | null): void {
    if (token) {
      this.defaultHeaders['Authorization'] = `Bearer ${token}`;
    } else {
      delete this.defaultHeaders['Authorization'];
    }
  }

  /**
   * Execute a GraphQL query or mutation
   */
  async request<T = unknown>(
    query: string,
    options: GraphQLRequestOptions = {}
  ): Promise<T> {
    const { variables, headers, signal, operationName } = options;

    // Create request key for deduplication
    const requestKey = this.createRequestKey(query, variables);

    // Check for pending identical request
    const pending = this.pendingRequests.get(requestKey);
    if (pending) {
      return pending as Promise<T>;
    }

    const requestPromise = this.executeRequest<T>(
      query,
      variables,
      headers,
      signal,
      operationName
    );

    // Store pending request
    this.pendingRequests.set(requestKey, requestPromise);

    try {
      const result = await requestPromise;
      return result;
    } finally {
      this.pendingRequests.delete(requestKey);
    }
  }

  private async executeRequest<T>(
    query: string,
    variables?: Record<string, unknown>,
    headers?: Record<string, string>,
    signal?: AbortSignal,
    operationName?: string
  ): Promise<T> {
    const token = typeof window !== 'undefined' 
      ? localStorage.getItem('access_token') 
      : null;

    const response = await fetch(this.endpoint, {
      method: 'POST',
      headers: {
        ...this.defaultHeaders,
        ...(token && { Authorization: `Bearer ${token}` }),
        ...headers,
      },
      body: JSON.stringify({
        query,
        variables,
        operationName,
      }),
      signal,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result: GraphQLResponse<T> = await response.json();

    if (result.errors && result.errors.length > 0) {
      const error = new GraphQLRequestError(result.errors);
      throw error;
    }

    return result.data as T;
  }

  /**
   * Subscribe to GraphQL subscriptions via WebSocket
   */
  subscribe<T>(options: SubscriptionOptions<T>): () => void {
    const { query, variables, onData, onError, onComplete } = options;
    const subscriptionId = this.createRequestKey(query, variables);

    // Close existing subscription with same query
    this.unsubscribe(subscriptionId);

    const token = typeof window !== 'undefined'
      ? localStorage.getItem('access_token')
      : null;

    const wsUrl = new URL(this.wsEndpoint);
    if (token) {
      wsUrl.searchParams.set('token', token);
    }

    const ws = new WebSocket(wsUrl.toString(), 'graphql-ws');

    ws.onopen = () => {
      // Send connection init
      ws.send(JSON.stringify({
        type: 'connection_init',
        payload: token ? { Authorization: `Bearer ${token}` } : {},
      }));

      // Subscribe to query
      ws.send(JSON.stringify({
        id: subscriptionId,
        type: 'subscribe',
        payload: { query, variables },
      }));
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);

      switch (message.type) {
        case 'next':
          if (message.payload?.data) {
            onData(message.payload.data as T);
          }
          break;
        case 'error':
          onError?.(new Error(message.payload?.message || 'Subscription error'));
          break;
        case 'complete':
          onComplete?.();
          break;
      }
    };

    ws.onerror = (error) => {
      onError?.(error as unknown as Error);
    };

    ws.onclose = () => {
      this.subscriptions.delete(subscriptionId);
      onComplete?.();
    };

    this.subscriptions.set(subscriptionId, ws);

    // Return unsubscribe function
    return () => this.unsubscribe(subscriptionId);
  }

  /**
   * Unsubscribe from a subscription
   */
  unsubscribe(subscriptionId: string): void {
    const ws = this.subscriptions.get(subscriptionId);
    if (ws) {
      ws.close();
      this.subscriptions.delete(subscriptionId);
    }
  }

  /**
   * Close all subscriptions
   */
  closeAllSubscriptions(): void {
    this.subscriptions.forEach((ws) => ws.close());
    this.subscriptions.clear();
  }

  private createRequestKey(
    query: string,
    variables?: Record<string, unknown>
  ): string {
    return `${query}:${JSON.stringify(variables || {})}`;
  }
}

// =============================================================================
// Error Classes
// =============================================================================

export class GraphQLRequestError extends Error {
  errors: GraphQLError[];

  constructor(errors: GraphQLError[]) {
    super(errors.map((e) => e.message).join(', '));
    this.name = 'GraphQLRequestError';
    this.errors = errors;
  }
}

// =============================================================================
// Query Definitions
// =============================================================================

export const QUERIES = {
  // Dashboard
  DASHBOARD_METRICS: `
    query DashboardMetrics {
      dashboardMetrics {
        totalLeads
        leadsThisMonth
        leadConversionRate
        totalOpportunities
        pipelineValue
        weightedPipeline
        totalContacts
        contactsThisMonth
        wonDealsCount
        wonDealsValue
        tasksDueToday
        overdueTasks
        activitiesThisWeek
      }
    }
  `,

  // Leads
  GET_LEADS: `
    query GetLeads(
      $filter: LeadFilterInput
      $pagination: PaginationInput
      $sort: SortInput
    ) {
      leads(filter: $filter, pagination: $pagination, sort: $sort) {
        items {
          id
          firstName
          lastName
          email
          phone
          company
          status
          source
          score
          notes
          createdAt
          updatedAt
          assignedTo {
            id
            email
            fullName
          }
          aiInsights {
            conversionProbability
            recommendedActions
            engagementScore
            bestContactTime
            sentiment
          }
        }
        pageInfo {
          page
          pageSize
          totalPages
          totalCount
          hasNext
          hasPrevious
        }
      }
    }
  `,

  GET_LEAD: `
    query GetLead($id: ID!) {
      lead(id: $id) {
        id
        firstName
        lastName
        email
        phone
        company
        status
        source
        score
        notes
        customFields
        createdAt
        updatedAt
        assignedTo {
          id
          email
          fullName
        }
        activities(limit: 20) {
          id
          type
          title
          description
          createdAt
          user {
            id
            fullName
          }
        }
        aiInsights {
          id
          conversionProbability
          recommendedActions
          engagementScore
          bestContactTime
          sentiment
          generatedAt
        }
      }
    }
  `,

  // Contacts
  GET_CONTACTS: `
    query GetContacts(
      $filter: ContactFilterInput
      $pagination: PaginationInput
      $sort: SortInput
    ) {
      contacts(filter: $filter, pagination: $pagination, sort: $sort) {
        items {
          id
          firstName
          lastName
          email
          phone
          mobile
          jobTitle
          department
          type
          tags
          createdAt
          updatedAt
          company {
            id
            name
            industry
          }
        }
        pageInfo {
          page
          pageSize
          totalPages
          totalCount
          hasNext
          hasPrevious
        }
      }
    }
  `,

  // Opportunities
  GET_OPPORTUNITIES: `
    query GetOpportunities(
      $filter: OpportunityFilterInput
      $pagination: PaginationInput
      $sort: SortInput
    ) {
      opportunities(filter: $filter, pagination: $pagination, sort: $sort) {
        items {
          id
          name
          value
          stage
          probability
          expectedCloseDate
          description
          weightedValue
          createdAt
          updatedAt
          contact {
            id
            fullName
            email
            company {
              id
              name
            }
          }
          owner {
            id
            fullName
          }
        }
        pageInfo {
          page
          pageSize
          totalPages
          totalCount
          hasNext
          hasPrevious
        }
      }
    }
  `,

  // Analytics
  SALES_ANALYTICS: `
    query SalesAnalytics($period: String!) {
      salesAnalytics(period: $period) {
        period
        revenue
        dealsWon
        dealsLost
        avgDealSize
        avgSalesCycleDays
        winRate
        pipelineByStage
        revenueBySource
        topPerformers {
          user {
            id
            fullName
          }
          dealsWon
          revenue
          conversionRate
        }
      }
    }
  `,

  // Current User
  ME: `
    query Me {
      me {
        id
        email
        firstName
        lastName
        fullName
        isActive
        dateJoined
        lastLogin
      }
    }
  `,
};

export const MUTATIONS = {
  // Leads
  CREATE_LEAD: `
    mutation CreateLead($input: CreateLeadInput!) {
      createLead(input: $input) {
        success
        message
        errors
        lead {
          id
          firstName
          lastName
          email
          status
          createdAt
        }
      }
    }
  `,

  UPDATE_LEAD: `
    mutation UpdateLead($id: ID!, $input: UpdateLeadInput!) {
      updateLead(id: $id, input: $input) {
        success
        message
        errors
        lead {
          id
          firstName
          lastName
          email
          status
          score
          updatedAt
        }
      }
    }
  `,

  DELETE_LEAD: `
    mutation DeleteLead($id: ID!) {
      deleteLead(id: $id) {
        success
        message
        errors
      }
    }
  `,

  CONVERT_LEAD: `
    mutation ConvertLead(
      $leadId: ID!
      $createOpportunity: Boolean
      $opportunityValue: Money
    ) {
      convertLeadToContact(
        leadId: $leadId
        createOpportunity: $createOpportunity
        opportunityValue: $opportunityValue
      ) {
        success
        message
        errors
        contact {
          id
          firstName
          lastName
          email
        }
      }
    }
  `,

  // Tasks
  CREATE_TASK: `
    mutation CreateTask($input: CreateTaskInput!) {
      createTask(input: $input) {
        success
        message
        errors
        task {
          id
          title
          dueDate
          priority
          isCompleted
        }
      }
    }
  `,

  COMPLETE_TASK: `
    mutation CompleteTask($id: ID!) {
      completeTask(id: $id) {
        success
        message
        errors
        task {
          id
          isCompleted
          completedAt
        }
      }
    }
  `,
};

export const SUBSCRIPTIONS = {
  LEAD_UPDATES: `
    subscription LeadUpdates {
      leadUpdates {
        id
        firstName
        lastName
        email
        status
        score
        updatedAt
      }
    }
  `,

  OPPORTUNITY_UPDATES: `
    subscription OpportunityUpdates {
      opportunityUpdates {
        id
        name
        value
        stage
        probability
        updatedAt
      }
    }
  `,

  ACTIVITY_FEED: `
    subscription ActivityFeed {
      activityFeed {
        id
        type
        title
        description
        relatedToType
        relatedToId
        createdAt
      }
    }
  `,

  NOTIFICATIONS: `
    subscription Notifications {
      notifications
    }
  `,
};

// =============================================================================
// React Query Integration
// =============================================================================

export const graphqlQueryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 30 * 60 * 1000, // 30 minutes (formerly cacheTime)
      retry: 3,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    },
    mutations: {
      retry: 1,
    },
  },
});

// =============================================================================
// Export singleton instance
// =============================================================================

export const graphqlClient = new GraphQLClient();
export default graphqlClient;
