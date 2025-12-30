'use client';

import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';

/**
 * Internationalization (i18n) System
 * 
 * Provides:
 * - Multi-language support
 * - Locale detection
 * - Number/Date formatting
 * - Pluralization
 */

// Supported locales
export type Locale = 'en' | 'es' | 'fr' | 'de' | 'pt' | 'ja' | 'zh';

export const locales: { code: Locale; name: string; flag: string }[] = [
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'es', name: 'Español', flag: '🇪🇸' },
    { code: 'fr', name: 'Français', flag: '🇫🇷' },
    { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
    { code: 'pt', name: 'Português', flag: '🇧🇷' },
    { code: 'ja', name: '日本語', flag: '🇯🇵' },
    { code: 'zh', name: '中文', flag: '🇨🇳' },
];

// Translation messages type
type Messages = {
    [key: string]: string | Messages;
};

// English translations (default)
const en: Messages = {
    common: {
        save: 'Save',
        cancel: 'Cancel',
        delete: 'Delete',
        edit: 'Edit',
        create: 'Create',
        search: 'Search',
        filter: 'Filter',
        export: 'Export',
        import: 'Import',
        loading: 'Loading...',
        noResults: 'No results found',
        error: 'An error occurred',
        success: 'Success',
        confirm: 'Confirm',
        back: 'Back',
        next: 'Next',
        previous: 'Previous',
        all: 'All',
        none: 'None',
        select: 'Select',
        close: 'Close',
        actions: 'Actions',
        view: 'View',
        more: 'More',
        less: 'Less',
    },
    auth: {
        login: 'Log In',
        logout: 'Log Out',
        register: 'Register',
        forgotPassword: 'Forgot Password?',
        resetPassword: 'Reset Password',
        email: 'Email',
        password: 'Password',
        confirmPassword: 'Confirm Password',
        rememberMe: 'Remember me',
        signInWith: 'Sign in with {provider}',
        noAccount: "Don't have an account?",
        hasAccount: 'Already have an account?',
    },
    navigation: {
        dashboard: 'Dashboard',
        leads: 'Leads',
        contacts: 'Contacts',
        opportunities: 'Opportunities',
        tasks: 'Tasks',
        calendar: 'Calendar',
        reports: 'Reports',
        settings: 'Settings',
        help: 'Help',
        profile: 'Profile',
    },
    leads: {
        title: 'Leads',
        newLead: 'New Lead',
        leadDetails: 'Lead Details',
        status: 'Status',
        source: 'Source',
        score: 'Score',
        assignedTo: 'Assigned To',
        createdAt: 'Created At',
        lastContact: 'Last Contact',
        statuses: {
            new: 'New',
            contacted: 'Contacted',
            qualified: 'Qualified',
            proposal: 'Proposal',
            won: 'Won',
            lost: 'Lost',
        },
    },
    contacts: {
        title: 'Contacts',
        newContact: 'New Contact',
        contactDetails: 'Contact Details',
        firstName: 'First Name',
        lastName: 'Last Name',
        email: 'Email',
        phone: 'Phone',
        company: 'Company',
        jobTitle: 'Job Title',
        address: 'Address',
        notes: 'Notes',
    },
    opportunities: {
        title: 'Opportunities',
        newOpportunity: 'New Opportunity',
        opportunityDetails: 'Opportunity Details',
        value: 'Value',
        stage: 'Stage',
        probability: 'Probability',
        expectedClose: 'Expected Close',
        stages: {
            prospecting: 'Prospecting',
            qualification: 'Qualification',
            proposal: 'Proposal',
            negotiation: 'Negotiation',
            closedWon: 'Closed Won',
            closedLost: 'Closed Lost',
        },
    },
    tasks: {
        title: 'Tasks',
        newTask: 'New Task',
        taskDetails: 'Task Details',
        dueDate: 'Due Date',
        priority: 'Priority',
        completed: 'Completed',
        priorities: {
            low: 'Low',
            medium: 'Medium',
            high: 'High',
            urgent: 'Urgent',
        },
    },
    dashboard: {
        title: 'Dashboard',
        welcome: 'Welcome back, {name}!',
        overview: 'Overview',
        recentActivity: 'Recent Activity',
        upcomingTasks: 'Upcoming Tasks',
        topDeals: 'Top Deals',
        metrics: {
            totalLeads: 'Total Leads',
            activeDeals: 'Active Deals',
            revenue: 'Revenue',
            tasksCompleted: 'Tasks Completed',
        },
    },
    errors: {
        required: 'This field is required',
        invalidEmail: 'Please enter a valid email address',
        invalidPhone: 'Please enter a valid phone number',
        minLength: 'Must be at least {min} characters',
        maxLength: 'Must be at most {max} characters',
        passwordMismatch: 'Passwords do not match',
        networkError: 'Network error. Please try again.',
        unauthorized: 'Please log in to continue.',
        forbidden: 'You do not have permission to perform this action.',
        notFound: 'The requested resource was not found.',
        serverError: 'Server error. Please try again later.',
    },
};

