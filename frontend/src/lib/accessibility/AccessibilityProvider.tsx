'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback, useRef } from 'react';
// import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// Speech Recognition types
declare global {
  interface Window {
    SpeechRecognition: new () => SpeechRecognition;
    webkitSpeechRecognition: new () => SpeechRecognition;
  }
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onresult: (event: SpeechRecognitionEvent) => void;
  onerror: (event: SpeechRecognitionErrorEvent) => void;
  onend: () => void;
  start(): void;
  stop(): void;
  abort(): void;
}

interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
  message: string;
}

interface SpeechRecognitionResultList {
  readonly length: number;
  item(index: number): SpeechRecognitionResult;
  [index: number]: SpeechRecognitionResult;
}

interface SpeechRecognitionResult {
  readonly length: number;
  item(index: number): SpeechRecognitionAlternative;
  [index: number]: SpeechRecognitionAlternative;
  isFinal: boolean;
}

interface SpeechRecognitionAlternative {
  transcript: string;
  confidence: number;
}

// Types
interface AccessibilitySettings {
  // Visual
  highContrastMode: boolean;
  colorBlindMode: 'none' | 'protanopia' | 'deuteranopia' | 'tritanopia' | 'achromatopsia';
  fontSizeMultiplier: number;
  reduceMotion: boolean;
  reduceTransparency: boolean;
  dyslexiaFont: boolean;

  // Focus & Navigation
  enhancedFocusIndicators: boolean;
  keyboardShortcutsEnabled: boolean;
  skipLinksEnabled: boolean;

  // Screen Reader
  screenReaderMode: boolean;
  announceNotifications: boolean;
  announcePageChanges: boolean;

  // Voice Control
  voiceCommandsEnabled: boolean;
  voiceLanguage: string;

  // Cognitive
  simplifiedInterface: boolean;
  extendedTimeouts: boolean;
  readingMask: boolean;
}

interface VoiceCommand {
  phrase: string;
  aliases: string[];
  action: string;
  handler: () => void;
}

interface KeyboardShortcut {
  id: string;
  name: string;
  keys: string;
  action: string;
  handler: () => void;
  scope: string;
}

interface AccessibilityContextType {
  settings: AccessibilitySettings;
  updateSettings: (updates: Partial<AccessibilitySettings>) => void;
  announce: (message: string, priority?: 'polite' | 'assertive') => void;
  registerVoiceCommand: (command: VoiceCommand) => void;
  unregisterVoiceCommand: (phrase: string) => void;
  registerShortcut: (shortcut: KeyboardShortcut) => void;
  unregisterShortcut: (id: string) => void;
  startVoiceListening: () => void;
  stopVoiceListening: () => void;
  isVoiceListening: boolean;
  focusTrap: (containerId: string) => void;
  releaseFocusTrap: () => void;
}

const defaultSettings: AccessibilitySettings = {
  highContrastMode: false,
  colorBlindMode: 'none',
  fontSizeMultiplier: 1.0,
  reduceMotion: false,
  reduceTransparency: false,
  dyslexiaFont: false,
  enhancedFocusIndicators: true,
  keyboardShortcutsEnabled: true,
  skipLinksEnabled: true,
  screenReaderMode: false,
  announceNotifications: true,
  announcePageChanges: true,
  voiceCommandsEnabled: false,
  voiceLanguage: 'en-US',
  simplifiedInterface: false,
  extendedTimeouts: false,
  readingMask: false,
};

// Context
const AccessibilityContext = createContext<AccessibilityContextType | null>(null);

// Live Region for Screen Readers
const LiveRegion: React.FC<{ message: string; priority: 'polite' | 'assertive' }> = ({
  message,
  priority,
}) => (
  <div
    role="status"
    aria-live={priority}
    aria-atomic="true"
    className="sr-only"
  >
    {message}
  </div>
);

