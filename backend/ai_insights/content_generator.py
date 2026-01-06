"""
AI-powered content generation using OpenAI
"""
import logging

import openai
from django.conf import settings

from .models import AIGeneratedContent

logger = logging.getLogger(__name__)


class AIContentGenerator:
    """Generate email and message content using AI"""

    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', '')
        if self.api_key:
            openai.api_key = self.api_key
        self.model = 'gpt-3.5-turbo'

    def generate_email(self, user, context, tone='professional', custom_prompt=None):
        """Generate email content"""
        if not self.api_key:
            return self._generate_fallback_email(context)

        # Build prompt
        prompt = custom_prompt if custom_prompt else self._build_email_prompt(context, tone)

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional business email writer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )

            content = response.choices[0].message.content
            subject, body = self._parse_email_response(content)

            # Save generated content
            ai_content = AIGeneratedContent.objects.create(
                user=user,
                content_type='email',
                prompt=custom_prompt or prompt,
                context_data=context,
                subject=subject,
                body=body,
                tone=tone,
                model_used=self.model,
                tokens_used=response.usage.total_tokens
            )

            return ai_content

        except Exception as e:
            logger.error(f"Failed to generate email with OpenAI: {e}")
            return self._generate_fallback_email(context, user)

    def _build_email_prompt(self, context, tone):
        """Build email generation prompt"""
        recipient_name = context.get('recipient_name', 'there')
        company_name = context.get('company_name', '')
        purpose = context.get('purpose', 'follow up')
        details = context.get('details', '')

        prompt = f"""Write a {tone} business email with the following details:

To: {recipient_name}
Company: {company_name}
Purpose: {purpose}
Additional Context: {details}

Generate a compelling subject line and email body. Format your response as:

Subject: [subject line]

Body:
[email body]
"""
        return prompt

    def _parse_email_response(self, content):
        """Parse subject and body from AI response"""
        lines = content.strip().split('\n')
        subject = ''
        body_lines = []
        in_body = False

        for line in lines:
            if line.startswith('Subject:'):
                subject = line.replace('Subject:', '').strip()
            elif 'Body:' in line or in_body:
                in_body = True
                if 'Body:' not in line:
                    body_lines.append(line)

        body = '\n'.join(body_lines).strip()
        return subject, body

    def _generate_fallback_email(self, context, user=None):
        """Generate email without AI as fallback"""
        recipient_name = context.get('recipient_name', 'there')
        purpose = context.get('purpose', 'follow up')

        subject = f"Re: {purpose.capitalize()}"
        body = f"""Hi {recipient_name},

I hope this email finds you well. I wanted to reach out regarding {purpose}.

{context.get('details', 'I look forward to connecting with you soon.')}

Best regards
"""

        if user:
            ai_content = AIGeneratedContent.objects.create(
                user=user,
                content_type='email',
                prompt='Fallback template',
                context_data=context,
                subject=subject,
                body=body,
                tone='professional',
                model_used='template'
            )
            return ai_content

        return {'subject': subject, 'body': body}

    def generate_sms(self, user, context, max_length=160):
        """Generate SMS message"""
        if not self.api_key:
            return self._generate_fallback_sms(context, user)

        prompt = f"""Write a brief SMS message (max {max_length} characters) for:

Purpose: {context.get('purpose')}
Recipient: {context.get('recipient_name')}
Context: {context.get('details')}

Keep it professional, friendly, and concise.
"""

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a concise business communicator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.7
            )

            body = response.choices[0].message.content.strip()

            # Truncate if needed
            if len(body) > max_length:
                body = body[:max_length-3] + '...'

            ai_content = AIGeneratedContent.objects.create(
                user=user,
                content_type='sms',
                prompt=prompt,
                context_data=context,
                body=body,
                model_used=self.model,
                tokens_used=response.usage.total_tokens
            )

            return ai_content

        except Exception as e:
            logger.error(f"Failed to generate SMS: {e}")
            return self._generate_fallback_sms(context, user)

    def _generate_fallback_sms(self, context, user):
        """Generate SMS fallback"""
        recipient = context.get('recipient_name', 'there')
        purpose = context.get('purpose', 'follow up')

        body = f"Hi {recipient}, following up on {purpose}. Let me know when you're available to chat."

        ai_content = AIGeneratedContent.objects.create(
            user=user,
            content_type='sms',
            prompt='Fallback template',
            context_data=context,
            body=body,
            model_used='template'
        )
        return ai_content

    def generate_social_post(self, user, context):
        """Generate social media post"""
        if not self.api_key:
            return self._generate_fallback_social(context, user)

        platform = context.get('platform', 'LinkedIn')
        topic = context.get('topic')

        prompt = f"""Create an engaging {platform} post about: {topic}

Context: {context.get('details', '')}

Make it professional, engaging, and appropriate for {platform}.
Include relevant hashtags.
"""

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"You are a {platform} content creator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.8
            )

            body = response.choices[0].message.content.strip()

            ai_content = AIGeneratedContent.objects.create(
                user=user,
                content_type='social',
                prompt=prompt,
                context_data=context,
                body=body,
                model_used=self.model,
                tokens_used=response.usage.total_tokens
            )

            return ai_content

        except Exception as e:
            logger.error(f"Failed to generate social post: {e}")
            return self._generate_fallback_social(context, user)

    def _generate_fallback_social(self, context, user):
        """Generate social post fallback"""
        topic = context.get('topic', 'business update')

        body = f"Excited to share updates about {topic}! #Business #Growth"

        ai_content = AIGeneratedContent.objects.create(
            user=user,
            content_type='social',
            prompt='Fallback template',
            context_data=context,
            body=body,
            model_used='template'
        )
        return ai_content

    def improve_content(self, original_content, improvement_type='grammar'):
        """Improve existing content"""
        if not self.api_key:
            return original_content

        prompts = {
            'grammar': 'Fix grammar and spelling errors in this text',
            'clarity': 'Rewrite this text for better clarity',
            'professional': 'Make this text more professional',
            'friendly': 'Make this text more friendly and approachable',
            'concise': 'Make this text more concise'
        }

        prompt_text = prompts.get(improvement_type, prompts['grammar'])
        full_prompt = f"{prompt_text}:\n\n{original_content}"

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional editor."},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=500,
                temperature=0.5
            )

            improved = response.choices[0].message.content.strip()
            return improved

        except Exception as e:
            logger.error(f"Failed to improve content: {e}")
            return original_content
