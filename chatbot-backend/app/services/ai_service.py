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
            # Prepare messages for OpenAI API
            messages = []
            
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
            
            # Add system prompt if no history
            if not history:
                messages.insert(0, {
                    "role": "system",
                    "content": "You are a helpful AI assistant on WhatsApp. Be friendly, concise, and helpful."
                })
            
            logger.info(f"Calling Groq API with {len(messages)} messages")
            
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
                logger.info(f"Groq API response received: {ai_response[:100]}...")
                
                return ai_response
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Groq API HTTP error: {e.response.status_code} - {e.response.text}")
            return "Sorry, I'm having trouble connecting to my AI service. Please try again later."
        except httpx.TimeoutException:
            logger.error("Groq API timeout")
            return "Sorry, my response took too long. Please try again."
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            return "Sorry, I encountered an error. Please try again later."
    



ai_service = AIService()