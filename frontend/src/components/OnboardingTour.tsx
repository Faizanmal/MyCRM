'use client';

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, ChevronLeft, ChevronRight, Check, Circle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

interface TourStep {
    id: string;
    target: string; // CSS selector for the target element
    title: string;
    content: string;
    placement?: 'top' | 'bottom' | 'left' | 'right';
    spotlightPadding?: number;
    action?: () => void;
    actionLabel?: string;
}

interface OnboardingTourContextType {
    isActive: boolean;
    currentStep: number;
    steps: TourStep[];
    startTour: (steps: TourStep[]) => void;
    endTour: () => void;
    nextStep: () => void;
    prevStep: () => void;
    skipTour: () => void;
    goToStep: (index: number) => void;
}

const OnboardingTourContext = createContext<OnboardingTourContextType | null>(null);

export function useOnboardingTour() {
    const context = useContext(OnboardingTourContext);
    if (!context) {
        throw new Error('useOnboardingTour must be used within OnboardingTourProvider');
    }
    return context;
}

interface OnboardingTourProviderProps {
    children: ReactNode;
    onComplete?: () => void;
    storageKey?: string;
}

export function OnboardingTourProvider({
    children,
    onComplete,
    storageKey = 'mycrm-onboarding-complete'
}: OnboardingTourProviderProps) {
    const [isActive, setIsActive] = useState(false);
    const [currentStep, setCurrentStep] = useState(0);
    const [steps, setSteps] = useState<TourStep[]>([]);
    const [targetRect, setTargetRect] = useState<DOMRect | null>(null);

    const updateTargetRect = useCallback(() => {
        if (!isActive || !steps[currentStep]) return;

        const target = document.querySelector(steps[currentStep].target);
        if (target) {
            setTargetRect(target.getBoundingClientRect());
            target.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }, [isActive, currentStep, steps]);

    useEffect(() => {
        updateTargetRect();
        window.addEventListener('resize', updateTargetRect);
        window.addEventListener('scroll', updateTargetRect);

        return () => {
            window.removeEventListener('resize', updateTargetRect);
            window.removeEventListener('scroll', updateTargetRect);
        };
    }, [updateTargetRect]);

    const startTour = useCallback((tourSteps: TourStep[]) => {
        setSteps(tourSteps);
        setCurrentStep(0);
        setIsActive(true);
    }, []);

    const endTour = useCallback(() => {
        setIsActive(false);
        setCurrentStep(0);
        setSteps([]);
        if (storageKey) {
            localStorage.setItem(storageKey, 'true');
        }
        onComplete?.();
    }, [onComplete, storageKey]);

    const nextStep = useCallback(() => {
        if (currentStep < steps.length - 1) {
            setCurrentStep(prev => prev + 1);
        } else {
            endTour();
        }
    }, [currentStep, steps.length, endTour]);

    const prevStep = useCallback(() => {
        if (currentStep > 0) {
            setCurrentStep(prev => prev - 1);
        }
    }, [currentStep]);

    const skipTour = useCallback(() => {
        endTour();
    }, [endTour]);

    const goToStep = useCallback((index: number) => {
        if (index >= 0 && index < steps.length) {
            setCurrentStep(index);
        }
    }, [steps.length]);

    const getTooltipPosition = useCallback(() => {
        if (!targetRect) return { top: '50%', left: '50%' };

        const step = steps[currentStep];
        const placement = step?.placement || 'bottom';
        const padding = step?.spotlightPadding || 10;

        switch (placement) {
            case 'top':
                return {
                    top: targetRect.top - padding - 10,
                    left: targetRect.left + targetRect.width / 2,
                    transform: 'translate(-50%, -100%)'
                };
            case 'bottom':
                return {
                    top: targetRect.bottom + padding + 10,
                    left: targetRect.left + targetRect.width / 2,
                    transform: 'translate(-50%, 0)'
                };
            case 'left':
                return {
                    top: targetRect.top + targetRect.height / 2,
                    left: targetRect.left - padding - 10,
                    transform: 'translate(-100%, -50%)'
                };
            case 'right':
                return {
                    top: targetRect.top + targetRect.height / 2,
                    left: targetRect.right + padding + 10,
                    transform: 'translate(0, -50%)'
                };
            default:
                return {
                    top: targetRect.bottom + padding + 10,
                    left: targetRect.left + targetRect.width / 2,
                    transform: 'translate(-50%, 0)'
                };
        }
    }, [targetRect, steps, currentStep]);

    return (
        <OnboardingTourContext.Provider value={{
            isActive,
            currentStep,
            steps,
            startTour,
            endTour,
            nextStep,
            prevStep,
            skipTour,
            goToStep
        }}>
            {children}

            <AnimatePresence>
                {isActive && targetRect && (
                    <>
                        {/* Overlay */}
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="fixed inset-0 z-[9998]"
                            style={{
                                background: 'rgba(0, 0, 0, 0.5)',
                                clipPath: `polygon(
                  0% 0%,
                  0% 100%,
                  ${targetRect.left - 10}px 100%,
                  ${targetRect.left - 10}px ${targetRect.top - 10}px,
                  ${targetRect.right + 10}px ${targetRect.top - 10}px,
                  ${targetRect.right + 10}px ${targetRect.bottom + 10}px,
                  ${targetRect.left - 10}px ${targetRect.bottom + 10}px,
                  ${targetRect.left - 10}px 100%,
                  100% 100%,
                  100% 0%
                )`
                            }}
                            onClick={skipTour}
                        />

                        {/* Spotlight border */}
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.9 }}
                            className="fixed z-[9999] pointer-events-none"
                            style={{
                                top: targetRect.top - 10,
                                left: targetRect.left - 10,
                                width: targetRect.width + 20,
                                height: targetRect.height + 20,
                                border: '2px solid #3b82f6',
                                borderRadius: '8px',
                                boxShadow: '0 0 0 4px rgba(59, 130, 246, 0.3)'
                            }}
                        />

                        {/* Tooltip */}
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: 10 }}
                            className="fixed z-[10000] w-80"
                            style={getTooltipPosition()}
                        >
                            <Card className="shadow-xl border-2 border-blue-500">
                                <CardHeader className="pb-2">
                                    <div className="flex items-center justify-between">
                                        <CardTitle className="text-lg">{steps[currentStep]?.title}</CardTitle>
                                        <Button
                                            size="icon"
                                            variant="ghost"
                                            className="h-6 w-6"
                                            onClick={skipTour}
                                        >
                                            <X className="h-4 w-4" />
                                        </Button>
                                    </div>
                                    <CardDescription className="text-sm">
                                        Step {currentStep + 1} of {steps.length}
                                    </CardDescription>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <p className="text-sm text-gray-600">{steps[currentStep]?.content}</p>

                                    {/* Progress dots */}
                                    <div className="flex items-center justify-center gap-1">
                                        {steps.map((_, index) => (
                                            <button
                                                key={index}
                                                onClick={() => goToStep(index)}
                                                className="p-0.5"
                                            >
                                                {index < currentStep ? (
                                                    <Check className="h-3 w-3 text-green-500" />
                                                ) : index === currentStep ? (
                                                    <Circle className="h-3 w-3 text-blue-500 fill-blue-500" />
                                                ) : (
                                                    <Circle className="h-3 w-3 text-gray-300" />
                                                )}
                                            </button>
                                        ))}
                                    </div>

                                    {/* Progress bar */}
                                    <Progress value={((currentStep + 1) / steps.length) * 100} className="h-1" />

                                    {/* Actions */}
                                    <div className="flex items-center justify-between pt-2">
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={prevStep}
                                            disabled={currentStep === 0}
                                        >
                                            <ChevronLeft className="h-4 w-4 mr-1" />
                                            Back
                                        </Button>

                                        <div className="flex gap-2">
                                            <Button variant="outline" size="sm" onClick={skipTour}>
                                                Skip
                                            </Button>

                                            {steps[currentStep]?.action && (
                                                <Button
                                                    size="sm"
                                                    variant="secondary"
                                                    onClick={steps[currentStep].action}
                                                >
                                                    {steps[currentStep].actionLabel || 'Try it'}
                                                </Button>
                                            )}

                                            <Button size="sm" onClick={nextStep}>
                                                {currentStep === steps.length - 1 ? 'Finish' : 'Next'}
                                                {currentStep < steps.length - 1 && <ChevronRight className="h-4 w-4 ml-1" />}
                                            </Button>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        </motion.div>
                    </>
                )}
            </AnimatePresence>
        </OnboardingTourContext.Provider>
    );
}

