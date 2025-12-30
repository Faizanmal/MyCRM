'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
    X,
    ChevronRight,
    ChevronLeft,
    Sparkles,
    Users,
    TrendingUp,
    BarChart3,
    Calendar,
    Trophy,
    Zap,
    CheckCircle2,
    Lightbulb,
    Target,
    Rocket,
} from 'lucide-react';
import { onboardingAPI } from '@/lib/api';

interface TourStep {
    id: string;
    title: string;
    description: string;
    icon: React.ElementType;
    highlight?: string; // CSS selector for element to highlight
    position?: 'top' | 'bottom' | 'left' | 'right' | 'center';
    action?: string;
    tip?: string;
}

const tourSteps: TourStep[] = [
    {
        id: 'welcome',
        title: 'Welcome to MyCRM! 🎉',
        description: 'Your intelligent CRM platform with AI-powered insights, gamification, and everything you need to close more deals. Let\'s take a quick tour!',
        icon: Rocket,
        position: 'center',
        tip: 'This tour takes about 2 minutes',
    },
    {
        id: 'dashboard',
        title: 'Your Command Center',
        description: 'The dashboard gives you an instant overview of your sales pipeline, recent activities, and key metrics. All your important data at a glance.',
        icon: BarChart3,
        highlight: '[data-tour="dashboard"]',
        position: 'right',
        action: 'View your daily KPIs and performance trends',
    },
    {
        id: 'contacts',
        title: 'Manage Your Network',
        description: 'Keep all your contacts organized in one place. Add custom fields, track interactions, and never lose touch with important relationships.',
        icon: Users,
        highlight: '[data-tour="contacts"]',
        position: 'right',
        tip: 'Pro tip: Use tags to segment your contacts!',
    },
    {
        id: 'opportunities',
        title: 'Track Your Deals',
        description: 'Visualize your pipeline with our drag-and-drop Kanban board. Move deals through stages and keep track of every opportunity.',
        icon: TrendingUp,
        highlight: '[data-tour="opportunities"]',
        position: 'right',
        tip: 'Drag cards to move deals between stages',
    },
    {
        id: 'ai-insights',
        title: 'AI-Powered Intelligence',
        description: 'Let AI analyze your data and provide actionable insights. Get predictions on deal closures, churn risk, and next best actions.',
        icon: Sparkles,
        highlight: '[data-tour="ai-insights"]',
        position: 'right',
        action: 'Explore AI recommendations tailored for you',
    },
    {
        id: 'tasks',
        title: 'Stay Organized',
        description: 'Never miss a follow-up! Create tasks, set reminders, and manage your calendar. Smart scheduling helps you find the best times.',
        icon: Calendar,
        highlight: '[data-tour="tasks"]',
        position: 'right',
    },
    {
        id: 'gamification',
        title: 'Level Up Your Sales! 🏆',
        description: 'Earn points, unlock achievements, and compete with your team on the leaderboard. Make sales fun and track your progress.',
        icon: Trophy,
        highlight: '[data-tour="gamification"]',
        position: 'right',
        tip: 'Complete daily challenges for bonus XP!',
    },
    {
        id: 'command-palette',
        title: 'Quick Navigation',
        description: 'Press ⌘K (or Ctrl+K) anytime to open the command palette. Search anything, navigate instantly, and take quick actions.',
        icon: Zap,
        position: 'center',
        action: 'Press ⌘K to try it now!',
    },
    {
        id: 'ai-assistant',
        title: 'Your AI Sales Assistant',
        description: 'Click the AI button in the corner anytime you need help. Get email templates, sales tips, or quick insights on any page.',
        icon: Lightbulb,
        position: 'center',
        tip: 'Ask the AI to help draft emails or analyze deals',
    },
    {
        id: 'complete',
        title: 'You\'re All Set! 🚀',
        description: 'You\'re ready to start using MyCRM. Explore all the features and reach out if you need any help. Good luck closing those deals!',
        icon: Target,
        position: 'center',
    },
];

