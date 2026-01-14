"""
AI Chatbot Services
Core AI processing, email generation, and data querying
"""

from django.db.models import Count, Q, Sum


class ChatbotService:
    """Main chatbot service for processing messages"""

    def __init__(self, user):
        self.user = user
        self.intents = self._load_intents()

    def _load_intents(self):
        """Load available intents"""
        return {
            'query_leads': {
                'patterns': ['show leads', 'list leads', 'find leads', 'how many leads'],
                'handler': self._handle_leads_query
            },
            'query_contacts': {
                'patterns': ['show contacts', 'list contacts', 'find contacts'],
                'handler': self._handle_contacts_query
            },
            'query_opportunities': {
                'patterns': ['show opportunities', 'pipeline', 'deals', 'revenue'],
                'handler': self._handle_opportunities_query
            },
            'query_tasks': {
                'patterns': ['my tasks', 'pending tasks', 'overdue tasks'],
                'handler': self._handle_tasks_query
            },
            'generate_email': {
                'patterns': ['write email', 'draft email', 'compose email', 'email to'],
                'handler': self._handle_email_generation
            },
            'suggest_action': {
                'patterns': ['what should i do', 'next action', 'suggest', 'recommend'],
                'handler': self._handle_action_suggestion
            },
            'summarize': {
                'patterns': ['summarize', 'summary of', 'overview'],
                'handler': self._handle_summarize
            },
            'help': {
                'patterns': ['help', 'what can you do', 'commands'],
                'handler': self._handle_help
            }
        }

    def process_message(self, session, message):
        """Process a user message and generate response"""
        message_lower = message.lower()

        # Detect intent
        intent = self._detect_intent(message_lower)

        if intent:
            handler = self.intents[intent]['handler']
            return handler(message, session)

        # Default to general AI response
        return self._generate_ai_response(message, session)

    def _detect_intent(self, message):
        """Detect the intent from a message"""
        for intent_name, intent_data in self.intents.items():
            for pattern in intent_data['patterns']:
                if pattern in message:
                    return intent_name
        return None

    def _handle_leads_query(self, message, session):
        """Handle leads-related queries"""
        from lead_management.models import Lead

        leads = Lead.objects.filter(
            Q(assigned_to=self.user) | Q(owner=self.user)
        )

        # Parse filters from message
        if 'hot' in message.lower() or 'high priority' in message.lower():
            leads = leads.filter(priority='high')
        if 'new' in message.lower():
            leads = leads.filter(status='new')
        if 'today' in message.lower():
            from django.utils import timezone
            today = timezone.now().date()
            leads = leads.filter(created_at__date=today)

        total = leads.count()
        by_status = list(leads.values('status').annotate(count=Count('id')))

        response_text = f"You have {total} leads"
        if by_status:
            status_parts = [f"{s['count']} {s['status']}" for s in by_status]
            response_text += f": {', '.join(status_parts)}"

        return {
            'type': 'query_result',
            'content': response_text,
            'data': {
                'total': total,
                'by_status': by_status,
                'leads': list(leads.values('id', 'first_name', 'last_name', 'email', 'status')[:10])
            }
        }

    def _handle_contacts_query(self, message, session):
        """Handle contacts-related queries"""
        from contact_management.models import Contact

        contacts = Contact.objects.filter(
            Q(assigned_to=self.user) | Q(created_by=self.user)
        )

        total = contacts.count()
        by_type = list(contacts.values('contact_type').annotate(count=Count('id')))

        return {
            'type': 'query_result',
            'content': f"You have {total} contacts in your database.",
            'data': {
                'total': total,
                'by_type': by_type,
                'contacts': list(contacts.values('id', 'first_name', 'last_name', 'email', 'company_name')[:10])
            }
        }

    def _handle_opportunities_query(self, message, session):
        """Handle opportunities-related queries"""
        from opportunity_management.models import Opportunity

        opportunities = Opportunity.objects.filter(owner=self.user)

        total = opportunities.count()
        total_value = opportunities.aggregate(total=Sum('amount'))['total'] or 0
        by_stage = list(opportunities.values('stage').annotate(
            count=Count('id'),
            value=Sum('amount')
        ))

        return {
            'type': 'query_result',
            'content': f"You have {total} opportunities worth ${total_value:,.2f} total.",
            'data': {
                'total': total,
                'total_value': float(total_value),
                'by_stage': by_stage,
                'opportunities': list(opportunities.values(
                    'id', 'name', 'amount', 'stage', 'probability'
                )[:10])
            }
        }

    def _handle_tasks_query(self, message, session):
        """Handle tasks-related queries"""
        from django.utils import timezone

        from task_management.models import Task

        tasks = Task.objects.filter(assigned_to=self.user)

        pending = tasks.filter(status__in=['pending', 'in_progress'])
        overdue = pending.filter(due_date__lt=timezone.now())
        due_today = pending.filter(due_date__date=timezone.now().date())

        response_text = f"You have {pending.count()} pending tasks"
        if overdue.count() > 0:
            response_text += f", {overdue.count()} are overdue"
        if due_today.count() > 0:
            response_text += f", {due_today.count()} due today"

        return {
            'type': 'query_result',
            'content': response_text,
            'data': {
                'pending': pending.count(),
                'overdue': overdue.count(),
                'due_today': due_today.count(),
                'tasks': list(pending.values('id', 'title', 'status', 'priority', 'due_date')[:10])
            }
        }

    def _handle_email_generation(self, message, session):
        """Handle email generation requests"""
        generator = EmailGenerator()

        # Parse intent from message
        purpose = 'follow_up'
        tone = 'professional'

        if 'introduction' in message.lower():
            purpose = 'introduction'
        elif 'proposal' in message.lower():
            purpose = 'proposal'
        elif 'thank' in message.lower():
            purpose = 'thank_you'
        elif 'meeting' in message.lower():
            purpose = 'meeting_request'

        if 'friendly' in message.lower():
            tone = 'friendly'
        elif 'formal' in message.lower():
            tone = 'formal'

        # Get context if session has it
        context = {}
        if session.context_type and session.context_id:
            context = self._get_entity_context(session.context_type, session.context_id)

        result = generator.generate(purpose, tone, context)

        return {
            'type': 'email_draft',
            'content': f"Here's a {purpose} email draft:\n\nSubject: {result['subject']}\n\n{result['body']}",
            'data': result
        }

    def _handle_action_suggestion(self, message, session):
        """Suggest next actions"""
        suggestions = self.suggest_next_actions(
            session.context_type,
            session.context_id
        )

        if suggestions:
            content = "Here are my suggestions:\n" + "\n".join(
                [f"• {s['action']}: {s['reason']}" for s in suggestions]
            )
        else:
            content = "Based on your current workload, here are some suggestions:\n"
            content += "• Review your pipeline and update opportunity stages\n"
            content += "• Follow up with leads that haven't been contacted recently\n"
            content += "• Complete any overdue tasks"

        return {
            'type': 'action_suggestion',
            'content': content,
            'data': {'suggestions': suggestions}
        }

    def _handle_summarize(self, message, session):
        """Handle summarization requests"""
        if session.context_type and session.context_id:
            context = self._get_entity_context(session.context_type, session.context_id)
            summary = self._generate_entity_summary(session.context_type, context)
        else:
            summary = self._generate_daily_summary()

        return {
            'type': 'data_summary',
            'content': summary,
            'data': {}
        }

    def _handle_help(self, message, session):
        """Handle help requests"""
        help_text = """I can help you with:

📊 **Data Queries**
- "Show my leads" - View your leads
- "List contacts" - View your contacts
- "Show pipeline" - View opportunities
- "My tasks" - View pending tasks

✉️ **Email Generation**
- "Write a follow-up email"
- "Draft an introduction email"
- "Compose a meeting request"

💡 **Suggestions**
- "What should I do next?"
- "Suggest actions for this lead"

📝 **Summaries**
- "Summarize this contact"
- "Give me an overview"

Just type naturally and I'll help you!"""

        return {
            'type': 'text',
            'content': help_text,
            'data': {}
        }

    def _generate_ai_response(self, message, session):
        """Generate a general AI response"""
        # In production, integrate with GPT or similar
        return {
            'type': 'text',
            'content': f"I understand you're asking about: {message}. Try asking me about your leads, contacts, opportunities, or tasks. You can also ask me to write emails or suggest next actions.",
            'data': {}
        }

    def _get_entity_context(self, entity_type, entity_id):
        """Get context data for an entity"""
        context = {}

        try:
            if entity_type == 'lead':
                from lead_management.models import Lead
                lead = Lead.objects.get(id=entity_id)
                context = {
                    'name': f"{lead.first_name} {lead.last_name}",
                    'email': lead.email,
                    'company': lead.company_name,
                    'status': lead.status
                }
            elif entity_type == 'contact':
                from contact_management.models import Contact
                contact = Contact.objects.get(id=entity_id)
                context = {
                    'name': contact.full_name,
                    'email': contact.email,
                    'company': contact.company_name
                }
            elif entity_type == 'opportunity':
                from opportunity_management.models import Opportunity
                opp = Opportunity.objects.get(id=entity_id)
                context = {
                    'name': opp.name,
                    'amount': float(opp.amount),
                    'stage': opp.stage
                }
        except Exception:
            pass

        return context

    def _generate_entity_summary(self, entity_type, context):
        """Generate a summary for an entity"""
        if entity_type == 'lead':
            return f"Lead: {context.get('name', 'Unknown')}\nCompany: {context.get('company', 'N/A')}\nStatus: {context.get('status', 'N/A')}"
        elif entity_type == 'contact':
            return f"Contact: {context.get('name', 'Unknown')}\nCompany: {context.get('company', 'N/A')}"
        elif entity_type == 'opportunity':
            return f"Opportunity: {context.get('name', 'Unknown')}\nValue: ${context.get('amount', 0):,.2f}\nStage: {context.get('stage', 'N/A')}"
        return "No summary available"

    def _generate_daily_summary(self):
        """Generate a daily summary for the user"""
        from django.utils import timezone

        from lead_management.models import Lead
        from opportunity_management.models import Opportunity
        from task_management.models import Task

        today = timezone.now().date()

        tasks_due = Task.objects.filter(
            assigned_to=self.user,
            due_date__date=today,
            status__in=['pending', 'in_progress']
        ).count()

        new_leads = Lead.objects.filter(
            assigned_to=self.user,
            created_at__date=today
        ).count()

        pipeline_value = Opportunity.objects.filter(
            owner=self.user,
            stage__in=['qualification', 'proposal', 'negotiation']
        ).aggregate(total=Sum('amount'))['total'] or 0

        return f"""📅 **Daily Summary**

📋 Tasks due today: {tasks_due}
🎯 New leads today: {new_leads}
💰 Active pipeline: ${pipeline_value:,.2f}

Need help with anything specific?"""

    def suggest_next_actions(self, entity_type, entity_id):
        """Suggest next actions for an entity"""
        suggestions = []

        if entity_type == 'lead':
            from lead_management.models import Lead
            try:
                lead = Lead.objects.get(id=entity_id)

                if lead.status == 'new':
                    suggestions.append({
                        'action': 'Make initial contact',
                        'reason': 'This is a new lead that needs first contact'
                    })
                elif lead.status == 'contacted':
                    suggestions.append({
                        'action': 'Schedule a discovery call',
                        'reason': 'Lead has been contacted, time for deeper qualification'
                    })

                suggestions.append({
                    'action': 'Send personalized email',
                    'reason': 'Keep the lead engaged with relevant content'
                })
            except Lead.DoesNotExist:
                pass

        return suggestions

    def generate_title(self, first_message):
        """Generate a session title from first message"""
        # Simple title generation
        words = first_message.split()[:5]
        title = ' '.join(words)
        if len(title) > 50:
            title = title[:47] + '...'
        return title


