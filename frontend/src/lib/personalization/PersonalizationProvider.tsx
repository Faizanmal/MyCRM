'use client';

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// Types
interface DashboardPreferences {
  defaultDashboard: string;
  layout: Record<string, unknown>;
  pinnedWidgets: string[];
  hiddenWidgets: string[];
}

interface NavigationPreferences {
  favoritePages: string[];
  recentPages: { path: string; timestamp: string }[];
  sidebarCollapsed: boolean;
  sidebarFavorites: string[];
}

interface DisplayPreferences {
  listDensity: 'compact' | 'comfortable' | 'spacious';
  defaultListView: 'table' | 'grid' | 'kanban';
  itemsPerPage: number;
}

interface NotificationPreferences {
  channels: Record<string, boolean>;
  quietHours: { start: string; end: string; enabled: boolean };
  digest: 'realtime' | 'hourly' | 'daily';
}

interface SmartFeatures {
  suggestionsEnabled: boolean;
  predictiveActionsEnabled: boolean;
  autoCompleteEnabled: boolean;
}

interface UserPreferences {
  dashboard: DashboardPreferences;
  navigation: NavigationPreferences;
  display: DisplayPreferences;
  notifications: NotificationPreferences;
  smartFeatures: SmartFeatures;
}

interface QuickAction {
  id: string;
  name: string;
  icon: string;
  color: string;
  actionType: string;
  actionConfig: Record<string, unknown>;
  keyboardShortcut?: string;
}

interface Insight {
  id: string;
  type: string;
  title: string;
  description: string;
  recommendation?: string;
  confidence: number;
  status: 'new' | 'viewed' | 'acted' | 'dismissed';
}

interface OnboardingTour {
  id: string;
  name: string;
  slug: string;
  description: string;
  totalSteps: number;
  currentStep: number;
  status: 'not_started' | 'in_progress' | 'completed' | 'skipped';
  progressPercent: number;
}

interface ContextualHelp {
  id: string;
  title: string;
  content: string;
  type: 'tooltip' | 'popover' | 'modal' | 'inline';
  elementSelector: string;
  position: string;
  trigger: string;
}

interface PersonalizationContextType {
  // Preferences
  preferences: UserPreferences | null;
  updatePreference: <K extends keyof UserPreferences>(
    section: K,
    updates: Partial<UserPreferences[K]>
  ) => void;
  resetPreferences: (section?: keyof UserPreferences) => void;

  // Quick Actions
  quickActions: QuickAction[];
  executeQuickAction: (actionId: string) => void;
  createQuickAction: (action: Omit<QuickAction, 'id'>) => void;
  deleteQuickAction: (actionId: string) => void;

  // Insights
  insights: Insight[];
  dismissInsight: (insightId: string) => void;
  actOnInsight: (insightId: string) => void;

  // Onboarding
  tours: OnboardingTour[];
  activeTour: OnboardingTour | null;
  startTour: (tourSlug: string) => void;
  skipTour: (tourSlug: string) => void;
  nextTourStep: () => void;

  // Contextual Help
  getHelpForPage: (pagePath: string) => ContextualHelp[];
  dismissHelp: (helpId: string) => void;

  // Smart Defaults
  getSmartDefaults: (entityType: string, context?: Record<string, unknown>) => Record<string, unknown>;

  // Behavior Tracking
  trackEvent: (eventType: string, eventData: Record<string, unknown>) => void;

  // UI Adaptations
  uiAdaptations: {
    dashboardWidgets: string[];
    sidebarOrder: string[];
    quickActions: QuickAction[];
    featureHighlights: { feature: string; description: string }[];
  } | null;

  // State
  isLoading: boolean;
}

// Default values
const defaultPreferences: UserPreferences = {
  dashboard: {
    defaultDashboard: 'overview',
    layout: {},
    pinnedWidgets: [],
    hiddenWidgets: [],
  },
  navigation: {
    favoritePages: [],
    recentPages: [],
    sidebarCollapsed: false,
    sidebarFavorites: [],
  },
  display: {
    listDensity: 'comfortable',
    defaultListView: 'table',
    itemsPerPage: 25,
  },
  notifications: {
    channels: { email: true, push: true, inApp: true },
    quietHours: { start: '22:00', end: '08:00', enabled: false },
    digest: 'realtime',
  },
  smartFeatures: {
    suggestionsEnabled: true,
    predictiveActionsEnabled: true,
    autoCompleteEnabled: true,
  },
};

// Context
const PersonalizationContext = createContext<PersonalizationContextType | undefined>(undefined);

// Mock API functions
async function fetchPreferences(): Promise<UserPreferences> {
  // In production, fetch from API
  return defaultPreferences;
}

