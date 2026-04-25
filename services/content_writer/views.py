from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from .services import ContentWriterService
from services.access import FeatureAccessMixin
from services.ai_router import record_token_usage

class WriterView(FeatureAccessMixin, View):
    feature_key = "content_writer"
    template_name="services/content_writer/write.html"

    def get(self,request):
        return render(request,self.template_name)

    def post(self,request):
        prompt=request.POST.get("prompt","").strip()
        if not prompt:
            return JsonResponse({"error":"No prompt."},status=400)
        try:
            reply=ContentWriterService().write(prompt)
        except Exception as exc:
            reply=f"Unable to generate content: {exc}"
        record_token_usage(request.user, "content_writer", "", prompt, reply)
        return JsonResponse({"content":reply})
