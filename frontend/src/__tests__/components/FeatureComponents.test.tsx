/**
 * MyCRM Frontend - Feature-Specific Component Tests
 * 
 * Tests for CRM-specific feature components
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

// =============================================================================
// Contact Card Component Tests
// =============================================================================

describe('ContactCard Component', () => {
    interface Contact {
        id: number;
        firstName: string;
        lastName: string;
        email: string;
        phone?: string;
        company?: string;
        avatar?: string;
    }

    const MockContactCard = ({
        contact,
        onEdit,
        onDelete,
        onClick
    }: {
        contact: Contact;
        onEdit?: (id: number) => void;
        onDelete?: (id: number) => void;
        onClick?: (id: number) => void;
    }) => (
        <div 
            data-testid="contact-card" 
            onClick={() => onClick?.(contact.id)}
            onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') onClick?.(contact.id); }}
            tabIndex={0}
        >
            {contact.avatar ? (
                <img src={contact.avatar} alt={`${contact.firstName} ${contact.lastName}`} />
            ) : (
                <span data-testid="avatar-fallback">
                    {contact.firstName[0]}{contact.lastName[0]}
                </span>
            )}
            <h3>{contact.firstName} {contact.lastName}</h3>
            <p>{contact.email}</p>
            {contact.phone && <p>{contact.phone}</p>}
            {contact.company && <p>{contact.company}</p>}
            <div>
                <button onClick={(e) => { e.stopPropagation(); onEdit?.(contact.id); }}>Edit</button>
                <button onClick={(e) => { e.stopPropagation(); onDelete?.(contact.id); }}>Delete</button>
            </div>
        </div>
    );

    const mockContact: Contact = {
        id: 1,
        firstName: 'John',
        lastName: 'Doe',
        email: 'john@example.com',
        phone: '+1-555-123-4567',
        company: 'Acme Corp'
    };

    it('renders contact information', () => {
        render(<MockContactCard contact={mockContact} />);

        expect(screen.getByText('John Doe')).toBeInTheDocument();
        expect(screen.getByText('john@example.com')).toBeInTheDocument();
        expect(screen.getByText('+1-555-123-4567')).toBeInTheDocument();
        expect(screen.getByText('Acme Corp')).toBeInTheDocument();
    });

    it('shows avatar fallback when no image', () => {
        render(<MockContactCard contact={mockContact} />);
        expect(screen.getByTestId('avatar-fallback')).toHaveTextContent('JD');
    });

    it('calls onClick when card clicked', async () => {
        const handleClick = jest.fn();
        render(<MockContactCard contact={mockContact} onClick={handleClick} />);

        await userEvent.click(screen.getByTestId('contact-card'));

        expect(handleClick).toHaveBeenCalledWith(1);
    });

    it('calls onEdit when edit button clicked', async () => {
        const handleEdit = jest.fn();
        render(<MockContactCard contact={mockContact} onEdit={handleEdit} />);

        await userEvent.click(screen.getByRole('button', { name: 'Edit' }));

        expect(handleEdit).toHaveBeenCalledWith(1);
    });

    it('calls onDelete when delete button clicked', async () => {
        const handleDelete = jest.fn();
        render(<MockContactCard contact={mockContact} onDelete={handleDelete} />);

        await userEvent.click(screen.getByRole('button', { name: 'Delete' }));

        expect(handleDelete).toHaveBeenCalledWith(1);
    });
});

// =============================================================================
// Lead Status Badge Tests
// =============================================================================

describe('LeadStatusBadge Component', () => {
    type LeadStatus = 'new' | 'contacted' | 'qualified' | 'converted' | 'lost';

    const MockLeadStatusBadge = ({ status }: { status: LeadStatus }) => {
        const statusConfig: Record<LeadStatus, { label: string; color: string }> = {
            new: { label: 'New', color: 'blue' },
            contacted: { label: 'Contacted', color: 'yellow' },
            qualified: { label: 'Qualified', color: 'green' },
            converted: { label: 'Converted', color: 'purple' },
            lost: { label: 'Lost', color: 'red' }
        };

        const config = statusConfig[status];

        return (
            <span data-testid="status-badge" data-color={config.color}>
                {config.label}
            </span>
        );
    };

    it.each([
        ['new', 'New', 'blue'],
        ['contacted', 'Contacted', 'yellow'],
        ['qualified', 'Qualified', 'green'],
        ['converted', 'Converted', 'purple'],
        ['lost', 'Lost', 'red']
    ] as const)('renders %s status correctly', (status, label, color) => {
        render(<MockLeadStatusBadge status={status} />);

        expect(screen.getByText(label)).toBeInTheDocument();
        expect(screen.getByTestId('status-badge')).toHaveAttribute('data-color', color);
    });
});

// =============================================================================
// Pipeline Stage Component Tests
// =============================================================================

describe('PipelineStage Component', () => {
    interface Opportunity {
        id: number;
        name: string;
        value: number;
    }

    interface Stage {
        id: number;
        name: string;
        opportunities: Opportunity[];
    }

    const MockPipelineStage = ({
        stage,
        onOpportunityClick
    }: {
        stage: Stage;
        onOpportunityClick?: (id: number) => void;
    }) => (
        <div data-testid={`stage-${stage.id}`}>
            <h3>{stage.name}</h3>
            <span data-testid="stage-count">{stage.opportunities.length}</span>
            <span data-testid="stage-value">
                ${stage.opportunities.reduce((sum, o) => sum + o.value, 0).toLocaleString()}
            </span>
            <div data-testid="opportunities">
                {stage.opportunities.map((opp) => (
                    <div 
                        key={opp.id} 
                        data-testid={`opp-${opp.id}`}
                        onClick={() => onOpportunityClick?.(opp.id)}
                        onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') onOpportunityClick?.(opp.id); }}
                        tabIndex={0}
                    >
                        <span>{opp.name}</span>
                        <span>${opp.value.toLocaleString()}</span>
                    </div>
                ))}
            </div>
        </div>
    );

    const mockStage: Stage = {
        id: 1,
        name: 'Prospecting',
        opportunities: [
            { id: 1, name: 'Deal 1', value: 50000 },
            { id: 2, name: 'Deal 2', value: 75000 }
        ]
    };

    it('renders stage name and count', () => {
        render(<MockPipelineStage stage={mockStage} />);

        expect(screen.getByText('Prospecting')).toBeInTheDocument();
        expect(screen.getByTestId('stage-count')).toHaveTextContent('2');
    });

    it('calculates total stage value', () => {
        render(<MockPipelineStage stage={mockStage} />);
        expect(screen.getByTestId('stage-value')).toHaveTextContent('$125,000');
    });

    it('renders opportunities', () => {
        render(<MockPipelineStage stage={mockStage} />);

        expect(screen.getByText('Deal 1')).toBeInTheDocument();
        expect(screen.getByText('Deal 2')).toBeInTheDocument();
    });

    it('calls onOpportunityClick when opportunity clicked', async () => {
        const handleClick = jest.fn();
        render(<MockPipelineStage stage={mockStage} onOpportunityClick={handleClick} />);

        await userEvent.click(screen.getByTestId('opp-1'));

        expect(handleClick).toHaveBeenCalledWith(1);
    });
});

// =============================================================================
// Task List Component Tests
// =============================================================================

describe('TaskList Component', () => {
    interface Task {
        id: number;
        title: string;
        status: 'pending' | 'in_progress' | 'completed';
        priority: 'low' | 'medium' | 'high' | 'urgent';
        dueDate?: string;
    }

    const MockTaskList = ({
        tasks,
        onComplete,
        onEdit,
        emptyMessage = 'No tasks'
    }: {
        tasks: Task[];
        onComplete?: (id: number) => void;
        onEdit?: (id: number) => void;
        emptyMessage?: string;
    }) => {
        if (tasks.length === 0) {
            return <div data-testid="empty-state">{emptyMessage}</div>;
        }

        return (
            <ul data-testid="task-list">
                {tasks.map((task) => (
                    <li key={task.id} data-testid={`task-${task.id}`} data-priority={task.priority}>
                        <input
                            type="checkbox"
                            checked={task.status === 'completed'}
                            onChange={() => onComplete?.(task.id)}
                            aria-label={`Complete ${task.title}`}
                        />
                        <span className={task.status === 'completed' ? 'completed' : ''}>
                            {task.title}
                        </span>
                        {task.dueDate && <span data-testid="due-date">{task.dueDate}</span>}
                        <button onClick={() => onEdit?.(task.id)}>Edit</button>
                    </li>
                ))}
            </ul>
        );
    };

    const mockTasks: Task[] = [
        { id: 1, title: 'Call client', status: 'pending', priority: 'high', dueDate: '2025-01-25' },
        { id: 2, title: 'Send proposal', status: 'in_progress', priority: 'medium' },
        { id: 3, title: 'Review contract', status: 'completed', priority: 'low' }
    ];

    it('renders all tasks', () => {
        render(<MockTaskList tasks={mockTasks} />);

        expect(screen.getByText('Call client')).toBeInTheDocument();
        expect(screen.getByText('Send proposal')).toBeInTheDocument();
        expect(screen.getByText('Review contract')).toBeInTheDocument();
    });

    it('shows empty state when no tasks', () => {
        render(<MockTaskList tasks={[]} emptyMessage="All done!" />);
        expect(screen.getByTestId('empty-state')).toHaveTextContent('All done!');
    });

    it('shows completed status', () => {
        render(<MockTaskList tasks={mockTasks} />);
        const completedCheckbox = screen.getByLabelText('Complete Review contract');
        expect(completedCheckbox).toBeChecked();
    });

    it('calls onComplete when checkbox toggled', async () => {
        const handleComplete = jest.fn();
        render(<MockTaskList tasks={mockTasks} onComplete={handleComplete} />);

        await userEvent.click(screen.getByLabelText('Complete Call client'));

        expect(handleComplete).toHaveBeenCalledWith(1);
    });

    it('shows priority indicator', () => {
        render(<MockTaskList tasks={mockTasks} />);
        expect(screen.getByTestId('task-1')).toHaveAttribute('data-priority', 'high');
    });

    it('shows due date when present', () => {
        render(<MockTaskList tasks={mockTasks} />);
        expect(screen.getByText('2025-01-25')).toBeInTheDocument();
    });
});

// =============================================================================
// Activity Feed Component Tests
// =============================================================================

describe('ActivityFeed Component', () => {
    interface Activity {
        id: number;
        type: 'call' | 'email' | 'meeting' | 'note';
        description: string;
        timestamp: string;
        user: string;
    }

    const MockActivityFeed = ({
        activities,
        loading,
        onLoadMore
    }: {
        activities: Activity[];
        loading?: boolean;
        onLoadMore?: () => void;
    }) => (
        <div data-testid="activity-feed">
            {loading && <div data-testid="loading">Loading...</div>}
            {activities.map((activity) => (
                <div key={activity.id} data-testid={`activity-${activity.id}`} data-type={activity.type}>
                    <span>{activity.type}</span>
                    <p>{activity.description}</p>
                    <span>{activity.user}</span>
                    <time>{activity.timestamp}</time>
                </div>
            ))}
            {onLoadMore && (
                <button onClick={onLoadMore} disabled={loading}>
                    Load More
                </button>
            )}
        </div>
    );

    const mockActivities: Activity[] = [
        { id: 1, type: 'call', description: 'Discussed pricing', timestamp: '2025-01-24 10:00', user: 'John' },
        { id: 2, type: 'email', description: 'Sent proposal', timestamp: '2025-01-24 09:00', user: 'Jane' }
    ];

    it('renders activities', () => {
        render(<MockActivityFeed activities={mockActivities} />);

        expect(screen.getByText('Discussed pricing')).toBeInTheDocument();
        expect(screen.getByText('Sent proposal')).toBeInTheDocument();
    });

    it('shows activity type', () => {
        render(<MockActivityFeed activities={mockActivities} />);
        expect(screen.getByTestId('activity-1')).toHaveAttribute('data-type', 'call');
    });

    it('shows loading state', () => {
        render(<MockActivityFeed activities={[]} loading />);
        expect(screen.getByTestId('loading')).toBeInTheDocument();
    });

    it('calls onLoadMore when button clicked', async () => {
        const handleLoadMore = jest.fn();
        render(<MockActivityFeed activities={mockActivities} onLoadMore={handleLoadMore} />);

        await userEvent.click(screen.getByRole('button', { name: 'Load More' }));

        expect(handleLoadMore).toHaveBeenCalled();
    });
});

// =============================================================================
// Statistics Card Component Tests
// =============================================================================

describe('StatisticsCard Component', () => {
    const MockStatCard = ({
        title,
        value,
        change,
        changeType,
        icon
    }: {
        title: string;
        value: string | number;
        change?: number;
        changeType?: 'increase' | 'decrease';
        icon?: React.ReactNode;
    }) => (
        <div data-testid="stat-card">
            {icon && <span data-testid="icon">{icon}</span>}
            <h4>{title}</h4>
            <span data-testid="value">{value}</span>
            {change !== undefined && (
                <span data-testid="change" data-type={changeType}>
                    {changeType === 'increase' ? '+' : '-'}{Math.abs(change)}%
                </span>
            )}
        </div>
    );

    it('renders title and value', () => {
        render(<MockStatCard title="Total Revenue" value="$125,000" />);

        expect(screen.getByText('Total Revenue')).toBeInTheDocument();
        expect(screen.getByTestId('value')).toHaveTextContent('$125,000');
    });

    it('shows increase change', () => {
        render(<MockStatCard title="Sales" value={100} change={15} changeType="increase" />);
        expect(screen.getByTestId('change')).toHaveTextContent('+15%');
        expect(screen.getByTestId('change')).toHaveAttribute('data-type', 'increase');
    });

    it('shows decrease change', () => {
        render(<MockStatCard title="Churn" value={5} change={10} changeType="decrease" />);
        expect(screen.getByTestId('change')).toHaveTextContent('-10%');
        expect(screen.getByTestId('change')).toHaveAttribute('data-type', 'decrease');
    });

    it('renders icon when provided', () => {
        render(<MockStatCard title="Contacts" value={250} icon={<span>📊</span>} />);
        expect(screen.getByTestId('icon')).toBeInTheDocument();
    });
});

// =============================================================================
// Search Results Component Tests
// =============================================================================

describe('SearchResults Component', () => {
    interface SearchResult {
        id: number;
        type: 'contact' | 'lead' | 'opportunity' | 'task';
        title: string;
        subtitle?: string;
    }

    const MockSearchResults = ({
        results,
        query,
        loading,
        onResultClick
    }: {
        results: SearchResult[];
        query: string;
        loading?: boolean;
        onResultClick?: (result: SearchResult) => void;
    }) => {
        if (loading) {
            return <div data-testid="search-loading">Searching...</div>;
        }

        if (!query) {
            return <div data-testid="search-empty">Start typing to search</div>;
        }

        if (results.length === 0) {
            return <div data-testid="no-results">No results found for &quot;{query}&quot;</div>;
        }

        return (
            <ul data-testid="search-results">
                {results.map((result) => (
                    <li
                        key={`${result.type}-${result.id}`}
                        onClick={() => onResultClick?.(result)}
                        onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') onResultClick?.(result); }}
                        tabIndex={0}
                        data-type={result.type}
                    >
                        <span>{result.type}</span>
                        <span>{result.title}</span>
                        {result.subtitle && <span>{result.subtitle}</span>}
                    </li>
                ))}
            </ul>
        );
    };

    const mockResults: SearchResult[] = [
        { id: 1, type: 'contact', title: 'John Doe', subtitle: 'john@example.com' },
        { id: 2, type: 'lead', title: 'New Lead', subtitle: 'Tech Corp' },
        { id: 3, type: 'opportunity', title: 'Big Deal' }
    ];

    it('shows empty state when no query', () => {
        render(<MockSearchResults results={[]} query="" />);
        expect(screen.getByTestId('search-empty')).toBeInTheDocument();
    });

    it('shows loading state', () => {
        render(<MockSearchResults results={[]} query="test" loading />);
        expect(screen.getByTestId('search-loading')).toBeInTheDocument();
    });

    it('shows no results message', () => {
        render(<MockSearchResults results={[]} query="xyz123" />);
        expect(screen.getByTestId('no-results')).toHaveTextContent('No results found for "xyz123"');
    });

    it('renders search results', () => {
        render(<MockSearchResults results={mockResults} query="test" />);

        expect(screen.getByText('John Doe')).toBeInTheDocument();
        expect(screen.getByText('New Lead')).toBeInTheDocument();
        expect(screen.getByText('Big Deal')).toBeInTheDocument();
    });

    it('calls onResultClick when result clicked', async () => {
        const handleClick = jest.fn();
        render(<MockSearchResults results={mockResults} query="test" onResultClick={handleClick} />);

        await userEvent.click(screen.getByText('John Doe'));

        expect(handleClick).toHaveBeenCalledWith(mockResults[0]);
    });
});

// =============================================================================
// Notification Component Tests
// =============================================================================

describe('Notification Component', () => {
    interface Notification {
        id: number;
        title: string;
        message: string;
        type: 'info' | 'success' | 'warning' | 'error';
        read: boolean;
    }

    const MockNotification = ({
        notification,
        onRead,
        onDismiss
    }: {
        notification: Notification;
        onRead?: (id: number) => void;
        onDismiss?: (id: number) => void;
    }) => (
        <div 
            data-testid={`notification-${notification.id}`}
            data-type={notification.type}
            data-read={notification.read}
        >
            <h4>{notification.title}</h4>
            <p>{notification.message}</p>
            {!notification.read && (
                <button onClick={() => onRead?.(notification.id)}>Mark as read</button>
            )}
            <button onClick={() => onDismiss?.(notification.id)}>Dismiss</button>
        </div>
    );

    const mockNotification: Notification = {
        id: 1,
        title: 'New Lead Assigned',
        message: 'A new lead has been assigned to you',
        type: 'info',
        read: false
    };

    it('renders notification content', () => {
        render(<MockNotification notification={mockNotification} />);

        expect(screen.getByText('New Lead Assigned')).toBeInTheDocument();
        expect(screen.getByText('A new lead has been assigned to you')).toBeInTheDocument();
    });

    it('shows type indicator', () => {
        render(<MockNotification notification={mockNotification} />);
        expect(screen.getByTestId('notification-1')).toHaveAttribute('data-type', 'info');
    });

    it('shows mark as read button for unread', () => {
        render(<MockNotification notification={mockNotification} />);
        expect(screen.getByRole('button', { name: 'Mark as read' })).toBeInTheDocument();
    });

    it('hides mark as read button for read notifications', () => {
        render(<MockNotification notification={{ ...mockNotification, read: true }} />);
        expect(screen.queryByRole('button', { name: 'Mark as read' })).not.toBeInTheDocument();
    });

    it('calls onRead when mark as read clicked', async () => {
        const handleRead = jest.fn();
        render(<MockNotification notification={mockNotification} onRead={handleRead} />);

        await userEvent.click(screen.getByRole('button', { name: 'Mark as read' }));

        expect(handleRead).toHaveBeenCalledWith(1);
    });

    it('calls onDismiss when dismiss clicked', async () => {
        const handleDismiss = jest.fn();
        render(<MockNotification notification={mockNotification} onDismiss={handleDismiss} />);

        await userEvent.click(screen.getByRole('button', { name: 'Dismiss' }));

        expect(handleDismiss).toHaveBeenCalledWith(1);
    });
});
