from django.urls import path
from .views import DocumentChatView, DocumentChatAjaxView

app_name="document_chat"
urlpatterns=[
  path("",DocumentChatView.as_view(),name="chat"),
  path("ajax/",DocumentChatAjaxView.as_view(),name="ajax"),
]
