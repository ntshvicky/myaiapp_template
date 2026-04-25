from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.contrib import messages
from .models import Document, DocChatSession, DocChatMessage
from .services import DocumentChatService
from .forms import DocumentForm
from services.access import FeatureAccessMixin
from services.ai_router import record_token_usage

class DocumentChatView(FeatureAccessMixin, View):
    feature_key = "document_chat"
    template_name="services/document_chat/chat.html"

    def get(self, request):
        docs = Document.objects.filter(user=request.user)
        
        doc_id = request.GET.get('doc_id')
        pages = request.GET.get('pages', 'all')
        session = None
        
        if doc_id:
            try:
                doc = Document.objects.get(id=doc_id, user=request.user)
                session, _ = DocChatSession.objects.get_or_create(document=doc, pages=pages)
            except Document.DoesNotExist:
                pass

        return render(request, self.template_name, {
            "docs": docs,
            "session": session,
            "selected_pages": pages,
            "doc_id": int(doc_id) if doc_id and doc_id.isdigit() else None
        })

    def post(self, request):
        action = request.POST.get('action')
        
        if action == 'upload':
            if Document.objects.filter(user=request.user).count() >= 3:
                messages.error(request, "You can only upload a maximum of 3 documents on your current plan.")
                return redirect(request.path)
                
            form = DocumentForm(request.POST, request.FILES)
            if form.is_valid():
                doc = form.save(commit=False)
                doc.user = request.user
                doc.save()
                messages.success(request, "Document uploaded successfully.")
                
        elif action == 'delete':
            doc_id = request.POST.get('doc_id')
            Document.objects.filter(id=doc_id, user=request.user).delete()
            messages.success(request, "Document deleted.")
            
        return redirect(request.path)


class DocumentChatAjaxView(FeatureAccessMixin, View):
    feature_key = "document_chat"
    def post(self, request):
        sess_id = request.POST.get("session_id")
        action  = request.POST.get("action")
        question = request.POST.get("message", "").strip()
        
        try:
            session = DocChatSession.objects.get(id=sess_id, document__user=request.user)
        except DocChatSession.DoesNotExist:
            return JsonResponse({"error": "Invalid session."}, status=400)
            
        if action == "clear_history":
            session.messages.all().delete()
            return JsonResponse({"cleared": True})
            
        if not question:
            return JsonResponse({"error": "Message is required."}, status=400)
            
        DocChatMessage.objects.create(session=session, sender="user", content=question)
        
        reply = DocumentChatService().send_message(session, question)
        usage = record_token_usage(request.user, "document_chat", session.id, question, reply)
        
        DocChatMessage.objects.create(session=session, sender="bot", content=reply)
        return JsonResponse({"bot_response": reply, "total_tokens": usage.total_tokens})
