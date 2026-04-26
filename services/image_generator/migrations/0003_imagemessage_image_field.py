from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("image_generator", "0002_imagemessage_user_text"),
    ]

    operations = [
        migrations.AddField(
            model_name="imagemessage",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="generated_images/"),
        ),
        migrations.AlterField(
            model_name="imagemessage",
            name="image_url",
            field=models.TextField(blank=True, default=""),
        ),
    ]
