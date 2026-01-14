'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';

import {
    preferencesAPI,
    onboardingAPI,
    recommendationsAPI,
    globalSearchAPI,
    smartFiltersAPI,
    quickActionsAPI
} from '@/lib/api';

// ==================== User Preferences Hook ====================

interface DashboardWidget {
    widget_id: string;
    visible: boolean;
    order: number;
    size?: 'small' | 'medium' | 'large';
}

interface UserPreferences {
    dashboard_layout: { widgets: DashboardWidget[] };
    sidebar_collapsed: boolean;
    theme: 'light' | 'dark' | 'system';
    accent_color: string;
    enable_sounds: boolean;
    enable_desktop_notifications: boolean;
    recent_items: Array<{ type: string; id: string; title: string; accessed_at: string }>;
}

export function useUserPreferences() {
    const [preferences, setPreferences] = useState<UserPreferences | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchPreferences = useCallback(async () => {
        try {
            setIsLoading(true);
            const data = await preferencesAPI.getPreferences();
            setPreferences(data);
            setError(null);
        } catch (err) {
            console.error("Failed to load preferences", err)
            setError('Failed to load preferences');
            // Use localStorage fallback
            const saved = localStorage.getItem('user_preferences');
            if (saved) {
                setPreferences(JSON.parse(saved));
            }
        } finally {
            setIsLoading(false);
        }
    }, []);

    const updatePreferences = useCallback(async (updates: Partial<UserPreferences>) => {
        try {
            const updated = await preferencesAPI.updatePreferences(updates);
            setPreferences(updated);
            localStorage.setItem('user_preferences', JSON.stringify(updated));
            return updated;
        } catch (err) {
            // Save locally if API fails
            const newPrefs = { ...preferences, ...updates };
            localStorage.setItem('user_preferences', JSON.stringify(newPrefs));
            setPreferences(newPrefs as UserPreferences);
            throw err;
        }
    }, [preferences]);

    const saveDashboardLayout = useCallback(async (widgets: DashboardWidget[]) => {
        try {
            await preferencesAPI.saveDashboardLayout(widgets);
            setPreferences(prev => prev ? { ...prev, dashboard_layout: { widgets } } : null);
        } catch (err) {
            console.error('Failed to save dashboard layout:', err);
        }
    }, []);

    const addRecentItem = useCallback(async (type: string, id: string, title: string) => {
        try {
            await preferencesAPI.addRecentItem(type, id, title);
        } catch (err) {
            console.error('Failed to add recent item:', err);
        }
    }, []);

    useEffect(() => {
        fetchPreferences();
    }, [fetchPreferences]);

    return {
        preferences,
        isLoading,
        error,
        updatePreferences,
        saveDashboardLayout,
        addRecentItem,
        refresh: fetchPreferences,
    };
}

// ==================== Onboarding Progress Hook ====================

interface OnboardingStatus {
    completed_steps: string[];
    tour_completed: boolean;
    tour_dismissed: boolean;
    onboarding_xp: number;
    completion_percentage: number;
}

export function useOnboarding() {
    const [status, setStatus] = useState<OnboardingStatus | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    const fetchStatus = useCallback(async () => {
        try {
            setIsLoading(true);
            const data = await onboardingAPI.getStatus();
            setStatus(data);
        } catch (err) {
            // Use localStorage fallback
            console.error("failed to onboarding", err)
            const saved = localStorage.getItem('mycrm_onboarding_checklist');
            if (saved) {
                const items = JSON.parse(saved);
                setStatus({
                    completed_steps: items.filter((i: { completed: boolean }) => i.completed).map((i: { id: string }) => i.id),
                    tour_completed: !!localStorage.getItem('mycrm_tour_completed'),
                    tour_dismissed: !!localStorage.getItem('mycrm_tour_dismissed'),
                    onboarding_xp: 0,
                    completion_percentage: 0,
                });
            }
        } finally {
            setIsLoading(false);
        }
    }, []);

    const completeStep = useCallback(async (stepId: string, xpReward: number = 50) => {
        try {
            const result = await onboardingAPI.completeStep(stepId, xpReward);
            setStatus(prev => prev ? {
                ...prev,
                completed_steps: result.completed_steps,
                onboarding_xp: result.total_xp,
            } : null);
            return result;
        } catch (err) {
            console.error('Failed to complete step:', err);
            throw err;
        }
    }, []);

    const completeTour = useCallback(async () => {
        try {
            await onboardingAPI.completeTour();
            setStatus(prev => prev ? { ...prev, tour_completed: true } : null);
        } catch (err) {
            console.error("Tour Failed", err)
            localStorage.setItem('mycrm_tour_completed', 'true');
        }
    }, []);

    const dismissTour = useCallback(async () => {
        try {
            await onboardingAPI.dismissTour();
            setStatus(prev => prev ? { ...prev, tour_dismissed: true } : null);
        } catch (err) {
            console.error("Failed to dismiss", err)
            localStorage.setItem('mycrm_tour_dismissed', 'true');
        }
    }, []);

    const isStepCompleted = useCallback((stepId: string) => {
        return status?.completed_steps.includes(stepId) ?? false;
    }, [status]);

    useEffect(() => {
        fetchStatus();
    }, [fetchStatus]);

    return {
        status,
        isLoading,
        completeStep,
        completeTour,
        dismissTour,
        isStepCompleted,
        refresh: fetchStatus,
    };
}

