"""
Admin API router for dashboard and analytics.

Provides authenticated endpoints for user management and statistics with MongoDB.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from typing import List

from app.config import settings
from app.models import User, Message
from app.schemas import (
    LoginRequest, TokenResponse, UserResponse,
    ConversationListResponse, MessageResponse, ConversationResponse
)
from app.utils.auth import create_access_token, get_current_admin
from app.utils.logger import logger

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/login", response_model=TokenResponse)
async def admin_login(request: LoginRequest):
    """
    Admin authentication endpoint.
    
    Validates credentials against configured admin username/password.
    Returns JWT token on successful authentication.
    """
    if (request.username != settings.ADMIN_USERNAME or
        request.password != settings.ADMIN_PASSWORD):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token = create_access_token(data={"sub": request.username})
    logger.info(f"Admin login successful: {request.username}")
    
    return TokenResponse(access_token=access_token)


@router.get("/users", response_model=ConversationListResponse)
async def list_users(
    skip: int = 0,
    limit: int = 50,
    current_admin: dict = Depends(get_current_admin)
):
    """
    List all registered users with message counts.
    
    Returns paginated list of users ordered by creation date.
    Requires admin authentication.
    """
    # Get total user count
    total = await User.count()
    
    # Fetch users with pagination (Cosmos DB compatible - no sort for now)
    users = await User.find_all().skip(skip).limit(limit).to_list()
    
    # Enrich with message counts
    user_responses = []
    for user in users:
        msg_count = await Message.find(Message.user_id == str(user.id)).count()
        
        user_dict = {
            "id": str(user.id),
            "phone_number": user.phone_number,
            "name": user.name,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "total_chats": msg_count
        }
        user_responses.append(UserResponse(**user_dict))
    
    return ConversationListResponse(users=user_responses, total=total)


@router.get("/conversation/{user_id}", response_model=ConversationResponse)
async def get_user_conversation(
    user_id: str,
    limit: int = 100,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Retrieve complete conversation history for a user.
    
    Returns all messages in chronological order.
    Requires admin authentication.
    """
    # Verify user exists
    user = await User.get(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Fetch conversation messages (Cosmos DB compatible - no sort for now)
    messages = await Message.find(
        Message.user_id == user_id
    ).limit(limit).to_list()
    
    user_response = UserResponse(
        id=str(user.id),
        phone_number=user.phone_number,
        name=user.name,
        is_active=user.is_active,
        created_at=user.created_at,
        total_chats=len(messages)
    )
    
    message_responses = [
        MessageResponse(
            id=str(msg.id),
            user_id=msg.user_id,
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at
        )
        for msg in messages
    ]
    
    return ConversationResponse(
        user=user_response,
        messages=message_responses,
        total_messages=len(messages)
    )


@router.get("/stats")
async def get_stats(current_admin: dict = Depends(get_current_admin)):
    """
    Get platform statistics and metrics.
    
    Returns total users, messages, and active users in last 24h.
    Requires admin authentication.
    """
    # Total users
    total_users = await User.count()
    
    # Total messages
    total_messages = await Message.count()
    
    # Active users in last 24 hours
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_messages = await Message.find(
        Message.created_at >= yesterday
    ).to_list()
    
    active_user_ids = set(msg.user_id for msg in recent_messages)
    active_count = len(active_user_ids)
    
    return {
        "total_users": total_users,
        "total_messages": total_messages,
        "active_users_24h": active_count,
        "timestamp": datetime.utcnow()
    }


@router.get("/chats/latest")
async def get_latest_chats(
    limit: int = 20,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Retrieve most recent chat messages across all users.
    
    Returns latest messages with user information.
    Requires admin authentication.
    """
    # Get latest messages (Cosmos DB compatible - no sort for now)
    messages = await Message.find_all().limit(limit).to_list()
    
    chats = []
    for message in messages:
        # Get user for each message
        user = await User.get(message.user_id)
        if user:
            chats.append({
                "user_name": user.name or user.phone_number,
                "phone_number": user.phone_number,
                "role": message.role.value,
                "message": message.content,
                "timestamp": message.created_at.isoformat()
            })
    
    return chats


@router.post("/ai-chat")
async def ai_chat(
    request: dict,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Direct AI chat interface for admins.
    
    Allows testing AI responses without WhatsApp integration.
    Requires admin authentication.
    """
    from app.services.ai_service import ai_service
    
    try:
        message = request.get("message", "").strip()
        if not message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Generate AI response
        response = await ai_service.generate_response(
            message=message,
            conversation_history=[]
        )
        
        return {
            "status": "success",
            "message": message,
            "response": response
        }
        
    except Exception as e:
        logger.error(f"Admin AI chat error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get AI response: {str(e)}"
        )
