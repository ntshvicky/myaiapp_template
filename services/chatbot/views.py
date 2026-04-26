from django.db.models import Sum
from django.shortcuts import redirect, render
from django.views import View
from django.http import JsonResponse
from .models import ChatSession, ChatMessage
from .services import ChatbotService
from accounts.models import UserProfile
from services.ai_router import AIProviderError, DEFAULT_MODELS
from services.access import FeatureAccessMixin

class ChatbotView(FeatureAccessMixin, View):
    feature_key = "chatbot"
    template_name = "services/chatbot/chatbot.html"

    def get(self, request):
        if request.GET.get("new") == "1":
            session = self._create_session(request)
            return redirect(f"{request.path}?session_id={session.id}")

        sessions = ChatSession.objects.filter(user=request.user).order_by("-updated_at")
        session_id = request.GET.get("session_id")
        session = sessions.filter(id=session_id).first() if session_id else sessions.first()
        if not session:
            session = self._create_session(request)
        chat_messages = session.messages.order_by("timestamp")
        token_totals = session.messages.aggregate(
            input_tokens=Sum("input_tokens"),
            output_tokens=Sum("output_tokens"),
            total_tokens=Sum("total_tokens"),
        )
        return render(request, self.template_name, {
            "session": session,
            "sessions": sessions,
            "chat_messages": chat_messages,
            "provider_choices": UserProfile.AI_PROVIDER_CHOICES,
            "default_models": DEFAULT_MODELS,
            "token_totals": token_totals,
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

        provider = request.POST.get("provider", session.provider)
        model_name = request.POST.get("model_name", session.model_name).strip()
        if provider in dict(UserProfile.AI_PROVIDER_CHOICES):
            session.provider = provider
        if model_name:
            session.model_name = model_name

        user_input = request.POST.get("message", "").strip()
        if not user_input:
            return JsonResponse({"error": "No message provided."}, status=400)

        # Save user message
        user_message = ChatMessage.objects.create(
            session=session, sender="user", content=user_input
        )

        if session.title == "New chat":
            session.title = user_input[:80]
        session.save(update_fields=["provider", "model_name", "title", "updated_at"])

        bot_service = ChatbotService()
        try:
            ai_response = bot_service.send_message(session, user_input)
            bot_reply = ai_response.text
        except AIProviderError as exc:
            bot_reply = str(exc)
            ai_response = None

        if ai_response:
            user_message.input_tokens = ai_response.input_tokens
            user_message.total_tokens = ai_response.input_tokens
            user_message.save(update_fields=["input_tokens", "total_tokens"])

        ChatMessage.objects.create(
            session=session,
            sender="bot",
            content=bot_reply,
            output_tokens=ai_response.output_tokens if ai_response else 0,
            total_tokens=ai_response.output_tokens if ai_response else 0,
        )

        return JsonResponse({
            "bot_response": bot_reply,
            "input_tokens": ai_response.input_tokens if ai_response else 0,
            "output_tokens": ai_response.output_tokens if ai_response else 0,
            "total_tokens": ai_response.total_tokens if ai_response else 0,
            "provider": session.provider,
            "model_name": session.model_name,
        })

    def _create_session(self, request):
        return ChatSession.objects.create(
            user=request.user,
            provider=request.user.preferred_ai_provider,
            model_name=request.user.preferred_model or DEFAULT_MODELS.get(request.user.preferred_ai_provider, "gemini-2.5-flash"),
        )
