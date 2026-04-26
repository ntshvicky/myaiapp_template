from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.contrib import messages

from .models import EmailAccount
from .services import IMAPClient, SMTPClient
from services.access import FeatureAccessMixin
from services.gemini import GeminiClient


class EmailManagerView(FeatureAccessMixin, View):
    feature_key = "email_manager"
    template_name = "services/email_manager/inbox.html"

    def get(self, request):
        accounts = EmailAccount.objects.filter(user=request.user)
        account_id = request.GET.get("account_id")
        folder = request.GET.get("folder", "INBOX")
        account = None
        folders = []
        if account_id:
            account = accounts.filter(id=account_id).first()
        elif accounts.exists():
            account = accounts.first()
            account_id = account.id
        if account:
            folders = IMAPClient(account).list_folders()
        return render(request, self.template_name, {
            "accounts": accounts,
            "account": account,
            "folders": folders,
            "folder": folder,
            "account_id": account_id or "",
        })

    def post(self, request):
        action = request.POST.get("action")

        # --- Add email account ---
        if action == "add_account":
            account = EmailAccount(user=request.user)
            account.email = request.POST.get("email", "").strip()
            account.display_name = request.POST.get("display_name", "").strip()
            account.username = request.POST.get("username", "").strip()
            account.password = request.POST.get("password", "").strip()
            account.imap_host = request.POST.get("imap_host", "imap.gmail.com").strip()
            account.imap_port = int(request.POST.get("imap_port") or 993)
            account.imap_use_ssl = request.POST.get("imap_use_ssl") == "1"
            account.smtp_host = request.POST.get("smtp_host", "smtp.gmail.com").strip()
            account.smtp_port = int(request.POST.get("smtp_port") or 587)
            account.smtp_use_tls = request.POST.get("smtp_use_tls") == "1"
            ok, err = IMAPClient(account).test_connection()
            if ok:
                account.save()
                messages.success(request, f"Account {account.email} added successfully.")
            else:
                messages.error(request, f"Connection failed: {err}")
            return redirect(request.path)

        if action == "delete_account":
            aid = request.POST.get("account_id")
            EmailAccount.objects.filter(id=aid, user=request.user).delete()
            messages.success(request, "Account removed.")
            return redirect(request.path)

        # --- AJAX actions ---
        account_id = request.POST.get("account_id")
        account = get_object_or_404(EmailAccount, id=account_id, user=request.user)

        if action == "list_emails":
            folder = request.POST.get("folder", "INBOX")
            emails = IMAPClient(account).fetch_emails(folder=folder, limit=40)
            return JsonResponse({"emails": emails})

        if action == "read_email":
            uid = request.POST.get("uid")
            folder = request.POST.get("folder", "INBOX")
            data = IMAPClient(account).fetch_email_body(uid, folder)
            return JsonResponse(data if data else {"error": "Not found"})

        if action == "search":
            query = request.POST.get("query", "")
            folder = request.POST.get("folder", "INBOX")
            results = IMAPClient(account).search_emails(query, folder)
            return JsonResponse({"emails": results})

        if action == "send":
            to = request.POST.get("to", "")
            subject = request.POST.get("subject", "")
            body = request.POST.get("body", "")
            ok, err = SMTPClient(account).send(to, subject, body)
            if ok:
                return JsonResponse({"sent": True})
            return JsonResponse({"sent": False, "error": err})

        if action == "ai_assist":
            content = request.POST.get("content", "")
            task = request.POST.get("task", "summarize")
            prompts = {
                "summarize": f"Summarize this email concisely in 2-3 bullet points:\n\n{content}",
                "reply":     f"Write a professional, friendly reply to this email:\n\n{content}",
                "fix":       f"Fix grammar, spelling and tone of this email draft (return ONLY the corrected text):\n\n{content}",
                "formal":    f"Rewrite this email in a more formal/professional tone:\n\n{content}",
                "shorter":   f"Make this email shorter and more concise:\n\n{content}",
            }
            prompt = prompts.get(task, prompts["summarize"])
            try:
                ai = GeminiClient()
                result = ai.generate_text([ai.text_content("user", prompt)])
                return JsonResponse({"result": result})
            except Exception as exc:
                return JsonResponse({"error": str(exc)}, status=500)

        return JsonResponse({"error": "Unknown action"}, status=400)
