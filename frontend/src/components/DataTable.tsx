'use client';

import React, { useState, useMemo, useCallback, ReactNode } from 'react';
import {
    useReactTable,
    getCoreRowModel,
    getFilteredRowModel,
    getPaginationRowModel,
    getSortedRowModel,
    flexRender,
    ColumnDef,
    SortingState,
    ColumnFiltersState,
    VisibilityState,
    RowSelectionState,
    FilterFn,
} from '@tanstack/react-table';
import {
    ChevronDown,
    ChevronUp,
    ChevronsUpDown,
    ChevronLeft,
    ChevronRight,
    ChevronsLeft,
    ChevronsRight,
    Settings2,
    Search,
    X,
    Download,
    MoreHorizontal,
} from 'lucide-react';

import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
    DropdownMenuCheckboxItem,
} from '@/components/ui/dropdown-menu';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { cn } from '@/lib/utils';

/**
 * Enhanced Data Table Component
 * 
 * Features:
 * - Sorting (single/multi column)
 * - Filtering (global and column-specific)
 * - Pagination
 * - Row selection
 * - Column visibility toggle
 * - Responsive design
 * - Export functionality
 * - Custom cell renderers
 */

interface DataTableProps<TData> {
    columns: ColumnDef<TData, unknown>[];
    data: TData[];
    searchKey?: string;
    searchPlaceholder?: string;
    pageSize?: number;
    pageSizeOptions?: number[];
    showColumnToggle?: boolean;
    showExport?: boolean;
    showRowSelection?: boolean;
    onRowClick?: (row: TData) => void;
    onSelectionChange?: (selectedRows: TData[]) => void;
    onExport?: (data: TData[]) => void;
    isLoading?: boolean;
    emptyMessage?: string;
    className?: string;
    stickyHeader?: boolean;
    rowActions?: (row: TData) => ReactNode;
}

// Fuzzy filter function for global search
const fuzzyFilter: FilterFn<unknown> = (row, columnId, value) => {
    const itemValue = row.getValue(columnId);
    if (itemValue == null) return false;

    const searchValue = String(value).toLowerCase();
    const cellValue = String(itemValue).toLowerCase();

    return cellValue.includes(searchValue);
};