const TOUR_STORAGE_KEY = 'mycrm_tour_completed';
const TOUR_DISMISSED_KEY = 'mycrm_tour_dismissed';

export default function ProductTour() {
    const [isActive, setIsActive] = useState(false);
    const [currentStep, setCurrentStep] = useState(0);
    const [hasSeenTour, setHasSeenTour] = useState(true);

    useEffect(() => {
        const checkTourStatus = async () => {
            try {
                // Try to get status from backend
                const status = await onboardingAPI.getStatus();
                if (status.tour_completed || status.tour_dismissed) {
                    setHasSeenTour(true);
                    return;
                }
                // Show tour for new users
                setTimeout(() => setHasSeenTour(false), 2000);
            } catch {
                // Fallback to localStorage
                const tourCompleted = localStorage.getItem(TOUR_STORAGE_KEY);
                const tourDismissed = localStorage.getItem(TOUR_DISMISSED_KEY);

                if (!tourCompleted && !tourDismissed) {
                    setTimeout(() => setHasSeenTour(false), 2000);
                }
            }
        };

        checkTourStatus();
    }, []);

    const startTour = useCallback(() => {
        setIsActive(true);
        setCurrentStep(0);
        setHasSeenTour(true);
    }, []);

    const endTour = useCallback(async (completed: boolean = false) => {
        setIsActive(false);
        setCurrentStep(0);
        if (completed) {
            localStorage.setItem(TOUR_STORAGE_KEY, 'true');
            try {
                await onboardingAPI.completeTour();
            } catch {
                // Already saved locally
            }
        }
    }, []);

    const dismissTour = useCallback(async () => {
        setHasSeenTour(true);
        localStorage.setItem(TOUR_DISMISSED_KEY, 'true');
        try {
            await onboardingAPI.dismissTour();
        } catch {
            // Already saved locally
        }
    }, []);

    const nextStep = useCallback(() => {
        if (currentStep < tourSteps.length - 1) {
            setCurrentStep(prev => prev + 1);
        } else {
            endTour(true);
        }
    }, [currentStep, endTour]);

    const prevStep = useCallback(() => {
        if (currentStep > 0) {
            setCurrentStep(prev => prev - 1);
        }
    }, [currentStep]);

    const step = tourSteps[currentStep];
    const progress = ((currentStep + 1) / tourSteps.length) * 100;

    // Render welcome prompt for new users
    if (!hasSeenTour) {
        return (
            <AnimatePresence>
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[100] flex items-center justify-center p-4"
                >
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0.9, opacity: 0 }}
                        className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl max-w-md w-full p-8 text-center"
                    >
                        <motion.div
                            animate={{
                                scale: [1, 1.1, 1],
                                rotate: [0, 5, -5, 0],
                            }}
                            transition={{
                                duration: 2,
                                repeat: Infinity,
                                repeatType: 'reverse',
                            }}
                            className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center"
                        >
                            <Rocket className="w-10 h-10 text-white" />
                        </motion.div>

                        <h2 className="text-2xl font-bold mb-3 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                            Welcome to MyCRM!
                        </h2>
                        <p className="text-gray-600 dark:text-gray-400 mb-6">
                            Would you like a quick tour of the key features? It only takes about 2 minutes.
                        </p>

                        <div className="flex flex-col gap-3">
                            <Button onClick={startTour} className="w-full gap-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                                <Sparkles className="w-4 h-4" />
                                Start the Tour
                            </Button>
                            <Button variant="ghost" onClick={dismissTour} className="w-full text-gray-500">
                                Maybe Later
                            </Button>
                        </div>
                    </motion.div>
                </motion.div>
            </AnimatePresence>
        );
    }

    if (!isActive) return null;

    return (
        <AnimatePresence>
            {isActive && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100]"
                        onClick={() => endTour(false)}
                    />

                    {/* Tour Modal */}
                    <motion.div
                        key={step.id}
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        transition={{ type: 'spring', damping: 25, stiffness: 300 }}
                        className="fixed z-[101] top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-lg p-4"
                    >
                        <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl overflow-hidden">
                            {/* Progress bar */}
                            <div className="h-1 bg-gray-100 dark:bg-gray-800">
                                <motion.div
                                    className="h-full bg-gradient-to-r from-blue-500 to-purple-600"
                                    initial={{ width: 0 }}
                                    animate={{ width: `${progress}%` }}
                                    transition={{ duration: 0.3 }}
                                />
                            </div>

                            {/* Header */}
                            <div className="p-6 pb-0">
                                <div className="flex items-start justify-between mb-4">
                                    <div className="flex items-center gap-3">
                                        <motion.div
                                            animate={{ rotate: [0, 10, -10, 0] }}
                                            transition={{ duration: 0.5, delay: 0.2 }}
                                            className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center"
                                        >
                                            <step.icon className="w-6 h-6 text-white" />
                                        </motion.div>
                                        <div>
                                            <Badge variant="secondary" className="mb-1">
                                                Step {currentStep + 1} of {tourSteps.length}
                                            </Badge>
                                            <h3 className="text-xl font-bold">{step.title}</h3>
                                        </div>
                                    </div>
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        onClick={() => endTour(false)}
                                        className="text-gray-400 hover:text-gray-600"
                                    >
                                        <X className="w-5 h-5" />
                                    </Button>
                                </div>
                            </div>

                            {/* Content */}
                            <div className="px-6 pb-6">
                                <p className="text-gray-600 dark:text-gray-400 mb-4 leading-relaxed">
                                    {step.description}
                                </p>

                                {step.tip && (
                                    <motion.div
                                        initial={{ opacity: 0, x: -10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: 0.3 }}
                                        className="flex items-start gap-2 p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800 mb-4"
                                    >
                                        <Lightbulb className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
                                        <p className="text-sm text-amber-800 dark:text-amber-200">{step.tip}</p>
                                    </motion.div>
                                )}

                                {step.action && (
                                    <motion.div
                                        initial={{ opacity: 0, x: -10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: 0.4 }}
                                        className="flex items-center gap-2 text-blue-600 dark:text-blue-400 text-sm font-medium"
                                    >
                                        <CheckCircle2 className="w-4 h-4" />
                                        {step.action}
                                    </motion.div>
                                )}
                            </div>

                            {/* Footer */}
                            <div className="px-6 py-4 bg-gray-50 dark:bg-gray-800/50 flex items-center justify-between">
                                <Button
                                    variant="ghost"
                                    onClick={prevStep}
                                    disabled={currentStep === 0}
                                    className="gap-2"
                                >
                                    <ChevronLeft className="w-4 h-4" />
                                    Back
                                </Button>

                                <div className="flex items-center gap-1">
                                    {tourSteps.map((_, index) => (
                                        <motion.div
                                            key={index}
                                            className={`w-2 h-2 rounded-full transition-colors ${index === currentStep
                                                ? 'bg-blue-600'
                                                : index < currentStep
                                                    ? 'bg-blue-300'
                                                    : 'bg-gray-300 dark:bg-gray-600'
                                                }`}
                                            animate={index === currentStep ? { scale: [1, 1.2, 1] } : {}}
                                            transition={{ duration: 0.3 }}
                                        />
                                    ))}
                                </div>

                                <Button
                                    onClick={nextStep}
                                    className="gap-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                                >
                                    {currentStep === tourSteps.length - 1 ? (
                                        <>
                                            Get Started
                                            <Rocket className="w-4 h-4" />
                                        </>
                                    ) : (
                                        <>
                                            Next
                                            <ChevronRight className="w-4 h-4" />
                                        </>
                                    )}
                                </Button>
                            </div>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}

// Export a hook to trigger the tour from anywhere
export function useProductTour() {
    const restartTour = () => {
        localStorage.removeItem(TOUR_STORAGE_KEY);
        localStorage.removeItem(TOUR_DISMISSED_KEY);
        window.location.reload();
    };

    return { restartTour };
}
