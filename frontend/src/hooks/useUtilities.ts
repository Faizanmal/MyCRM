'use client';

import { useRef, useEffect, useState, useCallback } from 'react';

/**
 * Hook for tracking component visibility using Intersection Observer
 */
export function useIntersectionObserver<T extends HTMLElement>(
    options?: IntersectionObserverInit
) {
    const ref = useRef<T>(null);
    const [isVisible, setIsVisible] = useState(false);
    const [hasBeenVisible, setHasBeenVisible] = useState(false);

    useEffect(() => {
        const element = ref.current;
        if (!element) return;

        const observer = new IntersectionObserver(([entry]) => {
            setIsVisible(entry.isIntersecting);
            if (entry.isIntersecting) {
                setHasBeenVisible(true);
            }
        }, options);

        observer.observe(element);
        return () => observer.disconnect();
    }, [options]);

    return { ref, isVisible, hasBeenVisible };
}

/**
 * Hook for debouncing values
 */
export function useDebounce<T>(value: T, delay: number): T {
    const [debouncedValue, setDebouncedValue] = useState(value);

    useEffect(() => {
        const timer = setTimeout(() => setDebouncedValue(value), delay);
        return () => clearTimeout(timer);
    }, [value, delay]);

    return debouncedValue;
}

/**
 * Hook for throttling callbacks
 */
export function useThrottle<T extends (...args: Parameters<T>) => ReturnType<T>>(
    callback: T,
    delay: number
): T {
    const lastRan = useRef(Date.now());
    const timeoutRef = useRef<NodeJS.Timeout | null>(null);

    return useCallback(
        ((...args: Parameters<T>) => {
            const now = Date.now();
            const timeSinceLastRan = now - lastRan.current;

            if (timeSinceLastRan >= delay) {
                lastRan.current = now;
                return callback(...args);
            } else if (!timeoutRef.current) {
                timeoutRef.current = setTimeout(() => {
                    lastRan.current = Date.now();
                    timeoutRef.current = null;
                    callback(...args);
                }, delay - timeSinceLastRan);
            }
        }) as T,
        [callback, delay]
    );
}

/**
 * Hook for local storage with automatic sync
 */
export function useLocalStorage<T>(
    key: string,
    initialValue: T
): [T, (value: T | ((prev: T) => T)) => void] {
    const [storedValue, setStoredValue] = useState<T>(() => {
        if (typeof window === 'undefined') return initialValue;

        try {
            const item = window.localStorage.getItem(key);
            return item ? JSON.parse(item) : initialValue;
        } catch (error) {
            console.warn(`Error reading localStorage key "${key}":`, error);
            return initialValue;
        }
    });

    const setValue = useCallback(
        (value: T | ((prev: T) => T)) => {
            try {
                const valueToStore = value instanceof Function ? value(storedValue) : value;
                setStoredValue(valueToStore);
                if (typeof window !== 'undefined') {
                    window.localStorage.setItem(key, JSON.stringify(valueToStore));
                }
            } catch (error) {
                console.warn(`Error setting localStorage key "${key}":`, error);
            }
        },
        [key, storedValue]
    );

    // Sync with other tabs
    useEffect(() => {
        const handleStorageChange = (e: StorageEvent) => {
            if (e.key === key && e.newValue) {
                try {
                    setStoredValue(JSON.parse(e.newValue));
                } catch {
                    // Ignore parse errors
                }
            }
        };

        window.addEventListener('storage', handleStorageChange);
        return () => window.removeEventListener('storage', handleStorageChange);
    }, [key]);

    return [storedValue, setValue];
}

/**
 * Hook for keyboard shortcuts
 */
export function useKeyboardShortcut(
    key: string,
    callback: () => void,
    options?: {
        ctrl?: boolean;
        shift?: boolean;
        alt?: boolean;
        meta?: boolean;
        preventDefault?: boolean;
    }
) {
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            const { ctrl = false, shift = false, alt = false, meta = false, preventDefault = true } = options || {};

            if (
                e.key.toLowerCase() === key.toLowerCase() &&
                e.ctrlKey === ctrl &&
                e.shiftKey === shift &&
                e.altKey === alt &&
                e.metaKey === meta
            ) {
                if (preventDefault) e.preventDefault();
                callback();
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [key, callback, options]);
}

/**
 * Hook for click outside detection
 */
export function useClickOutside<T extends HTMLElement>(
    callback: () => void
) {
    const ref = useRef<T>(null);

    useEffect(() => {
        const handleClick = (e: MouseEvent) => {
            if (ref.current && !ref.current.contains(e.target as Node)) {
                callback();
            }
        };

        document.addEventListener('mousedown', handleClick);
        return () => document.removeEventListener('mousedown', handleClick);
    }, [callback]);

    return ref;
}