// Spanish translations
const es: Messages = {
    common: {
        save: 'Guardar',
        cancel: 'Cancelar',
        delete: 'Eliminar',
        edit: 'Editar',
        create: 'Crear',
        search: 'Buscar',
        filter: 'Filtrar',
        export: 'Exportar',
        import: 'Importar',
        loading: 'Cargando...',
        noResults: 'No se encontraron resultados',
        error: 'Ocurrió un error',
        success: 'Éxito',
        confirm: 'Confirmar',
        back: 'Atrás',
        next: 'Siguiente',
        previous: 'Anterior',
        all: 'Todos',
        none: 'Ninguno',
        select: 'Seleccionar',
        close: 'Cerrar',
        actions: 'Acciones',
        view: 'Ver',
        more: 'Más',
        less: 'Menos',
    },
    auth: {
        login: 'Iniciar Sesión',
        logout: 'Cerrar Sesión',
        register: 'Registrarse',
        forgotPassword: '¿Olvidaste tu contraseña?',
        resetPassword: 'Restablecer Contraseña',
        email: 'Correo Electrónico',
        password: 'Contraseña',
        confirmPassword: 'Confirmar Contraseña',
        rememberMe: 'Recordarme',
        signInWith: 'Iniciar sesión con {provider}',
        noAccount: '¿No tienes una cuenta?',
        hasAccount: '¿Ya tienes una cuenta?',
    },
    navigation: {
        dashboard: 'Panel',
        leads: 'Prospectos',
        contacts: 'Contactos',
        opportunities: 'Oportunidades',
        tasks: 'Tareas',
        calendar: 'Calendario',
        reports: 'Informes',
        settings: 'Configuración',
        help: 'Ayuda',
        profile: 'Perfil',
    },
    leads: {
        title: 'Prospectos',
        newLead: 'Nuevo Prospecto',
        leadDetails: 'Detalles del Prospecto',
        status: 'Estado',
        source: 'Fuente',
        score: 'Puntuación',
        assignedTo: 'Asignado A',
        createdAt: 'Creado El',
        lastContact: 'Último Contacto',
        statuses: {
            new: 'Nuevo',
            contacted: 'Contactado',
            qualified: 'Calificado',
            proposal: 'Propuesta',
            won: 'Ganado',
            lost: 'Perdido',
        },
    },
    dashboard: {
        title: 'Panel',
        welcome: '¡Bienvenido de nuevo, {name}!',
        overview: 'Resumen',
        recentActivity: 'Actividad Reciente',
        upcomingTasks: 'Próximas Tareas',
        topDeals: 'Mejores Negocios',
        metrics: {
            totalLeads: 'Total de Prospectos',
            activeDeals: 'Negocios Activos',
            revenue: 'Ingresos',
            tasksCompleted: 'Tareas Completadas',
        },
    },
    errors: {
        required: 'Este campo es obligatorio',
        invalidEmail: 'Por favor, ingrese un correo electrónico válido',
        invalidPhone: 'Por favor, ingrese un número de teléfono válido',
        minLength: 'Debe tener al menos {min} caracteres',
        maxLength: 'Debe tener como máximo {max} caracteres',
        passwordMismatch: 'Las contraseñas no coinciden',
        networkError: 'Error de red. Por favor, inténtelo de nuevo.',
        unauthorized: 'Por favor, inicie sesión para continuar.',
        forbidden: 'No tiene permiso para realizar esta acción.',
        notFound: 'El recurso solicitado no fue encontrado.',
        serverError: 'Error del servidor. Por favor, inténtelo más tarde.',
    },
};

// All translations
const translations: Record<Locale, Messages> = {
    en,
    es,
    fr: en, // Fallback to English
    de: en,
    pt: en,
    ja: en,
    zh: en,
};

// i18n Context
interface I18nContextType {
    locale: Locale;
    setLocale: (locale: Locale) => void;
    t: (key: string, params?: Record<string, string | number>) => string;
    formatNumber: (value: number, options?: Intl.NumberFormatOptions) => string;
    formatCurrency: (value: number, currency?: string) => string;
    formatDate: (date: Date | string, options?: Intl.DateTimeFormatOptions) => string;
    formatRelativeTime: (date: Date | string) => string;
}

const I18nContext = createContext<I18nContextType | null>(null);

