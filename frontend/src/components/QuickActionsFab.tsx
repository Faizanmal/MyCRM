'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
// import { Button } from '@/components/ui/button';
import {
    Plus,
    X,
    UserPlus,
    Phone,
    Mail,
    Calendar,
    FileText,
    Target,
    ClipboardList,
    Sparkles,
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

interface QuickAction {
    id: string;
    label: string;
    icon: React.ElementType;
    color: string;
    action: () => void;
}

export default function QuickActionsFab() {
    const [isOpen, setIsOpen] = useState(false);
    const [isVisible, setIsVisible] = useState(true);
    const router = useRouter();

    const actions: QuickAction[] = [
        {
            id: 'contact',
            label: 'New Contact',
            icon: UserPlus,
            color: 'from-blue-500 to-blue-600',
            action: () => {
                router.push('/contacts?action=new');
                toast.success('Opening new contact form...');
                setIsOpen(false);
            },
        },
        {
            id: 'lead',
            label: 'New Lead',
            icon: Target,
            color: 'from-green-500 to-green-600',
            action: () => {
                router.push('/leads?action=new');
                toast.success('Opening new lead form...');
                setIsOpen(false);
            },
        },
        {
            id: 'opportunity',
            label: 'New Deal',
            icon: FileText,
            color: 'from-purple-500 to-purple-600',
            action: () => {
                router.push('/opportunities?action=new');
                toast.success('Opening new deal form...');
                setIsOpen(false);
            },
        },
        {
            id: 'task',
            label: 'New Task',
            icon: ClipboardList,
            color: 'from-amber-500 to-amber-600',
            action: () => {
                router.push('/tasks?action=new');
                toast.success('Opening new task form...');
                setIsOpen(false);
            },
        },
        {
            id: 'call',
            label: 'Log Call',
            icon: Phone,
            color: 'from-teal-500 to-teal-600',
            action: () => {
                router.push('/communications?type=call');
                toast.success('Opening call log...');
                setIsOpen(false);
            },
        },
        {
            id: 'email',
            label: 'Send Email',
            icon: Mail,
            color: 'from-red-500 to-red-600',
            action: () => {
                router.push('/communications?type=email');
                toast.success('Opening email composer...');
                setIsOpen(false);
            },
        },
        {
            id: 'meeting',
            label: 'Schedule Meeting',
            icon: Calendar,
            color: 'from-indigo-500 to-indigo-600',
            action: () => {
                router.push('/scheduling');
                toast.success('Opening scheduler...');
                setIsOpen(false);
            },
        },
        {
            id: 'ai-assist',
            label: 'Ask AI',
            icon: Sparkles,
            color: 'from-pink-500 to-pink-600',
            action: () => {
                // Trigger AI assistant
                const event = new CustomEvent('open-ai-assistant');
                window.dispatchEvent(event);
                toast.success('Opening AI Assistant...');
                setIsOpen(false);
            },
        },
    ];

    // Hide FAB when scrolling down, show when scrolling up
    useEffect(() => {
        let lastScrollY = window.scrollY;

        const handleScroll = () => {
            const currentScrollY = window.scrollY;
            if (currentScrollY > lastScrollY && currentScrollY > 100) {
                setIsVisible(false);
                setIsOpen(false);
            } else {
                setIsVisible(true);
            }
            lastScrollY = currentScrollY;
        };

        window.addEventListener('scroll', handleScroll, { passive: true });
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    // Close on escape
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'Escape' && isOpen) {
                setIsOpen(false);
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [isOpen]);

    return (
        <>
            {/* Backdrop */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
                        onClick={() => setIsOpen(false)}
                    />
                )}
            </AnimatePresence>

            {/* FAB Container */}
            <motion.div
                initial={{ opacity: 0, scale: 0 }}
                animate={{
                    opacity: isVisible ? 1 : 0,
                    scale: isVisible ? 1 : 0,
                    y: isVisible ? 0 : 20,
                }}
                transition={{ type: 'spring', damping: 20, stiffness: 300 }}
                className="fixed bottom-6 right-6 z-50 flex flex-col-reverse items-center gap-3"
            >
                {/* Action buttons */}
                <AnimatePresence>
                    {isOpen && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="flex flex-col-reverse items-end gap-2 mb-2"
                        >
                            {actions.map((action, index) => (
                                <motion.div
                                    key={action.id}
                                    initial={{ opacity: 0, x: 20, scale: 0.8 }}
                                    animate={{
                                        opacity: 1,
                                        x: 0,
                                        scale: 1,
                                        transition: { delay: index * 0.05 },
                                    }}
                                    exit={{
                                        opacity: 0,
                                        x: 20,
                                        scale: 0.8,
                                        transition: { delay: (actions.length - index) * 0.03 },
                                    }}
                                    className="flex items-center gap-3"
                                >
                                    {/* Label */}
                                    <motion.span
                                        initial={{ opacity: 0, x: 10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        exit={{ opacity: 0, x: 10 }}
                                        className="px-3 py-1.5 bg-gray-900 dark:bg-gray-800 text-white text-sm font-medium rounded-lg shadow-lg whitespace-nowrap"
                                    >
                                        {action.label}
                                    </motion.span>

                                    {/* Button */}
                                    <motion.button
                                        whileHover={{ scale: 1.1 }}
                                        whileTap={{ scale: 0.95 }}
                                        onClick={action.action}
                                        className={`w-12 h-12 rounded-full bg-linear-to-br ${action.color} text-white shadow-lg hover:shadow-xl flex items-center justify-center transition-shadow`}
                                    >
                                        <action.icon className="w-5 h-5" />
                                    </motion.button>
                                </motion.div>
                            ))}
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Main FAB button */}
                <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setIsOpen(!isOpen)}
                    className={`w-14 h-14 rounded-full shadow-lg hover:shadow-xl flex items-center justify-center transition-all duration-300 ${isOpen
                            ? 'bg-gray-900 dark:bg-gray-700'
                            : 'bg-linear-to-br from-blue-600 to-purple-600'
                        }`}
                >
                    <motion.div
                        animate={{ rotate: isOpen ? 45 : 0 }}
                        transition={{ duration: 0.2 }}
                    >
                        {isOpen ? (
                            <X className="w-6 h-6 text-white" />
                        ) : (
                            <Plus className="w-6 h-6 text-white" />
                        )}
                    </motion.div>
                </motion.button>

                {/* Ripple effect on hover */}
                {!isOpen && (
                    <motion.div
                        className="absolute w-14 h-14 rounded-full bg-blue-600/20"
                        animate={{
                            scale: [1, 1.5, 1],
                            opacity: [0.5, 0, 0.5],
                        }}
                        transition={{
                            duration: 2,
                            repeat: Infinity,
                            repeatType: 'loop',
                        }}
                    />
                )}
            </motion.div>
        </>
    );
}

