'use client';

import { useState, createContext, useContext, useCallback, ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Trophy,
    Star,
    Target,
    Zap,
    Award,
    TrendingUp,
    Users,
    Mail,
    Calendar,
    CheckCircle2,
    Sparkles,
    X,
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

import Confetti from './Confetti';

// Achievement types and icons
const achievementIcons: Record<string, React.ElementType> = {
    trophy: Trophy,
    star: Star,
    target: Target,
    zap: Zap,
    award: Award,
    trending: TrendingUp,
    users: Users,
    mail: Mail,
    calendar: Calendar,
    check: CheckCircle2,
    sparkles: Sparkles,
};

// Achievement tier colors
const tierColors: Record<string, { bg: string; border: string; text: string; glow: string }> = {
    bronze: {
        bg: 'from-amber-600 to-orange-700',
        border: 'border-amber-400',
        text: 'text-amber-100',
        glow: 'shadow-amber-500/50',
    },
    silver: {
        bg: 'from-gray-400 to-gray-500',
        border: 'border-gray-300',
        text: 'text-gray-100',
        glow: 'shadow-gray-400/50',
    },
    gold: {
        bg: 'from-yellow-500 to-amber-600',
        border: 'border-yellow-300',
        text: 'text-yellow-100',
        glow: 'shadow-yellow-500/50',
    },
    platinum: {
        bg: 'from-purple-500 to-indigo-600',
        border: 'border-purple-300',
        text: 'text-purple-100',
        glow: 'shadow-purple-500/50',
    },
    diamond: {
        bg: 'from-cyan-400 to-blue-500',
        border: 'border-cyan-300',
        text: 'text-cyan-100',
        glow: 'shadow-cyan-400/50',
    },
};

export interface Achievement {
    id: string;
    title: string;
    description: string;
    icon?: string;
    tier?: 'bronze' | 'silver' | 'gold' | 'platinum' | 'diamond';
    points?: number;
    showConfetti?: boolean;
}

interface AchievementContextType {
    showAchievement: (achievement: Achievement) => void;
    achievements: Achievement[];
}

const AchievementContext = createContext<AchievementContextType | null>(null);

export function useAchievement() {
    const context = useContext(AchievementContext);
    if (!context) {
        throw new Error('useAchievement must be used within an AchievementProvider');
    }
    return context;
}

interface AchievementProviderProps {
    children: ReactNode;
}

export function AchievementProvider({ children }: AchievementProviderProps) {
    const [achievements, setAchievements] = useState<Achievement[]>([]);
    const [currentAchievement, setCurrentAchievement] = useState<Achievement | null>(null);
    const [showConfetti, setShowConfetti] = useState(false);

    const showAchievement = useCallback((achievement: Achievement) => {
        setAchievements(prev => [...prev, achievement]);
        setCurrentAchievement(achievement);

        if (achievement.showConfetti !== false) {
            setShowConfetti(true);
        }

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            setCurrentAchievement(null);
            setShowConfetti(false);
        }, 5000);
    }, []);

    const dismissAchievement = useCallback(() => {
        setCurrentAchievement(null);
        setShowConfetti(false);
    }, []);

    return (
        <AchievementContext.Provider value={{ showAchievement, achievements }}>
            {children}

            {/* Confetti Effect */}
            <Confetti
                active={showConfetti}
                onComplete={() => setShowConfetti(false)}
                duration={3000}
                particleCount={150}
            />

            {/* Achievement Toast */}
            <AnimatePresence>
                {currentAchievement && (
                    <AchievementToast
                        achievement={currentAchievement}
                        onDismiss={dismissAchievement}
                    />
                )}
            </AnimatePresence>
        </AchievementContext.Provider>
    );
}

interface AchievementToastProps {
    achievement: Achievement;
    onDismiss: () => void;
}

