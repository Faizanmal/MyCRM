/**
 * Custom React Hooks for Animations
 * 
 * This file contains reusable animation hooks that can be used throughout the application.
 */

import { useEffect, useRef, useState } from 'react';
import { useInView } from 'react-intersection-observer';

/**
 * Hook for scroll-triggered animations
 * Returns a ref and inView state to trigger animations when element enters viewport
 */
export function useScrollAnimation(options = {}) {
  const defaultOptions = {
    triggerOnce: true,
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px',
    ...options,
  };

  const [ref, inView] = useInView(defaultOptions);

  return { ref, inView };
}

/**
 * Hook to detect if user prefers reduced motion
 */
export function usePrefersReducedMotion(): boolean {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(() => {
    if (typeof window === 'undefined') return false;
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  });

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

    const handleChange = () => {
      setPrefersReducedMotion(mediaQuery.matches);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  return prefersReducedMotion;
}

/**
 * Hook for delayed animations
 * Triggers an animation after a specified delay
 */
export function useDelayedAnimation(delay: number = 1000) {
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const timeout = setTimeout(() => {
      setIsReady(true);
    }, delay);

    return () => clearTimeout(timeout);
  }, [delay]);

  return isReady;
}

/**
 * Hook for sequential animations
 * Returns current step for multi-step animations
 */
export function useSequentialAnimation(steps: number, interval: number = 500) {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    if (currentStep >= steps) return;

    const timeout = setTimeout(() => {
      setCurrentStep((prev) => prev + 1);
    }, interval);

    return () => clearTimeout(timeout);
  }, [currentStep, steps, interval]);

  return currentStep;
}

/**
 * Hook for hover state with delay
 * Useful for preventing accidental hover animations
 */
export function useDelayedHover(delay: number = 200) {
  const [isHovered, setIsHovered] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const handleMouseEnter = () => {
    timeoutRef.current = setTimeout(() => {
      setIsHovered(true);
    }, delay);
  };

  const handleMouseLeave = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setIsHovered(false);
  };

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return { isHovered, handleMouseEnter, handleMouseLeave };
}

/**
 * Hook for scroll position
 * Returns current scroll position
 */
export function useScrollPosition() {
  const [scrollPosition, setScrollPosition] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      setScrollPosition(window.scrollY);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return scrollPosition;
}

/**
 * Hook for scroll direction
 * Returns 'up', 'down', or null
 */
export function useScrollDirection() {
  const [scrollDirection, setScrollDirection] = useState<'up' | 'down' | null>(null);
  const prevScrollY = useRef(0);

  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      
      if (currentScrollY > prevScrollY.current) {
        setScrollDirection('down');
      } else if (currentScrollY < prevScrollY.current) {
        setScrollDirection('up');
      }
      
      prevScrollY.current = currentScrollY;
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return scrollDirection;
}

/**
 * Hook for mouse position
 * Returns current mouse position
 */
export function useMousePosition() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (event: MouseEvent) => {
      setMousePosition({ x: event.clientX, y: event.clientY });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return mousePosition;
}

/**
 * Hook for element dimensions
 * Returns current element dimensions
 */
export function useElementSize<T extends HTMLElement = HTMLDivElement>() {
  const ref = useRef<T>(null);
  const [size, setSize] = useState({ width: 0, height: 0 });

  useEffect(() => {
    if (!ref.current) return;

    const observer = new ResizeObserver((entries) => {
      const { width, height } = entries[0].contentRect;
      setSize({ width, height });
    });

    observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);

  return { ref, size };
}

/**
 * Hook for parallax effect
 * Returns transform value based on scroll position
 */
export function useParallax(speed: number = 0.5) {
  const [offsetY, setOffsetY] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      setOffsetY(window.scrollY * speed);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [speed]);

  return offsetY;
}

/**
 * Hook for intersection ratio
 * Returns how much of the element is visible (0-1)
 */
export function useIntersectionRatio(options = {}) {
  const [ratio, setRatio] = useState(0);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        setRatio(entry.intersectionRatio);
      },
      {
        threshold: Array.from({ length: 101 }, (_, i) => i / 100),
        ...options,
      }
    );

    observer.observe(ref.current);
    return () => observer.disconnect();
  }, [options]);

  return { ref, ratio };
}

/**
 * Hook for media query
 * Returns true if media query matches
 */
export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(() => {
    if (typeof window === 'undefined') return false;
    return window.matchMedia(query).matches;
  });

  useEffect(() => {
    const media = window.matchMedia(query);

    const listener = (e: MediaQueryListEvent) => {
      setMatches(e.matches);
    };

    media.addEventListener('change', listener);
    return () => media.removeEventListener('change', listener);
  }, [query]);

  return matches;
}

/**
 * Hook for responsive animations
 * Returns animation config based on screen size
 */
export function useResponsiveAnimation() {
  const isMobile = useMediaQuery('(max-width: 768px)');
  const prefersReducedMotion = usePrefersReducedMotion();

  const getConfig = (baseConfig: Record<string, unknown> & { transition?: Record<string, unknown> }) => {
    if (prefersReducedMotion) {
      return {};
    }

    if (isMobile) {
      return {
        ...baseConfig,
        transition: {
          ...(baseConfig.transition || {}),
          duration: ((baseConfig.transition as Record<string, unknown>)?.duration as number || 0.3) * 0.7,
        },
      };
    }

    return baseConfig;
  };

  return { getConfig, isMobile, prefersReducedMotion };
}

/**
 * Hook for counting animation
 * Animates a number from start to end
 */
export function useCountAnimation(
  end: number,
  duration: number = 2000,
  start: number = 0
) {
  const [count, setCount] = useState(start);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (!isAnimating) return;

    const startTime = Date.now();
    const range = end - start;

    const timer = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);

      // Easing function (easeOutCubic)
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = start + range * eased;

      setCount(Math.floor(current));

      if (progress === 1) {
        clearInterval(timer);
        setIsAnimating(false);
      }
    }, 16); // ~60fps

    return () => clearInterval(timer);
  }, [start, end, duration, isAnimating]);

  const startAnimation = () => setIsAnimating(true);
  const resetAnimation = () => {
    setCount(start);
    setIsAnimating(false);
  };

  return { count, startAnimation, resetAnimation, isAnimating };
}
