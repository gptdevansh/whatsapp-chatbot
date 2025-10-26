"""
Pydantic schemas for API request/response validation.

Defines data transfer objects (DTOs) for all API endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models import MessageRole


# User Schemas
class UserBase(BaseModel):
    """Base user schema with common fields."""
    phone_number: str
    name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating new users."""
    pass


class UserResponse(UserBase):
    """
    User response schema with additional metadata.
    
    Includes total chat count for dashboard display.
    MongoDB ID is returned as string.
    """
    id: str  # MongoDB ObjectId as string
    is_active: bool
    created_at: datetime
    total_chats: int = 0
    
    class Config:
        from_attributes = True


# Message Schemas
class MessageBase(BaseModel):
    """Base message schema with common fields."""
    content: str
    role: MessageRole


class MessageCreate(MessageBase):
    """
    Schema for creating new messages.
    
    Includes Meta's message ID for tracking WhatsApp messages.
    MongoDB references user_id as string.
    """
    user_id: str  # MongoDB ObjectId as string
    meta_message_id: Optional[str] = None


class MessageResponse(MessageBase):
    """Message response schema with metadata. MongoDB IDs as strings."""
    id: str  # MongoDB ObjectId as string
    user_id: str  # MongoDB ObjectId as string
    created_at: datetime
    
    class Config:
        from_attributes = True


# Conversation Schemas
class ConversationResponse(BaseModel):
    """
    Complete conversation view.
    
    Includes user information and all associated messages.
    """
    user: UserResponse
    messages: List[MessageResponse]
    total_messages: int


class ConversationListResponse(BaseModel):
    """
    Paginated list of users with conversation metadata.
    """
    users: List[UserResponse]
    total: int


# Authentication Schemas
class LoginRequest(BaseModel):
    """Admin login credentials."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"


# Generic Response Schema
class APIResponse(BaseModel):
    """
    Generic API response wrapper.
    
    Provides consistent response format across endpoints.
    """
    success: bool
    message: str
    data: Optional[dict] = None