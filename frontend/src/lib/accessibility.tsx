'use client';

import { useEffect, useRef, useState, KeyboardEvent, ReactNode } from 'react';

import { cn } from '@/lib/utils';

/**
 * Accessibility utilities and components for MyCRM
 */

/**
 * Screen reader only text - visually hidden but accessible to screen readers
 */
export function ScreenReaderOnly({ children }: { children: ReactNode }) {
    return (
        <span className="sr-only">
            {children}
        </span>
    );
}

/**
 * Skip to main content link for keyboard navigation
 */
export function SkipToContent({ href = '#main-content' }: { href?: string }) {
    return (
        <a
            href={href}
            className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-9999 focus:bg-white focus:px-4 focus:py-2 focus:rounded-md focus:shadow-lg focus:ring-2 focus:ring-blue-500"
        >
            Skip to main content
        </a>
    );
}

/**
 * Live region for announcing dynamic content changes
 */
export function LiveRegion({
    message,
    politeness = 'polite',
    atomic = true,
}: {
    message: string;
    politeness?: 'polite' | 'assertive' | 'off';
    atomic?: boolean;
}) {
    return (
        <div
            role="status"
            aria-live={politeness}
            aria-atomic={atomic}
            className="sr-only"
        >
            {message}
        </div>
    );
}

/**
 * Hook for announcing messages to screen readers
 */
export function useAnnounce() {
    const [message, setMessage] = useState('');

    const announce = (text: string) => {
        // Clear first to ensure re-announcement
        setMessage('');
        setTimeout(() => setMessage(text), 100);
    };

    return { message, announce };
}

/**
 * Focus trap for modals and dialogs
 */
