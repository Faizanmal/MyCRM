/**
 * Interactive Features Integration Tests
 * Tests for all interactive components and hooks
 *
 * To run these tests, install testing dependencies:
 * npm install -D vitest @testing-library/react @testing-library/react-hooks
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock API module
vi.mock('@/lib/api', () => ({
    preferencesAPI: {
        getPreferences: vi.fn(),
        updatePreferences: vi.fn(),
        saveDashboardLayout: vi.fn(),
        addRecentItem: vi.fn(),
    },
    onboardingAPI: {
        getStatus: vi.fn(),
        completeStep: vi.fn(),
        completeTour: vi.fn(),
        dismissTour: vi.fn(),
        resetProgress: vi.fn(),
    },
    recommendationsAPI: {
        getActive: vi.fn(),
        dismiss: vi.fn(),
        complete: vi.fn(),
        generate: vi.fn(),
    },
    globalSearchAPI: {
        search: vi.fn(),
        getRecentSearches: vi.fn(),
        clearHistory: vi.fn(),
    },
    smartFiltersAPI: {
        getFilters: vi.fn(),
        createFilter: vi.fn(),
        deleteFilter: vi.fn(),
        useFilter: vi.fn(),
    },
    quickActionsAPI: {
        getActions: vi.fn(),
        getPinnedActions: vi.fn(),
        createAction: vi.fn(),
        togglePin: vi.fn(),
        recordUse: vi.fn(),
    },
    activityAPI: {
        getNotifications: vi.fn(),
        markNotificationRead: vi.fn(),
        markAllNotificationsRead: vi.fn(),
    },
}));

// Import hooks after mocking
import {
    useUserPreferences,
    useOnboarding,
    useAIRecommendations,
    useGlobalSearch,
    useSmartFilters,
    useQuickActions,
    useKeyboardShortcut,
    useLocalStorage,
} from '@/hooks/useInteractiveFeatures';

import {
    preferencesAPI,
    onboardingAPI,
    recommendationsAPI,
    globalSearchAPI,
    smartFiltersAPI,
    quickActionsAPI,
} from '@/lib/api';

// ==================== User Preferences Tests ====================

describe('useUserPreferences', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        localStorage.clear();
    });

    it('should fetch preferences on mount', async () => {
        const mockPreferences = {
            theme: 'dark',
            sidebar_collapsed: false,
            dashboard_layout: { widgets: [] },
        };

        vi.mocked(preferencesAPI.getPreferences).mockResolvedValue(mockPreferences);

        const { result } = renderHook(() => useUserPreferences());

        expect(result.current.isLoading).toBe(true);

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(result.current.preferences).toEqual(mockPreferences);
        expect(preferencesAPI.getPreferences).toHaveBeenCalledTimes(1);
    });

    it('should update preferences', async () => {
        const initialPrefs = { theme: 'light', sidebar_collapsed: false };
        const updatedPrefs = { theme: 'dark', sidebar_collapsed: false };

        vi.mocked(preferencesAPI.getPreferences).mockResolvedValue(initialPrefs);
        vi.mocked(preferencesAPI.updatePreferences).mockResolvedValue(updatedPrefs);

        const { result } = renderHook(() => useUserPreferences());

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        await act(async () => {
            await result.current.updatePreferences({ theme: 'dark' });
        });

        expect(result.current.preferences?.theme).toBe('dark');
    });

    it('should fallback to localStorage on API error', async () => {
        const savedPrefs = { theme: 'system', sidebar_collapsed: true };
        localStorage.setItem('user_preferences', JSON.stringify(savedPrefs));

        vi.mocked(preferencesAPI.getPreferences).mockRejectedValue(new Error('API Error'));

        const { result } = renderHook(() => useUserPreferences());

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(result.current.preferences).toEqual(savedPrefs);
    });
});

// ==================== Onboarding Tests ====================

describe('useOnboarding', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        localStorage.clear();
    });

    it('should fetch onboarding status on mount', async () => {
        const mockStatus = {
            completed_steps: ['profile', 'first_contact'],
            tour_completed: false,
            tour_dismissed: false,
            onboarding_xp: 150,
            completion_percentage: 25,
        };

        vi.mocked(onboardingAPI.getStatus).mockResolvedValue(mockStatus);

        const { result } = renderHook(() => useOnboarding());

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(result.current.status).toEqual(mockStatus);
    });

    it('should complete a step and update XP', async () => {
        const initialStatus = {
            completed_steps: [],
            tour_completed: false,
            tour_dismissed: false,
            onboarding_xp: 0,
            completion_percentage: 0,
        };

        const afterComplete = {
            completed_steps: ['first_contact'],
            total_xp: 100,
        };

        vi.mocked(onboardingAPI.getStatus).mockResolvedValue(initialStatus);
        vi.mocked(onboardingAPI.completeStep).mockResolvedValue(afterComplete);

        const { result } = renderHook(() => useOnboarding());

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        await act(async () => {
            await result.current.completeStep('first_contact', 100);
        });

        expect(result.current.status?.completed_steps).toContain('first_contact');
    });

    it('should check if step is completed', async () => {
        const mockStatus = {
            completed_steps: ['profile', 'first_contact'],
            tour_completed: false,
            tour_dismissed: false,
            onboarding_xp: 150,
            completion_percentage: 25,
        };

        vi.mocked(onboardingAPI.getStatus).mockResolvedValue(mockStatus);

        const { result } = renderHook(() => useOnboarding());

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(result.current.isStepCompleted('profile')).toBe(true);
        expect(result.current.isStepCompleted('first_lead')).toBe(false);
    });
});

// ==================== AI Recommendations Tests ====================

describe('useAIRecommendations', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('should fetch active recommendations', async () => {
        const mockRecommendations = [
            {
                id: '1',
                recommendation_type: 'action',
                title: 'Follow up with lead',
                description: 'Test description',
                impact: 'high',
                dismissable: true,
            },
            {
                id: '2',
                recommendation_type: 'insight',
                title: 'Best contact time',
                description: 'Test description',
                impact: 'medium',
                dismissable: true,
            },
        ];

        vi.mocked(recommendationsAPI.getActive).mockResolvedValue(mockRecommendations);

        const { result } = renderHook(() => useAIRecommendations());

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(result.current.recommendations).toHaveLength(2);
        expect(result.current.highImpactCount).toBe(1);
    });

    it('should dismiss a recommendation', async () => {
        const mockRecommendations = [
            { id: '1', recommendation_type: 'action', title: 'Test', impact: 'high', dismissable: true },
        ];

        vi.mocked(recommendationsAPI.getActive).mockResolvedValue(mockRecommendations);
        vi.mocked(recommendationsAPI.dismiss).mockResolvedValue({ success: true });

        const { result } = renderHook(() => useAIRecommendations());

        await waitFor(() => {
            expect(result.current.recommendations).toHaveLength(1);
        });

        await act(async () => {
            await result.current.dismissRecommendation('1');
        });

        expect(result.current.recommendations).toHaveLength(0);
    });

    it('should count recommendations by type', async () => {
        const mockRecommendations = [
            { id: '1', recommendation_type: 'action', impact: 'high' },
            { id: '2', recommendation_type: 'action', impact: 'medium' },
            { id: '3', recommendation_type: 'insight', impact: 'low' },
        ];

        vi.mocked(recommendationsAPI.getActive).mockResolvedValue(mockRecommendations);

        const { result } = renderHook(() => useAIRecommendations());

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(result.current.byType).toEqual({
            action: 2,
            insight: 1,
        });
    });
});

// ==================== Global Search Tests ====================

describe('useGlobalSearch', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('should perform search and return results', async () => {
        const mockResults = {
            results: [
                { id: '1', type: 'contact', title: 'John Smith' },
                { id: '2', type: 'company', title: 'TechCorp' },
            ],
        };

        vi.mocked(globalSearchAPI.search).mockResolvedValue(mockResults);

        const { result } = renderHook(() => useGlobalSearch());

        await act(async () => {
            await result.current.search('John');
        });

        expect(result.current.results).toHaveLength(2);
        expect(result.current.query).toBe('John');
    });

    it('should clear results', async () => {
        const mockResults = { results: [{ id: '1', title: 'Test' }] };
        vi.mocked(globalSearchAPI.search).mockResolvedValue(mockResults);

        const { result } = renderHook(() => useGlobalSearch());

        await act(async () => {
            await result.current.search('test');
        });

        expect(result.current.results).toHaveLength(1);

        act(() => {
            result.current.clearResults();
        });

        expect(result.current.results).toHaveLength(0);
        expect(result.current.query).toBe('');
    });

    it('should not search for empty query', async () => {
        const { result } = renderHook(() => useGlobalSearch());

        await act(async () => {
            await result.current.search('');
        });

        expect(globalSearchAPI.search).not.toHaveBeenCalled();
        expect(result.current.results).toHaveLength(0);
    });
});

// ==================== Smart Filters Tests ====================

describe('useSmartFilters', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('should fetch filters on mount', async () => {
        const mockFilters = [
            { id: '1', name: 'Hot Leads', entity_type: 'lead', use_count: 5 },
            { id: '2', name: 'Enterprise Clients', entity_type: 'company', use_count: 3 },
        ];

        vi.mocked(smartFiltersAPI.getFilters).mockResolvedValue(mockFilters);

        const { result } = renderHook(() => useSmartFilters());

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(result.current.filters).toHaveLength(2);
    });

    it('should create a new filter', async () => {
        const newFilter = {
            id: '3',
            name: 'New Filter',
            entity_type: 'contact',
            filter_config: {},
            use_count: 0,
        };

        vi.mocked(smartFiltersAPI.getFilters).mockResolvedValue([]);
        vi.mocked(smartFiltersAPI.createFilter).mockResolvedValue(newFilter);

        const { result } = renderHook(() => useSmartFilters());

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        await act(async () => {
            await result.current.createFilter({
                name: 'New Filter',
                entity_type: 'contact',
                filter_config: {},
            });
        });

        expect(result.current.filters).toHaveLength(1);
    });
});

// ==================== Quick Actions Tests ====================

describe('useQuickActions', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('should fetch actions and pinned actions', async () => {
        const mockActions = [
            { id: '1', name: 'New Contact', is_pinned: true, use_count: 10 },
            { id: '2', name: 'New Deal', is_pinned: false, use_count: 5 },
        ];
        const mockPinned = [mockActions[0]];

        vi.mocked(quickActionsAPI.getActions).mockResolvedValue(mockActions);
        vi.mocked(quickActionsAPI.getPinnedActions).mockResolvedValue(mockPinned);

        const { result } = renderHook(() => useQuickActions());

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(result.current.actions).toHaveLength(2);
        expect(result.current.pinnedActions).toHaveLength(1);
    });

    it('should toggle pin status', async () => {
        const mockActions = [{ id: '1', name: 'Test', is_pinned: false, use_count: 0 }];

        vi.mocked(quickActionsAPI.getActions).mockResolvedValue(mockActions);
        vi.mocked(quickActionsAPI.getPinnedActions).mockResolvedValue([]);
        vi.mocked(quickActionsAPI.togglePin).mockResolvedValue({ is_pinned: true });

        const { result } = renderHook(() => useQuickActions());

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        await act(async () => {
            await result.current.togglePin('1');
        });

        expect(result.current.actions[0].is_pinned).toBe(true);
    });
});

// ==================== Keyboard Shortcut Tests ====================

describe('useKeyboardShortcut', () => {
    it('should call callback on shortcut press', () => {
        const callback = vi.fn();

        renderHook(() => useKeyboardShortcut('ctrl+k', callback));

        // Simulate keyboard event
        const event = new KeyboardEvent('keydown', {
            key: 'k',
            ctrlKey: true,
        });
        window.dispatchEvent(event);

        expect(callback).toHaveBeenCalledTimes(1);
    });

    it('should not call callback when disabled', () => {
        const callback = vi.fn();

        renderHook(() => useKeyboardShortcut('ctrl+k', callback, { enabled: false }));

        const event = new KeyboardEvent('keydown', {
            key: 'k',
            ctrlKey: true,
        });
        window.dispatchEvent(event);

        expect(callback).not.toHaveBeenCalled();
    });
});

// ==================== Local Storage Tests ====================

describe('useLocalStorage', () => {
    beforeEach(() => {
        localStorage.clear();
    });

    it('should initialize with default value', () => {
        const { result } = renderHook(() => useLocalStorage('test-key', 'default'));

        expect(result.current[0]).toBe('default');
    });

    it('should read from localStorage if exists', () => {
        localStorage.setItem('test-key', JSON.stringify('saved-value'));

        const { result } = renderHook(() => useLocalStorage('test-key', 'default'));

        expect(result.current[0]).toBe('saved-value');
    });

    it('should update localStorage on setValue', () => {
        const { result } = renderHook(() => useLocalStorage('test-key', 'initial'));

        act(() => {
            result.current[1]('updated');
        });

        expect(result.current[0]).toBe('updated');
        expect(JSON.parse(localStorage.getItem('test-key') || '')).toBe('updated');
    });

    it('should remove from localStorage', () => {
        localStorage.setItem('test-key', JSON.stringify('value'));

        const { result } = renderHook(() => useLocalStorage('test-key', 'default'));

        act(() => {
            result.current[2](); // removeValue
        });

        expect(result.current[0]).toBe('default');
        expect(localStorage.getItem('test-key')).toBeNull();
    });
});

// ==================== Component Integration Tests ====================

describe('Component Integration', () => {
    it('should handle API errors gracefully', async () => {
        vi.mocked(preferencesAPI.getPreferences).mockRejectedValue(new Error('Network Error'));

        const { result } = renderHook(() => useUserPreferences());

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(result.current.error).toBe('Failed to load preferences');
    });

    it('should refresh data on demand', async () => {
        const mockData = { theme: 'light' };
        vi.mocked(preferencesAPI.getPreferences).mockResolvedValue(mockData);

        const { result } = renderHook(() => useUserPreferences());

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(preferencesAPI.getPreferences).toHaveBeenCalledTimes(1);

        await act(async () => {
            await result.current.refresh();
        });

        expect(preferencesAPI.getPreferences).toHaveBeenCalledTimes(2);
    });
});
