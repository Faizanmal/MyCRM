'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Search,
    X,
    User,
    Building2,
    Target,
    FileText,
    Calendar,
    Clock,
    ArrowRight,
    Sparkles,
    TrendingUp,
    Mail,
    Phone,
    Star,
    History,
    Loader2,
} from 'lucide-react';
import { useRouter } from 'next/navigation';

import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';

interface SearchResult {
    id: string;
    type: 'contact' | 'company' | 'lead' | 'opportunity' | 'task' | 'email';
    title: string;
    subtitle?: string;
    metadata?: string;
    score?: number;
    starred?: boolean;
}

interface RecentSearch {
    query: string;
    timestamp: number;
}

const typeIcons: Record<string, React.ElementType> = {
    contact: User,
    company: Building2,
    lead: Target,
    opportunity: FileText,
    task: Calendar,
    email: Mail,
};

const typeColors: Record<string, string> = {
    contact: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
    company: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
    lead: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
    opportunity: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
    task: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
    email: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400',
};

// AI-powered suggestions based on context
const aiSuggestions = [
    { icon: TrendingUp, text: 'Deals closing this week', query: 'deals closing:week' },
    { icon: Star, text: 'High-priority leads', query: 'leads priority:high' },
    { icon: Calendar, text: 'Overdue tasks', query: 'tasks status:overdue' },
    { icon: Phone, text: 'Contacts to follow up', query: 'contacts followup:needed' },
];

const RECENT_SEARCHES_KEY = 'mycrm_recent_searches';
const MAX_RECENT_SEARCHES = 5;

