from django.contrib import admin
from ai_agent.models import ChatSession, ChatMessage, VoiceCall, CallTranscript, CallAction


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('role', 'content', 'function_name', 'created_at')


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'updated_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ChatMessageInline]
    date_hierarchy = 'created_at'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'role', 'content_preview', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('content', 'session__user__username')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    def content_preview(self, obj):
        return obj.content[:100] if obj.content else ""
    content_preview.short_description = 'Content Preview'


class CallTranscriptInline(admin.TabularInline):
    model = CallTranscript
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('speaker', 'text', 'timestamp', 'created_at')
    ordering = ('timestamp',)


class CallActionInline(admin.TabularInline):
    model = CallAction
    extra = 0
    readonly_fields = ('created_at', 'completed_at')
    fields = ('action_type', 'status', 'parameters', 'result', 'created_at')


@admin.register(VoiceCall)
class VoiceCallAdmin(admin.ModelAdmin):
    list_display = ('id', 'pharmacy', 'user', 'status', 'duration', 'created_at', 'ended_at')
    list_filter = ('status', 'created_at')
    search_fields = ('pharmacy__name', 'user__username', 'session_id', 'summary')
    readonly_fields = ('created_at', 'updated_at', 'session_id')
    date_hierarchy = 'created_at'
    inlines = [CallTranscriptInline, CallActionInline]
    
    fieldsets = (
        ('Call Information', {
            'fields': ('pharmacy', 'user', 'session_id', 'status')
        }),
        ('Timing', {
            'fields': ('duration', 'created_at', 'updated_at', 'ended_at')
        }),
        ('Content', {
            'fields': ('audio_file', 'summary', 'metadata')
        }),
    )


@admin.register(CallTranscript)
class CallTranscriptAdmin(admin.ModelAdmin):
    list_display = ('id', 'call', 'speaker', 'text_preview', 'timestamp', 'created_at')
    list_filter = ('speaker', 'created_at')
    search_fields = ('text', 'call__session_id')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    def text_preview(self, obj):
        return obj.text[:100] if obj.text else ""
    text_preview.short_description = 'Text Preview'


@admin.register(CallAction)
class CallActionAdmin(admin.ModelAdmin):
    list_display = ('id', 'call', 'action_type', 'status', 'created_at', 'completed_at')
    list_filter = ('action_type', 'status', 'created_at')
    search_fields = ('call__session_id', 'parameters', 'result')
    readonly_fields = ('created_at', 'completed_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Action Information', {
            'fields': ('call', 'action_type', 'status')
        }),
        ('Details', {
            'fields': ('parameters', 'result', 'error_message')
        }),
        ('Timing', {
            'fields': ('created_at', 'completed_at')
        }),
    )
