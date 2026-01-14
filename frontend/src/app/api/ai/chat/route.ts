/**
 * AI Chat API Route
 * ==================
 * 
 * AI assistant chat endpoint with context-aware responses
 */

import { NextRequest, NextResponse } from 'next/server';

const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:8000/api/ai';

interface ChatRequest {
  message: string;
  context?: {
    leadId?: string;
    contactId?: string;
    opportunityId?: string;
    dealValue?: number;
    companyName?: string;
    contactName?: string;
  };
  history?: {
    role: 'user' | 'assistant';
    content: string;
  }[];
}

interface AIAction {
  id: string;
  label: string;
  icon: string;
  action: string;
  params?: Record<string, unknown>;
}

interface ChatResponse {
  response: string;
  type?: 'text' | 'email' | 'summary' | 'insights' | 'meeting_prep';
  suggestions?: string[];
  actions?: AIAction[];
  metadata?: Record<string, unknown>;
}

export async function POST(request: NextRequest) {
  try {
    const body: ChatRequest = await request.json();
    const authHeader = request.headers.get('authorization');

    if (!authHeader) {
      return NextResponse.json(
        { error: 'Authentication required' },
        { status: 401 }
      );
    }

    // Analyze intent from message
    const intent = analyzeIntent(body.message);

    // Forward to AI service
    const response = await fetch(`${AI_SERVICE_URL}/chat/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: authHeader,
      },
      body: JSON.stringify({
        message: body.message,
        context: body.context,
        history: body.history,
        intent,
      }),
    });

    if (!response.ok) {
      // Fallback to local processing if AI service is unavailable
      const fallbackResponse = generateFallbackResponse(body.message, intent);
      return NextResponse.json(fallbackResponse);
    }

    const data: ChatResponse = await response.json();

    // Enhance response with suggestions based on intent
    const enhancedResponse = {
      ...data,
      suggestions: data.suggestions || generateSuggestions(intent),
      actions: data.actions || generateActions(intent, body.context),
    };

    return NextResponse.json(enhancedResponse);
  } catch (error) {
    console.error('[AI Chat] Error:', error);
    return NextResponse.json(
      {
        response: "I'm sorry, I encountered an error. Please try again.",
        type: 'text',
        suggestions: ['Try again', 'Ask a different question'],
      },
      { status: 500 }
    );
  }
}

// Intent analysis
type Intent =
  | 'draft_email'
  | 'meeting_prep'
  | 'deal_analysis'
  | 'ai_insights'
  | 'task_management'
  | 'search'
  | 'general';

function analyzeIntent(message: string): Intent {
  const lowerMessage = message.toLowerCase();

  if (
    lowerMessage.includes('email') ||
    lowerMessage.includes('draft') ||
    lowerMessage.includes('write')
  ) {
    return 'draft_email';
  }

  if (
    lowerMessage.includes('meeting') ||
    lowerMessage.includes('prepare') ||
    lowerMessage.includes('agenda')
  ) {
    return 'meeting_prep';
  }

  if (
    lowerMessage.includes('deal') ||
    lowerMessage.includes('analysis') ||
    lowerMessage.includes('opportunity')
  ) {
    return 'deal_analysis';
  }

  if (
    lowerMessage.includes('insight') ||
    lowerMessage.includes('predict') ||
    lowerMessage.includes('forecast')
  ) {
    return 'ai_insights';
  }

  if (
    lowerMessage.includes('task') ||
    lowerMessage.includes('remind') ||
    lowerMessage.includes('schedule')
  ) {
    return 'task_management';
  }

  if (
    lowerMessage.includes('find') ||
    lowerMessage.includes('search') ||
    lowerMessage.includes('look for')
  ) {
    return 'search';
  }

  return 'general';
}

// Generate suggestions based on intent
function generateSuggestions(
  intent: Intent,
  // _context?: ChatRequest['context']
): string[] {
  const suggestionMap: Record<Intent, string[]> = {
    draft_email: [
      'Make it more formal',
      'Add a call-to-action',
      'Shorten the email',
      'Add a follow-up date',
    ],
    meeting_prep: [
      'Add talking points',
      'Include recent activities',
      'Generate questions to ask',
      'Create an agenda',
    ],
    deal_analysis: [
      'Show win probability',
      'Compare to similar deals',
      'List risk factors',
      'Suggest next steps',
    ],
    ai_insights: [
      'Show churn risk',
      'Revenue forecast',
      'Lead scoring analysis',
      'Activity recommendations',
    ],
    task_management: [
      'Create a task',
      'Set a reminder',
      'Show my tasks',
      'Prioritize tasks',
    ],
    search: [
      'Search by company',
      'Find recent deals',
      'Show active leads',
      'Filter by stage',
    ],
    general: [
      'Draft a follow-up email',
      'Prepare for my next meeting',
      'Analyze this deal',
      'Show AI insights',
    ],
  };

  return suggestionMap[intent] || suggestionMap.general;
}

// Generate actions based on intent
function generateActions(
  intent: Intent,
  context?: ChatRequest['context']
): AIAction[] {
  const actions: AIAction[] = [];

  if (intent === 'draft_email' || intent === 'meeting_prep') {
    actions.push({
      id: 'copy',
      label: 'Copy to clipboard',
      icon: 'copy',
      action: 'copy',
    });

    if (intent === 'draft_email') {
      actions.push({
        id: 'send',
        label: 'Open in email',
        icon: 'mail',
        action: 'open_email',
      });
    }
  }

  if (context?.leadId || context?.contactId) {
    actions.push({
      id: 'view',
      label: 'View profile',
      icon: 'user',
      action: 'navigate',
      params: {
        type: context.leadId ? 'lead' : 'contact',
        id: context.leadId || context.contactId,
      },
    });
  }

  if (intent === 'task_management') {
    actions.push({
      id: 'create_task',
      label: 'Create task',
      icon: 'plus',
      action: 'create_task',
    });
  }

  return actions;
}

// Fallback response when AI service is unavailable
function generateFallbackResponse(message: string, intent: Intent): ChatResponse {
  const responses: Record<Intent, string> = {
    draft_email: `I'd be happy to help you draft an email. Here's a template you can customize:\n\nSubject: Follow-up from our conversation\n\nHi [Name],\n\nThank you for taking the time to speak with me. I wanted to follow up on our discussion about [topic].\n\n[Add your key points here]\n\nPlease let me know if you have any questions or would like to schedule a follow-up call.\n\nBest regards,\n[Your name]`,
    meeting_prep: `Here's a meeting preparation checklist:\n\n1. **Review recent interactions** - Check emails, calls, and notes\n2. **Understand their needs** - What problems are they trying to solve?\n3. **Prepare talking points** - Key benefits and value propositions\n4. **Anticipate questions** - Have answers ready for common objections\n5. **Set clear objectives** - What do you want to achieve from this meeting?\n\nWould you like me to help with any specific aspect?`,
    deal_analysis: `To analyze this deal effectively, I would typically look at:\n\n• **Deal stage** and time in stage\n• **Engagement level** - Recent activities and responses\n• **Decision timeline** - Urgency and key dates\n• **Competition** - Other vendors being considered\n• **Budget confirmation** - Has budget been allocated?\n\nWould you like me to focus on any specific area?`,
    ai_insights: `Here are the types of insights I can provide:\n\n• **Lead scoring** - Prioritize your best opportunities\n• **Churn prediction** - Identify at-risk accounts\n• **Revenue forecast** - Predict future performance\n• **Activity recommendations** - Optimize your outreach\n\nWhat would you like to explore?`,
    task_management: `I can help you manage tasks! Here are some options:\n\n• Create a new task\n• View your upcoming tasks\n• Set a reminder\n• Prioritize your to-do list\n\nWhat would you like to do?`,
    search: `I can help you find information in your CRM. What would you like to search for?\n\n• Leads by company or industry\n• Contacts by name or role\n• Deals by stage or value\n• Activities by date or type`,
    general: `I'm here to help! I can assist you with:\n\n• **Email drafting** - Create professional follow-ups\n• **Meeting prep** - Prepare for upcoming calls\n• **Deal analysis** - Understand opportunity health\n• **AI insights** - Get predictive analytics\n\nWhat would you like to do?`,
  };

  return {
    response: responses[intent],
    type: 'text',
    suggestions: generateSuggestions(intent),
    actions: [],
  };
}

