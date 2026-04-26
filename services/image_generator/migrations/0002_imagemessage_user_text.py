from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("image_generator", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="imagemessage",
            name="user_text",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
    ]
