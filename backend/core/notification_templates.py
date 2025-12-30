"""
Notification Email Templates
HTML and text email templates for various notification types
"""

from django.template import Template, Context
from django.utils import timezone
from django.conf import settings


class EmailTemplates:
    """Collection of email templates for notifications"""
    
    # Base HTML template
    BASE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .header {
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            color: white;
            padding: 24px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 24px;
            font-weight: 600;
        }
        .content {
            padding: 32px 24px;
        }
        .content h2 {
            color: #1f2937;
            margin-top: 0;
        }
        .button {
            display: inline-block;
            background: #3b82f6;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 500;
            margin: 16px 0;
        }
        .button:hover {
            background: #2563eb;
        }
        .card {
            background: #f9fafb;
            border-radius: 6px;
            padding: 16px;
            margin: 16px 0;
            border-left: 4px solid #3b82f6;
        }
        .metric {
            display: inline-block;
            text-align: center;
            padding: 16px;
            margin: 8px;
            background: #f0f9ff;
            border-radius: 8px;
        }
        .metric-value {
            font-size: 28px;
            font-weight: 700;
            color: #3b82f6;
        }
        .metric-label {
            font-size: 12px;
            color: #6b7280;
            text-transform: uppercase;
        }
        .footer {
            background: #f9fafb;
            padding: 24px;
            text-align: center;
            font-size: 12px;
            color: #6b7280;
        }
        .footer a {
            color: #3b82f6;
            text-decoration: none;
        }
        .divider {
            border-top: 1px solid #e5e7eb;
            margin: 24px 0;
        }
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }
        .badge-success { background: #d1fae5; color: #065f46; }
        .badge-warning { background: #fef3c7; color: #92400e; }
        .badge-danger { background: #fee2e2; color: #991b1b; }
        .badge-info { background: #dbeafe; color: #1e40af; }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        table th, table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }
        table th {
            background: #f9fafb;
            font-weight: 600;
            color: #374151;
        }
    </style>
</head>
<body>
    <div style="padding: 24px;">
        <div class="container">
            <div class="header">
                <h1>{{ header_title|default:"MyCRM" }}</h1>
            </div>
            <div class="content">
                {{ content|safe }}
            </div>
            <div class="footer">
                <p>This email was sent by MyCRM</p>
                <p>
                    <a href="{{ settings_url }}">Manage Preferences</a> |
                    <a href="{{ unsubscribe_url }}">Unsubscribe</a>
                </p>
                <p>&copy; {{ year }} MyCRM. All rights reserved.</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

    # ==================== Deal Notifications ====================
    
    DEAL_WON_HTML = """
<h2>🎉 Congratulations! Deal Won!</h2>
<p>Great news! A deal has been closed successfully.</p>

<div class="card">
    <h3 style="margin-top: 0;">{{ deal.name }}</h3>
    <p><strong>Amount:</strong> ${{ deal.amount|floatformat:2 }}</p>
    <p><strong>Contact:</strong> {{ deal.contact_name }}</p>
    <p><strong>Company:</strong> {{ deal.company_name }}</p>
    <p><strong>Closed by:</strong> {{ deal.owner_name }}</p>
</div>

<div style="text-align: center;">
    <a href="{{ deal_url }}" class="button">View Deal Details</a>
</div>
"""

    DEAL_LOST_HTML = """
<h2>Deal Closed - Lost</h2>
<p>Unfortunately, a deal has been marked as lost.</p>

<div class="card">
    <h3 style="margin-top: 0;">{{ deal.name }}</h3>
    <p><strong>Amount:</strong> ${{ deal.amount|floatformat:2 }}</p>
    <p><strong>Reason:</strong> {{ deal.lost_reason|default:"Not specified" }}</p>
    <p><strong>Contact:</strong> {{ deal.contact_name }}</p>
</div>

<p>Consider reaching out to understand why and improve for next time.</p>

<div style="text-align: center;">
    <a href="{{ deal_url }}" class="button">View Deal Details</a>
</div>
"""

    DEAL_STAGE_CHANGE_HTML = """
<h2>Deal Stage Updated</h2>
<p>A deal has moved to a new stage in your pipeline.</p>

<div class="card">
    <h3 style="margin-top: 0;">{{ deal.name }}</h3>
    <p>
        <span class="badge badge-info">{{ deal.previous_stage }}</span>
        &rarr;
        <span class="badge badge-success">{{ deal.new_stage }}</span>
    </p>
    <p><strong>Amount:</strong> ${{ deal.amount|floatformat:2 }}</p>
    <p><strong>Probability:</strong> {{ deal.probability }}%</p>
</div>

<div style="text-align: center;">
    <a href="{{ deal_url }}" class="button">View Deal</a>
</div>
"""

    DEAL_ASSIGNED_HTML = """
<h2>New Deal Assigned to You</h2>
<p>A deal has been assigned to you for follow-up.</p>

<div class="card">
    <h3 style="margin-top: 0;">{{ deal.name }}</h3>
    <p><strong>Amount:</strong> ${{ deal.amount|floatformat:2 }}</p>
    <p><strong>Stage:</strong> {{ deal.stage }}</p>
    <p><strong>Expected Close:</strong> {{ deal.expected_close|date:"M d, Y" }}</p>
    <p><strong>Assigned by:</strong> {{ assigned_by }}</p>
</div>

<div style="text-align: center;">
    <a href="{{ deal_url }}" class="button">View Deal</a>
</div>
"""

    # ==================== Task Notifications ====================
    
    TASK_DUE_SOON_HTML = """
<h2>⏰ Task Due Soon</h2>
<p>You have a task due {{ task.time_until_due }}.</p>

<div class="card">
    <h3 style="margin-top: 0;">{{ task.title }}</h3>
    <p><strong>Due:</strong> {{ task.due_date|date:"M d, Y" }} at {{ task.due_date|time:"g:i A" }}</p>
    <p><strong>Priority:</strong> 
        <span class="badge {% if task.priority == 'high' %}badge-danger{% elif task.priority == 'medium' %}badge-warning{% else %}badge-info{% endif %}">
            {{ task.priority|upper }}
        </span>
    </p>
    {% if task.description %}
    <p><strong>Description:</strong> {{ task.description }}</p>
    {% endif %}
</div>

<div style="text-align: center;">
    <a href="{{ task_url }}" class="button">View Task</a>
</div>
"""

    TASK_OVERDUE_HTML = """
<h2>🚨 Task Overdue</h2>
<p>You have an overdue task that needs attention.</p>

<div class="card" style="border-left-color: #ef4444;">
    <h3 style="margin-top: 0; color: #ef4444;">{{ task.title }}</h3>
    <p><strong>Due:</strong> {{ task.due_date|date:"M d, Y" }} ({{ task.days_overdue }} days ago)</p>
    <p><strong>Priority:</strong> 
        <span class="badge badge-danger">{{ task.priority|upper }}</span>
    </p>
</div>

<div style="text-align: center;">
    <a href="{{ task_url }}" class="button" style="background: #ef4444;">Complete Task Now</a>
</div>
"""

    TASK_ASSIGNED_HTML = """
<h2>New Task Assigned</h2>
<p>{{ assigned_by }} has assigned you a new task.</p>

<div class="card">
    <h3 style="margin-top: 0;">{{ task.title }}</h3>
    <p><strong>Due:</strong> {{ task.due_date|date:"M d, Y" }}</p>
    <p><strong>Priority:</strong> {{ task.priority|title }}</p>
    {% if task.related_to %}
    <p><strong>Related to:</strong> {{ task.related_to }}</p>
    {% endif %}
</div>

<div style="text-align: center;">
    <a href="{{ task_url }}" class="button">View Task</a>
</div>
"""

    # ==================== Social Notifications ====================
    
    MENTION_HTML = """
<h2>@{{ mentioned_by }} mentioned you</h2>
<p>You were mentioned in a {{ context_type }}.</p>

<div class="card">
    <p>"{{ message }}"</p>
    <p style="font-size: 12px; color: #6b7280; margin-bottom: 0;">
        — {{ mentioned_by }}, {{ timestamp|date:"M d, Y" }} at {{ timestamp|time:"g:i A" }}
    </p>
</div>

<div style="text-align: center;">
    <a href="{{ context_url }}" class="button">View Context</a>
</div>
"""

    COMMENT_HTML = """
<h2>New Comment on {{ item_type }}</h2>
<p>{{ commenter }} left a comment on "{{ item_name }}".</p>

<div class="card">
    <p>"{{ comment }}"</p>
    <p style="font-size: 12px; color: #6b7280; margin-bottom: 0;">
        — {{ commenter }}, {{ timestamp|date:"M d, Y" }}
    </p>
</div>

<div style="text-align: center;">
    <a href="{{ item_url }}" class="button">View & Reply</a>
</div>
"""

    # ==================== System Notifications ====================
    
    SECURITY_ALERT_HTML = """
<h2>🔐 Security Alert</h2>
<p>We detected a security-related event on your account.</p>

<div class="card" style="border-left-color: #f59e0b;">
    <h3 style="margin-top: 0;">{{ alert_type }}</h3>
    <p><strong>Time:</strong> {{ timestamp|date:"M d, Y" }} at {{ timestamp|time:"g:i A" }}</p>
    <p><strong>IP Address:</strong> {{ ip_address }}</p>
    <p><strong>Location:</strong> {{ location|default:"Unknown" }}</p>
    <p><strong>Device:</strong> {{ device|default:"Unknown" }}</p>
</div>

<p>If this was you, you can ignore this email. If not, please secure your account immediately.</p>

<div style="text-align: center;">
    <a href="{{ security_settings_url }}" class="button" style="background: #f59e0b;">Review Security Settings</a>
</div>
"""

    EXPORT_READY_HTML = """
<h2>📥 Your Export is Ready</h2>
<p>Your data export has been completed successfully.</p>

<div class="card">
    <p><strong>Format:</strong> {{ export.format|upper }}</p>
    <p><strong>Data Included:</strong> {{ export.entities|join:", " }}</p>
    <p><strong>File Size:</strong> {{ export.file_size }}</p>
    <p><strong>Expires:</strong> {{ export.expires_at|date:"M d, Y" }}</p>
</div>

<div style="text-align: center;">
    <a href="{{ download_url }}" class="button">Download Export</a>
</div>

<p style="font-size: 12px; color: #6b7280;">
    This download link will expire in 7 days. Please download your data before then.
</p>
"""

    # ==================== AI Notifications ====================
    
    AI_RECOMMENDATION_HTML = """
<h2>💡 AI Recommendation</h2>
<p>Our AI has identified an opportunity that might interest you.</p>

<div class="card" style="border-left-color: #8b5cf6;">
    <h3 style="margin-top: 0;">{{ recommendation.title }}</h3>
    <p>{{ recommendation.description }}</p>
    <p><strong>Priority:</strong> 
        <span class="badge {% if recommendation.priority == 'high' %}badge-danger{% else %}badge-info{% endif %}">
            {{ recommendation.priority|upper }}
        </span>
    </p>
    <p><strong>Potential Impact:</strong> {{ recommendation.impact }}</p>
</div>

{% if recommendation.action_items %}
<h4>Suggested Actions:</h4>
<ul>
{% for action in recommendation.action_items %}
    <li>{{ action }}</li>
{% endfor %}
</ul>
{% endif %}

<div style="text-align: center;">
    <a href="{{ action_url }}" class="button" style="background: #8b5cf6;">Take Action</a>
</div>
"""

    # ==================== Digest Templates ====================
    
    DAILY_DIGEST_HTML = """
<h2>📊 Your Daily Digest</h2>
<p>Here's your activity summary for {{ date|date:"l, M d, Y" }}.</p>

<div class="divider"></div>

<h3>Today's Metrics</h3>
<div style="text-align: center;">
    <div class="metric">
        <div class="metric-value">{{ metrics.deals_closed }}</div>
        <div class="metric-label">Deals Closed</div>
    </div>
    <div class="metric">
        <div class="metric-value">${{ metrics.revenue|floatformat:0 }}</div>
        <div class="metric-label">Revenue</div>
    </div>
    <div class="metric">
        <div class="metric-value">{{ metrics.tasks_completed }}</div>
        <div class="metric-label">Tasks Done</div>
    </div>
    <div class="metric">
        <div class="metric-value">{{ metrics.activities }}</div>
        <div class="metric-label">Activities</div>
    </div>
</div>

{% if tasks_due %}
<div class="divider"></div>
<h3>Tasks Due Today</h3>
<ul>
{% for task in tasks_due %}
    <li><a href="{{ task.url }}">{{ task.title }}</a> - {{ task.priority|title }} priority</li>
{% endfor %}
</ul>
{% endif %}

{% if upcoming_meetings %}
<div class="divider"></div>
<h3>Upcoming Meetings</h3>
<ul>
{% for meeting in upcoming_meetings %}
    <li><strong>{{ meeting.time }}</strong> - {{ meeting.title }} with {{ meeting.attendees }}</li>
{% endfor %}
</ul>
{% endif %}

{% if ai_insights %}
<div class="divider"></div>
<h3>💡 AI Insights</h3>
<div class="card" style="border-left-color: #8b5cf6;">
{% for insight in ai_insights %}
    <p>• {{ insight }}</p>
{% endfor %}
</div>
{% endif %}

<div class="divider"></div>

<div style="text-align: center;">
    <a href="{{ dashboard_url }}" class="button">Go to Dashboard</a>
</div>
"""

    WEEKLY_DIGEST_HTML = """
<h2>📈 Your Weekly Report</h2>
<p>Here's your performance summary for the week of {{ week_start|date:"M d" }} - {{ week_end|date:"M d, Y" }}.</p>

<div class="divider"></div>

<h3>Weekly Performance</h3>
<div style="text-align: center;">
    <div class="metric">
        <div class="metric-value">{{ metrics.deals_won }}</div>
        <div class="metric-label">Deals Won</div>
    </div>
    <div class="metric">
        <div class="metric-value">${{ metrics.total_revenue|floatformat:0 }}</div>
        <div class="metric-label">Revenue</div>
    </div>
    <div class="metric">
        <div class="metric-value">{{ metrics.conversion_rate }}%</div>
        <div class="metric-label">Win Rate</div>
    </div>
</div>

<h3>Comparison to Last Week</h3>
<table>
    <tr>
        <th>Metric</th>
        <th>This Week</th>
        <th>Last Week</th>
        <th>Change</th>
    </tr>
    <tr>
        <td>Deals Closed</td>
        <td>{{ metrics.deals_won }}</td>
        <td>{{ metrics.prev_deals_won }}</td>
        <td>
            <span class="badge {% if metrics.deals_change >= 0 %}badge-success{% else %}badge-danger{% endif %}">
                {{ metrics.deals_change }}%
            </span>
        </td>
    </tr>
    <tr>
        <td>Revenue</td>
        <td>${{ metrics.total_revenue|floatformat:0 }}</td>
        <td>${{ metrics.prev_revenue|floatformat:0 }}</td>
        <td>
            <span class="badge {% if metrics.revenue_change >= 0 %}badge-success{% else %}badge-danger{% endif %}">
                {{ metrics.revenue_change }}%
            </span>
        </td>
    </tr>
    <tr>
        <td>Activities</td>
        <td>{{ metrics.activities }}</td>
        <td>{{ metrics.prev_activities }}</td>
        <td>
            <span class="badge {% if metrics.activity_change >= 0 %}badge-success{% else %}badge-danger{% endif %}">
                {{ metrics.activity_change }}%
            </span>
        </td>
    </tr>
</table>

{% if top_deals %}
<div class="divider"></div>
<h3>Top Deals This Week</h3>
<table>
    <tr>
        <th>Deal</th>
        <th>Amount</th>
        <th>Stage</th>
    </tr>
    {% for deal in top_deals %}
    <tr>
        <td><a href="{{ deal.url }}">{{ deal.name }}</a></td>
        <td>${{ deal.amount|floatformat:0 }}</td>
        <td>{{ deal.stage }}</td>
    </tr>
    {% endfor %}
</table>
{% endif %}

<div class="divider"></div>

<div style="text-align: center;">
    <a href="{{ dashboard_url }}" class="button">View Full Dashboard</a>
</div>
"""

    # Template Registry
    TEMPLATES = {
        'deal_won': DEAL_WON_HTML,
        'deal_lost': DEAL_LOST_HTML,
        'deal_stage_change': DEAL_STAGE_CHANGE_HTML,
        'deal_assigned': DEAL_ASSIGNED_HTML,
        'task_due_soon': TASK_DUE_SOON_HTML,
        'task_overdue': TASK_OVERDUE_HTML,
        'task_assigned': TASK_ASSIGNED_HTML,
        'mention': MENTION_HTML,
        'comment': COMMENT_HTML,
        'security_alert': SECURITY_ALERT_HTML,
        'export_ready': EXPORT_READY_HTML,
        'ai_recommendation': AI_RECOMMENDATION_HTML,
        'daily_digest': DAILY_DIGEST_HTML,
        'weekly_digest': WEEKLY_DIGEST_HTML,
    }

    @classmethod
    def render(cls, template_name, context):
        """Render a notification template with context"""
        if template_name not in cls.TEMPLATES:
            raise ValueError(f"Unknown template: {template_name}")
        
        content_template = Template(cls.TEMPLATES[template_name])
        content_html = content_template.render(Context(context))
        
        base_context = {
            'content': content_html,
            'title': context.get('title', 'MyCRM Notification'),
            'header_title': context.get('header_title', 'MyCRM'),
            'settings_url': context.get('settings_url', f"{settings.FRONTEND_URL}/settings/notifications"),
            'unsubscribe_url': context.get('unsubscribe_url', f"{settings.FRONTEND_URL}/unsubscribe"),
            'year': timezone.now().year,
        }
        
        base_template = Template(cls.BASE_HTML)
        return base_template.render(Context(base_context))
    
    @classmethod
    def get_text_version(cls, template_name, context):
        """Get plain text version of a notification"""
        texts = {
            'deal_won': f"Congratulations! Deal Won: {context.get('deal', {}).get('name')}\nAmount: ${context.get('deal', {}).get('amount')}",
            'deal_lost': f"Deal Lost: {context.get('deal', {}).get('name')}\nReason: {context.get('deal', {}).get('lost_reason', 'Not specified')}",
            'task_due_soon': f"Task Due Soon: {context.get('task', {}).get('title')}\nDue: {context.get('task', {}).get('due_date')}",
            'task_overdue': f"OVERDUE: {context.get('task', {}).get('title')}\nWas due: {context.get('task', {}).get('due_date')}",
            'mention': f"@{context.get('mentioned_by')} mentioned you: {context.get('message')}",
        }
        return texts.get(template_name, f"You have a new notification from MyCRM")
