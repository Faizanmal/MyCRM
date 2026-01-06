'use client';

import React, { createContext, useContext, useState, useEffect, useCallback, useRef, ReactNode } from 'react';
import { useQueryClient } from '@tanstack/react-query';

// Types
interface CacheEntry {
  key: string;
  data: unknown;
  timestamp: number;
  ttl: number;
  tags: string[];
  size: number;
  hitCount: number;
}

interface PrefetchHint {
  url: string;
  priority: 'high' | 'low';
  delayMs: number;
}

interface CacheStats {
  totalEntries: number;
  totalSize: number;
  hitRate: number;
  missRate: number;
  avgHitTime: number;
  avgMissTime: number;
}

interface CacheContextType {
  // Cache operations
  get: <T>(key: string) => T | null;
  set: <T>(key: string, value: T, options?: CacheOptions) => void;
  invalidate: (key: string) => void;
  invalidateByTag: (tag: string) => void;
  invalidateByPrefix: (prefix: string) => void;
  clear: () => void;
  
  // Prefetching
  prefetch: (url: string, options?: PrefetchOptions) => Promise<void>;
  prefetchMultiple: (urls: string[]) => Promise<void>;
  registerPrefetchHints: (currentUrl: string) => void;
  
  // Stale-while-revalidate
  getWithRevalidate: <T>(key: string, fetcher: () => Promise<T>, options?: SWROptions) => Promise<T>;
  
  // Stats and debugging
  getStats: () => CacheStats;
  getEntries: () => CacheEntry[];
  isOnline: boolean;
  
  // Configuration
  setDefaultTTL: (ttl: number) => void;
  enableOfflineMode: () => void;
  disableOfflineMode: () => void;
}

interface CacheOptions {
  ttl?: number; // Time to live in ms
  tags?: string[];
  priority?: 'high' | 'low';
}

interface PrefetchOptions {
  priority?: 'high' | 'low';
  delay?: number;
}

interface SWROptions {
  ttl?: number;
  staleTTL?: number;
  revalidateOnFocus?: boolean;
  revalidateOnReconnect?: boolean;
}

// Constants
const DEFAULT_TTL = 5 * 60 * 1000; // 5 minutes
// const DEFAULT_STALE_TTL = 60 * 1000; // 1 minute
const MAX_CACHE_SIZE = 50 * 1024 * 1024; // 50MB

// Context
const CacheContext = createContext<CacheContextType | undefined>(undefined);

// Cache storage implementation
class CacheStorage {
  private cache: Map<string, CacheEntry> = new Map();
  private tagIndex: Map<string, Set<string>> = new Map();
  private hits = 0;
  private misses = 0;
  private totalHitTime = 0;
  private totalMissTime = 0;
  private currentSize = 0;

  get(key: string): unknown | null {
    const start = performance.now();
    const entry = this.cache.get(key);
    
    if (!entry) {
      this.misses++;
      this.totalMissTime += performance.now() - start;
      return null;
    }
    
    // Check expiration
    if (Date.now() > entry.timestamp + entry.ttl) {
      this.delete(key);
      this.misses++;
      this.totalMissTime += performance.now() - start;
      return null;
    }
    
    entry.hitCount++;
    this.hits++;
    this.totalHitTime += performance.now() - start;
    return entry.data;
  }

  getStale(key: string): { data: unknown; isStale: boolean } | null {
    const entry = this.cache.get(key);
    
    if (!entry) {
      return null;
    }
    
    const isStale = Date.now() > entry.timestamp + entry.ttl;
    return { data: entry.data, isStale };
  }

