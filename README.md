# WhatsApp AI Chatbot

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-ready WhatsApp chatbot powered by FastAPI and Groq AI (Llama 3.3 70B), featuring a beautiful admin dashboard for managing conversations and users.

## ✨ Features

- 🤖 **AI-Powered Conversations** - Uses Groq's Llama 3.3 70B for intelligent responses
- 💬 **Multi-User Support** - Handle unlimited users with conversation history
- 📊 **Admin Dashboard** - Beautiful UI with analytics, user management, and chat viewer
- ⚡ **Real-Time Processing** - Instant message handling via WhatsApp webhooks
- 🔒 **Secure Authentication** - JWT-based admin authentication
- 🐳 **Docker Ready** - Containerized for easy deployment
- 💾 **Persistent Storage** - SQLite database with automatic data persistence
- 📱 **WhatsApp Business API** - Official Meta integration

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Meta WhatsApp Business account
- Groq API key (free at console.groq.com)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/gptdevansh/whatsapp-chatbot.git
cd whatsapp-chatbot
```

2. **Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
# WhatsApp Business API (from developers.facebook.com)
META_PHONE_NUMBER_ID=your_phone_number_id
META_ACCESS_TOKEN=your_access_token
META_VERIFY_TOKEN=your_custom_verify_token
META_API_VERSION=v21.0

# Groq AI (free from console.groq.com)
GROQ_API_KEY=your_groq_api_key

# Admin Credentials (change these!)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password
SECRET_KEY=your_random_32_character_secret_key

# Database (default works for Docker)
DATABASE_URL=sqlite+aiosqlite:////home/data/chatbot.db
```

3. **Start the application**
```bash
docker-compose up -d
```

4. **Access the admin dashboard**

Open your browser and navigate to:
```
http://localhost:8000/frontend/
```

Login with your configured admin credentials.

## 🔑 Getting API Keys

