'use client';

import React, { useState, useEffect, ReactNode } from 'react';

import { cn } from '@/lib/utils';

/**
 * Responsive Utilities
 * 
 * Provides:
 * - Breakpoint hooks
 * - Responsive visibility components
 * - Container queries
 * - Touch detection
 */

// Breakpoint definitions (matching Tailwind defaults)
export const breakpoints = {
    xs: 0,
    sm: 640,
    md: 768,
    lg: 1024,
    xl: 1280,
    '2xl': 1536,
} as const;

export type Breakpoint = keyof typeof breakpoints;

/**
 * Hook to get current breakpoint
 */
export function useBreakpoint(): Breakpoint {
    const [breakpoint, setBreakpoint] = useState<Breakpoint>('lg');

    useEffect(() => {
        const getBreakpoint = (): Breakpoint => {
            const width = window.innerWidth;
            if (width >= breakpoints['2xl']) return '2xl';
            if (width >= breakpoints.xl) return 'xl';
            if (width >= breakpoints.lg) return 'lg';
            if (width >= breakpoints.md) return 'md';
            if (width >= breakpoints.sm) return 'sm';
            return 'xs';
        };

        const handleResize = () => setBreakpoint(getBreakpoint());

        handleResize(); // Initial check
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    return breakpoint;
}

/**
 * Hook to check if viewport is at or above a breakpoint
 */
export function useBreakpointUp(target: Breakpoint): boolean {
    const [isAbove, setIsAbove] = useState(false);

    useEffect(() => {
        const check = () => {
            setIsAbove(window.innerWidth >= breakpoints[target]);
        };

        check();
        window.addEventListener('resize', check);
        return () => window.removeEventListener('resize', check);
    }, [target]);

    return isAbove;
}

/**
 * Hook to check if viewport is below a breakpoint
 */
export function useBreakpointDown(target: Breakpoint): boolean {
    const [isBelow, setIsBelow] = useState(false);

    useEffect(() => {
        const check = () => {
            setIsBelow(window.innerWidth < breakpoints[target]);
        };

        check();
        window.addEventListener('resize', check);
        return () => window.removeEventListener('resize', check);
    }, [target]);

    return isBelow;
}

/**
 * Hook to check if viewport is between two breakpoints
 */
export function useBreakpointBetween(min: Breakpoint, max: Breakpoint): boolean {
    const [isBetween, setIsBetween] = useState(false);

    useEffect(() => {
        const check = () => {
            const width = window.innerWidth;
            setIsBetween(width >= breakpoints[min] && width < breakpoints[max]);
        };

        check();
        window.addEventListener('resize', check);
        return () => window.removeEventListener('resize', check);
    }, [min, max]);

    return isBetween;
}

/**
 * Hook to detect if device is mobile
 */
export function useIsMobile(): boolean {
    return useBreakpointDown('md');
}

/**
 * Hook to detect if device is tablet
 */
export function useIsTablet(): boolean {
    return useBreakpointBetween('md', 'lg');
}

/**
 * Hook to detect if device is desktop
 */
export function useIsDesktop(): boolean {
    return useBreakpointUp('lg');
}

/**
 * Hook to detect touch device
 */
export function useIsTouchDevice(): boolean {
    const [isTouch] = useState(() => 
        typeof window !== 'undefined' && ('ontouchstart' in window || navigator.maxTouchPoints > 0)
    );

    return isTouch;
}

/**
 * Hook to get device orientation
 */
export function useOrientation(): 'portrait' | 'landscape' {
    const [orientation, setOrientation] = useState<'portrait' | 'landscape'>('portrait');

    useEffect(() => {
        const updateOrientation = () => {
            setOrientation(window.innerHeight > window.innerWidth ? 'portrait' : 'landscape');
        };

        updateOrientation();
        window.addEventListener('resize', updateOrientation);
        window.addEventListener('orientationchange', updateOrientation);

        return () => {
            window.removeEventListener('resize', updateOrientation);
            window.removeEventListener('orientationchange', updateOrientation);
        };
    }, []);

    return orientation;
}

/**
 * Component that renders only on specific breakpoints
 */
interface ResponsiveProps {
    children: ReactNode;
    className?: string;
}

export function MobileOnly({ children, className }: ResponsiveProps): React.ReactNode {
    const isMobile = useIsMobile();

    if (!isMobile) return null;
    return <div className={className}>{children}</div>;
}

export function TabletOnly({ children, className }: ResponsiveProps): React.ReactNode {
    const isTablet = useIsTablet();

    if (!isTablet) return null;
    return <div className={className}>{children}</div>;
}

export function DesktopOnly({ children, className }: ResponsiveProps): React.ReactNode {
    const isDesktop = useIsDesktop();

    if (!isDesktop) return null;
    return <div className={className}>{children}</div>;
}

export function MobileAndTablet({ children, className }: ResponsiveProps): React.ReactNode {
    const isDesktop = useIsDesktop();

    if (isDesktop) return null;
    return <div className={className}>{children}</div>;
}

export function TabletAndDesktop({ children, className }: ResponsiveProps): React.ReactNode {
    const isMobile = useIsMobile();

    if (isMobile) return null;
    return <div className={className}>{children}</div>;
}

/**
 * Component that shows different content based on breakpoint
 */
interface ResponsiveRenderProps {
    mobile?: ReactNode;
    tablet?: ReactNode;
    desktop?: ReactNode;
}

export function ResponsiveRender({ mobile, tablet, desktop }: ResponsiveRenderProps): React.JSX.Element {
    const breakpoint = useBreakpoint();

    if (breakpoint === 'xs' || breakpoint === 'sm') {
        return <>{mobile}</>;
    }
    if (breakpoint === 'md') {
        return <>{tablet ?? mobile}</>;
    }
    return <>{desktop ?? tablet ?? mobile}</>;
}

/**
 * Responsive container with max-width
 */
interface ContainerProps {
    children: ReactNode;
    size?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full';
    className?: string;
    padding?: boolean;
}

export function Container({
    children,
    size = 'xl',
    className,
    padding = true
}: ContainerProps): React.JSX.Element {
    const maxWidths = {
        sm: 'max-w-screen-sm',
        md: 'max-w-screen-md',
        lg: 'max-w-screen-lg',
        xl: 'max-w-screen-xl',
        '2xl': 'max-w-screen-2xl',
        full: 'max-w-full',
    };

    return (
        <div className={cn(
            'mx-auto w-full',
            maxWidths[size],
            padding && 'px-4 sm:px-6 lg:px-8',
            className
        )}>
            {children}
        </div>
    );
}

/**
 * Grid with responsive columns
 */
interface ResponsiveGridProps {
    children: ReactNode;
    cols?: {
        xs?: number;
        sm?: number;
        md?: number;
        lg?: number;
        xl?: number;
    };
    gap?: number;
    className?: string;
}

export function ResponsiveGrid({
    children,
    cols = { xs: 1, sm: 2, md: 3, lg: 4 },
    gap = 4,
    className,
}: ResponsiveGridProps): React.JSX.Element {
    const gridCols = {
        1: 'grid-cols-1',
        2: 'grid-cols-2',
        3: 'grid-cols-3',
        4: 'grid-cols-4',
        5: 'grid-cols-5',
        6: 'grid-cols-6',
    };

    const gapClass = `gap-${gap}`;

    return (
        <div className={cn(
            'grid',
            gapClass,
            cols.xs && gridCols[cols.xs as keyof typeof gridCols],
            cols.sm && `sm:${gridCols[cols.sm as keyof typeof gridCols]}`,
            cols.md && `md:${gridCols[cols.md as keyof typeof gridCols]}`,
            cols.lg && `lg:${gridCols[cols.lg as keyof typeof gridCols]}`,
            cols.xl && `xl:${gridCols[cols.xl as keyof typeof gridCols]}`,
            className
        )}>
            {children}
        </div>
    );
}

/**
 * Stack with responsive direction
 */
interface ResponsiveStackProps {
    children: ReactNode;
    direction?: {
        default?: 'row' | 'column';
        sm?: 'row' | 'column';
        md?: 'row' | 'column';
        lg?: 'row' | 'column';
    };
    gap?: number;
    className?: string;
}

export function ResponsiveStack({
    children,
    direction = { default: 'column', md: 'row' },
    gap = 4,
    className,
}: ResponsiveStackProps): React.JSX.Element {
    const directions = {
        row: 'flex-row',
        column: 'flex-col',
    };

    return (
        <div className={cn(
            'flex',
            `gap-${gap}`,
            direction.default && directions[direction.default],
            direction.sm && `sm:${directions[direction.sm]}`,
            direction.md && `md:${directions[direction.md]}`,
            direction.lg && `lg:${directions[direction.lg]}`,
            className
        )}>
            {children}
        </div>
    );
}

/**
 * Hook for responsive value
 */
export function useResponsiveValue<T>(values: {
    xs?: T;
    sm?: T;
    md?: T;
    lg?: T;
    xl?: T;
    '2xl'?: T;
}): T | undefined {
    const breakpoint = useBreakpoint();

    // Find the closest defined value
    const breakpointOrder: Breakpoint[] = ['xs', 'sm', 'md', 'lg', 'xl', '2xl'];
    const currentIndex = breakpointOrder.indexOf(breakpoint);

    for (let i = currentIndex; i >= 0; i--) {
        const key = breakpointOrder[i];
        if (values[key] !== undefined) {
            return values[key];
        }
    }

    return undefined;
}

/**
 * Safe area insets for mobile (notch, home indicator)
 */
export function useSafeAreaInsets(): { top: number; right: number; bottom: number; left: number; } {
    const [insets] = useState(() => {
        if (typeof document !== 'undefined') {
            const style = getComputedStyle(document.documentElement);
            return {
                top: parseInt(style.getPropertyValue('--sat') || '0', 10),
                right: parseInt(style.getPropertyValue('--sar') || '0', 10),
                bottom: parseInt(style.getPropertyValue('--sab') || '0', 10),
                left: parseInt(style.getPropertyValue('--sal') || '0', 10),
            };
        }
        return {
            top: 0,
            right: 0,
            bottom: 0,
            left: 0,
        };
    });

    return insets;
}

const Responsive = {
    useBreakpoint,
    useBreakpointUp,
    useBreakpointDown,
    useBreakpointBetween,
    useIsMobile,
    useIsTablet,
    useIsDesktop,
    useIsTouchDevice,
    useOrientation,
    useResponsiveValue,
    useSafeAreaInsets,
    MobileOnly,
    TabletOnly,
    DesktopOnly,
    MobileAndTablet,
    TabletAndDesktop,
    ResponsiveRender,
    Container,
    ResponsiveGrid,
    ResponsiveStack,
    breakpoints,
};

export default Responsive;