// Provider
export function AccessibilityProvider({ children }: { children: ReactNode }) {
  const [settings, setSettings] = useState<AccessibilitySettings>(defaultSettings);
  const [announcement, setAnnouncement] = useState({ message: '', priority: 'polite' as 'polite' | 'assertive' });
  const [voiceCommands, setVoiceCommands] = useState<Map<string, VoiceCommand>>(new Map());
  const [shortcuts, setShortcuts] = useState<Map<string, KeyboardShortcut>>(new Map());
  const [isVoiceListening, setIsVoiceListening] = useState(false);
  const [focusTrapContainer, setFocusTrapContainer] = useState<string | null>(null);
  
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  // Apply settings to DOM
  useEffect(() => {
    const root = document.documentElement;
    
    // High contrast
    root.classList.toggle('high-contrast', settings.highContrastMode);
    
    // Color blind mode
    root.dataset.colorBlind = settings.colorBlindMode;
    
    // Font size
    root.style.setProperty('--font-size-multiplier', settings.fontSizeMultiplier.toString());
    
    // Reduce motion
    if (settings.reduceMotion) {
      root.style.setProperty('--transition-duration', '0s');
      root.style.setProperty('--animation-duration', '0s');
    } else {
      root.style.removeProperty('--transition-duration');
      root.style.removeProperty('--animation-duration');
    }
    
    // Reduce transparency
    root.classList.toggle('reduce-transparency', settings.reduceTransparency);
    
    // Dyslexia font
    root.classList.toggle('dyslexia-font', settings.dyslexiaFont);
    
    // Enhanced focus
    root.classList.toggle('enhanced-focus', settings.enhancedFocusIndicators);
    
    // Screen reader mode
    root.classList.toggle('screen-reader-mode', settings.screenReaderMode);
    
    // Simplified interface
    root.classList.toggle('simplified-ui', settings.simplifiedInterface);

    // Reading mask
    root.classList.toggle('reading-mask', settings.readingMask);
  }, [settings]);

  // Keyboard shortcuts handler
  useEffect(() => {
    if (!settings.keyboardShortcutsEnabled) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      const keys: string[] = [];
      if (e.ctrlKey || e.metaKey) keys.push('Ctrl');
      if (e.altKey) keys.push('Alt');
      if (e.shiftKey) keys.push('Shift');
      keys.push(e.key.toUpperCase());
      
      const combination = keys.join('+');
      
      shortcuts.forEach((shortcut) => {
        if (shortcut.keys.toUpperCase() === combination) {
          e.preventDefault();
          shortcut.handler();
        }
      });
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [settings.keyboardShortcutsEnabled, shortcuts]);

  const announce = useCallback((message: string, priority: 'polite' | 'assertive' = 'polite') => {
    setAnnouncement({ message: '', priority });
    setTimeout(() => setAnnouncement({ message, priority }), 100);
  }, []);

  // Voice recognition setup
  useEffect(() => {
    if (!settings.voiceCommandsEnabled) return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.lang = settings.voiceLanguage;

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      const transcript = event.results[event.results.length - 1][0].transcript.toLowerCase().trim();
      
      voiceCommands.forEach((command) => {
        const phrases = [command.phrase.toLowerCase(), ...command.aliases.map(a => a.toLowerCase())];
        if (phrases.some(p => transcript.includes(p))) {
          command.handler();
          announce(`Executing: ${command.action}`);
        }
      });
    };

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      console.error('Voice recognition error:', event.error);
      setIsVoiceListening(false);
    };

    recognitionRef.current = recognition;

    return () => {
      recognition.stop();
    };
  }, [settings.voiceCommandsEnabled, settings.voiceLanguage, voiceCommands, announce]);

  // Focus trap implementation
  useEffect(() => {
    if (!focusTrapContainer) return;

    const container = document.getElementById(focusTrapContainer);
    if (!container) return;

    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

    const handleTab = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement?.focus();
        }
      } else {
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement?.focus();
        }
      }
    };

    container.addEventListener('keydown', handleTab);
    firstElement?.focus();

    return () => {
      container.removeEventListener('keydown', handleTab);
    };
  }, [focusTrapContainer]);

  const updateSettings = useCallback((updates: Partial<AccessibilitySettings>) => {
    setSettings((prev) => ({ ...prev, ...updates }));
  }, []);

  const registerVoiceCommand = useCallback((command: VoiceCommand) => {
    setVoiceCommands((prev) => new Map(prev).set(command.phrase, command));
  }, []);

  const unregisterVoiceCommand = useCallback((phrase: string) => {
    setVoiceCommands((prev) => {
      const next = new Map(prev);
      next.delete(phrase);
      return next;
    });
  }, []);

  const registerShortcut = useCallback((shortcut: KeyboardShortcut) => {
    setShortcuts((prev) => new Map(prev).set(shortcut.id, shortcut));
  }, []);

  const unregisterShortcut = useCallback((id: string) => {
    setShortcuts((prev) => {
      const next = new Map(prev);
      next.delete(id);
      return next;
    });
  }, []);

  const startVoiceListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.start();
      setIsVoiceListening(true);
      announce('Voice commands activated');
    }
  }, [announce]);

  const stopVoiceListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setIsVoiceListening(false);
      announce('Voice commands deactivated');
    }
  }, [announce]);

  const focusTrap = useCallback((containerId: string) => {
    setFocusTrapContainer(containerId);
  }, []);

  const releaseFocusTrap = useCallback(() => {
    setFocusTrapContainer(null);
  }, []);

  const value: AccessibilityContextType = {
    settings,
    updateSettings,
    announce,
    registerVoiceCommand,
    unregisterVoiceCommand,
    registerShortcut,
    unregisterShortcut,
    startVoiceListening,
    stopVoiceListening,
    isVoiceListening,
    focusTrap,
    releaseFocusTrap,
  };

  return (
    <AccessibilityContext.Provider value={value}>
      {settings.skipLinksEnabled && <SkipLinks />}
      <LiveRegion message={announcement.message} priority={announcement.priority} />
      {settings.readingMask && <ReadingMask />}
      {children}
    </AccessibilityContext.Provider>
  );
}

