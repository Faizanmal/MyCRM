'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// Types
interface LocaleSettings {
  language: string;
  languageName: string | null;
  currency: string;
  currencySymbol: string | null;
  timezone: string;
  timezoneOffset: string | null;
  dateFormat: string;
  timeFormat: string;
  firstDayOfWeek: number;
  isRtl: boolean;
}

interface Language {
  code: string;
  name: string;
  nativeName: string;
  isRtl: boolean;
  coverage: number;
}

interface Currency {
  code: string;
  name: string;
  symbol: string;
  decimalPlaces: number;
}

interface Timezone {
  name: string;
  displayName: string;
  offset: string;
}

interface I18nContextType {
  locale: LocaleSettings;
  languages: Language[];
  currencies: Currency[];
  timezones: Timezone[];
  t: (key: string, interpolations?: Record<string, string | number>) => string;
  formatDate: (date: Date | string, format?: string) => string;
  formatTime: (date: Date | string, format?: string) => string;
  formatDateTime: (date: Date | string) => string;
  formatNumber: (num: number, options?: Intl.NumberFormatOptions) => string;
  formatCurrency: (amount: number, currencyCode?: string) => string;
  setLanguage: (code: string) => Promise<void>;
  setCurrency: (code: string) => Promise<void>;
  setTimezone: (name: string) => Promise<void>;
  isLoading: boolean;
}

// Mock API functions
const fetchTranslations = async (languageCode: string): Promise<Record<string, string>> => {
  // In production, fetch from backend
  const translations: Record<string, Record<string, string>> = {
    'en-US': {
      'common.save': 'Save',
      'common.cancel': 'Cancel',
      'common.delete': 'Delete',
      'common.edit': 'Edit',
      'common.search': 'Search',
      'common.loading': 'Loading...',
      'common.noResults': 'No results found',
      'dashboard.title': 'Dashboard',
      'dashboard.welcome': 'Welcome, {name}!',
      'contacts.title': 'Contacts',
      'contacts.addNew': 'Add New Contact',
      'deals.title': 'Deals',
      'deals.pipeline': 'Pipeline',
      'settings.title': 'Settings',
      'settings.language': 'Language',
      'settings.timezone': 'Timezone',
      'settings.currency': 'Currency',
    },
    'es-ES': {
      'common.save': 'Guardar',
      'common.cancel': 'Cancelar',
      'common.delete': 'Eliminar',
      'common.edit': 'Editar',
      'common.search': 'Buscar',
      'common.loading': 'Cargando...',
      'common.noResults': 'No se encontraron resultados',
      'dashboard.title': 'Panel de Control',
      'dashboard.welcome': '¡Bienvenido, {name}!',
      'contacts.title': 'Contactos',
      'contacts.addNew': 'Añadir Nuevo Contacto',
      'deals.title': 'Negocios',
      'deals.pipeline': 'Pipeline',
      'settings.title': 'Configuración',
      'settings.language': 'Idioma',
      'settings.timezone': 'Zona Horaria',
      'settings.currency': 'Moneda',
    },
    'fr-FR': {
      'common.save': 'Enregistrer',
      'common.cancel': 'Annuler',
      'common.delete': 'Supprimer',
      'common.edit': 'Modifier',
      'common.search': 'Rechercher',
      'common.loading': 'Chargement...',
      'common.noResults': 'Aucun résultat trouvé',
      'dashboard.title': 'Tableau de Bord',
      'dashboard.welcome': 'Bienvenue, {name}!',
      'contacts.title': 'Contacts',
      'contacts.addNew': 'Ajouter un Contact',
      'deals.title': 'Affaires',
      'deals.pipeline': 'Pipeline',
      'settings.title': 'Paramètres',
      'settings.language': 'Langue',
      'settings.timezone': 'Fuseau Horaire',
      'settings.currency': 'Devise',
    },
    'de-DE': {
      'common.save': 'Speichern',
      'common.cancel': 'Abbrechen',
      'common.delete': 'Löschen',
      'common.edit': 'Bearbeiten',
      'common.search': 'Suchen',
      'common.loading': 'Laden...',
      'common.noResults': 'Keine Ergebnisse gefunden',
      'dashboard.title': 'Dashboard',
      'dashboard.welcome': 'Willkommen, {name}!',
      'contacts.title': 'Kontakte',
      'contacts.addNew': 'Neuen Kontakt hinzufügen',
      'deals.title': 'Geschäfte',
      'deals.pipeline': 'Pipeline',
      'settings.title': 'Einstellungen',
      'settings.language': 'Sprache',
      'settings.timezone': 'Zeitzone',
      'settings.currency': 'Währung',
    },
    'ja-JP': {
      'common.save': '保存',
      'common.cancel': 'キャンセル',
      'common.delete': '削除',
      'common.edit': '編集',
      'common.search': '検索',
      'common.loading': '読み込み中...',
      'common.noResults': '結果が見つかりません',
      'dashboard.title': 'ダッシュボード',
      'dashboard.welcome': 'ようこそ、{name}さん！',
      'contacts.title': '連絡先',
      'contacts.addNew': '新しい連絡先を追加',
      'deals.title': '取引',
      'deals.pipeline': 'パイプライン',
      'settings.title': '設定',
      'settings.language': '言語',
      'settings.timezone': 'タイムゾーン',
      'settings.currency': '通貨',
    },
    'ar-SA': {
      'common.save': 'حفظ',
      'common.cancel': 'إلغاء',
      'common.delete': 'حذف',
      'common.edit': 'تعديل',
      'common.search': 'بحث',
      'common.loading': 'جار التحميل...',
      'common.noResults': 'لم يتم العثور على نتائج',
      'dashboard.title': 'لوحة التحكم',
      'dashboard.welcome': 'مرحباً، {name}!',
      'contacts.title': 'جهات الاتصال',
      'contacts.addNew': 'إضافة جهة اتصال جديدة',
      'deals.title': 'الصفقات',
      'deals.pipeline': 'خط الأنابيب',
      'settings.title': 'الإعدادات',
      'settings.language': 'اللغة',
      'settings.timezone': 'المنطقة الزمنية',
      'settings.currency': 'العملة',
    },
  };

  return translations[languageCode] || translations['en-US'];
};

