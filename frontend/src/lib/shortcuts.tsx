'use client';

import React, { createContext, useContext, useEffect, useState, useCallback, ReactNode } from 'react';
// import { motion, AnimatePresence } from 'framer-motion';
import { Command } from 'cmdk';
import {
    Search, Home, Users, Target, CheckSquare,
    Calendar, Settings, Plus,
    FileText, Mail, ArrowRight,
} from 'lucide-react';
import { useRouter } from 'next/navigation';

import { Dialog, DialogContent } from '@/components/ui/dialog';
import { cn } from '@/lib/utils';

/**
 * Keyboard Shortcuts & Command Palette
 * 
 * Provides:
 * - Global keyboard shortcuts
 * - Command palette (Cmd+K)
 * - Quick navigation
 * - Action shortcuts
 */

interface Shortcut {
    id: string;
    keys: string[];
    description: string;
    action: () => void;
    category?: string;
    when?: () => boolean; // Conditional shortcut
}

interface ShortcutContextType {
    shortcuts: Shortcut[];
    registerShortcut: (shortcut: Shortcut) => void;
    unregisterShortcut: (id: string) => void;
    openCommandPalette: () => void;
    closeCommandPalette: () => void;
    isCommandPaletteOpen: boolean;
}

const ShortcutContext = createContext<ShortcutContextType | null>(null);

export function useShortcuts(): ShortcutContextType {
    const context = useContext(ShortcutContext);
    if (!context) {
        throw new Error('useShortcuts must be used within ShortcutProvider');
    }
    return context;
}

interface ShortcutProviderProps {
    children: ReactNode;
}

