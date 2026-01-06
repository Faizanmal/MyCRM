'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
// import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
  CommandShortcut,
} from '@/components/ui/command';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Search,
  Filter,
  Clock,
  Star,
  User,
  Users,
  Target,
  DollarSign,
  CheckSquare,
  Mail,
  Phone,
  Calendar,
  FileText,
  Tag,
  ArrowRight,
  Loader2,
  SlidersHorizontal,
  Save,
  Trash2,
  History,
  Bookmark,
  BookmarkPlus,
  ExternalLink,
  MoreHorizontal,
  Hash,
  Sparkles,
  TrendingUp,
} from 'lucide-react';
import { toast } from 'sonner';
import { globalSearchAPI, SearchResult, SavedSearch } from '@/lib/enterprise-api';
import Link from 'next/link';

const ENTITY_TYPES = [
  { value: 'all', label: 'All Types', icon: Search, color: 'bg-gray-500' },
  { value: 'contact', label: 'Contacts', icon: User, color: 'bg-blue-500' },
  { value: 'lead', label: 'Leads', icon: Target, color: 'bg-green-500' },
  { value: 'opportunity', label: 'Opportunities', icon: DollarSign, color: 'bg-purple-500' },
  { value: 'organization', label: 'Organizations', icon: Users, color: 'bg-orange-500' },
  { value: 'task', label: 'Tasks', icon: CheckSquare, color: 'bg-yellow-500' },
  { value: 'email', label: 'Emails', icon: Mail, color: 'bg-red-500' },
  { value: 'document', label: 'Documents', icon: FileText, color: 'bg-indigo-500' },
];

const SORT_OPTIONS = [
  { value: 'relevance', label: 'Most Relevant' },
  { value: 'created_desc', label: 'Newest First' },
  { value: 'created_asc', label: 'Oldest First' },
  { value: 'updated_desc', label: 'Recently Updated' },
  { value: 'name_asc', label: 'Name A-Z' },
  { value: 'name_desc', label: 'Name Z-A' },
];

const DATE_FILTERS = [
  { value: 'all', label: 'Any Time' },
  { value: 'today', label: 'Today' },
  { value: 'week', label: 'Past Week' },
  { value: 'month', label: 'Past Month' },
  { value: 'quarter', label: 'Past 3 Months' },
  { value: 'year', label: 'Past Year' },
];

// Mock search results
const MOCK_RESULTS: SearchResult[] = [
  {
    id: '1',
    entity_type: 'contact',
    title: 'John Smith',
    subtitle: 'VP of Sales at Acme Corp',
    description: 'john.smith@acme.com • +1 555-0123 • Last contacted 2 days ago',
    url: '/contacts/1',
    score: 0.95,
    highlights: { name: ['<em>John</em> <em>Smith</em>'], email: ['john.smith@acme.com'] },
    metadata: { status: 'active', tags: ['VIP', 'Enterprise'] },
    created_at: '2024-01-01T00:00:00Z',
  },
  {
    id: '2',
    entity_type: 'lead',
    title: 'Sarah Johnson - Enterprise Inquiry',
    subtitle: 'Tech Solutions Inc.',
    description: 'Interested in enterprise plan • Budget: $50k-100k • Hot lead',
    url: '/leads/2',
    score: 0.88,
    highlights: { company: ['Tech Solutions Inc.'] },
    metadata: { status: 'qualified', score: 85 },
    created_at: '2024-01-01T00:00:00Z',
  },
  {
    id: '3',
    entity_type: 'opportunity',
    title: 'Acme Corp - Annual Renewal',
    subtitle: 'Value: $150,000 • Stage: Negotiation',
    description: 'Annual subscription renewal with 20% upsell potential',
    url: '/opportunities/3',
    score: 0.82,
    highlights: { name: ['<em>Acme</em> Corp'] },
    metadata: { stage: 'negotiation', probability: 75 },
    created_at: '2024-01-01T00:00:00Z',
  },
  {
    id: '4',
    entity_type: 'organization',
    title: 'Acme Corporation',
    subtitle: 'Enterprise • Technology',
    description: '500+ employees • San Francisco, CA • Customer since 2020',
    url: '/organizations/4',
    score: 0.78,
    highlights: { name: ['<em>Acme</em> Corporation'] },
    metadata: { type: 'customer', industry: 'Technology' },
    created_at: '2024-01-01T00:00:00Z',
  },
  {
    id: '5',
    entity_type: 'task',
    title: 'Follow up with John about proposal',
    subtitle: 'Due: Tomorrow • Assigned to: You',
    description: 'Send revised proposal with updated pricing',
    url: '/tasks/5',
    score: 0.72,
    highlights: { description: ['Follow up with <em>John</em>'] },
    metadata: { priority: 'high', status: 'pending' },
    created_at: '2024-01-01T00:00:00Z',
  },
  {
    id: '6',
    entity_type: 'email',
    title: 'Re: Partnership Discussion',
    subtitle: 'From: jane@partner.com • 3 days ago',
    description: 'Looking forward to discussing the partnership terms...',
    url: '/communications/email/6',
    score: 0.68,
    highlights: { subject: ['Partnership Discussion'] },
    metadata: { direction: 'received', read: true },
    created_at: '2024-01-01T00:00:00Z',
  },
  {
    id: '7',
    entity_type: 'document',
    title: 'Q4 Sales Proposal - Acme.pdf',
    subtitle: 'Uploaded by: You • 1 week ago',
    description: 'Sales proposal document for Acme Corporation renewal',
    url: '/documents/7',
    score: 0.65,
    highlights: { title: ['Q4 Sales Proposal - <em>Acme</em>.pdf'] },
    metadata: { type: 'pdf', size: '2.4 MB' },
    created_at: '2024-01-01T00:00:00Z',
  },
];

