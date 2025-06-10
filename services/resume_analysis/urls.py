from django.urls import path
from .views import ResumeAnalysisView

app_name="resume_analysis"
urlpatterns=[ path("",ResumeAnalysisView.as_view(),name="analysis"), ]
