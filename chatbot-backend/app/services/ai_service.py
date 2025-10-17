"""
AI conversation service using Groq's Llama 3.3 70B model.

Provides intelligent chat responses with conversation history support.
"""
import httpx
from typing import List, Dict, Optional
from app.config import settings
from app.utils.logger import logger

# Constants
DEFAULT_MODEL = "llama-3.3-70b-versatile"
API_TIMEOUT = 30.0
MAX_HISTORY_LENGTH = 10
MAX_RESPONSE_TOKENS = 500


class AIService:
    """AI chatbot service powered by Groq."""
    
    def __init__(self):
        """Initialize AI service with Groq API credentials."""
        self.groq_key = settings.GROQ_API_KEY
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        
        if not self.groq_key:
            logger.error("Groq API key not configured")
            raise ValueError("GROQ_API_KEY is required")
        
        logger.info("AI service initialized with Groq")
    
    async def generate_response(
        self, 
        message: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate AI response with conversation context.
        
        Args:
            message: User's input message
            conversation_history: Previous conversation messages
            
        Returns:
            str: AI-generated response text
        """
        if conversation_history is None:
            conversation_history = []
        
        return await self._call_groq_api(message, conversation_history)
    
    async def _call_groq_api(self, message: str, history: List[Dict]) -> str:
        """
        Call Groq Chat Completions API.
        
        Args:
            message: Current user message
            history: Previous conversation messages
            
        Returns:
            str: Generated response or error message
        """
        try:
            # Build conversation messages
            messages = self._build_messages(message, history)
            
            # Prepare API request
            async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.groq_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": DEFAULT_MODEL,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": MAX_RESPONSE_TOKENS
                    }
                )
                
                # Handle API errors
                if response.status_code != 200:
                    return self._handle_api_error(response)
                
                # Extract AI response
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                return ai_response
                
        except httpx.TimeoutException:
            logger.error(f"Groq API timeout after {API_TIMEOUT}s")
            return "Sorry, my response took too long. Please try again."
        except Exception as e:
            logger.error(f"AI service error: {str(e)}")
            return "Sorry, I encountered an error. Please try again later."
    
    def _build_messages(self, current_message: str, history: List[Dict]) -> List[Dict]:
        """
        Build conversation messages for API.
        
        Args:
            current_message: Latest user message
            history: Previous conversation history
            
        Returns:
            list: Formatted messages for API
        """
        messages = []
        
        # System prompt - Medical Consultant
        messages.append({
            "role": "system",
            "content": """You are Dr. Health Assistant, a trusted medical consultant specializing in health guidance via WhatsApp.

YOUR EXPERTISE:
- Diagnose symptoms and suggest appropriate treatments
- Provide preventive care and lifestyle recommendations
- Offer DO's and DON'Ts for common health conditions
- Guide on when to seek emergency medical attention

COMMUNICATION STYLE:
- Professional yet warm and empathetic
- Use clear, simple language without medical jargon
- Keep responses concise (2-3 short paragraphs maximum)
- Ask targeted follow-up questions when needed (severity, duration, related symptoms)
- Be confident and authoritative in your guidance

CRITICAL RULES:
1. For emergencies (chest pain, breathing difficulty, severe bleeding, stroke signs): Immediately advise emergency room visit
2. Only mention consulting a doctor when truly necessary (serious conditions, persistent symptoms, or diagnosis needed)
3. Provide actionable advice - medications, home remedies, lifestyle changes
4. Never sound robotic or repetitive with disclaimers
5. Be natural, conversational, and trustworthy like a real doctor

Respond as a knowledgeable physician would - confident, helpful, and focused on solving the patient's concern."""
        })
        
        # Add recent conversation history
        for msg in history[-MAX_HISTORY_LENGTH:]:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": current_message
        })
        
        return messages
    
    def _handle_api_error(self, response: httpx.Response) -> str:
        """
        Handle Groq API error responses.
        
        Args:
            response: HTTP response from API
            
        Returns:
            str: User-friendly error message
        """
        status_code = response.status_code
        
        try:
            error_data = response.json()
            logger.error(f"Groq API error: {status_code}")
        except:
            logger.error(f"Groq API error: {status_code}")
        
        # Return user-friendly error messages
        if status_code == 401:
            return "Sorry, AI service authentication failed. Please contact support."
        elif status_code == 429:
            return "Sorry, too many requests. Please try again in a moment."
        else:
            return "Sorry, I'm having trouble connecting. Please try again later."


# Global service instance
ai_service = AIService()