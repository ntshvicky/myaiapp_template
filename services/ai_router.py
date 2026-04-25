import os

import requests
from django.conf import settings

from accounts.models import AIProviderCredential, TokenUsage, UserProfile
from services.gemini import GeminiClient


DEFAULT_MODELS = {
    UserProfile.PROVIDER_GEMINI: "gemini-2.5-flash",
    UserProfile.PROVIDER_OPENAI: "gpt-4o-mini",
    UserProfile.PROVIDER_ANTHROPIC: "claude-3-5-haiku-latest",
}

STALE_GEMINI_MODELS = {
    "gemini-1.5-flash",
    "gemini-1.5-pro",
}


def estimate_tokens(text):
    return max(1, len(text or "") // 4)


def record_token_usage(user, module, conversation_id, input_text, output_text, provider="", model_name=""):
    input_tokens = estimate_tokens(input_text)
    output_tokens = estimate_tokens(output_text)
    return TokenUsage.objects.create(
        user=user,
        module=module,
        conversation_id=str(conversation_id or ""),
        provider=provider or user.preferred_ai_provider,
        model_name=model_name or user.preferred_model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=input_tokens + output_tokens,
    )


class AIProviderError(RuntimeError):
    pass


class AIResponse:
    def __init__(self, text, input_tokens=0, output_tokens=0, provider="", model_name=""):
        self.text = text
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.total_tokens = input_tokens + output_tokens
        self.provider = provider
        self.model_name = model_name


class AIProviderRouter:
    def __init__(self, user, provider=None, model_name=None):
        self.user = user
        self.provider = provider or user.preferred_ai_provider
        self.model_name = self._normalize_model(model_name or self._default_model())
        self.api_key = self._api_key()

    def _credential(self):
        return AIProviderCredential.objects.filter(
            user=self.user,
            provider=self.provider,
            enabled=True,
        ).first()

    def _default_model(self):
        credential = self._credential()
        if credential and credential.default_model:
            return credential.default_model
        return self.user.preferred_model or DEFAULT_MODELS.get(self.user.preferred_ai_provider, DEFAULT_MODELS[UserProfile.PROVIDER_GEMINI])

    def _normalize_model(self, model_name):
        if self.provider == UserProfile.PROVIDER_GEMINI and model_name in STALE_GEMINI_MODELS:
            return DEFAULT_MODELS[UserProfile.PROVIDER_GEMINI]
        return model_name

    def _api_key(self):
        credential = self._credential()
        if credential and credential.api_key:
            return credential.api_key
        env_names = {
            UserProfile.PROVIDER_GEMINI: "GEMINI_API_KEY",
            UserProfile.PROVIDER_OPENAI: "OPENAI_API_KEY",
            UserProfile.PROVIDER_ANTHROPIC: "ANTHROPIC_API_KEY",
        }
        return os.environ.get(env_names.get(self.provider, ""), "")

    def chat(self, messages, system_prompt="", module="chatbot", conversation_id=""):
        if self.provider == UserProfile.PROVIDER_GEMINI:
            response = self._chat_gemini(messages, system_prompt)
        elif self.provider == UserProfile.PROVIDER_OPENAI:
            response = self._chat_openai(messages, system_prompt)
        elif self.provider == UserProfile.PROVIDER_ANTHROPIC:
            response = self._chat_anthropic(messages, system_prompt)
        else:
            raise AIProviderError("Unsupported AI provider.")

        TokenUsage.objects.create(
            user=self.user,
            module=module,
            conversation_id=str(conversation_id),
            provider=response.provider,
            model_name=response.model_name,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            total_tokens=response.total_tokens,
        )
        return response

    def _chat_gemini(self, messages, system_prompt):
        if not self.api_key and not settings.GEMINI_API_KEY:
            raise AIProviderError("Gemini API key is not configured in Settings or .env.")
        old_key = settings.GEMINI_API_KEY
        settings.GEMINI_API_KEY = self.api_key or settings.GEMINI_API_KEY
        try:
            ai = GeminiClient(model_id=self.model_name)
            contents = []
            for item in messages:
                role = "model" if item["role"] == "assistant" else "user"
                contents.append(ai.text_content(role, item["content"]))
            try:
                text = ai.generate_text(contents, system_instruction=system_prompt)
            except Exception as exc:
                if self.model_name != DEFAULT_MODELS[UserProfile.PROVIDER_GEMINI] and "NOT_FOUND" in str(exc):
                    self.model_name = DEFAULT_MODELS[UserProfile.PROVIDER_GEMINI]
                    ai = GeminiClient(model_id=self.model_name)
                    text = ai.generate_text(contents, system_instruction=system_prompt)
                else:
                    raise
        finally:
            settings.GEMINI_API_KEY = old_key
        return AIResponse(
            text=text,
            input_tokens=estimate_tokens(" ".join(item["content"] for item in messages)),
            output_tokens=estimate_tokens(text),
            provider=self.provider,
            model_name=self.model_name,
        )

    def _chat_openai(self, messages, system_prompt):
        if not self.api_key:
            raise AIProviderError("OpenAI API key is not configured in Settings.")
        payload_messages = []
        if system_prompt:
            payload_messages.append({"role": "system", "content": system_prompt})
        payload_messages.extend(messages)
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={"model": self.model_name, "messages": payload_messages},
            timeout=45,
        )
        if response.status_code >= 400:
            raise AIProviderError(response.json().get("error", {}).get("message", response.text))
        data = response.json()
        text = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        return AIResponse(
            text=text,
            input_tokens=usage.get("prompt_tokens", estimate_tokens(str(payload_messages))),
            output_tokens=usage.get("completion_tokens", estimate_tokens(text)),
            provider=self.provider,
            model_name=self.model_name,
        )

    def _chat_anthropic(self, messages, system_prompt):
        if not self.api_key:
            raise AIProviderError("Anthropic API key is not configured in Settings.")
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model_name,
                "max_tokens": 2048,
                "system": system_prompt,
                "messages": messages,
            },
            timeout=45,
        )
        if response.status_code >= 400:
            raise AIProviderError(response.json().get("error", {}).get("message", response.text))
        data = response.json()
        text = "".join(part.get("text", "") for part in data.get("content", []) if part.get("type") == "text")
        usage = data.get("usage", {})
        return AIResponse(
            text=text,
            input_tokens=usage.get("input_tokens", estimate_tokens(str(messages))),
            output_tokens=usage.get("output_tokens", estimate_tokens(text)),
            provider=self.provider,
            model_name=self.model_name,
        )
