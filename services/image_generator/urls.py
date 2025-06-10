from django.urls import path
from .views import ImageGeneratorView

app_name = "image_generator"
urlpatterns = [
    path("", ImageGeneratorView.as_view(), name="generator"),
]
