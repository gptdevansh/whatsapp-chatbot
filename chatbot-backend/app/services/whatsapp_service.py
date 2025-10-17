"""
WhatsApp Business API integration service.

Handles sending messages and managing WhatsApp conversations
using Meta's Cloud API.
"""
import httpx
from typing import Dict, Optional
from app.config import settings
from app.utils.logger import logger


class WhatsAppService:
    """WhatsApp Business API client for sending messages."""
    
    def __init__(self):
        """Initialize WhatsApp service with Meta API credentials."""
        self.phone_number_id = settings.META_PHONE_NUMBER_ID
        self.access_token = settings.META_ACCESS_TOKEN
        self.api_version = settings.META_API_VERSION
        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}"
        
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        # Validate credentials on initialization
        if not self.phone_number_id or not self.access_token:
            logger.error("WhatsApp credentials not configured")
            raise ValueError("META_PHONE_NUMBER_ID and META_ACCESS_TOKEN are required")
        
        logger.info("WhatsApp service initialized successfully")
    
    async def send_message(self, to_number: str, message: str) -> Dict[str, str]:
        """
        Send a text message via WhatsApp.
        
        Args:
            to_number: Recipient phone number (international format without +)
            message: Text message to send
            
        Returns:
            dict: Response with message_id and status
            
        Raises:
            Exception: If message sending fails
        """
        try:
            # Clean and normalize phone number
            to_number = to_number.replace("whatsapp:", "").replace("+", "").strip()
            
            # Prepare API request payload
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to_number,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": message
                }
            }
            
            # Send request to Meta WhatsApp API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                
                # Check for HTTP errors
                if response.status_code != 200:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                    logger.error(f"WhatsApp API error ({response.status_code}): {error_msg}")
                    raise Exception(f"Failed to send message: {error_msg}")
                
                result = response.json()
                message_id = result.get('messages', [{}])[0].get('id', 'unknown')
                
                logger.info(f"Message sent to {to_number[-4:]}****  (ID: {message_id})")
                
                return {
                    "message_id": message_id,
                    "status": "sent",
                    "to": to_number
                }
            
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json() if e.response.text else str(e)
            logger.error(f"HTTP error sending WhatsApp message: {error_detail}")
            raise Exception(f"WhatsApp API error: {error_detail}")
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message: {str(e)}")
            raise
    
    async def mark_as_read(self, message_id: str) -> bool:
        """
        Mark a received message as read.
        
        Args:
            message_id: WhatsApp message ID to mark as read
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            payload = {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    json=payload,
                    headers=self.headers,
                    timeout=10.0
                )
                
                response.raise_for_status()
                logger.debug(f"Marked message {message_id} as read")
                return True
                
        except Exception as e:
            logger.warning(f"Could not mark message as read: {str(e)}")
            return False


# Global service instance
whatsapp_service = WhatsAppService()