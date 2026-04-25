from django.urls import path
from django.contrib.auth import views as auth_views
from .views import ConversationHistoryView, RegisterView, SettingsView

app_name = 'accounts'

urlpatterns = [
    path('login/',
         auth_views.LoginView.as_view(template_name='accounts/login.html'),
         name='login'),
    path('logout/',
         auth_views.LogoutView.as_view(next_page='accounts:login'),
         name='logout'),
    path('register/',
         RegisterView.as_view(),
         name='register'),
    path('settings/', SettingsView.as_view(), name='settings'),
    path('history/', ConversationHistoryView.as_view(), name='history'),
]
