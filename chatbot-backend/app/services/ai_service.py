"""AI service for generating responses."""
import httpx
from typing import List, Dict, Optional
from app.config import settings
from app.utils.logger import logger


class AIService:
    """Service for interacting with AI models."""
    
    def __init__(self):
        self.groq_key = settings.GROQ_API_KEY
    
    async def generate_response(
        self, 
        message: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate AI response based on user message."""
        if conversation_history is None:
            conversation_history = []
        
        logger.info(f"Generating AI response using Groq")
        return await self._groq_call(message, conversation_history)
    
    async def _groq_call(self, message: str, history: List[Dict]) -> str:
        """Groq API implementation using Chat Completions (FREE tier with Llama 3.3 70B)."""
        try:
            # Validate API key
            if not self.groq_key:
                logger.error("GROQ_API_KEY is not set!")
                return "Sorry, the AI service is not properly configured. Please check the API key."
            
            # Prepare messages for OpenAI API
            messages = []
            
            # Add system prompt first
            messages.append({
                "role": "system",
                "content": "You are a helpful AI assistant on WhatsApp. Be friendly, concise, and helpful."
            })
            
            # Add conversation history
            for msg in history[-10:]:  # Keep last 10 messages for context
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
            
            # Add current message
            messages.append({
                "role": "user",
                "content": message
            })
            
            logger.info(f"Calling Groq API with {len(messages)} messages, model: llama-3.3-70b-versatile")
            
            # Make API call to Groq (OpenAI-compatible API, FREE tier)
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.groq_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.3-70b-versatile",  # Groq's latest Llama model (FREE!)
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 500
                    }
                )
                
                response.raise_for_status()
                result = response.json()
                
                ai_response = result["choices"][0]["message"]["content"]
                logger.info(f"Groq API response received successfully: {ai_response[:100]}...")
                
                return ai_response
                
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_detail = e.response.json()
                logger.error(f"Groq API HTTP error: {e.response.status_code} - {error_detail}")
            except:
                error_detail = e.response.text
                logger.error(f"Groq API HTTP error: {e.response.status_code} - {error_detail}")
            
            if e.response.status_code == 401:
                return "Sorry, the AI service authentication failed. Please check the API key configuration."
            elif e.response.status_code == 429:
                return "Sorry, the AI service is rate-limited. Please try again in a moment."
            else:
                return "Sorry, I'm having trouble connecting to my AI service. Please try again later."
                
        except httpx.TimeoutException:
            logger.error("Groq API timeout after 30 seconds")
            return "Sorry, my response took too long. Please try again."
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}", exc_info=True)
            return f"Sorry, I encountered an error: {str(e)[:100]}"
    



ai_service = AIService()