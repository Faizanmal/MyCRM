import '@testing-library/jest-dom';

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
}));

// Mock next-themes
jest.mock('next-themes', () => ({
    useTheme: () => ({
        theme: 'light',
        setTheme: jest.fn(),
        resolvedTheme: 'light',
    }),
    ThemeProvider: ({ children }: { children: React.ReactNode }) => children,
}));

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: jest.fn().mockImplementation(query => ({
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

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
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
    takeRecords = jest.fn().mockReturnValue([]);
};

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
    constructor(callback: ResizeObserverCallback) {
        this.callback = callback;
    }
    callback: ResizeObserverCallback;
    observe = jest.fn();
    unobserve = jest.fn();
    disconnect = jest.fn();
};

// Suppress console errors in tests unless explicitly needed
const originalError = console.error;
console.error = (...args: Parameters<typeof console.error>) => {
    // Filter out React 18 act() warnings and other noise
    if (
        typeof args[0] === 'string' &&
        (args[0].includes('Warning: ReactDOM.render') ||
            args[0].includes('act(...)') ||
            args[0].includes('inside a test was not wrapped'))
    ) {
        return;
    }
    originalError.apply(console, args);
};
