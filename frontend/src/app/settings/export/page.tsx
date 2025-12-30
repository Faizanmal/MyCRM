'use client';

import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { toast } from 'sonner';
import {
    Download,
    FileSpreadsheet,
    FileJson,
    FileText,
    Users,
    Building2,
    Target,
    CheckSquare,
    Activity,
    Mail,
    Calendar,
    Loader2,
    Check,
    AlertCircle,
    Clock,
    Package,
} from 'lucide-react';

// Types
type ExportFormat = 'csv' | 'json' | 'xlsx';
type ExportEntity = 'contacts' | 'companies' | 'deals' | 'tasks' | 'activities' | 'emails' | 'calendar';

interface ExportConfig {
    format: ExportFormat;
    entities: ExportEntity[];
    dateRange: 'all' | 'year' | 'quarter' | 'month' | 'custom';
    includeArchived: boolean;
    includeDeleted: boolean;
}

interface ExportJob {
    id: string;
    status: 'pending' | 'processing' | 'completed' | 'failed';
    progress: number;
    format: ExportFormat;
    entities: ExportEntity[];
    createdAt: Date;
    completedAt?: Date;
    downloadUrl?: string;
    fileSize?: string;
    error?: string;
}

// Entity options
const entityOptions: { id: ExportEntity; label: string; icon: React.ElementType; count?: number }[] = [
    { id: 'contacts', label: 'Contacts', icon: Users, count: 1234 },
    { id: 'companies', label: 'Companies', icon: Building2, count: 456 },
    { id: 'deals', label: 'Deals', icon: Target, count: 789 },
    { id: 'tasks', label: 'Tasks', icon: CheckSquare, count: 2345 },
    { id: 'activities', label: 'Activities', icon: Activity, count: 5678 },
    { id: 'emails', label: 'Emails', icon: Mail, count: 8901 },
    { id: 'calendar', label: 'Calendar Events', icon: Calendar, count: 123 },
];

const formatOptions: { id: ExportFormat; label: string; icon: React.ElementType; description: string }[] = [
    { id: 'csv', label: 'CSV', icon: FileSpreadsheet, description: 'Compatible with Excel, Google Sheets' },
    { id: 'json', label: 'JSON', icon: FileJson, description: 'For developers and API integrations' },
    { id: 'xlsx', label: 'Excel', icon: FileSpreadsheet, description: 'Native Excel format with formatting' },
];

