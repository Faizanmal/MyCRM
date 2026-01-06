'use client';

import { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
// import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
    Search,
    Filter,
    SortAsc,
    SortDesc,
    MoreHorizontal,
    Eye,
    Edit,
    Trash2,
    Archive,
    Star,
    Download,
    ChevronLeft,
    ChevronRight,
    CheckSquare,
    Square,
    X,
    Sparkles,
    RefreshCw,
    Columns,
} from 'lucide-react';
// import { toast } from 'sonner';

interface Column<T> {
    key: keyof T | string;
    label: string;
    sortable?: boolean;
    filterable?: boolean;
    width?: string;
    render?: (item: T, value: unknown) => React.ReactNode;
    hidden?: boolean;
}

interface Filter {
    key: string;
    operator: 'equals' | 'contains' | 'gt' | 'lt' | 'in';
    value: string | number | string[];
}

interface InteractiveTableProps<T extends { id: string | number }> {
    data: T[];
    columns: Column<T>[];
    onRowClick?: (item: T) => void;
    onSelectionChange?: (selectedIds: (string | number)[]) => void;
    onDelete?: (ids: (string | number)[]) => void;
    onExport?: (ids: (string | number)[]) => void;
    searchPlaceholder?: string;
    emptyMessage?: string;
    isLoading?: boolean;
    pageSize?: number;
    showBulkActions?: boolean;
    showColumnToggle?: boolean;
    showSmartFilters?: boolean;
}

const smartFilters = [
    { label: 'High Priority', icon: Star, filter: { key: 'priority', operator: 'equals' as const, value: 'high' } },
    { label: 'Recent', icon: RefreshCw, filter: { key: 'created_at', operator: 'gt' as const, value: '7d' } },
    { label: 'Needs Attention', icon: Sparkles, filter: { key: 'status', operator: 'in' as const, value: ['pending', 'overdue'] } },
];

