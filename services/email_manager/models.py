from django.db import models
from django.conf import settings


class EmailAccount(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="email_accounts")
    display_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField()

    # IMAP (reading)
    imap_host = models.CharField(max_length=200, default="imap.gmail.com")
    imap_port = models.IntegerField(default=993)
    imap_use_ssl = models.BooleanField(default=True)

    # SMTP (sending)
    smtp_host = models.CharField(max_length=200, default="smtp.gmail.com")
    smtp_port = models.IntegerField(default=587)
    smtp_use_tls = models.BooleanField(default=True)

    # Credentials
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=500, help_text="App password (Gmail) or IMAP password")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
