import openai
from django.conf import settings
from .models import ChatSession, ChatMessage

class ChatbotService:
    """
    Wraps OpenAI ChatCompletion, loading the session history
    from DB and appending the new user message.
    """

    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = "gpt-4o-mini"
        self.system_prompt = "You are a smart and helpful assistant."

    def send_message(self, session: ChatSession, user_input: str) -> str:
        # Build messages from history
        msgs = [
            {"role": "system", "content": self.system_prompt}
        ]
        for m in session.messages.order_by("timestamp"):
            role = "user" if m.sender == "user" else "assistant"
            msgs.append({"role": role, "content": m.content})
        # Append the new user message
        msgs.append({"role": "user", "content": user_input})

        # Call OpenAI
        resp = openai.ChatCompletion.create(
            model=self.model,
            messages=msgs
        )
        return resp.choices[0].message.content
