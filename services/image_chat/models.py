from django.db import models
from django.conf import settings

class ImageUpload(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="chat_images/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

class ImageChatSession(models.Model):
    image = models.ForeignKey(ImageUpload, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class ImageChatMessage(models.Model):
    session = models.ForeignKey(ImageChatSession, related_name="messages", on_delete=models.CASCADE)
    sender = models.CharField(max_length=4, choices=[("user","User"),("bot","Bot")])
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
