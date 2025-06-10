from django.urls import path
from .views import MusicGeneratorView

app_name="music_generator"
urlpatterns=[ path("",MusicGeneratorView.as_view(),name="generator"), ]
