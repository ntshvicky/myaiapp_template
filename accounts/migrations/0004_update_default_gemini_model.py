from django.db import migrations, models


def update_gemini_model_values(apps, schema_editor):
    UserProfile = apps.get_model("accounts", "UserProfile")
    AIProviderCredential = apps.get_model("accounts", "AIProviderCredential")
    ChatSession = apps.get_model("chatbot", "ChatSession")

    stale_models = ["gemini-1.5-flash", "gemini-1.5-pro"]
    UserProfile.objects.filter(preferred_ai_provider="gemini", preferred_model__in=stale_models).update(
        preferred_model="gemini-2.5-flash"
    )
    AIProviderCredential.objects.filter(provider="gemini", default_model__in=stale_models).update(
        default_model="gemini-2.5-flash"
    )
    ChatSession.objects.filter(provider="gemini", model_name__in=stale_models).update(
        model_name="gemini-2.5-flash"
    )


class Migration(migrations.Migration):

    dependencies = [
        ("chatbot", "0002_session_model_tokens"),
        ("accounts", "0003_ai_settings_usage"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="preferred_model",
            field=models.CharField(default="gemini-2.5-flash", max_length=120),
        ),
        migrations.RunPython(update_gemini_model_values, migrations.RunPython.noop),
    ]
