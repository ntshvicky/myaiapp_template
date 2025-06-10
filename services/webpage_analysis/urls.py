from django.urls import path
from .views import AnalysisView

app_name = "webpage_analysis"
urlpatterns = [
    path("", AnalysisView.as_view(), name="analysis"),
]
