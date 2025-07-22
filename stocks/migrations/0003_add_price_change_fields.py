# Generated manually to add missing price change fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0002_advanced_features'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockalert',
            name='price_change_today',
            field=models.FloatField(blank=True, help_text='Price change from previous close', null=True),
        ),
        migrations.AddField(
            model_name='stockalert',
            name='price_change_percent',
            field=models.FloatField(blank=True, help_text='Percentage change from previous close', null=True),
        ),
    ]
