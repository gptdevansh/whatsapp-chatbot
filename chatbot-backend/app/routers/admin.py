"""
Admin API router with JWT authentication.

Provides authenticated endpoints for user management, conversation viewing,
statistics, and direct AI chat testing.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, asc, desc
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional

from app.database import get_session
from app.models import User, Message
from app.schemas import (
    LoginRequest, 
    TokenResponse, 
    ConversationResponse,
    ConversationListResponse,
    UserResponse,
    MessageResponse
)
from app.config import settings
from app.utils.logger import logger

router = APIRouter(prefix="/admin", tags=["Admin"])

# Security configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generate JWT access token.
    
    Args:
        data: Payload data to encode in token
        expires_delta: Optional custom expiration time
        
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Verify JWT token and extract admin identity.
    
    Args:
        credentials: Bearer token from request header
        
    Returns:
        dict: Admin user information
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        
        if not username or not isinstance(username, str):
            raise credentials_exception
            
        return {"username": username}
        
    except JWTError:
        raise credentials_exception


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Admin authentication endpoint.
    
    Validates credentials and returns JWT access token.
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
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin)
):
    """
    List all registered users with message counts.
    
    Returns paginated list of users ordered by creation date.
    Requires admin authentication.
    """
    # Get total user count
    count_result = await session.execute(select(func.count(User.id)))
    total = count_result.scalar() or 0
    
    # Fetch users with pagination
    result = await session.execute(
        select(User)
        .order_by(desc(User.created_at))
        .offset(skip)
        .limit(limit)
    )
    users = result.scalars().all()
    
    # Enrich with message counts
    user_responses = []
    for user in users:
        msg_count_result = await session.execute(
            select(func.count(Message.id)).where(Message.user_id == user.id)
        )
        msg_count = msg_count_result.scalar() or 0
        
        user_dict = {
            "id": user.id,
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
    user_id: int,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin)
):
    """
    Retrieve complete conversation history for a user.
    
    Returns all messages in chronological order.
    Requires admin authentication.
    """
    # Verify user exists
    user_result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Fetch conversation messages
    messages_result = await session.execute(
        select(Message)
        .where(Message.user_id == user_id)
        .order_by(asc(Message.created_at))
        .limit(limit)
    )
    messages = messages_result.scalars().all()
    
    return ConversationResponse(
        user=UserResponse.model_validate(user),
        messages=[MessageResponse.model_validate(msg) for msg in messages],
        total_messages=len(messages)
    )


@router.get("/stats")
async def get_stats(
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin)
):
    """
    Get platform statistics and metrics.
    
    Returns total users, messages, and active users in last 24h.
    Requires admin authentication.
    """
    # Total users
    users_count = await session.execute(select(func.count(User.id)))
    total_users = users_count.scalar()
    
    # Total messages
    messages_count = await session.execute(select(func.count(Message.id)))
    total_messages = messages_count.scalar()
    
    # Active users in last 24 hours
    yesterday = datetime.utcnow() - timedelta(days=1)
    active_users = await session.execute(
        select(func.count(func.distinct(Message.user_id)))
        .where(Message.created_at >= yesterday)
    )
    active_count = active_users.scalar()
    
    return {
        "total_users": total_users,
        "total_messages": total_messages,
        "active_users_24h": active_count,
        "timestamp": datetime.utcnow()
    }


@router.get("/chats/latest")
async def get_latest_chats(
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
    current_admin: dict = Depends(get_current_admin)
):
    """
    Retrieve most recent chat messages across all users.
    
    Returns latest messages with user information.
    Requires admin authentication.
    """
    result = await session.execute(
        select(Message, User)
        .join(User, Message.user_id == User.id)
        .order_by(desc(Message.created_at))
        .limit(limit)
    )
    rows = result.all()
    
    chats = []
    for message, user in rows:
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
