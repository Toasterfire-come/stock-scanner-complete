from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("stocks", "0021_add_achievement_model"),
    ]

    operations = [
        migrations.AddField(
            model_name="backtestrun",
            name="public_view_count",
            field=models.PositiveIntegerField(default=0, help_text="Public page views"),
        ),
        migrations.AddField(
            model_name="backtestrun",
            name="share_slug",
            field=models.SlugField(
                blank=True,
                db_index=True,
                help_text="Public share slug (stable URL)",
                max_length=64,
                null=True,
                unique=True,
            ),
        ),
        migrations.AddField(
            model_name="backtestrun",
            name="shared_at",
            field=models.DateTimeField(
                blank=True,
                help_text="When backtest was first made public",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="backtestrun",
            name="is_public",
            field=models.BooleanField(
                default=False,
                help_text="Whether this backtest is publicly shareable",
            ),
        ),
    ]