  set(key: string, data: unknown, ttl: number, tags: string[] = []): void {
    const size = this.estimateSize(data);
    
    // Evict if necessary
    while (this.currentSize + size > MAX_CACHE_SIZE && this.cache.size > 0) {
      this.evictLRU();
    }
    
    // Remove old entry if exists
    if (this.cache.has(key)) {
      this.delete(key);
    }
    
    const entry: CacheEntry = {
      key,
      data,
      timestamp: Date.now(),
      ttl,
      tags,
      size,
      hitCount: 0,
    };
    
    this.cache.set(key, entry);
    this.currentSize += size;
    
    // Update tag index
    for (const tag of tags) {
      if (!this.tagIndex.has(tag)) {
        this.tagIndex.set(tag, new Set());
      }
      this.tagIndex.get(tag)!.add(key);
    }
  }

  delete(key: string): void {
    const entry = this.cache.get(key);
    if (!entry) return;
    
    this.currentSize -= entry.size;
    
    // Remove from tag index
    for (const tag of entry.tags) {
      const tagSet = this.tagIndex.get(tag);
      if (tagSet) {
        tagSet.delete(key);
        if (tagSet.size === 0) {
          this.tagIndex.delete(tag);
        }
      }
    }
    
    this.cache.delete(key);
  }

  invalidateByTag(tag: string): void {
    const keys = this.tagIndex.get(tag);
    if (!keys) return;
    
    for (const key of keys) {
      this.delete(key);
    }
  }

  invalidateByPrefix(prefix: string): void {
    for (const key of this.cache.keys()) {
      if (key.startsWith(prefix)) {
        this.delete(key);
      }
    }
  }

  clear(): void {
    this.cache.clear();
    this.tagIndex.clear();
    this.currentSize = 0;
    this.hits = 0;
    this.misses = 0;
  }

  getStats(): CacheStats {
    const total = this.hits + this.misses;
    return {
      totalEntries: this.cache.size,
      totalSize: this.currentSize,
      hitRate: total > 0 ? this.hits / total : 0,
      missRate: total > 0 ? this.misses / total : 0,
      avgHitTime: this.hits > 0 ? this.totalHitTime / this.hits : 0,
      avgMissTime: this.misses > 0 ? this.totalMissTime / this.misses : 0,
    };
  }

  getEntries(): CacheEntry[] {
    return Array.from(this.cache.values());
  }

  private evictLRU(): void {
    let oldest: CacheEntry | null = null;
    
    for (const entry of this.cache.values()) {
      if (!oldest || entry.timestamp < oldest.timestamp) {
        oldest = entry;
      }
    }
    
    if (oldest) {
      this.delete(oldest.key);
    }
  }

  private estimateSize(data: unknown): number {
    try {
      return new Blob([JSON.stringify(data)]).size;
    } catch {
      return 1024; // Default estimate
    }
  }
}

// Provider Component
interface CacheProviderProps {
  children: ReactNode;
  defaultTTL?: number;
}

