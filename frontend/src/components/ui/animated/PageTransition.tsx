'use client';

/**
 * Page Transition Component
 * 
 * Wrapper component that adds smooth page transitions when navigating between routes.
 */

import { ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { usePathname } from 'next/navigation';
import { pageTransition, pageTransitionFade } from '@/lib/animations';

interface PageTransitionProps {
  children: ReactNode;
  variant?: 'slide' | 'fade' | 'scale';
}

export function PageTransition({ children, variant = 'slide' }: PageTransitionProps) {
  const pathname = usePathname();

  const variants = {
    slide: pageTransition,
    fade: pageTransitionFade,
    scale: {
      initial: { opacity: 0, scale: 0.95 },
      animate: { opacity: 1, scale: 1 },
      exit: { opacity: 0, scale: 0.95 },
    },
  };

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={pathname}
        variants={variants[variant]}
        initial="initial"
        animate="animate"
        exit="exit"
        className="min-h-screen"
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}

/**
 * Section Transition - For animating sections within a page
 */
interface SectionTransitionProps {
  children: ReactNode;
  delay?: number;
}

export function SectionTransition({ children, delay = 0 }: SectionTransitionProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5, ease: 'easeOut' }}
    >
      {children}
    </motion.div>
  );
}

/**
 * Stagger Children - Animates children with stagger effect
 */
interface StaggerChildrenProps {
  children: ReactNode;
  staggerDelay?: number;
  className?: string;
}

export function StaggerChildren({ 
  children, 
  staggerDelay = 0.1,
  className 
}: StaggerChildrenProps) {
  return (
    <motion.div
      initial="hidden"
      animate="show"
      variants={{
        hidden: { opacity: 0 },
        show: {
          opacity: 1,
          transition: {
            staggerChildren: staggerDelay,
          },
        },
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

/**
 * Fade In When Visible - Fades in when element enters viewport
 */
import { useScrollAnimation } from '@/hooks/useAnimations';

interface FadeInWhenVisibleProps {
  children: ReactNode;
  className?: string;
}

export function FadeInWhenVisible({ children, className }: FadeInWhenVisibleProps) {
  const { ref, inView } = useScrollAnimation();

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 50 }}
      animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 50 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