export function ShortcutProvider({ children }: ShortcutProviderProps): React.JSX.Element {
    const router = useRouter();
    const [shortcuts, setShortcuts] = useState<Shortcut[]>([]);
    const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);

    const registerShortcut = useCallback((shortcut: Shortcut) => {
        setShortcuts(prev => {
            // Replace if exists, otherwise add
            const exists = prev.findIndex(s => s.id === shortcut.id);
            if (exists >= 0) {
                const updated = [...prev];
                updated[exists] = shortcut;
                return updated;
            }
            return [...prev, shortcut];
        });
    }, []);

    const unregisterShortcut = useCallback((id: string) => {
        setShortcuts(prev => prev.filter(s => s.id !== id));
    }, []);

    const openCommandPalette = useCallback(() => {
        setIsCommandPaletteOpen(true);
    }, []);

    const closeCommandPalette = useCallback(() => {
        setIsCommandPaletteOpen(false);
    }, []);

    // Register default shortcuts
    useEffect(() => {
        const defaultShortcuts: Shortcut[] = [
            {
                id: 'command-palette',
                keys: ['Meta+k', 'Control+k'],
                description: 'Open command palette',
                category: 'General',
                action: openCommandPalette,
            },
            {
                id: 'go-home',
                keys: ['g', 'h'],
                description: 'Go to Dashboard',
                category: 'Navigation',
                action: () => router.push('/dashboard'),
            },
            {
                id: 'go-leads',
                keys: ['g', 'l'],
                description: 'Go to Leads',
                category: 'Navigation',
                action: () => router.push('/leads'),
            },
            {
                id: 'go-contacts',
                keys: ['g', 'c'],
                description: 'Go to Contacts',
                category: 'Navigation',
                action: () => router.push('/contacts'),
            },
            {
                id: 'go-opportunities',
                keys: ['g', 'o'],
                description: 'Go to Opportunities',
                category: 'Navigation',
                action: () => router.push('/opportunities'),
            },
            {
                id: 'go-tasks',
                keys: ['g', 't'],
                description: 'Go to Tasks',
                category: 'Navigation',
                action: () => router.push('/tasks'),
            },
            {
                id: 'go-settings',
                keys: ['g', 's'],
                description: 'Go to Settings',
                category: 'Navigation',
                action: () => router.push('/settings'),
            },
            {
                id: 'new-lead',
                keys: ['n', 'l'],
                description: 'Create new Lead',
                category: 'Actions',
                action: () => router.push('/leads/new'),
            },
            {
                id: 'new-task',
                keys: ['n', 't'],
                description: 'Create new Task',
                category: 'Actions',
                action: () => router.push('/tasks/new'),
            },
            {
                id: 'search',
                keys: ['/'],
                description: 'Focus search',
                category: 'General',
                action: () => {
                    const searchInput = document.querySelector('[data-search-input]') as HTMLInputElement;
                    if (searchInput) searchInput.focus();
                },
            },
            {
                id: 'escape',
                keys: ['Escape'],
                description: 'Close dialogs',
                category: 'General',
                action: closeCommandPalette,
            },
        ];

        defaultShortcuts.forEach(registerShortcut);

        return () => {
            defaultShortcuts.forEach(s => unregisterShortcut(s.id));
        };
    }, [registerShortcut, unregisterShortcut, openCommandPalette, closeCommandPalette, router]);

    // Handle keyboard events
    useEffect(() => {
        let keySequence: string[] = [];
        let sequenceTimeout: NodeJS.Timeout;

        const handleKeyDown = (e: KeyboardEvent) => {
            // Ignore if in input
            const target = e.target as HTMLElement;
            if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
                // Allow escape and command palette in inputs
                if (e.key !== 'Escape' && !(e.key === 'k' && (e.metaKey || e.ctrlKey))) {
                    return;
                }
            }

            // Build key string
            const keyParts: string[] = [];
            if (e.metaKey) keyParts.push('Meta');
            if (e.ctrlKey) keyParts.push('Control');
            if (e.altKey) keyParts.push('Alt');
            if (e.shiftKey) keyParts.push('Shift');

            const key = e.key.length === 1 ? e.key.toLowerCase() : e.key;
            keyParts.push(key);

            const keyString = keyParts.join('+');

            // Check single key shortcuts
            for (const shortcut of shortcuts) {
                if (shortcut.when && !shortcut.when()) continue;

                if (shortcut.keys.includes(keyString)) {
                    e.preventDefault();
                    shortcut.action();
                    return;
                }
            }

            // Handle sequence shortcuts (like g+h)
            keySequence.push(key);
            clearTimeout(sequenceTimeout);

            sequenceTimeout = setTimeout(() => {
                keySequence = [];
            }, 500);

            // Check sequence shortcuts
            if (keySequence.length >= 2) {
                for (const shortcut of shortcuts) {
                    if (shortcut.when && !shortcut.when()) continue;

                    const shortcutSequence = shortcut.keys;
                    if (shortcutSequence.length === keySequence.length) {
                        const matches = shortcutSequence.every((k, i) => k === keySequence[i]);
                        if (matches) {
                            e.preventDefault();
                            shortcut.action();
                            keySequence = [];
                            return;
                        }
                    }
                }
            }
        };

        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, [shortcuts]);

    return (
        <ShortcutContext.Provider
            value={{
                shortcuts,
                registerShortcut,
                unregisterShortcut,
                openCommandPalette,
                closeCommandPalette,
                isCommandPaletteOpen,
            }}
        >
            {children}
            <CommandPalette />
        </ShortcutContext.Provider>
    );
}

/**
 * Command Palette Component
 */
