from django.db import models
from django.conf import settings

class ImageSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class ImageMessage(models.Model):
    session = models.ForeignKey(ImageSession, related_name="messages", on_delete=models.CASCADE)
    user_text = models.TextField(blank=True, default="")   # what the user typed
    prompt = models.TextField()                             # effective prompt sent to Imagen
    image = models.ImageField(upload_to="generated_images/", blank=True, null=True)
    image_url = models.TextField(blank=True, default="")   # fallback external URL
    timestamp = models.DateTimeField(auto_now_add=True)

    def get_image_url(self):
        """Return a usable URL for this image."""
        if self.image and self.image.name:
            from django.conf import settings
            return settings.MEDIA_URL + self.image.name
        return self.image_url or ""
