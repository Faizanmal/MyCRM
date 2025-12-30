/**
 * Animation Variants for Framer Motion
 * 
 * This file contains reusable animation variants that can be used across the application
 * to maintain consistency and reduce code duplication.
 */

import { Variants } from 'framer-motion';

// ============================================
// FADE ANIMATIONS
// ============================================

export const fadeIn: Variants = {
  initial: { opacity: 0 },
  animate: { 
    opacity: 1,
    transition: { duration: 0.3, ease: 'easeOut' }
  },
  exit: { 
    opacity: 0,
    transition: { duration: 0.2, ease: 'easeIn' }
  },
};

export const fadeInUp: Variants = {
  initial: { opacity: 0, y: 20 },
  animate: { 
    opacity: 1, 
    y: 0,
    transition: { duration: 0.4, ease: 'easeOut' }
  },
  exit: { 
    opacity: 0, 
    y: -20,
    transition: { duration: 0.3, ease: 'easeIn' }
  },
};

export const fadeInDown: Variants = {
  initial: { opacity: 0, y: -20 },
  animate: { 
    opacity: 1, 
    y: 0,
    transition: { duration: 0.4, ease: 'easeOut' }
  },
  exit: { 
    opacity: 0, 
    y: 20,
    transition: { duration: 0.3, ease: 'easeIn' }
  },
};

// ============================================
// SLIDE ANIMATIONS
// ============================================

export const slideInFromLeft: Variants = {
  initial: { opacity: 0, x: -50 },
  animate: { 
    opacity: 1, 
    x: 0,
    transition: { duration: 0.4, ease: 'easeOut' }
  },
  exit: { 
    opacity: 0, 
    x: -50,
    transition: { duration: 0.3, ease: 'easeIn' }
  },
};

export const slideInFromRight: Variants = {
  initial: { opacity: 0, x: 50 },
  animate: { 
    opacity: 1, 
    x: 0,
    transition: { duration: 0.4, ease: 'easeOut' }
  },
  exit: { 
    opacity: 0, 
    x: 50,
    transition: { duration: 0.3, ease: 'easeIn' }
  },
};

// ============================================
// SCALE ANIMATIONS
// ============================================

export const scaleIn: Variants = {
  initial: { opacity: 0, scale: 0.8 },
  animate: { 
    opacity: 1, 
    scale: 1,
    transition: { 
      duration: 0.3, 
      ease: [0.175, 0.885, 0.32, 1.075] // easeOutBack
    }
  },
  exit: { 
    opacity: 0, 
    scale: 0.8,
    transition: { duration: 0.2, ease: 'easeIn' }
  },
};

export const scaleInSmall: Variants = {
  initial: { opacity: 0, scale: 0.95 },
  animate: { 
    opacity: 1, 
    scale: 1,
    transition: { duration: 0.2, ease: 'easeOut' }
  },
  exit: { 
    opacity: 0, 
    scale: 0.95,
    transition: { duration: 0.15, ease: 'easeIn' }
  },
};

// ============================================
// STAGGER ANIMATIONS
// ============================================

export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};

export const staggerContainerFast: Variants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0.1,
    },
  },
};

export const staggerItem: Variants = {
  hidden: { opacity: 0, y: 20 },
  show: { 
    opacity: 1, 
    y: 0,
    transition: {
      type: 'spring',
      stiffness: 100,
      damping: 15,
    },
  },
};

export const staggerItemFast: Variants = {
  hidden: { opacity: 0, y: 10 },
  show: { 
    opacity: 1, 
    y: 0,
    transition: {
      duration: 0.3,
      ease: 'easeOut',
    },
  },
};

// ============================================
// PAGE TRANSITION ANIMATIONS
// ============================================

export const pageTransition: Variants = {
  initial: { opacity: 0, x: -20 },
  animate: { 
    opacity: 1, 
    x: 0,
    transition: { 
      duration: 0.3, 
      ease: 'easeOut',
      when: 'beforeChildren',
      staggerChildren: 0.1,
    },
  },
  exit: { 
    opacity: 0, 
    x: 20,
    transition: { 
      duration: 0.2, 
      ease: 'easeIn',
    },
  },
};

export const pageTransitionFade: Variants = {
  initial: { opacity: 0 },
  animate: { 
    opacity: 1,
    transition: { 
      duration: 0.4, 
      ease: 'easeOut',
    },
  },
  exit: { 
    opacity: 0,
    transition: { 
      duration: 0.3, 
      ease: 'easeIn',
    },
  },
};

// ============================================
// MODAL/DIALOG ANIMATIONS
// ============================================

export const modalBackdrop: Variants = {
  hidden: { opacity: 0 },
  visible: { 
    opacity: 1,
    transition: { duration: 0.2 },
  },
  exit: { 
    opacity: 0,
    transition: { duration: 0.2, delay: 0.1 },
  },
};

