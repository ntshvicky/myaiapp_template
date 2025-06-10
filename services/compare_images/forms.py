from django import forms
from .models import ComparisonResult

class CompareForm(forms.Form):
    image1 = forms.ImageField()
    image2 = forms.ImageField()
