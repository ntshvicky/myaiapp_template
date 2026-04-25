from django.contrib import admin
from django.urls import path, include
from myaiapp.views import DashboardView, PricingView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('pricing/', PricingView.as_view(), name='pricing'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('chatbot/', include('services.chatbot.urls')),
    path('webpage-analysis/', include('services.webpage_analysis.urls')),
    path('image-generator/', include('services.image_generator.urls')),
    path('video-generator/', include('services.video_generator.urls')),
    path('music-generator/', include('services.music_generator.urls')),
    path('document-chat/', include('services.document_chat.urls')),
    path('content-writer/', include('services.content_writer.urls')),
    path('email-manager/', include('services.email_manager.urls')),
    path('resume-analysis/', include('services.resume_analysis.urls')),
    path('image-chat/', include('services.image_chat.urls')),
    path('compare-images/', include('services.compare_images.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