export function DataTable<TData>({
    columns,
    data,
    searchPlaceholder = 'Search...',
    pageSize = 10,
    pageSizeOptions = [10, 20, 30, 50],
    showColumnToggle = true,
    showExport = false,
    showRowSelection = false,
    onRowClick,
    onSelectionChange,
    onExport,
    isLoading = false,
    emptyMessage = 'No results found.',
    className,
    stickyHeader = false,
    rowActions,
}: DataTableProps<TData>) {
    const [sorting, setSorting] = useState<SortingState>([]);
    const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
    const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({});
    const [rowSelection, setRowSelection] = useState<RowSelectionState>({});
    const [globalFilter, setGlobalFilter] = useState('');

    // Add selection column if enabled
    const tableColumns = useMemo(() => {
        const cols = [...columns];

        if (showRowSelection) {
            cols.unshift({
                id: 'select',
                header: ({ table }) => (
                    <Checkbox
                        checked={table.getIsAllPageRowsSelected()}
                        onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
                        aria-label="Select all"
                    />
                ),
                cell: ({ row }) => (
                    <Checkbox
                        checked={row.getIsSelected()}
                        onCheckedChange={(value) => row.toggleSelected(!!value)}
                        aria-label="Select row"
                        onClick={(e) => e.stopPropagation()}
                    />
                ),
                enableSorting: false,
                enableHiding: false,
                size: 40,
            });
        }

        if (rowActions) {
            cols.push({
                id: 'actions',
                header: () => <span className="sr-only">Actions</span>,
                cell: ({ row }) => rowActions(row.original),
                enableSorting: false,
                enableHiding: false,
                size: 60,
            });
        }

        return cols;
    }, [columns, showRowSelection, rowActions]);

    // eslint-disable-next-line react-hooks/incompatible-library -- TanStack's useReactTable returns non-memoizable functions
    const table = useReactTable<TData>({
        data,
        columns: tableColumns,
        getCoreRowModel: getCoreRowModel(),
        getPaginationRowModel: getPaginationRowModel(),
        getSortedRowModel: getSortedRowModel(),
        getFilteredRowModel: getFilteredRowModel(),
        onSortingChange: setSorting,
        onColumnFiltersChange: setColumnFilters,
        onColumnVisibilityChange: setColumnVisibility,
        onRowSelectionChange: setRowSelection,
        onGlobalFilterChange: setGlobalFilter,
        globalFilterFn: fuzzyFilter as FilterFn<TData>,
        state: {
            sorting,
            columnFilters,
            columnVisibility,
            rowSelection,
            globalFilter,
        },
        initialState: {
            pagination: {
                pageSize,
            },
        },
    });

    // Notify parent of selection changes
    React.useEffect(() => {
        if (onSelectionChange) {
            const selectedRows = table
                .getSelectedRowModel()
                .rows.map((row) => row.original);
            onSelectionChange(selectedRows as TData[]);
        }
    }, [rowSelection, onSelectionChange, table]);

    const handleExport = useCallback(() => {
        if (onExport) {
            const exportData = table.getFilteredRowModel().rows.map((row) => row.original);
            onExport(exportData as TData[]);
        }
    }, [onExport, table]);

    return (
        <div className={cn('space-y-4', className)}>
            {/* Toolbar */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div className="flex items-center gap-2 w-full sm:w-auto">
                    {/* Global Search */}
                    <div className="relative flex-1 sm:w-64">
                        <Search className="absolute left-2 top-2.5 h-4 w-4 text-gray-400" />
                        <Input
                            placeholder={searchPlaceholder}
                            value={globalFilter ?? ''}
                            onChange={(e) => setGlobalFilter(e.target.value)}
                            className="pl-8 pr-8"
                        />
                        {globalFilter && (
                            <button
                                onClick={() => setGlobalFilter('')}
                                className="absolute right-2 top-2.5 text-gray-400 hover:text-gray-600"
                            >
                                <X className="h-4 w-4" />
                            </button>
                        )}
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    {/* Export Button */}
                    {showExport && onExport && (
                        <Button variant="outline" size="sm" onClick={handleExport}>
                            <Download className="h-4 w-4 mr-2" />
                            Export
                        </Button>
                    )}

                    {/* Column Visibility Toggle */}
                    {showColumnToggle && (
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <Button variant="outline" size="sm">
                                    <Settings2 className="h-4 w-4 mr-2" />
                                    Columns
                                </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end" className="w-48">
                                <DropdownMenuLabel>Toggle columns</DropdownMenuLabel>
                                <DropdownMenuSeparator />
                                {table
                                    .getAllColumns()
                                    .filter((column) => column.getCanHide())
                                    .map((column) => (
                                        <DropdownMenuCheckboxItem
                                            key={column.id}
                                            checked={column.getIsVisible()}
                                            onCheckedChange={(value) => column.toggleVisibility(!!value)}
                                        >
                                            {column.id}
                                        </DropdownMenuCheckboxItem>
                                    ))}
                            </DropdownMenuContent>
                        </DropdownMenu>
                    )}
                </div>
            </div>

            {/* Selection Info */}
            {showRowSelection && Object.keys(rowSelection).length > 0 && (
                <div className="flex items-center gap-2 text-sm text-gray-600 bg-blue-50 px-3 py-2 rounded-md">
                    <span>{Object.keys(rowSelection).length} row(s) selected</span>
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => table.resetRowSelection()}
                    >
                        Clear selection
                    </Button>
                </div>
            )}

            {/* Table */}
            <div className="border rounded-lg overflow-hidden">
                <div className={cn('overflow-auto', stickyHeader && 'max-h-[600px]')}>
                    <table className="w-full">
                        <thead className={cn(
                            'bg-gray-50',
                            stickyHeader && 'sticky top-0 z-10'
                        )}>
                            {table.getHeaderGroups().map((headerGroup) => (
                                <tr key={headerGroup.id}>
                                    {headerGroup.headers.map((header) => (
                                        <th
                                            key={header.id}
                                            className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                                            style={{ width: header.getSize() }}
                                        >
                                            {header.isPlaceholder ? null : (
                                                <div
                                                    className={cn(
                                                        'flex items-center gap-1',
                                                        header.column.getCanSort() && 'cursor-pointer select-none'
                                                    )}
                                                    onClick={header.column.getToggleSortingHandler()}
                                                    onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { const handler = header.column.getToggleSortingHandler(); if (handler) handler(e); e.preventDefault(); } }}
                                                    tabIndex={header.column.getCanSort() ? 0 : -1}
                                                    role={header.column.getCanSort() ? 'button' : undefined}
                                                >
                                                    {flexRender(
                                                        header.column.columnDef.header,
                                                        header.getContext()
                                                    )}
                                                    {header.column.getCanSort() && (
                                                        <span className="ml-1">
                                                            {{
                                                                asc: <ChevronUp className="h-4 w-4" />,
                                                                desc: <ChevronDown className="h-4 w-4" />,
                                                            }[header.column.getIsSorted() as string] ?? (
                                                                    <ChevronsUpDown className="h-4 w-4 text-gray-400" />
                                                                )}
                                                        </span>
                                                    )}
                                                </div>
                                            )}
                                        </th>
                                    ))}
                                </tr>
                            ))}
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {isLoading ? (
                                // Loading skeleton
                                [...Array(5)].map((_, i) => (
                                    <tr key={i}>
                                        {tableColumns.map((_, j) => (
                                            <td key={j} className="px-4 py-4">
                                                <div className="h-4 bg-gray-200 rounded animate-pulse" />
                                            </td>
                                        ))}
                                    </tr>
                                ))
                            ) : table.getRowModel().rows.length > 0 ? (
                                table.getRowModel().rows.map((row) => (
                                    <tr
                                        key={row.id}
                                        className={cn(
                                            'hover:bg-gray-50 transition-colors',
                                            row.getIsSelected() && 'bg-blue-50',
                                            onRowClick && 'cursor-pointer'
                                        )}
                                        onClick={() => onRowClick?.(row.original as TData)}
                                    >
                                        {row.getVisibleCells().map((cell) => (
                                            <td key={cell.id} className="px-4 py-4 text-sm text-gray-900 dark:text-gray-100">
                                                {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                            </td>
                                        ))}
                                    </tr>
                                ))
                            ) : (
                                // Empty state
                                <tr>
                                    <td
                                        colSpan={tableColumns.length}
                                        className="px-4 py-12 text-center text-gray-500"
                                    >
                                        {emptyMessage}
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Pagination */}
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                <div className="flex items-center gap-2 text-sm text-gray-600">
                    <span>
                        Showing {table.getState().pagination.pageIndex * table.getState().pagination.pageSize + 1} to{' '}
                        {Math.min(
                            (table.getState().pagination.pageIndex + 1) * table.getState().pagination.pageSize,
                            table.getFilteredRowModel().rows.length
                        )}{' '}
                        of {table.getFilteredRowModel().rows.length} results
                    </span>
                </div>

                <div className="flex items-center gap-2">
                    {/* Page Size Selector */}
                    <div className="flex items-center gap-2">
                        <span className="text-sm text-gray-600">Rows per page:</span>
                        <Select
                            value={String(table.getState().pagination.pageSize)}
                            onValueChange={(value) => table.setPageSize(Number(value))}
                        >
                            <SelectTrigger className="w-16 h-8">
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                                {pageSizeOptions.map((size: number) => (
                                    <SelectItem key={size} value={String(size)}>
                                        {size}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>

                    {/* Page Navigation */}
                    <div className="flex items-center gap-1">
                        <Button
                            variant="outline"
                            size="icon"
                            className="h-8 w-8"
                            onClick={() => table.setPageIndex(0)}
                            disabled={!table.getCanPreviousPage()}
                        >
                            <ChevronsLeft className="h-4 w-4" />
                        </Button>
                        <Button
                            variant="outline"
                            size="icon"
                            className="h-8 w-8"
                            onClick={() => table.previousPage()}
                            disabled={!table.getCanPreviousPage()}
                        >
                            <ChevronLeft className="h-4 w-4" />
                        </Button>

                        <span className="text-sm text-gray-600 px-2">
                            Page {table.getState().pagination.pageIndex + 1} of{' '}
                            {table.getPageCount()}
                        </span>

                        <Button
                            variant="outline"
                            size="icon"
                            className="h-8 w-8"
                            onClick={() => table.nextPage()}
                            disabled={!table.getCanNextPage()}
                        >
                            <ChevronRight className="h-4 w-4" />
                        </Button>
                        <Button
                            variant="outline"
                            size="icon"
                            className="h-8 w-8"
                            onClick={() => table.setPageIndex(table.getPageCount() - 1)}
                            disabled={!table.getCanNextPage()}
                        >
                            <ChevronsRight className="h-4 w-4" />
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
}

/**
 * Row action dropdown component
 */
export function RowActions({
    onView,
    onEdit,
    onDelete,
    customActions,
}: {
    onView?: () => void;
    onEdit?: () => void;
    onDelete?: () => void;
    customActions?: { label: string; onClick: () => void; variant?: 'default' | 'destructive' }[];
}) {
    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8" onClick={(e) => e.stopPropagation()}>
                    <MoreHorizontal className="h-4 w-4" />
                    <span className="sr-only">Open menu</span>
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
                {onView && (
                    <DropdownMenuItem onClick={onView}>View details</DropdownMenuItem>
                )}
                {onEdit && (
                    <DropdownMenuItem onClick={onEdit}>Edit</DropdownMenuItem>
                )}
                {customActions?.map((action, i) => (
                    <DropdownMenuItem
                        key={i}
                        onClick={action.onClick}
                        className={action.variant === 'destructive' ? 'text-red-600' : ''}
                    >
                        {action.label}
                    </DropdownMenuItem>
                ))}
                {onDelete && (
                    <>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem onClick={onDelete} className="text-red-600">
                            Delete
                        </DropdownMenuItem>
                    </>
                )}
            </DropdownMenuContent>
        </DropdownMenu>
    );
}

export default DataTable;

