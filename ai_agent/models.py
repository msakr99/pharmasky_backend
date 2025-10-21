from django.db import models
from django.conf import settings


class ChatSession(models.Model):
    """
    Chat session model to store conversation history for each user
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_sessions',
        related_query_name='chat_sessions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
        ]

    def __str__(self):
        return f"Session {self.id} - {self.user.username}"


class ChatMessage(models.Model):
    """
    Individual chat messages within a session
    """
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages',
        related_query_name='messages'
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optional: store function calls and responses
    function_name = models.CharField(max_length=100, blank=True, null=True)
    function_arguments = models.JSONField(blank=True, null=True)
    function_response = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
        ]

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"


class VoiceCall(models.Model):
    """
    Voice call records for AI sales agent
    Stores metadata about calls with pharmacies
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    pharmacy = models.ForeignKey(
        'accounts.Pharmacy',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='voice_calls',
        related_query_name='voice_calls'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='voice_calls',
        related_query_name='voice_calls'
    )
    session_id = models.CharField(max_length=255, unique=True, db_index=True)
    audio_file = models.FileField(upload_to='voice_calls/', blank=True, null=True)
    duration = models.IntegerField(default=0, help_text="Call duration in seconds")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    # Summary and metadata
    summary = models.TextField(blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['pharmacy', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        pharmacy_name = self.pharmacy.name if self.pharmacy else "Unknown"
        return f"Call #{self.id} - {pharmacy_name} ({self.status})"


class CallTranscript(models.Model):
    """
    Transcript of voice call conversations
    Stores text from both user and AI assistant
    """
    SPEAKER_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    call = models.ForeignKey(
        VoiceCall,
        on_delete=models.CASCADE,
        related_name='transcripts',
        related_query_name='transcripts'
    )
    speaker = models.CharField(max_length=20, choices=SPEAKER_CHOICES)
    text = models.TextField()
    timestamp = models.FloatField(help_text="Timestamp in seconds from call start")
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Audio segment reference (optional)
    audio_segment = models.FileField(upload_to='call_segments/', blank=True, null=True)
    
    class Meta:
        ordering = ['call', 'timestamp']
        indexes = [
            models.Index(fields=['call', 'timestamp']),
            models.Index(fields=['call', 'speaker']),
        ]
    
    def __str__(self):
        return f"{self.speaker} @ {self.timestamp}s: {self.text[:50]}"


class CallAction(models.Model):
    """
    Actions executed during a call via MCP
    Tracks orders, searches, and other operations
    """
    ACTION_TYPE_CHOICES = [
        ('create_order', 'Create Order'),
        ('check_stock', 'Check Stock'),
        ('search_drug', 'Search Drug'),
        ('get_price', 'Get Price'),
        ('recommend_alternative', 'Recommend Alternative'),
        ('get_pharmacy_info', 'Get Pharmacy Info'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]
    
    call = models.ForeignKey(
        VoiceCall,
        on_delete=models.CASCADE,
        related_name='actions',
        related_query_name='actions'
    )
    action_type = models.CharField(max_length=50, choices=ACTION_TYPE_CHOICES)
    parameters = models.JSONField(default=dict)
    result = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['call', 'created_at']
        indexes = [
            models.Index(fields=['call', 'created_at']),
            models.Index(fields=['action_type', 'status']),
        ]
    
    def __str__(self):
        return f"{self.action_type} - {self.status}"
