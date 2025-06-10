from django.contrib import admin
from .models import ChatSession, ChatMessage

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id','user','created_at')
    search_fields = ('user__username',)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session','sender','timestamp','content_short')
    list_filter = ('sender',)
    search_fields = ('content',)

    def content_short(self, obj):
        return obj.content[:50]
    content_short.short_description = 'Content…'
