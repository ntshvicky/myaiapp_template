from django.contrib import admin
from .models import AIProviderCredential, TokenUsage, UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'subscription_plan', 'subscription_active', 'is_active')
    list_filter  = ('is_active', 'subscription_plan', 'subscription_active')
    search_fields = ('username','email')


@admin.register(AIProviderCredential)
class AIProviderCredentialAdmin(admin.ModelAdmin):
    list_display = ("user", "provider", "default_model", "enabled", "updated_at")
    list_filter = ("provider", "enabled")
    search_fields = ("user__username", "user__email")


@admin.register(TokenUsage)
class TokenUsageAdmin(admin.ModelAdmin):
    list_display = ("user", "module", "conversation_id", "provider", "model_name", "total_tokens", "created_at")
    list_filter = ("module", "provider", "model_name")
    search_fields = ("user__username", "conversation_id")
