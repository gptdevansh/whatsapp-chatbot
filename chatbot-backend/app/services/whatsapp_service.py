"""WhatsApp service using Meta WhatsApp Business API."""
import httpx
from app.config import settings
from app.utils.logger import logger


class WhatsAppService:
    """Service for sending WhatsApp messages via Meta WhatsApp Business API."""
    
    def __init__(self):
        self.phone_number_id = settings.META_PHONE_NUMBER_ID
        self.access_token = settings.META_ACCESS_TOKEN
        self.api_version = settings.META_API_VERSION
        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}"
        
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    async def send_message(self, to_number: str, message: str) -> dict:
        """
        Send WhatsApp message to a user using Meta's Cloud API.
        
        Args:
            to_number: Phone number in international format (e.g., "919876543210")
            message: Text message to send
            
        Returns:
            dict: Response from Meta API with message_id and status
        """
        try:
            # Clean phone number (remove whatsapp: prefix if present)
            to_number = to_number.replace("whatsapp:", "").replace("+", "").strip()
            
            logger.info(f"Sending WhatsApp message to {to_number}")
            
            # Prepare the request payload
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
            
            # Send the request to Meta's API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"Message sent successfully. Message ID: {result.get('messages', [{}])[0].get('id', 'unknown')}")
                
                return {
                    "message_id": result.get("messages", [{}])[0].get("id"),
                    "status": "sent",
                    "to": to_number,
                    "body": message
                }
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
            logger.error(f"Failed to send WhatsApp message: {error_msg}")
            raise Exception(f"Failed to send message: {error_msg}")
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message: {str(e)}")
            raise Exception(f"Failed to send message: {str(e)}")
    
    async def mark_as_read(self, message_id: str) -> bool:
        """
        Mark a message as read.
        
        Args:
            message_id: The WhatsApp message ID to mark as read
            
        Returns:
            bool: True if successful
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
                logger.info(f"Marked message {message_id} as read")
                return True
                
        except Exception as e:
            logger.error(f"Failed to mark message as read: {str(e)}")
            return False


whatsapp_service = WhatsAppService()