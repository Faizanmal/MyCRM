'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    CheckCircle2,
    Circle,
    ChevronDown,
    ChevronUp,
    Rocket,
    Users,
    Building2,
    Target,
    Calendar,
    Sparkles,
    Trophy,
    Settings,
    X,
    ArrowRight,
    Gift,
    Zap,
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { onboardingAPI } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';

interface ChecklistItem {
    id: string;
    title: string;
    description: string;
    icon: React.ElementType;
    href: string;
    points: number;
    completed: boolean;
}

const CHECKLIST_STORAGE_KEY = 'mycrm_onboarding_checklist';
const CHECKLIST_DISMISSED_KEY = 'mycrm_onboarding_dismissed';

const defaultChecklist: Omit<ChecklistItem, 'completed'>[] = [
    {
        id: 'profile',
        title: 'Complete your profile',
        description: 'Add your name, photo, and contact details',
        icon: Settings,
        href: '/settings',
        points: 50,
    },
    {
        id: 'first_contact',
        title: 'Add your first contact',
        description: 'Import or create a contact to get started',
        icon: Users,
        href: '/contacts',
        points: 100,
    },
    {
        id: 'first_company',
        title: 'Create a company',
        description: 'Add an organization to your CRM',
        icon: Building2,
        href: '/organizations',
        points: 75,
    },
    {
        id: 'first_lead',
        title: 'Add a lead',
        description: 'Track a potential customer',
        icon: Target,
        href: '/leads',
        points: 100,
    },
    {
        id: 'first_opportunity',
        title: 'Create a deal',
        description: 'Start tracking a sales opportunity',
        icon: Target,
        href: '/opportunities',
        points: 150,
    },
    {
        id: 'first_task',
        title: 'Schedule a task',
        description: 'Never miss a follow-up',
        icon: Calendar,
        href: '/tasks',
        points: 50,
    },
    {
        id: 'explore_ai',
        title: 'Explore AI Insights',
        description: 'Discover AI-powered recommendations',
        icon: Sparkles,
        href: '/ai-insights',
        points: 100,
    },
    {
        id: 'check_gamification',
        title: 'Check your achievements',
        description: 'See your progress on the leaderboard',
        icon: Trophy,
        href: '/gamification',
        points: 50,
    },
];

