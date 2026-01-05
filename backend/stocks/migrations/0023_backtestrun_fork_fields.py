from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("stocks", "0022_backtestrun_public_sharing_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="backtestrun",
            name="fork_count",
            field=models.PositiveIntegerField(default=0, help_text="How many times this backtest has been forked"),
        ),
        migrations.AddField(
            model_name="backtestrun",
            name="forked_from",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="forks",
                to="stocks.backtestrun",
            ),
        ),
    ]

