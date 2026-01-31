/**
 * MyCRM Frontend - Data Fetching Integration Tests
 * 
 * Tests for API integration, data loading, and state management
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import '@testing-library/jest-dom';

// =============================================================================
// Test Utilities
// =============================================================================

const createTestQueryClient = () =>
    new QueryClient({
        defaultOptions: {
            queries: {
                retry: false,
                gcTime: 0,
            },
        },
    });


const _createTestWrapper = () => {
    const queryClient = createTestQueryClient();
    const Wrapper = ({ children }: { children: React.ReactNode }) => (
        <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
    Wrapper.displayName = 'TestWrapper';
    return Wrapper;
};

// Mock fetch globally
const mockFetch = (data: unknown, options: { ok?: boolean; status?: number } = {}) => {
    return jest.fn(() =>
        Promise.resolve({
            ok: options.ok ?? true,
            status: options.status ?? 200,
            json: () => Promise.resolve(data),
        } as Response)
    );
};

// =============================================================================
// Contact List Data Fetching Tests
// =============================================================================

describe('Contact List Data Fetching', () => {
    const MockContactListPage = ({ onContactClick }: { onContactClick?: (id: number) => void }) => {
        const [contacts, setContacts] = React.useState<Array<{ id: number; name: string; email: string }>>([]);
        const [loading, setLoading] = React.useState(true);
        const [error, setError] = React.useState<string | null>(null);
        const [page, setPage] = React.useState(1);

        React.useEffect(() => {
            const fetchContacts = async () => {
                try {
                    setLoading(true);
                    const response = await fetch(`/api/contacts?page=${page}`);
                    if (!response.ok) throw new Error('Failed to fetch');
                    const data = await response.json();
                    setContacts(data.results);
                } catch (err) {
                    setError((err as Error).message);
                } finally {
                    setLoading(false);
                }
            };
            fetchContacts();
        }, [page]);

        if (error) return <div data-testid="error">{error}</div>;
        if (loading) return <div data-testid="loading">Loading...</div>;

        return (
            <div>
                <ul data-testid="contact-list">
                    {contacts.map((c) => (
                        <li
                            key={c.id}
                            onClick={() => onContactClick?.(c.id)}
                            onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') onContactClick?.(c.id); }}
                            tabIndex={0}
                        >
                            {c.name} - {c.email}
                        </li>
                    ))}
                </ul>
                <button onClick={() => setPage((p) => p + 1)}>Next Page</button>
            </div>
        );
    };

    beforeEach(() => {
        jest.clearAllMocks();
    });

    it('shows loading state initially', () => {
        global.fetch = mockFetch({ results: [] });
        render(<MockContactListPage />);
        expect(screen.getByTestId('loading')).toBeInTheDocument();
    });

    it('renders contacts after loading', async () => {
        const mockContacts = {
            results: [
                { id: 1, name: 'John Doe', email: 'john@example.com' },
                { id: 2, name: 'Jane Smith', email: 'jane@example.com' },
            ],
        };
        global.fetch = mockFetch(mockContacts);

        render(<MockContactListPage />);

        await waitFor(() => {
            expect(screen.getByText(/John Doe/)).toBeInTheDocument();
            expect(screen.getByText(/Jane Smith/)).toBeInTheDocument();
        });
    });

    it('shows error when fetch fails', async () => {
        global.fetch = mockFetch(null, { ok: false, status: 500 });

        render(<MockContactListPage />);

        await waitFor(() => {
            expect(screen.getByTestId('error')).toHaveTextContent('Failed to fetch');
        });
    });

    it('fetches next page on pagination', async () => {
        global.fetch = mockFetch({
            results: [{ id: 1, name: 'Contact 1', email: 'c1@example.com' }],
        });

        render(<MockContactListPage />);

        await waitFor(() => {
            expect(screen.getByText(/Contact 1/)).toBeInTheDocument();
        });

        global.fetch = mockFetch({
            results: [{ id: 2, name: 'Contact 2', email: 'c2@example.com' }],
        });

        await userEvent.click(screen.getByRole('button', { name: 'Next Page' }));

        await waitFor(() => {
            expect(global.fetch).toHaveBeenCalledWith('/api/contacts?page=2');
        });
    });
});

// =============================================================================
// Lead Detail Data Fetching Tests
// =============================================================================

describe('Lead Detail Data Fetching', () => {
    interface Lead {
        id: number;
        name: string;
        company: string;
        status: string;
        score: number;
    }

    const MockLeadDetailPage = ({ leadId }: { leadId: number }) => {
        const [lead, setLead] = React.useState<Lead | null>(null);
        const [loading, setLoading] = React.useState(true);
        const [error, setError] = React.useState<string | null>(null);

        React.useEffect(() => {
            const fetchLead = async () => {
                try {
                    setLoading(true);
                    const response = await fetch(`/api/leads/${leadId}`);
                    if (response.status === 404) throw new Error('Lead not found');
                    if (!response.ok) throw new Error('Failed to fetch');
                    const data = await response.json();
                    setLead(data);
                } catch (err) {
                    setError((err as Error).message);
                } finally {
                    setLoading(false);
                }
            };
            fetchLead();
        }, [leadId]);

        if (error) return <div data-testid="error">{error}</div>;
        if (loading) return <div data-testid="loading">Loading...</div>;
        if (!lead) return null;

        return (
            <div data-testid="lead-detail">
                <h1>{lead.name}</h1>
                <p>Company: {lead.company}</p>
                <p>Status: {lead.status}</p>
                <p>Score: {lead.score}</p>
            </div>
        );
    };

    it('fetches and displays lead details', async () => {
        const mockLead = {
            id: 1,
            name: 'Hot Lead',
            company: 'Tech Corp',
            status: 'qualified',
            score: 85,
        };
        global.fetch = mockFetch(mockLead);

        render(<MockLeadDetailPage leadId={1} />);

        await waitFor(() => {
            expect(screen.getByText('Hot Lead')).toBeInTheDocument();
            expect(screen.getByText('Company: Tech Corp')).toBeInTheDocument();
            expect(screen.getByText('Status: qualified')).toBeInTheDocument();
            expect(screen.getByText('Score: 85')).toBeInTheDocument();
        });
    });

    it('shows 404 error for non-existent lead', async () => {
        global.fetch = mockFetch(null, { ok: false, status: 404 });

        render(<MockLeadDetailPage leadId={999} />);

        await waitFor(() => {
            expect(screen.getByTestId('error')).toHaveTextContent('Lead not found');
        });
    });
});

// =============================================================================
// Opportunity Pipeline Data Tests
// =============================================================================

describe('Opportunity Pipeline Data', () => {
    interface Stage {
        id: number;
        name: string;
        opportunities: Array<{ id: number; name: string; value: number }>;
    }

    const MockPipelinePage = () => {
        const [stages, setStages] = React.useState<Stage[]>([]);
        const [loading, setLoading] = React.useState(true);

        React.useEffect(() => {
            const fetchPipeline = async () => {
                const response = await fetch('/api/pipeline');
                const data = await response.json();
                setStages(data.stages);
                setLoading(false);
            };
            fetchPipeline();
        }, []);

        if (loading) return <div data-testid="loading">Loading pipeline...</div>;

        const totalValue = stages.flatMap((s) => s.opportunities).reduce((sum, o) => sum + o.value, 0);

        return (
            <div data-testid="pipeline">
                <div data-testid="total-value">${totalValue.toLocaleString()}</div>
                {stages.map((stage) => (
                    <div key={stage.id} data-testid={`stage-${stage.id}`}>
                        <h3>{stage.name}</h3>
                        <span>{stage.opportunities.length} deals</span>
                        {stage.opportunities.map((opp) => (
                            <div key={opp.id}>{opp.name}</div>
                        ))}
                    </div>
                ))}
            </div>
        );
    };

    it('renders pipeline stages with opportunities', async () => {
        const mockPipeline = {
            stages: [
                {
                    id: 1,
                    name: 'Prospecting',
                    opportunities: [
                        { id: 1, name: 'Deal A', value: 50000 },
                        { id: 2, name: 'Deal B', value: 75000 },
                    ],
                },
                {
                    id: 2,
                    name: 'Negotiation',
                    opportunities: [{ id: 3, name: 'Deal C', value: 100000 }],
                },
            ],
        };
        global.fetch = mockFetch(mockPipeline);

        render(<MockPipelinePage />);

        await waitFor(() => {
            expect(screen.getByText('Prospecting')).toBeInTheDocument();
            expect(screen.getByText('Negotiation')).toBeInTheDocument();
            expect(screen.getByTestId('stage-1')).toHaveTextContent('2 deals');
        });
    });

    it('calculates total pipeline value', async () => {
        const mockPipeline = {
            stages: [
                {
                    id: 1,
                    name: 'Stage 1',
                    opportunities: [
                        { id: 1, name: 'Deal A', value: 100000 },
                        { id: 2, name: 'Deal B', value: 50000 },
                    ],
                },
            ],
        };
        global.fetch = mockFetch(mockPipeline);

        render(<MockPipelinePage />);

        await waitFor(() => {
            expect(screen.getByTestId('total-value')).toHaveTextContent('$150,000');
        });
    });
});

// =============================================================================
// Dashboard Stats Data Tests
// =============================================================================

describe('Dashboard Stats Data', () => {
    interface DashboardStats {
        contacts: number;
        leads: number;
        opportunities: number;
        revenue: number;
        tasks: number;
    }

    const MockDashboardPage = () => {
        const [stats, setStats] = React.useState<DashboardStats | null>(null);
        const [loading, setLoading] = React.useState(true);
        const [refreshing, setRefreshing] = React.useState(false);

        const fetchStats = async (isRefresh = false) => {
            if (isRefresh) setRefreshing(true);
            else setLoading(true);

            const response = await fetch('/api/dashboard/stats');
            const data = await response.json();
            setStats(data);
            setLoading(false);
            setRefreshing(false);
        };

        React.useEffect(() => {
            fetchStats();
        }, []);

        if (loading) return <div data-testid="loading">Loading dashboard...</div>;
        if (!stats) return null;

        return (
            <div data-testid="dashboard">
                <button onClick={() => fetchStats(true)} disabled={refreshing}>
                    {refreshing ? 'Refreshing...' : 'Refresh'}
                </button>
                <div data-testid="stat-contacts">Contacts: {stats.contacts}</div>
                <div data-testid="stat-leads">Leads: {stats.leads}</div>
                <div data-testid="stat-opportunities">Opportunities: {stats.opportunities}</div>
                <div data-testid="stat-revenue">Revenue: ${stats.revenue.toLocaleString()}</div>
                <div data-testid="stat-tasks">Tasks: {stats.tasks}</div>
            </div>
        );
    };

    it('displays dashboard statistics', async () => {
        const mockStats = {
            contacts: 150,
            leads: 45,
            opportunities: 20,
            revenue: 500000,
            tasks: 12,
        };
        global.fetch = mockFetch(mockStats);

        render(<MockDashboardPage />);

        await waitFor(() => {
            expect(screen.getByTestId('stat-contacts')).toHaveTextContent('150');
            expect(screen.getByTestId('stat-leads')).toHaveTextContent('45');
            expect(screen.getByTestId('stat-opportunities')).toHaveTextContent('20');
            expect(screen.getByTestId('stat-revenue')).toHaveTextContent('$500,000');
            expect(screen.getByTestId('stat-tasks')).toHaveTextContent('12');
        });
    });

    it('refreshes stats on button click', async () => {
        global.fetch = mockFetch({
            contacts: 100,
            leads: 30,
            opportunities: 10,
            revenue: 300000,
            tasks: 5,
        });

        render(<MockDashboardPage />);

        await waitFor(() => {
            expect(screen.getByTestId('stat-contacts')).toHaveTextContent('100');
        });

        global.fetch = mockFetch({
            contacts: 105,
            leads: 32,
            opportunities: 12,
            revenue: 320000,
            tasks: 6,
        });

        await userEvent.click(screen.getByRole('button', { name: 'Refresh' }));

        await waitFor(() => {
            expect(screen.getByTestId('stat-contacts')).toHaveTextContent('105');
        });
    });
});

// =============================================================================
// Search Integration Tests
// =============================================================================

describe('Search Data Fetching', () => {
    interface SearchResult {
        id: number;
        type: string;
        title: string;
    }

    const MockSearchComponent = () => {
        const [query, setQuery] = React.useState('');
        const [results, setResults] = React.useState<SearchResult[]>([]);
        const [loading, setLoading] = React.useState(false);

        React.useEffect(() => {
            if (!query || query.length < 2) {
                setResults([]);
                return;
            }

            const searchTimeout = setTimeout(async () => {
                setLoading(true);
                const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                const data = await response.json();
                setResults(data.results);
                setLoading(false);
            }, 300);

            return () => clearTimeout(searchTimeout);
        }, [query]);

        return (
            <div data-testid="search">
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search..."
                    aria-label="Search"
                />
                {loading && <span data-testid="search-loading">Searching...</span>}
                <ul data-testid="search-results">
                    {results.map((r) => (
                        <li key={`${r.type}-${r.id}`}>
                            [{r.type}] {r.title}
                        </li>
                    ))}
                </ul>
            </div>
        );
    };

    beforeEach(() => {
        jest.useFakeTimers();
    });

    afterEach(() => {
        jest.useRealTimers();
    });

    it('searches after debounce delay', async () => {
        const mockResults = {
            results: [
                { id: 1, type: 'contact', title: 'John Doe' },
                { id: 2, type: 'lead', title: 'New Lead' },
            ],
        };
        global.fetch = mockFetch(mockResults);

        const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });
        render(<MockSearchComponent />);

        const input = screen.getByLabelText('Search');
        await user.type(input, 'john');

        // Should not have searched yet
        expect(global.fetch).not.toHaveBeenCalled();

        // Advance past debounce
        jest.advanceTimersByTime(300);

        await waitFor(() => {
            expect(global.fetch).toHaveBeenCalledWith('/api/search?q=john');
        });
    });

    it('does not search with less than 2 characters', async () => {
        global.fetch = mockFetch({ results: [] });

        const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });
        render(<MockSearchComponent />);

        const input = screen.getByLabelText('Search');
        await user.type(input, 'a');

        jest.advanceTimersByTime(500);

        expect(global.fetch).not.toHaveBeenCalled();
    });
});

// =============================================================================
// Form Submission Tests
// =============================================================================

describe('Form Submission Integration', () => {
    interface ContactFormData {
        firstName: string;
        lastName: string;
        email: string;
    }

    const MockContactForm = ({ onSuccess }: { onSuccess?: (id: number) => void }) => {
        const [formData, setFormData] = React.useState<ContactFormData>({
            firstName: '',
            lastName: '',
            email: '',
        });
        const [submitting, setSubmitting] = React.useState(false);
        const [error, setError] = React.useState<string | null>(null);
        const [success, setSuccess] = React.useState(false);

        const handleSubmit = async (e: React.FormEvent) => {
            e.preventDefault();
            setSubmitting(true);
            setError(null);

            try {
                const response = await fetch('/api/contacts', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData),
                });

                if (!response.ok) {
                    const data = await response.json();
                    throw new Error(data.message || 'Failed to create contact');
                }

                const created = await response.json();
                setSuccess(true);
                onSuccess?.(created.id);
            } catch (err) {
                setError((err as Error).message);
            } finally {
                setSubmitting(false);
            }
        };

        if (success) {
            return <div data-testid="success">Contact created successfully!</div>;
        }

        return (
            <form onSubmit={handleSubmit} data-testid="contact-form">
                {error && <div data-testid="form-error">{error}</div>}
                <input
                    type="text"
                    name="firstName"
                    placeholder="First Name"
                    value={formData.firstName}
                    onChange={(e) => setFormData((d) => ({ ...d, firstName: e.target.value }))}
                    aria-label="First Name"
                />
                <input
                    type="text"
                    name="lastName"
                    placeholder="Last Name"
                    value={formData.lastName}
                    onChange={(e) => setFormData((d) => ({ ...d, lastName: e.target.value }))}
                    aria-label="Last Name"
                />
                <input
                    type="email"
                    name="email"
                    placeholder="Email"
                    value={formData.email}
                    onChange={(e) => setFormData((d) => ({ ...d, email: e.target.value }))}
                    aria-label="Email"
                />
                <button type="submit" disabled={submitting}>
                    {submitting ? 'Creating...' : 'Create Contact'}
                </button>
            </form>
        );
    };

    it('submits form and shows success', async () => {
        global.fetch = mockFetch({ id: 1, firstName: 'John', lastName: 'Doe', email: 'john@example.com' });

        render(<MockContactForm />);

        await userEvent.type(screen.getByLabelText('First Name'), 'John');
        await userEvent.type(screen.getByLabelText('Last Name'), 'Doe');
        await userEvent.type(screen.getByLabelText('Email'), 'john@example.com');
        await userEvent.click(screen.getByRole('button', { name: 'Create Contact' }));

        await waitFor(() => {
            expect(screen.getByTestId('success')).toBeInTheDocument();
        });
    });

    it('shows error on submission failure', async () => {
        global.fetch = jest.fn(() =>
            Promise.resolve({
                ok: false,
                status: 400,
                json: () => Promise.resolve({ message: 'Email already exists' }),
            } as Response)
        );

        render(<MockContactForm />);

        await userEvent.type(screen.getByLabelText('First Name'), 'John');
        await userEvent.type(screen.getByLabelText('Last Name'), 'Doe');
        await userEvent.type(screen.getByLabelText('Email'), 'existing@example.com');
        await userEvent.click(screen.getByRole('button', { name: 'Create Contact' }));

        await waitFor(() => {
            expect(screen.getByTestId('form-error')).toHaveTextContent('Email already exists');
        });
    });

    it('calls onSuccess callback with created id', async () => {
        global.fetch = mockFetch({ id: 42, firstName: 'Jane', lastName: 'Doe', email: 'jane@example.com' });
        const handleSuccess = jest.fn();

        render(<MockContactForm onSuccess={handleSuccess} />);

        await userEvent.type(screen.getByLabelText('First Name'), 'Jane');
        await userEvent.type(screen.getByLabelText('Last Name'), 'Doe');
        await userEvent.type(screen.getByLabelText('Email'), 'jane@example.com');
        await userEvent.click(screen.getByRole('button', { name: 'Create Contact' }));

        await waitFor(() => {
            expect(handleSuccess).toHaveBeenCalledWith(42);
        });
    });
});

// =============================================================================
// Real-time Updates Integration Tests
// =============================================================================

describe('Real-time Updates', () => {
    interface Notification {
        id: number;
        message: string;
        timestamp: string;
    }

    const MockNotificationCenter = () => {
        const [notifications, setNotifications] = React.useState<Notification[]>([]);
        const [connected, setConnected] = React.useState(false);

        // Simulate WebSocket-like behavior with polling
        React.useEffect(() => {
            setConnected(true);

            const pollInterval = setInterval(async () => {
                try {
                    const response = await fetch('/api/notifications');
                    const data = await response.json();
                    setNotifications(data.notifications);
                } catch {
                    setConnected(false);
                }
            }, 5000);

            return () => {
                clearInterval(pollInterval);
                setConnected(false);
            };
        }, []);

        return (
            <div data-testid="notification-center">
                <span data-testid="connection-status">{connected ? 'Connected' : 'Disconnected'}</span>
                <span data-testid="notification-count">{notifications.length}</span>
                <ul>
                    {notifications.map((n) => (
                        <li key={n.id}>{n.message}</li>
                    ))}
                </ul>
            </div>
        );
    };

    it('shows connection status', async () => {
        global.fetch = mockFetch({ notifications: [] });

        render(<MockNotificationCenter />);

        await waitFor(() => {
            expect(screen.getByTestId('connection-status')).toHaveTextContent('Connected');
        });
    });

    it('displays notifications from polling', async () => {
        jest.useFakeTimers();
        global.fetch = mockFetch({
            notifications: [
                { id: 1, message: 'New lead assigned', timestamp: '2025-01-24T10:00:00Z' },
                { id: 2, message: 'Meeting reminder', timestamp: '2025-01-24T10:05:00Z' },
            ],
        });

        render(<MockNotificationCenter />);

        // Advance past polling interval
        jest.advanceTimersByTime(5000);

        await waitFor(() => {
            expect(screen.getByText('New lead assigned')).toBeInTheDocument();
            expect(screen.getByText('Meeting reminder')).toBeInTheDocument();
        });

        jest.useRealTimers();
    });
});