class EmailGenerator:
    """AI-powered email generation"""

    TEMPLATES = {
        'follow_up': {
            'professional': {
                'subject': 'Following up on our conversation',
                'body': '''Hi {{name}},

I wanted to follow up on our recent conversation about {{topic}}.

I believe our solution could really help {{company}} achieve {{goals}}.

Would you be available for a quick call this week to discuss further?

Best regards'''
            }
        },
        'introduction': {
            'professional': {
                'subject': 'Introduction from {{sender_company}}',
                'body': '''Hi {{name}},

I hope this email finds you well. My name is {{sender_name}} from {{sender_company}}.

I noticed that {{company}} is {{observation}}, and I thought you might be interested in learning how we help companies like yours {{value_prop}}.

Would you be open to a brief conversation?

Best regards'''
            }
        },
        'meeting_request': {
            'professional': {
                'subject': 'Meeting Request: {{topic}}',
                'body': '''Hi {{name}},

I would like to schedule a meeting to discuss {{topic}}.

Would any of the following times work for you?
- [Option 1]
- [Option 2]
- [Option 3]

Please let me know what works best for your schedule.

Best regards'''
            }
        },
        'thank_you': {
            'professional': {
                'subject': 'Thank you for your time',
                'body': '''Hi {{name}},

Thank you for taking the time to meet with me today. I really enjoyed our conversation about {{topic}}.

As discussed, I will {{next_steps}}.

Please don't hesitate to reach out if you have any questions.

Best regards'''
            }
        }
    }

    def generate(self, purpose, tone, context=None, recipient_name='', company_name='', additional_context=''):
        """Generate an email based on purpose and tone"""
        context = context or {}

        template = self.TEMPLATES.get(purpose, {}).get(tone, {})

        if not template:
            # Default template
            template = {
                'subject': f'{purpose.replace("_", " ").title()}',
                'body': f'Hi {{{{name}}}},\n\n{additional_context}\n\nBest regards'
            }

        subject = template['subject']
        body = template['body']

        # Replace placeholders
        replacements = {
            'name': recipient_name or context.get('name', '[Name]'),
            'company': company_name or context.get('company', '[Company]'),
            'topic': context.get('topic', '[Topic]'),
            'goals': context.get('goals', '[Goals]'),
            'observation': context.get('observation', '[Observation]'),
            'value_prop': context.get('value_prop', '[Value Proposition]'),
            'next_steps': context.get('next_steps', '[Next Steps]'),
            'sender_name': context.get('sender_name', '[Your Name]'),
            'sender_company': context.get('sender_company', '[Your Company]'),
        }

        for key, value in replacements.items():
            subject = subject.replace(f'{{{{{key}}}}}', value)
            body = body.replace(f'{{{{{key}}}}}', value)

        return {
            'subject': subject,
            'body': body,
            'purpose': purpose,
            'tone': tone
        }


