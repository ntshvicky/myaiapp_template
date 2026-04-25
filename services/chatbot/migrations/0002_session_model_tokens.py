from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chatbot", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="chatsession",
            name="model_name",
            field=models.CharField(default="gemini-1.5-flash", max_length=120),
        ),
        migrations.AddField(
            model_name="chatsession",
            name="provider",
            field=models.CharField(default="gemini", max_length=20),
        ),
        migrations.AddField(
            model_name="chatsession",
            name="title",
            field=models.CharField(default="New chat", max_length=140),
        ),
        migrations.AddField(
            model_name="chatsession",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="chatmessage",
            name="input_tokens",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="chatmessage",
            name="output_tokens",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="chatmessage",
            name="total_tokens",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
