from django.db import models
from django.conf import settings

class EmailAccount(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.EmailField()
    oauth_token = models.TextField()

class StoredEmail(models.Model):
    account = models.ForeignKey(EmailAccount, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    received_at = models.DateTimeField()
