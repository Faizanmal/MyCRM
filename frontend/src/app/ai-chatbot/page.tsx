'use client';

import { useState, useEffect, useRef } from 'react';
import { 
  Bot, 
  Send, 
  Plus, 
  Trash2, 
  MessageSquare, 
  Mail, 
  Database, 
  Lightbulb,
  ThumbsUp,
  ThumbsDown,
  Copy,
  RefreshCw,
  Sparkles,
  Clock,
  Zap
} from 'lucide-react';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { aiChatbotAPI } from '@/lib/api';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  feedback?: 'positive' | 'negative';
}

interface ChatSession {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

interface QuickAction {
  id: string;
  name: string;
  action_type: string;
  icon: string;
}

interface EmailTemplate {
  id: string;
  name: string;
  subject: string;
  body: string;
}

export default function AIChatbotPage() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSession, setActiveSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [quickActions, setQuickActions] = useState<QuickAction[]>([]);
  const [emailTemplates, setEmailTemplates] = useState<EmailTemplate[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadSessions();
    loadQuickActions();
    loadEmailTemplates();
    loadSuggestions();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadSessions = async () => {
    try {
      const data = await aiChatbotAPI.getSessions();
      setSessions(data.results || data || []);
    } catch (error) {
      console.error('Failed to load sessions:', error);
      // Set demo data
      setSessions([
        { id: '1', name: 'Sales Strategy Discussion', created_at: '2026-01-12T10:00:00Z', updated_at: '2026-01-12T14:30:00Z', message_count: 12 },
        { id: '2', name: 'Lead Analysis', created_at: '2026-01-11T09:00:00Z', updated_at: '2026-01-11T16:00:00Z', message_count: 8 },
        { id: '3', name: 'Email Drafts', created_at: '2026-01-10T11:00:00Z', updated_at: '2026-01-10T15:00:00Z', message_count: 5 },
      ]);
    }
  };

  const loadQuickActions = async () => {
    try {
      const data = await aiChatbotAPI.getQuickActions();
      setQuickActions(data.results || data || []);
    } catch (error) {
      console.error('Failed to load quick actions:', error);
      setQuickActions([
        { id: '1', name: 'Summarize Pipeline', action_type: 'query', icon: 'chart' },
        { id: '2', name: 'Draft Follow-up Email', action_type: 'email', icon: 'mail' },
        { id: '3', name: 'Find High-Value Leads', action_type: 'query', icon: 'search' },
        { id: '4', name: 'Weekly Report', action_type: 'report', icon: 'file' },
      ]);
    }
  };

  const loadEmailTemplates = async () => {
    try {
      const data = await aiChatbotAPI.getEmailTemplates();
      setEmailTemplates(data.results || data || []);
    } catch (error) {
      console.error('Failed to load email templates:', error);
      setEmailTemplates([
        { id: '1', name: 'Introduction Email', subject: 'Nice to meet you!', body: 'Hi {{name}},\n\nIt was great connecting with you...' },
        { id: '2', name: 'Follow-up Email', subject: 'Following up on our conversation', body: 'Hi {{name}},\n\nJust wanted to follow up...' },
        { id: '3', name: 'Meeting Request', subject: 'Can we schedule a call?', body: 'Hi {{name}},\n\nI would love to schedule...' },
      ]);
    }
  };

  const loadSuggestions = async () => {
    try {
      const data = await aiChatbotAPI.suggestActions();
      setSuggestions(data.suggestions || []);
    } catch (error) {
      console.error('Failed to load suggestions:', error);
      setSuggestions([
        'Review 5 leads that need follow-up today',
        'Check opportunities closing this week',
        'Analyze last month\'s conversion rate',
        'Draft proposal for pending deals',
      ]);
    }
  };

  const createNewSession = async () => {
    try {
      const newSession = await aiChatbotAPI.createSession('New Conversation');
      setSessions([newSession, ...sessions]);
      setActiveSession(newSession);
      setMessages([]);
    } catch (error) {
      console.error('Failed to create session:', error);
      const demoSession: ChatSession = {
        id: Date.now().toString(),
        name: 'New Conversation',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        message_count: 0,
      };
      setSessions([demoSession, ...sessions]);
      setActiveSession(demoSession);
      setMessages([]);
    }
  };

  const selectSession = async (session: ChatSession) => {
    setActiveSession(session);
    try {
      const data = await aiChatbotAPI.getSession(session.id);
      setMessages(data.messages || []);
    } catch (error) {
      console.error('Failed to load session messages:', error);
      // Demo messages
      setMessages([
        { id: '1', role: 'user', content: 'Can you summarize my sales pipeline?', timestamp: '2026-01-12T10:00:00Z' },
        { id: '2', role: 'assistant', content: 'Based on your current pipeline:\n\n📊 **Pipeline Summary**\n- Total Deals: 45\n- Total Value: $2.3M\n- Avg Deal Size: $51K\n\n**By Stage:**\n- Qualification: 12 deals ($450K)\n- Proposal: 18 deals ($920K)\n- Negotiation: 10 deals ($680K)\n- Closing: 5 deals ($250K)\n\nWould you like me to dive deeper into any stage?', timestamp: '2026-01-12T10:01:00Z' },
      ]);
    }
  };

  const deleteSession = async (sessionId: string) => {
    try {
      await aiChatbotAPI.deleteSession(sessionId);
      setSessions(sessions.filter(s => s.id !== sessionId));
      if (activeSession?.id === sessionId) {
        setActiveSession(null);
        setMessages([]);
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !activeSession) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages([...messages, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await aiChatbotAPI.sendMessage(activeSession.id, inputMessage);
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.message || response.content,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
      // Demo response
      const demoResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `I understand you're asking about: "${  inputMessage  }"\n\nLet me help you with that. Based on your CRM data, here are some insights I can provide...\n\nWould you like me to elaborate on any specific aspect?`,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, demoResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickAction = (action: QuickAction) => {
    setInputMessage(action.name);
    if (activeSession) {
      sendMessage();
    }
  };

  const handleSuggestion = (suggestion: string) => {
    setInputMessage(suggestion);
  };

  const provideFeedback = async (messageId: string, positive: boolean) => {
    try {
      await aiChatbotAPI.submitFeedback(messageId, positive ? 5 : 1);
      setMessages(messages.map(m => 
        m.id === messageId ? { ...m, feedback: positive ? 'positive' : 'negative' } : m
      ));
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const generateEmail = async (template: EmailTemplate) => {
    setIsLoading(true);
    try {
      const response = await aiChatbotAPI.generateEmail({ 
        context: template.body, 
        tone: 'professional' 
      });
      const assistantMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `📧 **Generated Email**\n\n**Subject:** ${response.subject || template.subject}\n\n${response.body || template.body}`,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Failed to generate email:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-4rem)] gap-4 p-4">
      {/* Sidebar - Sessions */}
      <Card className="w-80 flex flex-col">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg flex items-center gap-2">
              <Bot className="h-5 w-5" />
              AI Assistant
            </CardTitle>
            <Button size="sm" onClick={createNewSession}>
              <Plus className="h-4 w-4" />
            </Button>
          </div>
          <CardDescription>Your CRM AI companion</CardDescription>
        </CardHeader>
        <CardContent className="flex-1 overflow-hidden p-0">
          <ScrollArea className="h-full px-4">
            <div className="space-y-2 pb-4">
              {sessions.map((session) => (
                <div
                  key={session.id}
                  className={`flex items-center justify-between p-3 rounded-lg cursor-pointer transition-colors ${
                    activeSession?.id === session.id
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted/50 hover:bg-muted'
                  }`}
                  onClick={() => selectSession(session)}
                  onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { selectSession(session); e.preventDefault(); } }}
                  tabIndex={0}
                >
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{session.name}</p>
                    <p className="text-xs opacity-70">
                      {session.message_count} messages
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 w-8 p-0 opacity-0 group-hover:opacity-100"
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteSession(session.id);
                    }}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        <Card className="flex-1 flex flex-col">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-yellow-500" />
                  {activeSession?.name || 'Select a conversation'}
                </CardTitle>
                <CardDescription>
                  Powered by AI to help you work smarter
                </CardDescription>
              </div>
              {activeSession && (
                <Badge variant="outline" className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  Active
                </Badge>
              )}
            </div>
          </CardHeader>
          
          <Separator />
          
          <CardContent className="flex-1 overflow-hidden p-0">
            {activeSession ? (
              <ScrollArea className="h-full p-4">
                <div className="space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[80%] rounded-lg p-4 ${
                          message.role === 'user'
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-muted'
                        }`}
                      >
                        <div className="whitespace-pre-wrap">{message.content}</div>
                        {message.role === 'assistant' && (
                          <div className="flex items-center gap-2 mt-2 pt-2 border-t border-current/10">
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-6 px-2"
                              onClick={() => provideFeedback(message.id, true)}
                            >
                              <ThumbsUp className={`h-3 w-3 ${message.feedback === 'positive' ? 'fill-current' : ''}`} />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-6 px-2"
                              onClick={() => provideFeedback(message.id, false)}
                            >
                              <ThumbsDown className={`h-3 w-3 ${message.feedback === 'negative' ? 'fill-current' : ''}`} />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-6 px-2"
                              onClick={() => copyToClipboard(message.content)}
                            >
                              <Copy className="h-3 w-3" />
                            </Button>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                  {isLoading && (
                    <div className="flex justify-start">
                      <div className="bg-muted rounded-lg p-4">
                        <div className="flex items-center gap-2">
                          <RefreshCw className="h-4 w-4 animate-spin" />
                          <span>Thinking...</span>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              </ScrollArea>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-muted-foreground p-8">
                <Bot className="h-16 w-16 mb-4 opacity-50" />
                <h3 className="text-lg font-medium mb-2">Welcome to AI Assistant</h3>
                <p className="text-center mb-6">
                  Start a new conversation or select an existing one to get AI-powered insights about your CRM data.
                </p>
                <Button onClick={createNewSession}>
                  <Plus className="h-4 w-4 mr-2" />
                  Start New Conversation
                </Button>
              </div>
            )}
          </CardContent>

          {activeSession && (
            <>
              <Separator />
              <div className="p-4">
                {/* Suggestions */}
                {suggestions.length > 0 && messages.length === 0 && (
                  <div className="flex flex-wrap gap-2 mb-4">
                    {suggestions.map((suggestion, index) => (
                      <Button
                        key={index}
                        variant="outline"
                        size="sm"
                        className="text-xs"
                        onClick={() => handleSuggestion(suggestion)}
                      >
                        <Lightbulb className="h-3 w-3 mr-1" />
                        {suggestion}
                      </Button>
                    ))}
                  </div>
                )}
                
                {/* Input */}
                <div className="flex gap-2">
                  <Input
                    placeholder="Ask me anything about your CRM..."
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    disabled={isLoading}
                  />
                  <Button onClick={sendMessage} disabled={isLoading || !inputMessage.trim()}>
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </>
          )}
        </Card>
      </div>

      {/* Right Sidebar - Quick Actions & Templates */}
      <Card className="w-72">
        <Tabs defaultValue="actions">
          <CardHeader className="pb-2">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="actions" className="text-xs">
                <Zap className="h-3 w-3 mr-1" />
                Actions
              </TabsTrigger>
              <TabsTrigger value="templates" className="text-xs">
                <Mail className="h-3 w-3 mr-1" />
                Templates
              </TabsTrigger>
            </TabsList>
          </CardHeader>
          
          <CardContent className="p-0">
            <TabsContent value="actions" className="m-0">
              <ScrollArea className="h-[calc(100vh-16rem)] px-4">
                <div className="space-y-2 pb-4">
                  <p className="text-xs text-muted-foreground mb-2">Quick Actions</p>
                  {quickActions.map((action) => (
                    <Button
                      key={action.id}
                      variant="outline"
                      className="w-full justify-start"
                      onClick={() => handleQuickAction(action)}
                      disabled={!activeSession}
                    >
                      {action.action_type === 'query' && <Database className="h-4 w-4 mr-2" />}
                      {action.action_type === 'email' && <Mail className="h-4 w-4 mr-2" />}
                      {action.action_type === 'report' && <MessageSquare className="h-4 w-4 mr-2" />}
                      {action.name}
                    </Button>
                  ))}
                </div>
              </ScrollArea>
            </TabsContent>
            
            <TabsContent value="templates" className="m-0">
              <ScrollArea className="h-[calc(100vh-16rem)] px-4">
                <div className="space-y-2 pb-4">
                  <p className="text-xs text-muted-foreground mb-2">Email Templates</p>
                  {emailTemplates.map((template) => (
                    <Card key={template.id} className="cursor-pointer hover:bg-muted/50" onClick={() => generateEmail(template)}>
                      <CardContent className="p-3">
                        <p className="font-medium text-sm">{template.name}</p>
                        <p className="text-xs text-muted-foreground truncate">{template.subject}</p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </ScrollArea>
            </TabsContent>
          </CardContent>
        </Tabs>
      </Card>
    </div>
  );
}

