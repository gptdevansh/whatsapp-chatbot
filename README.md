# WhatsApp AI Medical Chatbot

AI-powered WhatsApp chatbot for medical consultations using Llama 3.3 70B.

## Prerequisites

- Python 3.11+
- Azure account (free tier)
- Meta Developer account
- Groq API account (free)

## Setup

### 1. Clone Repository
```bash
git clone https://github.com/gptdevansh/whatsapp-chatbot.git
cd whatsapp-chatbot
```

### 2. Create Azure Cosmos DB

**Step 1:** Login to Azure
```bash
az login
```

**Step 2:** Create Cosmos DB (Free Tier)
```bash
az cosmosdb create \
  --name your-cosmosdb-name \
  --resource-group your-resource-group \
  --kind MongoDB \
  --locations regionName="Central India" \
  --enable-free-tier true
```

**Step 3:** Get Connection String
```bash
az cosmosdb keys list \
  --name your-cosmosdb-name \
  --resource-group your-resource-group \
  --type connection-strings \
  --query "connectionStrings[0].connectionString"
```

**Step 4:** Create Database
```bash
az cosmosdb mongodb database create \
  --account-name your-cosmosdb-name \
  --resource-group your-resource-group \
  --name whatsapp_chatbot
```

### 3. Configure Environment

Copy `.env.example` to `.env` in `chatbot-backend/`:
```bash
cd chatbot-backend
cp .env.example .env
```

Edit `.env` with your credentials:
```env
MONGODB_URL=your_cosmos_connection_string
MONGODB_DATABASE=whatsapp_chatbot
META_PHONE_NUMBER_ID=your_whatsapp_phone_id
META_ACCESS_TOKEN=your_whatsapp_token
META_VERIFY_TOKEN=your_custom_verify_token
GROQ_API_KEY=your_groq_api_key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password
SECRET_KEY=your_32_char_secret_key
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Create Database Indexes
```bash
python create_indexes.py
```

### 6. Run Application
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Access admin panel: http://localhost:8000/frontend

## Docker Deployment

```bash
docker build -f docker/Dockerfile -t whatsapp-chatbot .
docker run -p 8000:8000 --env-file chatbot-backend/.env whatsapp-chatbot
```

## Production Deployment

1. Set environment variables in your cloud platform
2. Configure WhatsApp webhook: `https://your-domain.com/webhook/whatsapp`
3. Ensure HTTPS is enabled
4. Deploy Docker container

## Project Structure

```
chatbot-backend/
├── app/
│   ├── routers/         API endpoints
│   ├── services/        Business logic
│   ├── utils/           Helper functions
│   ├── models.py        Database models
│   ├── database.py      Database connection
│   └── main.py          Application entry
├── create_indexes.py    Database index setup
└── requirements.txt     Python dependencies
```

## Tech Stack

FastAPI, Python 3.11, Azure Cosmos DB, Groq AI, Meta WhatsApp API

## License

MIT
