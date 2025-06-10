from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from .services import ContentWriterService

class WriterView(LoginRequiredMixin, View):
    template_name="services/content_writer/write.html"

    def get(self,request):
        return render(request,self.template_name)

    def post(self,request):
        prompt=request.POST.get("prompt","").strip()
        if not prompt:
            return JsonResponse({"error":"No prompt."},status=400)
        reply=ContentWriterService().write(prompt)
        return JsonResponse({"content":reply})
