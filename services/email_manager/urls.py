from django.urls import path
from .views import EmailManagerView

app_name="email_manager"
urlpatterns=[ path("",EmailManagerView.as_view(),name="inbox"), ]