// ==================== AI Recommendations Hook ====================

interface AIRecommendation {
    id: string;
    recommendation_type: 'action' | 'insight' | 'warning' | 'opportunity' | 'tip';
    title: string;
    description: string;
    impact: 'high' | 'medium' | 'low';
    action_label: string;
    action_url: string;
    dismissable: boolean;
    confidence_score?: number;
}

export function useAIRecommendations(options?: { type?: string; impact?: string; limit?: number }) {
    const [recommendations, setRecommendations] = useState<AIRecommendation[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isGenerating, setIsGenerating] = useState(false);

    const fetchRecommendations = useCallback(async () => {
        try {
            setIsLoading(true);
            const data = await recommendationsAPI.getActive(options);
            setRecommendations(Array.isArray(data) ? data : []);
        } catch (err) {
            console.error('Failed to fetch recommendations:', err);
            setRecommendations([]);
        } finally {
            setIsLoading(false);
        }
    }, [options]);

    const dismissRecommendation = useCallback(async (id: string) => {
        try {
            await recommendationsAPI.dismiss(id);
            setRecommendations(prev => prev.filter(r => r.id !== id));
        } catch (err) {
            console.error('Failed to dismiss recommendation:', err);
        }
    }, []);

    const completeRecommendation = useCallback(async (id: string) => {
        try {
            await recommendationsAPI.complete(id);
            setRecommendations(prev => prev.filter(r => r.id !== id));
        } catch (err) {
            console.error('Failed to complete recommendation:', err);
        }
    }, []);

    const generateRecommendations = useCallback(async () => {
        try {
            setIsGenerating(true);
            const result = await recommendationsAPI.generate();
            await fetchRecommendations();
            return result;
        } catch (err) {
            console.error('Failed to generate recommendations:', err);
            throw err;
        } finally {
            setIsGenerating(false);
        }
    }, [fetchRecommendations]);

    // Computed properties
    const highImpactCount = useMemo(() =>
        recommendations.filter(r => r.impact === 'high').length,
        [recommendations]);

    const byType = useMemo(() => {
        return recommendations.reduce((acc, r) => {
            acc[r.recommendation_type] = (acc[r.recommendation_type] || 0) + 1;
            return acc;
        }, {} as Record<string, number>);
    }, [recommendations]);

    useEffect(() => {
        fetchRecommendations();
    }, [fetchRecommendations]);

    return {
        recommendations,
        isLoading,
        isGenerating,
        highImpactCount,
        byType,
        dismissRecommendation,
        completeRecommendation,
        generateRecommendations,
        refresh: fetchRecommendations,
    };
}

// ==================== Global Search Hook ====================

interface SearchResult {
    id: string;
    type: string;
    title: string;
    subtitle?: string;
    metadata?: string;
    score?: number;
    url: string;
}

