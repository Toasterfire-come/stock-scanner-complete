# Generated manually to add new models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stocks', '0001_initial'),
    ]

    operations = [
        # Create UserProfile model
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plan', models.CharField(choices=[('free', 'Free'), ('bronze', 'Bronze'), ('silver', 'Silver'), ('gold', 'Gold')], default='free', max_length=20)),
                ('is_premium', models.BooleanField(default=False)),
                ('monthly_api_calls', models.IntegerField(default=0)),
                ('daily_api_calls', models.IntegerField(default=0)),
                ('last_api_call', models.DateTimeField(blank=True, null=True)),
                ('last_daily_reset', models.DateField(blank=True, null=True)),
                ('last_monthly_reset', models.DateField(blank=True, null=True)),
                ('paypal_subscription_id', models.CharField(blank=True, max_length=100)),
                ('subscription_active', models.BooleanField(default=False)),
                ('subscription_end_date', models.DateTimeField(blank=True, null=True)),
                ('trial_used', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        
        # Create APIToken model
        migrations.CreateModel(
            name='APIToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(default=uuid.uuid4, max_length=255, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_used', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        
        # Create BillingHistory model
        migrations.CreateModel(
            name='BillingHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plan_type', models.CharField(choices=[('bronze', 'Bronze'), ('silver', 'Silver'), ('gold', 'Gold')], max_length=20)),
                ('billing_cycle', models.CharField(choices=[('monthly', 'Monthly'), ('annual', 'Annual')], max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('paypal_order_id', models.CharField(max_length=100, unique=True)),
                ('paypal_payment_id', models.CharField(blank=True, max_length=100)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('discount_code', models.CharField(blank=True, max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        
        # Create UsageStats model
        migrations.CreateModel(
            name='UsageStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('endpoint', models.CharField(max_length=100)),
                ('api_calls', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'date', 'endpoint')},
            },
        ),
        
        # Modify StockAlert model to make it compatible with new structure
        migrations.RemoveField(
            model_name='stockalert',
            name='user',
        ),
        migrations.RemoveField(
            model_name='stockalert',
            name='alert_type',
        ),
        migrations.RemoveField(
            model_name='stockalert',
            name='target_value',
        ),
        migrations.AddField(
            model_name='stockalert',
            name='target_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stockalert',
            name='condition',
            field=models.CharField(choices=[('above', 'Price Above'), ('below', 'Price Below')], default='above', max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stockalert',
            name='email',
            field=models.EmailField(default='test@example.com', max_length=254),
            preserve_default=False,
        ),
    ]
