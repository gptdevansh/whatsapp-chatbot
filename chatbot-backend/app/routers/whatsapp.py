"""WhatsApp webhook router for Meta WhatsApp Business API."""
from fastapi import APIRouter, Depends, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional

from app.database import get_session
from app.models import User, Message, MessageRole
from app.services.ai_service import ai_service
from app.services.whatsapp_service import whatsapp_service
from app.utils.logger import logger
from app.config import settings

router = APIRouter(prefix="/webhook", tags=["WhatsApp Webhook"])


@router.get("/whatsapp")
async def whatsapp_webhook_verify(request: Request):
    """Simple webhook verification."""
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    
    logger.info(f"Webhook verification request: mode={mode}, token={token}, challenge={challenge}")
    
    if mode == "subscribe" and token == settings.META_VERIFY_TOKEN:
        logger.info("Webhook verified successfully!")
        return PlainTextResponse(content=str(challenge))
    
    logger.error(f"Webhook verification failed. Got token: {token}, expected: {settings.META_VERIFY_TOKEN}")
    return PlainTextResponse(content="Invalid token", status_code=403)


@router.post("/whatsapp")
async def whatsapp_webhook(
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    """
    Webhook endpoint for incoming WhatsApp messages from Meta.
    
    Flow:
    1. Parse Meta's webhook payload
    2. Extract message details (sender, text, message_id)
    3. Get or create user
    4. Save incoming message
    5. Get conversation history
    6. Generate AI response
    7. Save AI response
    8. Send response back to user
    9. Mark message as read
    """
    try:
        body = await request.json()
        logger.info(f"Received webhook POST: {body}")
        
        # Meta sends a test webhook on setup - acknowledge it
        if body.get("object") != "whatsapp_business_account":
            logger.info(f"Non-WhatsApp webhook received: {body.get('object')}")
            return {"status": "ok"}
        
        # Extract message data from Meta's payload
        for entry in body.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                
                # Check if this is a message event
                messages = value.get("messages", [])
                if not messages:
                    logger.info("No messages in webhook, skipping")
                    continue
                
                for message_data in messages:
                    # Extract message details
                    message_id = message_data.get("id")
                    sender_phone = message_data.get("from")  # Phone number
                    message_type = message_data.get("type")
                    timestamp = message_data.get("timestamp")
                    
                    # Only process text messages
                    if message_type != "text":
                        logger.info(f"Ignoring non-text message type: {message_type}")
                        continue
                    
                    message_text = message_data.get("text", {}).get("body", "")
                    
                    # Get sender name from contacts if available
                    contacts = value.get("contacts", [])
                    sender_name = None
                    if contacts:
                        profile = contacts[0].get("profile", {})
                        sender_name = profile.get("name")
                    
                    logger.info(f"Processing message from {sender_phone} ({sender_name}): {message_text}")
                    
                    # Get or create user
                    user = await get_or_create_user(session, sender_phone, sender_name)
                    
                    if not user.id:
                        raise HTTPException(status_code=500, detail="Failed to create/retrieve user")
                    
                    # Save user's message
                    user_message = Message(
                        user_id=user.id,
                        role=MessageRole.USER,
                        content=message_text,
                        meta_message_id=message_id
                    )
                    session.add(user_message)
                    await session.commit()
                    await session.refresh(user_message)
                    
                    logger.info(f"Saved user message (ID: {user_message.id})")
                    
                    # Mark message as read
                    await whatsapp_service.mark_as_read(message_id)
                    
                    # Get conversation history
                    conversation_history = await get_conversation_history(session, user.id, limit=10)
                    
                    # Generate AI response
                    ai_response = await ai_service.generate_response(message_text, conversation_history)
                    
                    # Save AI response
                    assistant_message = Message(
                        user_id=user.id,  # type: ignore
                        role=MessageRole.ASSISTANT,
                        content=ai_response
                    )
                    session.add(assistant_message)
                    await session.commit()
                    await session.refresh(assistant_message)
                    
                    logger.info(f"Saved AI response (ID: {assistant_message.id})")
                    
                    # Send response back to user
                    await whatsapp_service.send_message(sender_phone, ai_response)
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {str(e)}")
        # Return 200 to Meta even on error to avoid retries
        return {"status": "error", "message": str(e)}


async def get_or_create_user(
    session: AsyncSession, 
    phone_number: str, 
    name: Optional[str] = None
) -> User:
    """Get existing user or create new one."""
    result = await session.execute(
        select(User).where(User.phone_number == phone_number)  # type: ignore
    )
    user = result.scalar_one_or_none()
    
    if user:
        logger.info(f"Found existing user: {phone_number}")
        if name and user.name != name:
            user.name = name
            await session.commit()
            await session.refresh(user)
        return user
    
    # Create new user
    user = User(phone_number=phone_number, name=name)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    logger.info(f"Created new user: {phone_number} (ID: {user.id})")
    return user


async def get_conversation_history(
    session: AsyncSession, 
    user_id: int, 
    limit: int = 10
) -> list[dict]:
    """Retrieve conversation history for AI context."""
    result = await session.execute(
        select(Message)
        .where(Message.user_id == user_id)  # type: ignore
        .order_by(desc(Message.created_at))  # type: ignore
        .limit(limit)
    )
    messages = result.scalars().all()
    
    # Reverse to chronological order and format for AI
    history = [
        {"role": msg.role.value, "content": msg.content}
        for msg in reversed(messages)
    ]
    
    return history