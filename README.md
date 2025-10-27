# WhatsApp AI Medical Consultant

A production-ready WhatsApp chatbot powered by AI (Llama 3.3 70B) that provides professional medical guidance and health consultations.

## Features

- AI medical consultant with symptom diagnosis and treatment advice
- WhatsApp integration for easy patient communication
- Admin dashboard for monitoring conversations
- Conversation history and user management
- Docker deployment ready

## Quick Setup

### 1. Clone Repository
```bash
git clone https://github.com/gptdevansh/whatsapp-chatbot.git
cd whatsapp-chatbot
```

### 2. Configure Environment
Create `.env` file in `chatbot-backend/` directory:
```env
# WhatsApp Business API (get from developers.facebook.com)
META_PHONE_NUMBER_ID=your_phone_id
META_ACCESS_TOKEN=your_access_token
META_VERIFY_TOKEN=your_verify_token

# AI API (get from console.groq.com)
GROQ_API_KEY=your_groq_api_key

# Admin Access
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_password

# Security
SECRET_KEY=your_32_character_secret

# Database - MongoDB Atlas (free tier)
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=whatsapp_chatbot
```

### 3. Run Locally
```bash
cd chatbot-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Access: http://localhost:8000/frontend/

### 4. Run with Docker
```bash
docker-compose up -d
```

## API Keys

- **Groq AI**: [console.groq.com](https://console.groq.com) (free tier available)
- **WhatsApp**: [developers.facebook.com](https://developers.facebook.com) → Create App → Add WhatsApp Product

## Tech Stack

FastAPI • Python 3.11 • Groq AI (Llama 3.3 70B) • WhatsApp Business API • MongoDB Atlas • Docker

## Deployment

**Docker:**
```bash
docker build -t whatsapp-chatbot -f docker/Dockerfile .
docker run -p 8000:8000 --env-file .env whatsapp-chatbot
```

**Production (Azure/AWS/GCP):**
- Configure environment variables in cloud platform
- Set webhook URL: `https://your-domain.com/api/v1/webhook/whatsapp`
- Ensure HTTPS enabled
- Connect to MongoDB Atlas for cloud database

## Project Structure

```
├── chatbot-backend/
│   ├── app/
│   │   ├── routers/       # API endpoints
│   │   ├── services/      # AI & WhatsApp logic
│   │   ├── models.py      # Database models
│   │   └── main.py        # FastAPI app
│   └── requirements.txt
├── chatbot-frontend/      # Admin dashboard
└── docker/                # Deployment configs
```

## License

MIT License
