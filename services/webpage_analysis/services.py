import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from services.gemini import GeminiClient


class WebpageAnalysisService:
    def send_message(self, session, user_input):
        if "::" not in user_input:
            return "Use this format: https://example.com::Your question about the page."

        raw_url, question = [part.strip() for part in user_input.split("::", 1)]
        parsed = urlparse(raw_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            return "Please enter a valid http or https URL before the :: separator."

        response = requests.get(raw_url, timeout=12, headers={"User-Agent": "MyAIAppBot/1.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))[:20000]

        ai = GeminiClient()
        prompt = (
            f"Website URL: {raw_url}\n\nExtracted page text:\n{text}\n\n"
            f"Question: {question}\n\nAnswer from the page. If the page does not contain enough information, say so."
        )
        return ai.generate_text([ai.text_content("user", prompt)])