class DataQueryEngine:
    """Natural language query engine for CRM data"""

    def __init__(self, user):
        self.user = user

    def query(self, query, entity_type='all'):
        """Process a natural language query"""
        query_lower = query.lower()

        results = {}

        if entity_type in ['all', 'leads']:
            results['leads'] = self._query_leads(query_lower)

        if entity_type in ['all', 'contacts']:
            results['contacts'] = self._query_contacts(query_lower)

        if entity_type in ['all', 'opportunities']:
            results['opportunities'] = self._query_opportunities(query_lower)

        if entity_type in ['all', 'tasks']:
            results['tasks'] = self._query_tasks(query_lower)

        return {
            'query': query,
            'results': results,
            'total': sum(len(v) for v in results.values() if isinstance(v, list))
        }

    def _query_leads(self, query):
        from lead_management.models import Lead

        leads = Lead.objects.filter(
            Q(assigned_to=self.user) | Q(owner=self.user)
        )

        # Apply filters based on query
        if 'hot' in query or 'high' in query:
            leads = leads.filter(priority='high')
        if 'new' in query:
            leads = leads.filter(status='new')

        return list(leads.values('id', 'first_name', 'last_name', 'email', 'status')[:20])

    def _query_contacts(self, query):
        from contact_management.models import Contact

        contacts = Contact.objects.filter(
            Q(assigned_to=self.user) | Q(created_by=self.user)
        )

        # Search by name or company
        words = query.split()
        for word in words:
            if len(word) > 2:
                contacts = contacts.filter(
                    Q(first_name__icontains=word) |
                    Q(last_name__icontains=word) |
                    Q(company_name__icontains=word)
                )

        return list(contacts.values('id', 'first_name', 'last_name', 'email', 'company_name')[:20])

    def _query_opportunities(self, query):
        from opportunity_management.models import Opportunity

        opportunities = Opportunity.objects.filter(owner=self.user)

        if 'closing' in query or 'close' in query:
            opportunities = opportunities.filter(stage__in=['negotiation', 'proposal'])
        if 'won' in query:
            opportunities = opportunities.filter(stage='closed_won')
        if 'lost' in query:
            opportunities = opportunities.filter(stage='closed_lost')

        return list(opportunities.values('id', 'name', 'amount', 'stage', 'probability')[:20])

    def _query_tasks(self, query):
        from django.utils import timezone

        from task_management.models import Task

        tasks = Task.objects.filter(assigned_to=self.user)

        if 'overdue' in query:
            tasks = tasks.filter(
                due_date__lt=timezone.now(),
                status__in=['pending', 'in_progress']
            )
        if 'today' in query:
            tasks = tasks.filter(due_date__date=timezone.now().date())
        if 'pending' in query:
            tasks = tasks.filter(status='pending')

        return list(tasks.values('id', 'title', 'status', 'priority', 'due_date')[:20])
