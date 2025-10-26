"""MongoDB/Cosmos DB configuration and connection management."""
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from typing import Optional

from app.config import settings
from app.models import User, Message


# MongoDB client
mongodb_client: Optional[AsyncIOMotorClient] = None


async def connect_db():
    """Initialize MongoDB/Cosmos DB connection and Beanie ODM."""
    global mongodb_client
    
    # Create MongoDB client (works with Cosmos DB MongoDB API)
    mongodb_client = AsyncIOMotorClient(
        settings.MONGODB_URL,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=10000,
    )
    
    # Get database
    database = mongodb_client[settings.MONGODB_DATABASE]
    
    # Initialize Beanie with document models
    await init_beanie(
        database=database,
        document_models=[User, Message]
    )
    
    print(f"✅ Connected to MongoDB: {settings.MONGODB_DATABASE}")


async def close_db():
    """Close MongoDB connection."""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        print("✅ MongoDB connection closed")


# Compatibility function for dependency injection
async def get_db():
    """
    Dependency function for database access.
    With Beanie, we don't need to pass sessions - models work directly.
    This is kept for compatibility but doesn't yield anything.
    """
    yield None  # Beanie handles connections internally
