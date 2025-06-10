from django.urls import path
from .views import WriterView

app_name="content_writer"
urlpatterns=[ path("",WriterView.as_view(),name="write"), ]
