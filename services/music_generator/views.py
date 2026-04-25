from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from .models import MusicSession, MusicMessage
from .services import MusicGeneratorService
from services.access import FeatureAccessMixin

class MusicGeneratorView(FeatureAccessMixin, View):
    feature_key = "music_generator"
    template_name="services/music_generator/generator.html"

    def get(self, request):
        session,_=MusicSession.objects.get_or_create(user=request.user)
        msgs=session.messages.order_by("-timestamp")
        return render(request,self.template_name,{"session":session,"musics":msgs})

    def post(self, request):
        sid=request.POST.get("session_id")
        prompt=request.POST.get("prompt","").strip()
        session=MusicSession.objects.filter(id=sid,user=request.user).first()
        if not session or not prompt:
            return JsonResponse({"error":"Bad request"},status=400)
        url=MusicGeneratorService().generate(prompt)
        MusicMessage.objects.create(session=session,prompt=prompt,music_url=url)
        return JsonResponse({"music_url":url})
