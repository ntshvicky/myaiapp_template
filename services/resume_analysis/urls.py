from django.urls import path
from .views import ResumeAnalysisView, CVChatAjaxView

app_name = "resume_analysis"
urlpatterns = [
    path("", ResumeAnalysisView.as_view(), name="analysis"),
    path("chat/", CVChatAjaxView.as_view(), name="cv_chat"),
]
