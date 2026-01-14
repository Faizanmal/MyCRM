'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Bot,
    X,
    Send,
    Sparkles,
    Minimize2,
    Maximize2,
    Lightbulb,
    TrendingUp,
    Users,
    Calendar,
    BarChart3,
    RefreshCw,
    Copy,
    ThumbsUp,
    ThumbsDown,
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    suggestions?: string[];
    isTyping?: boolean;
}

const quickPrompts = [
    { icon: TrendingUp, label: 'Sales tips', prompt: 'Give me tips to improve my sales performance' },
    { icon: Users, label: 'Lead follow-up', prompt: 'Help me write a follow-up email for a lead' },
    { icon: Calendar, label: 'Meeting prep', prompt: 'Help me prepare for my next sales meeting' },
    { icon: BarChart3, label: 'Analyze data', prompt: 'Analyze my sales pipeline performance' },
];

const suggestedResponses = [
    'What leads should I prioritize today?',
    'Help me draft an email to a prospect',
    'Show me my top opportunities',
    'What tasks are overdue?',
    'Generate a sales report summary',
];

const aiResponses: Record<string, string> = {
    default: "I'm your AI sales assistant! I can help you with lead prioritization, email drafts, sales insights, and more. What would you like to know?",
    sales: "Based on your pipeline data, here are my top recommendations:\n\n1. **Follow up with high-value leads** - You have 3 leads with scores above 80 that haven't been contacted in 3+ days\n\n2. **Close pending opportunities** - 2 opportunities are in the final stage and need attention\n\n3. **Schedule demos** - Your conversion rate from demo to close is 45%, consider scheduling more demos this week",
    email: "Here's a draft follow-up email:\n\n**Subject: Following up on our conversation**\n\nHi [Name],\n\nI wanted to follow up on our recent discussion about [topic]. I believe our solution could really help you achieve [specific goal].\n\nWould you have 15 minutes this week for a quick call to discuss next steps?\n\nBest regards,\n[Your name]",
    meeting: "Here's a meeting preparation checklist:\n\n✅ **Research** - Review the prospect's company and recent news\n✅ **Objectives** - Define 3 key goals for the meeting\n✅ **Questions** - Prepare discovery questions\n✅ **Demo** - Customize your demo to their use case\n✅ **Next steps** - Plan your closing strategy",
    pipeline: "📊 **Pipeline Analysis**\n\n• Total opportunities: 24\n• Total value: $1.2M\n• Win rate: 32%\n• Average deal size: $48K\n\n**Key Insights:**\n- Deals are slowing down in the 'Proposal' stage\n- Your best performing product line is Enterprise\n- Consider focusing on the Financial Services sector",
};

