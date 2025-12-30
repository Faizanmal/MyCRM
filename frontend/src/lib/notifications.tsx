'use client';

import { createContext, useContext, useState, useCallback, ReactNode, useEffect } from 'react';
import { toast as sonnerToast } from 'sonner';
import { cn } from '@/lib/utils';

/**
 * Notification types and utilities
 */

export type NotificationType = 'success' | 'error' | 'warning' | 'info' | 'loading';

export interface Notification {
    id: string;
    type: NotificationType;
    title: string;
    message?: string;
    duration?: number;
    action?: {
        label: string;
        onClick: () => void;
    };
    dismissible?: boolean;
}

interface NotificationContextType {
    notifications: Notification[];
    addNotification: (notification: Omit<Notification, 'id'>) => string;
    removeNotification: (id: string) => void;
    clearAll: () => void;
    success: (title: string, message?: string) => string;
    error: (title: string, message?: string) => string;
    warning: (title: string, message?: string) => string;
    info: (title: string, message?: string) => string;
    loading: (title: string, message?: string) => string;
    update: (id: string, notification: Partial<Notification>) => void;
    promise: <T>(
        promise: Promise<T>,
        options: {
            loading: string;
            success: string | ((data: T) => string);
            error: string | ((err: Error) => string);
        }
    ) => Promise<T>;
}

const NotificationContext = createContext<NotificationContextType | null>(null);

export function useNotifications() {
    const context = useContext(NotificationContext);
    if (!context) {
        throw new Error('useNotifications must be used within NotificationProvider');
    }
    return context;
}

interface NotificationProviderProps {
    children: ReactNode;
    maxNotifications?: number;
    defaultDuration?: number;
}

export function NotificationProvider({
    children,
    maxNotifications = 5,
    defaultDuration = 5000,
}: NotificationProviderProps) {
    const [notifications, setNotifications] = useState<Notification[]>([]);

    const generateId = () => `notification-${Date.now()}-${Math.random().toString(36).slice(2)}`;

    const addNotification = useCallback((notification: Omit<Notification, 'id'>) => {
        const id = generateId();
        const newNotification: Notification = {
            id,
            dismissible: true,
            duration: defaultDuration,
            ...notification,
        };

        setNotifications(prev => {
            const updated = [newNotification, ...prev];
            return updated.slice(0, maxNotifications);
        });

        // Also show with sonner for better UX
        const toastFn = {
            success: sonnerToast.success,
            error: sonnerToast.error,
            warning: sonnerToast.warning,
            info: sonnerToast.info,
            loading: sonnerToast.loading,
        }[notification.type];

        toastFn(notification.title, {
            id,
            description: notification.message,
            duration: notification.duration,
            action: notification.action ? {
                label: notification.action.label,
                onClick: notification.action.onClick,
            } : undefined,
        });

        return id;
    }, [maxNotifications, defaultDuration]);

    const removeNotification = useCallback((id: string) => {
        setNotifications(prev => prev.filter(n => n.id !== id));
        sonnerToast.dismiss(id);
    }, []);

    const clearAll = useCallback(() => {
        setNotifications([]);
        sonnerToast.dismiss();
    }, []);

    const success = useCallback((title: string, message?: string) => {
        return addNotification({ type: 'success', title, message });
    }, [addNotification]);

    const error = useCallback((title: string, message?: string) => {
        return addNotification({ type: 'error', title, message, duration: 8000 });
    }, [addNotification]);

    const warning = useCallback((title: string, message?: string) => {
        return addNotification({ type: 'warning', title, message });
    }, [addNotification]);

    const info = useCallback((title: string, message?: string) => {
        return addNotification({ type: 'info', title, message });
    }, [addNotification]);

    const loading = useCallback((title: string, message?: string) => {
        return addNotification({ type: 'loading', title, message, duration: Infinity });
    }, [addNotification]);

    const update = useCallback((id: string, updates: Partial<Notification>) => {
        setNotifications(prev =>
            prev.map(n => (n.id === id ? { ...n, ...updates } : n))
        );

        if (updates.title || updates.message) {
            sonnerToast.message(updates.title || '', {
                id,
                description: updates.message,
            });
        }
    }, []);

    const promiseHandler = useCallback(async <T,>(
        promise: Promise<T>,
        options: {
            loading: string;
            success: string | ((data: T) => string);
            error: string | ((err: Error) => string);
        }
    ): Promise<T> => {
        const id = loading(options.loading);

        try {
            const result = await promise;
            removeNotification(id);
            const successMessage = typeof options.success === 'function'
                ? options.success(result)
                : options.success;
            success(successMessage);
            return result;
        } catch (err) {
            removeNotification(id);
            const errorMessage = typeof options.error === 'function'
                ? options.error(err as Error)
                : options.error;
            error(errorMessage);
            throw err;
        }
    }, [loading, removeNotification, success, error]);

    return (
        <NotificationContext.Provider
            value={{
                notifications,
                addNotification,
                removeNotification,
                clearAll,
                success,
                error,
                warning,
                info,
                loading,
                update,
                promise: promiseHandler,
            }}
        >
            {children}
        </NotificationContext.Provider>
    );
}

