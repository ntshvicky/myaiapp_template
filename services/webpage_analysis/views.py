from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from .models import AnalysisSession, AnalysisMessage
from .services import WebpageAnalysisService
from services.access import FeatureAccessMixin
from services.ai_router import record_token_usage

class AnalysisView(FeatureAccessMixin, View):
    feature_key = "webpage_analysis"
    template_name = "services/webpage_analysis/analysis.html"

    def get(self, request):
        session, _ = AnalysisSession.objects.get_or_create(user=request.user)
        chat_messages = session.messages.order_by("timestamp")
        return render(request, self.template_name, {"session": session, "chat_messages": chat_messages})

    def post(self, request):
        session_id = request.POST.get("session_id")
        action = request.POST.get("action")
        try:
            session = AnalysisSession.objects.get(id=session_id, user=request.user)
        except AnalysisSession.DoesNotExist:
            return JsonResponse({"error": "Invalid session."}, status=400)

        if action == "clear_history":
            session.messages.all().delete()
            return JsonResponse({"cleared": True})

        user_input = request.POST.get("message","").strip()
        if not user_input:
            return JsonResponse({"error":"No message."}, status=400)

        AnalysisMessage.objects.create(session=session, sender="user", content=user_input)
        bot = WebpageAnalysisService()
        try:
            reply = bot.send_message(session, user_input)
        except Exception as exc:
            reply = f"Unable to analyze webpage: {exc}"
        record_token_usage(request.user, "webpage_analysis", session.id, user_input, reply)
        AnalysisMessage.objects.create(session=session, sender="bot", content=reply)
        return JsonResponse({"bot_response": reply})