/**
 * Hook for copy to clipboard
 */
export function useCopyToClipboard(): [
    string | null,
    (text: string) => Promise<boolean>
] {
    const [copiedText, setCopiedText] = useState<string | null>(null);

    const copy = useCallback(async (text: string): Promise<boolean> => {
        if (!navigator?.clipboard) {
            console.warn('Clipboard API not available');
            return false;
        }

        try {
            await navigator.clipboard.writeText(text);
            setCopiedText(text);
            return true;
        } catch (error) {
            console.warn('Copy failed:', error);
            setCopiedText(null);
            return false;
        }
    }, []);

    return [copiedText, copy];
}

/**
 * Hook for window size
 */
export function useWindowSize() {
    const [size, setSize] = useState({
        width: typeof window !== 'undefined' ? window.innerWidth : 0,
        height: typeof window !== 'undefined' ? window.innerHeight : 0,
    });

    useEffect(() => {
        const handleResize = () => {
            setSize({
                width: window.innerWidth,
                height: window.innerHeight,
            });
        };

        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    return size;
}

/**
 * Hook for media query matching
 */
export function useMediaQuery(query: string): boolean {
    const [matches, setMatches] = useState(false);

    useEffect(() => {
        const mediaQuery = window.matchMedia(query);
        setMatches(mediaQuery.matches);

        const handler = (e: MediaQueryListEvent) => setMatches(e.matches);
        mediaQuery.addEventListener('change', handler);
        return () => mediaQuery.removeEventListener('change', handler);
    }, [query]);

    return matches;
}

/**
 * Hook for previous value
 */
export function usePrevious<T>(value: T): T | undefined {
    const ref = useRef<T>();

    useEffect(() => {
        ref.current = value;
    }, [value]);

    return ref.current;
}

/**
 * Hook for async operations with loading state
 */
export function useAsync<T, E = Error>(
    asyncFunction: () => Promise<T>,
    immediate = true
): {
    execute: () => Promise<void>;
    loading: boolean;
    value: T | null;
    error: E | null;
} {
    const [loading, setLoading] = useState(immediate);
    const [value, setValue] = useState<T | null>(null);
    const [error, setError] = useState<E | null>(null);

    const execute = useCallback(async () => {
        setLoading(true);
        setValue(null);
        setError(null);

        try {
            const response = await asyncFunction();
            setValue(response);
        } catch (e) {
            setError(e as E);
        } finally {
            setLoading(false);
        }
    }, [asyncFunction]);

    useEffect(() => {
        if (immediate) {
            execute();
        }
    }, [execute, immediate]);

    return { execute, loading, value, error };
}

/**
 * Hook for online/offline status
 */
export function useOnlineStatus(): boolean {
    const [isOnline, setIsOnline] = useState(
        typeof navigator !== 'undefined' ? navigator.onLine : true
    );

    useEffect(() => {
        const handleOnline = () => setIsOnline(true);
        const handleOffline = () => setIsOnline(false);

        window.addEventListener('online', handleOnline);
        window.addEventListener('offline', handleOffline);

        return () => {
            window.removeEventListener('online', handleOnline);
            window.removeEventListener('offline', handleOffline);
        };
    }, []);

    return isOnline;
}

/**
 * Hook for document title
 */
export function useDocumentTitle(title: string) {
    useEffect(() => {
        const previousTitle = document.title;
        document.title = title;
        return () => {
            document.title = previousTitle;
        };
    }, [title]);
}

/**
 * Hook for scroll position
 */
export function useScrollPosition() {
    const [scrollPosition, setScrollPosition] = useState({
        x: 0,
        y: 0,
    });

    useEffect(() => {
        const handleScroll = () => {
            setScrollPosition({
                x: window.scrollX,
                y: window.scrollY,
            });
        };

        window.addEventListener('scroll', handleScroll, { passive: true });
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    return scrollPosition;
}

/**
 * Hook for idle detection
 */
export function useIdle(timeout: number = 60000): boolean {
    const [isIdle, setIsIdle] = useState(false);

    useEffect(() => {
        let timeoutId: NodeJS.Timeout;

        const handleActivity = () => {
            setIsIdle(false);
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => setIsIdle(true), timeout);
        };

        const events = ['mousedown', 'mousemove', 'keydown', 'scroll', 'touchstart'];
        events.forEach(event => window.addEventListener(event, handleActivity));

        timeoutId = setTimeout(() => setIsIdle(true), timeout);

        return () => {
            events.forEach(event => window.removeEventListener(event, handleActivity));
            clearTimeout(timeoutId);
        };
    }, [timeout]);

    return isIdle;
}