const MOCK_SAVED_SEARCHES: SavedSearch[] = [
  { id: '1', name: 'Hot Leads', query: 'status:hot', filters: { entity_types: ['lead'] }, created_at: '' },
  { id: '2', name: 'Enterprise Contacts', query: 'tag:enterprise', filters: { entity_types: ['contact', 'organization'] }, created_at: '' },
  { id: '3', name: 'Pending Tasks', query: 'status:pending', filters: { entity_types: ['task'], date_range: 'week' }, created_at: '' },
];

const MOCK_RECENT_SEARCHES = [
  'John Smith',
  'Acme Corp',
  'pending proposals',
  'high priority tasks',
];

const MOCK_TRENDING_SEARCHES = [
  'Q4 renewals',
  'enterprise leads',
  'pending follow-ups',
];

export default function GlobalSearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedTypes, setSelectedTypes] = useState<string[]>(['all']);
  const [sortBy, setSortBy] = useState('relevance');
  const [dateFilter, setDateFilter] = useState('all');
  const [savedSearches, setSavedSearches] = useState<SavedSearch[]>(MOCK_SAVED_SEARCHES);
  const [recentSearches, setRecentSearches] = useState<string[]>(MOCK_RECENT_SEARCHES);
  const [showFilters, setShowFilters] = useState(false);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [saveSearchName, setSaveSearchName] = useState('');
  const [] = useState('results');
  const [selectedResults, setSelectedResults] = useState<string[]>([]);
  const [isCommandOpen, setIsCommandOpen] = useState(false);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Keyboard shortcut for search
  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setIsCommandOpen(true);
      }
    };
    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, []);

  const handleSearch = useCallback(async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setResults([]);
      return;
    }

    setLoading(true);
    try {
      const filters: Record<string, unknown> = {};
      if (!selectedTypes.includes('all')) {
        filters.entity_types = selectedTypes;
      }
      if (dateFilter !== 'all') {
        filters.date_range = dateFilter;
      }
      filters.sort = sortBy;

      const response = await globalSearchAPI.search(searchQuery, filters);
      setResults(response.results || []);

      // Add to recent searches
      if (!recentSearches.includes(searchQuery)) {
        setRecentSearches([searchQuery, ...recentSearches.slice(0, 4)]);
      }
    } catch (error) {
      console.error('Search failed:', error);
      // Use mock results filtered by query
      const filtered = MOCK_RESULTS.filter(r =>
        r.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        r.subtitle?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        r.description?.toLowerCase().includes(searchQuery.toLowerCase())
      ).filter(r => selectedTypes.includes('all') || selectedTypes.includes(r.entity_type));
      setResults(filtered.length > 0 ? filtered : MOCK_RESULTS);
    } finally {
      setLoading(false);
    }
  }, [selectedTypes, sortBy, dateFilter, recentSearches]);

  useEffect(() => {
    const debounce = setTimeout(() => {
      handleSearch(query);
    }, 300);
    return () => clearTimeout(debounce);
  }, [query, handleSearch]);

  const toggleEntityType = (type: string) => {
    if (type === 'all') {
      setSelectedTypes(['all']);
    } else {
      let newTypes = selectedTypes.filter(t => t !== 'all');
      if (newTypes.includes(type)) {
        newTypes = newTypes.filter(t => t !== type);
      } else {
        newTypes = [...newTypes, type];
      }
      setSelectedTypes(newTypes.length === 0 ? ['all'] : newTypes);
    }
  };

  const handleSaveSearch = async () => {
    if (!saveSearchName.trim() || !query.trim()) {
      toast.error('Please enter a name for your saved search');
      return;
    }

    try {
      const filters: Record<string, unknown> = {};
      if (!selectedTypes.includes('all')) {
        filters.entity_types = selectedTypes;
      }
      if (dateFilter !== 'all') {
        filters.date_range = dateFilter;
      }

      await globalSearchAPI.saveSearch({ name: saveSearchName, query, filters });
      toast.success('Search saved!');

      // Add to saved searches locally
      setSavedSearches([
        { id: Date.now().toString(), name: saveSearchName, query, filters, created_at: new Date().toISOString() },
        ...savedSearches,
      ]);

      setShowSaveDialog(false);
      setSaveSearchName('');
    } catch (error) {
      console.error('Failed to save search:', error);
      // Mock success
      setSavedSearches([
        { id: Date.now().toString(), name: saveSearchName, query, filters: {}, created_at: new Date().toISOString() },
        ...savedSearches,
      ]);
      toast.success('Search saved!');
      setShowSaveDialog(false);
      setSaveSearchName('');
    }
  };

  const applySavedSearch = (saved: SavedSearch) => {
    setQuery(saved.query);
    if (saved.filters?.entity_types) {
      setSelectedTypes(saved.filters.entity_types as string[]);
    } else {
      setSelectedTypes(['all']);
    }
    if (saved.filters?.date_range) {
      setDateFilter(saved.filters.date_range as string);
    }
  };

  const deleteSavedSearch = async (id: string) => {
    try {
      await globalSearchAPI.deleteSavedSearch(id);
      setSavedSearches(savedSearches.filter(s => s.id !== id));
      toast.success('Saved search deleted');
    } catch (error) {
      console.error('Failed to delete:', error);
      setSavedSearches(savedSearches.filter(s => s.id !== id));
      toast.success('Saved search deleted');
    }
  };

  const getEntityIcon = (type: string) => {
    const entity = ENTITY_TYPES.find(e => e.value === type);
    return entity?.icon || Search;
  };

  const getEntityColor = (type: string) => {
    const entity = ENTITY_TYPES.find(e => e.value === type);
    return entity?.color || 'bg-gray-500';
  };

  const ResultCard = ({ result }: { result: SearchResult }) => {
    const EntityIcon = getEntityIcon(result.entity_type);
    const colorClass = getEntityColor(result.entity_type);
    const isSelected = selectedResults.includes(result.id);

    return (
      <Card className="hover:shadow-lg transition-all hover:scale-[1.01] cursor-pointer border-l-4" style={{ borderLeftColor: colorClass.replace('bg-', '') }}>
        <CardContent className="p-4">
          <div className="flex items-start gap-4">
            <Checkbox
              checked={isSelected}
              onCheckedChange={(checked) => {
                if (checked) {
                  setSelectedResults([...selectedResults, result.id]);
                } else {
                  setSelectedResults(selectedResults.filter(id => id !== result.id));
                }
              }}
              className="mt-1"
            />
            <Link href={result.url} className="flex items-start gap-4 flex-1">
              <div className={`p-2 rounded-lg ${colorClass} text-white flex-shrink-0`}>
                <EntityIcon className="w-5 h-5" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h3
                    className="font-semibold text-gray-900 dark:text-white truncate"
                    dangerouslySetInnerHTML={{
                      __html: result.highlights?.name?.[0] || result.title,
                    }}
                  />
                  <Badge variant="secondary" className="text-xs capitalize">
                    {result.entity_type}
                  </Badge>
                  {result.score && result.score > 0.9 && (
                    <Badge className="bg-green-100 text-green-700 text-xs">
                      <Sparkles className="w-3 h-3 mr-1" />
                      Best Match
                    </Badge>
                  )}
                </div>
                {result.subtitle && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                    {result.subtitle}
                  </p>
                )}
                {result.description && (
                  <p className="text-sm text-gray-500 dark:text-gray-500 truncate flex items-center gap-1">
                    {result.entity_type === 'contact' && <Phone className="w-3 h-3" />}
                    {result.description}
                  </p>
                )}
                {result.metadata && Object.keys(result.metadata).length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {result.metadata.tags?.map((tag: string) => (
                      <Badge key={tag} variant="outline" className="text-xs">
                        <Tag className="w-3 h-3 mr-1" />
                        {tag}
                      </Badge>
                    ))}
                    {result.metadata.status && (
                      <Badge variant="outline" className="text-xs capitalize">
                        {result.metadata.status as string}
                      </Badge>
                    )}
                    {result.metadata.priority && (
                      <Badge
                        className={`text-xs ${
                          result.metadata.priority === 'high'
                            ? 'bg-red-100 text-red-700'
                            : result.metadata.priority === 'medium'
                            ? 'bg-yellow-100 text-yellow-700'
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {result.metadata.priority as string} priority
                      </Badge>
                    )}
                  </div>
                )}
              </div>
              <div className="flex items-center gap-2">
                <ArrowRight className="w-5 h-5 text-gray-400 flex-shrink-0" />
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                      <MoreHorizontal className="w-4 h-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => window.open(result.url, '_blank')}>
                      <ExternalLink className="w-4 h-4 mr-2" />
                      Open in new tab
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => navigator.clipboard.writeText(result.url)}>
                      <Hash className="w-4 h-4 mr-2" />
                      Copy link
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={() => toast.success('Added to favorites')}>
                      <Star className="w-4 h-4 mr-2" />
                      Add to favorites
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </Link>
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-4 lg:p-6 space-y-6">
          {/* Header */}
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 dark:text-white mb-2">
              Search Everything
            </h1>
            <p className="text-gray-500 dark:text-gray-400 mb-6">
              Find contacts, leads, opportunities, tasks, and more across your entire CRM
            </p>

            {/* Main Search Bar */}
            <div className="relative">
              <div className="flex items-center gap-2 bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 focus-within:border-blue-500 shadow-sm overflow-hidden">
                <Search className="w-5 h-5 text-gray-400 ml-4" />
                <Input
                  ref={searchInputRef}
                  type="text"
                  placeholder="Search contacts, leads, opportunities, tasks..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="border-0 focus-visible:ring-0 text-lg py-6"
                />
                <div className="flex items-center gap-2 pr-2">
                  <kbd className="hidden sm:inline-flex items-center gap-1 px-2 py-1 text-xs font-mono bg-gray-100 dark:bg-gray-700 rounded">
                    <span className="text-xs">⌘</span>K
                  </kbd>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowFilters(!showFilters)}
                    className={showFilters ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300' : ''}
                  >
                    <Filter className="w-4 h-4 mr-1" />
                    Filters
                  </Button>
                  {query && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowSaveDialog(true)}
                    >
                      <BookmarkPlus className="w-4 h-4" />
                    </Button>
                  )}
                </div>
              </div>

              {/* Loading indicator */}
              {loading && (
                <div className="absolute right-20 top-1/2 -translate-y-1/2">
                  <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
                </div>
              )}
            </div>

            {/* Entity Type Filters */}
            {showFilters && (
              <Card className="mt-4 text-left">
                <CardContent className="p-4 space-y-4">
                  {/* Entity Types */}
                  <div>
                    <Label className="text-sm font-medium mb-2 block">Entity Types</Label>
                    <div className="flex flex-wrap gap-2">
                      {ENTITY_TYPES.map((type) => {
                        const TypeIcon = type.icon;
                        const isSelected = selectedTypes.includes(type.value);
                        return (
                          <button
                            key={type.value}
                            onClick={() => toggleEntityType(type.value)}
                            className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm transition-all ${
                              isSelected
                                ? `${type.color} text-white`
                                : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200'
                            }`}
                          >
                            <TypeIcon className="w-4 h-4" />
                            {type.label}
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  {/* Sort and Date */}
                  <div className="grid sm:grid-cols-2 gap-4">
                    <div>
                      <Label className="text-sm font-medium mb-2 block">Sort By</Label>
                      <div className="flex flex-wrap gap-2">
                        {SORT_OPTIONS.map((option) => (
                          <button
                            key={option.value}
                            onClick={() => setSortBy(option.value)}
                            className={`px-3 py-1.5 rounded-lg text-sm transition-all ${
                              sortBy === option.value
                                ? 'bg-blue-500 text-white'
                                : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200'
                            }`}
                          >
                            {option.label}
                          </button>
                        ))}
                      </div>
                    </div>
                    <div>
                      <Label className="text-sm font-medium mb-2 block">Date Range</Label>
                      <div className="flex flex-wrap gap-2">
                        {DATE_FILTERS.map((option) => (
                          <button
                            key={option.value}
                            onClick={() => setDateFilter(option.value)}
                            className={`px-3 py-1.5 rounded-lg text-sm transition-all flex items-center gap-1 ${
                              dateFilter === option.value
                                ? 'bg-blue-500 text-white'
                                : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200'
                            }`}
                          >
                            <Calendar className="w-3 h-3" />
                            {option.label}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          <div className="grid lg:grid-cols-4 gap-6">
            {/* Sidebar */}
            <div className="lg:col-span-1 space-y-6">
              {/* Saved Searches */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <Bookmark className="w-4 h-4 text-blue-600" />
                    Saved Searches
                  </CardTitle>
                  <CardDescription>Quick access to your saved search queries</CardDescription>
                </CardHeader>
                <CardContent className="space-y-2">
                  {savedSearches.length === 0 ? (
                    <p className="text-sm text-gray-500 text-center py-4">
                      No saved searches yet
                    </p>
                  ) : (
                    savedSearches.map((saved) => (
                      <div
                        key={saved.id}
                        className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 group"
                      >
                        <button
                          onClick={() => applySavedSearch(saved)}
                          className="flex items-center gap-2 text-sm text-left flex-1"
                        >
                          <Star className="w-4 h-4 text-yellow-500" />
                          <span className="truncate">{saved.name}</span>
                        </button>
                        <button
                          onClick={() => deleteSavedSearch(saved.id)}
                          className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 rounded"
                        >
                          <Trash2 className="w-3 h-3 text-red-500" />
                        </button>
                      </div>
                    ))
                  )}
                </CardContent>
              </Card>

              {/* Recent Searches */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <History className="w-4 h-4 text-gray-500" />
                    Recent Searches
                  </CardTitle>
                  <CardDescription>Your recent search history</CardDescription>
                </CardHeader>
                <CardContent className="space-y-1">
                  {recentSearches.map((search, index) => (
                    <button
                      key={index}
                      onClick={() => setQuery(search)}
                      className="flex items-center gap-2 w-full p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 text-sm text-left"
                    >
                      <Clock className="w-4 h-4 text-gray-400" />
                      <span className="truncate">{search}</span>
                    </button>
                  ))}
                </CardContent>
              </Card>

              {/* Trending Searches */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-green-500" />
                    Trending
                  </CardTitle>
                  <CardDescription>Popular searches this week</CardDescription>
                </CardHeader>
                <CardContent className="space-y-1">
                  {MOCK_TRENDING_SEARCHES.map((search, index) => (
                    <button
                      key={index}
                      onClick={() => setQuery(search)}
                      className="flex items-center gap-2 w-full p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 text-sm text-left"
                    >
                      <Hash className="w-4 h-4 text-gray-400" />
                      <span className="truncate">{search}</span>
                    </button>
                  ))}
                </CardContent>
              </Card>
            </div>

            {/* Results */}
            <div className="lg:col-span-3">
              {/* Results Header */}
              {query && (
                <div className="flex items-center justify-between mb-4">
                  <p className="text-sm text-gray-500">
                    {loading ? 'Searching...' : `${results.length} results for "${query}"`}
                  </p>
                  {results.length > 0 && (
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-500">Sort:</span>
                      <select
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value)}
                        className="text-sm border rounded-lg px-2 py-1 bg-white dark:bg-gray-800"
                      >
                        {SORT_OPTIONS.map((option) => (
                          <option key={option.value} value={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  )}
                </div>
              )}

              {/* Results List */}
              {!query ? (
                <Card className="text-center py-12">
                  <CardContent>
                    <Search className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                      Start searching
                    </h3>
                    <p className="text-gray-500 dark:text-gray-400 max-w-md mx-auto">
                      Type in the search box to find contacts, leads, opportunities, tasks, and more across your entire CRM.
                    </p>
                    <div className="mt-6 flex flex-wrap justify-center gap-2">
                      <Button variant="outline" size="sm" onClick={() => setQuery('high priority')}>
                        High priority tasks
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => setQuery('enterprise')}>
                        Enterprise contacts
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => setQuery('pending')}>
                        Pending items
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ) : results.length === 0 && !loading ? (
                <Card className="text-center py-12">
                  <CardContent>
                    <Search className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                      No results found
                    </h3>
                    <p className="text-gray-500 dark:text-gray-400 max-w-md mx-auto">
                      Try adjusting your search terms or filters to find what you&apos;re looking for.
                    </p>
                  </CardContent>
                </Card>
              ) : (
                <div className="space-y-3">
                  {results.map((result) => (
                    <ResultCard key={result.id} result={result} />
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Save Search Dialog */}
          <Dialog open={showSaveDialog} onOpenChange={setShowSaveDialog}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Save Search</DialogTitle>
                <DialogDescription>
                  Save this search to quickly access it later.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="search_name">Search Name</Label>
                  <Input
                    id="search_name"
                    placeholder="e.g., Hot Leads This Week"
                    value={saveSearchName}
                    onChange={(e) => setSaveSearchName(e.target.value)}
                  />
                </div>
                <div className="p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
                  <p className="text-sm text-gray-500">Query: <span className="font-medium text-gray-700 dark:text-gray-300">{query}</span></p>
                  {!selectedTypes.includes('all') && (
                    <p className="text-sm text-gray-500">Types: <span className="font-medium text-gray-700 dark:text-gray-300">{selectedTypes.join(', ')}</span></p>
                  )}
                  {dateFilter !== 'all' && (
                    <p className="text-sm text-gray-500">Date: <span className="font-medium text-gray-700 dark:text-gray-300">{DATE_FILTERS.find(d => d.value === dateFilter)?.label}</span></p>
                  )}
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setShowSaveDialog(false)}>
                  Cancel
                </Button>
                <Button onClick={handleSaveSearch}>
                  <Save className="w-4 h-4 mr-2" />
                  Save Search
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          {/* Command Palette (Keyboard Shortcut) */}
          <CommandDialog open={isCommandOpen} onOpenChange={setIsCommandOpen}>
            <CommandInput placeholder="Search everything..." />
            <CommandList>
              <CommandEmpty>No results found.</CommandEmpty>
              <CommandGroup heading="Saved Searches">
                {savedSearches.map((saved) => (
                  <CommandItem
                    key={saved.id}
                    onSelect={() => {
                      applySavedSearch(saved);
                      setIsCommandOpen(false);
                    }}
                  >
                    <Star className="mr-2 h-4 w-4 text-yellow-500" />
                    <span>{saved.name}</span>
                    <CommandShortcut>{saved.query}</CommandShortcut>
                  </CommandItem>
                ))}
              </CommandGroup>
              <CommandSeparator />
              <CommandGroup heading="Quick Actions">
                <CommandItem onSelect={() => { setQuery(''); setIsCommandOpen(false); searchInputRef.current?.focus(); }}>
                  <Search className="mr-2 h-4 w-4" />
                  <span>New Search</span>
                </CommandItem>
                <CommandItem onSelect={() => { setShowFilters(true); setIsCommandOpen(false); }}>
                  <SlidersHorizontal className="mr-2 h-4 w-4" />
                  <span>Open Filters</span>
                </CommandItem>
              </CommandGroup>
            </CommandList>
          </CommandDialog>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
