from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0005_alter_stockalert_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='auto_renew',
            field=models.BooleanField(default=True, help_text='Whether subscription auto-renews at next_billing_date'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='subscription_status',
            field=models.CharField(default='active', help_text='Subscription status: active, canceled, past_due', max_length=20),
        ),
    ]

