import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from services.gemini import GeminiClient


class WebpageAnalysisService:
    def _fetch_page_text(self, url):
        """Fetch a URL and return cleaned plain text (up to 20 000 chars)."""
        resp = requests.get(url, timeout=12, headers={"User-Agent": "MyAIAppBot/1.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        return re.sub(r"\s+", " ", soup.get_text(" ", strip=True))[:20000]

    def send_message(self, session, user_input, url_override=None):
        """
        Analyze a webpage.

        URL resolution order:
          1. url_override  (sent explicitly by the frontend when user changes URL)
          2. session.current_url  (previously set URL — main use-case)
          3. Legacy inline format: "https://… :: question"
        """
        url = (url_override or "").strip()
        question = user_input.strip()

        # Legacy inline format still supported as a fallback
        if not url and "::" in user_input:
            url, question = [p.strip() for p in user_input.split("::", 1)]

        # Use the session's stored URL if nothing else provided
        if not url:
            url = session.current_url

        if not url:
            return "Please enter a website URL first using the URL bar above the chat."

        # Validate URL
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            return f"'{url}' doesn't look like a valid http/https URL. Please check and try again."

        # Save URL on session so future messages reuse it
        if url != session.current_url:
            session.current_url = url
            session.save(update_fields=["current_url"])

        if not question:
            question = "Summarize this page."

        try:
            page_text = self._fetch_page_text(url)
        except Exception as exc:
            return f"Could not fetch '{url}': {exc}"

        ai = GeminiClient()
        prompt = (
            f"Website URL: {url}\n\nExtracted page content:\n{page_text}\n\n"
            f"User question: {question}\n\n"
            f"Answer based on the page content. If the page doesn't contain enough information, say so."
        )
        return ai.generate_text([ai.text_content("user", prompt)])