export function useGlobalSearch() {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<SearchResult[]>([]);
    const [isSearching, setIsSearching] = useState(false);
    const [recentSearches, setRecentSearches] = useState<string[]>([]);

    const search = useCallback(async (searchQuery: string, options?: { types?: string[]; limit?: number }) => {
        if (!searchQuery.trim()) {
            setResults([]);
            return [];
        }

        try {
            setIsSearching(true);
            setQuery(searchQuery);
            const response = await globalSearchAPI.search(searchQuery, options);
            setResults(response.results || []);
            return response.results;
        } catch (err) {
            console.error('Search failed:', err);
            setResults([]);
            return [];
        } finally {
            setIsSearching(false);
        }
    }, []);

    const fetchRecentSearches = useCallback(async () => {
        try {
            const response = await globalSearchAPI.getRecentSearches();
            setRecentSearches(response.recent_searches || []);
        } catch (err) {
            console.error('Failed to fetch recent searches:', err);
        }
    }, []);

    const clearSearchHistory = useCallback(async () => {
        try {
            await globalSearchAPI.clearHistory();
            setRecentSearches([]);
        } catch (err) {
            console.error('Failed to clear search history:', err);
        }
    }, []);

    const clearResults = useCallback(() => {
        setQuery('');
        setResults([]);
    }, []);

    useEffect(() => {
        fetchRecentSearches();
    }, [fetchRecentSearches]);

    return {
        query,
        results,
        isSearching,
        recentSearches,
        search,
        clearResults,
        clearSearchHistory,
        refreshRecentSearches: fetchRecentSearches,
    };
}

// ==================== Smart Filters Hook ====================

interface SmartFilter {
    id: string;
    name: string;
    entity_type: string;
    filter_config: Record<string, unknown>;
    icon?: string;
    color?: string;
    use_count: number;
    is_shared: boolean;
    is_default: boolean;
}

