# SQLite to MongoDB Migration - Complete ✅

## Overview
Successfully migrated WhatsApp AI Chatbot from SQLite to MongoDB (Azure Cosmos DB compatible).

## Migration Scope
- **Database**: SQLite → MongoDB
- **ORM/ODM**: SQLModel/SQLAlchemy → Beanie/Motor
- **ID Type**: Integer (auto-increment) → ObjectId (string)
- **Connections**: Session-based → Direct document operations

---

## Files Modified

### 1. **Models** (`app/models.py`)
- ✅ Replaced `SQLModel` with `Beanie.Document`
- ✅ Removed foreign key relationships
- ✅ Added collection names and indexes via `Settings` class
- ✅ Changed ID fields from `Optional[int]` to auto-generated ObjectId

**Key Changes**:
```python
# OLD
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    messages: List["Message"] = Relationship(back_populates="user")

# NEW
class User(Document):
    phone_number: str
    class Settings:
        name = "users"
        indexes = [IndexModel([("phone_number", 1)], unique=True)]
```

### 2. **Database Connection** (`app/database.py`)
- ✅ Removed SQLAlchemy async engine and session maker
- ✅ Added Motor AsyncIOMotorClient
- ✅ Implemented Beanie initialization with `init_beanie()`
- ✅ Created `connect_db()` and `close_db()` functions

**Key Changes**:
```python
# OLD
engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine)

# NEW
client = AsyncIOMotorClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DATABASE]
await init_beanie(database=db, document_models=[User, Message])
```

