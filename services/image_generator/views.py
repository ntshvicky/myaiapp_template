from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from .models import ImageSession, ImageMessage
from .services import ImageGeneratorService
from services.access import FeatureAccessMixin

class ImageGeneratorView(FeatureAccessMixin, View):
    feature_key = "image_generator"
    template_name = "services/image_generator/generator.html"

    def get(self, request):
        session, _ = ImageSession.objects.get_or_create(user=request.user)
        images = session.messages.order_by("-timestamp")
        return render(request, self.template_name, {"session": session, "images": images})

    def post(self, request):
        session_id = request.POST.get("session_id")
        prompt = request.POST.get("prompt","").strip()
        try:
            session = ImageSession.objects.get(id=session_id, user=request.user)
        except ImageSession.DoesNotExist:
            return JsonResponse({"error":"Invalid session."}, status=400)
        if not prompt:
            return JsonResponse({"error":"No prompt."}, status=400)

        service = ImageGeneratorService()
        url = service.generate(prompt)
        ImageMessage.objects.create(session=session, prompt=prompt, image_url=url)
        return JsonResponse({"image_url": url})
