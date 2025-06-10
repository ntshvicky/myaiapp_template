from django.contrib.auth.models import AbstractUser
from django.db import models

class UserProfile(AbstractUser):
    can_use_chatbot = models.BooleanField(default=True)
    can_use_webpage_analysis = models.BooleanField(default=True)
    can_use_image_generator = models.BooleanField(default=True)
    can_use_video_generator = models.BooleanField(default=True)
    can_use_music_generator = models.BooleanField(default=True)
    can_use_document_chat = models.BooleanField(default=True)
    can_use_content_writer = models.BooleanField(default=True)
    can_use_email_manager = models.BooleanField(default=True)
    can_use_resume_analysis = models.BooleanField(default=True)
    can_use_image_chat = models.BooleanField(default=True)
    can_use_compare_images = models.BooleanField(default=True)
