from django.db import models
from django.conf import settings


class JobDescription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to="jds/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name.split("/")[-1]


class CV(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to="cvs/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # Extracted metadata (populated on first analysis)
    candidate_name  = models.CharField(max_length=150, blank=True)
    email           = models.EmailField(blank=True)
    phone           = models.CharField(max_length=40, blank=True)
    skills_summary  = models.TextField(blank=True)
    total_experience = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.candidate_name or self.file.name.split("/")[-1]

    def display_name(self):
        return self.candidate_name or self.file.name.split("/")[-1]


class MatchReport(models.Model):
    jd = models.ForeignKey(JobDescription, on_delete=models.CASCADE, related_name="reports")
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name="reports")
    score = models.FloatField()
    details = models.JSONField()          # {"analysis": str, "skills_match": [], "gaps": []}
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-score"]


class CVChatSession(models.Model):
    """Persistent chat session for Q&A about a specific CV."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cv   = models.ForeignKey(CV, on_delete=models.CASCADE, related_name="chat_sessions")
    jd   = models.ForeignKey(JobDescription, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=120, default="CV Chat")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} — {self.cv}"


class CVChatMessage(models.Model):
    session = models.ForeignKey(CVChatSession, related_name="messages", on_delete=models.CASCADE)
    sender  = models.CharField(max_length=4, choices=[("user", "User"), ("bot", "Bot")])
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