export function useSmartFilters(entityType?: string) {
    const [filters, setFilters] = useState<SmartFilter[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    const fetchFilters = useCallback(async () => {
        try {
            setIsLoading(true);
            const data = await smartFiltersAPI.getFilters(entityType);
            setFilters(Array.isArray(data) ? data : data.results || []);
        } catch (err) {
            console.error('Failed to fetch filters:', err);
        } finally {
            setIsLoading(false);
        }
    }, [entityType]);

    const createFilter = useCallback(async (filterData: Omit<SmartFilter, 'id' | 'use_count'>) => {
        try {
            const created = await smartFiltersAPI.createFilter(filterData);
            setFilters(prev => [...prev, created]);
            return created;
        } catch (err) {
            console.error('Failed to create filter:', err);
            throw err;
        }
    }, []);

    const deleteFilter = useCallback(async (id: string) => {
        try {
            await smartFiltersAPI.deleteFilter(id);
            setFilters(prev => prev.filter(f => f.id !== id));
        } catch (err) {
            console.error('Failed to delete filter:', err);
            throw err;
        }
    }, []);

    const useFilter = useCallback(async (id: string) => {
        try {
            await smartFiltersAPI.useFilter(id);
            setFilters(prev => prev.map(f =>
                f.id === id ? { ...f, use_count: f.use_count + 1 } : f
            ));
        } catch (err) {
            console.error('Failed to record filter use:', err);
        }
    }, []);

    useEffect(() => {
        fetchFilters();
    }, [fetchFilters]);

    return {
        filters,
        isLoading,
        createFilter,
        deleteFilter,
        useFilter,
        refresh: fetchFilters,
    };
}

// ==================== Quick Actions Hook ====================

interface QuickAction {
    id: string;
    name: string;
    action_type: string;
    url?: string;
    icon?: string;
    color?: string;
    shortcut?: string;
    is_pinned: boolean;
    use_count: number;
}

export function useQuickActions() {
    const [actions, setActions] = useState<QuickAction[]>([]);
    const [pinnedActions, setPinnedActions] = useState<QuickAction[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    const fetchActions = useCallback(async () => {
        try {
            setIsLoading(true);
            const [allActions, pinned] = await Promise.all([
                quickActionsAPI.getActions(),
                quickActionsAPI.getPinnedActions(),
            ]);
            setActions(Array.isArray(allActions) ? allActions : allActions.results || []);
            setPinnedActions(Array.isArray(pinned) ? pinned : pinned.results || []);
        } catch (err) {
            console.error('Failed to fetch quick actions:', err);
        } finally {
            setIsLoading(false);
        }
    }, []);

    const createAction = useCallback(async (actionData: Omit<QuickAction, 'id' | 'is_pinned' | 'use_count'>) => {
        try {
            const created = await quickActionsAPI.createAction(actionData);
            setActions(prev => [...prev, created]);
            return created;
        } catch (err) {
            console.error('Failed to create quick action:', err);
            throw err;
        }
    }, []);

    const togglePin = useCallback(async (id: string) => {
        try {
            const result = await quickActionsAPI.togglePin(id);
            setActions(prev => prev.map(a =>
                a.id === id ? { ...a, is_pinned: result.is_pinned } : a
            ));
            // Refresh pinned list
            const pinned = await quickActionsAPI.getPinnedActions();
            setPinnedActions(Array.isArray(pinned) ? pinned : pinned.results || []);
        } catch (err) {
            console.error('Failed to toggle pin:', err);
        }
    }, []);

    const recordUse = useCallback(async (id: string) => {
        try {
            await quickActionsAPI.recordUse(id);
            setActions(prev => prev.map(a =>
                a.id === id ? { ...a, use_count: a.use_count + 1 } : a
            ));
        } catch (err) {
            console.error('Failed to record action use:', err);
        }
    }, []);

    useEffect(() => {
        fetchActions();
    }, [fetchActions]);

    return {
        actions,
        pinnedActions,
        isLoading,
        createAction,
        togglePin,
        recordUse,
        refresh: fetchActions,
    };
}

// ==================== Keyboard Shortcut Registration Hook ====================

type KeyboardCallback = (event: KeyboardEvent) => void;

export function useKeyboardShortcut(
    shortcut: string,
    callback: KeyboardCallback,
    options: { enabled?: boolean; preventDefault?: boolean } = {}
) {
    const { enabled = true, preventDefault = true } = options;

    useEffect(() => {
        if (!enabled) return;

        const handleKeyDown = (event: KeyboardEvent) => {
            const parts = shortcut.toLowerCase().split('+');
            const key = parts[parts.length - 1];
            const requiresMeta = parts.includes('meta') || parts.includes('cmd') || parts.includes('⌘');
            const requiresCtrl = parts.includes('ctrl') || parts.includes('control');
            const requiresShift = parts.includes('shift');
            const requiresAlt = parts.includes('alt') || parts.includes('option');

            const metaPressed = event.metaKey || event.ctrlKey;
            const shiftPressed = event.shiftKey;
            const altPressed = event.altKey;

            const keyMatches = event.key.toLowerCase() === key;
            const modifiersMatch =
                (!requiresMeta || metaPressed) &&
                (!requiresCtrl || event.ctrlKey) &&
                (!requiresShift || shiftPressed) &&
                (!requiresAlt || altPressed);

            if (keyMatches && modifiersMatch) {
                if (preventDefault) {
                    event.preventDefault();
                }
                callback(event);
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [shortcut, callback, enabled, preventDefault]);
}

// ==================== Local Storage Sync Hook ====================

export function useLocalStorage<T>(key: string, initialValue: T) {
    const [storedValue, setStoredValue] = useState<T>(() => {
        if (typeof window === 'undefined') return initialValue;
        try {
            const item = window.localStorage.getItem(key);
            return item ? JSON.parse(item) : initialValue;
        } catch (error) {
            console.error(`Error reading localStorage key "${key}":`, error);
            return initialValue;
        }
    });

    const setValue = useCallback((value: T | ((val: T) => T)) => {
        try {
            const valueToStore = value instanceof Function ? value(storedValue) : value;
            setStoredValue(valueToStore);
            if (typeof window !== 'undefined') {
                window.localStorage.setItem(key, JSON.stringify(valueToStore));
            }
        } catch (error) {
            console.error(`Error setting localStorage key "${key}":`, error);
        }
    }, [key, storedValue]);

    const removeValue = useCallback(() => {
        try {
            if (typeof window !== 'undefined') {
                window.localStorage.removeItem(key);
            }
            setStoredValue(initialValue);
        } catch (error) {
            console.error(`Error removing localStorage key "${key}":`, error);
        }
    }, [key, initialValue]);

    return [storedValue, setValue, removeValue] as const;
}

