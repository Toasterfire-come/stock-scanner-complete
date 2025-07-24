# Generated migration for advanced features

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stocks', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='APIUsageTracking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('endpoint', models.CharField(db_index=True, max_length=200)),
                ('method', models.CharField(choices=[('GET', 'GET'), ('POST', 'POST'), ('PUT', 'PUT'), ('DELETE', 'DELETE'), ('PATCH', 'PATCH')], max_length=10)),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('response_time_ms', models.IntegerField(help_text='Response time in milliseconds')),
                ('status_code', models.IntegerField()),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.TextField(blank=True)),
                ('request_size_bytes', models.IntegerField(default=0)),
                ('response_size_bytes', models.IntegerField(default=0)),
                ('membership_tier', models.CharField(db_index=True, max_length=20)),
                ('cost_credits', models.DecimalField(decimal_places=4, default=0.0001, max_digits=10)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='api_usage', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='ComplianceLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_type', models.CharField(choices=[('login', 'User Login'), ('logout', 'User Logout'), ('password_change', 'Password Change'), ('profile_update', 'Profile Update'), ('payment_processed', 'Payment Processed'), ('data_export', 'Data Export'), ('api_access', 'API Access'), ('data_deletion', 'Data Deletion'), ('consent_given', 'Privacy Consent Given'), ('consent_withdrawn', 'Privacy Consent Withdrawn'), ('suspicious_activity', 'Suspicious Activity Detected'), ('security_violation', 'Security Policy Violation'), ('admin_action', 'Admin Action Performed')], max_length=50)),
                ('description', models.TextField()),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.TextField(blank=True)),
                ('session_id', models.CharField(blank=True, max_length=40)),
                ('request_data', models.JSONField(default=dict, help_text='Relevant request data for audit')),
                ('compliance_status', models.CharField(choices=[('compliant', 'Compliant'), ('flagged', 'Flagged for Review'), ('violation', 'Policy Violation'), ('resolved', 'Resolved')], default='compliant', max_length=20)),
                ('risk_level', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], default='low', max_length=10)),
                ('regulatory_framework', models.CharField(choices=[('gdpr', 'GDPR'), ('ccpa', 'CCPA'), ('finra', 'FINRA'), ('sox', 'Sarbanes-Oxley'), ('mifid', 'MiFID II'), ('pci_dss', 'PCI DSS'), ('general', 'General Security')], default='general', max_length=20)),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('resolved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='resolved_compliance_logs', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='compliance_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='MarketSentiment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticker', models.CharField(db_index=True, max_length=10)),
                ('sentiment_source', models.CharField(choices=[('twitter', 'Twitter'), ('reddit', 'Reddit'), ('news', 'Financial News'), ('analyst_reports', 'Analyst Reports'), ('options_flow', 'Options Flow'), ('social_aggregate', 'Social Media Aggregate'), ('professional', 'Professional Analysis')], max_length=50)),
                ('sentiment_score', models.FloatField(help_text='Score from -1.0 (very bearish) to 1.0 (very bullish)')),
                ('confidence_level', models.FloatField(help_text='Confidence level from 0.0 to 1.0')),
                ('volume_mentions', models.IntegerField(default=0, help_text='Number of mentions/posts analyzed')),
                ('positive_mentions', models.IntegerField(default=0)),
                ('negative_mentions', models.IntegerField(default=0)),
                ('neutral_mentions', models.IntegerField(default=0)),
                ('key_phrases', models.JSONField(default=list, help_text='Most mentioned phrases/keywords')),
                ('sentiment_trend', models.CharField(choices=[('improving', 'Improving'), ('declining', 'Declining'), ('stable', 'Stable'), ('volatile', 'Volatile')], default='stable', max_length=20)),
                ('analyzed_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('data_timeframe', models.CharField(default='24h', help_text='Timeframe of analyzed data', max_length=20)),
            ],
            options={
                'ordering': ['-analyzed_at'],
            },
        ),
        migrations.CreateModel(
            name='SecurityEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(choices=[('failed_login', 'Failed Login Attempt'), ('brute_force', 'Brute Force Attack'), ('unusual_access', 'Unusual Access Pattern'), ('data_breach_attempt', 'Data Breach Attempt'), ('sql_injection', 'SQL Injection Attempt'), ('xss_attempt', 'XSS Attack Attempt'), ('rate_limit_exceeded', 'Rate Limit Exceeded'), ('unauthorized_api_access', 'Unauthorized API Access'), ('suspicious_geolocation', 'Suspicious Geographic Location'), ('account_takeover', 'Potential Account Takeover'), ('malware_detected', 'Malware Detection'), ('phishing_attempt', 'Phishing Attempt')], max_length=50)),
                ('severity', models.CharField(choices=[('info', 'Informational'), ('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], max_length=10)),
                ('source_ip', models.GenericIPAddressField()),
                ('target_endpoint', models.CharField(blank=True, max_length=200)),
                ('description', models.TextField()),
                ('request_data', models.JSONField(default=dict)),
                ('geolocation', models.JSONField(default=dict, help_text='IP geolocation data')),
                ('user_agent', models.TextField(blank=True)),
                ('attack_vector', models.CharField(blank=True, max_length=100)),
                ('mitigation_action', models.CharField(choices=[('none', 'No Action'), ('logged', 'Logged Only'), ('blocked', 'Request Blocked'), ('rate_limited', 'Rate Limited'), ('account_locked', 'Account Locked'), ('ip_banned', 'IP Address Banned'), ('escalated', 'Escalated to Admin')], default='logged', max_length=50)),
                ('detected_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('false_positive', models.BooleanField(default=False)),
                ('target_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='security_events', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-detected_at'],
            },
        ),
        migrations.CreateModel(
            name='PortfolioAnalytics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sharpe_ratio', models.FloatField(blank=True, help_text='Risk-adjusted return measure', null=True)),
                ('beta', models.FloatField(blank=True, help_text='Market sensitivity', null=True)),
                ('alpha', models.FloatField(blank=True, help_text='Excess return vs market', null=True)),
                ('value_at_risk_1d', models.FloatField(blank=True, help_text='1-day VaR at 95% confidence', null=True)),
                ('value_at_risk_1w', models.FloatField(blank=True, help_text='1-week VaR at 95% confidence', null=True)),
                ('max_drawdown', models.FloatField(blank=True, help_text='Maximum historical loss', null=True)),
                ('volatility_annualized', models.FloatField(blank=True, help_text='Annualized volatility', null=True)),
                ('total_return_1m', models.FloatField(blank=True, null=True)),
                ('total_return_3m', models.FloatField(blank=True, null=True)),
                ('total_return_6m', models.FloatField(blank=True, null=True)),
                ('total_return_1y', models.FloatField(blank=True, null=True)),
                ('total_return_ytd', models.FloatField(blank=True, null=True)),
                ('annualized_return', models.FloatField(blank=True, null=True)),
                ('sector_concentration_risk', models.FloatField(blank=True, help_text='0-1, higher means more concentrated', null=True)),
                ('geographic_concentration', models.FloatField(blank=True, null=True)),
                ('largest_position_weight', models.FloatField(blank=True, null=True)),
                ('effective_number_stocks', models.FloatField(blank=True, help_text='Diversification measure', null=True)),
                ('sector_allocation', models.JSONField(default=dict, help_text='Sector breakdown percentages')),
                ('market_cap_allocation', models.JSONField(default=dict, help_text='Large/Mid/Small cap breakdown')),
                ('geographic_allocation', models.JSONField(default=dict, help_text='Geographic region breakdown')),
                ('performance_attribution', models.JSONField(default=dict, help_text='Performance attribution by holding')),
                ('top_contributors', models.JSONField(default=list, help_text='Top 5 performance contributors')),
                ('top_detractors', models.JSONField(default=list, help_text='Top 5 performance detractors')),
                ('rebalancing_needed', models.BooleanField(default=False)),
                ('rebalancing_suggestions', models.JSONField(default=list, help_text='Suggested portfolio adjustments')),
                ('risk_score', models.IntegerField(default=50, help_text='Overall portfolio risk score 1-100')),
                ('last_calculated', models.DateTimeField(auto_now=True)),
                ('calculation_status', models.CharField(choices=[('pending', 'Pending'), ('calculating', 'Calculating'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('portfolio', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='analytics', to='stocks.portfolio')),
            ],
            options={
                'ordering': ['-last_calculated'],
            },
        ),
        migrations.AddIndex(
            model_name='securityevent',
            index=models.Index(fields=['severity', 'detected_at'], name='stocks_secu_severit_d14cde_idx'),
        ),
        migrations.AddIndex(
            model_name='securityevent',
            index=models.Index(fields=['source_ip', 'detected_at'], name='stocks_secu_source__2f8c0e_idx'),
        ),
        migrations.AddIndex(
            model_name='securityevent',
            index=models.Index(fields=['event_type', 'detected_at'], name='stocks_secu_event_t_3a98e6_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='marketsentiment',
            unique_together={('ticker', 'sentiment_source', 'analyzed_at')},
        ),
        migrations.AddIndex(
            model_name='marketsentiment',
            index=models.Index(fields=['ticker', 'analyzed_at'], name='stocks_mark_ticker_e1aec0_idx'),
        ),
        migrations.AddIndex(
            model_name='marketsentiment',
            index=models.Index(fields=['sentiment_score', 'analyzed_at'], name='stocks_mark_sentime_d5ed45_idx'),
        ),
        migrations.AddIndex(
            model_name='compliancelog',
            index=models.Index(fields=['user', 'timestamp'], name='stocks_comp_user_id_5a8f8d_idx'),
        ),
        migrations.AddIndex(
            model_name='compliancelog',
            index=models.Index(fields=['action_type', 'timestamp'], name='stocks_comp_action__34a0c8_idx'),
        ),
        migrations.AddIndex(
            model_name='compliancelog',
            index=models.Index(fields=['compliance_status', 'risk_level'], name='stocks_comp_complia_e8a4d3_idx'),
        ),
        migrations.AddIndex(
            model_name='compliancelog',
            index=models.Index(fields=['regulatory_framework', 'timestamp'], name='stocks_comp_regulat_b2e3c8_idx'),
        ),
        migrations.AddIndex(
            model_name='apiusagetracking',
            index=models.Index(fields=['user', 'timestamp'], name='stocks_apiu_user_id_6fb6b1_idx'),
        ),
        migrations.AddIndex(
            model_name='apiusagetracking',
            index=models.Index(fields=['endpoint', 'timestamp'], name='stocks_apiu_endpoin_0b1b1a_idx'),
        ),
        migrations.AddIndex(
            model_name='apiusagetracking',
            index=models.Index(fields=['membership_tier', 'timestamp'], name='stocks_apiu_members_92b72a_idx'),
        ),
    ]
