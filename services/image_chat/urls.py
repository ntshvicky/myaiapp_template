from django.urls import path
from .views import ImageChatView, ImageChatAjax

app_name="image_chat"
urlpatterns=[
  path("",ImageChatView.as_view(),name="chat"),
  path("ajax/",ImageChatAjax.as_view(),name="ajax"),
]