const fetchLocaleSettings = async (): Promise<LocaleSettings> => {
  // In production, fetch from user preferences
  return {
    language: 'en-US',
    languageName: 'English (US)',
    currency: 'USD',
    currencySymbol: '$',
    timezone: 'America/New_York',
    timezoneOffset: '-05:00',
    dateFormat: 'MM/DD/YYYY',
    timeFormat: 'h:mm A',
    firstDayOfWeek: 0,
    isRtl: false,
  };
};

const fetchLanguages = async (): Promise<Language[]> => {
  return [
    { code: 'en-US', name: 'English (US)', nativeName: 'English', isRtl: false, coverage: 100 },
    { code: 'es-ES', name: 'Spanish', nativeName: 'Español', isRtl: false, coverage: 95 },
    { code: 'fr-FR', name: 'French', nativeName: 'Français', isRtl: false, coverage: 92 },
    { code: 'de-DE', name: 'German', nativeName: 'Deutsch', isRtl: false, coverage: 88 },
    { code: 'ja-JP', name: 'Japanese', nativeName: '日本語', isRtl: false, coverage: 82 },
    { code: 'zh-CN', name: 'Chinese (Simplified)', nativeName: '简体中文', isRtl: false, coverage: 78 },
    { code: 'pt-BR', name: 'Portuguese (Brazil)', nativeName: 'Português', isRtl: false, coverage: 75 },
    { code: 'ar-SA', name: 'Arabic', nativeName: 'العربية', isRtl: true, coverage: 70 },
    { code: 'he-IL', name: 'Hebrew', nativeName: 'עברית', isRtl: true, coverage: 65 },
  ];
};

const fetchCurrencies = async (): Promise<Currency[]> => {
  return [
    { code: 'USD', name: 'US Dollar', symbol: '$', decimalPlaces: 2 },
    { code: 'EUR', name: 'Euro', symbol: '€', decimalPlaces: 2 },
    { code: 'GBP', name: 'British Pound', symbol: '£', decimalPlaces: 2 },
    { code: 'JPY', name: 'Japanese Yen', symbol: '¥', decimalPlaces: 0 },
    { code: 'CNY', name: 'Chinese Yuan', symbol: '¥', decimalPlaces: 2 },
    { code: 'CAD', name: 'Canadian Dollar', symbol: 'C$', decimalPlaces: 2 },
    { code: 'AUD', name: 'Australian Dollar', symbol: 'A$', decimalPlaces: 2 },
    { code: 'CHF', name: 'Swiss Franc', symbol: 'CHF', decimalPlaces: 2 },
    { code: 'INR', name: 'Indian Rupee', symbol: '₹', decimalPlaces: 2 },
    { code: 'BRL', name: 'Brazilian Real', symbol: 'R$', decimalPlaces: 2 },
  ];
};

const fetchTimezones = async (): Promise<Timezone[]> => {
  return [
    { name: 'America/New_York', displayName: 'Eastern Time (US)', offset: '-05:00' },
    { name: 'America/Chicago', displayName: 'Central Time (US)', offset: '-06:00' },
    { name: 'America/Denver', displayName: 'Mountain Time (US)', offset: '-07:00' },
    { name: 'America/Los_Angeles', displayName: 'Pacific Time (US)', offset: '-08:00' },
    { name: 'Europe/London', displayName: 'London', offset: '+00:00' },
    { name: 'Europe/Paris', displayName: 'Paris', offset: '+01:00' },
    { name: 'Europe/Berlin', displayName: 'Berlin', offset: '+01:00' },
    { name: 'Asia/Tokyo', displayName: 'Tokyo', offset: '+09:00' },
    { name: 'Asia/Shanghai', displayName: 'Shanghai', offset: '+08:00' },
    { name: 'Asia/Singapore', displayName: 'Singapore', offset: '+08:00' },
    { name: 'Asia/Dubai', displayName: 'Dubai', offset: '+04:00' },
    { name: 'Australia/Sydney', displayName: 'Sydney', offset: '+11:00' },
  ];
};

