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
        session = ImageSession.objects.filter(user=request.user).last()
        if not session:
            session = ImageSession.objects.create(user=request.user)
        messages = session.messages.order_by("timestamp")
        return render(request, self.template_name, {
            "session": session,
            "chat_messages": messages,
        })

    def post(self, request):
        session_id = request.POST.get("session_id")
        action = request.POST.get("action", "generate")

        session = ImageSession.objects.filter(id=session_id, user=request.user).first()
        if not session:
            return JsonResponse({"error": "Invalid session."}, status=400)

        svc = ImageGeneratorService()

        # ── Generate new image ─────────────────────────────────────────
        if action == "generate":
            user_text = request.POST.get("prompt", "").strip()
            if not user_text:
                return JsonResponse({"error": "No prompt provided."}, status=400)

            effective_prompt = user_text
            try:
                img_file = svc.generate(effective_prompt)
            except Exception as exc:
                return JsonResponse({"error": str(exc)}, status=500)

            msg = ImageMessage(
                session=session,
                user_text=user_text,
                prompt=effective_prompt,
            )
            msg.image.save(img_file.name, img_file, save=False)
            msg.save()

            return JsonResponse({
                "id": msg.id,
                "image_url": msg.get_image_url(),
                "prompt": effective_prompt,
                "user_text": user_text,
            })

        # ── Modify existing image ──────────────────────────────────────
        if action == "modify":
            modification = request.POST.get("modification", "").strip()
            base_msg_id = request.POST.get("base_message_id", "").strip()

            if not modification:
                return JsonResponse({"error": "No modification instruction."}, status=400)

            # Get the base image's prompt
            base_msg = ImageMessage.objects.filter(
                id=base_msg_id, session=session
            ).first()
            if not base_msg:
                # Fallback: use the last message in the session
                base_msg = session.messages.order_by("timestamp").last()
            if not base_msg:
                return JsonResponse({"error": "No image to modify yet."}, status=400)

            # Merge prompts using AI
            merged_prompt = svc.merge_prompt(base_msg.prompt, modification)

            try:
                img_file = svc.generate(merged_prompt)
            except Exception as exc:
                return JsonResponse({"error": str(exc)}, status=500)

            msg = ImageMessage(
                session=session,
                user_text=modification,
                prompt=merged_prompt,
            )
            msg.image.save(img_file.name, img_file, save=False)
            msg.save()

            return JsonResponse({
                "id": msg.id,
                "image_url": msg.get_image_url(),
                "prompt": merged_prompt,
                "user_text": modification,
            })

        # ── Delete a message ───────────────────────────────────────────
        if action == "delete_message":
            msg_id = request.POST.get("message_id")
            ImageMessage.objects.filter(id=msg_id, session=session).delete()
            return JsonResponse({"ok": True})

        # ── Clear all messages ─────────────────────────────────────────
        if action == "clear_all":
            session.messages.all().delete()
            return JsonResponse({"ok": True})

        return JsonResponse({"error": "Unknown action."}, status=400)
