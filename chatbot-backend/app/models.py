"""
Database models for WhatsApp chatbot.

Defines SQLModel entities for users and conversation messages.
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """
    Message role enumeration.
    
    Distinguishes between user-sent messages and AI-generated responses.
    """
    USER = "user"
    ASSISTANT = "assistant"


class User(SQLModel, table=True):
    """
    WhatsApp user entity.
    
    Stores user profile information and links to conversation history.
    Each user is uniquely identified by their phone number.
    
    Attributes:
        id: Unique user identifier (auto-generated)
        phone_number: WhatsApp phone number (unique, indexed)
        name: Display name from WhatsApp profile (optional)
        is_active: Whether user account is active
        created_at: Account creation timestamp
        updated_at: Last profile update timestamp
        messages: All messages associated with this user
    """
    __tablename__: str = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    phone_number: str = Field(unique=True, index=True)
    name: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    messages: List["Message"] = Relationship(back_populates="user")


class Message(SQLModel, table=True):
    """
    Conversation message entity.
    
    Stores individual messages in chat conversations, including both
    user inputs and AI-generated responses.
    
    Attributes:
        id: Unique message identifier (auto-generated)
        user_id: Reference to the user who owns this conversation
        role: Whether message is from user or AI assistant
        content: The actual message text
        meta_message_id: WhatsApp's internal message ID (for user messages)
        created_at: Message timestamp (indexed for sorting)
        user: Associated user object
    """
    __tablename__: str = "messages"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    role: MessageRole = Field(description="Message sender: user or assistant")
    content: str = Field(description="Message content/text")
    meta_message_id: Optional[str] = Field(
        default=None, 
        description="WhatsApp's message ID from Meta API"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Relationships
    user: Optional[User] = Relationship(back_populates="messages")