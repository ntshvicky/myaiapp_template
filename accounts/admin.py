from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_active',
                    'can_use_chatbot', 'can_use_webpage_analysis',
                    # …all your permission flags…
                   )
    list_filter  = ('is_active',)
    search_fields = ('username','email')
