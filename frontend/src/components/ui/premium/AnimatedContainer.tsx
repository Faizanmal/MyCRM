'use client';

/**
 * AnimatedContainer Component
 * 
 * Wrapper component for adding entrance animations,
 * stagger effects, and scroll-triggered animations.
 */

import React, { ReactNode } from 'react';
import { motion, Variants, HTMLMotionProps } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { cn } from '@/lib/utils';

// Animation Variants
const fadeInUpVariants: Variants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0 },
};

const fadeInDownVariants: Variants = {
  hidden: { opacity: 0, y: -30 },
  visible: { opacity: 1, y: 0 },
};

const fadeInLeftVariants: Variants = {
  hidden: { opacity: 0, x: -30 },
  visible: { opacity: 1, x: 0 },
};

const fadeInRightVariants: Variants = {
  hidden: { opacity: 0, x: 30 },
  visible: { opacity: 1, x: 0 },
};

const scaleInVariants: Variants = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: { opacity: 1, scale: 1 },
};

const blurInVariants: Variants = {
  hidden: { opacity: 0, filter: 'blur(10px)' },
  visible: { opacity: 1, filter: 'blur(0px)' },
};

const animationVariants = {
  fadeInUp: fadeInUpVariants,
  fadeInDown: fadeInDownVariants,
  fadeInLeft: fadeInLeftVariants,
  fadeInRight: fadeInRightVariants,
  scaleIn: scaleInVariants,
  blurIn: blurInVariants,
};

interface AnimatedContainerProps extends Omit<HTMLMotionProps<'div'>, 'children'> {
  children: ReactNode;
  animation?: keyof typeof animationVariants;
  delay?: number;
  duration?: number;
  once?: boolean;
  threshold?: number;
  className?: string;
}

export function AnimatedContainer({
  children,
  animation = 'fadeInUp',
  delay = 0,
  duration = 0.5,
  once = true,
  threshold = 0.1,
  className,
  ...props
}: AnimatedContainerProps) {
  const [ref, inView] = useInView({
    triggerOnce: once,
    threshold,
  });

  return (
    <motion.div
      ref={ref}
      initial="hidden"
      animate={inView ? 'visible' : 'hidden'}
      variants={animationVariants[animation]}
      transition={{
        duration,
        delay,
        ease: [0.4, 0, 0.2, 1],
      }}
      className={className}
      {...props}
    >
      {children}
    </motion.div>
  );
}

/**
 * StaggerContainer - Animates children with stagger effect
 */
interface StaggerContainerProps {
  children: ReactNode;
  staggerDelay?: number;
  animation?: keyof typeof animationVariants;
  className?: string;
  once?: boolean;
}

export function StaggerContainer({
  children,
  staggerDelay = 0.1,
  animation = 'fadeInUp',
  className,
  once = true,
}: StaggerContainerProps) {
  const [ref, inView] = useInView({
    triggerOnce: once,
    threshold: 0.1,
  });

  const containerVariants: Variants = {
    hidden: {},
    visible: {
      transition: {
        staggerChildren: staggerDelay,
      },
    },
  };

  return (
    <motion.div
      ref={ref}
      initial="hidden"
      animate={inView ? 'visible' : 'hidden'}
      variants={containerVariants}
      className={className}
    >
      {React.Children.map(children, (child, index) => (
        <motion.div
          key={index}
          variants={animationVariants[animation]}
          transition={{
            duration: 0.5,
            ease: [0.4, 0, 0.2, 1],
          }}
        >
          {child}
        </motion.div>
      ))}
    </motion.div>
  );
}

/**
 * PageWrapper - Wraps page content with entrance animation
 */
interface PageWrapperProps {
  children: ReactNode;
  className?: string;
}

export function PageWrapper({ children, className }: PageWrapperProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
      className={cn('min-h-screen', className)}
    >
      {children}
    </motion.div>
  );
}

/**
 * SectionWrapper - Animates section on scroll
 */
interface SectionWrapperProps {
  children: ReactNode;
  className?: string;
  id?: string;
}

export function SectionWrapper({ children, className, id }: SectionWrapperProps) {
  const [ref, inView] = useInView({
    triggerOnce: true,
    threshold: 0.1,
  });

  return (
    <motion.section
      ref={ref}
      id={id}
      initial={{ opacity: 0, y: 50 }}
      animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 50 }}
      transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
      className={cn('py-16 lg:py-24', className)}
    >
      {children}
    </motion.section>
  );
}

/**
 * ParallaxContainer - Subtle parallax effect on scroll
 */
interface ParallaxContainerProps {
  children: ReactNode;
  offset?: number;
  className?: string;
}

export function ParallaxContainer({
  children,
  offset = 50,
  className,
}: ParallaxContainerProps) {
  const [ref, inView] = useInView({
    threshold: 0,
  });

  return (
    <motion.div
      ref={ref}
      initial={{ y: offset }}
      animate={{ y: inView ? 0 : offset }}
      transition={{ duration: 0.8, ease: 'easeOut' }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

/**
 * HoverScaleContainer - Scales on hover
 */
interface HoverScaleContainerProps {
  children: ReactNode;
  scale?: number;
  className?: string;
}

export function HoverScaleContainer({
  children,
  scale = 1.02,
  className,
}: HoverScaleContainerProps) {
  return (
    <motion.div
      whileHover={{ scale }}
      transition={{ duration: 0.2 }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

/**
 * RevealContainer - Reveals content with mask animation
 */
interface RevealContainerProps {
  children: ReactNode;
  className?: string;
  delay?: number;
}

export function RevealContainer({
  children,
  className,
  delay = 0,
}: RevealContainerProps) {
  const [ref, inView] = useInView({
    triggerOnce: true,
    threshold: 0.2,
  });

  return (
    <div ref={ref} className={cn('relative overflow-hidden', className)}>
      <motion.div
        initial={{ y: '100%' }}
        animate={inView ? { y: 0 } : { y: '100%' }}
        transition={{
          duration: 0.6,
          delay,
          ease: [0.4, 0, 0.2, 1],
        }}
      >
        {children}
      </motion.div>
    </div>
  );
}
