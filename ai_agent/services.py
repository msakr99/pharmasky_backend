"""
OpenAI API integration services
"""
from openai import OpenAI
from django.conf import settings
from ai_agent.prompts import get_system_prompt
from ai_agent.tools import AGENT_TOOLS, execute_tool
from ai_agent.models import ChatSession, ChatMessage
import json
import base64
from io import BytesIO


class OpenAIService:
    """
    Service class to interact with OpenAI API via DigitalOcean
    """
    
    def __init__(self):
        """Initialize OpenAI client with DigitalOcean endpoint"""
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.DIGITALOCEAN_AGENT_URL
        )
        self.model = "gpt-4o-mini"
        self.tts_model = "tts-1"
        self.whisper_model = "whisper-1"
    
    def get_or_create_session(self, user):
        """Get or create active chat session for user"""
        session = ChatSession.objects.filter(
            user=user,
            is_active=True
        ).first()
        
        if not session:
            session = ChatSession.objects.create(user=user)
        
        return session
    
    def get_conversation_history(self, session, limit=10):
        """Get recent conversation history for context"""
        messages = []
        
        # Add system prompt
        messages.append({
            "role": "system",
            "content": get_system_prompt()
        })
        
        # Add recent chat history
        recent_messages = session.messages.all().order_by('-created_at')[:limit]
        for msg in reversed(recent_messages):
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        return messages
    
    def chat(self, user, message_text, session=None):
        """
        Send a chat message and get response from GPT
        Handles function calling automatically
        """
        if not session:
            session = self.get_or_create_session(user)
        
        # Save user message
        ChatMessage.objects.create(
            session=session,
            role='user',
            content=message_text
        )
        
        # Get conversation history
        messages = self.get_conversation_history(session)
        
        # Add current message
        messages.append({
            "role": "user",
            "content": message_text
        })
        
        # Call OpenAI API with tools
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=AGENT_TOOLS,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        
        # Handle function calls if any
        if response_message.tool_calls:
            # Add assistant message with tool calls
            messages.append(response_message)
            
            # Execute each tool call
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                # Execute the function
                function_response = execute_tool(
                    function_name,
                    function_args,
                    user
                )
                
                # Save function call details
                ChatMessage.objects.create(
                    session=session,
                    role='assistant',
                    content=f"[Function Call: {function_name}]",
                    function_name=function_name,
                    function_arguments=function_args,
                    function_response=json.loads(function_response)
                )
                
                # Add function response to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": function_response
                })
            
            # Get final response after function execution
            second_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            
            final_message = second_response.choices[0].message.content
        else:
            final_message = response_message.content
        
        # Save assistant response
        ChatMessage.objects.create(
            session=session,
            role='assistant',
            content=final_message
        )
        
        return {
            "message": final_message,
            "session_id": session.id
        }
    
    def transcribe_audio(self, audio_file):
        """
        Transcribe audio to text using Whisper
        audio_file: File object or BytesIO
        """
        try:
            transcription = self.client.audio.transcriptions.create(
                model=self.whisper_model,
                file=audio_file,
                response_format="text"
            )
            return {
                "success": True,
                "text": transcription
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def text_to_speech(self, text, voice="alloy"):
        """
        Convert text to speech using OpenAI TTS
        Returns audio as base64 encoded string
        """
        try:
            response = self.client.audio.speech.create(
                model=self.tts_model,
                voice=voice,
                input=text
            )
            
            # Convert to base64
            audio_bytes = response.content
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            return {
                "success": True,
                "audio_base64": audio_base64
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_voice_message(self, user, audio_file):
        """
        Process voice message: transcribe -> chat -> TTS
        """
        # Step 1: Transcribe audio to text
        transcription = self.transcribe_audio(audio_file)
        
        if not transcription.get("success"):
            return {
                "success": False,
                "error": "فشل تحويل الصوت إلى نص"
            }
        
        text = transcription.get("text")
        
        # Step 2: Get chat response
        chat_response = self.chat(user, text)
        
        # Step 3: Convert response to speech
        tts_response = self.text_to_speech(chat_response["message"])
        
        if not tts_response.get("success"):
            return {
                "success": False,
                "error": "فشل تحويل النص إلى صوت"
            }
        
        return {
            "success": True,
            "text": chat_response["message"],
            "audio_base64": tts_response["audio_base64"],
            "session_id": chat_response["session_id"],
            "transcription": text
        }


# Global service instance
openai_service = OpenAIService()

