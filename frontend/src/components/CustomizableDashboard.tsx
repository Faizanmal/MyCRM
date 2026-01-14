'use client';

import { useState } from 'react';
import { motion, AnimatePresence, Reorder, useDragControls } from 'framer-motion';
import {
    GripVertical,
    Settings,
    TrendingUp,
    Users,
    Target,
    Calendar,
    DollarSign,
    Clock,
    CheckCircle2,
    AlertCircle,
    Trophy,
    Zap,
    Eye,
    EyeOff,
    RotateCcw,
    Save,
} from 'lucide-react';
import { toast } from 'sonner';

import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface Widget {
    id: string;
    title: string;
    icon: React.ElementType;
    type: 'stat' | 'chart' | 'list' | 'progress';
    size: 'small' | 'medium' | 'large';
    visible: boolean;
    color: string;
}

interface WidgetData {
    value?: string | number;
    change?: number;
    items?: Array<{ label: string; value: string | number; color?: string }>;
    progress?: number;
}

const defaultWidgets: Widget[] = [
    { id: 'total-contacts', title: 'Total Contacts', icon: Users, type: 'stat', size: 'small', visible: true, color: 'blue' },
    { id: 'active-leads', title: 'Active Leads', icon: Target, type: 'stat', size: 'small', visible: true, color: 'green' },
    { id: 'opportunities', title: 'Open Deals', icon: TrendingUp, type: 'stat', size: 'small', visible: true, color: 'purple' },
    { id: 'revenue', title: 'Pipeline Value', icon: DollarSign, type: 'stat', size: 'small', visible: true, color: 'amber' },
    { id: 'tasks-today', title: 'Tasks Today', icon: Calendar, type: 'stat', size: 'small', visible: true, color: 'red' },
    { id: 'completed-tasks', title: 'Completed', icon: CheckCircle2, type: 'stat', size: 'small', visible: true, color: 'emerald' },
    { id: 'overdue-tasks', title: 'Overdue', icon: AlertCircle, type: 'stat', size: 'small', visible: false, color: 'rose' },
    { id: 'response-time', title: 'Avg Response', icon: Clock, type: 'stat', size: 'small', visible: false, color: 'indigo' },
    { id: 'win-rate', title: 'Win Rate', icon: Trophy, type: 'stat', size: 'small', visible: true, color: 'yellow' },
    { id: 'conversion', title: 'Conversion', icon: Zap, type: 'stat', size: 'small', visible: true, color: 'pink' },
];

// Mock data - replace with actual API calls
const widgetData: Record<string, WidgetData> = {
    'total-contacts': { value: '1,234', change: 12 },
    'active-leads': { value: '456', change: 8 },
    'opportunities': { value: '89', change: 23 },
    'revenue': { value: '$1.2M', change: 15 },
    'tasks-today': { value: '12', change: -5 },
    'completed-tasks': { value: '38', change: 10 },
    'overdue-tasks': { value: '5', change: -20 },
    'response-time': { value: '2.4h', change: -15 },
    'win-rate': { value: '32%', change: 5 },
    'conversion': { value: '18%', change: 3 },
};

const WIDGETS_STORAGE_KEY = 'mycrm_dashboard_widgets';

interface DashboardWidgetProps {
    widget: Widget;
    data: WidgetData;
    isEditing: boolean;
    onToggleVisibility: () => void;
}

