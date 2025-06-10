from django.db import models
from django.conf import settings

class Document(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to="documents/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

class DocChatSession(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class DocChatMessage(models.Model):
    session = models.ForeignKey(DocChatSession, related_name="messages", on_delete=models.CASCADE)
    sender = models.CharField(max_length=4, choices=[("user","User"),("bot","Bot")])
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
