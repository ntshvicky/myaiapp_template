from django.db import models
from django.conf import settings

class JobDescription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to="jds/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

class CV(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to="cvs/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

class MatchReport(models.Model):
    jd = models.ForeignKey(JobDescription, on_delete=models.CASCADE)
    cv = models.ForeignKey(CV, on_delete=models.CASCADE)
    score = models.FloatField()
    details = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
