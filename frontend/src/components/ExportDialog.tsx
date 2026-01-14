'use client';

import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Download, FileText, FileSpreadsheet, File, FileJson, Loader2, Check, X } from 'lucide-react';

import { Button } from '@/components/ui/button';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import { Progress } from '@/components/ui/progress';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { cn } from '@/lib/utils';
// import { api } from '@/lib/apiClient';

/**
 * Export Dialog Component
 * 
 * Provides a user-friendly interface for exporting data in various formats
 */

export type ExportFormat = 'csv' | 'xlsx' | 'json' | 'pdf';

interface ExportColumn {
    id: string;
    label: string;
    selected: boolean;
}

interface ExportDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    title: string;
    endpoint: string;
    columns?: ExportColumn[];
    filters?: Record<string, unknown>;
    onExportComplete?: () => void;
    onExportError?: (error: Error) => void;
}

export function ExportDialog({
    open,
    onOpenChange,
    title,
    endpoint,
    columns: defaultColumns,
    filters = {},
    onExportComplete,
    onExportError,
}: ExportDialogProps) {
    const [format, setFormat] = useState<ExportFormat>('csv');
    const [selectedColumns, setSelectedColumns] = useState<ExportColumn[]>(
        defaultColumns || []
    );
    const [isExporting, setIsExporting] = useState(false);
    const [progress, setProgress] = useState(0);
    const [exportStatus, setExportStatus] = useState<'idle' | 'exporting' | 'success' | 'error'>('idle');

    const formatIcons: Record<ExportFormat, React.ReactNode> = {
        csv: <FileText className="h-4 w-4" />,
        xlsx: <FileSpreadsheet className="h-4 w-4" />,
        json: <FileJson className="h-4 w-4" />,
        pdf: <File className="h-4 w-4" />,
    };

    const formatLabels: Record<ExportFormat, string> = {
        csv: 'CSV (Comma Separated)',
        xlsx: 'Excel Spreadsheet',
        json: 'JSON',
        pdf: 'PDF Document',
    };

    const handleColumnToggle = useCallback((columnId: string) => {
        setSelectedColumns(cols =>
            cols.map(col =>
                col.id === columnId ? { ...col, selected: !col.selected } : col
            )
        );
    }, []);

    const handleSelectAll = useCallback(() => {
        const allSelected = selectedColumns.every(col => col.selected);
        setSelectedColumns(cols =>
            cols.map(col => ({ ...col, selected: !allSelected }))
        );
    }, [selectedColumns]);

    const handleExport = useCallback(async () => {
        setIsExporting(true);
        setExportStatus('exporting');
        setProgress(0);

        try {
            // Build query params
            const params = new URLSearchParams({
                format,
                ...Object.fromEntries(
                    Object.entries(filters).map(([k, v]) => [k, String(v)])
                ),
            });

            if (selectedColumns.length > 0) {
                const cols = selectedColumns.filter(c => c.selected).map(c => c.id);
                params.set('columns', cols.join(','));
            }

            // Simulate progress for better UX
            const progressInterval = setInterval(() => {
                setProgress(p => Math.min(p + 10, 90));
            }, 200);

            // Make export request
            const response = await fetch(`${endpoint}?${params.toString()}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                },
            });

            clearInterval(progressInterval);

            if (!response.ok) {
                throw new Error(`Export failed: ${response.statusText}`);
            }

            // Get filename from Content-Disposition header
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = `export.${format}`;
            if (contentDisposition) {
                const match = contentDisposition.match(/filename="?([^"]+)"?/);
                if (match) filename = match[1];
            }

            // Download the file
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            setProgress(100);
            setExportStatus('success');
            onExportComplete?.();

            // Close dialog after success
            setTimeout(() => {
                onOpenChange(false);
                setExportStatus('idle');
                setProgress(0);
            }, 1500);

        } catch (error) {
            setExportStatus('error');
            onExportError?.(error as Error);
        } finally {
            setIsExporting(false);
        }
    }, [format, filters, selectedColumns, endpoint, onExportComplete, onExportError, onOpenChange]);

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[500px]">
                <DialogHeader>
                    <DialogTitle>Export {title}</DialogTitle>
                    <DialogDescription>
                        Choose your export format and customize the columns to include.
                    </DialogDescription>
                </DialogHeader>

                <div className="space-y-6 py-4">
                    {/* Format Selection */}
                    <div className="space-y-3">
                        <Label className="text-sm font-medium">Export Format</Label>
                        <RadioGroup
                            value={format}
                            onValueChange={(v) => setFormat(v as ExportFormat)}
                            className="grid grid-cols-2 gap-3"
                        >
                            {(Object.keys(formatLabels) as ExportFormat[]).map((fmt) => (
                                <div key={fmt}>
                                    <RadioGroupItem
                                        value={fmt}
                                        id={fmt}
                                        className="peer sr-only"
                                    />
                                    <Label
                                        htmlFor={fmt}
                                        className={cn(
                                            'flex items-center gap-3 rounded-lg border-2 p-3 cursor-pointer transition-colors',
                                            'hover:bg-gray-50',
                                            'peer-data-[state=checked]:border-blue-500 peer-data-[state=checked]:bg-blue-50'
                                        )}
                                    >
                                        {formatIcons[fmt]}
                                        <span className="text-sm font-medium">{fmt.toUpperCase()}</span>
                                    </Label>
                                </div>
                            ))}
                        </RadioGroup>
                    </div>

                    {/* Column Selection (if columns provided) */}
                    {selectedColumns.length > 0 && (
                        <div className="space-y-3">
                            <div className="flex items-center justify-between">
                                <Label className="text-sm font-medium">Columns to Export</Label>
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={handleSelectAll}
                                >
                                    {selectedColumns.every(c => c.selected) ? 'Deselect All' : 'Select All'}
                                </Button>
                            </div>
                            <div className="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto p-1">
                                {selectedColumns.map((column) => (
                                    <div
                                        key={column.id}
                                        className="flex items-center space-x-2"
                                    >
                                        <Checkbox
                                            id={column.id}
                                            checked={column.selected}
                                            onCheckedChange={() => handleColumnToggle(column.id)}
                                        />
                                        <Label
                                            htmlFor={column.id}
                                            className="text-sm font-normal cursor-pointer"
                                        >
                                            {column.label}
                                        </Label>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Export Progress */}
                    <AnimatePresence>
                        {exportStatus !== 'idle' && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                exit={{ opacity: 0, height: 0 }}
                                className="space-y-2"
                            >
                                <Progress value={progress} className="h-2" />
                                <div className="flex items-center gap-2 text-sm">
                                    {exportStatus === 'exporting' && (
                                        <>
                                            <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
                                            <span className="text-gray-600">Exporting data...</span>
                                        </>
                                    )}
                                    {exportStatus === 'success' && (
                                        <>
                                            <Check className="h-4 w-4 text-green-500" />
                                            <span className="text-green-600">Export complete!</span>
                                        </>
                                    )}
                                    {exportStatus === 'error' && (
                                        <>
                                            <X className="h-4 w-4 text-red-500" />
                                            <span className="text-red-600">Export failed. Please try again.</span>
                                        </>
                                    )}
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>

                <DialogFooter>
                    <Button variant="outline" onClick={() => onOpenChange(false)} disabled={isExporting}>
                        Cancel
                    </Button>
                    <Button onClick={handleExport} disabled={isExporting}>
                        {isExporting ? (
                            <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                Exporting...
                            </>
                        ) : (
                            <>
                                <Download className="mr-2 h-4 w-4" />
                                Export
                            </>
                        )}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}

/**
 * Quick Export Button with dropdown
 */
interface QuickExportButtonProps {
    endpoint: string;
    title?: string;
    filters?: Record<string, unknown>;
    className?: string;
}

export function QuickExportButton({
    endpoint,
    title = 'Data',
    filters = {},
    className,
}: QuickExportButtonProps) {
    const [isExporting, setIsExporting] = useState(false);

    const handleExport = async (format: ExportFormat) => {
        setIsExporting(true);

        try {
            const params = new URLSearchParams({
                format,
                ...Object.fromEntries(
                    Object.entries(filters).map(([k, v]) => [k, String(v)])
                ),
            });

            const response = await fetch(`${endpoint}?${params.toString()}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                },
            });

            if (!response.ok) throw new Error('Export failed');

            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = `export.${format}`;
            if (contentDisposition) {
                const match = contentDisposition.match(/filename="?([^"]+)"?/);
                if (match) filename = match[1];
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

        } catch {
            console.error('Export failed');
        } finally {
            setIsExporting(false);
        }
    };

    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className={className} disabled={isExporting}>
                    {isExporting ? (
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                        <Download className="h-4 w-4 mr-2" />
                    )}
                    Export
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
                <DropdownMenuLabel>Export {title}</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => handleExport('csv')}>
                    <FileText className="h-4 w-4 mr-2" />
                    CSV
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleExport('xlsx')}>
                    <FileSpreadsheet className="h-4 w-4 mr-2" />
                    Excel
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleExport('json')}>
                    <FileJson className="h-4 w-4 mr-2" />
                    JSON
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleExport('pdf')}>
                    <File className="h-4 w-4 mr-2" />
                    PDF
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    );
}

export default ExportDialog;

