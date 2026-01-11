"""
Social Inbox Services
Platform integrations and sentiment analysis
"""

import json
from abc import ABC, abstractmethod
from django.utils import timezone


class SocialPlatformAdapter(ABC):
    """Abstract base class for social platform adapters"""
    
    @abstractmethod
    def sync_messages(self):
        pass
    
    @abstractmethod
    def send_message(self, conversation, content, attachments):
        pass
    
    @abstractmethod
    def publish_post(self, content, media_urls):
        pass
    
    @abstractmethod
    def refresh_access_token(self):
        pass


class TwitterAdapter(SocialPlatformAdapter):
    """Twitter/X API adapter"""
    
    def __init__(self, account):
        self.account = account
        self.api_base = "https://api.twitter.com/2"
    
    def sync_messages(self):
        """Sync DMs and mentions from Twitter"""
        # Placeholder - implement with Twitter API v2
        return {'new_conversations': 0, 'new_messages': 0}
    
    def send_message(self, conversation, content, attachments):
        """Send a DM or reply"""
        # Placeholder - implement with Twitter API v2
        return {'message_id': 'placeholder', 'success': True}
    
    def publish_post(self, content, media_urls):
        """Publish a tweet"""
        # Placeholder - implement with Twitter API v2
        return {'post_id': 'placeholder', 'url': 'https://twitter.com/...'}
    
    def refresh_access_token(self):
        """Refresh OAuth 2.0 token"""
        # Placeholder - implement OAuth refresh flow
        return {'access_token': 'new_token', 'expires_at': timezone.now()}


class LinkedInAdapter(SocialPlatformAdapter):
    """LinkedIn API adapter"""
    
    def __init__(self, account):
        self.account = account
        self.api_base = "https://api.linkedin.com/v2"
    
    def sync_messages(self):
        """Sync messages from LinkedIn"""
        return {'new_conversations': 0, 'new_messages': 0}
    
    def send_message(self, conversation, content, attachments):
        """Send a LinkedIn message"""
        return {'message_id': 'placeholder', 'success': True}
    
    def publish_post(self, content, media_urls):
        """Publish a LinkedIn post"""
        return {'post_id': 'placeholder', 'url': 'https://linkedin.com/...'}
    
    def refresh_access_token(self):
        """Refresh OAuth token"""
        return {'access_token': 'new_token', 'expires_at': timezone.now()}


class FacebookAdapter(SocialPlatformAdapter):
    """Facebook/Meta API adapter"""
    
    def __init__(self, account):
        self.account = account
        self.api_base = "https://graph.facebook.com/v18.0"
    
    def sync_messages(self):
        """Sync messages from Facebook Messenger"""
        return {'new_conversations': 0, 'new_messages': 0}
    
    def send_message(self, conversation, content, attachments):
        """Send a Facebook message"""
        return {'message_id': 'placeholder', 'success': True}
    
    def publish_post(self, content, media_urls):
        """Publish a Facebook post"""
        return {'post_id': 'placeholder', 'url': 'https://facebook.com/...'}
    
    def refresh_access_token(self):
        """Refresh access token"""
        return {'access_token': 'new_token', 'expires_at': timezone.now()}


class InstagramAdapter(SocialPlatformAdapter):
    """Instagram API adapter (via Facebook Graph API)"""
    
    def __init__(self, account):
        self.account = account
        self.api_base = "https://graph.facebook.com/v18.0"
    
    def sync_messages(self):
        """Sync messages from Instagram Direct"""
        return {'new_conversations': 0, 'new_messages': 0}
    
    def send_message(self, conversation, content, attachments):
        """Send an Instagram message"""
        return {'message_id': 'placeholder', 'success': True}
    
    def publish_post(self, content, media_urls):
        """Publish an Instagram post"""
        return {'post_id': 'placeholder', 'url': 'https://instagram.com/...'}
    
    def refresh_access_token(self):
        """Refresh access token"""
        return {'access_token': 'new_token', 'expires_at': timezone.now()}


class SocialPlatformService:
    """Service factory for social platform operations"""
    
    ADAPTERS = {
        'twitter': TwitterAdapter,
        'linkedin': LinkedInAdapter,
        'facebook': FacebookAdapter,
        'instagram': InstagramAdapter,
    }
    
    def __init__(self, account):
        self.account = account
        adapter_class = self.ADAPTERS.get(account.platform)
        if not adapter_class:
            raise ValueError(f"Unsupported platform: {account.platform}")
        self.adapter = adapter_class(account)
    
    def sync_messages(self):
        return self.adapter.sync_messages()
    
    def send_message(self, conversation, content, attachments=None):
        return self.adapter.send_message(conversation, content, attachments or [])
    
    def publish_post(self, content, media_urls=None):
        return self.adapter.publish_post(content, media_urls or [])
    
    def refresh_access_token(self):
        return self.adapter.refresh_access_token()


class SentimentAnalyzer:
    """Sentiment analysis service for social messages"""
    
    def __init__(self):
        # In production, use a proper NLP model or API
        self.positive_words = [
            'great', 'awesome', 'love', 'excellent', 'amazing', 'wonderful',
            'fantastic', 'good', 'happy', 'thanks', 'thank', 'appreciate'
        ]
        self.negative_words = [
            'bad', 'terrible', 'awful', 'horrible', 'hate', 'worst',
            'disappointed', 'angry', 'frustrated', 'problem', 'issue', 'broken'
        ]
    
    def analyze(self, text):
        """Analyze sentiment of text"""
        text_lower = text.lower()
        
        positive_count = sum(1 for word in self.positive_words if word in text_lower)
        negative_count = sum(1 for word in self.negative_words if word in text_lower)
        
        total = positive_count + negative_count
        if total == 0:
            return {'score': 0, 'label': 'neutral'}
        
        score = (positive_count - negative_count) / total
        
        if score > 0.2:
            label = 'positive'
        elif score < -0.2:
            label = 'negative'
        else:
            label = 'neutral'
        
        return {'score': score, 'label': label}
    
    def analyze_with_ai(self, text):
        """Analyze sentiment using AI (integration with ai_insights)"""
        try:
            from ai_insights.services import AIService
            ai = AIService()
            result = ai.analyze_sentiment(text)
            return result
        except Exception:
            # Fallback to basic analysis
            return self.analyze(text)


class AutoResponder:
    """Automated response generator for social messages"""
    
    def __init__(self, account):
        self.account = account
    
    def should_auto_respond(self, conversation, message):
        """Check if message should get an auto-response"""
        from .models import SocialMonitoringRule
        
        rules = SocialMonitoringRule.objects.filter(
            is_active=True,
            actions__contains=['respond']
        )
        
        for rule in rules:
            if self._matches_rule(rule, message.content):
                return rule.auto_response_template
        
        return None
    
    def _matches_rule(self, rule, content):
        """Check if content matches a rule"""
        content_lower = content.lower()
        
        # Check for excluded keywords first
        for exclude in rule.exclude_keywords:
            if exclude.lower() in content_lower:
                return False
        
        # Check for matching keywords
        for keyword in rule.keywords:
            if keyword.lower() in content_lower:
                return True
        
        return False
    
    def personalize_response(self, template, conversation):
        """Personalize a response template"""
        replacements = {
            '{{name}}': conversation.participant_name,
            '{{handle}}': conversation.participant_handle,
            '{{platform}}': conversation.social_account.platform,
        }
        
        result = template
        for key, value in replacements.items():
            result = result.replace(key, value or '')
        
        return result
