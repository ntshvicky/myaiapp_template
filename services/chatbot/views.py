from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import ChatSession, ChatMessage
from .services import ChatbotService

class ChatbotView(LoginRequiredMixin, View):
    template_name = "services/chatbot/chatbot.html"

    def get(self, request):
        # one open session per user
        session, _ = ChatSession.objects.get_or_create(user=request.user)
        messages = session.messages.order_by("timestamp")
        return render(request, self.template_name, {
            "session": session,
            "messages": messages
        })

    def post(self, request):
        session_id = request.POST.get("session_id")
        action = request.POST.get("action")
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            return JsonResponse({"error": "Invalid session."}, status=400)

        if action == "clear_history":
            session.messages.all().delete()
            return JsonResponse({"cleared": True})

        user_input = request.POST.get("message", "").strip()
        if not user_input:
            return JsonResponse({"error": "No message provided."}, status=400)

        # Save user message
        ChatMessage.objects.create(
            session=session, sender="user", content=user_input
        )

        # Generate bot reply
        bot_service = ChatbotService()
        bot_reply = bot_service.send_message(session, user_input)

        # Save bot reply
        ChatMessage.objects.create(
            session=session, sender="bot", content=bot_reply
        )

        return JsonResponse({"bot_response": bot_reply})
