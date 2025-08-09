# Generated migration for REF50 discount tracking and revenue analytics

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def create_ref50_discount(apps, schema_editor):
    DiscountCode = apps.get_model('stocks', 'DiscountCode')
    # Create or update REF50 discount code
    obj, _created = DiscountCode.objects.update_or_create(
        code='REF50',
        defaults={
            'discount_percentage': 50.00,
            'is_active': True,
            'applies_to_first_payment_only': True,
        }
    )


def delete_ref50_discount(apps, schema_editor):
    DiscountCode = apps.get_model('stocks', 'DiscountCode')
    DiscountCode.objects.filter(code='REF50').delete()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stocks', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiscountCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(db_index=True, max_length=20, unique=True)),
                ('discount_percentage', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('is_active', models.BooleanField(default=True)),
                ('applies_to_first_payment_only', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserDiscountUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_used_date', models.DateTimeField(auto_now_add=True)),
                ('total_savings', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('discount_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_usage', to='stocks.discountcode')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discount_usage', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'discount_code')},
            },
        ),
        migrations.CreateModel(
            name='RevenueTracking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('revenue_type', models.CharField(choices=[('regular', 'Regular Revenue'), ('discount_generated', 'Discount Code Generated Revenue')], default='regular', max_length=20)),
                ('original_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('discount_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('final_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_date', models.DateTimeField()),
                ('month_year', models.CharField(db_index=True, max_length=7)),
                ('commission_rate', models.DecimalField(decimal_places=2, default=20.0, max_digits=5)),
                ('commission_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('discount_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='stocks.discountcode')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='revenue_tracking', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MonthlyRevenueSummary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month_year', models.CharField(db_index=True, max_length=7, unique=True)),
                ('total_revenue', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('regular_revenue', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('discount_generated_revenue', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('total_discount_savings', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('total_commission_owed', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('total_paying_users', models.IntegerField(default=0)),
                ('new_discount_users', models.IntegerField(default=0)),
                ('existing_discount_users', models.IntegerField(default=0)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        # Insert initial REF50 discount code using ORM for cross-database compatibility
        migrations.RunPython(create_ref50_discount, reverse_code=delete_ref50_discount),
    ]