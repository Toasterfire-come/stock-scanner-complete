from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stocks', '0007_referrals_and_webhook'),
    ]

    operations = [
        migrations.CreateModel(
            name='APIKey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='default', max_length=100)),
                ('key_hash', models.CharField(db_index=True, max_length=128)),
                ('prefix', models.CharField(db_index=True, max_length=12)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_used_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='api_keys', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name='apikey',
            index=models.Index(fields=['user', 'is_active'], name='stocks_apik_user_id_6a7f43_idx'),
        ),
        migrations.AddIndex(
            model_name='apikey',
            index=models.Index(fields=['prefix', 'is_active'], name='stocks_apik_prefix__f1e8a4_idx'),
        ),
    ]

