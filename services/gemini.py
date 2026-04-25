from django.conf import settings


class GeminiError(RuntimeError):
    pass


class GeminiClient:
    def __init__(self, model_id=None):
        if not settings.GEMINI_API_KEY:
            raise GeminiError("Gemini API key is not configured. Add GEMINI_API_KEY to .env.")
        try:
            from google import genai
            from google.genai import types
        except Exception as exc:
            raise GeminiError("google-genai is not installed. Run pip install -r requirements.txt.") from exc

        self.types = types
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_id = model_id or settings.GEMINI_MODEL

    def text_content(self, role, text):
        return self.types.Content(role=role, parts=[self.types.Part.from_text(text=text)])

    def generate_text(self, contents, system_instruction=None):
        config = None
        if system_instruction:
            config = self.types.GenerateContentConfig(system_instruction=system_instruction)
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=contents,
            config=config,
        )
        return response.text or ""
