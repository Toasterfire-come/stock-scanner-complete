from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stocks', '0006_userprofile_autorenew_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReferralAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inviter_uid', models.CharField(db_index=True, help_text='External inviter identifier for non-auth flows', max_length=64)),
                ('referral_code', models.CharField(db_index=True, max_length=16, unique=True)),
                ('rewards_months_granted', models.IntegerField(default=0)),
                ('free_months_redeemed', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='referral_account', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ReferralInvite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inviter_uid', models.CharField(db_index=True, max_length=64)),
                ('invitee_email', models.EmailField(db_index=True, max_length=254)),
                ('referral_code', models.CharField(db_index=True, max_length=16)),
                ('status', models.CharField(choices=[('invited', 'Invited'), ('accepted', 'Accepted'), ('paid', 'Paid')], default='invited', max_length=16)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('invitee_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='referral_origin', to=settings.AUTH_USER_MODEL)),
                ('inviter', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sent_referral_invites', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('invitee_email', 'referral_code')},
            },
        ),
        migrations.CreateModel(
            name='ReferralRedemption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inviter_uid', models.CharField(db_index=True, max_length=64)),
                ('months', models.PositiveIntegerField(default=1)),
                ('invites_consumed', models.PositiveIntegerField(default=3)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='WebhookEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(help_text='stripe|paypal|custom', max_length=32)),
                ('event_id', models.CharField(db_index=True, max_length=128, unique=True)),
                ('signature', models.CharField(blank=True, max_length=256)),
                ('payload_hash', models.CharField(blank=True, max_length=64)),
                ('received_at', models.DateTimeField(auto_now_add=True)),
                ('processed_at', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(default='received', max_length=16)),
            ],
        ),
        migrations.AddIndex(
            model_name='referralaccount',
            index=models.Index(fields=['inviter_uid'], name='stocks_refe_inviter_3f16a5_idx'),
        ),
        migrations.AddIndex(
            model_name='referralinvite',
            index=models.Index(fields=['inviter_uid', 'status'], name='stocks_refe_inviter_1a7d1c_idx'),
        ),
        migrations.AddIndex(
            model_name='referralinvite',
            index=models.Index(fields=['referral_code', 'status'], name='stocks_refe_referral_f4d6d2_idx'),
        ),
        migrations.AddIndex(
            model_name='referralredemption',
            index=models.Index(fields=['inviter_uid', 'created_at'], name='stocks_refe_inviter_8a2c42_idx'),
        ),
        migrations.AddIndex(
            model_name='webhookevent',
            index=models.Index(fields=['source', 'event_id'], name='stocks_webh_source__0a2e5a_idx'),
        ),
        migrations.AddIndex(
            model_name='webhookevent',
            index=models.Index(fields=['status'], name='stocks_webh_status_1c5b2f_idx'),
        ),
        migrations.AddIndex(
            model_name='webhookevent',
            index=models.Index(fields=['received_at'], name='stocks_webh_received_3b82a7_idx'),
        ),
    ]

