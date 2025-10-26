"""
Database models for WhatsApp chatbot.

MongoDB/Cosmos DB models using Pydantic and Beanie ODM.
"""
from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """
    Message role enumeration.
    
    Distinguishes between user-sent messages and AI-generated responses.
    """
    USER = "user"
    ASSISTANT = "assistant"


class User(Document):
    """
    WhatsApp user entity stored in MongoDB/Cosmos DB.
    
    Stores user profile information. Messages are linked via user_id reference.
    Each user is uniquely identified by their phone number.
    
    Attributes:
        phone_number: WhatsApp phone number (unique, indexed)
        name: Display name from WhatsApp profile (optional)
        is_active: Whether user account is active
        created_at: Account creation timestamp
        updated_at: Last profile update timestamp
    """
    phone_number: str = Field(..., unique=True)
    name: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "users"
        indexes = [
            "phone_number",
        ]


class Message(Document):
    """
    Conversation message entity stored in MongoDB/Cosmos DB.
    
    Stores individual messages in chat conversations, including both
    user inputs and AI-generated responses.
    
    Attributes:
        user_id: Reference to the user document ID (ObjectId as string)
        role: Whether message is from user or AI assistant
        content: The actual message text
        meta_message_id: WhatsApp's internal message ID (for user messages)
        created_at: Message timestamp (indexed for sorting)
    """
    user_id: str = Field(..., description="User document ID reference")
    role: MessageRole = Field(..., description="Message sender: user or assistant")
    content: str = Field(..., description="Message content/text")
    meta_message_id: Optional[str] = Field(
        default=None, 
        description="WhatsApp's message ID from Meta API"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "messages"
        indexes = [
            "user_id",
            "created_at",
        ]