export function useFocusTrap<T extends HTMLElement>(isActive: boolean) {
    const containerRef = useRef<T>(null);

    useEffect(() => {
        if (!isActive || !containerRef.current) return;

        const container = containerRef.current;
        const focusableElements = container.querySelectorAll<HTMLElement>(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        // Store previously focused element
        const previouslyFocused = document.activeElement as HTMLElement;

        // Focus first element
        firstElement?.focus();

        const handleKeyDown = (e: globalThis.KeyboardEvent) => {
            if (e.key !== 'Tab') return;

            if (e.shiftKey) {
                if (document.activeElement === firstElement) {
                    e.preventDefault();
                    lastElement?.focus();
                }
            } else {
                if (document.activeElement === lastElement) {
                    e.preventDefault();
                    firstElement?.focus();
                }
            }
        };

        container.addEventListener('keydown', handleKeyDown);

        return () => {
            container.removeEventListener('keydown', handleKeyDown);
            // Restore focus
            previouslyFocused?.focus();
        };
    }, [isActive]);

    return containerRef;
}

/**
 * Roving tabindex for keyboard navigation in lists
 */
export function useRovingTabIndex<T extends HTMLElement>(
    itemCount: number,
    orientation: 'horizontal' | 'vertical' = 'vertical'
) {
    const [activeIndex, setActiveIndex] = useState(0);
    const itemRefs = useRef<(T | null)[]>([]);

    const handleKeyDown = (e: KeyboardEvent, index: number) => {
        const goNext = orientation === 'vertical' ? 'ArrowDown' : 'ArrowRight';
        const goPrev = orientation === 'vertical' ? 'ArrowUp' : 'ArrowLeft';

        let newIndex = index;

        switch (e.key) {
            case goNext:
                e.preventDefault();
                newIndex = (index + 1) % itemCount;
                break;
            case goPrev:
                e.preventDefault();
                newIndex = (index - 1 + itemCount) % itemCount;
                break;
            case 'Home':
                e.preventDefault();
                newIndex = 0;
                break;
            case 'End':
                e.preventDefault();
                newIndex = itemCount - 1;
                break;
            default:
                return;
        }

        setActiveIndex(newIndex);
        itemRefs.current[newIndex]?.focus();
    };

    const getItemProps = (index: number) => ({
        ref: (el: T | null) => {
            itemRefs.current[index] = el;
        },
        tabIndex: index === activeIndex ? 0 : -1,
        onKeyDown: (e: KeyboardEvent) => handleKeyDown(e, index),
        onFocus: () => setActiveIndex(index),
    });

    return { activeIndex, setActiveIndex, getItemProps };
}

/**
 * Accessible icon button wrapper
 */
export function IconButton({
    label,
    children,
    className,
    ...props
}: {
    label: string;
    children: ReactNode;
    className?: string;
} & React.ButtonHTMLAttributes<HTMLButtonElement>) {
    return (
        <button
            aria-label={label}
            className={cn(
                'inline-flex items-center justify-center rounded-md p-2',
                'hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'disabled:opacity-50 disabled:pointer-events-none',
                className
            )}
            {...props}
        >
            {children}
            <ScreenReaderOnly>{label}</ScreenReaderOnly>
        </button>
    );
}

/**
 * Progress indicator with accessibility
 */
export function AccessibleProgress({
    value,
    max = 100,
    label,
    showValue = true,
    className,
}: {
    value: number;
    max?: number;
    label: string;
    showValue?: boolean;
    className?: string;
}) {
    const percentage = Math.round((value / max) * 100);

    return (
        <div className={cn('space-y-1', className)}>
            <div className="flex justify-between text-sm">
                <span id="progress-label">{label}</span>
                {showValue && <span>{percentage}%</span>}
            </div>
            <div
                role="progressbar"
                aria-labelledby="progress-label"
                aria-valuenow={value}
                aria-valuemin={0}
                aria-valuemax={max}
                className="h-2 bg-gray-200 rounded-full overflow-hidden"
            >
                <div
                    className="h-full bg-blue-500 transition-all duration-300"
                    style={{ width: `${percentage}%` }}
                />
            </div>
        </div>
    );
}

/**
 * Loading indicator with accessibility
 */
export function AccessibleLoader({
    size = 'md',
    label = 'Loading...',
}: {
    size?: 'sm' | 'md' | 'lg';
    label?: string;
}) {
    const sizeClasses = {
        sm: 'h-4 w-4',
        md: 'h-8 w-8',
        lg: 'h-12 w-12',
    };

    return (
        <div role="status" aria-label={label} className="flex items-center justify-center">
            <svg
                className={cn('animate-spin text-blue-500', sizeClasses[size])}
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
            >
                <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                />
                <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
            </svg>
            <ScreenReaderOnly>{label}</ScreenReaderOnly>
        </div>
    );
}

/**
 * Accessible table with proper ARIA attributes
 */
export function AccessibleTable({
    caption,
    headers,
    data,
    onRowClick,
    className,
}: {
    caption: string;
    headers: { key: string; label: string; sortable?: boolean }[];
    data: Record<string, ReactNode>[];
    onRowClick?: (row: Record<string, ReactNode>, index: number) => void;
    className?: string;
}) {
    const [sortKey, setSortKey] = useState<string | null>(null);
    const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

    const handleSort = (key: string) => {
        if (sortKey === key) {
            setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
        } else {
            setSortKey(key);
            setSortOrder('asc');
        }
    };

    return (
        <div className={cn('overflow-x-auto', className)}>
            <table className="min-w-full divide-y divide-gray-200" role="table">
                <caption className="sr-only">{caption}</caption>
                <thead className="bg-gray-50">
                    <tr>
                        {headers.map((header) => (
                            <th
                                key={header.key}
                                scope="col"
                                className={cn(
                                    'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
                                    header.sortable && 'cursor-pointer hover:bg-gray-100'
                                )}
                                onClick={header.sortable ? () => handleSort(header.key) : undefined}
                                aria-sort={
                                    sortKey === header.key
                                        ? sortOrder === 'asc'
                                            ? 'ascending'
                                            : 'descending'
                                        : undefined
                                }
                            >
                                {header.label}
                                {header.sortable && sortKey === header.key && (
                                    <span className="ml-1">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                                )}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                    {data.map((row, index) => (
                        <tr
                            key={index}
                            onClick={onRowClick ? () => onRowClick(row, index) : undefined}
                            className={cn(
                                onRowClick && 'cursor-pointer hover:bg-gray-50'
                            )}
                            tabIndex={onRowClick ? 0 : undefined}
                            onKeyDown={(e) => {
                                if (onRowClick && (e.key === 'Enter' || e.key === ' ')) {
                                    e.preventDefault();
                                    onRowClick(row, index);
                                }
                            }}
                            role={onRowClick ? 'button' : undefined}
                        >
                            {headers.map((header) => (
                                <td
                                    key={header.key}
                                    className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100"
                                >
                                    {row[header.key]}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

/**
 * Custom checkbox with full accessibility
 */
export function AccessibleCheckbox({
    id,
    label,
    checked,
    onChange,
    disabled = false,
    indeterminate = false,
    className,
}: {
    id: string;
    label: string;
    checked: boolean;
    onChange: (checked: boolean) => void;
    disabled?: boolean;
    indeterminate?: boolean;
    className?: string;
}) {
    const checkboxRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        if (checkboxRef.current) {
            checkboxRef.current.indeterminate = indeterminate;
        }
    }, [indeterminate]);

    return (
        <div className={cn('flex items-center gap-2', className)}>
            <input
                ref={checkboxRef}
                type="checkbox"
                id={id}
                checked={checked}
                onChange={(e) => onChange(e.target.checked)}
                disabled={disabled}
                className={cn(
                    'h-4 w-4 rounded border-gray-300 text-blue-600',
                    'focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
                    'disabled:opacity-50 disabled:cursor-not-allowed'
                )}
                aria-checked={indeterminate ? 'mixed' : checked}
            />
            <label
                htmlFor={id}
                className={cn(
                    'text-sm font-medium text-gray-700',
                    disabled && 'opacity-50 cursor-not-allowed'
                )}
            >
                {label}
            </label>
        </div>
    );
}

