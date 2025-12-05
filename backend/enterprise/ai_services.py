"""
Enhanced AI Services with GPT-4 Integration

Provides:
- GPT-4 powered content generation
- AI sales assistant
- Intelligent email composition
- Meeting preparation summaries
- Competitive intelligence
- Lead research automation
"""

import os
import json
import logging
from typing import Dict, Optional, Any, List, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from functools import lru_cache

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """Supported AI providers"""
    OPENAI = 'openai'
    AZURE_OPENAI = 'azure_openai'
    ANTHROPIC = 'anthropic'


@dataclass
class AIConfig:
    """AI service configuration"""
    provider: AIProvider = AIProvider.OPENAI
    model: str = 'gpt-4-turbo-preview'
    temperature: float = 0.7
    max_tokens: int = 2000
    api_key: Optional[str] = None
    organization: Optional[str] = None
    azure_endpoint: Optional[str] = None
    azure_deployment: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'AIConfig':
        """Load configuration from environment"""
        provider = AIProvider(os.getenv('AI_PROVIDER', 'openai'))
        
        return cls(
            provider=provider,
            model=os.getenv('AI_MODEL', 'gpt-4-turbo-preview'),
            temperature=float(os.getenv('AI_TEMPERATURE', '0.7')),
            max_tokens=int(os.getenv('AI_MAX_TOKENS', '2000')),
            api_key=os.getenv('OPENAI_API_KEY') or os.getenv('AZURE_OPENAI_API_KEY'),
            organization=os.getenv('OPENAI_ORG_ID'),
            azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
            azure_deployment=os.getenv('AZURE_OPENAI_DEPLOYMENT')
        )


class AIClient:
    """
    Unified AI client supporting multiple providers
    """
    
    def __init__(self, config: Optional[AIConfig] = None):
        self.config = config or AIConfig.from_env()
        self._client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize the AI client"""
        if self.config.provider == AIProvider.OPENAI:
            self._init_openai()
        elif self.config.provider == AIProvider.AZURE_OPENAI:
            self._init_azure_openai()
        elif self.config.provider == AIProvider.ANTHROPIC:
            self._init_anthropic()
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        try:
            from openai import OpenAI
            
            self._client = OpenAI(
                api_key=self.config.api_key,
                organization=self.config.organization
            )
            logger.info("OpenAI client initialized")
        except ImportError:
            logger.error("openai package not installed")
            raise
    
    def _init_azure_openai(self):
        """Initialize Azure OpenAI client"""
        try:
            from openai import AzureOpenAI
            
            self._client = AzureOpenAI(
                api_key=self.config.api_key,
                azure_endpoint=self.config.azure_endpoint,
                api_version="2024-02-15-preview"
            )
            logger.info("Azure OpenAI client initialized")
        except ImportError:
            logger.error("openai package not installed")
            raise
    
    def _init_anthropic(self):
        """Initialize Anthropic client"""
        try:
            import anthropic
            
            self._client = anthropic.Anthropic(api_key=self.config.api_key)
            logger.info("Anthropic client initialized")
        except ImportError:
            logger.error("anthropic package not installed")
            raise
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Send chat completion request
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters
        
        Returns:
            Generated text response
        """
        temperature = kwargs.get('temperature', self.config.temperature)
        max_tokens = kwargs.get('max_tokens', self.config.max_tokens)
        
        if self.config.provider in [AIProvider.OPENAI, AIProvider.AZURE_OPENAI]:
            model = self.config.azure_deployment if self.config.provider == AIProvider.AZURE_OPENAI else self.config.model
            
            response = self._client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        
        elif self.config.provider == AIProvider.ANTHROPIC:
            # Convert messages format for Anthropic
            system_msg = next((m['content'] for m in messages if m['role'] == 'system'), None)
            anthropic_messages = [m for m in messages if m['role'] != 'system']
            
            response = self._client.messages.create(
                model=self.config.model,
                max_tokens=max_tokens,
                system=system_msg,
                messages=anthropic_messages
            )
            return response.content[0].text
    
    def embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        if self.config.provider in [AIProvider.OPENAI, AIProvider.AZURE_OPENAI]:
            response = self._client.embeddings.create(
                model='text-embedding-3-small',
                input=text
            )
            return response.data[0].embedding
        
        raise NotImplementedError(f"Embeddings not supported for {self.config.provider}")


# =====================
# Prompt Templates
# =====================

