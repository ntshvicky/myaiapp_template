from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import VideoSession, VideoMessage
from .services import VideoGeneratorService

class VideoGeneratorView(LoginRequiredMixin, View):
    template_name = "services/video_generator/generator.html"

    def get(self, request):
        session, _ = VideoSession.objects.get_or_create(user=request.user)
        vids = session.messages.order_by("-timestamp")
        return render(request, self.template_name, {"session": session, "videos": vids})

    def post(self, request):
        session_id = request.POST.get("session_id")
        prompt = request.POST.get("prompt","").strip()
        session = VideoSession.objects.filter(id=session_id, user=request.user).first()
        if not session or not prompt:
            return JsonResponse({"error":"Bad request"}, status=400)
        url = VideoGeneratorService().generate(prompt)
        VideoMessage.objects.create(session=session,prompt=prompt,video_url=url)
        return JsonResponse({"video_url":url})
