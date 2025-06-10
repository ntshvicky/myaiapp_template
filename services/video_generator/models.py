from django.db import models
from django.conf import settings

class VideoSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class VideoMessage(models.Model):
    session = models.ForeignKey(VideoSession, related_name="messages", on_delete=models.CASCADE)
    prompt = models.TextField()
    video_url = models.URLField()
    timestamp = models.DateTimeField(auto_now_add=True)
