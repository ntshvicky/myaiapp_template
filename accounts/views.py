# accounts/views.py

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView
from .models import AIProviderCredential, TokenUsage, UserProfile
from .forms import ProfileSettingsForm, ProviderCredentialForm, RegistrationForm

class RegisterView(CreateView):
    model = UserProfile
    form_class = RegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def get_initial(self):
        initial = super().get_initial()
        selected_plan = self.request.session.get("selected_plan")
        if selected_plan:
            initial["subscription_plan"] = selected_plan
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.session.pop("selected_plan", None)
        return response


class SettingsView(LoginRequiredMixin, View):
    template_name = "accounts/settings.html"

    def get(self, request):
        return render(request, self.template_name, self._context(request))

    def post(self, request):
        profile_form = ProfileSettingsForm(request.POST, instance=request.user)
        credential_form = ProviderCredentialForm(request.POST, user=request.user)
        if profile_form.is_valid() and credential_form.is_valid():
            profile_form.save()
            credential_form.save()
            messages.success(request, "Settings updated.")
            return redirect("accounts:settings")
        return render(request, self.template_name, self._context(request, profile_form, credential_form))

    def _context(self, request, profile_form=None, credential_form=None):
        credentials = {item.provider: item for item in request.user.ai_credentials.all()}
        credential_status = [
            {
                "provider": provider,
                "label": label,
                "masked_key": credentials.get(provider).masked_key() if credentials.get(provider) else "Not configured",
                "model": credentials.get(provider).default_model if credentials.get(provider) else "",
            }
            for provider, label in UserProfile.AI_PROVIDER_CHOICES
        ]
        token_totals = request.user.token_usage.aggregate(
            input_tokens=Sum("input_tokens"),
            output_tokens=Sum("output_tokens"),
            total_tokens=Sum("total_tokens"),
        )
        by_conversation = (
            request.user.token_usage.values("module", "conversation_id", "provider", "model_name")
            .annotate(total_tokens=Sum("total_tokens"), input_tokens=Sum("input_tokens"), output_tokens=Sum("output_tokens"))
            .order_by("module", "-total_tokens")[:50]
        )
        return {
            "profile_form": profile_form or ProfileSettingsForm(instance=request.user),
            "credential_form": credential_form or ProviderCredentialForm(user=request.user),
            "credential_status": credential_status,
            "token_totals": token_totals,
            "by_conversation": by_conversation,
        }


class ConversationHistoryView(LoginRequiredMixin, View):
    template_name = "accounts/history.html"

    def get(self, request):
        from services.chatbot.models import ChatSession
        from services.document_chat.models import DocChatSession
        from services.image_chat.models import ImageChatSession
        from services.webpage_analysis.models import AnalysisSession

        conversations = []
        for session in ChatSession.objects.filter(user=request.user).order_by("-updated_at"):
            conversations.append({
                "module": "AI Chatbot",
                "title": session.title,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "message_count": session.messages.count(),
                "tokens": session.messages.aggregate(total=Sum("total_tokens"))["total"] or 0,
                "url": f"/chatbot/?session_id={session.id}",
            })
        for session in AnalysisSession.objects.filter(user=request.user).order_by("-created_at"):
            conversations.append({
                "module": "Website Analyzer",
                "title": "Website analysis chat",
                "created_at": session.created_at,
                "updated_at": session.created_at,
                "message_count": session.messages.count(),
                "tokens": 0,
                "url": "/webpage-analysis/",
            })
        for session in DocChatSession.objects.filter(document__user=request.user).order_by("-created_at"):
            conversations.append({
                "module": "Document Chat",
                "title": session.document.file.name,
                "created_at": session.created_at,
                "updated_at": session.created_at,
                "message_count": session.messages.count(),
                "tokens": 0,
                "url": f"/document-chat/?doc_id={session.document_id}&pages={session.pages}",
            })
        for session in ImageChatSession.objects.filter(image__user=request.user).order_by("-created_at"):
            conversations.append({
                "module": "Image Chat",
                "title": session.image.image.name,
                "created_at": session.created_at,
                "updated_at": session.created_at,
                "message_count": session.messages.count(),
                "tokens": 0,
                "url": f"/image-chat/?image_id={session.image_id}",
            })
        conversations.sort(key=lambda item: item["updated_at"], reverse=True)
        return render(request, self.template_name, {"conversations": conversations})
