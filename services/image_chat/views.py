from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import ImageUpload, ImageChatSession, ImageChatMessage
from .services import ImageChatService
from .forms import ImageUploadForm

class ImageChatView(LoginRequiredMixin, View):
    template_name="services/image_chat/chat.html"

    def get(self,request):
        uploads=ImageUpload.objects.filter(user=request.user)
        return render(request,self.template_name,{"uploads":uploads})

    def post(self,request):
        form=ImageUploadForm(request.POST,request.FILES)
        if form.is_valid():
            img=form.save(commit=False); img.user=request.user; img.save()
        return redirect(request.path)

class ImageChatAjax(LoginRequiredMixin, View):
    def post(self,request):
        sid=request.POST.get("session_id")
        action=request.POST.get("action")
        prompt=request.POST.get("message","").strip()
        session=ImageChatSession.objects.filter(id=sid).first()
        if action=="clear_history":
            session.messages.all().delete()
            return JsonResponse({"cleared":True})
        ImageChatMessage.objects.create(session=session,sender="user",content=prompt)
        reply=ImageChatService().send_message(session,prompt)
        ImageChatMessage.objects.create(session=session,sender="bot",content=reply)
        return JsonResponse({"bot_response":reply})
