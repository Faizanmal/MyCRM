'use client';

import { useState, useCallback, useMemo, useRef, useEffect, ReactNode } from 'react';
import { useInView } from 'react-intersection-observer';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
    ChevronDown,
    ChevronUp,
    X,
    Filter,
    Calendar,
    User,
    Building2,
    Tag,
    Search
} from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Calendar as CalendarComponent } from '@/components/ui/calender';
import { cn } from '@/lib/utils';

/**
 * Filter types and utilities for smart filtering
 */

export interface FilterOption {
    value: string;
    label: string;
    count?: number;
    icon?: ReactNode;
}

export interface FilterConfig {
    id: string;
    label: string;
    type: 'select' | 'multi-select' | 'text' | 'date' | 'date-range' | 'number-range';
    options?: FilterOption[];
    placeholder?: string;
    icon?: ReactNode;
}

export interface ActiveFilter {
    id: string;
    value: string | string[] | { start?: Date; end?: Date };
    label: string;
}

interface SmartFiltersProps {
    filters: FilterConfig[];
    activeFilters: ActiveFilter[];
    onFilterChange: (filters: ActiveFilter[]) => void;
    onClearAll?: () => void;
    savedViews?: { id: string; name: string; filters: ActiveFilter[] }[];
    onSaveView?: (name: string, filters: ActiveFilter[]) => void;
    className?: string;
}

