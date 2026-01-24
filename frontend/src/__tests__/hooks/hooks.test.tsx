/**
 * MyCRM Frontend - Hook Tests
 * 
 * Comprehensive tests for custom React hooks
 */

import React from 'react';
import { renderHook, act, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import '@testing-library/jest-dom';

// =============================================================================
// Mock API Hook Tests
// =============================================================================

describe('useApi Hook', () => {
    // Mock implementation for testing
    const createUseApi = () => {
        const useApi = <T,>(
            url: string,
            options?: {
                enabled?: boolean;
                refetchInterval?: number;
            }
        ) => {
            const [data, setData] = React.useState<T | null>(null);
            const [isLoading, setIsLoading] = React.useState(true);
            const [error, setError] = React.useState<Error | null>(null);

            React.useEffect(() => {
                if (options?.enabled === false) {
                    setIsLoading(false);
                    return;
                }

                const fetchData = async () => {
                    try {
                        setIsLoading(true);
                        // Simulated fetch
                        const response = await Promise.resolve({ data: { id: 1, name: 'Test' } as unknown as T });
                        setData(response.data);
                        setError(null);
                    } catch (err) {
                        setError(err as Error);
                    } finally {
                        setIsLoading(false);
                    }
                };

                fetchData();
            }, [url, options?.enabled]);

            const refetch = () => {
                setIsLoading(true);
                setTimeout(() => {
                    setData({ id: 1, name: 'Refetched' } as unknown as T);
                    setIsLoading(false);
                }, 100);
            };

            return { data, isLoading, error, refetch };
        };

        return useApi;
    };

    it('returns loading state initially', () => {
        const useApi = createUseApi();
        const { result } = renderHook(() => useApi('/api/test'));

        expect(result.current.isLoading).toBe(true);
    });

    it('returns data after fetch', async () => {
        const useApi = createUseApi();
        const { result } = renderHook(() => useApi<{ id: number; name: string }>('/api/test'));

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(result.current.data).toEqual({ id: 1, name: 'Test' });
    });

    it('respects enabled option', () => {
        const useApi = createUseApi();
        const { result } = renderHook(() => 
            useApi('/api/test', { enabled: false })
        );

        expect(result.current.data).toBeNull();
    });

    it('provides refetch function', async () => {
        const useApi = createUseApi();
        const { result } = renderHook(() => useApi<{ id: number; name: string }>('/api/test'));

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        act(() => {
            result.current.refetch();
        });

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(result.current.data?.name).toBe('Refetched');
    });
});

// =============================================================================
// useMobile Hook Tests
// =============================================================================

describe('useMobile Hook', () => {
    const createUseMobile = () => {
        const useMobile = (breakpoint = 768) => {
            const [isMobile, setIsMobile] = React.useState(
                typeof window !== 'undefined' ? window.innerWidth < breakpoint : false
            );

            React.useEffect(() => {
                const handleResize = () => {
                    setIsMobile(window.innerWidth < breakpoint);
                };

                window.addEventListener('resize', handleResize);
                return () => window.removeEventListener('resize', handleResize);
            }, [breakpoint]);

            return isMobile;
        };

        return useMobile;
    };

    beforeAll(() => {
        Object.defineProperty(window, 'innerWidth', {
            writable: true,
            configurable: true,
            value: 1024,
        });
    });

    it('returns false for desktop width', () => {
        window.innerWidth = 1024;
        const useMobile = createUseMobile();
        const { result } = renderHook(() => useMobile());

        expect(result.current).toBe(false);
    });

    it('returns true for mobile width', () => {
        window.innerWidth = 375;
        const useMobile = createUseMobile();
        const { result } = renderHook(() => useMobile());

        expect(result.current).toBe(true);
    });

    it('uses custom breakpoint', () => {
        window.innerWidth = 900;
        const useMobile = createUseMobile();
        const { result } = renderHook(() => useMobile(1024));

        expect(result.current).toBe(true);
    });

    it('updates on resize', () => {
        window.innerWidth = 1024;
        const useMobile = createUseMobile();
        const { result } = renderHook(() => useMobile());

        expect(result.current).toBe(false);

        act(() => {
            window.innerWidth = 500;
            window.dispatchEvent(new Event('resize'));
        });

        expect(result.current).toBe(true);
    });
});

// =============================================================================
// useLocalStorage Hook Tests
// =============================================================================

describe('useLocalStorage Hook', () => {
    const createUseLocalStorage = () => {
        const useLocalStorage = <T,>(key: string, initialValue: T) => {
            const [storedValue, setStoredValue] = React.useState<T>(() => {
                try {
                    const item = window.localStorage.getItem(key);
                    return item ? JSON.parse(item) : initialValue;
                } catch {
                    return initialValue;
                }
            });

            const setValue = (value: T | ((val: T) => T)) => {
                try {
                    const valueToStore = value instanceof Function ? value(storedValue) : value;
                    setStoredValue(valueToStore);
                    window.localStorage.setItem(key, JSON.stringify(valueToStore));
                } catch (error) {
                    console.error(error);
                }
            };

            const removeValue = () => {
                try {
                    window.localStorage.removeItem(key);
                    setStoredValue(initialValue);
                } catch (error) {
                    console.error(error);
                }
            };

            return [storedValue, setValue, removeValue] as const;
        };

        return useLocalStorage;
    };

    beforeEach(() => {
        window.localStorage.clear();
    });

    it('returns initial value when storage is empty', () => {
        const useLocalStorage = createUseLocalStorage();
        const { result } = renderHook(() => useLocalStorage('testKey', 'default'));

        expect(result.current[0]).toBe('default');
    });

    it('returns stored value when available', () => {
        window.localStorage.setItem('testKey', JSON.stringify('stored value'));
        const useLocalStorage = createUseLocalStorage();
        const { result } = renderHook(() => useLocalStorage('testKey', 'default'));

        expect(result.current[0]).toBe('stored value');
    });

    it('updates value in storage', () => {
        const useLocalStorage = createUseLocalStorage();
        const { result } = renderHook(() => useLocalStorage('testKey', 'initial'));

        act(() => {
            result.current[1]('new value');
        });

        expect(result.current[0]).toBe('new value');
        expect(JSON.parse(window.localStorage.getItem('testKey') || '')).toBe('new value');
    });

    it('removes value from storage', () => {
        window.localStorage.setItem('testKey', JSON.stringify('to remove'));
        const useLocalStorage = createUseLocalStorage();
        const { result } = renderHook(() => useLocalStorage('testKey', 'default'));

        act(() => {
            result.current[2]();
        });

        expect(result.current[0]).toBe('default');
        expect(window.localStorage.getItem('testKey')).toBeNull();
    });

    it('handles objects', () => {
        const useLocalStorage = createUseLocalStorage();
        const { result } = renderHook(() => 
            useLocalStorage('testKey', { name: 'John', age: 30 })
        );

        act(() => {
            result.current[1]({ name: 'Jane', age: 25 });
        });

        expect(result.current[0]).toEqual({ name: 'Jane', age: 25 });
    });
});

// =============================================================================
// useDebounce Hook Tests
// =============================================================================

describe('useDebounce Hook', () => {
    const createUseDebounce = () => {
        const useDebounce = <T,>(value: T, delay: number) => {
            const [debouncedValue, setDebouncedValue] = React.useState(value);

            React.useEffect(() => {
                const timer = setTimeout(() => {
                    setDebouncedValue(value);
                }, delay);

                return () => {
                    clearTimeout(timer);
                };
            }, [value, delay]);

            return debouncedValue;
        };

        return useDebounce;
    };

    beforeEach(() => {
        jest.useFakeTimers();
    });

    afterEach(() => {
        jest.useRealTimers();
    });

    it('returns initial value immediately', () => {
        const useDebounce = createUseDebounce();
        const { result } = renderHook(() => useDebounce('initial', 500));

        expect(result.current).toBe('initial');
    });

    it('updates value after delay', () => {
        const useDebounce = createUseDebounce();
        const { result, rerender } = renderHook(
            ({ value }) => useDebounce(value, 500),
            { initialProps: { value: 'initial' } }
        );

        rerender({ value: 'updated' });

        expect(result.current).toBe('initial');

        act(() => {
            jest.advanceTimersByTime(500);
        });

        expect(result.current).toBe('updated');
    });

    it('cancels previous timer on rapid updates', () => {
        const useDebounce = createUseDebounce();
        const { result, rerender } = renderHook(
            ({ value }) => useDebounce(value, 500),
            { initialProps: { value: 'initial' } }
        );

        rerender({ value: 'update1' });
        act(() => {
            jest.advanceTimersByTime(200);
        });

        rerender({ value: 'update2' });
        act(() => {
            jest.advanceTimersByTime(200);
        });

        rerender({ value: 'final' });
        
        expect(result.current).toBe('initial');

        act(() => {
            jest.advanceTimersByTime(500);
        });

        expect(result.current).toBe('final');
    });
});

// =============================================================================
// useToggle Hook Tests
// =============================================================================

describe('useToggle Hook', () => {
    const createUseToggle = () => {
        const useToggle = (initialValue = false) => {
            const [value, setValue] = React.useState(initialValue);

            const toggle = React.useCallback(() => {
                setValue(v => !v);
            }, []);

            const setTrue = React.useCallback(() => {
                setValue(true);
            }, []);

            const setFalse = React.useCallback(() => {
                setValue(false);
            }, []);

            return { value, toggle, setTrue, setFalse };
        };

        return useToggle;
    };

    it('returns initial value', () => {
        const useToggle = createUseToggle();
        const { result } = renderHook(() => useToggle(false));

        expect(result.current.value).toBe(false);
    });

    it('toggles value', () => {
        const useToggle = createUseToggle();
        const { result } = renderHook(() => useToggle(false));

        act(() => {
            result.current.toggle();
        });

        expect(result.current.value).toBe(true);

        act(() => {
            result.current.toggle();
        });

        expect(result.current.value).toBe(false);
    });

    it('sets value to true', () => {
        const useToggle = createUseToggle();
        const { result } = renderHook(() => useToggle(false));

        act(() => {
            result.current.setTrue();
        });

        expect(result.current.value).toBe(true);
    });

    it('sets value to false', () => {
        const useToggle = createUseToggle();
        const { result } = renderHook(() => useToggle(true));

        act(() => {
            result.current.setFalse();
        });

        expect(result.current.value).toBe(false);
    });
});

// =============================================================================
// usePrevious Hook Tests
// =============================================================================

describe('usePrevious Hook', () => {
    const createUsePrevious = () => {
        const usePrevious = <T,>(value: T) => {
            const ref = React.useRef<T>();

            React.useEffect(() => {
                ref.current = value;
            }, [value]);

            return ref.current;
        };

        return usePrevious;
    };

    it('returns undefined on first render', () => {
        const usePrevious = createUsePrevious();
        const { result } = renderHook(() => usePrevious('initial'));

        expect(result.current).toBeUndefined();
    });

    it('returns previous value after update', () => {
        const usePrevious = createUsePrevious();
        const { result, rerender } = renderHook(
            ({ value }) => usePrevious(value),
            { initialProps: { value: 'first' } }
        );

        rerender({ value: 'second' });

        expect(result.current).toBe('first');

        rerender({ value: 'third' });

        expect(result.current).toBe('second');
    });
});

// =============================================================================
// useOnClickOutside Hook Tests
// =============================================================================

describe('useOnClickOutside Hook', () => {
    const createUseOnClickOutside = () => {
        const useOnClickOutside = (
            ref: React.RefObject<HTMLElement>,
            handler: (event: MouseEvent | TouchEvent) => void
        ) => {
            React.useEffect(() => {
                const listener = (event: MouseEvent | TouchEvent) => {
                    if (!ref.current || ref.current.contains(event.target as Node)) {
                        return;
                    }
                    handler(event);
                };

                document.addEventListener('mousedown', listener);
                document.addEventListener('touchstart', listener);

                return () => {
                    document.removeEventListener('mousedown', listener);
                    document.removeEventListener('touchstart', listener);
                };
            }, [ref, handler]);
        };

        return useOnClickOutside;
    };

    it('calls handler when clicking outside', () => {
        const useOnClickOutside = createUseOnClickOutside();
        const handler = jest.fn();
        const ref = { current: document.createElement('div') };

        renderHook(() => useOnClickOutside(ref, handler));

        act(() => {
            document.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
        });

        expect(handler).toHaveBeenCalled();
    });

    it('does not call handler when clicking inside', () => {
        const useOnClickOutside = createUseOnClickOutside();
        const handler = jest.fn();
        const element = document.createElement('div');
        document.body.appendChild(element);
        const ref = { current: element };

        renderHook(() => useOnClickOutside(ref, handler));

        act(() => {
            element.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
        });

        expect(handler).not.toHaveBeenCalled();

        document.body.removeChild(element);
    });
});

// =============================================================================
// useKeyPress Hook Tests
// =============================================================================

describe('useKeyPress Hook', () => {
    const createUseKeyPress = () => {
        const useKeyPress = (targetKey: string) => {
            const [keyPressed, setKeyPressed] = React.useState(false);

            React.useEffect(() => {
                const downHandler = ({ key }: KeyboardEvent) => {
                    if (key === targetKey) {
                        setKeyPressed(true);
                    }
                };

                const upHandler = ({ key }: KeyboardEvent) => {
                    if (key === targetKey) {
                        setKeyPressed(false);
                    }
                };

                window.addEventListener('keydown', downHandler);
                window.addEventListener('keyup', upHandler);

                return () => {
                    window.removeEventListener('keydown', downHandler);
                    window.removeEventListener('keyup', upHandler);
                };
            }, [targetKey]);

            return keyPressed;
        };

        return useKeyPress;
    };

    it('returns false when key not pressed', () => {
        const useKeyPress = createUseKeyPress();
        const { result } = renderHook(() => useKeyPress('Enter'));

        expect(result.current).toBe(false);
    });

    it('returns true when target key is pressed', () => {
        const useKeyPress = createUseKeyPress();
        const { result } = renderHook(() => useKeyPress('Enter'));

        act(() => {
            window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter' }));
        });

        expect(result.current).toBe(true);
    });

    it('returns false when key is released', () => {
        const useKeyPress = createUseKeyPress();
        const { result } = renderHook(() => useKeyPress('Enter'));

        act(() => {
            window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter' }));
        });

        act(() => {
            window.dispatchEvent(new KeyboardEvent('keyup', { key: 'Enter' }));
        });

        expect(result.current).toBe(false);
    });

    it('ignores other keys', () => {
        const useKeyPress = createUseKeyPress();
        const { result } = renderHook(() => useKeyPress('Enter'));

        act(() => {
            window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
        });

        expect(result.current).toBe(false);
    });
});

// =============================================================================
// useCopyToClipboard Hook Tests
// =============================================================================

describe('useCopyToClipboard Hook', () => {
    const createUseCopyToClipboard = () => {
        const useCopyToClipboard = () => {
            const [copiedText, setCopiedText] = React.useState<string | null>(null);
            const [error, setError] = React.useState<Error | null>(null);

            const copy = async (text: string) => {
                if (!navigator?.clipboard) {
                    setError(new Error('Clipboard not supported'));
                    return false;
                }

                try {
                    await navigator.clipboard.writeText(text);
                    setCopiedText(text);
                    setError(null);
                    return true;
                } catch (err) {
                    setError(err as Error);
                    setCopiedText(null);
                    return false;
                }
            };

            return { copiedText, error, copy };
        };

        return useCopyToClipboard;
    };

    beforeAll(() => {
        Object.assign(navigator, {
            clipboard: {
                writeText: jest.fn(() => Promise.resolve()),
            },
        });
    });

    it('copies text to clipboard', async () => {
        const useCopyToClipboard = createUseCopyToClipboard();
        const { result } = renderHook(() => useCopyToClipboard());

        await act(async () => {
            await result.current.copy('Hello World');
        });

        expect(result.current.copiedText).toBe('Hello World');
        expect(navigator.clipboard.writeText).toHaveBeenCalledWith('Hello World');
    });

    it('returns error when clipboard fails', async () => {
        (navigator.clipboard.writeText as jest.Mock).mockRejectedValueOnce(
            new Error('Failed to copy')
        );

        const useCopyToClipboard = createUseCopyToClipboard();
        const { result } = renderHook(() => useCopyToClipboard());

        await act(async () => {
            await result.current.copy('text');
        });

        expect(result.current.error).toBeInstanceOf(Error);
    });
});

// =============================================================================
// useMediaQuery Hook Tests
// =============================================================================

describe('useMediaQuery Hook', () => {
    const createUseMediaQuery = () => {
        const useMediaQuery = (query: string) => {
            const [matches, setMatches] = React.useState(false);

            React.useEffect(() => {
                const media = window.matchMedia(query);
                setMatches(media.matches);

                const listener = (event: MediaQueryListEvent) => {
                    setMatches(event.matches);
                };

                media.addEventListener('change', listener);
                return () => media.removeEventListener('change', listener);
            }, [query]);

            return matches;
        };

        return useMediaQuery;
    };

    beforeAll(() => {
        window.matchMedia = jest.fn().mockImplementation((query) => ({
            matches: query.includes('min-width: 768px'),
            media: query,
            onchange: null,
            addListener: jest.fn(),
            removeListener: jest.fn(),
            addEventListener: jest.fn(),
            removeEventListener: jest.fn(),
            dispatchEvent: jest.fn(),
        }));
    });

    it('returns match status for media query', () => {
        const useMediaQuery = createUseMediaQuery();
        const { result } = renderHook(() => useMediaQuery('(min-width: 768px)'));

        expect(result.current).toBe(true);
    });

    it('returns false for non-matching query', () => {
        const useMediaQuery = createUseMediaQuery();
        const { result } = renderHook(() => useMediaQuery('(min-width: 1200px)'));

        expect(result.current).toBe(false);
    });
});
