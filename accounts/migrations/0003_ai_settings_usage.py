from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_subscription_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="preferred_ai_provider",
            field=models.CharField(
                choices=[
                    ("gemini", "Google Gemini"),
                    ("openai", "OpenAI"),
                    ("anthropic", "Anthropic Claude"),
                ],
                default="gemini",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="preferred_model",
            field=models.CharField(default="gemini-1.5-flash", max_length=120),
        ),
        migrations.CreateModel(
            name="AIProviderCredential",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "provider",
                    models.CharField(
                        choices=[
                            ("gemini", "Google Gemini"),
                            ("openai", "OpenAI"),
                            ("anthropic", "Anthropic Claude"),
                        ],
                        max_length=20,
                    ),
                ),
                ("api_key", models.TextField(blank=True)),
                ("default_model", models.CharField(blank=True, max_length=120)),
                ("enabled", models.BooleanField(default=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="ai_credentials", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "unique_together": {("user", "provider")},
            },
        ),
        migrations.CreateModel(
            name="TokenUsage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("module", models.CharField(max_length=80)),
                ("conversation_id", models.CharField(blank=True, max_length=80)),
                ("provider", models.CharField(blank=True, max_length=20)),
                ("model_name", models.CharField(blank=True, max_length=120)),
                ("input_tokens", models.PositiveIntegerField(default=0)),
                ("output_tokens", models.PositiveIntegerField(default=0)),
                ("total_tokens", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="token_usage", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