export const modalContent: Variants = {
  hidden: { 
    opacity: 0, 
    scale: 0.95,
    y: 20,
  },
  visible: { 
    opacity: 1, 
    scale: 1,
    y: 0,
    transition: { 
      duration: 0.3,
      ease: [0.175, 0.885, 0.32, 1.075],
    },
  },
  exit: { 
    opacity: 0, 
    scale: 0.95,
    y: 20,
    transition: { duration: 0.2 },
  },
};

export const slideUpModal: Variants = {
  hidden: { 
    opacity: 0, 
    y: '100%',
  },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: { 
      duration: 0.3,
      ease: 'easeOut',
    },
  },
  exit: { 
    opacity: 0, 
    y: '100%',
    transition: { duration: 0.25 },
  },
};

// ============================================
// CARD ANIMATIONS
// ============================================

export const cardHover = {
  rest: { 
    scale: 1, 
    y: 0,
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
  },
  hover: { 
    scale: 1.02,
    y: -5,
    boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
  },
};

export const cardTap = {
  scale: 0.98,
};

// ============================================
// BUTTON ANIMATIONS
// ============================================

export const buttonHover = {
  scale: 1.05,
  transition: {
    duration: 0.2,
    ease: 'easeOut',
  },
};

export const buttonTap = {
  scale: 0.95,
};

export const buttonWithGlow = {
  rest: { 
    scale: 1,
    boxShadow: '0 0 0 rgba(139, 92, 246, 0)',
  },
  hover: { 
    scale: 1.05,
    boxShadow: '0 0 20px rgba(139, 92, 246, 0.5)',
    transition: {
      duration: 0.3,
      ease: 'easeOut',
    },
  },
  tap: { 
    scale: 0.95,
  },
};

// ============================================
// LIST ANIMATIONS
// ============================================

export const listContainer: Variants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
    },
  },
};

export const listItem: Variants = {
  hidden: { opacity: 0, x: -10 },
  show: { 
    opacity: 1, 
    x: 0,
    transition: {
      duration: 0.3,
      ease: 'easeOut',
    },
  },
};

// ============================================
// NOTIFICATION/TOAST ANIMATIONS
// ============================================

export const toastSlideIn: Variants = {
  initial: { 
    opacity: 0, 
    y: -50,
    scale: 0.3,
  },
  animate: { 
    opacity: 1, 
    y: 0,
    scale: 1,
    transition: {
      duration: 0.4,
      ease: [0.175, 0.885, 0.32, 1.275],
    },
  },
  exit: { 
    opacity: 0,
    scale: 0.5,
    transition: {
      duration: 0.2,
      ease: 'easeIn',
    },
  },
};

// ============================================
// DROPDOWN/MENU ANIMATIONS
// ============================================

export const dropdownMenu: Variants = {
  hidden: { 
    opacity: 0,
    scale: 0.95,
    y: -10,
  },
  visible: { 
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      duration: 0.2,
      ease: 'easeOut',
    },
  },
  exit: { 
    opacity: 0,
    scale: 0.95,
    y: -10,
    transition: {
      duration: 0.15,
      ease: 'easeIn',
    },
  },
};

// ============================================
// LOADING ANIMATIONS
// ============================================

