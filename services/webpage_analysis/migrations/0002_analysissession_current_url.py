from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("webpage_analysis", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="analysissession",
            name="current_url",
            field=models.URLField(blank=True, default=""),
        ),
    ]
