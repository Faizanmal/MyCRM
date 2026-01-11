'use client';

import React, { lazy, Suspense, ComponentType, ReactNode, useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { Skeleton } from '@/components/ui/skeleton';
import Image, { ImageProps } from 'next/image';

/**
 * Lazy Loading Utilities
 * 
 * Provides utilities for code splitting and lazy loading components
 * to improve initial load performance.
 */

/**
 * Create a lazy-loaded component with loading fallback
 */
export function lazyLoad<T extends ComponentType<unknown>>(
    importFn: () => Promise<{ default: T }>,
    LoadingComponent?: ComponentType<unknown>
): ComponentType<unknown> {
    const LazyComponent = lazy(importFn) as unknown as ComponentType<unknown>;

    const LoadingFallback = LoadingComponent || DefaultLoadingFallback;

    return function LazyLoadedComponent(props: unknown) {
        return (
            <Suspense fallback={<LoadingFallback />}>
                <LazyComponent {...props as Record<string, unknown>} />
            </Suspense>
        );
    } as ComponentType<unknown>;
}

/**
 * Default loading fallback component
 */
function DefaultLoadingFallback() {
    return (
        <div className="flex items-center justify-center p-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
        </div>
    );
}

/**
 * Chart loading skeleton
 */
export function ChartLoadingFallback() {
    return (
        <div className="p-4">
            <Skeleton className="h-64 w-full rounded-lg" />
        </div>
    );
}

/**
 * Table loading skeleton
 */
export function TableLoadingFallback() {
    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <Skeleton className="h-10 w-64" />
                <Skeleton className="h-10 w-32" />
            </div>
            <div className="border rounded-lg">
                <div className="p-4 border-b">
                    <div className="flex gap-4">
                        {[...Array(5)].map((_, i) => (
                            <Skeleton key={i} className="h-4 flex-1" />
                        ))}
                    </div>
                </div>
                {[...Array(5)].map((_, i) => (
                    <div key={i} className="p-4 border-b last:border-b-0">
                        <div className="flex gap-4">
                            {[...Array(5)].map((_, j) => (
                                <Skeleton key={j} className="h-4 flex-1" />
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

/**
 * Form loading skeleton
 */
export function FormLoadingFallback() {
    return (
        <div className="space-y-6 p-6">
            {[...Array(4)].map((_, i) => (
                <div key={i} className="space-y-2">
                    <Skeleton className="h-4 w-24" />
                    <Skeleton className="h-10 w-full" />
                </div>
            ))}
            <Skeleton className="h-10 w-32" />
        </div>
    );
}

/**
 * Card grid loading skeleton
 */
export function CardGridLoadingFallback({ count = 6 }: { count?: number }) {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[...Array(count)].map((_, i) => (
                <div key={i} className="border rounded-lg p-4">
                    <div className="flex items-center gap-3 mb-4">
                        <Skeleton className="h-12 w-12 rounded-full" />
                        <div className="space-y-2 flex-1">
                            <Skeleton className="h-4 w-32" />
                            <Skeleton className="h-3 w-24" />
                        </div>
                    </div>
                    <div className="space-y-2">
                        <Skeleton className="h-3 w-full" />
                        <Skeleton className="h-3 w-3/4" />
                    </div>
                </div>
            ))}
        </div>
    );
}

/**
 * Lazy image component with blur placeholder
 */
export function LazyImage({
    src,
    alt,
    className,
    placeholderColor = '#f3f4f6',
    ...props
}: {
    src: string;
    alt: string;
    className?: string;
    placeholderColor?: string;
} & Omit<ImageProps, 'src' | 'alt' | 'className'>) {
    const [isLoaded, setIsLoaded] = useState(false);
    const [error, setError] = useState(false);

    return (
        <div className="relative overflow-hidden" style={{ backgroundColor: placeholderColor }}>
            {!isLoaded && !error && (
                <Skeleton className="absolute inset-0" />
            )}
            {error ? (
                <div className="flex items-center justify-center h-full bg-gray-100 text-gray-400">
                    <span className="text-sm">Failed to load</span>
                </div>
            ) : (
                <Image
                    src={src}
                    alt={alt}
                    className={`${className} ${isLoaded ? 'opacity-100' : 'opacity-0'} transition-opacity duration-300`}
                    onLoad={() => setIsLoaded(true)}
                    onError={() => setError(true)}
                    loading="lazy"
                    {...props}
                />
            )}
        </div>
    );
}

/**
 * Intersection Observer based lazy loading wrapper
 */
export function LazyLoadOnView({
    children,
    placeholder,
    rootMargin = '100px',
    threshold = 0.1,
}: {
    children: ReactNode;
    placeholder?: ReactNode;
    rootMargin?: string;
    threshold?: number;
}) {
    const [, setIsVisible] = useState(false);
    const [hasBeenVisible, setHasBeenVisible] = useState(false);
    const containerRef = React.useRef<HTMLDivElement>(null);

    useEffect(() => {
        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting) {
                    setIsVisible(true);
                    setHasBeenVisible(true);
                } else {
                    setIsVisible(false);
                }
            },
            { rootMargin, threshold }
        );

        if (containerRef.current) {
            observer.observe(containerRef.current);
        }

        return () => observer.disconnect();
    }, [rootMargin, threshold, setIsVisible]);

    return (
        <div ref={containerRef}>
            {hasBeenVisible ? children : (placeholder || <DefaultLoadingFallback />)}
        </div>
    );
}

/**
 * Prefetch component for anticipatory loading
 */
export function usePrefetch(importFn: () => Promise<unknown>) {
    const prefetch = React.useCallback(() => {
        importFn();
    }, [importFn]);

    return prefetch;
}

/**
 * Module preload link generator
 */
export function PreloadModules({ modules }: { modules: string[] }) {
    return (
        <>
            {modules.map((module) => (
                <link key={module} rel="modulepreload" href={module} />
            ))}
        </>
    );
}

// Pre-configured lazy components for common use cases
export const LazyChart = lazyLoad(
    () => import('recharts').then(m => ({ default: m.ResponsiveContainer as unknown as ComponentType<unknown> })) as Promise<{ default: ComponentType<unknown> }>,
    ChartLoadingFallback
);

// export const LazyEditor = lazyLoad(
//     () => (import('@/components/RichTextEditor') as any).catch(() => ({
//         default: () => <div>Editor not available</div>
//     })) as Promise<{ default: ComponentType }>,
//     DefaultLoadingFallback
// );

// Dynamic import wrapper for Next.js
export const createDynamicComponent = <P extends object>(
    importFn: () => Promise<{ default: ComponentType<P> }>,
    options?: {
        loading?: ComponentType<unknown>;
        ssr?: boolean;
    }
) => {
    const LoadingFn = options?.loading ? ((props: unknown) => React.createElement(options!.loading as ComponentType<unknown>, props as any)) : undefined; // eslint-disable-line @typescript-eslint/no-explicit-any
    return dynamic(importFn, {
        loading: LoadingFn as ((loadingProps: any) => ReactNode) | undefined, // eslint-disable-line @typescript-eslint/no-explicit-any
        ssr: options?.ssr ?? true,
    });
};

const lazyLoadingUtils = {
    lazyLoad,
    LazyImage,
    LazyLoadOnView,
    usePrefetch,
    ChartLoadingFallback,
    TableLoadingFallback,
    FormLoadingFallback,
    CardGridLoadingFallback,
    createDynamicComponent,
};

export default lazyLoadingUtils;
