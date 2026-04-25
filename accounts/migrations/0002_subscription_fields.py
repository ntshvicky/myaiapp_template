from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="subscription_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="subscription_expires_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="subscription_plan",
            field=models.CharField(
                choices=[
                    ("free", "Free"),
                    ("plus", "Plus"),
                    ("pro", "Pro"),
                    ("enterprise", "Enterprise"),
                ],
                default="free",
                max_length=20,
            ),
        ),
    ]
