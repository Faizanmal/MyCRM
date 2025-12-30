'use client';

import React, { ReactNode, useCallback, useMemo, useState } from 'react';
import {
    DndContext,
    closestCenter,
    KeyboardSensor,
    PointerSensor,
    useSensor,
    useSensors,
    DragEndEvent,
    DragOverlay,
    DragStartEvent,
} from '@dnd-kit/core';
import {
    arrayMove,
    SortableContext,
    sortableKeyboardCoordinates,
    useSortable,
    verticalListSortingStrategy,
    rectSortingStrategy,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { GripVertical, Plus, Trash2, Settings, Maximize2, Minimize2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

/**
 * Customizable Dashboard Widget System
 */

export interface WidgetConfig {
    id: string;
    type: string;
    title: string;
    size: 'sm' | 'md' | 'lg' | 'xl';
    position: number;
    settings?: Record<string, unknown>;
    component?: ReactNode;
}

interface SortableWidgetProps {
    widget: WidgetConfig;
    children: ReactNode;
    onRemove?: () => void;
    onSettings?: () => void;
    onResize?: (size: WidgetConfig['size']) => void;
    isEditing?: boolean;
}

function SortableWidget({
    widget,
    children,
    onRemove,
    onSettings,
    onResize,
    isEditing = false
}: SortableWidgetProps) {
    const [isExpanded, setIsExpanded] = useState(false);
    const {
        attributes,
        listeners,
        setNodeRef,
        transform,
        transition,
        isDragging,
    } = useSortable({ id: widget.id });

    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
    };

    const sizeClasses = {
        sm: 'col-span-1',
        md: 'col-span-1 md:col-span-2',
        lg: 'col-span-1 md:col-span-2 lg:col-span-3',
        xl: 'col-span-full',
    };

    return (
        <div
            ref={setNodeRef}
            style={style}
            className={cn(
                sizeClasses[isExpanded ? 'xl' : widget.size],
                isDragging && 'opacity-50 z-50',
                'transition-all duration-200'
            )}
        >
            <Card className={cn(
                'h-full',
                isEditing && 'ring-2 ring-blue-200 ring-offset-2'
            )}>
                <CardHeader className="p-3 pb-2 flex flex-row items-center justify-between space-y-0">
                    <div className="flex items-center gap-2">
                        {isEditing && (
                            <button
                                {...attributes}
                                {...listeners}
                                className="cursor-grab active:cursor-grabbing p-1 hover:bg-gray-100 rounded"
                            >
                                <GripVertical className="h-4 w-4 text-gray-400" />
                            </button>
                        )}
                        <CardTitle className="text-sm font-medium">{widget.title}</CardTitle>
                    </div>
                    <div className="flex items-center gap-1">
                        <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6"
                            onClick={() => setIsExpanded(!isExpanded)}
                        >
                            {isExpanded ? (
                                <Minimize2 className="h-3 w-3" />
                            ) : (
                                <Maximize2 className="h-3 w-3" />
                            )}
                        </Button>
                        {isEditing && (
                            <>
                                {onSettings && (
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        className="h-6 w-6"
                                        onClick={onSettings}
                                    >
                                        <Settings className="h-3 w-3" />
                                    </Button>
                                )}
                                {onRemove && (
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        className="h-6 w-6 text-red-500 hover:text-red-700"
                                        onClick={onRemove}
                                    >
                                        <Trash2 className="h-3 w-3" />
                                    </Button>
                                )}
                            </>
                        )}
                    </div>
                </CardHeader>
                <CardContent className="p-3 pt-0">
                    {children}
                </CardContent>
            </Card>
        </div>
    );
}

interface CustomizableDashboardProps {
    widgets: WidgetConfig[];
    onWidgetsChange: (widgets: WidgetConfig[]) => void;
    renderWidget: (widget: WidgetConfig) => ReactNode;
    availableWidgets?: { type: string; title: string; defaultSize: WidgetConfig['size'] }[];
    className?: string;
}

export function CustomizableDashboard({
    widgets,
    onWidgetsChange,
    renderWidget,
    availableWidgets = [],
    className,
}: CustomizableDashboardProps) {
    const [isEditing, setIsEditing] = useState(false);
    const [activeId, setActiveId] = useState<string | null>(null);

    const sensors = useSensors(
        useSensor(PointerSensor, {
            activationConstraint: {
                distance: 8,
            },
        }),
        useSensor(KeyboardSensor, {
            coordinateGetter: sortableKeyboardCoordinates,
        })
    );

    const widgetIds = useMemo(() => widgets.map(w => w.id), [widgets]);

    const handleDragStart = (event: DragStartEvent) => {
        setActiveId(event.active.id as string);
    };

    const handleDragEnd = (event: DragEndEvent) => {
        setActiveId(null);
        const { active, over } = event;

        if (over && active.id !== over.id) {
            const oldIndex = widgets.findIndex(w => w.id === active.id);
            const newIndex = widgets.findIndex(w => w.id === over.id);

            const newWidgets = arrayMove(widgets, oldIndex, newIndex).map((w, i) => ({
                ...w,
                position: i,
            }));

            onWidgetsChange(newWidgets);
        }
    };

    const addWidget = useCallback((type: string) => {
        const config = availableWidgets.find(w => w.type === type);
        if (!config) return;

        const newWidget: WidgetConfig = {
            id: `widget-${Date.now()}`,
            type: config.type,
            title: config.title,
            size: config.defaultSize,
            position: widgets.length,
        };

        onWidgetsChange([...widgets, newWidget]);
    }, [widgets, availableWidgets, onWidgetsChange]);

    const removeWidget = useCallback((id: string) => {
        onWidgetsChange(widgets.filter(w => w.id !== id));
    }, [widgets, onWidgetsChange]);

    const resizeWidget = useCallback((id: string, size: WidgetConfig['size']) => {
        onWidgetsChange(widgets.map(w =>
            w.id === id ? { ...w, size } : w
        ));
    }, [widgets, onWidgetsChange]);

    const activeWidget = activeId ? widgets.find(w => w.id === activeId) : null;

    return (
        <div className={cn('space-y-4', className)}>
            {/* Dashboard Controls */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Button
                        variant={isEditing ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setIsEditing(!isEditing)}
                    >
                        <Settings className="h-4 w-4 mr-2" />
                        {isEditing ? 'Done Editing' : 'Customize'}
                    </Button>
                </div>

                {isEditing && availableWidgets.length > 0 && (
                    <div className="flex items-center gap-2">
                        <span className="text-sm text-gray-500">Add widget:</span>
                        {availableWidgets.map(widget => (
                            <Button
                                key={widget.type}
                                variant="outline"
                                size="sm"
                                onClick={() => addWidget(widget.type)}
                            >
                                <Plus className="h-4 w-4 mr-1" />
                                {widget.title}
                            </Button>
                        ))}
                    </div>
                )}
            </div>

            {/* Widget Grid */}
            <DndContext
                sensors={sensors}
                collisionDetection={closestCenter}
                onDragStart={handleDragStart}
                onDragEnd={handleDragEnd}
            >
                <SortableContext
                    items={widgetIds}
                    strategy={rectSortingStrategy}
                >
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        {widgets.map(widget => (
                            <SortableWidget
                                key={widget.id}
                                widget={widget}
                                isEditing={isEditing}
                                onRemove={() => removeWidget(widget.id)}
                                onResize={(size) => resizeWidget(widget.id, size)}
                            >
                                {renderWidget(widget)}
                            </SortableWidget>
                        ))}
                    </div>
                </SortableContext>

                <DragOverlay>
                    {activeWidget ? (
                        <Card className="shadow-lg opacity-90">
                            <CardHeader className="p-3">
                                <CardTitle className="text-sm">{activeWidget.title}</CardTitle>
                            </CardHeader>
                            <CardContent className="p-3">
                                {renderWidget(activeWidget)}
                            </CardContent>
                        </Card>
                    ) : null}
                </DragOverlay>
            </DndContext>

            {/* Empty State */}
            {widgets.length === 0 && (
                <Card className="p-12">
                    <div className="text-center text-gray-500">
                        <p className="mb-4">No widgets on your dashboard yet.</p>
                        <Button onClick={() => setIsEditing(true)}>
                            <Plus className="h-4 w-4 mr-2" />
                            Add your first widget
                        </Button>
                    </div>
                </Card>
            )}
        </div>
    );
}

// Sample widget components
export function MetricWidget({
    title,
    value,
    change,
    trend
}: {
    title: string;
    value: string | number;
    change?: string;
    trend?: 'up' | 'down' | 'neutral';
}) {
    return (
        <div className="space-y-2">
            <p className="text-sm text-gray-500">{title}</p>
            <p className="text-2xl font-bold">{value}</p>
            {change && (
                <p className={cn(
                    'text-sm',
                    trend === 'up' && 'text-green-600',
                    trend === 'down' && 'text-red-600',
                    trend === 'neutral' && 'text-gray-500'
                )}>
                    {change}
                </p>
            )}
        </div>
    );
}

export function ChartPlaceholder({ height = 150 }: { height?: number }) {
    return (
        <div
            className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg flex items-center justify-center"
            style={{ height }}
        >
            <span className="text-gray-400 text-sm">Chart Content</span>
        </div>
    );
}

export function ListWidget({
    items,
    renderItem
}: {
    items: { id: string;[key: string]: unknown }[];
    renderItem: (item: { id: string;[key: string]: unknown }) => ReactNode;
}) {
    return (
        <div className="space-y-2">
            {items.slice(0, 5).map(item => (
                <div key={item.id}>{renderItem(item)}</div>
            ))}
            {items.length > 5 && (
                <p className="text-xs text-gray-500 text-center">
                    +{items.length - 5} more
                </p>
            )}
        </div>
    );
}

export default CustomizableDashboard;