// Context
const I18nContext = createContext<I18nContextType | null>(null);

// Provider
export function I18nProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const [translations, setTranslations] = useState<Record<string, string>>({});

  const { data: locale, isLoading: localeLoading } = useQuery({
    queryKey: ['user-locale'],
    queryFn: fetchLocaleSettings,
  });

  const { data: languages = [] } = useQuery({
    queryKey: ['languages'],
    queryFn: fetchLanguages,
  });

  const { data: currencies = [] } = useQuery({
    queryKey: ['currencies'],
    queryFn: fetchCurrencies,
  });

  const { data: timezones = [] } = useQuery({
    queryKey: ['timezones'],
    queryFn: fetchTimezones,
  });

  // Load translations when language changes
  useEffect(() => {
    if (locale?.language) {
      fetchTranslations(locale.language).then(setTranslations);
    }
  }, [locale?.language]);

  // Apply RTL
  useEffect(() => {
    if (locale?.isRtl) {
      document.documentElement.dir = 'rtl';
      document.documentElement.lang = locale.language;
    } else {
      document.documentElement.dir = 'ltr';
      document.documentElement.lang = locale?.language || 'en';
    }
  }, [locale?.isRtl, locale?.language]);

  const t = (key: string, interpolations?: Record<string, string | number>): string => {
    let value = translations[key] || key;

    if (interpolations) {
      Object.entries(interpolations).forEach(([k, v]) => {
        value = value.replace(`{${k}}`, String(v));
      });
    }

    return value;
  };

  const formatDate = (date: Date | string, format?: string): string => {
    const d = typeof date === 'string' ? new Date(date) : date;
    const fmt = format || locale?.dateFormat || 'MM/DD/YYYY';

    // Simple format implementation
    const day = d.getDate().toString().padStart(2, '0');
    const month = (d.getMonth() + 1).toString().padStart(2, '0');
    const year = d.getFullYear();

    return fmt
      .replace('DD', day)
      .replace('MM', month)
      .replace('YYYY', year.toString())
      .replace('YY', year.toString().slice(-2));
  };

  const formatTime = (date: Date | string, format?: string): string => {
    const d = typeof date === 'string' ? new Date(date) : date;

    return d.toLocaleTimeString(locale?.language || 'en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatDateTime = (date: Date | string): string => {
    return `${formatDate(date)} ${formatTime(date)}`;
  };

  const formatNumber = (num: number, options?: Intl.NumberFormatOptions): string => {
    return new Intl.NumberFormat(locale?.language || 'en-US', options).format(num);
  };

  const formatCurrency = (amount: number, currencyCode?: string): string => {
    const code = currencyCode || locale?.currency || 'USD';
    const currency = currencies.find((c) => c.code === code);

    return new Intl.NumberFormat(locale?.language || 'en-US', {
      style: 'currency',
      currency: code,
      minimumFractionDigits: currency?.decimalPlaces ?? 2,
      maximumFractionDigits: currency?.decimalPlaces ?? 2,
    }).format(amount);
  };

  const setLanguage = async (code: string): Promise<void> => {
    // In production, save to backend
    const newTranslations = await fetchTranslations(code);
    setTranslations(newTranslations);
    queryClient.setQueryData(['user-locale'], (old: LocaleSettings) => ({
      ...old,
      language: code,
      isRtl: languages.find((l) => l.code === code)?.isRtl || false,
    }));
  };

  const setCurrency = async (code: string): Promise<void> => {
    const currency = currencies.find((c) => c.code === code);
    queryClient.setQueryData(['user-locale'], (old: LocaleSettings) => ({
      ...old,
      currency: code,
      currencySymbol: currency?.symbol,
    }));
  };

  const setTimezone = async (name: string): Promise<void> => {
    const tz = timezones.find((t) => t.name === name);
    queryClient.setQueryData(['user-locale'], (old: LocaleSettings) => ({
      ...old,
      timezone: name,
      timezoneOffset: tz?.offset,
    }));
  };

  const value: I18nContextType = {
    locale: locale || {
      language: 'en-US',
      languageName: 'English (US)',
      currency: 'USD',
      currencySymbol: '$',
      timezone: 'UTC',
      timezoneOffset: '+00:00',
      dateFormat: 'MM/DD/YYYY',
      timeFormat: 'h:mm A',
      firstDayOfWeek: 0,
      isRtl: false,
    },
    languages,
    currencies,
    timezones,
    t,
    formatDate,
    formatTime,
    formatDateTime,
    formatNumber,
    formatCurrency,
    setLanguage,
    setCurrency,
    setTimezone,
    isLoading: localeLoading,
  };

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

// Hook
export function useI18n(): I18nContextType {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error('useI18n must be used within an I18nProvider');
  }
  return context;
}

// Utility hook for just translations
export function useTranslation() {
  const { t, locale } = useI18n();
  return { t, language: locale.language };
}

// Utility hook for formatting
export function useFormatters() {
  const { formatDate, formatTime, formatDateTime, formatNumber, formatCurrency, locale } = useI18n();
  return { formatDate, formatTime, formatDateTime, formatNumber, formatCurrency, locale };
}