export const pulseAnimation: Variants = {
  animate: {
    scale: [1, 1.05, 1],
    opacity: [0.5, 1, 0.5],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};

export const spinAnimation: Variants = {
  animate: {
    rotate: 360,
    transition: {
      duration: 1,
      repeat: Infinity,
      ease: 'linear',
    },
  },
};

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Check if the user prefers reduced motion
 */
export const prefersReducedMotion = (): boolean => {
  if (typeof window === 'undefined') return false;
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
};

/**
 * Get animation variant with reduced motion support
 */
export const getAnimationVariant = (variant: Variants): Variants => {
  if (prefersReducedMotion()) {
    return {
      initial: {},
      animate: {},
      exit: {},
    };
  }
  return variant;
};

/**
 * Get responsive animation duration based on screen size
 */
export const getResponsiveDuration = (baseDuration: number = 0.3): number => {
  if (typeof window === 'undefined') return baseDuration;
  const isMobile = window.innerWidth < 768;
  return isMobile ? baseDuration * 0.7 : baseDuration;
};

/**
 * Spring configuration presets
 */
export const springConfigs = {
  gentle: { stiffness: 100, damping: 15 },
  wobbly: { stiffness: 180, damping: 12 },
  stiff: { stiffness: 300, damping: 20 },
  slow: { stiffness: 50, damping: 20 },
  snappy: { stiffness: 400, damping: 30 },
  bouncy: { stiffness: 200, damping: 10 },
  smooth: { stiffness: 120, damping: 20 },
};

/**
 * Easing presets
 */
export const easings = {
  easeOutBack: [0.175, 0.885, 0.32, 1.275],
  easeInOutBack: [0.68, -0.55, 0.265, 1.55],
  easeOutExpo: [0.19, 1, 0.22, 1],
  easeInOutExpo: [0.87, 0, 0.13, 1],
  easeOutQuart: [0.25, 1, 0.5, 1],
  easeInOutQuart: [0.76, 0, 0.24, 1],
  easeOutElastic: [0.16, 1.3, 0.3, 1],
  spring: [0.175, 0.885, 0.32, 1.275],
};

// ============================================
// PREMIUM ANIMATIONS
// ============================================

/**
 * Glassmorphism card reveal animation
 */
export const glassReveal: Variants = {
  hidden: {
    opacity: 0,
    scale: 0.95,
    backdropFilter: 'blur(0px)',
  },
  visible: {
    opacity: 1,
    scale: 1,
    backdropFilter: 'blur(20px)',
    transition: {
      duration: 0.5,
      ease: [0.175, 0.885, 0.32, 1.275],
    },
  },
};

/**
 * Gradient border animation
 */
export const gradientBorder = {
  animate: {
    backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
    transition: {
      duration: 5,
      repeat: Infinity,
      ease: 'linear',
    },
  },
};

/**
 * Floating element animation
 */
export const floatingAnimation: Variants = {
  animate: {
    y: [0, -20, 0],
    transition: {
      duration: 3,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};

/**
 * Glow pulse animation
 */
export const glowPulse: Variants = {
  animate: {
    boxShadow: [
      '0 0 10px rgba(99, 102, 241, 0.3)',
      '0 0 30px rgba(99, 102, 241, 0.6)',
      '0 0 10px rgba(99, 102, 241, 0.3)',
    ],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};

/**
 * 3D tilt card animation helpers
 */
export const tiltCard = {
  initial: { rotateX: 0, rotateY: 0 },
  hover: (angle: { x: number; y: number }) => ({
    rotateX: angle.x,
    rotateY: angle.y,
    transition: { duration: 0.3 },
  }),
};

/**
 * Stagger children with perspective
 */
export const perspectiveContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};

export const perspectiveItem: Variants = {
  hidden: {
    opacity: 0,
    y: 50,
    rotateX: -15,
  },
  visible: {
    opacity: 1,
    y: 0,
    rotateX: 0,
    transition: {
      type: 'spring',
      stiffness: 100,
      damping: 15,
    },
  },
};

/**
 * Morphing blob animation
 */
export const morphingBlob: Variants = {
  animate: {
    borderRadius: [
      '60% 40% 30% 70% / 60% 30% 70% 40%',
      '30% 60% 70% 40% / 50% 60% 30% 60%',
      '60% 40% 30% 70% / 60% 30% 70% 40%',
    ],
    transition: {
      duration: 8,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};

/**
 * Spotlight effect animation
 */
export const spotlight: Variants = {
  hidden: {
    opacity: 0,
    scale: 1.5,
  },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.5,
      ease: 'easeOut',
    },
  },
};

/**
 * Ripple effect animation
 */
export const rippleEffect: Variants = {
  initial: {
    scale: 0,
    opacity: 1,
  },
  animate: {
    scale: 4,
    opacity: 0,
    transition: {
      duration: 0.6,
      ease: 'easeOut',
    },
  },
};

/**
 * Text reveal animation (character by character)
 */
export const textRevealContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.03,
    },
  },
};

export const textRevealChar: Variants = {
  hidden: {
    opacity: 0,
    y: 20,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      type: 'spring',
      damping: 12,
      stiffness: 200,
    },
  },
};

/**
 * Counter animation helper
 */
export const counterAnimation = (from: number, to: number, duration: number = 2) => ({
  initial: { count: from },
  animate: {
    count: to,
    transition: {
      duration,
      ease: 'easeOut',
    },
  },
});

/**
 * Parallax scroll animation helpers
 */
export const parallaxY = (offset: number = 100) => ({
  initial: { y: 0 },
  animate: (scrollY: number) => ({
    y: scrollY * offset * -0.001,
  }),
});

/**
 * Magnetic hover effect
 */
export const magneticHover = {
  rest: { x: 0, y: 0 },
  hover: (position: { x: number; y: number }) => ({
    x: position.x * 0.1,
    y: position.y * 0.1,
    transition: { type: 'spring', stiffness: 400, damping: 25 },
  }),
};

/**
 * Shake animation for errors
 */
export const shakeAnimation: Variants = {
  shake: {
    x: [0, -10, 10, -10, 10, 0],
    transition: {
      duration: 0.5,
      ease: 'easeInOut',
    },
  },
};

