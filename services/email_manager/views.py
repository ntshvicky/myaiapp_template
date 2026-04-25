from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from .models import EmailAccount
from .services import EmailService
from services.access import FeatureAccessMixin

class EmailManagerView(FeatureAccessMixin,View):
    feature_key = "email_manager"
    template_name="services/email_manager/inbox.html"

    def get(self,request):
        accounts=EmailAccount.objects.filter(user=request.user)
        return render(request,self.template_name,{"accounts":accounts})

    def post(self,request):
        action=request.POST.get("action")
        account_id=request.POST.get("account_id")
        if action=="search":
            q=request.POST.get("query","")
            results=EmailService().search(account_id,q)
            return JsonResponse({"results":results})
        if action=="send":
            to=request.POST.get("to")
            subj=request.POST.get("subject")
            body=request.POST.get("body")
            ok=EmailService().send(account_id,to,subj,body)
            return JsonResponse({"sent":ok})
        return JsonResponse({"error":"Unknown action"},status=400)
