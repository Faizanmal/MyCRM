# Generated for 02-session-auth: Two-factor backup recovery codes support

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user_management", "0006_userprofile_two_factor_enabled_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="two_factor_backup_codes",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
