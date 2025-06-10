from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Document, DocChatSession, DocChatMessage
from .services import DocumentChatService
from .forms import DocumentForm

class DocumentChatView(LoginRequiredMixin, View):
    template_name="services/document_chat/chat.html"

    def get(self, request):
        docs=Document.objects.filter(user=request.user)
        return render(request,self.template_name,{"docs":docs})

    def post(self, request):
        # handle file upload
        form=DocumentForm(request.POST,request.FILES)
        if form.is_valid():
            doc=form.save(commit=False)
            doc.user=request.user
            doc.save()
        return redirect(request.path)


class DocumentChatAjaxView(LoginRequiredMixin, View):
    def post(self, request):
        sess_id = request.POST.get("session_id")
        action  = request.POST.get("action")
        question=request.POST.get("message","").strip()
        try:
            session=DocChatSession.objects.get(id=sess_id, document__user=request.user)
        except:
            return JsonResponse({"error":"Invalid session."},status=400)
        if action=="clear_history":
            session.messages.all().delete()
            return JsonResponse({"cleared":True})
        DocChatMessage.objects.create(session=session,sender="user",content=question)
        reply=DocumentChatService().send_message(session,question)
        DocChatMessage.objects.create(session=session,sender="bot",content=reply)
        return JsonResponse({"bot_response":reply})
