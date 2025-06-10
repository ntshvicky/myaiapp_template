# accounts/views.py

from django.urls import reverse_lazy
from django.views.generic import CreateView
from .models import UserProfile
from .forms import RegistrationForm

class RegisterView(CreateView):
    model = UserProfile
    form_class = RegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
