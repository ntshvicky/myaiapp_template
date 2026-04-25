# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import AIProviderCredential, UserProfile

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    subscription_plan = forms.ChoiceField(choices=UserProfile.PLAN_CHOICES, initial=UserProfile.PLAN_FREE)

    class Meta:
        model = UserProfile
        fields = ("username", "email", "subscription_plan", "password1", "password2")


class ProfileSettingsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("username", "email", "preferred_ai_provider", "preferred_model")


class ProviderCredentialForm(forms.Form):
    gemini_api_key = forms.CharField(required=False, widget=forms.PasswordInput(render_value=False))
    gemini_model = forms.CharField(required=False, initial="gemini-2.5-flash")
    openai_api_key = forms.CharField(required=False, widget=forms.PasswordInput(render_value=False))
    openai_model = forms.CharField(required=False, initial="gpt-4o-mini")
    anthropic_api_key = forms.CharField(required=False, widget=forms.PasswordInput(render_value=False))
    anthropic_model = forms.CharField(required=False, initial="claude-3-5-haiku-latest")

    PROVIDER_FIELDS = {
        UserProfile.PROVIDER_GEMINI: ("gemini_api_key", "gemini_model"),
        UserProfile.PROVIDER_OPENAI: ("openai_api_key", "openai_model"),
        UserProfile.PROVIDER_ANTHROPIC: ("anthropic_api_key", "anthropic_model"),
    }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user:
            credentials = {item.provider: item for item in user.ai_credentials.all()}
            for provider, (_, model_field) in self.PROVIDER_FIELDS.items():
                credential = credentials.get(provider)
                if credential and credential.default_model:
                    self.fields[model_field].initial = credential.default_model

    def save(self):
        for provider, (key_field, model_field) in self.PROVIDER_FIELDS.items():
            key = self.cleaned_data.get(key_field, "").strip()
            model = self.cleaned_data.get(model_field, "").strip()
            credential, _ = AIProviderCredential.objects.get_or_create(
                user=self.user,
                provider=provider,
            )
            if key:
                credential.api_key = key
            if model:
                credential.default_model = model
            credential.enabled = True
            credential.save()
