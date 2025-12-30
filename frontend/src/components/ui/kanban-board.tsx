/**
 * MyCRM Kanban Board Component
 *
 * A drag-and-drop Kanban board for managing opportunities across pipeline stages.
 * Uses @dnd-kit for accessible drag-and-drop functionality.
 */

'use client';

import * as React from 'react';
import {
  DndContext,
  DragEndEvent,
  DragOverEvent,
  DragOverlay,
  DragStartEvent,
  KeyboardSensor,
  PointerSensor,
  closestCorners,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import Image from 'next/image';
import {
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import {
  Building2,
  Calendar,
  DollarSign,
  GripVertical,
  MoreHorizontal,
  Plus,
  User,
} from 'lucide-react';

import { cn, formatCurrency, formatDate } from '@/lib/utils';
import type { Opportunity, PipelineStage } from '@/types';

// ============================================================================
// Types
// ============================================================================

interface KanbanBoardProps {
  stages: PipelineStage[];
  opportunities: Opportunity[];
  onMoveOpportunity: (
    opportunityId: string,
    sourceStageId: string,
    targetStageId: string
  ) => void;
  onOpportunityClick?: (opportunity: Opportunity) => void;
  onAddOpportunity?: (stageId: string) => void;
  isLoading?: boolean;
  className?: string;
}

interface KanbanColumnProps {
  stage: PipelineStage;
  opportunities: Opportunity[];
  onOpportunityClick?: (opportunity: Opportunity) => void;
  onAddOpportunity?: () => void;
}

interface KanbanCardProps {
  opportunity: Opportunity;
  onClick?: () => void;
  isDragging?: boolean;
}

// ============================================================================
// Kanban Card Component
// ============================================================================

function KanbanCard({ opportunity, onClick, isDragging }: KanbanCardProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging: isSortableDragging,
  } = useSortable({
    id: opportunity.id,
    data: {
      type: 'opportunity',
      opportunity,
    },
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  const isCurrentlyDragging = isDragging || isSortableDragging;

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={cn(
        'group cursor-pointer rounded-lg border border-gray-200 bg-white p-4 shadow-sm transition-all hover:shadow-md dark:border-gray-700 dark:bg-gray-800',
        isCurrentlyDragging && 'opacity-50 shadow-lg ring-2 ring-blue-500'
      )}
      onClick={onClick}
    >
      {/* Drag Handle & Actions */}
      <div className="mb-3 flex items-center justify-between">
        <button
          className="cursor-grab touch-none rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600 active:cursor-grabbing dark:hover:bg-gray-700"
          {...attributes}
          {...listeners}
        >
          <GripVertical className="h-4 w-4" />
        </button>
        <button
          className="rounded p-1 text-gray-400 opacity-0 hover:bg-gray-100 hover:text-gray-600 group-hover:opacity-100 dark:hover:bg-gray-700"
          onClick={(e) => {
            e.stopPropagation();
            // Open actions menu
          }}
        >
          <MoreHorizontal className="h-4 w-4" />
        </button>
      </div>

      {/* Opportunity Name */}
      <h4 className="mb-2 font-medium text-gray-900 dark:text-gray-100">
        {opportunity.name}
      </h4>

      {/* Company */}
      {opportunity.company && (
        <div className="mb-2 flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
          <Building2 className="h-4 w-4" />
          <span className="truncate">{opportunity.company.name}</span>
        </div>
      )}

      {/* Contact */}
      {opportunity.contact && (
        <div className="mb-2 flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
          <User className="h-4 w-4" />
          <span className="truncate">{opportunity.contact.full_name}</span>
        </div>
      )}

      {/* Value */}
      <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-green-600 dark:text-green-400">
        <DollarSign className="h-4 w-4" />
        <span>{formatCurrency(opportunity.value, opportunity.currency)}</span>
      </div>

      {/* Close Date */}
      {opportunity.expected_close_date && (
        <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
          <Calendar className="h-4 w-4" />
          <span>{formatDate(opportunity.expected_close_date)}</span>
        </div>
      )}

      {/* Probability Badge */}
      <div className="mt-3 flex items-center justify-between">
        <span
          className={cn(
            'inline-flex items-center rounded-full px-2 py-1 text-xs font-medium',
            opportunity.probability >= 0.7
              ? 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400'
              : opportunity.probability >= 0.4
                ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-400'
                : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
          )}
        >
          {Math.round(opportunity.probability * 100)}% likely
        </span>

        {/* Owner Avatar */}
        {opportunity.owner && (
          <div
            className="h-6 w-6 overflow-hidden rounded-full bg-blue-500"
            title={opportunity.owner.full_name}
          >
            {opportunity.owner.avatar_url ? (
              <Image
                src={opportunity.owner.avatar_url}
                alt={opportunity.owner.full_name}
                width={24}
                height={24}
                className="h-full w-full object-cover"
              />
            ) : (
              <span className="flex h-full w-full items-center justify-center text-xs font-medium text-white">
                {opportunity.owner.first_name?.[0]}
                {opportunity.owner.last_name?.[0]}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ============================================================================
// Kanban Column Component
// ============================================================================

function KanbanColumn({
  stage,
  opportunities,
  onOpportunityClick,
  onAddOpportunity,
}: KanbanColumnProps) {
  const totalValue = opportunities.reduce((sum, opp) => sum + opp.value, 0);

  return (
    <div className="flex h-full w-80 flex-shrink-0 flex-col rounded-lg bg-gray-50 dark:bg-gray-900">
      {/* Column Header */}
      <div
        className="sticky top-0 z-10 rounded-t-lg border-b border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-900"
        style={{ borderTopColor: stage.color, borderTopWidth: '3px' }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-gray-900 dark:text-gray-100">
              {stage.name}
            </h3>
            <span className="inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-gray-200 px-1.5 text-xs font-medium text-gray-700 dark:bg-gray-700 dark:text-gray-300">
              {opportunities.length}
            </span>
          </div>
          {onAddOpportunity && (
            <button
              onClick={onAddOpportunity}
              className="rounded p-1 text-gray-400 hover:bg-gray-200 hover:text-gray-600 dark:hover:bg-gray-700"
            >
              <Plus className="h-4 w-4" />
            </button>
          )}
        </div>
        <div className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          {formatCurrency(totalValue)} • {stage.probability}% probability
        </div>
      </div>

      {/* Column Content */}
      <div className="flex-1 overflow-y-auto p-2">
        <SortableContext
          items={opportunities.map((o) => o.id)}
          strategy={verticalListSortingStrategy}
        >
          <div className="space-y-3">
            {opportunities.map((opportunity) => (
              <KanbanCard
                key={opportunity.id}
                opportunity={opportunity}
                onClick={() => onOpportunityClick?.(opportunity)}
              />
            ))}
          </div>
        </SortableContext>

        {opportunities.length === 0 && (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <p className="text-sm text-gray-400">No opportunities</p>
            {onAddOpportunity && (
              <button
                onClick={onAddOpportunity}
                className="mt-2 text-sm text-blue-500 hover:text-blue-600"
              >
                + Add opportunity
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ============================================================================
// Kanban Board Component
// ============================================================================

export function KanbanBoard({
  stages,
  opportunities,
  onMoveOpportunity,
  onOpportunityClick,
  onAddOpportunity,
  isLoading = false,
  className,
}: KanbanBoardProps) {
  const [activeOpportunity, setActiveOpportunity] = React.useState<Opportunity | null>(null);
  const [localOpportunities, setLocalOpportunities] = React.useState(opportunities);

  // Update local state when props change
  React.useEffect(() => {
    setLocalOpportunities(opportunities);
  }, [opportunities]);

  // Group opportunities by stage
  const opportunitiesByStage = React.useMemo(() => {
    const grouped: Record<string, Opportunity[]> = {};
    stages.forEach((stage) => {
      grouped[stage.id] = localOpportunities.filter(
        (opp) => opp.stage_id === stage.id
      );
    });
    return grouped;
  }, [stages, localOpportunities]);

  // DnD Sensors
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

  // Handle drag start
  const handleDragStart = (event: DragStartEvent) => {
    const { active } = event;
    const opportunity = localOpportunities.find((o) => o.id === active.id);
    if (opportunity) {
      setActiveOpportunity(opportunity);
    }
  };

  // Handle drag over (for moving between columns)
  const handleDragOver = (event: DragOverEvent) => {
    const { active, over } = event;
    if (!over) return;

    const activeId = active.id as string;
    const overId = over.id as string;

    // Find the active opportunity
    const activeOpportunity = localOpportunities.find((o) => o.id === activeId);
    if (!activeOpportunity) return;

    // Find target stage (could be dropping on another card or on a stage)
    let targetStageId: string | null = null;

    // Check if dropping on a stage
    const targetStage = stages.find((s) => s.id === overId);
    if (targetStage) {
      targetStageId = targetStage.id;
    } else {
      // Check if dropping on another opportunity
      const overOpportunity = localOpportunities.find((o) => o.id === overId);
      if (overOpportunity) {
        targetStageId = overOpportunity.stage_id;
      }
    }

    // Update local state for immediate feedback
    if (targetStageId && activeOpportunity.stage_id !== targetStageId) {
      setLocalOpportunities((prev) =>
        prev.map((opp) =>
          opp.id === activeId ? { ...opp, stage_id: targetStageId! } : opp
        )
      );
    }
  };

  // Handle drag end
  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveOpportunity(null);

    if (!over) {
      // Reset to original state if dropped outside
      setLocalOpportunities(opportunities);
      return;
    }

    const activeId = active.id as string;
    const activeOpportunity = localOpportunities.find((o) => o.id === activeId);
    const originalOpportunity = opportunities.find((o) => o.id === activeId);

    if (!activeOpportunity || !originalOpportunity) return;

    // Only trigger callback if stage actually changed
    if (activeOpportunity.stage_id !== originalOpportunity.stage_id) {
      onMoveOpportunity(
        activeId,
        originalOpportunity.stage_id,
        activeOpportunity.stage_id
      );
    }
  };

  if (isLoading) {
    return (
      <div className={cn('flex gap-4 overflow-x-auto p-4', className)}>
        {stages.map((stage) => (
          <div
            key={stage.id}
            className="h-[600px] w-80 flex-shrink-0 animate-pulse rounded-lg bg-gray-100 dark:bg-gray-800"
          />
        ))}
      </div>
    );
  }

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCorners}
      onDragStart={handleDragStart}
      onDragOver={handleDragOver}
      onDragEnd={handleDragEnd}
    >
      <div className={cn('flex gap-4 overflow-x-auto p-4', className)}>
        {stages.map((stage) => (
          <KanbanColumn
            key={stage.id}
            stage={stage}
            opportunities={opportunitiesByStage[stage.id] || []}
            onOpportunityClick={onOpportunityClick}
            onAddOpportunity={
              onAddOpportunity ? () => onAddOpportunity(stage.id) : undefined
            }
          />
        ))}
      </div>

      {/* Drag Overlay */}
      <DragOverlay dropAnimation={null}>
        {activeOpportunity && (
          <KanbanCard opportunity={activeOpportunity} isDragging />
        )}
      </DragOverlay>
    </DndContext>
  );
}

export default KanbanBoard;
