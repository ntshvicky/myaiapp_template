from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from .models import ImageUpload, ImageChatSession, ImageChatMessage
from .services import ImageChatService
from .forms import ImageUploadForm
from services.access import FeatureAccessMixin
from services.ai_router import record_token_usage

class ImageChatView(FeatureAccessMixin, View):
    feature_key = "image_chat"
    template_name="services/image_chat/chat.html"

    def get(self,request):
        uploads=ImageUpload.objects.filter(user=request.user)
        selected_image_id = request.GET.get("image_id", "")
        return render(request,self.template_name,{"uploads":uploads, "form": ImageUploadForm(), "selected_image_id": selected_image_id})

    def post(self,request):
        form=ImageUploadForm(request.POST,request.FILES)
        if form.is_valid():
            img=form.save(commit=False); img.user=request.user; img.save()
        return redirect(request.path)

class ImageChatAjax(FeatureAccessMixin, View):
    feature_key = "image_chat"
    def post(self,request):
        image_id=request.POST.get("image_id")
        action=request.POST.get("action")
        prompt=request.POST.get("message","").strip()
        upload = ImageUpload.objects.filter(id=image_id, user=request.user).first()
        if not upload:
            return JsonResponse({"error":"Invalid image."}, status=400)
        session, _ = ImageChatSession.objects.get_or_create(image=upload)
        if action=="clear_history":
            session.messages.all().delete()
            return JsonResponse({"cleared":True})
        if not prompt:
            return JsonResponse({"error":"Message is required."}, status=400)
        ImageChatMessage.objects.create(session=session,sender="user",content=prompt)
        reply=ImageChatService().send_message(session,prompt)
        usage = record_token_usage(request.user, "image_chat", session.id, prompt, reply)
        ImageChatMessage.objects.create(session=session,sender="bot",content=reply)
        return JsonResponse({"bot_response":reply, "total_tokens": usage.total_tokens})
