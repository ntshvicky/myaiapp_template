from django.db import models
from django.conf import settings

class CompareSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class ComparisonResult(models.Model):
    session = models.ForeignKey(CompareSession, related_name="results", on_delete=models.CASCADE)
    image1 = models.ImageField(upload_to="compares/")
    image2 = models.ImageField(upload_to="compares/")
    score = models.FloatField()
    diff_url = models.URLField(blank=True)
    ai_description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