/**
 * API Error Handler utility
 */
export interface ApiError {
    status: number;
    message: string;
    code?: string;
    details?: Record<string, string[]>;
}

export function parseApiError(error: unknown): ApiError {
    // Axios error
    if (error && typeof error === 'object' && 'response' in error) {
        const response = (error as { response?: { status: number; data?: { message?: string; detail?: string; errors?: Record<string, string[]> } } }).response;
        if (response) {
            return {
                status: response.status,
                message: response.data?.message || response.data?.detail || 'An error occurred',
                details: response.data?.errors,
            };
        }
    }

    // Fetch error
    if (error instanceof Response) {
        return {
            status: error.status,
            message: error.statusText || 'An error occurred',
        };
    }

    // Standard Error
    if (error instanceof Error) {
        return {
            status: 500,
            message: error.message,
        };
    }

    // Unknown error
    return {
        status: 500,
        message: 'An unexpected error occurred',
    };
}

export function getErrorMessage(error: ApiError): string {
    const statusMessages: Record<number, string> = {
        400: 'Invalid request. Please check your input.',
        401: 'Please log in to continue.',
        403: 'You do not have permission to perform this action.',
        404: 'The requested resource was not found.',
        409: 'This action conflicts with an existing resource.',
        422: 'The provided data is invalid.',
        429: 'Too many requests. Please try again later.',
        500: 'Server error. Please try again later.',
        502: 'Service temporarily unavailable.',
        503: 'Service temporarily unavailable.',
    };

    return error.message || statusMessages[error.status] || 'An unexpected error occurred';
}

/**
 * Form error display component
 */
export function FormErrors({
    errors,
    className,
}: {
    errors?: Record<string, string[]>;
    className?: string;
}) {
    if (!errors || Object.keys(errors).length === 0) return null;

    return (
        <div className={cn('rounded-md bg-red-50 p-4', className)}>
            <div className="flex">
                <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                </div>
                <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-800">
                        Please fix the following errors:
                    </h3>
                    <div className="mt-2 text-sm text-red-700">
                        <ul className="list-disc pl-5 space-y-1">
                            {Object.entries(errors).map(([field, messages]) =>
                                messages.map((message, index) => (
                                    <li key={`${field}-${index}`}>
                                        <strong>{field}:</strong> {message}
                                    </li>
                                ))
                            )}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
}

/**
 * Confirmation dialog hook
 */
export function useConfirmation() {
    const [isOpen, setIsOpen] = useState(false);
    const [config, setConfig] = useState<{
        title: string;
        message: string;
        confirmLabel?: string;
        cancelLabel?: string;
        variant?: 'danger' | 'warning' | 'default';
        onConfirm: () => void | Promise<void>;
        onCancel?: () => void;
    } | null>(null);

    const confirm = useCallback((options: NonNullable<typeof config>) => {
        setConfig(options);
        setIsOpen(true);
    }, []);

    const handleConfirm = useCallback(async () => {
        if (config?.onConfirm) {
            await config.onConfirm();
        }
        setIsOpen(false);
        setConfig(null);
    }, [config]);

    const handleCancel = useCallback(() => {
        if (config?.onCancel) {
            config.onCancel();
        }
        setIsOpen(false);
        setConfig(null);
    }, [config]);

    return {
        isOpen,
        config,
        confirm,
        handleConfirm,
        handleCancel,
    };
}
