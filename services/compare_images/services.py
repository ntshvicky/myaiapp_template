import base64
from PIL import Image, ImageChops, ImageStat

from services.gemini import GeminiClient


class ImageCompareService:
    def _pixel_similarity(self, image1, image2):
        """Compute pixel-level RMS similarity (0→1) between two images."""
        with Image.open(image1) as img_a, Image.open(image2) as img_b:
            img_a = img_a.convert("RGB").resize((512, 512))
            img_b = img_b.convert("RGB").resize((512, 512))
            diff = ImageChops.difference(img_a, img_b)
            stat = ImageStat.Stat(diff)
            rms = sum(v ** 2 for v in stat.rms) ** 0.5
        return max(0.0, min(1.0, 1.0 - (rms / 441.67295593)))

    def _image_to_bytes(self, image_field):
        """Read image field into raw bytes and detect MIME type."""
        image_field.seek(0)
        raw = image_field.read()
        image_field.seek(0)
        # Detect MIME from first bytes
        if raw[:4] == b'\x89PNG':
            mime = "image/png"
        elif raw[:2] in (b'\xff\xd8',):
            mime = "image/jpeg"
        elif raw[:4] == b'RIFF' and raw[8:12] == b'WEBP':
            mime = "image/webp"
        elif raw[:6] in (b'GIF87a', b'GIF89a'):
            mime = "image/gif"
        else:
            mime = "image/jpeg"
        return raw, mime

    def _ai_description(self, image1, image2):
        """Ask Gemini Vision to analyse and describe differences between the two images."""
        ai = GeminiClient()
        raw1, mime1 = self._image_to_bytes(image1)
        raw2, mime2 = self._image_to_bytes(image2)

        prompt = (
            "You are a visual analysis expert. I will give you two images labeled Image A and Image B.\n\n"
            "Please provide a thorough comparison covering:\n"
            "1. **Overall content** — What does each image show? Are they the same subject?\n"
            "2. **Key differences** — List every notable difference in content, objects, people, text, colors, layout, background, style, quality, etc.\n"
            "3. **Similarities** — What do they have in common?\n"
            "4. **Summary** — A one-sentence verdict on how similar or different they are.\n\n"
            "Be specific and visual — describe what you actually see, not just file properties."
        )

        contents = [
            ai.types.Content(
                role="user",
                parts=[
                    ai.types.Part.from_text(text="**Image A:**"),
                    ai.types.Part.from_bytes(data=raw1, mime_type=mime1),
                    ai.types.Part.from_text(text="**Image B:**"),
                    ai.types.Part.from_bytes(data=raw2, mime_type=mime2),
                    ai.types.Part.from_text(text=prompt),
                ],
            )
        ]
        return ai.generate_text(contents)

    def compare(self, image1, image2):
        """Run both pixel similarity and AI content analysis."""
        similarity = self._pixel_similarity(image1, image2)
        try:
            description = self._ai_description(image1, image2)
        except Exception as exc:
            description = f"AI analysis unavailable: {exc}"
        return {
            "score": round(similarity, 4),
            "diff_url": "",
            "ai_description": description,
        }