### 3. **Configuration** (`app/config.py`)
- ✅ Removed `DATABASE_URL` (SQLite connection string)
- ✅ Added `MONGODB_URL` (default: mongodb://localhost:27017)
- ✅ Added `MONGODB_DATABASE` (default: whatsapp_chatbot)

**Key Changes**:
```python
# OLD
DATABASE_URL: str = "sqlite+aiosqlite:///./chatbot.db"

# NEW
MONGODB_URL: str = "mongodb://localhost:27017"
MONGODB_DATABASE: str = "whatsapp_chatbot"
```

### 4. **Dependencies** (`requirements.txt`)
- ✅ Removed: `sqlmodel`, `aiosqlite`, `alembic`
- ✅ Added: `motor==3.3.2`, `beanie==1.24.0`, `pymongo==4.6.1`

### 5. **Main Application** (`app/main.py`)
- ✅ Updated lifespan: `init_db()` → `connect_db()`
- ✅ Added shutdown: `await close_db()`

### 6. **WhatsApp Router** (`app/routers/whatsapp.py`)
- ✅ Removed all `AsyncSession` dependencies
- ✅ Replaced SQLAlchemy queries with Beanie operations
- ✅ Changed user_id type from `int` to `str`

**Query Pattern Changes**:
```python
# OLD - SQLAlchemy
result = await session.execute(select(User).where(User.phone_number == phone))
user = result.scalar_one_or_none()
session.add(new_message)
await session.commit()

# NEW - Beanie
user = await User.find_one(User.phone_number == phone)
await new_message.insert()
```

### 7. **Admin Router** (`app/routers/admin.py`)
- ✅ Removed all `AsyncSession` dependencies
- ✅ Replaced complex SQL queries with Beanie operations
- ✅ Updated all ID fields from `int` to `str`

**Endpoint Changes**:
- `list_users()`: Uses `User.find_all().sort().skip().limit()`
- `get_user_conversation()`: Uses `User.get()` and `Message.find()`
- `get_stats()`: Direct `count()` aggregations
- `get_latest_chats()`: Sequential document lookups

### 8. **Schemas** (`app/schemas.py`)
- ✅ Changed all ID fields from `int` to `str` (MongoDB ObjectId)
- ✅ Updated: `UserResponse.id`, `MessageCreate.user_id`, `MessageResponse.id/user_id`

### 9. **Environment Configuration** (`.env`)
- ✅ Replaced `DATABASE_URL=sqlite+aiosqlite:///./chatbot.db`
- ✅ Added `MONGODB_URL=mongodb://mongodb:27017` (Docker)
- ✅ Added `MONGODB_DATABASE=whatsapp_chatbot`

### 10. **Docker Compose** (`docker/docker-compose.yml`)
- ✅ Added MongoDB 7.0 service
- ✅ Added health check for MongoDB
- ✅ Updated backend to depend on MongoDB service
- ✅ Changed volume from `data` to `mongodb_data`
- ✅ Updated environment variables to use MongoDB

**New Service**:
```yaml
mongodb:
  image: mongo:7.0
  ports:
    - "27017:27017"
  volumes:
    - mongodb_data:/data/db
  healthcheck:
    test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
```

### 11. **Dockerfile** (`docker/Dockerfile`)
- ✅ Removed SQLite data directory creation
- ✅ Removed SQLite-specific comments

---

## Testing Steps

### Local Testing (Docker)

1. **Start Services**:
```powershell
cd docker
docker-compose up -d
```

2. **Check Logs**:
```powershell
docker-compose logs -f backend
docker-compose logs -f mongodb
```

3. **Verify MongoDB Connection**:
```powershell
docker exec -it whatsapp-chatbot-mongodb mongosh
# In MongoDB shell:
use whatsapp_chatbot
db.users.find()
db.messages.find()
```

4. **Test API**:
- Health: http://localhost:8000/health
- Admin: http://localhost:8000/admin/
- Docs: http://localhost:8000/docs

5. **Test WhatsApp Integration**:
- Send test message to your WhatsApp number
- Check user creation in MongoDB
- Verify conversation history

---

## Azure Deployment

### 1. Create Azure Cosmos DB (MongoDB API)

**Option A: Azure Portal**
1. Go to Azure Portal → Create Resource → Azure Cosmos DB
2. Select **MongoDB API**
3. Choose:
   - Resource Group: (your existing group)
   - Account Name: `whatsapp-chatbot-cosmosdb`
   - Location: Central India (same as your app)
   - Capacity: Serverless (cost-effective for small workloads)
4. Create and wait for deployment

**Option B: Azure CLI**
```bash
az cosmosdb create \
  --name whatsapp-chatbot-cosmosdb \
  --resource-group <your-resource-group> \
  --kind MongoDB \
  --server-version 4.2 \
  --default-consistency-level Eventual \
  --enable-automatic-failover true \
  --locations regionName=centralindia failoverPriority=0 isZoneRedundant=False
```

### 2. Get Connection String

**Azure Portal**:
1. Go to Cosmos DB account → Settings → Connection String
2. Copy **PRIMARY CONNECTION STRING**
3. Format: `mongodb://<account>:<password>@<account>.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb`

**Azure CLI**:
```bash
az cosmosdb keys list \
  --name whatsapp-chatbot-cosmosdb \
  --resource-group <your-resource-group> \
  --type connection-strings
```

### 3. Update Azure App Service Environment Variables

**Azure Portal**:
1. Go to App Service: `wtbot-chatbot`
2. Settings → Configuration → Application settings
3. Add/Update:
   - `MONGODB_URL` = (your Cosmos DB connection string)
   - `MONGODB_DATABASE` = `whatsapp_chatbot`
4. Remove old variable:
   - Delete `DATABASE_URL` (if exists)
5. Click **Save** → **Restart**

**Azure CLI**:
```bash
az webapp config appsettings set \
  --resource-group <your-resource-group> \
  --name wtbot-chatbot \
  --settings \
    MONGODB_URL="<your-cosmos-db-connection-string>" \
    MONGODB_DATABASE="whatsapp_chatbot"

# Remove old SQLite variable
az webapp config appsettings delete \
  --resource-group <your-resource-group> \
  --name wtbot-chatbot \
  --setting-names DATABASE_URL
```

### 4. Deploy Updated Application

**If using Docker Hub**:
```powershell
# Build new image with MongoDB dependencies
docker build -f docker/Dockerfile -t <your-dockerhub-username>/whatsapp-chatbot:latest .

# Push to Docker Hub
docker push <your-dockerhub-username>/whatsapp-chatbot:latest

# Azure will auto-pull if webhook is configured
# Otherwise, restart the app service
az webapp restart --name wtbot-chatbot --resource-group <your-resource-group>
```

### 5. Verify Deployment

**Check Logs**:
```bash
az webapp log tail --name wtbot-chatbot --resource-group <your-resource-group>
```

**Test Endpoints**:
- Health: https://wtbot-chatbot.azurewebsites.net/health
- Admin: https://wtbot-chatbot.azurewebsites.net/admin/
- API Docs: https://wtbot-chatbot.azurewebsites.net/docs

**Verify Cosmos DB**:
1. Azure Portal → Cosmos DB → Data Explorer
2. Check `whatsapp_chatbot` database
3. View `users` and `messages` collections

---

## Data Migration (Optional)

If you have existing SQLite data you want to migrate:

1. **Export from SQLite**:
```python
import sqlite3
import json
from datetime import datetime

conn = sqlite3.connect('chatbot.db')
cursor = conn.cursor()

# Export users
cursor.execute("SELECT * FROM user")
users = cursor.fetchall()
with open('users.json', 'w') as f:
    json.dump([{
        'phone_number': row[1],
        'name': row[2],
        'is_active': row[3],
        'created_at': row[4],
        'updated_at': row[5]
    } for row in users], f)

# Export messages
cursor.execute("SELECT * FROM message")
messages = cursor.fetchall()
with open('messages.json', 'w') as f:
    json.dump([{
        'user_id': row[1],  # Will need to map to new ObjectId
        'role': row[2],
        'content': row[3],
        'meta_message_id': row[4],
        'created_at': row[5]
    } for row in messages], f)

conn.close()
```

2. **Import to MongoDB**:
```python
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import json

async def migrate():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.whatsapp_chatbot
    
    # Import users
    with open('users.json') as f:
        users = json.load(f)
        if users:
            result = await db.users.insert_many(users)
            print(f"Imported {len(result.inserted_ids)} users")
    
    # TODO: Map old user IDs to new ObjectIds for messages
    
asyncio.run(migrate())
```

---

## Rollback Plan (If Needed)

If you encounter issues, you can rollback:

1. **Restore Git**:
```powershell
git checkout <commit-before-migration>
```

2. **Restore Environment Variables**:
```bash
az webapp config appsettings set \
  --resource-group <your-resource-group> \
  --name wtbot-chatbot \
  --settings DATABASE_URL="sqlite+aiosqlite:///./data/chatbot.db"
```

3. **Deploy Old Version**:
```powershell
docker build -f docker/Dockerfile -t <your-dockerhub-username>/whatsapp-chatbot:rollback .
docker push <your-dockerhub-username>/whatsapp-chatbot:rollback
```

---

## Key Differences: SQLite vs MongoDB

| Aspect | SQLite (OLD) | MongoDB (NEW) |
|--------|-------------|---------------|
| **Database Type** | Relational (SQL) | Document (NoSQL) |
| **ORM/ODM** | SQLModel/SQLAlchemy | Beanie/Motor |
| **Primary Key** | Auto-increment Integer | ObjectId (24-char hex) |
| **Relationships** | Foreign Keys | Document References |
| **Queries** | SQL via select() | MongoDB queries |
| **Transactions** | Session-based | Document-based |
| **Scalability** | Single file | Distributed clusters |
| **Cloud** | Not cloud-native | Azure Cosmos DB native |

---

## Performance Considerations

**MongoDB Advantages**:
- ✅ Better horizontal scaling (sharding)
- ✅ Cloud-native (Cosmos DB integration)
- ✅ Flexible schema (easy to add fields)
- ✅ Better for document-based data (messages)
- ✅ Built-in replication and high availability

**Potential Concerns**:
- ⚠️ ObjectId as string (24 chars vs 4 bytes int)
- ⚠️ No joins (manual document lookups)
- ⚠️ Eventual consistency in Cosmos DB (by default)

**Optimizations Applied**:
- ✅ Indexes on `phone_number` (unique)
- ✅ Indexes on `user_id` and `created_at` for messages
- ✅ Limited conversation history (last 10 messages)
- ✅ Async operations with Motor

---

## Next Steps

1. ✅ **Test Locally**: Run `docker-compose up -d` and verify
2. ⏳ **Create Cosmos DB**: Provision MongoDB API instance
3. ⏳ **Update Azure App Service**: Set environment variables
4. ⏳ **Deploy**: Push new Docker image or redeploy
5. ⏳ **Monitor**: Check logs and Cosmos DB metrics
6. ⏳ **Test Production**: Send WhatsApp messages and verify storage

---

## Troubleshooting

### Issue: Connection Timeout to MongoDB
**Solution**: Check network connectivity, firewall rules, and connection string

### Issue: Authentication Failed
**Solution**: Verify Cosmos DB connection string includes `ssl=true` and correct credentials

### Issue: Documents Not Persisting
**Solution**: Ensure `await document.insert()` or `await document.save()` is called

### Issue: Index Errors
**Solution**: Drop and recreate indexes:
```python
await User.get_motor_collection().drop_indexes()
await init_beanie(database=db, document_models=[User, Message])
```

---

## Support & Contact

- **Azure Documentation**: https://learn.microsoft.com/azure/cosmos-db/mongodb/
- **Beanie ODM Docs**: https://beanie-odm.dev/
- **Motor Docs**: https://motor.readthedocs.io/

---

**Migration Completed**: ✅ All files updated, ready for deployment
**Next Action**: Test locally with Docker, then deploy to Azure Cosmos DB