export default function OnboardingChecklist() {
    const [isExpanded, setIsExpanded] = useState(true);
    const [isDismissed, setIsDismissed] = useState(true);
    const [items, setItems] = useState<ChecklistItem[]>([]);
    const [totalXp, setTotalXp] = useState(0);
    const router = useRouter();
    const { isAuthenticated } = useAuth();

    const loadOnboardingProgress = useCallback(async () => {
        if (!isAuthenticated) {
            // Don't fetch if not authenticated
            setIsDismissed(true);
            return;
        }

        try {
            // Try to fetch from backend
            const status = await onboardingAPI.getStatus();

            const completedSteps = status.completed_steps || [];
            setTotalXp(status.onboarding_xp || 0);

            // Merge with default items
            const mergedItems = defaultChecklist.map(item => ({
                ...item,
                completed: completedSteps.includes(item.id),
            }));
            setItems(mergedItems);

            // Check if dismissed
            if (status.tour_dismissed) {
                setIsDismissed(true);
            } else {
                setIsDismissed(false);
            }
        } catch (error) {
            // Fallback to localStorage
            console.error('Failed to fetch onboarding progress:', error);
            const dismissed = localStorage.getItem(CHECKLIST_DISMISSED_KEY);
            if (dismissed) {
                setIsDismissed(true);
                return;
            }

            const saved = localStorage.getItem(CHECKLIST_STORAGE_KEY);
            if (saved) {
                try {
                    const savedItems = JSON.parse(saved);
                    const mergedItems = defaultChecklist.map(item => ({
                        ...item,
                        completed: savedItems.find((s: ChecklistItem) => s.id === item.id)?.completed || false,
                    }));
                    setItems(mergedItems);
                    setTotalXp(mergedItems.filter(i => i.completed).reduce((acc, i) => acc + i.points, 0));
                } catch {
                    setItems(defaultChecklist.map(item => ({ ...item, completed: false })));
                }
            } else {
                setItems(defaultChecklist.map(item => ({ ...item, completed: false })));
            }
            setIsDismissed(false);
        }
    }, [isAuthenticated]);

    useEffect(() => {
        // Defer call to avoid synchronous setState inside effect
        Promise.resolve().then(() => loadOnboardingProgress());

    }, [loadOnboardingProgress]);

    const completedCount = items.filter(item => item.completed).length;
    const calculatedPoints = items.filter(item => item.completed).reduce((acc, item) => acc + item.points, 0);
    const displayPoints = totalXp || calculatedPoints;
    const maxPoints = items.reduce((acc, item) => acc + item.points, 0);
    const progress = items.length > 0 ? (completedCount / items.length) * 100 : 0;

    const completeItem = async (id: string) => {
        const item = items.find(i => i.id === id);
        if (!item || item.completed) return;

        // Optimistically update UI
        const updatedItems = items.map(i =>
            i.id === id ? { ...i, completed: true } : i
        );
        setItems(updatedItems);
        setTotalXp(prev => prev + item.points);

        // Save to localStorage as backup
        localStorage.setItem(CHECKLIST_STORAGE_KEY, JSON.stringify(updatedItems));

        try {
            // Sync with backend only if authenticated
            if (isAuthenticated) {
                await onboardingAPI.completeStep(id, item.points);
            }
        } catch (error) {
            // Already saved locally, continue
            console.error('Failed to sync step completion:', error);
            console.warn('Step completion synced locally');
        }

        toast.success(`🎉 +${item.points} XP earned!`, {
            description: `Completed: ${item.title}`,
        });

        // Check if all items are completed
        if (updatedItems.every(item => item.completed)) {
            setTimeout(() => {
                toast.success('🏆 Onboarding Complete!', {
                    description: `You earned a total of ${  maxPoints  } XP!`,
                });
            }, 500);
        }
    };

    const handleItemClick = (item: ChecklistItem) => {
        router.push(item.href);
        // Mark as complete when they visit the page
        if (!item.completed) {
            setTimeout(() => {
                completeItem(item.id);
            }, 1000);
        }
    };

    const dismissChecklist = async () => {
        setIsDismissed(true);
        localStorage.setItem(CHECKLIST_DISMISSED_KEY, 'true');

        try {
            if (isAuthenticated) {
                await onboardingAPI.dismissTour();
            }
        } catch (error) {
            // Already saved locally
            console.error('Failed to sync checklist dismissal:', error);
            console.warn('Checklist dismissal synced locally');
        }

        toast.info('You can find the checklist in Settings anytime');
    };

    if (isDismissed || completedCount === items.length || !isAuthenticated) {
        return null;
    }

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="fixed bottom-24 left-6 z-40 w-80"
        >
            <Card className="shadow-xl border-2 border-blue-100 dark:border-blue-900 overflow-hidden">
                {/* Header */}
                <CardHeader className="pb-2 bg-linear-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <motion.div
                                animate={{ rotate: [0, 10, -10, 0] }}
                                transition={{ duration: 2, repeat: Infinity }}
                            >
                                <Rocket className="w-5 h-5 text-blue-600" />
                            </motion.div>
                            <CardTitle className="text-base font-semibold">Getting Started</CardTitle>
                        </div>
                        <div className="flex items-center gap-1">
                            <Button
                                variant="ghost"
                                size="icon"
                                className="h-7 w-7 text-gray-400 hover:text-gray-600"
                                onClick={() => setIsExpanded(!isExpanded)}
                            >
                                {isExpanded ? (
                                    <ChevronDown className="h-4 w-4" />
                                ) : (
                                    <ChevronUp className="h-4 w-4" />
                                )}
                            </Button>
                            <Button
                                variant="ghost"
                                size="icon"
                                className="h-7 w-7 text-gray-400 hover:text-gray-600"
                                onClick={dismissChecklist}
                            >
                                <X className="h-4 w-4" />
                            </Button>
                        </div>
                    </div>

                    {/* Progress */}
                    <div className="mt-3">
                        <div className="flex items-center justify-between text-xs mb-1">
                            <span className="text-gray-600 dark:text-gray-400">
                                {completedCount} of {items.length} complete
                            </span>
                            <Badge variant="secondary" className="gap-1 text-xs">
                                <Zap className="w-3 h-3" />
                                {displayPoints} XP
                            </Badge>
                        </div>
                        <Progress value={progress} className="h-2" />
                    </div>
                </CardHeader>

                {/* Checklist Items */}
                <AnimatePresence>
                    {isExpanded && (
                        <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            transition={{ duration: 0.2 }}
                        >
                            <CardContent className="pt-3 max-h-64 overflow-y-auto space-y-1">
                                {items.map((item, index) => (
                                    <motion.div
                                        key={item.id}
                                        initial={{ opacity: 0, x: -10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: index * 0.05 }}
                                        onClick={() => handleItemClick(item)}
                                        className={`group flex items-center gap-3 p-2 rounded-lg cursor-pointer transition-all ${item.completed
                                            ? 'bg-green-50 dark:bg-green-900/20'
                                            : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                                            }`}
                                    >
                                        <div className={`shrink-0 ${item.completed ? 'text-green-500' : 'text-gray-300'}`}>
                                            {item.completed ? (
                                                <CheckCircle2 className="w-5 h-5" />
                                            ) : (
                                                <Circle className="w-5 h-5 group-hover:text-blue-400 transition-colors" />
                                            )}
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <p className={`text-sm font-medium truncate ${item.completed ? 'text-green-700 dark:text-green-400 line-through' : ''
                                                }`}>
                                                {item.title}
                                            </p>
                                            <p className="text-xs text-gray-500 truncate">{item.description}</p>
                                        </div>
                                        <div className="shrink-0 flex items-center gap-2">
                                            <Badge variant="outline" className="text-xs">
                                                +{item.points}
                                            </Badge>
                                            {!item.completed && (
                                                <ArrowRight className="w-4 h-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                                            )}
                                        </div>
                                    </motion.div>
                                ))}
                            </CardContent>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Bonus reward teaser */}
                <div className="px-4 py-2 bg-linear-to-r from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 border-t">
                    <div className="flex items-center gap-2 text-xs">
                        <Gift className="w-4 h-4 text-amber-500" />
                        <span className="text-amber-700 dark:text-amber-400 font-medium">
                            Complete all tasks to unlock a special badge!
                        </span>
                    </div>
                </div>
            </Card>
        </motion.div>
    );
}