function DashboardWidget({ widget, data, isEditing, onToggleVisibility }: DashboardWidgetProps) {
    const dragControls = useDragControls();
    const Icon = widget.icon;

    const colorClasses: Record<string, { bg: string; text: string; icon: string }> = {
        blue: { bg: 'bg-blue-50 dark:bg-blue-900/20', text: 'text-blue-600', icon: 'text-blue-500' },
        green: { bg: 'bg-green-50 dark:bg-green-900/20', text: 'text-green-600', icon: 'text-green-500' },
        purple: { bg: 'bg-purple-50 dark:bg-purple-900/20', text: 'text-purple-600', icon: 'text-purple-500' },
        amber: { bg: 'bg-amber-50 dark:bg-amber-900/20', text: 'text-amber-600', icon: 'text-amber-500' },
        red: { bg: 'bg-red-50 dark:bg-red-900/20', text: 'text-red-600', icon: 'text-red-500' },
        emerald: { bg: 'bg-emerald-50 dark:bg-emerald-900/20', text: 'text-emerald-600', icon: 'text-emerald-500' },
        rose: { bg: 'bg-rose-50 dark:bg-rose-900/20', text: 'text-rose-600', icon: 'text-rose-500' },
        indigo: { bg: 'bg-indigo-50 dark:bg-indigo-900/20', text: 'text-indigo-600', icon: 'text-indigo-500' },
        yellow: { bg: 'bg-yellow-50 dark:bg-yellow-900/20', text: 'text-yellow-600', icon: 'text-yellow-500' },
        pink: { bg: 'bg-pink-50 dark:bg-pink-900/20', text: 'text-pink-600', icon: 'text-pink-500' },
    };

    const colors = colorClasses[widget.color] || colorClasses.blue;

    return (
        <motion.div
            layout
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: widget.visible ? 1 : 0.5, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            whileHover={{ scale: isEditing ? 1.02 : 1 }}
            className={`relative ${!widget.visible && !isEditing ? 'hidden' : ''}`}
        >
            <Card className={`overflow-hidden transition-shadow ${isEditing ? 'ring-2 ring-blue-200 dark:ring-blue-800' : ''}`}>
                {isEditing && (
                    <div
                        onPointerDown={(e) => dragControls.start(e)}
                        className="absolute top-2 left-2 p-1 cursor-grab active:cursor-grabbing text-gray-400 hover:text-gray-600"
                    >
                        <GripVertical className="w-4 h-4" />
                    </div>
                )}

                {isEditing && (
                    <Button
                        variant="ghost"
                        size="icon"
                        className="absolute top-1 right-1 h-7 w-7"
                        onClick={onToggleVisibility}
                    >
                        {widget.visible ? (
                            <Eye className="w-4 h-4 text-green-500" />
                        ) : (
                            <EyeOff className="w-4 h-4 text-gray-400" />
                        )}
                    </Button>
                )}

                <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-500 dark:text-gray-400">{widget.title}</p>
                            <p className={`text-2xl font-bold ${colors.text}`}>{data.value}</p>
                        </div>
                        <div className={`p-3 rounded-xl ${colors.bg}`}>
                            <Icon className={`w-6 h-6 ${colors.icon}`} />
                        </div>
                    </div>
                    {data.change !== undefined && (
                        <div className="mt-2 flex items-center gap-1">
                            <span className={`text-xs font-medium ${data.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {data.change >= 0 ? '+' : ''}{data.change}%
                            </span>
                            <span className="text-xs text-gray-400">vs last month</span>
                        </div>
                    )}
                </CardContent>
            </Card>
        </motion.div>
    );
}

export default function CustomizableDashboard() {
    const [widgets, setWidgets] = useState<Widget[]>(() => {
        const saved = localStorage.getItem(WIDGETS_STORAGE_KEY);
        if (saved) {
            try {
                const savedWidgets = JSON.parse(saved);
                // Merge with default widgets to handle new widgets
                return defaultWidgets.map(defaultWidget => {
                    const savedWidget = savedWidgets.find((w: Widget) => w.id === defaultWidget.id);
                    return savedWidget ? { ...defaultWidget, ...savedWidget } : defaultWidget;
                });
            } catch {
                // Use defaults if parse fails
                return defaultWidgets;
            }
        }
        return defaultWidgets;
    });
    const [isEditing, setIsEditing] = useState(false);
    const [isDirty, setIsDirty] = useState(false);

    const toggleWidgetVisibility = (widgetId: string) => {
        setWidgets(prev => prev.map(w =>
            w.id === widgetId ? { ...w, visible: !w.visible } : w
        ));
        setIsDirty(true);
    };

    const reorderWidgets = (newOrder: Widget[]) => {
        setWidgets(newOrder);
        setIsDirty(true);
    };

    const saveConfiguration = () => {
        localStorage.setItem(WIDGETS_STORAGE_KEY, JSON.stringify(widgets));
        setIsDirty(false);
        setIsEditing(false);
        toast.success('Dashboard layout saved!');
    };

    const resetToDefaults = () => {
        setWidgets(defaultWidgets);
        localStorage.removeItem(WIDGETS_STORAGE_KEY);
        setIsDirty(false);
        toast.info('Dashboard reset to defaults');
    };

    const visibleWidgets = widgets.filter(w => w.visible || isEditing);

    return (
        <div className="space-y-4">
            {/* Controls */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-lg font-semibold">Dashboard Overview</h2>
                    <p className="text-sm text-gray-500">Your key metrics at a glance</p>
                </div>
                <div className="flex items-center gap-2">
                    {isEditing ? (
                        <>
                            <Button variant="outline" size="sm" onClick={resetToDefaults}>
                                <RotateCcw className="w-4 h-4 mr-2" />
                                Reset
                            </Button>
                            <Button variant="outline" size="sm" onClick={() => { setIsEditing(false); setIsDirty(false); }}>
                                Cancel
                            </Button>
                            <Button size="sm" onClick={saveConfiguration} disabled={!isDirty}>
                                <Save className="w-4 h-4 mr-2" />
                                Save Layout
                            </Button>
                        </>
                    ) : (
                        <Button variant="outline" size="sm" onClick={() => setIsEditing(true)}>
                            <Settings className="w-4 h-4 mr-2" />
                            Customize
                        </Button>
                    )}
                </div>
            </div>

            {/* Editing hint */}
            <AnimatePresence>
                {isEditing && (
                    <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800 text-sm text-blue-700 dark:text-blue-300 flex items-center gap-2"
                    >
                        <Settings className="w-4 h-4" />
                        Drag widgets to reorder. Click the eye icon to show/hide widgets.
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Widget Grid */}
            {isEditing ? (
                <Reorder.Group
                    axis="x"
                    values={widgets}
                    onReorder={reorderWidgets}
                    className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4"
                >
                    {widgets.map(widget => (
                        <Reorder.Item key={widget.id} value={widget}>
                            <DashboardWidget
                                widget={widget}
                                data={widgetData[widget.id] || {}}
                                isEditing={isEditing}
                                onToggleVisibility={() => toggleWidgetVisibility(widget.id)}
                            />
                        </Reorder.Item>
                    ))}
                </Reorder.Group>
            ) : (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                    {visibleWidgets.map(widget => (
                        <DashboardWidget
                            key={widget.id}
                            widget={widget}
                            data={widgetData[widget.id] || {}}
                            isEditing={isEditing}
                            onToggleVisibility={() => toggleWidgetVisibility(widget.id)}
                        />
                    ))}
                </div>
            )}

            {/* Hidden widgets hint */}
            {!isEditing && widgets.filter(w => !w.visible).length > 0 && (
                <p className="text-xs text-gray-400 text-center">
                    {widgets.filter(w => !w.visible).length} hidden widgets • Click &quot;Customize&quot; to show them
                </p>
            )}
        </div>
    );
}

