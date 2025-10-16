"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models import MessageRole


class UserBase(BaseModel):
    phone_number: str
    name: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    total_chats: int = 0
    
    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    content: str
    role: MessageRole


class MessageCreate(MessageBase):
    user_id: int
    meta_message_id: Optional[str] = None


class MessageResponse(MessageBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    user: UserResponse
    messages: List[MessageResponse]
    total_messages: int


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ConversationListResponse(BaseModel):
    users: List[UserResponse]
    total: int


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None