export function SmartFilters({
    filters,
    activeFilters,
    onFilterChange,
    onClearAll,
    savedViews = [],
    onSaveView,
    className,
}: SmartFiltersProps) {
    const [isExpanded, setIsExpanded] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');

    const handleFilterChange = useCallback((filterId: string, value: string | string[], label: string) => {
        const existing = activeFilters.find(f => f.id === filterId);

        if (existing) {
            // Update existing filter
            if (value === '' || (Array.isArray(value) && value.length === 0)) {
                // Remove filter if empty
                onFilterChange(activeFilters.filter(f => f.id !== filterId));
            } else {
                onFilterChange(activeFilters.map(f =>
                    f.id === filterId ? { ...f, value, label } : f
                ));
            }
        } else if (value !== '' && (!Array.isArray(value) || value.length > 0)) {
            // Add new filter
            onFilterChange([...activeFilters, { id: filterId, value, label }]);
        }
    }, [activeFilters, onFilterChange]);

    const removeFilter = useCallback((filterId: string) => {
        onFilterChange(activeFilters.filter(f => f.id !== filterId));
    }, [activeFilters, onFilterChange]);

    const filteredOptions = useMemo(() => {
        if (!searchTerm) return filters;
        const term = searchTerm.toLowerCase();
        return filters.filter(f =>
            f.label.toLowerCase().includes(term) ||
            f.options?.some(o => o.label.toLowerCase().includes(term))
        );
    }, [filters, searchTerm]);

    return (
        <Card className={cn('w-full', className)}>
            <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Filter className="h-4 w-4" />
                        <CardTitle className="text-sm font-medium">Filters</CardTitle>
                        {activeFilters.length > 0 && (
                            <Badge variant="secondary" className="ml-2">
                                {activeFilters.length} active
                            </Badge>
                        )}
                    </div>
                    <div className="flex items-center gap-2">
                        {savedViews.length > 0 && (
                            <Select>
                                <SelectTrigger className="w-[140px] h-8 text-xs">
                                    <SelectValue placeholder="Saved views" />
                                </SelectTrigger>
                                <SelectContent>
                                    {savedViews.map(view => (
                                        <SelectItem
                                            key={view.id}
                                            value={view.id}
                                            onClick={() => onFilterChange(view.filters)}
                                        >
                                            {view.name}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        )}
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setIsExpanded(!isExpanded)}
                        >
                            {isExpanded ? (
                                <ChevronUp className="h-4 w-4" />
                            ) : (
                                <ChevronDown className="h-4 w-4" />
                            )}
                        </Button>
                    </div>
                </div>
            </CardHeader>

            {/* Active Filters */}
            {activeFilters.length > 0 && (
                <CardContent className="py-2 border-t">
                    <div className="flex flex-wrap gap-2">
                        {activeFilters.map(filter => (
                            <Badge
                                key={filter.id}
                                variant="outline"
                                className="px-2 py-1 gap-1"
                            >
                                <span className="text-gray-500">{filter.label}:</span>
                                <span className="font-medium">
                                    {Array.isArray(filter.value)
                                        ? filter.value.join(', ')
                                        : typeof filter.value === 'object'
                                            ? `${(filter.value as { start?: Date }).start?.toLocaleDateString() || ''} - ${(filter.value as { end?: Date }).end?.toLocaleDateString() || ''}`
                                            : filter.value}
                                </span>
                                <button
                                    onClick={() => removeFilter(filter.id)}
                                    className="ml-1 hover:text-red-500"
                                >
                                    <X className="h-3 w-3" />
                                </button>
                            </Badge>
                        ))}
                        {onClearAll && (
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={onClearAll}
                                className="h-6 text-xs text-red-500 hover:text-red-700"
                            >
                                Clear all
                            </Button>
                        )}
                    </div>
                </CardContent>
            )}

            {/* Expanded Filter Panel */}
            {isExpanded && (
                <CardContent className="pt-3 border-t bg-gray-50/50">
                    <div className="space-y-4">
                        {/* Search */}
                        <div className="relative">
                            <Search className="absolute left-2 top-2.5 h-4 w-4 text-gray-400" />
                            <Input
                                placeholder="Search filters..."
                                value={searchTerm}
                                onChange={e => setSearchTerm(e.target.value)}
                                className="pl-8 h-9"
                            />
                        </div>

                        {/* Filter Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            {filteredOptions.map(filter => (
                                <FilterField
                                    key={filter.id}
                                    config={filter}
                                    value={activeFilters.find(f => f.id === filter.id)?.value}
                                    onChange={(value, label) => handleFilterChange(filter.id, value, label)}
                                />
                            ))}
                        </div>
                    </div>
                </CardContent>
            )}
        </Card>
    );
}

interface FilterFieldProps {
    config: FilterConfig;
    value?: string | string[] | { start?: Date; end?: Date };
    onChange: (value: string | string[], label: string) => void;
}

function FilterField({ config, value, onChange }: FilterFieldProps) {
    switch (config.type) {
        case 'select':
            return (
                <div className="space-y-1">
                    <label className="text-xs font-medium text-gray-500">{config.label}</label>
                    <Select
                        value={value as string || ''}
                        onValueChange={(v) => {
                            const option = config.options?.find(o => o.value === v);
                            onChange(v, option?.label || v);
                        }}
                    >
                        <SelectTrigger className="h-9">
                            <SelectValue placeholder={config.placeholder || `Select ${config.label}`} />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="">All</SelectItem>
                            {config.options?.map(option => (
                                <SelectItem key={option.value} value={option.value}>
                                    <div className="flex items-center gap-2">
                                        {option.icon}
                                        <span>{option.label}</span>
                                        {option.count !== undefined && (
                                            <Badge variant="secondary" className="ml-auto text-xs">
                                                {option.count}
                                            </Badge>
                                        )}
                                    </div>
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>
            );

        case 'text':
            return (
                <div className="space-y-1">
                    <label className="text-xs font-medium text-gray-500">{config.label}</label>
                    <Input
                        placeholder={config.placeholder || `Filter by ${config.label}`}
                        value={value as string || ''}
                        onChange={(e) => onChange(e.target.value, config.label)}
                        className="h-9"
                    />
                </div>
            );

        case 'date':
            return (
                <div className="space-y-1">
                    <label className="text-xs font-medium text-gray-500">{config.label}</label>
                    <Popover>
                        <PopoverTrigger asChild>
                            <Button variant="outline" className="w-full h-9 justify-start text-left font-normal">
                                <Calendar className="mr-2 h-4 w-4" />
                                {value ? new Date(value as string).toLocaleDateString() : config.placeholder || 'Pick a date'}
                            </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-auto p-0">
                            <CalendarComponent
                                mode="single"
                                selected={value ? new Date(value as string) : undefined}
                                onSelect={(date: Date | undefined) => date && onChange(date.toISOString(), date.toLocaleDateString())}
                            />
                        </PopoverContent>
                    </Popover>
                </div>
            );

        default:
            return null;
    }
}

// Pre-configured filter sets for common entities
export const leadFilters: FilterConfig[] = [
    {
        id: 'status',
        label: 'Status',
        type: 'select',
        icon: <Tag className="h-4 w-4" />,
        options: [
            { value: 'new', label: 'New', count: 45 },
            { value: 'contacted', label: 'Contacted', count: 23 },
            { value: 'qualified', label: 'Qualified', count: 18 },
            { value: 'proposal', label: 'Proposal', count: 12 },
            { value: 'won', label: 'Won', count: 8 },
            { value: 'lost', label: 'Lost', count: 5 },
        ],
    },
    {
        id: 'source',
        label: 'Source',
        type: 'select',
        options: [
            { value: 'website', label: 'Website' },
            { value: 'referral', label: 'Referral' },
            { value: 'social', label: 'Social Media' },
            { value: 'cold_call', label: 'Cold Call' },
            { value: 'event', label: 'Event' },
        ],
    },
    {
        id: 'assigned_to',
        label: 'Assigned To',
        type: 'select',
        icon: <User className="h-4 w-4" />,
        options: [],  // Populate dynamically
    },
    {
        id: 'company',
        label: 'Company',
        type: 'text',
        icon: <Building2 className="h-4 w-4" />,
        placeholder: 'Search company...',
    },
    {
        id: 'created_date',
        label: 'Created Date',
        type: 'date',
        icon: <Calendar className="h-4 w-4" />,
    },
];

export const contactFilters: FilterConfig[] = [
    {
        id: 'lifecycle_stage',
        label: 'Lifecycle Stage',
        type: 'select',
        options: [
            { value: 'subscriber', label: 'Subscriber' },
            { value: 'lead', label: 'Lead' },
            { value: 'opportunity', label: 'Opportunity' },
            { value: 'customer', label: 'Customer' },
            { value: 'evangelist', label: 'Evangelist' },
        ],
    },
    {
        id: 'owner',
        label: 'Owner',
        type: 'select',
        icon: <User className="h-4 w-4" />,
        options: [],
    },
    {
        id: 'company',
        label: 'Company',
        type: 'text',
        icon: <Building2 className="h-4 w-4" />,
    },
    {
        id: 'last_activity',
        label: 'Last Activity',
        type: 'date',
        icon: <Calendar className="h-4 w-4" />,
    },
];

export const opportunityFilters: FilterConfig[] = [
    {
        id: 'stage',
        label: 'Stage',
        type: 'select',
        options: [
            { value: 'prospecting', label: 'Prospecting' },
            { value: 'qualification', label: 'Qualification' },
            { value: 'proposal', label: 'Proposal' },
            { value: 'negotiation', label: 'Negotiation' },
            { value: 'closed_won', label: 'Closed Won' },
            { value: 'closed_lost', label: 'Closed Lost' },
        ],
    },
    {
        id: 'owner',
        label: 'Owner',
        type: 'select',
        icon: <User className="h-4 w-4" />,
        options: [],
    },
    {
        id: 'close_date',
        label: 'Expected Close',
        type: 'date',
        icon: <Calendar className="h-4 w-4" />,
    },
];

export default SmartFilters;
