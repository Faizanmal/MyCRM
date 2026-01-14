/**
 * Dashboard Charts Unit Tests
 * Tests for all chart components
 *
 * To run: npm install -D vitest @testing-library/react jsdom
 * Then: npx vitest run
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';

// Mock framer-motion
vi.mock('framer-motion', () => ({
    motion: {
        div: ({ children, ...props }: React.PropsWithChildren<Record<string, unknown>>) => <div {...props}>{children}</div>,
        circle: (props: Record<string, unknown>) => <circle {...props} />,
        path: (props: Record<string, unknown>) => <path {...props} />,
        span: ({ children, ...props }: React.PropsWithChildren<Record<string, unknown>>) => <span {...props}>{children}</span>,
        tr: ({ children, ...props }: React.PropsWithChildren<Record<string, unknown>>) => <tr {...props}>{children}</tr>,
    },
    AnimatePresence: ({ children }: React.PropsWithChildren<Record<string, unknown>>) => children,
}));

import {
    BarChart,
    HorizontalBarChart,
    DonutChart,
    LineChart,
    Sparkline,
    ProgressRing,
    StatCardWithSparkline,
    FunnelChart,
    HeatMap,
} from '../DashboardCharts';

// ==================== BarChart Tests ====================

describe('BarChart', () => {
    const mockData = [
        { label: 'Jan', value: 100, color: '#3b82f6' },
        { label: 'Feb', value: 200, color: '#22c55e' },
        { label: 'Mar', value: 150, color: '#f59e0b' },
    ];

    it('should render without crashing', () => {
        const { container } = render(<BarChart data={mockData} />);
        expect(container).toBeTruthy();
    });

    it('should render correct number of bars', () => {
        const { container } = render(<BarChart data={mockData} height={200} />);
        // Each data point creates a bar container
        const bars = container.querySelectorAll('[class*="rounded-t-md"]');
        expect(bars.length).toBe(mockData.length);
    });

    it('should render labels when showLabels is true', () => {
        render(<BarChart data={mockData} showLabels={true} />);
        mockData.forEach(item => {
            expect(screen.getByText(item.label)).toBeTruthy();
        });
    });

    it('should not render labels when showLabels is false', () => {
        render(<BarChart data={mockData} showLabels={false} />);
        mockData.forEach(item => {
            expect(screen.queryByText(item.label)).toBeNull();
        });
    });

    it('should handle empty data', () => {
        const { container } = render(<BarChart data={[]} />);
        expect(container).toBeTruthy();
    });

    it('should apply custom height', () => {
        const { container } = render(<BarChart data={mockData} height={300} />);
        const chartContainer = container.firstChild as HTMLElement;
        expect(chartContainer.style.height).toBe('300px');
    });
});

// ==================== HorizontalBarChart Tests ====================

describe('HorizontalBarChart', () => {
    const mockData = [
        { label: 'Product A', value: 500 },
        { label: 'Product B', value: 300 },
        { label: 'Product C', value: 200 },
    ];

    it('should render without crashing', () => {
        const { container } = render(<HorizontalBarChart data={mockData} />);
        expect(container).toBeTruthy();
    });

    it('should display all labels', () => {
        render(<HorizontalBarChart data={mockData} />);
        mockData.forEach(item => {
            expect(screen.getByText(item.label)).toBeTruthy();
        });
    });

    it('should render correct number of bars', () => {
        const { container } = render(<HorizontalBarChart data={mockData} />);
        const bars = container.querySelectorAll('[class*="rounded-full"]');
        expect(bars.length).toBeGreaterThanOrEqual(mockData.length);
    });
});

// ==================== DonutChart Tests ====================

describe('DonutChart', () => {
    const mockData = [
        { label: 'Won', value: 45, color: '#22c55e' },
        { label: 'Lost', value: 25, color: '#ef4444' },
        { label: 'Open', value: 30, color: '#3b82f6' },
    ];

    it('should render without crashing', () => {
        const { container } = render(<DonutChart data={mockData} />);
        expect(container).toBeTruthy();
    });

    it('should display total in center', () => {
        render(<DonutChart data={mockData} />);
        const total = mockData.reduce((sum, d) => sum + d.value, 0);
        expect(screen.getByText(String(total))).toBeTruthy();
    });

    it('should render legend with labels', () => {
        render(<DonutChart data={mockData} />);
        mockData.forEach(item => {
            expect(screen.getByText(item.label)).toBeTruthy();
        });
    });

    it('should render SVG circles', () => {
        const { container } = render(<DonutChart data={mockData} />);
        const circles = container.querySelectorAll('circle');
        expect(circles.length).toBe(mockData.length);
    });
});

// ==================== LineChart Tests ====================

describe('LineChart', () => {
    const mockData = [
        { date: 'Week 1', value: 100 },
        { date: 'Week 2', value: 150 },
        { date: 'Week 3', value: 120 },
        { date: 'Week 4', value: 180 },
    ];

    it('should render without crashing', () => {
        const { container } = render(<LineChart data={mockData} />);
        expect(container).toBeTruthy();
    });

    it('should render SVG paths', () => {
        const { container } = render(<LineChart data={mockData} />);
        const paths = container.querySelectorAll('path');
        expect(paths.length).toBeGreaterThan(0);
    });

    it('should render data points', () => {
        const { container } = render(<LineChart data={mockData} />);
        const circles = container.querySelectorAll('circle');
        expect(circles.length).toBe(mockData.length);
    });

    it('should render secondary line when showSecondary is true', () => {
        const dataWithSecondary = mockData.map(d => ({ ...d, secondaryValue: d.value * 0.8 }));
        const { container } = render(<LineChart data={dataWithSecondary} showSecondary={true} />);
        const paths = container.querySelectorAll('path');
        expect(paths.length).toBeGreaterThan(1);
    });
});

// ==================== Sparkline Tests ====================

describe('Sparkline', () => {
    const mockData = [10, 20, 15, 25, 30, 20, 35];

    it('should render without crashing', () => {
        const { container } = render(<Sparkline data={mockData} />);
        expect(container).toBeTruthy();
    });

    it('should render SVG element', () => {
        const { container } = render(<Sparkline data={mockData} />);
        const svg = container.querySelector('svg');
        expect(svg).toBeTruthy();
    });

    it('should render path', () => {
        const { container } = render(<Sparkline data={mockData} />);
        const path = container.querySelector('path');
        expect(path).toBeTruthy();
    });

    it('should apply custom color', () => {
        const { container } = render(<Sparkline data={mockData} color="#ff0000" />);
        const path = container.querySelector('path');
        expect(path?.getAttribute('stroke')).toBe('#ff0000');
    });

    it('should apply custom height', () => {
        const { container } = render(<Sparkline data={mockData} height={50} />);
        const svg = container.querySelector('svg');
        expect(svg?.getAttribute('height')).toBe('50');
    });
});

// ==================== ProgressRing Tests ====================

describe('ProgressRing', () => {
    it('should render without crashing', () => {
        const { container } = render(<ProgressRing value={50} />);
        expect(container).toBeTruthy();
    });

    it('should display percentage by default', () => {
        render(<ProgressRing value={75} max={100} />);
        expect(screen.getByText('75%')).toBeTruthy();
    });

    it('should display custom label', () => {
        render(<ProgressRing value={75} label="$75K" />);
        expect(screen.getByText('$75K')).toBeTruthy();
    });

    it('should display sublabel', () => {
        render(<ProgressRing value={75} sublabel="of goal" />);
        expect(screen.getByText('of goal')).toBeTruthy();
    });

    it('should render SVG circles', () => {
        const { container } = render(<ProgressRing value={50} />);
        const circles = container.querySelectorAll('circle');
        expect(circles.length).toBe(2); // Background and progress
    });

    it('should cap at 100%', () => {
        render(<ProgressRing value={150} max={100} />);
        expect(screen.getByText('100%')).toBeTruthy();
    });
});

// ==================== StatCardWithSparkline Tests ====================

describe('StatCardWithSparkline', () => {
    const props = {
        title: 'Revenue',
        value: '$125,000',
        change: 12.5,
        sparklineData: [10, 20, 15, 25, 30],
    };

    it('should render without crashing', () => {
        const { container } = render(<StatCardWithSparkline {...props} />);
        expect(container).toBeTruthy();
    });

    it('should display title', () => {
        render(<StatCardWithSparkline {...props} />);
        expect(screen.getByText('Revenue')).toBeTruthy();
    });

    it('should display value', () => {
        render(<StatCardWithSparkline {...props} />);
        expect(screen.getByText('$125,000')).toBeTruthy();
    });

    it('should display positive change with arrow up', () => {
        const { container } = render(<StatCardWithSparkline {...props} />);
        expect(screen.getByText('12.5%')).toBeTruthy();
        expect(container.querySelector('[class*="text-green"]')).toBeTruthy();
    });

    it('should display negative change with arrow down', () => {
        const { container } = render(<StatCardWithSparkline {...props} change={-5.2} />);
        expect(screen.getByText('5.2%')).toBeTruthy();
        expect(container.querySelector('[class*="text-red"]')).toBeTruthy();
    });

    it('should display change label if provided', () => {
        render(<StatCardWithSparkline {...props} changeLabel="vs last month" />);
        expect(screen.getByText('vs last month')).toBeTruthy();
    });
});

// ==================== FunnelChart Tests ====================

describe('FunnelChart', () => {
    const mockData = [
        { label: 'Leads', value: 1000 },
        { label: 'Qualified', value: 500 },
        { label: 'Proposal', value: 200 },
        { label: 'Won', value: 50 },
    ];

    it('should render without crashing', () => {
        const { container } = render(<FunnelChart data={mockData} />);
        expect(container).toBeTruthy();
    });

    it('should display all stage labels', () => {
        render(<FunnelChart data={mockData} />);
        mockData.forEach(item => {
            expect(screen.getByText(item.label)).toBeTruthy();
        });
    });

    it('should display conversion rates', () => {
        render(<FunnelChart data={mockData} />);
        // Check for conversion rate text
        expect(screen.getByText(/50\.0% conversion/)).toBeTruthy();
    });
});

// ==================== HeatMap Tests ====================

describe('HeatMap', () => {
    const mockData = [
        [1, 5, 3, 2, 4],
        [2, 3, 5, 1, 2],
        [4, 2, 3, 5, 1],
    ];
    const rows = ['Week 1', 'Week 2', 'Week 3'];
    const cols = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'];

    it('should render without crashing', () => {
        const { container } = render(<HeatMap data={mockData} rows={rows} cols={cols} />);
        expect(container).toBeTruthy();
    });

    it('should display column headers', () => {
        render(<HeatMap data={mockData} rows={rows} cols={cols} />);
        cols.forEach(col => {
            expect(screen.getByText(col)).toBeTruthy();
        });
    });

    it('should display row labels', () => {
        render(<HeatMap data={mockData} rows={rows} cols={cols} />);
        rows.forEach(row => {
            expect(screen.getByText(row)).toBeTruthy();
        });
    });

    it('should render correct number of cells', () => {
        const { container } = render(<HeatMap data={mockData} rows={rows} cols={cols} />);
        const cells = container.querySelectorAll('[class*="rounded-sm"]');
        expect(cells.length).toBe(mockData.length * mockData[0].length);
    });
});

// ==================== Edge Cases ====================

describe('Edge Cases', () => {
    it('BarChart handles single data point', () => {
        const { container } = render(<BarChart data={[{ label: 'A', value: 100 }]} />);
        expect(container).toBeTruthy();
    });

    it('DonutChart handles zero values', () => {
        const { container } = render(
            <DonutChart data={[{ label: 'A', value: 0 }, { label: 'B', value: 0 }]} />
        );
        expect(container).toBeTruthy();
    });

    it('LineChart handles single data point', () => {
        const { container } = render(<LineChart data={[{ date: 'Day 1', value: 100 }]} />);
        expect(container).toBeTruthy();
    });

    it('Sparkline handles empty data', () => {
        const { container } = render(<Sparkline data={[]} />);
        expect(container).toBeTruthy();
    });

    it('ProgressRing handles zero value', () => {
        render(<ProgressRing value={0} />);
        expect(screen.getByText('0%')).toBeTruthy();
    });
});

