"""SQLModel database models."""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """Enum for message roles."""
    USER = "user"
    ASSISTANT = "assistant"


class User(SQLModel, table=True):
    """User model representing WhatsApp users."""
    __tablename__: str = "users"  # type: ignore
    
    id: Optional[int] = Field(default=None, primary_key=True)
    phone_number: str = Field(unique=True, index=True)
    name: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    messages: List["Message"] = Relationship(back_populates="user")


class Message(SQLModel, table=True):
    """Message model storing conversation history."""
    __tablename__: str = "messages"  # type: ignore
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    role: MessageRole = Field(description="Message sender: user or assistant")
    content: str = Field(description="Message content/text")
    meta_message_id: Optional[str] = Field(default=None, description="Meta WhatsApp message ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    user: Optional[User] = Relationship(back_populates="messages")