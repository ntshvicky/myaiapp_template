from django.urls import path
from .views import VideoGeneratorView

app_name="video_generator"
urlpatterns=[ path("",VideoGeneratorView.as_view(),name="generator"), ]