export function CacheProvider({ children, defaultTTL = DEFAULT_TTL }: CacheProviderProps) {
  const queryClient = useQueryClient();
  const cacheRef = useRef(new CacheStorage());
  const [isOnline, setIsOnline] = useState(true);
  const [currentTTL, setCurrentTTL] = useState(defaultTTL);
  const pendingPrefetches = useRef<Set<string>>(new Set());
  const prefetchQueue = useRef<PrefetchHint[]>([]);
  const offlineMode = useRef(false);

  // Monitor online status
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    setIsOnline(navigator.onLine);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Process prefetch queue
  useEffect(() => {
    const processPrefetchQueue = () => {
      if (prefetchQueue.current.length === 0) return;
      
      const hint = prefetchQueue.current.shift();
      if (!hint || pendingPrefetches.current.has(hint.url)) return;
      
      pendingPrefetches.current.add(hint.url);
      
      setTimeout(async () => {
        try {
          const response = await fetch(hint.url, {
            headers: { 'X-Prefetch': 'true' },
          });
          
          if (response.ok) {
            const data = await response.json();
            cacheRef.current.set(hint.url, data, currentTTL, ['prefetch']);
          }
        } catch (error) {
          console.warn('Prefetch failed:', hint.url, error);
        } finally {
          pendingPrefetches.current.delete(hint.url);
        }
      }, hint.delayMs);
    };

    const interval = setInterval(processPrefetchQueue, 100);
    return () => clearInterval(interval);
  }, [currentTTL]);

  // Cache operations
  const get = useCallback(<T,>(key: string): T | null => {
    return cacheRef.current.get(key) as T | null;
  }, []);

  const set = useCallback(<T,>(key: string, value: T, options?: CacheOptions): void => {
    const ttl = options?.ttl ?? currentTTL;
    const tags = options?.tags ?? [];
    cacheRef.current.set(key, value, ttl, tags);
  }, [currentTTL]);

  const invalidate = useCallback((key: string): void => {
    cacheRef.current.delete(key);
    queryClient.invalidateQueries({ queryKey: [key] });
  }, [queryClient]);

  const invalidateByTag = useCallback((tag: string): void => {
    cacheRef.current.invalidateByTag(tag);
  }, []);

  const invalidateByPrefix = useCallback((prefix: string): void => {
    cacheRef.current.invalidateByPrefix(prefix);
  }, []);

  const clear = useCallback((): void => {
    cacheRef.current.clear();
    queryClient.clear();
  }, [queryClient]);

  // Prefetching
  const prefetch = useCallback(async (url: string, options?: PrefetchOptions): Promise<void> => {
    const hint: PrefetchHint = {
      url,
      priority: options?.priority ?? 'low',
      delayMs: options?.delay ?? 100,
    };
    
    if (hint.priority === 'high') {
      prefetchQueue.current.unshift(hint);
    } else {
      prefetchQueue.current.push(hint);
    }
  }, []);

  const prefetchMultiple = useCallback(async (urls: string[]): Promise<void> => {
    for (const url of urls) {
      await prefetch(url);
    }
  }, [prefetch]);

  const registerPrefetchHints = useCallback((currentUrl: string): void => {
    // Define prefetch rules based on current URL
    const hints: PrefetchHint[] = [];
    
    if (currentUrl.includes('/contacts')) {
      hints.push({ url: '/api/contacts/recent', priority: 'low', delayMs: 500 });
      hints.push({ url: '/api/contacts/stats', priority: 'low', delayMs: 1000 });
    } else if (currentUrl.includes('/deals')) {
      hints.push({ url: '/api/deals/pipeline', priority: 'low', delayMs: 500 });
      hints.push({ url: '/api/deals/stats', priority: 'low', delayMs: 1000 });
    } else if (currentUrl.includes('/dashboard')) {
      hints.push({ url: '/api/dashboard/widgets', priority: 'high', delayMs: 0 });
      hints.push({ url: '/api/activities/recent', priority: 'low', delayMs: 500 });
    }
    
    prefetchQueue.current.push(...hints);
  }, []);

  // Stale-while-revalidate
  const getWithRevalidate = useCallback(async <T,>(
    key: string,
    fetcher: () => Promise<T>,
    options?: SWROptions
  ): Promise<T> => {
    const ttl = options?.ttl ?? currentTTL;
    // const staleTTL = options?.staleTTL ?? DEFAULT_STALE_TTL;
    
    const cached = cacheRef.current.getStale(key);
    
    if (cached) {
      if (cached.isStale) {
        // Return stale data, revalidate in background
        fetcher().then(data => {
          cacheRef.current.set(key, data, ttl);
        }).catch(console.error);
        
        return cached.data as T;
      }
      
      return cached.data as T;
    }
    
    // Cache miss - fetch fresh data
    const data = await fetcher();
    cacheRef.current.set(key, data, ttl);
    return data;
  }, [currentTTL]);

  // Stats and debugging
  const getStats = useCallback((): CacheStats => {
    return cacheRef.current.getStats();
  }, []);

  const getEntries = useCallback((): CacheEntry[] => {
    return cacheRef.current.getEntries();
  }, []);

  // Configuration
  const setDefaultTTL = useCallback((ttl: number): void => {
    setCurrentTTL(ttl);
  }, []);

  const enableOfflineMode = useCallback((): void => {
    offlineMode.current = true;
  }, []);

  const disableOfflineMode = useCallback((): void => {
    offlineMode.current = false;
  }, []);

  const value: CacheContextType = {
    get,
    set,
    invalidate,
    invalidateByTag,
    invalidateByPrefix,
    clear,
    prefetch,
    prefetchMultiple,
    registerPrefetchHints,
    getWithRevalidate,
    getStats,
    getEntries,
    isOnline,
    setDefaultTTL,
    enableOfflineMode,
    disableOfflineMode,
  };

  return (
    <CacheContext.Provider value={value}>
      {children}
    </CacheContext.Provider>
  );
}