export default function DataExportPage() {
    const [config, setConfig] = useState<ExportConfig>({
        format: 'csv',
        entities: [],
        dateRange: 'all',
        includeArchived: false,
        includeDeleted: false,
    });

    const [isExporting, setIsExporting] = useState(false);
    const [exportProgress, setExportProgress] = useState(0);
    const [exportJobs, setExportJobs] = useState<ExportJob[]>([
        // Mock previous exports
        {
            id: '1',
            status: 'completed',
            progress: 100,
            format: 'csv',
            entities: ['contacts', 'companies'],
            createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
            completedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000 + 45000),
            downloadUrl: '#',
            fileSize: '2.4 MB',
        },
        {
            id: '2',
            status: 'completed',
            progress: 100,
            format: 'json',
            entities: ['deals', 'activities'],
            createdAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
            completedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000 + 120000),
            downloadUrl: '#',
            fileSize: '5.1 MB',
        },
    ]);

    // Toggle entity selection
    const toggleEntity = (entityId: ExportEntity) => {
        setConfig(prev => ({
            ...prev,
            entities: prev.entities.includes(entityId)
                ? prev.entities.filter(e => e !== entityId)
                : [...prev.entities, entityId],
        }));
    };

    // Select all entities
    const selectAllEntities = () => {
        setConfig(prev => ({
            ...prev,
            entities: entityOptions.map(e => e.id),
        }));
    };

    // Clear all entities
    const clearAllEntities = () => {
        setConfig(prev => ({
            ...prev,
            entities: [],
        }));
    };

    // Start export
    const startExport = useCallback(async () => {
        if (config.entities.length === 0) {
            toast.error('Please select at least one data type to export');
            return;
        }

        setIsExporting(true);
        setExportProgress(0);

        const newJob: ExportJob = {
            id: Date.now().toString(),
            status: 'processing',
            progress: 0,
            format: config.format,
            entities: [...config.entities],
            createdAt: new Date(),
        };

        setExportJobs(prev => [newJob, ...prev]);

        // Simulate export progress
        const totalSteps = config.entities.length * 10;
        for (let i = 0; i <= totalSteps; i++) {
            await new Promise(resolve => setTimeout(resolve, 100));
            const progress = Math.round((i / totalSteps) * 100);
            setExportProgress(progress);

            setExportJobs(prev => prev.map(job =>
                job.id === newJob.id
                    ? { ...job, progress }
                    : job
            ));
        }

        // Complete the export
        setExportJobs(prev => prev.map(job =>
            job.id === newJob.id
                ? {
                    ...job,
                    status: 'completed',
                    progress: 100,
                    completedAt: new Date(),
                    downloadUrl: '#',
                    fileSize: `${(Math.random() * 10 + 1).toFixed(1)} MB`,
                }
                : job
        ));

        setIsExporting(false);
        setExportProgress(0);
        toast.success('Export completed successfully!');
    }, [config]);

    // Download export
    const downloadExport = (job: ExportJob) => {
        // In a real app, this would download the file
        toast.success(`Downloading ${job.format.toUpperCase()} export...`);
    };

    // Delete export
    const deleteExport = (jobId: string) => {
        setExportJobs(prev => prev.filter(job => job.id !== jobId));
        toast.success('Export deleted');
    };

    // Format date
    const formatDate = (date: Date): string => {
        return new Intl.DateTimeFormat('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        }).format(date);
    };

    return (
        <div className="container mx-auto py-8 px-4 max-w-4xl">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold flex items-center gap-3">
                    <Download className="w-8 h-8 text-blue-500" />
                    Data Export
                </h1>
                <p className="text-gray-500 mt-1">
                    Export your CRM data in various formats for backup or analysis
                </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Export Configuration */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Select Data */}
                    <Card>
                        <CardHeader>
                            <div className="flex items-center justify-between">
                                <div>
                                    <CardTitle>Select Data to Export</CardTitle>
                                    <CardDescription>Choose which data types to include</CardDescription>
                                </div>
                                <div className="flex gap-2">
                                    <Button variant="ghost" size="sm" onClick={selectAllEntities}>
                                        Select All
                                    </Button>
                                    <Button variant="ghost" size="sm" onClick={clearAllEntities}>
                                        Clear
                                    </Button>
                                </div>
                            </div>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-2 gap-3">
                                {entityOptions.map((entity) => (
                                    <Label
                                        key={entity.id}
                                        htmlFor={entity.id}
                                        className={`flex items-center gap-3 p-4 rounded-lg border-2 cursor-pointer transition-colors ${config.entities.includes(entity.id)
                                                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                                                : 'border-gray-200 hover:border-gray-300'
                                            }`}
                                    >
                                        <Checkbox
                                            id={entity.id}
                                            checked={config.entities.includes(entity.id)}
                                            onCheckedChange={() => toggleEntity(entity.id)}
                                        />
                                        <entity.icon className="w-5 h-5 text-gray-500" />
                                        <div className="flex-1">
                                            <span className="font-medium">{entity.label}</span>
                                            {entity.count && (
                                                <Badge variant="secondary" className="ml-2">
                                                    {entity.count.toLocaleString()}
                                                </Badge>
                                            )}
                                        </div>
                                    </Label>
                                ))}
                            </div>
                        </CardContent>
                    </Card>

                    {/* Export Format */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Export Format</CardTitle>
                            <CardDescription>Choose your preferred file format</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <RadioGroup
                                value={config.format}
                                onValueChange={(value) => setConfig(prev => ({ ...prev, format: value as ExportFormat }))}
                                className="grid grid-cols-3 gap-4"
                            >
                                {formatOptions.map((format) => (
                                    <Label
                                        key={format.id}
                                        htmlFor={format.id}
                                        className={`flex flex-col items-center gap-2 p-4 rounded-lg border-2 cursor-pointer transition-colors ${config.format === format.id
                                                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                                                : 'border-gray-200 hover:border-gray-300'
                                            }`}
                                    >
                                        <RadioGroupItem value={format.id} id={format.id} className="sr-only" />
                                        <format.icon className="w-8 h-8 text-gray-500" />
                                        <span className="font-medium">{format.label}</span>
                                        <span className="text-xs text-gray-500 text-center">{format.description}</span>
                                    </Label>
                                ))}
                            </RadioGroup>
                        </CardContent>
                    </Card>

                    {/* Options */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Options</CardTitle>
                            <CardDescription>Configure export options</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {/* Date Range */}
                            <div className="space-y-2">
                                <Label>Date Range</Label>
                                <RadioGroup
                                    value={config.dateRange}
                                    onValueChange={(value) => setConfig(prev => ({ ...prev, dateRange: value as ExportConfig['dateRange'] }))}
                                    className="flex flex-wrap gap-2"
                                >
                                    {[
                                        { id: 'all', label: 'All Time' },
                                        { id: 'year', label: 'Last Year' },
                                        { id: 'quarter', label: 'Last Quarter' },
                                        { id: 'month', label: 'Last Month' },
                                    ].map((option) => (
                                        <Label
                                            key={option.id}
                                            htmlFor={`range-${option.id}`}
                                            className={`px-4 py-2 rounded-full border cursor-pointer transition-colors ${config.dateRange === option.id
                                                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                                                    : 'border-gray-200 hover:border-gray-300'
                                                }`}
                                        >
                                            <RadioGroupItem value={option.id} id={`range-${option.id}`} className="sr-only" />
                                            {option.label}
                                        </Label>
                                    ))}
                                </RadioGroup>
                            </div>

                            <Separator />

                            {/* Include options */}
                            <div className="space-y-3">
                                <div className="flex items-center gap-3">
                                    <Checkbox
                                        id="archived"
                                        checked={config.includeArchived}
                                        onCheckedChange={(checked) =>
                                            setConfig(prev => ({ ...prev, includeArchived: !!checked }))
                                        }
                                    />
                                    <Label htmlFor="archived">Include archived items</Label>
                                </div>

                                <div className="flex items-center gap-3">
                                    <Checkbox
                                        id="deleted"
                                        checked={config.includeDeleted}
                                        onCheckedChange={(checked) =>
                                            setConfig(prev => ({ ...prev, includeDeleted: !!checked }))
                                        }
                                    />
                                    <Label htmlFor="deleted">Include deleted items (30-day retention)</Label>
                                </div>
                            </div>
                        </CardContent>
                        <CardFooter>
                            <Button
                                onClick={startExport}
                                disabled={isExporting || config.entities.length === 0}
                                className="w-full gap-2"
                                size="lg"
                            >
                                {isExporting ? (
                                    <>
                                        <Loader2 className="w-5 h-5 animate-spin" />
                                        Exporting... {exportProgress}%
                                    </>
                                ) : (
                                    <>
                                        <Download className="w-5 h-5" />
                                        Start Export
                                    </>
                                )}
                            </Button>
                        </CardFooter>
                    </Card>
                </div>

                {/* Export History */}
                <div>
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Clock className="w-5 h-5" />
                                Recent Exports
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <AnimatePresence mode="popLayout">
                                {exportJobs.length === 0 ? (
                                    <div className="text-center py-8 text-gray-500">
                                        <Package className="w-12 h-12 mx-auto mb-3 opacity-30" />
                                        <p>No exports yet</p>
                                    </div>
                                ) : (
                                    exportJobs.map((job) => (
                                        <motion.div
                                            key={job.id}
                                            initial={{ opacity: 0, y: -10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            exit={{ opacity: 0, x: -10 }}
                                            className="p-3 border rounded-lg"
                                        >
                                            <div className="flex items-center justify-between mb-2">
                                                <div className="flex items-center gap-2">
                                                    {job.status === 'completed' && (
                                                        <Check className="w-4 h-4 text-green-500" />
                                                    )}
                                                    {job.status === 'processing' && (
                                                        <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
                                                    )}
                                                    {job.status === 'failed' && (
                                                        <AlertCircle className="w-4 h-4 text-red-500" />
                                                    )}
                                                    <Badge variant="outline" className="uppercase text-xs">
                                                        {job.format}
                                                    </Badge>
                                                </div>
                                                {job.fileSize && (
                                                    <span className="text-xs text-gray-500">{job.fileSize}</span>
                                                )}
                                            </div>

                                            <div className="text-xs text-gray-500 mb-2">
                                                {job.entities.join(', ')}
                                            </div>

                                            {job.status === 'processing' && (
                                                <Progress value={job.progress} className="h-1 mb-2" />
                                            )}

                                            <div className="flex items-center justify-between text-xs">
                                                <span className="text-gray-400">
                                                    {formatDate(job.createdAt)}
                                                </span>
                                                {job.status === 'completed' && job.downloadUrl && (
                                                    <Button
                                                        variant="ghost"
                                                        size="sm"
                                                        onClick={() => downloadExport(job)}
                                                        className="h-6 text-xs"
                                                    >
                                                        <Download className="w-3 h-3 mr-1" />
                                                        Download
                                                    </Button>
                                                )}
                                            </div>
                                        </motion.div>
                                    ))
                                )}
                            </AnimatePresence>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