async function fetchQuickActions(): Promise<QuickAction[]> {
  return [
    {
      id: '1',
      name: 'New Deal',
      icon: 'plus-circle',
      color: 'blue',
      actionType: 'create',
      actionConfig: { entity: 'deal' },
      keyboardShortcut: 'Ctrl+Shift+D',
    },
    {
      id: '2',
      name: 'Search',
      icon: 'search',
      color: 'green',
      actionType: 'search',
      actionConfig: {},
      keyboardShortcut: 'Ctrl+K',
    },
  ];
}

async function fetchInsights(): Promise<Insight[]> {
  return [
    {
      id: '1',
      type: 'productivity_tip',
      title: 'Optimize Your Schedule',
      description: 'You are most productive between 9-11 AM.',
      recommendation: 'Schedule important calls during this time.',
      confidence: 0.85,
      status: 'new',
    },
  ];
}

async function fetchTours(): Promise<OnboardingTour[]> {
  return [
    {
      id: '1',
      name: 'Getting Started',
      slug: 'getting-started',
      description: 'Learn the basics',
      totalSteps: 5,
      currentStep: 2,
      status: 'in_progress',
      progressPercent: 40,
    },
  ];
}

async function fetchUIAdaptations() {
  return {
    dashboardWidgets: ['pipeline', 'revenue_chart', 'tasks'],
    sidebarOrder: ['deals', 'contacts', 'tasks', 'reports'],
    quickActions: [],
    featureHighlights: [
      { feature: 'automation', description: 'Automate repetitive tasks' },
    ],
  };
}

// Provider Component
interface PersonalizationProviderProps {
  children: ReactNode;
  userId?: string;
}