// Pre-defined tour configurations
export const dashboardTour: TourStep[] = [
    {
        id: 'welcome',
        target: '.dashboard-header',
        title: 'Welcome to MyCRM! 👋',
        content: 'This is your dashboard where you can see an overview of your sales activities and key metrics.',
        placement: 'bottom'
    },
    {
        id: 'stats',
        target: '.stats-cards',
        title: 'Quick Stats',
        content: 'These cards show your key performance indicators at a glance - leads, deals, revenue, and tasks.',
        placement: 'bottom'
    },
    {
        id: 'sidebar',
        target: '.sidebar-nav',
        title: 'Navigation',
        content: 'Use the sidebar to navigate between different sections of the CRM - Leads, Contacts, Deals, and more.',
        placement: 'right'
    },
    {
        id: 'command-palette',
        target: '[data-command-palette]',
        title: 'Quick Actions (⌘+K)',
        content: 'Press ⌘+K (or Ctrl+K) anytime to open the command palette for quick navigation and actions.',
        placement: 'bottom'
    },
    {
        id: 'ai-assistant',
        target: '[data-ai-assistant]',
        title: 'AI Assistant',
        content: 'Click the AI chat button to get help, insights, and recommendations powered by AI.',
        placement: 'left'
    }
];

export const leadsTour: TourStep[] = [
    {
        id: 'leads-list',
        target: '.leads-table',
        title: 'Your Leads',
        content: 'This table shows all your leads. You can sort, filter, and search to find specific leads.',
        placement: 'top'
    },
    {
        id: 'add-lead',
        target: '[data-add-lead]',
        title: 'Add New Lead',
        content: 'Click here to add a new lead to your pipeline.',
        placement: 'bottom'
    },
    {
        id: 'lead-scoring',
        target: '.lead-score',
        title: 'AI Lead Scoring',
        content: 'Each lead has an AI-generated score based on their likelihood to convert. Focus on high-scoring leads.',
        placement: 'left'
    }
];

export default OnboardingTourProvider;
