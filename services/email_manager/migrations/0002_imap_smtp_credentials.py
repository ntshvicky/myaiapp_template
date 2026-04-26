"""
Migration: Replace oauth_token with full IMAP/SMTP credential fields.
Drops StoredEmail (replaced by live IMAP fetch).
"""
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("email_manager", "0001_initial"),
    ]

    operations = [
        # Drop StoredEmail — emails now fetched live from IMAP
        migrations.DeleteModel(name="StoredEmail"),

        # Rename address → email
        migrations.RenameField(
            model_name="emailaccount",
            old_name="address",
            new_name="email",
        ),

        # Remove the old oauth_token
        migrations.RemoveField(model_name="emailaccount", name="oauth_token"),

        # Add all new fields
        migrations.AddField(
            model_name="emailaccount",
            name="display_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="emailaccount",
            name="imap_host",
            field=models.CharField(default="imap.gmail.com", max_length=200),
        ),
        migrations.AddField(
            model_name="emailaccount",
            name="imap_port",
            field=models.IntegerField(default=993),
        ),
        migrations.AddField(
            model_name="emailaccount",
            name="imap_use_ssl",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="emailaccount",
            name="smtp_host",
            field=models.CharField(default="smtp.gmail.com", max_length=200),
        ),
        migrations.AddField(
            model_name="emailaccount",
            name="smtp_port",
            field=models.IntegerField(default=587),
        ),
        migrations.AddField(
            model_name="emailaccount",
            name="smtp_use_tls",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="emailaccount",
            name="username",
            field=models.CharField(default="", max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="emailaccount",
            name="password",
            field=models.CharField(
                default="",
                help_text="App password (Gmail) or IMAP password",
                max_length=500,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="emailaccount",
            name="created_at",
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
