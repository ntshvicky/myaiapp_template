from django.db import models
from django.conf import settings

class AnalysisSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class AnalysisMessage(models.Model):
    session = models.ForeignKey(AnalysisSession, related_name="messages", on_delete=models.CASCADE)
    sender = models.CharField(max_length=4, choices=[("user","User"),("bot","Bot")])
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
