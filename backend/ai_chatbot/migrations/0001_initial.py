import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user_management', '0005_alter_user_last_login_alter_user_last_login_ip'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatSession',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(default='New Chat', max_length=255)),
                ('context_type', models.CharField(blank=True, max_length=50)),
                ('context_id', models.CharField(blank=True, max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('message_count', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_message_at', models.DateTimeField(blank=True)),
                ('user', models.ForeignKey(on_delete=models.CASCADE, related_name='chat_sessions', to='user_management.user')),
            ],
            options={
                'db_table': 'ai_chatbot_sessions',
                'verbose_name': 'Chat Session',
                'verbose_name_plural': 'Chat Sessions',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('role', models.CharField(choices=[('user', 'User'), ('assistant', 'Assistant'), ('system', 'System')], max_length=20)),
                ('message_type', models.CharField(choices=[('text', 'Text'), ('query_result', 'Query Result'), ('email_draft', 'Email Draft'), ('action_suggestion', 'Action Suggestion'), ('data_summary', 'Data Summary'), ('error', 'Error')], default='text', max_length=30)),
                ('content', models.TextField()),
                ('structured_data', models.JSONField(default=dict, blank=True)),
                ('tokens_used', models.IntegerField(default=0)),
                ('model_used', models.CharField(blank=True, max_length=50)),
                ('processing_time_ms', models.IntegerField(default=0)),
                ('is_helpful', models.BooleanField(blank=True)),
                ('feedback', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('session', models.ForeignKey(on_delete=models.CASCADE, related_name='messages', to='ai_chatbot.chatsession')),
            ],
            options={
                'db_table': 'ai_chatbot_messages',
                'verbose_name': 'Chat Message',
                'verbose_name_plural': 'Chat Messages',
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='ChatIntent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('category', models.CharField(choices=[('query', 'Data Query'), ('email', 'Email Generation'), ('action', 'Action Suggestion'), ('report', 'Report Generation'), ('help', 'Help/Documentation'), ('general', 'General')], max_length=30)),
                ('example_phrases', models.JSONField(default=list)),
                ('handler_function', models.CharField(max_length=255)),
                ('required_parameters', models.JSONField(default=list, blank=True)),
                ('usage_count', models.IntegerField(default=0)),
                ('success_rate', models.FloatField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'ai_chatbot_intents',
                'verbose_name': 'Chat Intent',
                'verbose_name_plural': 'Chat Intents',
            },
        ),
        migrations.CreateModel(
            name='QuickAction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('icon', models.CharField(blank=True, max_length=50)),
                ('prompt_template', models.TextField()),
                ('requires_context', models.BooleanField(default=False)),
                ('context_types', models.JSONField(default=list, blank=True)),
                ('category', models.CharField(blank=True, max_length=50)),
                ('order', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'ai_chatbot_quick_actions',
                'verbose_name': 'Quick Action',
                'verbose_name_plural': 'Quick Actions',
                'ordering': ['category', 'order'],
            },
        ),
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('purpose', models.CharField(choices=[('follow_up', 'Follow Up'), ('introduction', 'Introduction'), ('proposal', 'Proposal'), ('thank_you', 'Thank You'), ('meeting_request', 'Meeting Request'), ('closing', 'Closing'), ('nurture', 'Nurture')], max_length=30)),
                ('tone', models.CharField(choices=[('professional', 'Professional'), ('friendly', 'Friendly'), ('formal', 'Formal'), ('casual', 'Casual'), ('persuasive', 'Persuasive')], default='professional', max_length=30)),
                ('subject_template', models.CharField(max_length=255)),
                ('body_template', models.TextField()),
                ('variables', models.JSONField(default=list, blank=True)),
                ('usage_count', models.IntegerField(default=0)),
                ('avg_open_rate', models.FloatField(blank=True)),
                ('avg_response_rate', models.FloatField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=models.SET_NULL, related_name='ai_chatbot_email_templates', to='user_management.user')),
            ],
            options={
                'db_table': 'ai_chatbot_email_templates',
                'verbose_name': 'Email Template',
                'verbose_name_plural': 'Email Templates',
            },
        ),
    ]
