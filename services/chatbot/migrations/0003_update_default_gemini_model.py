from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chatbot", "0002_session_model_tokens"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chatsession",
            name="model_name",
            field=models.CharField(default="gemini-2.5-flash", max_length=120),
        ),
    ]
