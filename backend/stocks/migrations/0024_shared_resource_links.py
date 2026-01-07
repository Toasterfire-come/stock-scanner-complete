from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("stocks", "0023_backtestrun_fork_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="SharedResourceLink",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(db_index=True, max_length=64, unique=True)),
                ("resource_type", models.CharField(choices=[("portfolio", "Portfolio"), ("watchlist", "Watchlist")], max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("view_count", models.PositiveIntegerField(default=0)),
                ("last_viewed_at", models.DateTimeField(blank=True, null=True)),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="shared_links", to="auth.user")),
                ("portfolio", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="share_links", to="stocks.userportfolio")),
                ("watchlist", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="share_links", to="stocks.userwatchlist")),
            ],
            options={
                "indexes": [
                    models.Index(fields=["resource_type", "slug"], name="stocks_share_resource_type_slug_idx"),
                    models.Index(fields=["created_by", "-created_at"], name="stocks_share_created_by_created_at_idx"),
                ],
            },
        ),
    ]

