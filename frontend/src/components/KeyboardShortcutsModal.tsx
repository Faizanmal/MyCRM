'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Keyboard, Search, User, Calendar, Moon, ArrowUp, CornerDownLeft, X as XIcon } from 'lucide-react';

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
// import { Badge } from '@/components/ui/badge';

interface ShortcutGroup {
    title: string;
    shortcuts: {
        keys: string[];
        description: string;
        icon?: React.ElementType;
    }[];
}

const shortcutGroups: ShortcutGroup[] = [
    {
        title: 'Navigation',
        shortcuts: [
            { keys: ['⌘', 'K'], description: 'Open command palette', icon: Search },
            { keys: ['G', 'D'], description: 'Go to Dashboard' },
            { keys: ['G', 'L'], description: 'Go to Leads' },
            { keys: ['G', 'C'], description: 'Go to Contacts' },
            { keys: ['G', 'O'], description: 'Go to Opportunities' },
            { keys: ['G', 'T'], description: 'Go to Tasks' },
        ],
    },
    {
        title: 'Quick Actions',
        shortcuts: [
            { keys: ['⌘', 'N'], description: 'Create new lead', icon: User },
            { keys: ['⌘', 'T'], description: 'Create new task', icon: Calendar },
            { keys: ['⌘', 'I'], description: 'Open AI Assistant' },
            { keys: ['⌘', 'D'], description: 'Toggle dark/light mode', icon: Moon },
        ],
    },
    {
        title: 'Command Palette',
        shortcuts: [
            { keys: ['↑', '↓'], description: 'Navigate items', icon: ArrowUp },
            { keys: ['↵'], description: 'Select item', icon: CornerDownLeft },
            { keys: ['Esc'], description: 'Close palette', icon: XIcon },
        ],
    },
    {
        title: 'General',
        shortcuts: [
            { keys: ['?'], description: 'Show this help' },
            { keys: ['Esc'], description: 'Close dialogs/modals' },
        ],
    },
];

export default function KeyboardShortcutsModal() {
    const [isOpen, setIsOpen] = useState(false);

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            // Show shortcuts modal on ?
            if (e.key === '?' && !e.metaKey && !e.ctrlKey && !e.altKey) {
                const activeElement = document.activeElement;
                const isInput = activeElement instanceof HTMLInputElement ||
                    activeElement instanceof HTMLTextAreaElement ||
                    activeElement?.getAttribute('contenteditable') === 'true';

                if (!isInput) {
                    e.preventDefault();
                    setIsOpen(true);
                }
            }
        };

        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, []);

    return (
        <Dialog open={isOpen} onOpenChange={setIsOpen}>
            <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2">
                        <Keyboard className="h-5 w-5" />
                        Keyboard Shortcuts
                    </DialogTitle>
                    <DialogDescription>
                        Use these shortcuts to navigate and take actions quickly
                    </DialogDescription>
                </DialogHeader>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 py-4">
                    {shortcutGroups.map((group, groupIndex) => (
                        <motion.div
                            key={group.title}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: groupIndex * 0.1 }}
                            className="space-y-3"
                        >
                            <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
                                {group.title}
                            </h3>
                            <div className="space-y-2">
                                {group.shortcuts.map((shortcut, index) => (
                                    <motion.div
                                        key={index}
                                        initial={{ opacity: 0, x: -10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: groupIndex * 0.1 + index * 0.05 }}
                                        className="flex items-center justify-between p-2 rounded-lg hover:bg-accent/50 transition-colors"
                                    >
                                        <span className="text-sm flex items-center gap-2">
                                            {shortcut.icon && <shortcut.icon className="h-4 w-4 text-muted-foreground" />}
                                            {shortcut.description}
                                        </span>
                                        <div className="flex items-center gap-1">
                                            {shortcut.keys.map((key, keyIndex) => (
                                                <span key={keyIndex}>
                                                    <kbd className="min-w-[24px] h-6 px-1.5 inline-flex items-center justify-center rounded border border-border bg-muted text-xs font-medium">
                                                        {key}
                                                    </kbd>
                                                    {keyIndex < shortcut.keys.length - 1 && (
                                                        <span className="mx-0.5 text-muted-foreground text-xs">+</span>
                                                    )}
                                                </span>
                                            ))}
                                        </div>
                                    </motion.div>
                                ))}
                            </div>
                        </motion.div>
                    ))}
                </div>

                <div className="flex items-center justify-center pt-4 border-t">
                    <p className="text-xs text-muted-foreground flex items-center gap-2">
                        <kbd className="px-1.5 py-0.5 rounded border border-border bg-muted text-xs">?</kbd>
                        Press anywhere to show this dialog
                    </p>
                </div>
            </DialogContent>
        </Dialog>
    );
}