### Groq AI (Free - No Credit Card)
1. Visit [console.groq.com](https://console.groq.com)
2. Sign up for a free account
3. Navigate to API Keys section
4. Generate a new API key
5. Copy the key to your `.env` file

### WhatsApp Business API
1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create a new app or use existing one
3. Add WhatsApp product to your app
4. Get your:
   - Phone Number ID (from WhatsApp > API Setup)
   - Access Token (from WhatsApp > API Setup)
   - Create a Verify Token (any secure string you choose)
5. Configure webhook URL: `https://your-domain.com/api/v1/webhook/whatsapp`

## 📁 Project Structure

```
whatsapp-chatbot/
├── app/
│   ├── routers/              # API endpoints
│   │   ├── admin.py          # Admin authentication & management
│   │   └── whatsapp.py       # WhatsApp webhook handler
│   ├── services/             # Business logic
│   │   ├── ai_service.py     # Groq AI integration
│   │   └── whatsapp_service.py # WhatsApp API client
│   ├── config.py             # Configuration management
│   ├── database.py           # Database connection
│   ├── models.py             # SQLModel entities
│   ├── schemas.py            # Pydantic schemas
│   └── main.py               # FastAPI application
├── chatbot-frontend/         # Admin dashboard
│   ├── js/                   # JavaScript modules
│   ├── css/                  # Stylesheets
│   └── *.html                # Dashboard pages
├── data/                     # Persistent database storage
├── docker-compose.yml        # Docker orchestration
├── Dockerfile                # Container image
└── requirements.txt          # Python dependencies
```

## 🛠️ Technologies

**Backend**
- FastAPI - Modern Python web framework
- SQLModel - SQL databases with Python type annotations
- SQLite - Lightweight database
- Pydantic - Data validation
- Jose - JWT token handling

**Frontend**
- Vanilla JavaScript (ES6+)
- CSS3 with custom properties
- ApexCharts - Data visualization
- Toastify - Notifications

**AI & Integration**
- Groq API - Llama 3.3 70B model
- Meta WhatsApp Business API
- httpx - Async HTTP client

**Infrastructure**
- Docker - Containerization
- Azure App Service - Cloud hosting

## 💻 Development

### Local Development (without Docker)

1. **Set up Python environment**
```bash
cd chatbot-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Run the server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. **Access the application**
- API: http://localhost:8000
- Admin Dashboard: http://localhost:8000/frontend/
- API Docs: http://localhost:8000/docs

### Useful Commands

**View logs**
```bash
docker-compose logs -f
```

**Restart services**
```bash
docker-compose restart
```

**Rebuild after code changes**
```bash
docker-compose up -d --build
```

**Stop all services**
```bash
docker-compose down
```

**Access database**
```bash
docker exec -it whatsapp-chatbot-backend sqlite3 /home/data/chatbot.db
```

## 🚢 Deployment

### Azure App Service (Recommended)

1. **Build and push Docker image**
```bash
docker build -t your-registry/whatsapp-chatbot:latest .
docker push your-registry/whatsapp-chatbot:latest
```

2. **Configure Azure App Service**
```bash
az webapp config appsettings set --resource-group <resource-group> \
  --name <app-name> \
  --settings WEBSITES_ENABLE_APP_SERVICE_STORAGE=true \
             META_PHONE_NUMBER_ID=<your-id> \
             META_ACCESS_TOKEN=<your-token> \
             # ... other environment variables
```

3. **Enable persistent storage**
- Set `WEBSITES_ENABLE_APP_SERVICE_STORAGE=true`
- Database will persist at `/home/data/chatbot.db`

For detailed deployment guide, see [DEPLOYMENT_GUIDE.txt](DEPLOYMENT_GUIDE.txt)

### Other Platforms

Works on any Docker-compatible platform:
- AWS ECS/Fargate
- Google Cloud Run
- DigitalOcean App Platform
- Railway
- Render
- Fly.io

**Requirements:**
- HTTPS endpoint (for WhatsApp webhooks)
- Persistent volume for database
- Environment variables configured

## 🐛 Troubleshooting

### WhatsApp messages not sending

**Problem:** Messages reach server but don't send back to WhatsApp.

**Solution:** Check your Meta Access Token permissions:
1. Go to Meta Developer Console
2. Ensure token has `whatsapp_business_messaging` permission
3. Regenerate token if needed
4. Update `META_ACCESS_TOKEN` in environment variables

### Database not persisting

**Problem:** Data lost after container restart.

**Solution:** 
- Ensure `WEBSITES_ENABLE_APP_SERVICE_STORAGE=true` (Azure)
- Verify database path is `/home/data/chatbot.db`
- Check volume mounts in `docker-compose.yml`

### AI responses failing

**Problem:** AI service not responding.

**Solutions:**
- Verify `GROQ_API_KEY` is correct
- Check Groq API rate limits
- Review logs: `docker-compose logs -f`

### Authentication errors

**Problem:** Can't login to admin dashboard.

**Solutions:**
- Verify `ADMIN_USERNAME` and `ADMIN_PASSWORD` in `.env`
- Clear browser localStorage
- Check `SECRET_KEY` is at least 32 characters

## 📊 Admin Dashboard Features

### Dashboard Page
- Total users count
- Total messages count
- Active users (last 24h)
- 7-day activity chart

### Users Page
- View all registered users
- Search by name, phone, or ID
- See message counts per user

### Chats Page
- Recent conversations across all users
- View both user and AI messages
- Timestamps for each message

### AI Chat Page
- Test AI responses directly
- No WhatsApp needed
- Useful for debugging

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Groq](https://groq.com/) - AI inference platform
- [Meta](https://developers.facebook.com/) - WhatsApp Business API
- [ApexCharts](https://apexcharts.com/) - Chart library

## 📧 Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Made with ❤️ using FastAPI and Groq AI**