class PromptTemplates:
    """Collection of prompt templates for CRM operations"""
    
    # Email composition
    EMAIL_COMPOSE = """You are an expert sales professional composing an email.

Context about the recipient:
{contact_context}

Email purpose: {purpose}
Tone: {tone}
Key points to include:
{key_points}

Write a professional, personalized email that:
1. Uses the recipient's name and references relevant context
2. Is concise and action-oriented
3. Includes a clear call-to-action
4. Maintains the specified tone

Email:"""

    EMAIL_FOLLOW_UP = """You are composing a follow-up email for a sales opportunity.

Previous interaction summary:
{interaction_summary}

Days since last contact: {days_since_contact}
Opportunity stage: {stage}
Deal value: {deal_value}

Write a follow-up email that:
1. References the previous conversation naturally
2. Provides additional value or information
3. Moves the deal forward with a specific ask
4. Creates urgency without being pushy

Email:"""

    # Lead research
    LEAD_RESEARCH = """You are a sales research analyst preparing a lead profile.

Lead information:
- Name: {name}
- Company: {company}
- Title: {title}
- Industry: {industry}

Research and provide:
1. Key company information and recent news
2. Likely pain points based on role and industry
3. Personalization hooks for outreach
4. Recommended talking points
5. Potential objections and how to address them

Research Summary:"""

    # Meeting preparation
    MEETING_PREP = """You are preparing a sales representative for an important meeting.

Meeting details:
- Attendees: {attendees}
- Company: {company}
- Opportunity: {opportunity}
- Current stage: {stage}
- Deal value: {deal_value}

Previous interactions:
{interaction_history}

Prepare a meeting brief including:
1. Executive summary of the opportunity
2. Key stakeholders and their likely priorities
3. Suggested agenda items
4. Questions to ask
5. Potential objections and responses
6. Success criteria for this meeting
7. Recommended next steps

Meeting Brief:"""

    # Competitive intelligence
    COMPETITIVE_ANALYSIS = """You are a competitive intelligence analyst.

Our product: {our_product}
Competitor: {competitor}

Based on general industry knowledge, provide:
1. Key differentiators (ours vs theirs)
2. Common competitor weaknesses
3. Handling competitive objections
4. Win themes to emphasize
5. Traps to avoid

Competitive Battle Card:"""

    # Deal coaching
    DEAL_COACHING = """You are a sales coach analyzing an opportunity.

Opportunity details:
- Name: {opportunity_name}
- Value: {value}
- Stage: {stage}
- Days in stage: {days_in_stage}
- Win probability: {win_probability}%

Activity summary:
{activity_summary}

Provide coaching advice:
1. Deal health assessment (1-10)
2. Top 3 risks to this deal
3. Recommended actions to improve win probability
4. Questions the rep should be asking
5. Stakeholders that need engagement

Coaching Analysis:"""

    # Content generation
    SOCIAL_POST = """You are a professional social media manager for a B2B company.

Topic: {topic}
Platform: {platform}
Tone: {tone}
Call to action: {cta}

Write a {platform} post that:
1. Grabs attention in the first line
2. Provides value to the reader
3. Uses appropriate hashtags
4. Includes the call to action naturally

Post:"""

    # Sentiment analysis
    SENTIMENT_ANALYSIS = """Analyze the sentiment and key themes in this customer communication:

Communication:
{communication}

Provide:
1. Overall sentiment (positive/neutral/negative) with confidence score
2. Key themes mentioned
3. Urgency level (low/medium/high)
4. Action items mentioned
5. Recommended response approach

Analysis:"""


# =====================
# AI Services
# =====================

