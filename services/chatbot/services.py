from .models import ChatSession
from services.ai_router import AIProviderError, AIProviderRouter

class ChatbotService:
    """
    Wraps Google Gemini Chat capabilities, loading the session history
    from DB and appending the new user message.
    """

    def __init__(self):
        self.system_prompt = (
            "You are a smart and helpful assistant. Format substantial answers in clean Markdown "
            "with headings, bullets, tables, and code blocks when helpful. "
            "For scientific, workflow, architecture, comparison, lifecycle, or process explanations, "
            "include a Mermaid diagram when it adds clarity, using a fenced ```mermaid code block. "
            "When the user asks for research, statistics, trends, or data comparisons, include a "
            "Chart.js chart using a fenced ```chart-json code block containing valid JSON with keys: "
            "type (bar/line/pie/doughnut), data.labels (array), data.datasets (array with label and data). "
            "Example: ```chart-json\n{\"type\":\"bar\",\"data\":{\"labels\":[\"A\",\"B\"],\"datasets\":[{\"label\":\"Score\",\"data\":[10,20]}]}}\n``` "
            "Only include charts when data visualization genuinely helps. Keep diagrams and charts valid."
        )

    def send_message(self, session: ChatSession, user_input: str):
        messages = []
        for item in session.messages.order_by("timestamp"):
            messages.append({
                "role": "user" if item.sender == "user" else "assistant",
                "content": item.content,
            })
        try:
            return AIProviderRouter(
                user=session.user,
                provider=session.provider,
                model_name=session.model_name,
            ).chat(
                messages=messages,
                system_prompt=self.system_prompt,
                module="chatbot",
                conversation_id=session.id,
            )
        except AIProviderError as exc:
            raise exc
        except Exception as exc:
            raise AIProviderError(f"Error communicating with AI: {exc}")