/**
 * Success checkmark animation
 */
export const checkmarkAnimation: Variants = {
  hidden: {
    pathLength: 0,
    opacity: 0,
  },
  visible: {
    pathLength: 1,
    opacity: 1,
    transition: {
      duration: 0.5,
      ease: 'easeOut',
    },
  },
};

/**
 * Orbit animation for decorative elements
 */
export const orbitAnimation = (radius: number = 100, duration: number = 10) => ({
  animate: {
    rotate: 360,
    transition: {
      duration,
      repeat: Infinity,
      ease: 'linear',
    },
  },
  style: {
    transformOrigin: `${radius}px center`,
  },
});

/**
 * Typewriter animation
 */
export const typewriter: Variants = {
  hidden: { width: 0 },
  visible: {
    width: '100%',
    transition: {
      duration: 2,
      ease: 'linear',
    },
  },
};

/**
 * Blur in animation
 */
export const blurIn: Variants = {
  hidden: {
    opacity: 0,
    filter: 'blur(10px)',
  },
  visible: {
    opacity: 1,
    filter: 'blur(0px)',
    transition: {
      duration: 0.5,
      ease: 'easeOut',
    },
  },
};

/**
 * Flip animation
 */
export const flipIn: Variants = {
  hidden: {
    opacity: 0,
    rotateY: -90,
  },
  visible: {
    opacity: 1,
    rotateY: 0,
    transition: {
      duration: 0.6,
      ease: [0.175, 0.885, 0.32, 1.275],
    },
  },
};

/**
 * Elastic scale
 */
export const elasticScale: Variants = {
  hidden: { scale: 0 },
  visible: {
    scale: 1,
    transition: {
      type: 'spring',
      stiffness: 400,
      damping: 10,
    },
  },
};

/**
 * Reveal from direction
 */
export const revealFromDirection = (direction: 'left' | 'right' | 'top' | 'bottom'): Variants => {
  const offset = 100;
  const initialPosition = {
    left: { x: -offset, y: 0 },
    right: { x: offset, y: 0 },
    top: { x: 0, y: -offset },
    bottom: { x: 0, y: offset },
  };

  return {
    hidden: {
      opacity: 0,
      ...initialPosition[direction],
    },
    visible: {
      opacity: 1,
      x: 0,
      y: 0,
      transition: {
        duration: 0.6,
        ease: [0.175, 0.885, 0.32, 1.275],
      },
    },
  };
};

/**
 * Create custom stagger animation
 */
export const createStagger = (staggerDelay: number = 0.1, initialDelay: number = 0): Variants => ({
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: staggerDelay,
      delayChildren: initialDelay,
    },
  },
});

/**
 * Create custom spring animation
 */
export const createSpring = (stiffness: number = 100, damping: number = 15) => ({
  type: 'spring',
  stiffness,
  damping,
});

/**
 * Hover grow effect for interactive elements
 */
export const hoverGrow = {
  rest: { scale: 1 },
  hover: {
    scale: 1.05,
    transition: {
      duration: 0.2,
      ease: 'easeOut',
    },
  },
  tap: { scale: 0.95 },
};

/**
 * Skeleton shimmer animation
 */
export const skeletonShimmer: Variants = {
  animate: {
    backgroundPosition: ['-200% 0', '200% 0'],
    transition: {
      duration: 1.5,
      repeat: Infinity,
      ease: 'linear',
    },
  },
};

/**
 * Page transition presets
 */
export const pageTransitions = {
  fade: {
    initial: { opacity: 0 },
    animate: { opacity: 1, transition: { duration: 0.3 } },
    exit: { opacity: 0, transition: { duration: 0.2 } },
  },
  slideUp: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } },
    exit: { opacity: 0, y: -20, transition: { duration: 0.3, ease: 'easeIn' } },
  },
  slideRight: {
    initial: { opacity: 0, x: -20 },
    animate: { opacity: 1, x: 0, transition: { duration: 0.4, ease: 'easeOut' } },
    exit: { opacity: 0, x: 20, transition: { duration: 0.3, ease: 'easeIn' } },
  },
  scale: {
    initial: { opacity: 0, scale: 0.95 },
    animate: { opacity: 1, scale: 1, transition: { duration: 0.3, ease: 'easeOut' } },
    exit: { opacity: 0, scale: 1.05, transition: { duration: 0.2, ease: 'easeIn' } },
  },
  blur: {
    initial: { opacity: 0, filter: 'blur(10px)' },
    animate: { opacity: 1, filter: 'blur(0px)', transition: { duration: 0.4 } },
    exit: { opacity: 0, filter: 'blur(10px)', transition: { duration: 0.3 } },
  },
};
