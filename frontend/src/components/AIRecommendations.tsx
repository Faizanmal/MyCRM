'use client';

import { useEffect, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
    TrendingUp,
    AlertTriangle,
    ArrowRight,
    X,
    Sparkles,
    Phone,
    Calendar,
    Lightbulb,
    Target,
    RefreshCw,
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import { recommendationsAPI } from '@/lib/api';
import { toast } from 'sonner';

interface AIRecommendation {
    id: string;
    recommendation_type: 'action' | 'insight' | 'warning' | 'opportunity' | 'tip';
    title: string;
    description: string;
    impact: 'high' | 'medium' | 'low';
    action_label: string;
    action_url: string;
    dismissable: boolean;
    confidence_score?: number;
}

// Map recommendation types to icons
const typeIcons: Record<string, React.ElementType> = {
    action: Phone,
    insight: Lightbulb,
    warning: AlertTriangle,
    opportunity: TrendingUp,
    tip: Target,
};

const typeStyles: Record<string, { bg: string; border: string; icon: string }> = {
    action: {
        bg: 'bg-blue-50 dark:bg-blue-900/20',
        border: 'border-blue-200 dark:border-blue-800',
        icon: 'text-blue-500',
    },
    insight: {
        bg: 'bg-purple-50 dark:bg-purple-900/20',
        border: 'border-purple-200 dark:border-purple-800',
        icon: 'text-purple-500',
    },
    warning: {
        bg: 'bg-amber-50 dark:bg-amber-900/20',
        border: 'border-amber-200 dark:border-amber-800',
        icon: 'text-amber-500',
    },
    opportunity: {
        bg: 'bg-green-50 dark:bg-green-900/20',
        border: 'border-green-200 dark:border-green-800',
        icon: 'text-green-500',
    },
    tip: {
        bg: 'bg-indigo-50 dark:bg-indigo-900/20',
        border: 'border-indigo-200 dark:border-indigo-800',
        icon: 'text-indigo-500',
    },
};

// Fallback mock data for when API is unavailable
const fallbackRecommendations: AIRecommendation[] = [
    {
        id: '1',
        recommendation_type: 'action',
        title: 'Follow up with hot leads',
        description: '3 leads haven\'t been contacted in 5 days. They showed high engagement last week.',
        impact: 'high',
        action_label: 'View Leads',
        action_url: '/leads?filter=hot',
        dismissable: false,
    },
    {
        id: '2',
        recommendation_type: 'opportunity',
        title: 'Upsell opportunity detected',
        description: 'TechCorp has expanded their team by 50%. Consider proposing our enterprise plan.',
        impact: 'high',
        action_label: 'View Details',
        action_url: '/opportunities',
        dismissable: true,
    },
    {
        id: '3',
        recommendation_type: 'warning',
        title: 'Deal at risk',
        description: 'Enterprise Deal - ABC Corp hasn\'t responded in 14 days. Engagement score dropped 40%.',
        impact: 'high',
        action_label: 'Take Action',
        action_url: '/opportunities',
        dismissable: false,
    },
    {
        id: '4',
        recommendation_type: 'insight',
        title: 'Best time to reach Sarah',
        description: 'Based on past interactions, Tuesdays at 2 PM show highest response rates.',
        impact: 'medium',
        action_label: 'Schedule',
        action_url: '/scheduling',
        dismissable: true,
    },
];

export default function AIRecommendations() {
    const [recommendations, setRecommendations] = useState<AIRecommendation[]>([]);
    const [isExpanded, setIsExpanded] = useState(true);
    const [isLoading, setIsLoading] = useState(true);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const router = useRouter();

    const fetchRecommendations = useCallback(async (showRefresh = false) => {
        try {
            if (showRefresh) setIsRefreshing(true);

            const data = await recommendationsAPI.getActive({ limit: 5 });

            if (Array.isArray(data) && data.length > 0) {
                setRecommendations(data);
            } else {
                // Use fallback data if API returns empty
                setRecommendations(fallbackRecommendations);
            }
        } catch (error) {
            // Use fallback recommendations if API fails
            console.log('Using fallback recommendations');
            setRecommendations(fallbackRecommendations);
        } finally {
            setIsLoading(false);
            setIsRefreshing(false);
        }
    }, []);

    useEffect(() => {
        fetchRecommendations();
    }, [fetchRecommendations]);

    const dismissRecommendation = async (id: string) => {
        try {
            // Optimistically remove from UI
            setRecommendations(prev => prev.filter(r => r.id !== id));

            // Call API to dismiss
            await recommendationsAPI.dismiss(id);
            toast.success('Recommendation dismissed');
        } catch (error) {
            // Silently handle - already removed from UI
            console.log('Dismiss synced locally');
        }
    };

    const handleAction = async (recommendation: AIRecommendation) => {
        try {
            // Mark as completed
            await recommendationsAPI.complete(recommendation.id);
        } catch (error) {
            // Continue navigation even if API fails
        }
        router.push(recommendation.action_url);
    };

    const handleRefresh = async () => {
        setIsRefreshing(true);
        try {
            await recommendationsAPI.generate();
            await fetchRecommendations(true);
            toast.success('Recommendations refreshed');
        } catch (error) {
            toast.error('Failed to refresh recommendations');
            setIsRefreshing(false);
        }
    };

    if (isLoading) {
        return (
            <div className="rounded-xl border bg-gradient-to-br from-indigo-50/50 via-purple-50/30 to-pink-50/50 dark:from-indigo-900/10 dark:via-purple-900/5 dark:to-pink-900/10 p-4">
                <div className="flex items-center gap-3 mb-4">
                    <Skeleton className="w-10 h-10 rounded-lg" />
                    <div>
                        <Skeleton className="h-5 w-40 mb-1" />
                        <Skeleton className="h-4 w-60" />
                    </div>
                </div>
                <div className="space-y-3">
                    {[1, 2, 3].map(i => (
                        <Skeleton key={i} className="h-24 w-full" />
                    ))}
                </div>
            </div>
        );
    }

    if (recommendations.length === 0) return null;

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-xl border bg-gradient-to-br from-indigo-50/50 via-purple-50/30 to-pink-50/50 dark:from-indigo-900/10 dark:via-purple-900/5 dark:to-pink-900/10 overflow-hidden"
        >
            {/* Header */}
            <div className="p-4 flex items-center justify-between border-b dark:border-gray-800">
                <div className="flex items-center gap-3">
                    <motion.div
                        animate={{ rotate: [0, 10, -10, 0] }}
                        transition={{ duration: 2, repeat: Infinity }}
                        className="p-2 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg"
                    >
                        <Sparkles className="w-5 h-5 text-white" />
                    </motion.div>
                    <div>
                        <h3 className="font-semibold flex items-center gap-2">
                            AI Recommendations
                            <Badge variant="secondary" className="text-xs">
                                {recommendations.length} suggestions
                            </Badge>
                        </h3>
                        <p className="text-sm text-gray-500">Personalized insights to help you close more deals</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={handleRefresh}
                        disabled={isRefreshing}
                        className="h-8 w-8"
                    >
                        <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                    </Button>
                    <Button variant="ghost" size="sm" onClick={() => setIsExpanded(!isExpanded)}>
                        {isExpanded ? 'Collapse' : 'Expand'}
                    </Button>
                </div>
            </div>

            {/* Recommendations */}
            <AnimatePresence>
                {isExpanded && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="divide-y dark:divide-gray-800"
                    >
                        {recommendations.map((rec, index) => {
                            const styles = typeStyles[rec.recommendation_type] || typeStyles.action;
                            const Icon = typeIcons[rec.recommendation_type] || Sparkles;

                            return (
                                <motion.div
                                    key={rec.id}
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: 10, height: 0 }}
                                    transition={{ delay: index * 0.05 }}
                                    className={`p-4 ${styles.bg} border-l-4 ${styles.border}`}
                                >
                                    <div className="flex items-start gap-3">
                                        <div className={`p-2 rounded-lg bg-white dark:bg-gray-900 shadow-sm ${styles.icon}`}>
                                            <Icon className="w-5 h-5" />
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-2 mb-1">
                                                <h4 className="font-medium">{rec.title}</h4>
                                                <Badge
                                                    variant="outline"
                                                    className={`text-xs ${rec.impact === 'high' ? 'border-red-300 text-red-600' :
                                                        rec.impact === 'medium' ? 'border-amber-300 text-amber-600' :
                                                            'border-gray-300 text-gray-600'
                                                        }`}
                                                >
                                                    {rec.impact} impact
                                                </Badge>
                                                {rec.confidence_score && (
                                                    <Badge variant="outline" className="text-xs">
                                                        {Math.round(rec.confidence_score * 100)}% confidence
                                                    </Badge>
                                                )}
                                            </div>
                                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">{rec.description}</p>
                                            <div className="flex items-center gap-2">
                                                <Button
                                                    size="sm"
                                                    onClick={() => handleAction(rec)}
                                                    className="gap-1"
                                                >
                                                    {rec.action_label}
                                                    <ArrowRight className="w-4 h-4" />
                                                </Button>
                                                {rec.dismissable && (
                                                    <Button
                                                        variant="ghost"
                                                        size="sm"
                                                        onClick={() => dismissRecommendation(rec.id)}
                                                    >
                                                        Dismiss
                                                    </Button>
                                                )}
                                            </div>
                                        </div>
                                        {rec.dismissable && (
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                className="h-7 w-7 text-gray-400 hover:text-gray-600"
                                                onClick={() => dismissRecommendation(rec.id)}
                                            >
                                                <X className="w-4 h-4" />
                                            </Button>
                                        )}
                                    </div>
                                </motion.div>
                            );
                        })}
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Footer */}
            <div className="p-3 bg-white/50 dark:bg-gray-900/50 border-t dark:border-gray-800 text-center">
                <Button variant="link" size="sm" onClick={() => router.push('/ai-insights')}>
                    View all AI insights <ArrowRight className="w-4 h-4 ml-1" />
                </Button>
            </div>
        </motion.div>
    );
}