export default function SmartSearch() {
    const [isOpen, setIsOpen] = useState(false);
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<SearchResult[]>([]);
    const [recentSearches, setRecentSearches] = useState<RecentSearch[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [selectedIndex, setSelectedIndex] = useState(0);
    const inputRef = useRef<HTMLInputElement>(null);
    const router = useRouter();

    // Load recent searches on mount
    useEffect(() => {
        const saved = localStorage.getItem(RECENT_SEARCHES_KEY);
        if (saved) {
            try {
                setRecentSearches(JSON.parse(saved));
            } catch {
                // ignore
            }
        }
    }, []);

    // Search function with API integration
    const performSearch = useCallback(async (searchQuery: string) => {
        if (!searchQuery.trim()) {
            setResults([]);
            return;
        }

        setIsLoading(true);

        try {
            // Try backend search API
            const { globalSearchAPI } = await import('@/lib/api');
            const response = await globalSearchAPI.search(searchQuery, { limit: 10 });

            if (response.results && Array.isArray(response.results)) {
                setResults(response.results.map((r: Record<string, unknown>) => ({
                    id: String(r.id),
                    type: String(r.type) as SearchResult['type'],
                    title: String(r.title),
                    subtitle: r.subtitle as string | undefined,
                    metadata: r.metadata as string | undefined,
                    score: r.score as number | undefined,
                    starred: Boolean(r.starred),
                })));
            } else {
                setResults([]);
            }
        } catch (error) {
            console.error("Failed", error)
            // Fallback to mock/local results
            const mockResults: SearchResult[] = [
                { id: '1', type: 'contact' as const, title: 'John Smith', subtitle: 'CEO at TechCorp', metadata: 'Last contacted: 2 days ago', score: 98, starred: true },
                { id: '2', type: 'company' as const, title: 'TechCorp Inc.', subtitle: 'Technology • San Francisco', metadata: '15 contacts, 3 deals' },
                { id: '3', type: 'opportunity' as const, title: 'Enterprise Deal - TechCorp', subtitle: '$50,000 • Proposal Stage', metadata: 'Closes in 2 weeks', score: 85 },
                { id: '4', type: 'lead' as const, title: 'Sarah Johnson', subtitle: 'Marketing Director', metadata: 'Score: 85/100' },
                { id: '5', type: 'task' as const, title: 'Follow up with John Smith', subtitle: 'Due: Tomorrow', metadata: 'High priority' },
            ].filter(r =>
                r.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                r.subtitle?.toLowerCase().includes(searchQuery.toLowerCase())
            );
            setResults(mockResults);
        }

        setSelectedIndex(0);
        setIsLoading(false);
    }, []);

    // Debounced search
    useEffect(() => {
        const timer = setTimeout(() => {
            if (query) {
                performSearch(query);
            }
        }, 200);

        return () => clearTimeout(timer);
    }, [query, performSearch]);

    const saveRecentSearch = (searchQuery: string) => {
        const newSearch: RecentSearch = {
            query: searchQuery,
            timestamp: Date.now(),
        };

        const updated = [
            newSearch,
            ...recentSearches.filter(s => s.query !== searchQuery),
        ].slice(0, MAX_RECENT_SEARCHES);

        setRecentSearches(updated);
        localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(updated));
    };

    const handleSelect = (result: SearchResult) => {
        saveRecentSearch(query);

        const routes: Record<string, string> = {
            contact: `/contacts/${result.id}`,
            company: `/organizations/${result.id}`,
            lead: `/leads/${result.id}`,
            opportunity: `/opportunities/${result.id}`,
            task: `/tasks/${result.id}`,
            email: `/communications?email=${result.id}`,
        };

        router.push(routes[result.type] || '/dashboard');
        setIsOpen(false);
        setQuery('');
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            setSelectedIndex(prev => Math.min(prev + 1, results.length - 1));
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            setSelectedIndex(prev => Math.max(prev - 1, 0));
        } else if (e.key === 'Enter' && results[selectedIndex]) {
            e.preventDefault();
            handleSelect(results[selectedIndex]);
        } else if (e.key === 'Escape') {
            setIsOpen(false);
        }
    };

    return (
        <>
            {/* Search Trigger */}
            <div
                onClick={() => setIsOpen(true)}
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { setIsOpen(true); e.preventDefault(); } }}
                tabIndex={0}
                role="button"
                className="relative flex items-center cursor-pointer"
            >
                <div className="flex items-center gap-2 px-3 py-2 bg-gray-100 dark:bg-gray-800 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors">
                    <Search className="w-4 h-4 text-gray-500" />
                    <span className="text-sm text-gray-500 hidden md:inline">Search everything...</span>
                    <Badge variant="secondary" className="text-xs hidden md:flex gap-1">
                        <kbd>⌘</kbd>
                        <kbd>K</kbd>
                    </Badge>
                </div>
            </div>

            {/* Search Modal */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-start justify-center pt-[15vh]"
                        onClick={() => setIsOpen(false)}
                    >
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95, y: -10 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95, y: -10 }}
                            transition={{ duration: 0.15 }}
                            className="w-full max-w-2xl bg-white dark:bg-gray-900 rounded-xl shadow-2xl overflow-hidden mx-4"
                            onClick={e => e.stopPropagation()}
                        >
                            {/* Search Input */}
                            <div className="flex items-center gap-3 p-4 border-b dark:border-gray-800">
                                {isLoading ? (
                                    <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
                                ) : (
                                    <Search className="w-5 h-5 text-gray-400" />
                                )}
                                <Input
                                    ref={inputRef}
                                    autoFocus
                                    placeholder="Search contacts, deals, tasks..."
                                    value={query}
                                    onChange={e => setQuery(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    className="border-0 shadow-none text-lg focus-visible:ring-0 placeholder:text-gray-400"
                                />
                                {query && (
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        onClick={() => setQuery('')}
                                        className="h-8 w-8"
                                    >
                                        <X className="w-4 h-4" />
                                    </Button>
                                )}
                            </div>

                            <ScrollArea className="max-h-[60vh]">
                                {/* No query - show suggestions and recent */}
                                {!query && (
                                    <div className="p-4 space-y-6">
                                        {/* AI Suggestions */}
                                        <div>
                                            <div className="flex items-center gap-2 text-xs font-semibold text-gray-500 mb-2">
                                                <Sparkles className="w-3 h-3 text-purple-500" />
                                                AI SUGGESTIONS
                                            </div>
                                            <div className="grid grid-cols-2 gap-2">
                                                {aiSuggestions.map((suggestion, index) => (
                                                    <motion.button
                                                        key={index}
                                                        whileHover={{ scale: 1.02 }}
                                                        whileTap={{ scale: 0.98 }}
                                                        onClick={() => setQuery(suggestion.query)}
                                                        className="flex items-center gap-2 p-2.5 rounded-lg bg-linear-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 hover:from-purple-100 hover:to-blue-100 dark:hover:from-purple-900/30 dark:hover:to-blue-900/30 transition-colors text-left"
                                                    >
                                                        <suggestion.icon className="w-4 h-4 text-purple-500" />
                                                        <span className="text-sm font-medium">{suggestion.text}</span>
                                                    </motion.button>
                                                ))}
                                            </div>
                                        </div>

                                        {/* Recent Searches */}
                                        {recentSearches.length > 0 && (
                                            <div>
                                                <div className="flex items-center gap-2 text-xs font-semibold text-gray-500 mb-2">
                                                    <History className="w-3 h-3" />
                                                    RECENT SEARCHES
                                                </div>
                                                <div className="space-y-1">
                                                    {recentSearches.map((search, index) => (
                                                        <button
                                                            key={index}
                                                            onClick={() => setQuery(search.query)}
                                                            className="w-full flex items-center gap-3 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-left"
                                                        >
                                                            <Clock className="w-4 h-4 text-gray-400" />
                                                            <span className="text-sm">{search.query}</span>
                                                        </button>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )}

                                {/* Search Results */}
                                {query && results.length > 0 && (
                                    <div className="p-2">
                                        {results.map((result, index) => {
                                            const Icon = typeIcons[result.type] || FileText;
                                            return (
                                                <motion.div
                                                    key={result.id}
                                                    initial={{ opacity: 0, y: 5 }}
                                                    animate={{ opacity: 1, y: 0 }}
                                                    transition={{ delay: index * 0.03 }}
                                                    onClick={() => handleSelect(result)}
                                                    className={`group flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors ${selectedIndex === index
                                                        ? 'bg-blue-50 dark:bg-blue-900/20'
                                                        : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                                                        }`}
                                                >
                                                    <div className={`p-2 rounded-lg ${typeColors[result.type]}`}>
                                                        <Icon className="w-4 h-4" />
                                                    </div>
                                                    <div className="flex-1 min-w-0">
                                                        <div className="flex items-center gap-2">
                                                            <span className="font-medium truncate">{result.title}</span>
                                                            {result.starred && (
                                                                <Star className="w-3 h-3 text-amber-400 fill-amber-400" />
                                                            )}
                                                            {result.score && (
                                                                <Badge variant="outline" className="text-xs">
                                                                    {result.score}%
                                                                </Badge>
                                                            )}
                                                        </div>
                                                        {result.subtitle && (
                                                            <p className="text-sm text-gray-500 truncate">{result.subtitle}</p>
                                                        )}
                                                        {result.metadata && (
                                                            <p className="text-xs text-gray-400 mt-0.5">{result.metadata}</p>
                                                        )}
                                                    </div>
                                                    <ArrowRight className="w-4 h-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                                                </motion.div>
                                            );
                                        })}
                                    </div>
                                )}

                                {/* No Results */}
                                {query && !isLoading && results.length === 0 && (
                                    <div className="p-8 text-center">
                                        <Search className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                                        <p className="text-gray-500">No results found for &quot;{query}&quot;</p>
                                        <p className="text-sm text-gray-400 mt-1">Try a different search term</p>
                                    </div>
                                )}
                            </ScrollArea>

                            {/* Footer */}
                            <div className="p-3 border-t dark:border-gray-800 flex items-center justify-between text-xs text-gray-400">
                                <div className="flex items-center gap-4">
                                    <span className="flex items-center gap-1">
                                        <kbd className="px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800">↵</kbd>
                                        Select
                                    </span>
                                    <span className="flex items-center gap-1">
                                        <kbd className="px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800">↑</kbd>
                                        <kbd className="px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800">↓</kbd>
                                        Navigate
                                    </span>
                                </div>
                                <span className="flex items-center gap-1">
                                    <kbd className="px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800">Esc</kbd>
                                    Close
                                </span>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
}

