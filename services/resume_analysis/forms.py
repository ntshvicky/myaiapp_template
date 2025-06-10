from django import forms
from .models import JobDescription, CV

class JDForm(forms.ModelForm):
    class Meta:
        model = JobDescription
        fields = ["file"]

class CVForm(forms.ModelForm):
    class Meta:
        model = CV
        fields = ["file"]
