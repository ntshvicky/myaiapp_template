from services.gemini import GeminiClient


class ContentWriterService:
    def write(self, prompt:str) -> str:
        ai = GeminiClient()
        system = (
            "You are an expert content writer. Produce clear, polished copy. "
            "Ask for missing details only when they are essential."
        )
        return ai.generate_text([ai.text_content("user", prompt)], system_instruction=system)
