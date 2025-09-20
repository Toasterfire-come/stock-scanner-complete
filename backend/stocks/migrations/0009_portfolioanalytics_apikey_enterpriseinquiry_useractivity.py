from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("stocks", "0008_userprofile_alerts_limit_userprofile_alerts_sent_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PortfolioAnalytics",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField()),
                ("total_value", models.DecimalField(decimal_places=2, max_digits=15)),
                ("day_change", models.DecimalField(decimal_places=2, max_digits=15)),
                ("performance_metrics", models.JSONField()),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="portfolio_analytics", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-date"],
                "unique_together": {("user", "date")},
                "indexes": [
                    models.Index(fields=["user", "-date"], name="stocks_port_user_id_7a4f17_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="APIKey",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.CharField(max_length=64, unique=True)),
                ("name", models.CharField(max_length=200)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("last_used", models.DateTimeField(null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="api_keys", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["user", "-created_at"], name="stocks_apik_user_id_2c6d6b_idx"),
                    models.Index(fields=["is_active"], name="stocks_apik_is_acti_3f1b86_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="EnterpriseInquiry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("company_name", models.CharField(max_length=200)),
                ("contact_email", models.EmailField(max_length=254)),
                ("contact_name", models.CharField(max_length=200)),
                ("phone", models.CharField(max_length=20)),
                ("message", models.TextField()),
                ("solution_type", models.CharField(max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["contact_email", "-created_at"], name="stocks_ente_contac_d5ab7e_idx"),
                    models.Index(fields=["solution_type", "-created_at"], name="stocks_ente_soluti_7a14a9_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="UserActivity",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("action_type", models.CharField(max_length=50)),
                ("details", models.JSONField()),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="activities", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-timestamp"],
                "indexes": [
                    models.Index(fields=["user", "-timestamp"], name="stocks_user_user_id_0e1d6a_idx"),
                    models.Index(fields=["action_type", "-timestamp"], name="stocks_user_action__70b2a3_idx"),
                ],
            },
        ),
    ]

