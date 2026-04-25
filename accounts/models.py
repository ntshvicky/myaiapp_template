from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class UserProfile(AbstractUser):
    PLAN_FREE = "free"
    PLAN_PLUS = "plus"
    PLAN_PRO = "pro"
    PLAN_ENTERPRISE = "enterprise"

    PLAN_CHOICES = [
        (PLAN_FREE, "Free"),
        (PLAN_PLUS, "Plus"),
        (PLAN_PRO, "Pro"),
        (PLAN_ENTERPRISE, "Enterprise"),
    ]

    PROVIDER_GEMINI = "gemini"
    PROVIDER_OPENAI = "openai"
    PROVIDER_ANTHROPIC = "anthropic"

    AI_PROVIDER_CHOICES = [
        (PROVIDER_GEMINI, "Google Gemini"),
        (PROVIDER_OPENAI, "OpenAI"),
        (PROVIDER_ANTHROPIC, "Anthropic Claude"),
    ]

    subscription_plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default=PLAN_FREE)
    subscription_active = models.BooleanField(default=True)
    subscription_expires_at = models.DateTimeField(blank=True, null=True)
    preferred_ai_provider = models.CharField(max_length=20, choices=AI_PROVIDER_CHOICES, default=PROVIDER_GEMINI)
    preferred_model = models.CharField(max_length=120, default="gemini-2.5-flash")
    can_use_chatbot = models.BooleanField(default=True)
    can_use_webpage_analysis = models.BooleanField(default=True)
    can_use_image_generator = models.BooleanField(default=True)
    can_use_video_generator = models.BooleanField(default=True)
    can_use_music_generator = models.BooleanField(default=True)
    can_use_document_chat = models.BooleanField(default=True)
    can_use_content_writer = models.BooleanField(default=True)
    can_use_email_manager = models.BooleanField(default=True)
    can_use_resume_analysis = models.BooleanField(default=True)
    can_use_image_chat = models.BooleanField(default=True)
    can_use_compare_images = models.BooleanField(default=True)

    PLAN_FEATURES = {
        PLAN_FREE: {
            "chatbot",
            "content_writer",
            "image_chat",
            "compare_images",
        },
        PLAN_PLUS: {
            "chatbot",
            "content_writer",
            "image_chat",
            "compare_images",
            "document_chat",
            "webpage_analysis",
            "image_generator",
            "music_generator",
        },
        PLAN_PRO: {
            "chatbot",
            "content_writer",
            "image_chat",
            "compare_images",
            "document_chat",
            "webpage_analysis",
            "image_generator",
            "music_generator",
            "video_generator",
            "email_manager",
            "resume_analysis",
        },
        PLAN_ENTERPRISE: {
            "chatbot",
            "content_writer",
            "image_chat",
            "compare_images",
            "document_chat",
            "webpage_analysis",
            "image_generator",
            "music_generator",
            "video_generator",
            "email_manager",
            "resume_analysis",
        },
    }

    def has_active_subscription(self):
        if not self.subscription_active:
            return False
        return not self.subscription_expires_at or self.subscription_expires_at > timezone.now()

    def can_access_feature(self, feature_key):
        flag_name = f"can_use_{feature_key}"
        manual_flag = getattr(self, flag_name, True)
        return self.has_active_subscription() and manual_flag and feature_key in self.PLAN_FEATURES.get(self.subscription_plan, set())


class AIProviderCredential(models.Model):
    user = models.ForeignKey(UserProfile, related_name="ai_credentials", on_delete=models.CASCADE)
    provider = models.CharField(max_length=20, choices=UserProfile.AI_PROVIDER_CHOICES)
    api_key = models.TextField(blank=True)
    default_model = models.CharField(max_length=120, blank=True)
    enabled = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "provider")

    def masked_key(self):
        if not self.api_key:
            return "Not configured"
        if len(self.api_key) <= 8:
            return "Configured"
        return f"{self.api_key[:4]}...{self.api_key[-4:]}"


class TokenUsage(models.Model):
    user = models.ForeignKey(UserProfile, related_name="token_usage", on_delete=models.CASCADE)
    module = models.CharField(max_length=80)
    conversation_id = models.CharField(max_length=80, blank=True)
    provider = models.CharField(max_length=20, blank=True)
    model_name = models.CharField(max_length=120, blank=True)
    input_tokens = models.PositiveIntegerField(default=0)
    output_tokens = models.PositiveIntegerField(default=0)
    total_tokens = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
