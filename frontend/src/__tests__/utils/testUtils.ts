/**
 * MyCRM - Test Utilities
 * 
 * Shared utilities for testing
 */

import React from 'react';
import { render, RenderOptions, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// =============================================================================
// Query Client Utilities
// =============================================================================

export const createTestQueryClient = () =>
    new QueryClient({
        defaultOptions: {
            queries: {
                retry: false,
                gcTime: 0,
                staleTime: 0,
            },
            mutations: {
                retry: false,
            },
        },
    });

// =============================================================================
// Mock Data Factories
// =============================================================================

export const createMockUser = (overrides = {}) => ({
    id: 1,
    email: 'test@example.com',
    firstName: 'Test',
    lastName: 'User',
    avatar: null,
    role: 'user',
    createdAt: '2025-01-01T00:00:00Z',
    ...overrides,
});

export const createMockContact = (overrides = {}) => ({
    id: 1,
    firstName: 'John',
    lastName: 'Doe',
    email: 'john.doe@example.com',
    phone: '+1-555-123-4567',
    company: 'Acme Corp',
    title: 'CEO',
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2025-01-01T00:00:00Z',
    ...overrides,
});

export const createMockLead = (overrides = {}) => ({
    id: 1,
    name: 'New Lead',
    email: 'lead@example.com',
    company: 'Tech Corp',
    status: 'new' as const,
    source: 'website',
    score: 50,
    assignedTo: null,
    createdAt: '2025-01-01T00:00:00Z',
    ...overrides,
});

export const createMockOpportunity = (overrides = {}) => ({
    id: 1,
    name: 'Big Deal',
    value: 50000,
    stage: 'prospecting' as const,
    probability: 20,
    closeDate: '2025-03-01',
    ownerId: 1,
    contactId: 1,
    createdAt: '2025-01-01T00:00:00Z',
    ...overrides,
});

export const createMockTask = (overrides = {}) => ({
    id: 1,
    title: 'Follow up call',
    description: 'Call client about proposal',
    status: 'pending' as const,
    priority: 'medium' as const,
    dueDate: '2025-01-25T10:00:00Z',
    assignedTo: 1,
    createdAt: '2025-01-01T00:00:00Z',
    ...overrides,
});

export const createMockActivity = (overrides = {}) => ({
    id: 1,
    type: 'call' as const,
    description: 'Called client about renewal',
    timestamp: '2025-01-24T10:00:00Z',
    userId: 1,
    subjectType: 'contact',
    subjectId: 1,
    ...overrides,
});

// =============================================================================
// API Mock Helpers
// =============================================================================

export const mockApiResponse = <T>(data: T, options: { ok?: boolean; status?: number } = {}) => {
    return jest.fn(() =>
        Promise.resolve({
            ok: options.ok ?? true,
            status: options.status ?? 200,
            json: () => Promise.resolve(data),
            text: () => Promise.resolve(JSON.stringify(data)),
            headers: new Headers({ 'Content-Type': 'application/json' }),
        } as Response)
    );
};

export const mockApiError = (message: string, status = 400) => {
    return jest.fn(() =>
        Promise.resolve({
            ok: false,
            status,
            json: () => Promise.resolve({ message, error: message }),
            text: () => Promise.resolve(JSON.stringify({ message })),
            headers: new Headers({ 'Content-Type': 'application/json' }),
        } as Response)
    );
};

export const mockNetworkError = () => {
    return jest.fn(() => Promise.reject(new Error('Network error')));
};

// =============================================================================
// Render Helpers
// =============================================================================

interface WrapperOptions {
    queryClient?: QueryClient;
    initialEntries?: string[];
}

export const createWrapper = (options: WrapperOptions = {}) => {
    const queryClient = options.queryClient || createTestQueryClient();

    return ({ children }: { children: React.ReactNode }) => (
        <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
};

interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
    wrapperOptions?: WrapperOptions;
}

export const renderWithProviders = (
    ui: React.ReactElement,
    options: CustomRenderOptions = {}
) => {
    const { wrapperOptions, ...renderOptions } = options;
    const wrapper = createWrapper(wrapperOptions);

    return {
        ...render(ui, { wrapper, ...renderOptions }),
        user: userEvent.setup(),
    };
};

// =============================================================================
// Wait Helpers
// =============================================================================

export const waitForLoadingToFinish = async () => {
    await waitFor(() => {
        const loadingElements = screen.queryAllByTestId('loading');
        const spinners = screen.queryAllByRole('progressbar');
        const loadingTexts = screen.queryAllByText(/loading/i);

        expect([...loadingElements, ...spinners, ...loadingTexts]).toHaveLength(0);
    });
};

export const waitForElement = async (testId: string) => {
    return waitFor(() => {
        expect(screen.getByTestId(testId)).toBeInTheDocument();
    });
};

export const waitForElementToBeRemoved = async (testId: string) => {
    await waitFor(() => {
        expect(screen.queryByTestId(testId)).not.toBeInTheDocument();
    });
};

// =============================================================================
// Form Helpers
// =============================================================================

export const fillForm = async (
    user: ReturnType<typeof userEvent.setup>,
    fields: Record<string, string>
) => {
    for (const [label, value] of Object.entries(fields)) {
        const input = screen.getByLabelText(new RegExp(label, 'i'));
        await user.clear(input);
        await user.type(input, value);
    }
};

export const submitForm = async (user: ReturnType<typeof userEvent.setup>) => {
    const submitButton = screen.getByRole('button', { name: /submit|save|create/i });
    await user.click(submitButton);
};

// =============================================================================
// Table Helpers
// =============================================================================

export const getTableRows = () => {
    return screen.getAllByRole('row').slice(1); // Exclude header row
};

export const getTableCell = (row: HTMLElement, columnIndex: number) => {
    return row.querySelectorAll('td')[columnIndex];
};

// =============================================================================
// Date Helpers
// =============================================================================

export const mockDate = (dateString: string) => {
    const mockedDate = new Date(dateString);
    jest.useFakeTimers();
    jest.setSystemTime(mockedDate);

    return () => {
        jest.useRealTimers();
    };
};

// =============================================================================
// Accessibility Helpers
// =============================================================================

export const checkAccessibility = async (container: HTMLElement) => {
    // Basic accessibility checks
    const images = container.querySelectorAll('img');
    images.forEach((img) => {
        expect(img).toHaveAttribute('alt');
    });

    const buttons = container.querySelectorAll('button');
    buttons.forEach((button) => {
        const hasText = button.textContent?.trim();
        const hasAriaLabel = button.hasAttribute('aria-label');
        expect(hasText || hasAriaLabel).toBeTruthy();
    });

    const inputs = container.querySelectorAll('input:not([type="hidden"])');
    inputs.forEach((input) => {
        const id = input.getAttribute('id');
        const ariaLabel = input.hasAttribute('aria-label');
        const ariaLabelledBy = input.hasAttribute('aria-labelledby');
        const hasLabel = id && container.querySelector(`label[for="${id}"]`);
        expect(hasLabel || ariaLabel || ariaLabelledBy).toBeTruthy();
    });
};

// =============================================================================
// Event Helpers
// =============================================================================

export const createEvent = {
    click: () => new MouseEvent('click', { bubbles: true, cancelable: true }),
    keyDown: (key: string) =>
        new KeyboardEvent('keydown', { key, bubbles: true, cancelable: true }),
    keyUp: (key: string) =>
        new KeyboardEvent('keyup', { key, bubbles: true, cancelable: true }),
    change: (value: string) => {
        const event = new Event('change', { bubbles: true, cancelable: true });
        Object.defineProperty(event, 'target', { value: { value } });
        return event;
    },
};

// =============================================================================
// Storage Helpers
// =============================================================================

export const mockLocalStorage = (data: Record<string, unknown> = {}) => {
    const storage: Record<string, string> = {};

    Object.entries(data).forEach(([key, value]) => {
        storage[key] = JSON.stringify(value);
    });

    return {
        getItem: jest.fn((key: string) => storage[key] ?? null),
        setItem: jest.fn((key: string, value: string) => {
            storage[key] = value;
        }),
        removeItem: jest.fn((key: string) => {
            delete storage[key];
        }),
        clear: jest.fn(() => {
            Object.keys(storage).forEach((key) => delete storage[key]);
        }),
    };
};