export function PersonalizationProvider({ children, userId }: PersonalizationProviderProps) {
  const queryClient = useQueryClient();
  const [activeTour, setActiveTour] = useState<OnboardingTour | null>(null);
  const [helpDismissed, setHelpDismissed] = useState<Set<string>>(new Set());
  // const [sessionId] = useState(() => `session_${Date.now()}`);

  // Fetch preferences
  const { data: preferences, isLoading: prefsLoading } = useQuery({
    queryKey: ['preferences', userId],
    queryFn: fetchPreferences,
    enabled: !!userId,
    staleTime: 5 * 60 * 1000,
  });

  // Fetch quick actions
  const { data: quickActions = [] } = useQuery({
    queryKey: ['quickActions', userId],
    queryFn: fetchQuickActions,
    enabled: !!userId,
  });

  // Fetch insights
  const { data: insights = [] } = useQuery({
    queryKey: ['insights', userId],
    queryFn: fetchInsights,
    enabled: !!userId,
  });

  // Fetch tours
  const { data: tours = [] } = useQuery({
    queryKey: ['tours', userId],
    queryFn: fetchTours,
    enabled: !!userId,
  });

  // Fetch UI adaptations
  const { data: uiAdaptations } = useQuery({
    queryKey: ['uiAdaptations', userId],
    queryFn: fetchUIAdaptations,
    enabled: !!userId,
  });

  // Update preference mutation
  const updatePrefMutation = useMutation({
    mutationFn: async ({ section, updates }: { section: string; updates: Record<string, unknown> }) => {
      // In production, send to API
      return { section, updates };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['preferences', userId] });
    },
  });

  // Update preferences
  const updatePreference = useCallback(
    <K extends keyof UserPreferences>(section: K, updates: Partial<UserPreferences[K]>) => {
      updatePrefMutation.mutate({ section, updates });
    },
    [updatePrefMutation]
  );

  // Reset preferences
  const resetPreferences = useCallback(() => {
    // In production, call API to reset
    queryClient.invalidateQueries({ queryKey: ['preferences', userId] });
  }, [queryClient, userId]);

  // Execute quick action
  const executeQuickAction = useCallback((actionId: string) => {
    const action = quickActions.find(a => a.id === actionId);
    if (!action) return;

    // Handle different action types
    switch (action.actionType) {
      case 'navigate':
        window.location.href = action.actionConfig.path as string;
        break;
      case 'create':
        // Dispatch create event
        window.dispatchEvent(new CustomEvent('personalization:create', {
          detail: { entity: action.actionConfig.entity },
        }));
        break;
      case 'search':
        // Focus search input
        const searchInput = document.querySelector('[data-search-input]') as HTMLInputElement;
        searchInput?.focus();
        break;
    }
  }, [quickActions]);

  // Create quick action
  const createQuickAction = useCallback(() => {
    // In production, send to API
    queryClient.invalidateQueries({ queryKey: ['quickActions', userId] });
  }, [queryClient, userId]);

  // Delete quick action
  const deleteQuickAction = useCallback(() => {
    // In production, send to API
    queryClient.invalidateQueries({ queryKey: ['quickActions', userId] });
  }, [queryClient, userId]);

  // Dismiss insight
  const dismissInsight = useCallback(() => {
    // In production, send to API
    queryClient.invalidateQueries({ queryKey: ['insights', userId] });
  }, [queryClient, userId]);

  // Act on insight
  const actOnInsight = useCallback(() => {
    // In production, send to API and handle action
    queryClient.invalidateQueries({ queryKey: ['insights', userId] });
  }, [queryClient, userId]);

  // Start tour
  const startTour = useCallback((tourSlug: string) => {
    const tour = tours.find(t => t.slug === tourSlug);
    if (tour) {
      setActiveTour({ ...tour, status: 'in_progress', currentStep: 1 });
    }
  }, [tours]);

  // Skip tour
  const skipTour = useCallback((tourSlug: string) => {
    if (activeTour?.slug === tourSlug) {
      setActiveTour(null);
    }
    // In production, update API
    queryClient.invalidateQueries({ queryKey: ['tours', userId] });
  }, [activeTour, queryClient, userId]);

  // Next tour step
  const nextTourStep = useCallback(() => {
    if (!activeTour) return;

    if (activeTour.currentStep >= activeTour.totalSteps) {
      setActiveTour(null);
      queryClient.invalidateQueries({ queryKey: ['tours', userId] });
    } else {
      setActiveTour({
        ...activeTour,
        currentStep: activeTour.currentStep + 1,
        progressPercent: ((activeTour.currentStep + 1) / activeTour.totalSteps) * 100,
      });
    }
  }, [activeTour, queryClient, userId]);

  // Get help for page
  const getHelpForPage = useCallback((): ContextualHelp[] => {
    // In production, fetch from API
    // Filter out dismissed help
    return [];
  }, []);

  // Dismiss help
  const dismissHelp = useCallback((helpId: string) => {
    setHelpDismissed(prev => new Set(prev).add(helpId));
    // In production, send to API
  }, [setHelpDismissed]);

  // Get smart defaults
  const getSmartDefaults = useCallback((entityType: string) => {
    // In production, fetch from API with ML predictions
    const defaults: Record<string, Record<string, unknown>> = {
      opportunity: { stage: 'qualification', probability: 20 },
      task: { priority: 'medium', dueDays: 3 },
      contact: { status: 'active' },
    };
    return defaults[entityType] || {};
  }, []);

  // Track event
  const trackEvent = useCallback((eventType: string, eventData: Record<string, unknown>) => {
    // Send to analytics/tracking service
    // In production, this would batch events and send to API
    if (process.env.NODE_ENV === 'development') {
      console.log('Track event:', eventType, eventData);
    }
  }, []);

  // Set up keyboard shortcuts for quick actions
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      for (const action of quickActions) {
        if (!action.keyboardShortcut) continue;

        const parts = action.keyboardShortcut.toLowerCase().split('+');
        const key = parts.pop();
        const modifiers = parts;

        const matchesKey = e.key.toLowerCase() === key;
        const matchesCtrl = modifiers.includes('ctrl') === e.ctrlKey;
        const matchesShift = modifiers.includes('shift') === e.shiftKey;
        const matchesAlt = modifiers.includes('alt') === e.altKey;

        if (matchesKey && matchesCtrl && matchesShift && matchesAlt) {
          e.preventDefault();
          executeQuickAction(action.id);
          return;
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [quickActions, executeQuickAction]);

  // Track page views
  useEffect(() => {
    const handlePageView = () => {
      trackEvent('page_view', {
        path: window.location.pathname,
        timestamp: new Date().toISOString(),
      });
    };

    handlePageView();
    window.addEventListener('popstate', handlePageView);
    return () => window.removeEventListener('popstate', handlePageView);
  }, [trackEvent]);

  const value: PersonalizationContextType = {
    preferences: preferences || null,
    updatePreference,
    resetPreferences,
    quickActions,
    executeQuickAction,
    createQuickAction,
    deleteQuickAction,
    insights,
    dismissInsight,
    actOnInsight,
    tours,
    activeTour,
    startTour,
    skipTour,
    nextTourStep,
    getHelpForPage,
    dismissHelp,
    getSmartDefaults,
    trackEvent,
    uiAdaptations: uiAdaptations || null,
    isLoading: prefsLoading,
  };

  return (
    <PersonalizationContext.Provider value={value}>
      {children}
    </PersonalizationContext.Provider>
  );
}

