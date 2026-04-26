from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("resume_analysis", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Add CV metadata fields
        migrations.AddField(
            model_name="cv",
            name="candidate_name",
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name="cv",
            name="email",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name="cv",
            name="phone",
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AddField(
            model_name="cv",
            name="skills_summary",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="cv",
            name="total_experience",
            field=models.CharField(blank=True, max_length=50),
        ),
        # Add ordering + related_name to MatchReport
        migrations.AlterModelOptions(
            name="matchreport",
            options={"ordering": ["-score"]},
        ),
        migrations.AlterField(
            model_name="matchreport",
            name="cv",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reports",
                to="resume_analysis.cv",
            ),
        ),
        migrations.AlterField(
            model_name="matchreport",
            name="jd",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reports",
                to="resume_analysis.jobdescription",
            ),
        ),
        # CVChatSession model
        migrations.CreateModel(
            name="CVChatSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(default="CV Chat", max_length=120)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "cv",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="chat_sessions",
                        to="resume_analysis.cv",
                    ),
                ),
                (
                    "jd",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="resume_analysis.jobdescription",
                    ),
                ),
            ],
        ),
        # CVChatMessage model
        migrations.CreateModel(
            name="CVChatMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "sender",
                    models.CharField(
                        choices=[("user", "User"), ("bot", "Bot")],
                        max_length=4,
                    ),
                ),
                ("content", models.TextField()),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="messages",
                        to="resume_analysis.cvchatsession",
                    ),
                ),
            ],
        ),
    ]