class EmailComposer:
    """AI-powered email composition service"""
    
    def __init__(self, ai_client: Optional[AIClient] = None):
        self.ai = ai_client or AIClient()
    
    def compose_email(
        self,
        contact: Dict,
        purpose: str,
        tone: str = 'professional',
        key_points: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Compose a personalized email
        
        Args:
            contact: Contact information dict
            purpose: Email purpose (intro, follow_up, proposal, etc.)
            tone: Email tone (professional, friendly, urgent)
            key_points: Key points to include
        
        Returns:
            Dict with 'subject' and 'body'
        """
        contact_context = self._build_contact_context(contact)
        
        prompt = PromptTemplates.EMAIL_COMPOSE.format(
            contact_context=contact_context,
            purpose=purpose,
            tone=tone,
            key_points='\n'.join(f"- {p}" for p in (key_points or []))
        )
        
        messages = [
            {"role": "system", "content": "You are an expert B2B sales professional who writes compelling, personalized emails."},
            {"role": "user", "content": prompt}
        ]
        
        response = self.ai.chat(messages, temperature=0.7)
        
        # Parse subject and body
        return self._parse_email_response(response)
    
    def compose_follow_up(
        self,
        opportunity: Dict,
        interactions: List[Dict]
    ) -> Dict[str, str]:
        """Compose a follow-up email for an opportunity"""
        interaction_summary = self._summarize_interactions(interactions)
        
        last_contact = interactions[-1]['date'] if interactions else None
        days_since = (timezone.now() - last_contact).days if last_contact else 0
        
        prompt = PromptTemplates.EMAIL_FOLLOW_UP.format(
            interaction_summary=interaction_summary,
            days_since_contact=days_since,
            stage=opportunity.get('stage', 'Unknown'),
            deal_value=f"${opportunity.get('value', 0):,.2f}"
        )
        
        messages = [
            {"role": "system", "content": "You are an expert sales professional who writes effective follow-up emails that move deals forward."},
            {"role": "user", "content": prompt}
        ]
        
        response = self.ai.chat(messages, temperature=0.6)
        return self._parse_email_response(response)
    
    def _build_contact_context(self, contact: Dict) -> str:
        """Build context string from contact data"""
        context_parts = []
        
        if contact.get('name'):
            context_parts.append(f"Name: {contact['name']}")
        if contact.get('title'):
            context_parts.append(f"Title: {contact['title']}")
        if contact.get('company'):
            context_parts.append(f"Company: {contact['company']}")
        if contact.get('industry'):
            context_parts.append(f"Industry: {contact['industry']}")
        if contact.get('notes'):
            context_parts.append(f"Notes: {contact['notes']}")
        
        return '\n'.join(context_parts)
    
    def _summarize_interactions(self, interactions: List[Dict]) -> str:
        """Summarize recent interactions"""
        if not interactions:
            return "No previous interactions recorded."
        
        summaries = []
        for interaction in interactions[-5:]:  # Last 5 interactions
            date = interaction.get('date', 'Unknown date')
            action = interaction.get('type', 'interaction')
            notes = interaction.get('notes', '')
            summaries.append(f"- {date}: {action} - {notes[:100]}")
        
        return '\n'.join(summaries)
    
    def _parse_email_response(self, response: str) -> Dict[str, str]:
        """Parse AI response into subject and body"""
        lines = response.strip().split('\n')
        
        subject = ""
        body_lines = []
        in_body = False
        
        for line in lines:
            if line.lower().startswith('subject:'):
                subject = line[8:].strip()
            elif line.lower().startswith('body:'):
                in_body = True
            elif subject and (in_body or not line.lower().startswith('subject')):
                body_lines.append(line)
        
        # If no explicit subject found, generate one
        if not subject and body_lines:
            subject = body_lines[0][:60] + "..." if len(body_lines[0]) > 60 else body_lines[0]
            body_lines = body_lines[1:]
        
        return {
            'subject': subject or "Following up",
            'body': '\n'.join(body_lines).strip() or response
        }


class LeadResearcher:
    """AI-powered lead research service"""
    
    def __init__(self, ai_client: Optional[AIClient] = None):
        self.ai = ai_client or AIClient()
    
    def research_lead(self, lead: Dict) -> Dict:
        """
        Generate comprehensive lead research
        
        Args:
            lead: Lead information dict
        
        Returns:
            Research findings dict
        """
        prompt = PromptTemplates.LEAD_RESEARCH.format(
            name=lead.get('name', 'Unknown'),
            company=lead.get('company', 'Unknown'),
            title=lead.get('title', 'Unknown'),
            industry=lead.get('industry', 'Unknown')
        )
        
        messages = [
            {"role": "system", "content": "You are a sales research analyst who provides actionable intelligence for sales teams."},
            {"role": "user", "content": prompt}
        ]
        
        response = self.ai.chat(messages, temperature=0.5)
        
        return {
            'lead_id': lead.get('id'),
            'research_summary': response,
            'generated_at': timezone.now().isoformat(),
            'cached_until': (timezone.now() + timedelta(days=7)).isoformat()
        }
    
    def get_personalization_hooks(self, lead: Dict) -> List[str]:
        """Get personalization hooks for outreach"""
        messages = [
            {"role": "system", "content": "You are an expert at finding personalization hooks for sales outreach."},
            {"role": "user", "content": f"""Based on this lead profile, provide 5 personalization hooks for outreach:

Name: {lead.get('name')}
Title: {lead.get('title')}
Company: {lead.get('company')}
Industry: {lead.get('industry')}

Provide hooks as a numbered list:"""}
        ]
        
        response = self.ai.chat(messages, temperature=0.7, max_tokens=500)
        
        # Parse numbered list
        hooks = []
        for line in response.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                hooks.append(line.lstrip('0123456789.-) '))
        
        return hooks[:5]


class MeetingPrepAssistant:
    """AI-powered meeting preparation service"""
    
    def __init__(self, ai_client: Optional[AIClient] = None):
        self.ai = ai_client or AIClient()
    
    def prepare_meeting_brief(
        self,
        meeting: Dict,
        opportunity: Dict,
        interactions: List[Dict]
    ) -> Dict:
        """
        Generate meeting preparation brief
        
        Args:
            meeting: Meeting details
            opportunity: Related opportunity
            interactions: Previous interaction history
        
        Returns:
            Meeting brief dict
        """
        interaction_history = self._format_interactions(interactions)
        
        prompt = PromptTemplates.MEETING_PREP.format(
            attendees=', '.join(meeting.get('attendees', [])),
            company=opportunity.get('company', 'Unknown'),
            opportunity=opportunity.get('name', 'Unknown'),
            stage=opportunity.get('stage', 'Unknown'),
            deal_value=f"${opportunity.get('value', 0):,.2f}",
            interaction_history=interaction_history
        )
        
        messages = [
            {"role": "system", "content": "You are a sales strategist who prepares comprehensive meeting briefs for sales teams."},
            {"role": "user", "content": prompt}
        ]
        
        response = self.ai.chat(messages, temperature=0.5, max_tokens=2500)
        
        return {
            'meeting_id': meeting.get('id'),
            'opportunity_id': opportunity.get('id'),
            'brief': response,
            'generated_at': timezone.now().isoformat()
        }
    
    def _format_interactions(self, interactions: List[Dict]) -> str:
        """Format interactions for prompt"""
        if not interactions:
            return "No previous interactions recorded."
        
        formatted = []
        for i in interactions[-10:]:  # Last 10
            formatted.append(
                f"- {i.get('date', 'N/A')}: {i.get('type', 'interaction')} - {i.get('summary', 'No summary')}"
            )
        
        return '\n'.join(formatted)


class DealCoach:
    """AI-powered deal coaching service"""
    
    def __init__(self, ai_client: Optional[AIClient] = None):
        self.ai = ai_client or AIClient()
    
    def analyze_deal(self, opportunity: Dict, activities: List[Dict]) -> Dict:
        """
        Analyze a deal and provide coaching
        
        Args:
            opportunity: Opportunity details
            activities: Related activities
        
        Returns:
            Coaching analysis dict
        """
        activity_summary = self._summarize_activities(activities)
        
        # Calculate days in stage
        stage_entered = opportunity.get('stage_entered_at', timezone.now())
        if isinstance(stage_entered, str):
            stage_entered = datetime.fromisoformat(stage_entered)
        days_in_stage = (timezone.now() - stage_entered).days
        
        prompt = PromptTemplates.DEAL_COACHING.format(
            opportunity_name=opportunity.get('name', 'Unknown'),
            value=f"${opportunity.get('value', 0):,.2f}",
            stage=opportunity.get('stage', 'Unknown'),
            days_in_stage=days_in_stage,
            win_probability=opportunity.get('win_probability', 50),
            activity_summary=activity_summary
        )
        
        messages = [
            {"role": "system", "content": "You are an experienced sales coach who provides actionable deal coaching to help reps win more deals."},
            {"role": "user", "content": prompt}
        ]
        
        response = self.ai.chat(messages, temperature=0.5)
        
        return {
            'opportunity_id': opportunity.get('id'),
            'coaching': response,
            'deal_health': self._extract_deal_health(response),
            'top_risks': self._extract_risks(response),
            'generated_at': timezone.now().isoformat()
        }
    
    def _summarize_activities(self, activities: List[Dict]) -> str:
        """Summarize recent activities"""
        if not activities:
            return "No recent activities recorded."
        
        summary_parts = []
        activity_counts = {}
        
        for activity in activities:
            activity_type = activity.get('type', 'other')
            activity_counts[activity_type] = activity_counts.get(activity_type, 0) + 1
        
        summary_parts.append(f"Total activities: {len(activities)}")
        for atype, count in activity_counts.items():
            summary_parts.append(f"- {atype}: {count}")
        
        # Last activity
        if activities:
            last = activities[-1]
            summary_parts.append(f"\nMost recent: {last.get('type', 'activity')} on {last.get('date', 'N/A')}")
        
        return '\n'.join(summary_parts)
    
    def _extract_deal_health(self, response: str) -> int:
        """Extract deal health score from response"""
        import re
        
        # Look for patterns like "Deal health: 7/10" or "health assessment: 7"
        patterns = [
            r'health[:\s]+(\d+)(?:/10)?',
            r'(\d+)/10',
            r'score[:\s]+(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response.lower())
            if match:
                score = int(match.group(1))
                if score <= 10:
                    return score
        
        return 5  # Default
    
    def _extract_risks(self, response: str) -> List[str]:
        """Extract top risks from response"""
        risks = []
        
        # Look for risk section
        lines = response.split('\n')
        in_risks = False
        
        for line in lines:
            if 'risk' in line.lower() and ':' in line:
                in_risks = True
                continue
            
            if in_risks:
                line = line.strip()
                if line.startswith(('-', '•', '*', '1', '2', '3')):
                    risks.append(line.lstrip('-•*0123456789. '))
                elif line and not line[0].isalpha():
                    continue
                elif len(risks) >= 3:
                    break
        
        return risks[:3]


class SentimentAnalyzer:
    """AI-powered sentiment analysis service"""
    
    def __init__(self, ai_client: Optional[AIClient] = None):
        self.ai = ai_client or AIClient()
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze sentiment of customer communication
        
        Args:
            text: Communication text
        
        Returns:
            Analysis results dict
        """
        prompt = PromptTemplates.SENTIMENT_ANALYSIS.format(communication=text[:2000])
        
        messages = [
            {"role": "system", "content": "You are an expert at analyzing customer communications for sentiment, urgency, and key themes."},
            {"role": "user", "content": prompt}
        ]
        
        response = self.ai.chat(messages, temperature=0.3, max_tokens=800)
        
        return {
            'analysis': response,
            'sentiment': self._extract_sentiment(response),
            'urgency': self._extract_urgency(response),
            'analyzed_at': timezone.now().isoformat()
        }
    
    def _extract_sentiment(self, response: str) -> str:
        """Extract sentiment from response"""
        response_lower = response.lower()
        
        if 'positive' in response_lower:
            return 'positive'
        elif 'negative' in response_lower:
            return 'negative'
        return 'neutral'
    
    def _extract_urgency(self, response: str) -> str:
        """Extract urgency level from response"""
        response_lower = response.lower()
        
        if 'high' in response_lower and 'urgency' in response_lower:
            return 'high'
        elif 'low' in response_lower and 'urgency' in response_lower:
            return 'low'
        return 'medium'


# =====================
# Unified AI Service
# =====================

class EnterpriseAIService:
    """
    Unified AI service for CRM operations
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.ai_client = AIClient()
        self.email_composer = EmailComposer(self.ai_client)
        self.lead_researcher = LeadResearcher(self.ai_client)
        self.meeting_assistant = MeetingPrepAssistant(self.ai_client)
        self.deal_coach = DealCoach(self.ai_client)
        self.sentiment_analyzer = SentimentAnalyzer(self.ai_client)
        
        self._initialized = True
        logger.info("EnterpriseAIService initialized")
    
    def compose_email(self, contact: Dict, purpose: str, **kwargs) -> Dict[str, str]:
        """Compose a personalized email"""
        return self.email_composer.compose_email(contact, purpose, **kwargs)
    
    def compose_follow_up(self, opportunity: Dict, interactions: List[Dict]) -> Dict[str, str]:
        """Compose a follow-up email"""
        return self.email_composer.compose_follow_up(opportunity, interactions)
    
    def research_lead(self, lead: Dict) -> Dict:
        """Research a lead"""
        # Check cache first
        cache_key = f"lead_research:{lead.get('id')}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        research = self.lead_researcher.research_lead(lead)
        cache.set(cache_key, research, 86400 * 7)  # Cache for 7 days
        return research
    
    def prepare_meeting(self, meeting: Dict, opportunity: Dict, interactions: List[Dict]) -> Dict:
        """Prepare for a meeting"""
        return self.meeting_assistant.prepare_meeting_brief(meeting, opportunity, interactions)
    
    def coach_deal(self, opportunity: Dict, activities: List[Dict]) -> Dict:
        """Get deal coaching"""
        return self.deal_coach.analyze_deal(opportunity, activities)
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text"""
        return self.sentiment_analyzer.analyze(text)
    
    def get_personalization_hooks(self, lead: Dict) -> List[str]:
        """Get personalization hooks for a lead"""
        return self.lead_researcher.get_personalization_hooks(lead)