function AchievementToast({ achievement, onDismiss }: AchievementToastProps) {
    const tier = achievement.tier || 'gold';
    const colors = tierColors[tier];
    const IconComponent = achievementIcons[achievement.icon || 'trophy'];

    return (
        <motion.div
            initial={{ opacity: 0, y: -100, scale: 0.8 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -50, scale: 0.9 }}
            transition={{
                type: 'spring',
                stiffness: 300,
                damping: 25
            }}
            className="fixed top-6 left-1/2 -translate-x-1/2 z-101"
        >
            <div
                className={cn(
                    "relative overflow-hidden rounded-2xl p-1",
                    "bg-linear-to-r",
                    colors.bg,
                    "shadow-2xl",
                    colors.glow
                )}
            >
                {/* Animated glow effect */}
                <div className="absolute inset-0 bg-white/20 animate-pulse" />

                {/* Inner content */}
                <div className="relative bg-background/95 backdrop-blur-xl rounded-xl p-4 min-w-[320px]">
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={onDismiss}
                        className="absolute top-2 right-2 h-6 w-6 text-muted-foreground hover:text-foreground"
                    >
                        <X className="h-4 w-4" />
                    </Button>

                    <div className="flex items-center gap-4">
                        {/* Achievement Icon */}
                        <motion.div
                            initial={{ scale: 0, rotate: -180 }}
                            animate={{ scale: 1, rotate: 0 }}
                            transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
                            className={cn(
                                "h-16 w-16 rounded-xl flex items-center justify-center",
                                "bg-linear-to-br",
                                colors.bg,
                                colors.border,
                                "border-2 shadow-lg"
                            )}
                        >
                            <IconComponent className={cn("h-8 w-8", colors.text)} />
                        </motion.div>

                        {/* Achievement Details */}
                        <div className="flex-1 pr-6">
                            <motion.div
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.3 }}
                                className="flex items-center gap-2 mb-1"
                            >
                                <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                                    Achievement Unlocked!
                                </span>
                                <Sparkles className="h-3 w-3 text-yellow-500 animate-pulse" />
                            </motion.div>

                            <motion.h3
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.4 }}
                                className="font-bold text-lg"
                            >
                                {achievement.title}
                            </motion.h3>

                            <motion.p
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.5 }}
                                className="text-sm text-muted-foreground"
                            >
                                {achievement.description}
                            </motion.p>

                            {achievement.points && (
                                <motion.div
                                    initial={{ opacity: 0, scale: 0.8 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    transition={{ delay: 0.6 }}
                                    className="flex items-center gap-1 mt-2"
                                >
                                    <Star className="h-4 w-4 text-yellow-500 fill-yellow-500" />
                                    <span className="text-sm font-bold text-yellow-600 dark:text-yellow-400">
                                        +{achievement.points} points
                                    </span>
                                </motion.div>
                            )}
                        </div>
                    </div>

                    {/* Progress bar animation */}
                    <motion.div
                        initial={{ scaleX: 1 }}
                        animate={{ scaleX: 0 }}
                        transition={{ duration: 5, ease: 'linear' }}
                        className={cn(
                            "absolute bottom-0 left-0 right-0 h-1 origin-left",
                            "bg-linear-to-r",
                            colors.bg
                        )}
                    />
                </div>
            </div>
        </motion.div>
    );
}

// Demo function to test achievements
export function triggerDemoAchievement(showAchievement: (a: Achievement) => void) {
    const demoAchievements: Achievement[] = [
        {
            id: 'first-lead',
            title: 'First Lead',
            description: 'Created your first lead in MyCRM',
            icon: 'target',
            tier: 'bronze',
            points: 50,
        },
        {
            id: 'deal-closer',
            title: 'Deal Closer',
            description: 'Closed your first deal!',
            icon: 'trophy',
            tier: 'gold',
            points: 200,
        },
        {
            id: 'email-master',
            title: 'Email Master',
            description: 'Sent 100 emails to prospects',
            icon: 'mail',
            tier: 'silver',
            points: 100,
        },
        {
            id: 'revenue-king',
            title: 'Revenue King',
            description: 'Generated $100K in pipeline value',
            icon: 'trending',
            tier: 'platinum',
            points: 500,
        },
        {
            id: 'ai-pioneer',
            title: 'AI Pioneer',
            description: 'Used AI assistant 50 times',
            icon: 'sparkles',
            tier: 'diamond',
            points: 300,
        },
    ];

    const randomAchievement = demoAchievements[Math.floor(Math.random() * demoAchievements.length)];
    showAchievement(randomAchievement);
}