function CommandPalette() {
    const { isCommandPaletteOpen, closeCommandPalette } = useShortcuts();
    const router = useRouter();
    const [search, setSearch] = useState('');

    // Group shortcuts by category
    // const categories = shortcuts.reduce((acc, shortcut) => {
    //     const category = shortcut.category || 'Other';
    //     if (!acc[category]) acc[category] = [];
    //     acc[category].push(shortcut);
    //     return acc;
    // }, {} as Record<string, Shortcut[]>);

    const navigationItems = [
        { icon: Home, label: 'Dashboard', path: '/dashboard' },
        { icon: Users, label: 'Leads', path: '/leads' },
        { icon: Users, label: 'Contacts', path: '/contacts' },
        { icon: Target, label: 'Opportunities', path: '/opportunities' },
        { icon: CheckSquare, label: 'Tasks', path: '/tasks' },
        { icon: Calendar, label: 'Calendar', path: '/calendar' },
        { icon: Settings, label: 'Settings', path: '/settings' },
    ];

    const actionItems = [
        { icon: Plus, label: 'Create Lead', path: '/leads/new' },
        { icon: Plus, label: 'Create Contact', path: '/contacts/new' },
        { icon: Plus, label: 'Create Task', path: '/tasks/new' },
        { icon: Mail, label: 'Send Email', path: '/emails/compose' },
        { icon: FileText, label: 'Create Report', path: '/reports/new' },
    ];

    const handleSelect = (path: string) => {
        closeCommandPalette();
        router.push(path);
    };

    return (
        <Dialog open={isCommandPaletteOpen} onOpenChange={closeCommandPalette}>
            <DialogContent className="overflow-hidden p-0 shadow-2xl max-w-2xl">
                <Command className="rounded-lg border-0">
                    <div className="flex items-center border-b px-4">
                        <Search className="mr-2 h-4 w-4 shrink-0 opacity-50" />
                        <Command.Input
                            placeholder="Type a command or search..."
                            value={search}
                            onValueChange={setSearch}
                            className="flex h-12 w-full bg-transparent py-3 text-sm outline-none placeholder:text-gray-500"
                        />
                    </div>

                    <Command.List className="max-h-100 overflow-y-auto p-2">
                        <Command.Empty className="py-6 text-center text-sm text-gray-500">
                            No results found.
                        </Command.Empty>

                        {/* Navigation */}
                        <Command.Group heading="Navigation" className="**:[[cmdk-group-heading]]:text-xs **:[[cmdk-group-heading]]:font-semibold **:[[cmdk-group-heading]]:text-gray-500 **:[[cmdk-group-heading]]:px-2 **:[[cmdk-group-heading]]:py-1.5">
                            {navigationItems.map((item) => (
                                <Command.Item
                                    key={item.path}
                                    onSelect={() => handleSelect(item.path)}
                                    className="flex items-center gap-3 px-3 py-2 text-sm rounded-md cursor-pointer aria-selected:bg-blue-50 aria-selected:text-blue-900"
                                >
                                    <item.icon className="h-4 w-4" />
                                    <span>{item.label}</span>
                                    <ArrowRight className="ml-auto h-3 w-3 opacity-50" />
                                </Command.Item>
                            ))}
                        </Command.Group>

                        {/* Actions */}
                        <Command.Group heading="Quick Actions" className="**:[[cmdk-group-heading]]:text-xs **:[[cmdk-group-heading]]:font-semibold **:[[cmdk-group-heading]]:text-gray-500 **:[[cmdk-group-heading]]:px-2 **:[[cmdk-group-heading]]:py-1.5">
                            {actionItems.map((item) => (
                                <Command.Item
                                    key={item.path}
                                    onSelect={() => handleSelect(item.path)}
                                    className="flex items-center gap-3 px-3 py-2 text-sm rounded-md cursor-pointer aria-selected:bg-blue-50 aria-selected:text-blue-900"
                                >
                                    <item.icon className="h-4 w-4" />
                                    <span>{item.label}</span>
                                </Command.Item>
                            ))}
                        </Command.Group>

                        {/* Shortcuts Help */}
                        <Command.Group heading="Keyboard Shortcuts" className="**:[[cmdk-group-heading]]:text-xs **:[[cmdk-group-heading]]:font-semibold **:[[cmdk-group-heading]]:text-gray-500 **:[[cmdk-group-heading]]:px-2 **:[[cmdk-group-heading]]:py-1.5">
                            <Command.Item
                                onSelect={() => { /* TODO: show all shortcuts */ }}
                                className="flex items-center justify-between gap-3 px-3 py-2 text-sm rounded-md cursor-pointer aria-selected:bg-blue-50"
                            >
                                <span>Show all shortcuts</span>
                                <kbd className="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-gray-100 px-1.5 font-mono text-xs text-gray-600">
                                    ?
                                </kbd>
                            </Command.Item>
                        </Command.Group>
                    </Command.List>

                    {/* Footer */}
                    <div className="flex items-center justify-between border-t px-4 py-2 text-xs text-gray-500">
                        <div className="flex items-center gap-2">
                            <kbd className="rounded border bg-gray-100 px-1.5 py-0.5">↑↓</kbd>
                            <span>Navigate</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <kbd className="rounded border bg-gray-100 px-1.5 py-0.5">↵</kbd>
                            <span>Select</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <kbd className="rounded border bg-gray-100 px-1.5 py-0.5">esc</kbd>
                            <span>Close</span>
                        </div>
                    </div>
                </Command>
            </DialogContent>
        </Dialog>
    );
}