// Hooks
export function useCache(): CacheContextType {
  const context = useContext(CacheContext);
  if (!context) {
    throw new Error('useCache must be used within CacheProvider');
  }
  return context;
}

export function useCachedFetch<T>(
  key: string,
  fetcher: () => Promise<T>,
  options?: SWROptions
): { data: T | null; isLoading: boolean; error: Error | null; refetch: () => Promise<void> } {
  const { getWithRevalidate, get } = useCache();
  const [data, setData] = useState<T | null>(() => get<T>(key));
  const [isLoading, setIsLoading] = useState(!data);
  const [error, setError] = useState<Error | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await getWithRevalidate(key, fetcher, options);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
    } finally {
      setIsLoading(false);
    }
  }, [key, fetcher, options, getWithRevalidate]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  const refetch = useCallback(async () => {
    await fetch();
  }, [fetch]);

  return { data, isLoading, error, refetch };
}

export function usePrefetch() {
  const { prefetch, prefetchMultiple, registerPrefetchHints } = useCache();
  
  return {
    prefetch,
    prefetchMultiple,
    registerPrefetchHints,
  };
}

export function useCacheStats() {
  const { getStats, getEntries, isOnline } = useCache();
  const [stats, setStats] = useState<CacheStats | null>(null);

  useEffect(() => {
    const interval = setInterval(() => {
      setStats(getStats());
    }, 1000);
    
    return () => clearInterval(interval);
  }, [getStats]);

  return { stats, entries: getEntries(), isOnline };
}

// Utility Components
export function CacheDebugPanel() {
  const { stats, isOnline } = useCacheStats();
  
  if (process.env.NODE_ENV !== 'development') {
    return null;
  }
  
  return (
    <div className="fixed bottom-4 right-4 bg-gray-900 text-white p-4 rounded-lg shadow-xl max-w-sm z-50 text-xs font-mono">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-bold">Cache Debug</h3>
        <span className={`h-2 w-2 rounded-full ${isOnline ? 'bg-green-500' : 'bg-red-500'}`} />
      </div>
      {stats && (
        <div className="space-y-1">
          <p>Entries: {stats.totalEntries}</p>
          <p>Size: {(stats.totalSize / 1024).toFixed(1)} KB</p>
          <p>Hit Rate: {(stats.hitRate * 100).toFixed(1)}%</p>
          <p>Avg Hit: {stats.avgHitTime.toFixed(2)}ms</p>
          <p>Avg Miss: {stats.avgMissTime.toFixed(2)}ms</p>
        </div>
      )}
    </div>
  );
}

// Link prefetching component
export function PrefetchLink({ 
  href, 
  children, 
  ...props 
}: React.AnchorHTMLAttributes<HTMLAnchorElement> & { href: string }) {
  const { prefetch } = usePrefetch();
  
  const handleMouseEnter = useCallback(() => {
    prefetch(href, { priority: 'high', delay: 50 });
  }, [href, prefetch]);
  
  return (
    <a href={href} onMouseEnter={handleMouseEnter} {...props}>
      {children}
    </a>
  );
}
