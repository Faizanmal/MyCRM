/**
 * Hooks Index
 * Export all custom hooks for easy importing
 */

// Interactive Features Hooks
export {
    useUserPreferences,
    useOnboarding,
    useAIRecommendations,
    useGlobalSearch,
    useSmartFilters,
    useQuickActions,
    useKeyboardShortcut,
    useLocalStorage,
} from './useInteractiveFeatures';

// Real-time Notifications
export {
    RealtimeNotificationProvider,
    useRealtime,
    useRealtimeSubscription,
    useRealtimeNotifications,
} from './useRealtimeNotifications';

// Re-export existing hooks if any
export * from './useApi';