export function useI18n() {
    const context = useContext(I18nContext);
    if (!context) {
        throw new Error('useI18n must be used within I18nProvider');
    }
    return context;
}

// Shorthand hook for translations
export function useTranslation() {
    const { t } = useI18n();
    return t;
}

interface I18nProviderProps {
    children: ReactNode;
    defaultLocale?: Locale;
}

export function I18nProvider({ children, defaultLocale = 'en' }: I18nProviderProps) {
    const [locale, setLocaleState] = useState<Locale>(() => {
        // Try to get from localStorage or browser
        if (typeof window !== 'undefined') {
            const stored = localStorage.getItem('locale') as Locale;
            if (stored && locales.some(l => l.code === stored)) {
                return stored;
            }

            // Try browser language
            const browserLang = navigator.language.split('-')[0] as Locale;
            if (locales.some(l => l.code === browserLang)) {
                return browserLang;
            }
        }
        return defaultLocale;
    });

    const setLocale = useCallback((newLocale: Locale) => {
        setLocaleState(newLocale);
        if (typeof window !== 'undefined') {
            localStorage.setItem('locale', newLocale);
            document.documentElement.lang = newLocale;
        }
    }, []);

    // Translation function
    const t = useCallback((key: string, params?: Record<string, string | number>): string => {
        const keys = key.split('.');
        let value: unknown = translations[locale];

        for (const k of keys) {
            if (value && typeof value === 'object' && k in value) {
                value = (value as Messages)[k];
            } else {
                // Fallback to English
                value = translations.en;
                for (const fallbackKey of keys) {
                    if (value && typeof value === 'object' && fallbackKey in value) {
                        value = (value as Messages)[fallbackKey];
                    } else {
                        return key; // Return key if not found
                    }
                }
                break;
            }
        }

        if (typeof value !== 'string') {
            return key;
        }

        // Replace parameters
        if (params) {
            return value.replace(/\{(\w+)\}/g, (_, param) =>
                params[param]?.toString() ?? `{${param}}`
            );
        }

        return value;
    }, [locale]);

    // Number formatting
    const formatNumber = useCallback((value: number, options?: Intl.NumberFormatOptions): string => {
        return new Intl.NumberFormat(locale, options).format(value);
    }, [locale]);

    // Currency formatting
    const formatCurrency = useCallback((value: number, currency = 'USD'): string => {
        return new Intl.NumberFormat(locale, {
            style: 'currency',
            currency,
        }).format(value);
    }, [locale]);

    // Date formatting
    const formatDate = useCallback((date: Date | string, options?: Intl.DateTimeFormatOptions): string => {
        const dateObj = typeof date === 'string' ? new Date(date) : date;
        return new Intl.DateTimeFormat(locale, {
            dateStyle: 'medium',
            ...options,
        }).format(dateObj);
    }, [locale]);

    // Relative time formatting
    const formatRelativeTime = useCallback((date: Date | string): string => {
        const dateObj = typeof date === 'string' ? new Date(date) : date;
        const now = new Date();
        const diffInSeconds = Math.floor((now.getTime() - dateObj.getTime()) / 1000);

        const rtf = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' });

        if (diffInSeconds < 60) {
            return rtf.format(-diffInSeconds, 'second');
        } else if (diffInSeconds < 3600) {
            return rtf.format(-Math.floor(diffInSeconds / 60), 'minute');
        } else if (diffInSeconds < 86400) {
            return rtf.format(-Math.floor(diffInSeconds / 3600), 'hour');
        } else if (diffInSeconds < 2592000) {
            return rtf.format(-Math.floor(diffInSeconds / 86400), 'day');
        } else if (diffInSeconds < 31536000) {
            return rtf.format(-Math.floor(diffInSeconds / 2592000), 'month');
        } else {
            return rtf.format(-Math.floor(diffInSeconds / 31536000), 'year');
        }
    }, [locale]);

    return (
        <I18nContext.Provider
            value={{
                locale,
                setLocale,
                t,
                formatNumber,
                formatCurrency,
                formatDate,
                formatRelativeTime,
            }}
        >
            {children}
        </I18nContext.Provider>
    );
}

// Language Selector Component
export function LanguageSelector({ className }: { className?: string }) {
    const { locale, setLocale } = useI18n();

    return (
        <select
            value={locale}
            onChange={(e) => setLocale(e.target.value as Locale)}
            className={`px-3 py-2 border rounded-md bg-white ${className}`}
        >
            {locales.map((l) => (
                <option key={l.code} value={l.code}>
                    {l.flag} {l.name}
                </option>
            ))}
        </select>
    );
}

export default {
    I18nProvider,
    useI18n,
    useTranslation,
    LanguageSelector,
    locales,
};
