"""
WhatsApp webhook router for Meta WhatsApp Business API.

Handles webhook verification and incoming message processing with MongoDB.
"""
from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from typing import Optional, Dict, Any

from app.models import User, Message, MessageRole
from app.services.ai_service import ai_service
from app.services.whatsapp_service import whatsapp_service
from app.utils.logger import logger
from app.config import settings

router = APIRouter(prefix="/webhook", tags=["WhatsApp Webhook"])


@router.get("/whatsapp")
async def whatsapp_webhook_verify(request: Request):
    """
    Verify webhook subscription with Meta.
    
    Meta sends a GET request with verification parameters when setting up
    the webhook. This endpoint validates the verify token and returns the
    challenge to complete the verification process.
    """
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    
    logger.info(f"Webhook verification attempt: mode={mode}")
    
    # Verify the token matches configuration
    if mode == "subscribe" and token == settings.META_VERIFY_TOKEN:
        logger.info("Webhook verified successfully")
        return PlainTextResponse(content=str(challenge))
    
    logger.warning("Webhook verification failed - invalid token")
    return PlainTextResponse(content="Invalid token", status_code=403)


@router.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    Process incoming WhatsApp messages from Meta.
    
    Workflow:
    1. Parse Meta webhook payload
    2. Extract message details (sender, text, message_id)
    3. Get or create user in database
    4. Save incoming message
    5. Retrieve conversation history for context
    6. Generate AI response using conversation context
    7. Save AI response to database
    8. Send response back to user via WhatsApp
    9. Mark original message as read
    
    Returns 200 status to Meta regardless of errors to prevent retries.
    """
    try:
        body = await request.json()
        logger.info("Received WhatsApp webhook event")
        
        # Validate webhook object type
        if body.get("object") != "whatsapp_business_account":
            logger.debug(f"Ignoring non-WhatsApp webhook: {body.get('object')}")
            return {"status": "ok"}
        
        # Process all message entries
        await process_webhook_entries(body)
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        # Return 200 to prevent Meta from retrying
        return {"status": "error", "message": str(e)}


async def process_webhook_entries(body: Dict[str, Any]):
    """
    Process all entries in a webhook payload.
    
    Args:
        body: Webhook payload from Meta
    """
    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            
            # Check for messages in this change
            messages = value.get("messages", [])
            if not messages:
                continue
            
            # Get contact info for name lookup
            contacts = value.get("contacts", [])
            
            # Process each message
            for message_data in messages:
                await process_message(message_data, contacts)


async def process_message(message_data: Dict[str, Any], contacts: list):
    """
    Process a single incoming message.
    
    Args:
        message_data: Message data from webhook
        contacts: Contact information from webhook
    """
    # Extract message details
    message_id = message_data.get("id")
    sender_phone = message_data.get("from")
    message_type = message_data.get("type")
    
    # Only process text messages
    if message_type != "text":
        logger.debug(f"Ignoring {message_type} message")
        return
    
    message_text = message_data.get("text", {}).get("body", "")
    if not message_text:
        logger.warning("Received empty message text")
        return
    
    # Extract sender name from contacts
    sender_name = None
    if contacts:
        profile = contacts[0].get("profile", {})
        sender_name = profile.get("name")
    
    logger.info(f"Processing message from {sender_phone[-4:]}****")
    
    # Get or create user
    user = await get_or_create_user(sender_phone, sender_name)
    
    # Save incoming message
    user_message = Message(
        user_id=str(user.id),
        role=MessageRole.USER,
        content=message_text,
        meta_message_id=message_id
    )
    await user_message.insert()
    
    # Mark as read
    await whatsapp_service.mark_as_read(message_id)
    
    # Get conversation context
    conversation_history = await get_conversation_history(str(user.id), limit=10)
    
    # Generate AI response
    ai_response = await ai_service.generate_response(message_text, conversation_history)
    
    # Save AI response
    assistant_message = Message(
        user_id=str(user.id),
        role=MessageRole.ASSISTANT,
        content=ai_response
    )
    await assistant_message.insert()
    
    # Send response to user
    try:
        await whatsapp_service.send_message(sender_phone, ai_response)
        logger.info("Response sent successfully")
    except Exception as e:
        logger.error(f"Failed to send WhatsApp response: {str(e)}")
        # Don't raise - message is already saved


async def get_or_create_user(phone_number: str, name: Optional[str] = None) -> User:
    """
    Retrieve existing user or create new one.
    
    Args:
        phone_number: User's phone number
        name: Optional user display name
        
    Returns:
        User: User database object
    """
    # Check if user exists
    user = await User.find_one(User.phone_number == phone_number)
    
    if user:
        # Update name if provided and changed
        if name and user.name != name:
            user.name = name
            await user.save()
        return user
    
    # Create new user
    user = User(phone_number=phone_number, name=name)
    await user.insert()
    
    logger.info(f"New user created: {phone_number[-4:]}**** (ID: {user.id})")
    return user


async def get_conversation_history(user_id: str, limit: int = 10) -> list[dict]:
    """
    Retrieve recent conversation history for AI context.
    
    Args:
        user_id: User identifier (ObjectId as string)
        limit: Maximum number of messages to retrieve
        
    Returns:
        list: Conversation messages in chronological order
    """
    messages = await Message.find(
        Message.user_id == user_id
    ).sort(-Message.created_at).limit(limit).to_list()
    
    # Convert to chronological order and format for AI
    history = [
        {"role": msg.role.value, "content": msg.content}
        for msg in reversed(messages)
    ]
    
    return history