// Skip Links Component
const SkipLinks: React.FC = () => (
  <nav className="skip-links" aria-label="Skip links">
    <a href="#main-content" className="skip-link">
      Skip to main content
    </a>
    <a href="#main-navigation" className="skip-link">
      Skip to navigation
    </a>
    <a href="#search" className="skip-link">
      Skip to search
    </a>
  </nav>
);

// Reading Mask Component
const ReadingMask: React.FC = () => {
  const [position, setPosition] = useState({ y: 0 });
  const maskHeight = 100;

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setPosition({ y: e.clientY });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return (
    <>
      <div
        className="fixed inset-x-0 top-0 bg-black/60 pointer-events-none z-50"
        style={{ height: position.y - maskHeight / 2 }}
      />
      <div
        className="fixed inset-x-0 bottom-0 bg-black/60 pointer-events-none z-50"
        style={{ top: position.y + maskHeight / 2 }}
      />
    </>
  );
};

// Hook
export function useAccessibility(): AccessibilityContextType {
  const context = useContext(AccessibilityContext);
  if (!context) {
    throw new Error('useAccessibility must be used within an AccessibilityProvider');
  }
  return context;
}

// Utility Hooks
export function useAnnounce() {
  const { announce } = useAccessibility();
  return announce;
}

export function useVoiceCommand(phrase: string, aliases: string[], action: string, handler: () => void) {
  const { registerVoiceCommand, unregisterVoiceCommand } = useAccessibility();

  useEffect(() => {
    registerVoiceCommand({ phrase, aliases, action, handler });
    return () => unregisterVoiceCommand(phrase);
  }, [phrase, aliases, action, handler, registerVoiceCommand, unregisterVoiceCommand]);
}

export function useKeyboardShortcut(
  id: string,
  name: string,
  keys: string,
  action: string,
  handler: () => void,
  scope: string = 'global'
) {
  const { registerShortcut, unregisterShortcut } = useAccessibility();

  useEffect(() => {
    registerShortcut({ id, name, keys, action, handler, scope });
    return () => unregisterShortcut(id);
  }, [id, name, keys, action, handler, scope, registerShortcut, unregisterShortcut]);
}

