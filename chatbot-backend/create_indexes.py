"""
Create indexes for Azure Cosmos DB for MongoDB.
Cosmos DB requires explicit index creation for sorting operations.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

async def create_cosmos_indexes():
    """Create required indexes for Cosmos DB."""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DATABASE]
    
    print("Creating indexes for Azure Cosmos DB...")
    
    # Create index on User.created_at for sorting
    try:
        await db.User.create_index([("created_at", -1)])
        print("✅ Created index on User.created_at")
    except Exception as e:
        print(f"⚠️ User.created_at index: {e}")
    
    # Create index on Message.created_at for sorting
    try:
        await db.Message.create_index([("created_at", -1)])
        print("✅ Created index on Message.created_at")
    except Exception as e:
        print(f"⚠️ Message.created_at index: {e}")
    
    # Create index on Message.user_id for filtering
    try:
        await db.Message.create_index([("user_id", 1)])
        print("✅ Created index on Message.user_id")
    except Exception as e:
        print(f"⚠️ Message.user_id index: {e}")
    
    # Create compound index for user messages sorted by date
    try:
        await db.Message.create_index([("user_id", 1), ("created_at", -1)])
        print("✅ Created compound index on Message.user_id + created_at")
    except Exception as e:
        print(f"⚠️ Compound index: {e}")
    
    print("\n✅ Index creation complete!")
    client.close()

if __name__ == "__main__":
    asyncio.run(create_cosmos_indexes())