export default function InteractiveTable<T extends { id: string | number }>({
    data,
    columns: initialColumns,
    onRowClick,
    onSelectionChange,
    onDelete,
    onExport,
    searchPlaceholder = 'Search...',
    emptyMessage = 'No data found',
    isLoading = false,
    pageSize = 10,
    showBulkActions = true,
    showColumnToggle = true,
    showSmartFilters = true,
}: InteractiveTableProps<T>) {
    const [columns, setColumns] = useState(initialColumns);
    const [searchQuery, setSearchQuery] = useState('');
    const [sortConfig, setSortConfig] = useState<{ key: string; direction: 'asc' | 'desc' } | null>(null);
    const [selectedIds, setSelectedIds] = useState<Set<string | number>>(new Set());
    const [activeFilters, setActiveFilters] = useState<Filter[]>([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [isColumnMenuOpen, setIsColumnMenuOpen] = useState(false);

    // Filter and search data
    const filteredData = useMemo(() => {
        let result = [...data];

        // Apply search
        if (searchQuery) {
            const query = searchQuery.toLowerCase();
            result = result.filter(item =>
                columns.some(col => {
                    const value = (item as Record<string, unknown>)[col.key as string];
                    return value && String(value).toLowerCase().includes(query);
                })
            );
        }

        // Apply filters
        activeFilters.forEach(filter => {
            result = result.filter(item => {
                const value = (item as Record<string, unknown>)[filter.key];
                switch (filter.operator) {
                    case 'equals':
                        return value === filter.value;
                    case 'contains':
                        return String(value).toLowerCase().includes(String(filter.value).toLowerCase());
                    case 'gt':
                        return Number(value) > Number(filter.value);
                    case 'lt':
                        return Number(value) < Number(filter.value);
                    case 'in':
                        return Array.isArray(filter.value) && filter.value.includes(String(value));
                    default:
                        return true;
                }
            });
        });

        // Apply sorting
        if (sortConfig) {
            result.sort((a, b) => {
                const aVal = (a as Record<string, unknown>)[sortConfig.key];
                const bVal = (b as Record<string, unknown>)[sortConfig.key];

                if (aVal === bVal) return 0;

                const comparison = aVal! > bVal! ? 1 : -1;
                return sortConfig.direction === 'asc' ? comparison : -comparison;
            });
        }

        return result;
    }, [data, searchQuery, activeFilters, sortConfig, columns]);

    // Pagination
    const totalPages = Math.ceil(filteredData.length / pageSize);
    const paginatedData = filteredData.slice(
        (currentPage - 1) * pageSize,
        currentPage * pageSize
    );

    // Selection handlers
    const toggleSelectAll = () => {
        if (selectedIds.size === paginatedData.length) {
            setSelectedIds(new Set());
        } else {
            setSelectedIds(new Set(paginatedData.map(item => item.id)));
        }
    };

    const toggleSelect = (id: string | number) => {
        const newSelected = new Set(selectedIds);
        if (newSelected.has(id)) {
            newSelected.delete(id);
        } else {
            newSelected.add(id);
        }
        setSelectedIds(newSelected);
    };

    useEffect(() => {
        onSelectionChange?.(Array.from(selectedIds));
    }, [selectedIds, onSelectionChange]);

    // Sort handler
    const handleSort = (key: string) => {
        setSortConfig(prev => {
            if (prev?.key === key) {
                if (prev.direction === 'asc') return { key, direction: 'desc' };
                if (prev.direction === 'desc') return null;
            }
            return { key, direction: 'asc' };
        });
    };

    // Toggle column visibility
    const toggleColumn = (key: string) => {
        setColumns(prev =>
            prev.map(col =>
                col.key === key ? { ...col, hidden: !col.hidden } : col
            )
        );
    };

    // Add smart filter
    const addSmartFilter = (filter: Filter) => {
        if (!activeFilters.find(f => f.key === filter.key)) {
            setActiveFilters(prev => [...prev, filter]);
            setCurrentPage(1);
        }
    };

    // Remove filter
    const removeFilter = (key: string) => {
        setActiveFilters(prev => prev.filter(f => f.key !== key));
    };

    // Bulk actions
    const handleBulkDelete = () => {
        if (onDelete) {
            onDelete(Array.from(selectedIds));
            setSelectedIds(new Set());
        }
    };

    const handleBulkExport = () => {
        if (onExport) {
            onExport(Array.from(selectedIds));
        }
    };

    const visibleColumns = columns.filter(col => !col.hidden);
    const isAllSelected = paginatedData.length > 0 && selectedIds.size === paginatedData.length;
    const hasSelection = selectedIds.size > 0;

    return (
        <div className="space-y-4">
            {/* Toolbar */}
            <div className="flex flex-wrap items-center gap-3">
                {/* Search */}
                <div className="relative flex-1 min-w-[200px] max-w-md">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <Input
                        placeholder={searchPlaceholder}
                        value={searchQuery}
                        onChange={e => {
                            setSearchQuery(e.target.value);
                            setCurrentPage(1);
                        }}
                        className="pl-9"
                    />
                    {searchQuery && (
                        <button
                            onClick={() => setSearchQuery('')}
                            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                        >
                            <X className="w-4 h-4" />
                        </button>
                    )}
                </div>

                {/* Smart Filters */}
                {showSmartFilters && (
                    <div className="flex items-center gap-2">
                        {smartFilters.map(sf => (
                            <Button
                                key={sf.label}
                                variant={activeFilters.find(f => f.key === sf.filter.key) ? 'default' : 'outline'}
                                size="sm"
                                onClick={() => {
                                    const existing = activeFilters.find(f => f.key === sf.filter.key);
                                    if (existing) {
                                        removeFilter(sf.filter.key);
                                    } else {
                                        addSmartFilter(sf.filter);
                                    }
                                }}
                                className="gap-1.5"
                            >
                                <sf.icon className="w-3.5 h-3.5" />
                                {sf.label}
                            </Button>
                        ))}
                    </div>
                )}

                {/* Column Toggle */}
                {showColumnToggle && (
                    <DropdownMenu open={isColumnMenuOpen} onOpenChange={setIsColumnMenuOpen}>
                        <DropdownMenuTrigger asChild>
                            <Button variant="outline" size="sm">
                                <Columns className="w-4 h-4 mr-2" />
                                Columns
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="w-48">
                            {columns.map(col => (
                                <DropdownMenuItem
                                    key={String(col.key)}
                                    onClick={() => toggleColumn(String(col.key))}
                                    className="flex items-center gap-2"
                                >
                                    <Checkbox checked={!col.hidden} />
                                    {col.label}
                                </DropdownMenuItem>
                            ))}
                        </DropdownMenuContent>
                    </DropdownMenu>
                )}
            </div>

            {/* Active Filters */}
            {activeFilters.length > 0 && (
                <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-sm text-gray-500">Filters:</span>
                    {activeFilters.map(filter => (
                        <Badge
                            key={filter.key}
                            variant="secondary"
                            className="gap-1 pl-2 cursor-pointer hover:bg-gray-200"
                            onClick={() => removeFilter(filter.key)}
                        >
                            {filter.key}: {Array.isArray(filter.value) ? filter.value.join(', ') : String(filter.value)}
                            <X className="w-3 h-3 ml-1" />
                        </Badge>
                    ))}
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setActiveFilters([])}
                        className="text-xs h-6"
                    >
                        Clear all
                    </Button>
                </div>
            )}

            {/* Bulk Actions Bar */}
            <AnimatePresence>
                {showBulkActions && hasSelection && (
                    <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="flex items-center gap-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800"
                    >
                        <span className="text-sm font-medium text-blue-700 dark:text-blue-300">
                            {selectedIds.size} item{selectedIds.size > 1 ? 's' : ''} selected
                        </span>
                        <div className="flex items-center gap-2 ml-auto">
                            {onExport && (
                                <Button variant="outline" size="sm" onClick={handleBulkExport}>
                                    <Download className="w-4 h-4 mr-2" />
                                    Export
                                </Button>
                            )}
                            {onDelete && (
                                <Button variant="destructive" size="sm" onClick={handleBulkDelete}>
                                    <Trash2 className="w-4 h-4 mr-2" />
                                    Delete
                                </Button>
                            )}
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setSelectedIds(new Set())}
                            >
                                Cancel
                            </Button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Table */}
            <div className="border rounded-lg overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-gray-50 dark:bg-gray-800 border-b">
                            <tr>
                                {showBulkActions && (
                                    <th className="w-12 px-4 py-3">
                                        <button onClick={toggleSelectAll} className="flex items-center justify-center">
                                            {isAllSelected ? (
                                                <CheckSquare className="w-4 h-4 text-blue-600" />
                                            ) : hasSelection ? (
                                                <div className="w-4 h-4 border-2 border-blue-600 rounded bg-blue-600/20" />
                                            ) : (
                                                <Square className="w-4 h-4 text-gray-400" />
                                            )}
                                        </button>
                                    </th>
                                )}
                                {visibleColumns.map(column => (
                                    <th
                                        key={String(column.key)}
                                        className={`px-4 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider ${column.sortable ? 'cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700' : ''
                                            }`}
                                        style={{ width: column.width }}
                                        onClick={() => column.sortable && handleSort(String(column.key))}
                                    >
                                        <div className="flex items-center gap-2">
                                            {column.label}
                                            {column.sortable && sortConfig?.key === column.key && (
                                                sortConfig.direction === 'asc' ? (
                                                    <SortAsc className="w-4 h-4" />
                                                ) : (
                                                    <SortDesc className="w-4 h-4" />
                                                )
                                            )}
                                        </div>
                                    </th>
                                ))}
                                <th className="w-12 px-4 py-3"></th>
                            </tr>
                        </thead>
                        <tbody className="divide-y dark:divide-gray-800">
                            {isLoading ? (
                                [...Array(pageSize)].map((_, i) => (
                                    <tr key={i} className="animate-pulse">
                                        {showBulkActions && (
                                            <td className="px-4 py-4">
                                                <div className="w-4 h-4 bg-gray-200 rounded" />
                                            </td>
                                        )}
                                        {visibleColumns.map(col => (
                                            <td key={String(col.key)} className="px-4 py-4">
                                                <div className="h-4 bg-gray-200 rounded w-3/4" />
                                            </td>
                                        ))}
                                        <td className="px-4 py-4">
                                            <div className="w-4 h-4 bg-gray-200 rounded" />
                                        </td>
                                    </tr>
                                ))
                            ) : paginatedData.length === 0 ? (
                                <tr>
                                    <td
                                        colSpan={visibleColumns.length + (showBulkActions ? 2 : 1)}
                                        className="px-4 py-12 text-center text-gray-500"
                                    >
                                        <Search className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                                        <p>{emptyMessage}</p>
                                    </td>
                                </tr>
                            ) : (
                                paginatedData.map((item, index) => (
                                    <motion.tr
                                        key={item.id}
                                        initial={{ opacity: 0, y: 5 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ delay: index * 0.02 }}
                                        className={`group hover:bg-gray-50 dark:hover:bg-gray-800/50 cursor-pointer ${selectedIds.has(item.id) ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                                            }`}
                                        onClick={() => onRowClick?.(item)}
                                    >
                                        {showBulkActions && (
                                            <td className="px-4 py-4" onClick={e => e.stopPropagation()}>
                                                <button onClick={() => toggleSelect(item.id)}>
                                                    {selectedIds.has(item.id) ? (
                                                        <CheckSquare className="w-4 h-4 text-blue-600" />
                                                    ) : (
                                                        <Square className="w-4 h-4 text-gray-400 group-hover:text-gray-600" />
                                                    )}
                                                </button>
                                            </td>
                                        )}
                                        {visibleColumns.map(column => {
                                            const value = (item as Record<string, unknown>)[column.key as string];
                                            return (
                                                <td key={String(column.key)} className="px-4 py-4 text-sm">
                                                    {column.render ? column.render(item, value) : String(value ?? '-')}
                                                </td>
                                            );
                                        })}
                                        <td className="px-4 py-4" onClick={e => e.stopPropagation()}>
                                            <DropdownMenu>
                                                <DropdownMenuTrigger asChild>
                                                    <Button variant="ghost" size="icon" className="h-8 w-8 opacity-0 group-hover:opacity-100">
                                                        <MoreHorizontal className="w-4 h-4" />
                                                    </Button>
                                                </DropdownMenuTrigger>
                                                <DropdownMenuContent align="end">
                                                    <DropdownMenuItem>
                                                        <Eye className="w-4 h-4 mr-2" />
                                                        View
                                                    </DropdownMenuItem>
                                                    <DropdownMenuItem>
                                                        <Edit className="w-4 h-4 mr-2" />
                                                        Edit
                                                    </DropdownMenuItem>
                                                    <DropdownMenuItem>
                                                        <Archive className="w-4 h-4 mr-2" />
                                                        Archive
                                                    </DropdownMenuItem>
                                                    <DropdownMenuSeparator />
                                                    <DropdownMenuItem className="text-red-600">
                                                        <Trash2 className="w-4 h-4 mr-2" />
                                                        Delete
                                                    </DropdownMenuItem>
                                                </DropdownMenuContent>
                                            </DropdownMenu>
                                        </td>
                                    </motion.tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
                <div className="flex items-center justify-between px-2">
                    <p className="text-sm text-gray-500">
                        Showing {(currentPage - 1) * pageSize + 1} to{' '}
                        {Math.min(currentPage * pageSize, filteredData.length)} of{' '}
                        {filteredData.length} results
                    </p>
                    <div className="flex items-center gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                            disabled={currentPage === 1}
                        >
                            <ChevronLeft className="w-4 h-4" />
                        </Button>
                        <div className="flex items-center gap-1">
                            {[...Array(Math.min(5, totalPages))].map((_, i) => {
                                let pageNum: number;
                                if (totalPages <= 5) {
                                    pageNum = i + 1;
                                } else if (currentPage <= 3) {
                                    pageNum = i + 1;
                                } else if (currentPage >= totalPages - 2) {
                                    pageNum = totalPages - 4 + i;
                                } else {
                                    pageNum = currentPage - 2 + i;
                                }

                                return (
                                    <Button
                                        key={pageNum}
                                        variant={currentPage === pageNum ? 'default' : 'ghost'}
                                        size="sm"
                                        onClick={() => setCurrentPage(pageNum)}
                                        className="w-8 h-8 p-0"
                                    >
                                        {pageNum}
                                    </Button>
                                );
                            })}
                        </div>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                            disabled={currentPage === totalPages}
                        >
                            <ChevronRight className="w-4 h-4" />
                        </Button>
                    </div>
                </div>
            )}
        </div>
    );
}