// Hooks
export function usePersonalization(): PersonalizationContextType {
  const context = useContext(PersonalizationContext);
  if (!context) {
    throw new Error('usePersonalization must be used within PersonalizationProvider');
  }
  return context;
}

export function usePreferences() {
  const { preferences, updatePreference, resetPreferences, isLoading } = usePersonalization();
  return { preferences, updatePreference, resetPreferences, isLoading };
}

export function useQuickActions() {
  const { quickActions, executeQuickAction, createQuickAction, deleteQuickAction } = usePersonalization();
  return { quickActions, executeQuickAction, createQuickAction, deleteQuickAction };
}

export function useInsights() {
  const { insights, dismissInsight, actOnInsight } = usePersonalization();
  return { insights, dismissInsight, actOnInsight };
}

export function useOnboarding() {
  const { tours, activeTour, startTour, skipTour, nextTourStep } = usePersonalization();
  return { tours, activeTour, startTour, skipTour, nextTourStep };
}

export function useSmartDefaults(entityType: string, context?: Record<string, unknown>) {
  const { getSmartDefaults } = usePersonalization();
  return getSmartDefaults(entityType, context);
}

export function useTrackEvent() {
  const { trackEvent } = usePersonalization();
  return trackEvent;
}

// Utility Components
export function InsightBanner() {
  const { insights, dismissInsight, actOnInsight } = useInsights();
  const newInsights = insights.filter(i => i.status === 'new');

  if (newInsights.length === 0) return null;

  const insight = newInsights[0];

  return (
    <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-4">
      <div className="flex items-start">
        <div className="flex-1">
          <h4 className="text-sm font-medium text-blue-800">{insight.title}</h4>
          <p className="text-sm text-blue-700 mt-1">{insight.description}</p>
          {insight.recommendation && (
            <p className="text-sm text-blue-600 mt-1 italic">{insight.recommendation}</p>
          )}
        </div>
        <div className="flex gap-2 ml-4">
          <button
            onClick={() => actOnInsight(insight.id)}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            Take Action
          </button>
          <button
            onClick={() => dismissInsight(insight.id)}
            className="text-sm text-gray-500 hover:text-gray-700"
          >
            Dismiss
          </button>
        </div>
      </div>
    </div>
  );
}

export function OnboardingOverlay() {
  const { activeTour, nextTourStep, skipTour } = useOnboarding();

  if (!activeTour) return null;

  return (
    <div className="fixed inset-0 z-50 pointer-events-none">
      <div className="absolute inset-0 bg-black/50 pointer-events-auto" />
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 bg-white rounded-lg shadow-xl p-6 pointer-events-auto max-w-md">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-500">
            Step {activeTour.currentStep} of {activeTour.totalSteps}
          </span>
          <button
            onClick={() => skipTour(activeTour.slug)}
            className="text-sm text-gray-400 hover:text-gray-600"
          >
            Skip Tour
          </button>
        </div>
        <div className="w-full h-1 bg-gray-200 rounded mb-4">
          <div
            className="h-full bg-blue-500 rounded transition-all"
            style={{ width: `${activeTour.progressPercent}%` }}
          />
        </div>
        <h3 className="text-lg font-semibold mb-2">{activeTour.name}</h3>
        <p className="text-gray-600 mb-4">{activeTour.description}</p>
        <button
          onClick={nextTourStep}
          className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600"
        >
          {activeTour.currentStep >= activeTour.totalSteps ? 'Finish' : 'Next'}
        </button>
      </div>
    </div>
  );
}

export function CommandPalette() {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const { quickActions, executeQuickAction } = useQuickActions();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsOpen(prev => !prev);
      }
      if (e.key === 'Escape') {
        setIsOpen(false);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  const filteredActions = quickActions.filter(action =>
    action.name.toLowerCase().includes(query.toLowerCase())
  );

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-32">
      <div className="absolute inset-0 bg-black/50" onClick={() => setIsOpen(false)} />
      <div className="relative bg-white rounded-lg shadow-2xl w-full max-w-lg">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Type a command or search..."
          className="w-full px-4 py-3 text-lg border-b focus:outline-none"
          autoFocus
        />
        <div className="max-h-80 overflow-y-auto">
          {filteredActions.map(action => (
            <button
              key={action.id}
              onClick={() => {
                executeQuickAction(action.id);
                setIsOpen(false);
              }}
              className="w-full flex items-center justify-between px-4 py-3 hover:bg-gray-100 text-left"
            >
              <span>{action.name}</span>
              {action.keyboardShortcut && (
                <kbd className="text-xs bg-gray-200 px-2 py-1 rounded">
                  {action.keyboardShortcut}
                </kbd>
              )}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
