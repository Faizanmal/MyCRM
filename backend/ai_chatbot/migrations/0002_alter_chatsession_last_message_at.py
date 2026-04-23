from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai_chatbot', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatsession',
            name='last_message_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
