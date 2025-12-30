'use client';

import { useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface ConfettiPiece {
    id: number;
    x: number;
    y: number;
    rotation: number;
    color: string;
    scale: number;
    velocityX: number;
    velocityY: number;
    rotationSpeed: number;
    shape: 'square' | 'circle' | 'star' | 'triangle';
}

interface ConfettiProps {
    active: boolean;
    onComplete?: () => void;
    duration?: number;
    particleCount?: number;
}

const colors = [
    '#FF6B6B', // Red
    '#4ECDC4', // Teal
    '#45B7D1', // Blue
    '#96CEB4', // Green
    '#FFEAA7', // Yellow
    '#DDA0DD', // Plum
    '#98D8C8', // Mint
    '#F7DC6F', // Gold
    '#BB8FCE', // Purple
    '#85C1E9', // Light Blue
];

const shapes = ['square', 'circle', 'star', 'triangle'] as const;

export default function Confetti({
    active,
    onComplete,
    duration = 3000,
    particleCount = 100
}: ConfettiProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const animationRef = useRef<number | undefined>(undefined);
    const particlesRef = useRef<ConfettiPiece[]>([]);
    const startTimeRef = useRef<number>(0);

    const createParticle = useCallback((index: number): ConfettiPiece => {
        return {
            id: index,
            x: Math.random() * window.innerWidth,
            y: -20 - Math.random() * 100,
            rotation: Math.random() * 360,
            color: colors[Math.floor(Math.random() * colors.length)],
            scale: 0.5 + Math.random() * 0.5,
            velocityX: (Math.random() - 0.5) * 10,
            velocityY: 3 + Math.random() * 5,
            rotationSpeed: (Math.random() - 0.5) * 20,
            shape: shapes[Math.floor(Math.random() * shapes.length)],
        };
    }, []);

    const drawShape = useCallback((
        ctx: CanvasRenderingContext2D,
        particle: ConfettiPiece
    ) => {
        const size = 10 * particle.scale;

        ctx.save();
        ctx.translate(particle.x, particle.y);
        ctx.rotate((particle.rotation * Math.PI) / 180);
        ctx.fillStyle = particle.color;
        ctx.beginPath();

        switch (particle.shape) {
            case 'square':
                ctx.fillRect(-size / 2, -size / 2, size, size * 0.6);
                break;
            case 'circle':
                ctx.arc(0, 0, size / 2, 0, Math.PI * 2);
                ctx.fill();
                break;
            case 'star':
                for (let i = 0; i < 5; i++) {
                    ctx.lineTo(
                        Math.cos(((18 + i * 72) * Math.PI) / 180) * size,
                        Math.sin(((18 + i * 72) * Math.PI) / 180) * size
                    );
                    ctx.lineTo(
                        Math.cos(((54 + i * 72) * Math.PI) / 180) * (size / 2),
                        Math.sin(((54 + i * 72) * Math.PI) / 180) * (size / 2)
                    );
                }
                ctx.closePath();
                ctx.fill();
                break;
            case 'triangle':
                ctx.moveTo(0, -size / 2);
                ctx.lineTo(size / 2, size / 2);
                ctx.lineTo(-size / 2, size / 2);
                ctx.closePath();
                ctx.fill();
                break;
        }

        ctx.restore();
    }, []);

    const animate = useCallback((timestamp: number) => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        if (startTimeRef.current === 0) {
            startTimeRef.current = timestamp;
        }

        const elapsed = timestamp - startTimeRef.current;
        const progress = Math.min(elapsed / duration, 1);

        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Update and draw particles
        particlesRef.current = particlesRef.current.filter(particle => {
            // Update position
            particle.x += particle.velocityX;
            particle.y += particle.velocityY;
            particle.rotation += particle.rotationSpeed;
            particle.velocityY += 0.1; // Gravity

            // Add some wind effect
            particle.velocityX += (Math.random() - 0.5) * 0.5;

            // Calculate opacity based on progress
            const opacity = 1 - (progress * 0.8);
            ctx.globalAlpha = opacity;

            // Draw particle
            drawShape(ctx, particle);

            // Remove particles that are off screen
            return particle.y < window.innerHeight + 50;
        });

        // Continue animation or complete
        if (progress < 1 && particlesRef.current.length > 0) {
            animationRef.current = requestAnimationFrame(animate);
        } else {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            onComplete?.();
        }
    }, [duration, drawShape, onComplete]);

    useEffect(() => {
        if (active) {
            const canvas = canvasRef.current;
            if (!canvas) return;

            // Set canvas size
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;

            // Create particles
            particlesRef.current = Array.from({ length: particleCount }, (_, i) =>
                createParticle(i)
            );

            // Reset start time
            startTimeRef.current = 0;

            // Start animation
            animationRef.current = requestAnimationFrame(animate);

            return () => {
                if (animationRef.current) {
                    cancelAnimationFrame(animationRef.current);
                }
            };
        }
    }, [active, particleCount, createParticle, animate]);

    // Handle window resize
    useEffect(() => {
        const handleResize = () => {
            const canvas = canvasRef.current;
            if (canvas) {
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
            }
        };

        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    return (
        <AnimatePresence>
            {active && (
                <motion.canvas
                    ref={canvasRef}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 pointer-events-none z-[100]"
                />
            )}
        </AnimatePresence>
    );
}

// Hook to trigger confetti easily
export function useConfetti() {
    const triggerRef = useRef<(() => void) | null>(null);

    const fire = useCallback(() => {
        triggerRef.current?.();
    }, []);

    return { fire, triggerRef };
}
