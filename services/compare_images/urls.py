from django.urls import path
from .views import CompareView

app_name="compare_images"
urlpatterns=[ path("",CompareView.as_view(),name="compare"), ]
