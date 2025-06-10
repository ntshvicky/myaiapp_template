from django.db import models
from django.conf import settings

class MusicSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class MusicMessage(models.Model):
    session = models.ForeignKey(MusicSession, related_name="messages", on_delete=models.CASCADE)
    prompt = models.TextField()
    music_url = models.URLField()
    timestamp = models.DateTimeField(auto_now_add=True)
