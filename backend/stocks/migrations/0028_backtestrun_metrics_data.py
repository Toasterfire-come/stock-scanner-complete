from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("stocks", "0027_favoriteticker"),
    ]

    operations = [
        migrations.AddField(
            model_name="backtestrun",
            name="metrics_data",
            field=models.JSONField(blank=True, help_text="Full computed metrics payload (including advanced metrics)", null=True),
        ),
    ]

