/**
 * MyCRM - Test Setup File
 * 
 * Global test configuration and mocks
 */

import '@testing-library/jest-dom';

// =============================================================================
// Global Mocks
// =============================================================================

// Mock Next.js router
jest.mock('next/navigation', () => ({
    useRouter: () => ({
        push: jest.fn(),
        replace: jest.fn(),
        prefetch: jest.fn(),
        back: jest.fn(),
        forward: jest.fn(),
        refresh: jest.fn(),
    }),
    usePathname: () => '/',
    useSearchParams: () => new URLSearchParams(),
    useParams: () => ({}),
}));

// Mock Next.js Link
jest.mock('next/link', () => {
    return ({ children, href }: { children: React.ReactNode; href: string }) => {
        return <a href={href}>{children}</a>;
    };
});

// Mock Next.js Image
jest.mock('next/image', () => {
    return ({ src, alt, ...props }: { src: string; alt: string; [key: string]: unknown }) => {
        return <img src={src} alt={alt} {...props} />;
    };
});

// =============================================================================
// Window/DOM Mocks
// =============================================================================

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: jest.fn().mockImplementation((query: string) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: jest.fn(),
        removeListener: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
    })),
});

// Mock ResizeObserver
class MockResizeObserver {
    observe = jest.fn();
    unobserve = jest.fn();
    disconnect = jest.fn();
}
window.ResizeObserver = MockResizeObserver;

// Mock IntersectionObserver
class MockIntersectionObserver {
    constructor(callback: IntersectionObserverCallback) {
        this.callback = callback;
    }
    callback: IntersectionObserverCallback;
    root = null;
    rootMargin = '';
    thresholds = [];
    observe = jest.fn();
    unobserve = jest.fn();
    disconnect = jest.fn();
    takeRecords = jest.fn(() => []);
}
window.IntersectionObserver = MockIntersectionObserver as unknown as typeof IntersectionObserver;

// Mock scrollTo
window.scrollTo = jest.fn();

// Mock localStorage
const localStorageMock = {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn(),
    clear: jest.fn(),
    length: 0,
    key: jest.fn(),
};
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Mock sessionStorage
const sessionStorageMock = {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn(),
    clear: jest.fn(),
    length: 0,
    key: jest.fn(),
};
Object.defineProperty(window, 'sessionStorage', { value: sessionStorageMock });

// Mock clipboard
Object.assign(navigator, {
    clipboard: {
        writeText: jest.fn(() => Promise.resolve()),
        readText: jest.fn(() => Promise.resolve('')),
    },
});

// =============================================================================
// Fetch Mock
// =============================================================================

// Default fetch mock that returns empty response
global.fetch = jest.fn(() =>
    Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve({}),
        text: () => Promise.resolve(''),
        blob: () => Promise.resolve(new Blob()),
        headers: new Headers(),
    } as Response)
);

// =============================================================================
// Console Warnings Suppression
// =============================================================================

// Suppress specific console warnings in tests
const originalError = console.error;
const originalWarn = console.warn;

beforeAll(() => {
    console.error = (...args: unknown[]) => {
        const message = args[0]?.toString() || '';
        // Suppress specific React warnings during tests
        if (
            message.includes('Warning: ReactDOM.render is no longer supported') ||
            message.includes('Warning: An update to') ||
            message.includes('act(...)') 
        ) {
            return;
        }
        originalError.apply(console, args);
    };

    console.warn = (...args: unknown[]) => {
        const message = args[0]?.toString() || '';
        if (message.includes('componentWillMount')) {
            return;
        }
        originalWarn.apply(console, args);
    };
});

afterAll(() => {
    console.error = originalError;
    console.warn = originalWarn;
});

// =============================================================================
// Test Cleanup
// =============================================================================

afterEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockClear();
    localStorageMock.setItem.mockClear();
    localStorageMock.removeItem.mockClear();
    localStorageMock.clear.mockClear();
});

// =============================================================================
// Custom Test Utilities
// =============================================================================

// Re-export testing library utilities
export * from '@testing-library/react';

// Custom render with providers wrapper
import React from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const createTestQueryClient = () =>
    new QueryClient({
        defaultOptions: {
            queries: {
                retry: false,
                gcTime: 0,
            },
        },
    });

const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
    const queryClient = createTestQueryClient();
    
    return (
        <QueryClientProvider client={queryClient}>
            {children}
        </QueryClientProvider>
    );
};

const customRender = (
    ui: React.ReactElement,
    options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options });

export { customRender as renderWithProviders };
