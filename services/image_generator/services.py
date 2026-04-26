import uuid

from django.conf import settings
from django.core.files.base import ContentFile


# Gemini image generation models to try in order
_IMAGE_MODELS = [
    "gemini-2.5-flash-image",
    "gemini-3.1-flash-image-preview",
    "gemini-3-pro-image-preview",
]


class ImageGeneratorService:
    """Generate images using Google Gemini image models."""

    def _client(self):
        from google import genai
        return genai.Client(api_key=settings.GEMINI_API_KEY)

    def generate(self, prompt: str):
        """
        Generate an image from a prompt.
        Returns (ContentFile, None) on success, or raises RuntimeError on failure.
        """
        from google.genai import types as genai_types

        client = self._client()
        last_error = None

        for model in _IMAGE_MODELS:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=genai_types.GenerateContentConfig(
                        response_modalities=["IMAGE"],
                    ),
                )
                # Find the image part
                for part in response.candidates[0].content.parts:
                    if part.inline_data and part.inline_data.data:
                        image_bytes = part.inline_data.data
                        # Determine extension from mime type
                        mime = part.inline_data.mime_type or "image/jpeg"
                        ext = "png" if "png" in mime else "jpg"
                        filename = f"{uuid.uuid4().hex}.{ext}"
                        return ContentFile(image_bytes, name=filename)
            except Exception as exc:
                last_error = exc
                continue

        raise RuntimeError(
            f"Image generation failed. {last_error}"
            if last_error else "No image models available."
        )

    def merge_prompt(self, original_prompt: str, modification: str) -> str:
        """
        Use Gemini text to merge an original image prompt with a modification instruction
        so the new image keeps the same scene/style but includes the changes.
        """
        try:
            from services.gemini import GeminiClient
            ai = GeminiClient()
            system = (
                "You are an expert image-prompt engineer. "
                "Given an original image-generation prompt and a user's modification request, "
                "produce a single new, complete, detailed prompt that preserves the original "
                "scene, style, and composition while incorporating the change. "
                "Return ONLY the new prompt — no explanation, no quotes, no preamble."
            )
            user_msg = (
                f"ORIGINAL PROMPT:\n{original_prompt}\n\n"
                f"USER MODIFICATION:\n{modification}\n\n"
                "NEW PROMPT:"
            )
            result = ai.generate_text(
                [ai.text_content("user", user_msg)],
                system_instruction=system,
            )
            merged = result.strip()
            return merged if merged else f"{original_prompt}, {modification}"
        except Exception:
            return f"{original_prompt}, {modification}"
