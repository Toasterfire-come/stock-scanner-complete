# Migration to remove pay-as-you-go functionality

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0002_advanced_features'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='apiusagetracking',
            name='cost_credits',
        ),
    ]
