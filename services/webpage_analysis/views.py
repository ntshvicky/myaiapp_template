from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import AnalysisSession, AnalysisMessage
from .services import WebpageAnalysisService

class AnalysisView(LoginRequiredMixin, View):
    template_name = "services/webpage_analysis/analysis.html"

    def get(self, request):
        session, _ = AnalysisSession.objects.get_or_create(user=request.user)
        messages = session.messages.order_by("timestamp")
        return render(request, self.template_name, {"session": session, "messages": messages})

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
        reply = bot.send_message(session, user_input)
        AnalysisMessage.objects.create(session=session, sender="bot", content=reply)
        return JsonResponse({"bot_response": reply})