export default function FloatingAIAssistant() {
    const [isOpen, setIsOpen] = useState(false);
    const [isMinimized, setIsMinimized] = useState(false);
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    // Focus input when chat opens
    useEffect(() => {
        if (isOpen && !isMinimized && inputRef.current) {
            setTimeout(() => inputRef.current?.focus(), 100);
        }
    }, [isOpen, isMinimized]);

    const generateResponse = useCallback((userMessage: string): string => {
        const lowerMessage = userMessage.toLowerCase();

        if (lowerMessage.includes('sales') || lowerMessage.includes('tip') || lowerMessage.includes('performance')) {
            return aiResponses.sales;
        }
        if (lowerMessage.includes('email') || lowerMessage.includes('follow') || lowerMessage.includes('draft')) {
            return aiResponses.email;
        }
        if (lowerMessage.includes('meeting') || lowerMessage.includes('prep') || lowerMessage.includes('prepare')) {
            return aiResponses.meeting;
        }
        if (lowerMessage.includes('pipeline') || lowerMessage.includes('analyz') || lowerMessage.includes('data') || lowerMessage.includes('report')) {
            return aiResponses.pipeline;
        }

        return aiResponses.default;
    }, []);

    const handleSend = useCallback(async (messageText?: string) => {
        const text = messageText || input.trim();
        if (!text || isLoading) return;

        const userMessage: Message = {
            id: `user-${Date.now()}`,
            role: 'user',
            content: text,
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        // Simulate AI thinking with typing indicator
        const typingMessage: Message = {
            id: `typing-${Date.now()}`,
            role: 'assistant',
            content: '',
            timestamp: new Date(),
            isTyping: true,
        };
        setMessages(prev => [...prev, typingMessage]);

        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000));

        const response = generateResponse(text);

        setMessages(prev => {
            const withoutTyping = prev.filter(m => !m.isTyping);
            return [...withoutTyping, {
                id: `assistant-${Date.now()}`,
                role: 'assistant',
                content: response,
                timestamp: new Date(),
                suggestions: Math.random() > 0.5 ? suggestedResponses.slice(0, 3) : undefined,
            }];
        });

        setIsLoading(false);
    }, [input, isLoading, generateResponse]);

    const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    }, [handleSend]);

    const handleQuickPrompt = useCallback((prompt: string) => {
        handleSend(prompt);
    }, [handleSend]);

    const clearChat = useCallback(() => {
        setMessages([]);
    }, []);

    return (
        <>
            {/* Floating Button */}
            <AnimatePresence>
                {!isOpen && (
                    <motion.div
                        initial={{ scale: 0, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0, opacity: 0 }}
                        className="fixed bottom-6 right-6 z-50"
                    >
                        <Button
                            onClick={() => setIsOpen(true)}
                            className={cn(
                                "h-14 w-14 rounded-full shadow-lg hover:shadow-xl transition-all duration-300",
                                "bg-linear-to-br from-purple-600 via-blue-600 to-indigo-600 hover:from-purple-500 hover:via-blue-500 hover:to-indigo-500",
                                "border-2 border-white/20"
                            )}
                        >
                            <Bot className="h-6 w-6 text-white" />
                            {!isOpen && (
                                <span className="absolute -top-1 -right-1 h-4 w-4">
                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-400 opacity-75"></span>
                                    <span className="relative inline-flex rounded-full h-4 w-4 bg-purple-500 border-2 border-white"></span>
                                </span>
                            )}
                        </Button>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Chat Window */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: 20, scale: 0.95 }}
                        animate={{
                            opacity: 1,
                            y: 0,
                            scale: 1,
                            height: isMinimized ? 'auto' : 'auto',
                        }}
                        exit={{ opacity: 0, y: 20, scale: 0.95 }}
                        transition={{ duration: 0.2 }}
                        className={cn(
                            "fixed bottom-6 right-6 z-50 w-100 rounded-2xl shadow-2xl overflow-hidden",
                            "bg-background/95 backdrop-blur-xl border border-border/50",
                            "dark:bg-gray-900/95"
                        )}
                    >
                        {/* Header */}
                        <div className="flex items-center justify-between p-4 bg-linear-to-r from-purple-600 via-blue-600 to-indigo-600">
                            <div className="flex items-center gap-3">
                                <div className="h-10 w-10 rounded-full bg-white/20 flex items-center justify-center">
                                    <Sparkles className="h-5 w-5 text-white" />
                                </div>
                                <div>
                                    <h3 className="font-semibold text-white">AI Assistant</h3>
                                    <p className="text-xs text-white/70">Always here to help</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-1">
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    onClick={() => setIsMinimized(!isMinimized)}
                                    className="text-white hover:bg-white/20 h-8 w-8"
                                >
                                    {isMinimized ? <Maximize2 className="h-4 w-4" /> : <Minimize2 className="h-4 w-4" />}
                                </Button>
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    onClick={() => setIsOpen(false)}
                                    className="text-white hover:bg-white/20 h-8 w-8"
                                >
                                    <X className="h-4 w-4" />
                                </Button>
                            </div>
                        </div>

                        {/* Chat Content - Hidden when minimized */}
                        <AnimatePresence>
                            {!isMinimized && (
                                <motion.div
                                    initial={{ height: 0, opacity: 0 }}
                                    animate={{ height: 'auto', opacity: 1 }}
                                    exit={{ height: 0, opacity: 0 }}
                                    transition={{ duration: 0.2 }}
                                >
                                    {/* Messages Area */}
                                    <ScrollArea className="h-[350px] p-4" ref={scrollRef}>
                                        {messages.length === 0 ? (
                                            <div className="space-y-4">
                                                {/* Welcome Message */}
                                                <div className="text-center py-4">
                                                    <div className="h-16 w-16 rounded-full bg-linear-to-br from-purple-100 to-blue-100 dark:from-purple-900/30 dark:to-blue-900/30 flex items-center justify-center mx-auto mb-3">
                                                        <Lightbulb className="h-8 w-8 text-purple-600 dark:text-purple-400" />
                                                    </div>
                                                    <h4 className="font-semibold mb-1">Hi! I&apos;m your AI Sales Assistant</h4>
                                                    <p className="text-sm text-muted-foreground">
                                                        Ask me anything about your sales, leads, or get help with tasks
                                                    </p>
                                                </div>

                                                {/* Quick Prompts */}
                                                <div className="grid grid-cols-2 gap-2">
                                                    {quickPrompts.map((item, index) => (
                                                        <button
                                                            key={index}
                                                            onClick={() => handleQuickPrompt(item.prompt)}
                                                            className="flex items-center gap-2 p-3 rounded-xl border border-border/50 hover:bg-accent/50 transition-colors text-left"
                                                        >
                                                            <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                                                                <item.icon className="h-4 w-4 text-primary" />
                                                            </div>
                                                            <span className="text-sm font-medium">{item.label}</span>
                                                        </button>
                                                    ))}
                                                </div>
                                            </div>
                                        ) : (
                                            <div className="space-y-4">
                                                {messages.map((message) => (
                                                    <div
                                                        key={message.id}
                                                        className={cn(
                                                            "flex gap-3",
                                                            message.role === 'user' ? 'justify-end' : 'justify-start'
                                                        )}
                                                    >
                                                        {message.role === 'assistant' && (
                                                            <div className="h-8 w-8 rounded-full bg-linear-to-br from-purple-500 to-blue-500 flex items-center justify-center shrink-0">
                                                                <Bot className="h-4 w-4 text-white" />
                                                            </div>
                                                        )}
                                                        <div
                                                            className={cn(
                                                                "max-w-[80%] rounded-2xl px-4 py-2.5",
                                                                message.role === 'user'
                                                                    ? 'bg-primary text-primary-foreground'
                                                                    : 'bg-muted'
                                                            )}
                                                        >
                                                            {message.isTyping ? (
                                                                <div className="flex gap-1 py-1">
                                                                    <span className="w-2 h-2 rounded-full bg-current animate-bounce" style={{ animationDelay: '0ms' }} />
                                                                    <span className="w-2 h-2 rounded-full bg-current animate-bounce" style={{ animationDelay: '150ms' }} />
                                                                    <span className="w-2 h-2 rounded-full bg-current animate-bounce" style={{ animationDelay: '300ms' }} />
                                                                </div>
                                                            ) : (
                                                                <>
                                                                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>

                                                                    {/* Message Actions for AI responses */}
                                                                    {message.role === 'assistant' && !message.isTyping && (
                                                                        <div className="flex items-center gap-1 mt-2 pt-2 border-t border-border/30">
                                                                            <Button variant="ghost" size="icon" className="h-6 w-6">
                                                                                <Copy className="h-3 w-3" />
                                                                            </Button>
                                                                            <Button variant="ghost" size="icon" className="h-6 w-6">
                                                                                <ThumbsUp className="h-3 w-3" />
                                                                            </Button>
                                                                            <Button variant="ghost" size="icon" className="h-6 w-6">
                                                                                <ThumbsDown className="h-3 w-3" />
                                                                            </Button>
                                                                        </div>
                                                                    )}

                                                                    {/* Suggestions */}
                                                                    {message.suggestions && message.suggestions.length > 0 && (
                                                                        <div className="flex flex-wrap gap-1.5 mt-3">
                                                                            {message.suggestions.map((suggestion, idx) => (
                                                                                <Badge
                                                                                    key={idx}
                                                                                    variant="secondary"
                                                                                    className="cursor-pointer hover:bg-secondary/80 text-xs"
                                                                                    onClick={() => handleSend(suggestion)}
                                                                                >
                                                                                    {suggestion}
                                                                                </Badge>
                                                                            ))}
                                                                        </div>
                                                                    )}
                                                                </>
                                                            )}
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </ScrollArea>

                                    {/* Input Area */}
                                    <div className="p-4 border-t border-border/50">
                                        <div className="flex items-center gap-2">
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                onClick={clearChat}
                                                className="h-9 w-9 shrink-0"
                                                title="Clear chat"
                                            >
                                                <RefreshCw className="h-4 w-4" />
                                            </Button>
                                            <div className="relative flex-1">
                                                <Input
                                                    ref={inputRef}
                                                    value={input}
                                                    onChange={(e) => setInput(e.target.value)}
                                                    onKeyPress={handleKeyPress}
                                                    placeholder="Ask me anything..."
                                                    className="pr-10 rounded-xl"
                                                    disabled={isLoading}
                                                />
                                                <Button
                                                    size="icon"
                                                    onClick={() => handleSend()}
                                                    disabled={!input.trim() || isLoading}
                                                    className="absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7 rounded-lg"
                                                >
                                                    {isLoading ? (
                                                        <RefreshCw className="h-4 w-4 animate-spin" />
                                                    ) : (
                                                        <Send className="h-4 w-4" />
                                                    )}
                                                </Button>
                                            </div>
                                        </div>
                                        <p className="text-[10px] text-muted-foreground text-center mt-2">
                                            AI responses are generated and may not be 100% accurate
                                        </p>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
}