/**
 * Shortcut Display Component
 */
interface ShortcutKeyProps {
    keys: string | string[];
    className?: string;
}

export function ShortcutKey({ keys, className }: ShortcutKeyProps): React.JSX.Element {
    const keyArray = Array.isArray(keys) ? keys : [keys];

    const formatKey = (key: string) => {
        const replacements: Record<string, string> = {
            'Meta': '⌘',
            'Control': 'Ctrl',
            'Alt': '⌥',
            'Shift': '⇧',
            'ArrowUp': '↑',
            'ArrowDown': '↓',
            'ArrowLeft': '←',
            'ArrowRight': '→',
            'Enter': '↵',
            'Escape': 'Esc',
            'Backspace': '⌫',
        };

        return key.split('+').map(k => replacements[k] || k.toUpperCase()).join(' + ');
    };

    return (
        <span className={cn('flex items-center gap-1', className)}>
            {keyArray.map((key, i) => (
                <React.Fragment key={key}>
                    {i > 0 && <span className="text-gray-400">or</span>}
                    <kbd className="inline-flex h-5 select-none items-center gap-1 rounded border bg-gray-100 px-1.5 font-mono text-xs text-gray-600">
                        {formatKey(key)}
                    </kbd>
                </React.Fragment>
            ))}
        </span>
    );
}

/**
 * Shortcuts Help Modal
 */
export function ShortcutsHelpModal({ open, onOpenChange }: { open: boolean; onOpenChange: (open: boolean) => void }): React.JSX.Element {
    const { shortcuts } = useShortcuts();

    const categories = shortcuts.reduce((acc, shortcut) => {
        const category = shortcut.category || 'Other';
        if (!acc[category]) acc[category] = [];
        acc[category].push(shortcut);
        return acc;
    }, {} as Record<string, Shortcut[]>);

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-lg">
                <h2 className="text-lg font-semibold mb-4">Keyboard Shortcuts</h2>

                {Object.entries(categories).map(([category, categoryShortcuts]) => (
                    <div key={category} className="mb-6">
                        <h3 className="text-sm font-medium text-gray-500 mb-2">{category}</h3>
                        <div className="space-y-2">
                            {categoryShortcuts.map((shortcut) => (
                                <div
                                    key={shortcut.id}
                                    className="flex items-center justify-between py-1"
                                >
                                    <span className="text-sm">{shortcut.description}</span>
                                    <ShortcutKey keys={shortcut.keys} />
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
            </DialogContent>
        </Dialog>
    );
}

const Shortcuts = {
    ShortcutProvider,
    useShortcuts,
    ShortcutKey,
    ShortcutsHelpModal,
};

export default Shortcuts;

