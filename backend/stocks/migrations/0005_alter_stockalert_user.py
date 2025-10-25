from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0004_billinghistory_notificationhistory_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockalert',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='auth.user'),
        ),
    ]

