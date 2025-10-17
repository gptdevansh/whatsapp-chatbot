# WhatsApp AI Chatbot

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-ready WhatsApp chatbot powered by FastAPI and Groq AI (Llama 3.3 70B), featuring an admin dashboard for managing conversations and users.

## Features

- AI-powered conversations using Groq's Llama 3.3 70B model
- Multi-user support with conversation history
- Admin dashboard with analytics and user management
- Real-time message processing via WhatsApp webhooks
- JWT-based authentication
- Docker containerized deployment
- SQLite database with persistent storage
- Meta WhatsApp Business API integration

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Meta WhatsApp Business account
- Groq API key (free at console.groq.com)

### Installation

1. Clone and configure:
```bash
git clone https://github.com/gptdevansh/whatsapp-chatbot.git
cd whatsapp-chatbot
cp .env.example .env
```

2. Edit `.env` with your credentials:
```env
META_PHONE_NUMBER_ID=your_phone_number_id
META_ACCESS_TOKEN=your_access_token
META_VERIFY_TOKEN=your_custom_verify_token
GROQ_API_KEY=your_groq_api_key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password
SECRET_KEY=your_random_32_character_secret_key
```

3. Start the application:
```bash
docker-compose up -d
```

4. Access dashboard at `http://localhost:8000/frontend/`

## API Keys Setup

**Groq AI:** Get free API key at [console.groq.com](https://console.groq.com)

**WhatsApp Business API:** 
- Visit [Meta for Developers](https://developers.facebook.com/)
- Create app and add WhatsApp product
- Get Phone Number ID and Access Token from API Setup
- Configure webhook: `https://your-domain.com/api/v1/webhook/whatsapp`

## Project Structure

```
whatsapp-chatbot/
├── app/                      # FastAPI backend
│   ├── routers/              # API endpoints
│   ├── services/             # Business logic
│   ├── config.py             # Configuration
│   ├── models.py             # Database models
│   └── main.py               # Application entry
├── chatbot-frontend/         # Admin dashboard
└── docker/                   # Docker configuration
```

## Technology Stack

**Backend:** FastAPI, SQLModel, SQLite, Pydantic  
**Frontend:** Vanilla JavaScript, CSS3, ApexCharts  
**AI:** Groq API (Llama 3.3 70B)  
**Integration:** Meta WhatsApp Business API  
**Deployment:** Docker, Azure App Service

## Development

### Local Setup (without Docker)

```bash
cd chatbot-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Access at:
- Dashboard: http://localhost:8000/frontend/
- API Docs: http://localhost:8000/docs

### Docker Commands

```bash
docker-compose logs -f              # View logs
docker-compose restart              # Restart services
docker-compose up -d --build        # Rebuild
docker-compose down                 # Stop all
```

## Deployment

### Azure App Service

**Live**: https://wtbot-chatbot.azurewebsites.net (Central India, B1 Basic)

```bash
# Build and push
docker build -t gptdevansh/whatsapp-chatbot:latest -f docker/Dockerfile .
docker push gptdevansh/whatsapp-chatbot:latest

# Deploy
az webapp restart --name wtbot-chatbot --resource-group whatsapp-chatbot-resources
```

### Required Environment Variables

Configure in Azure App Service → Configuration:
- `GROQ_API_KEY`, `META_ACCESS_TOKEN`, `PHONE_NUMBER_ID`
- `VERIFY_TOKEN`, `DATABASE_URL`
- `ADMIN_USERNAME`, `ADMIN_PASSWORD`

See [DEPLOYMENT_GUIDE.txt](DEPLOYMENT_GUIDE.txt) for detailed instructions.

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

## Troubleshooting

### Common Issues

**WhatsApp messages not sending**
- Verify `META_ACCESS_TOKEN` has `whatsapp_business_messaging` permission
- Check logs: `docker-compose logs -f`

**Database not persisting**
- Ensure `data/` directory exists with correct permissions
- Verify `DATABASE_URL` points to `/home/data/chatbot.db`

**Admin login failing**
- Confirm `ADMIN_USERNAME` and `ADMIN_PASSWORD` in environment
- Clear browser cache

**AI timeouts**
- Verify `GROQ_API_KEY` is valid
- Check Groq API rate limits

## Admin Dashboard

**Dashboard**: Total users, messages, active users (24h), 7-day activity chart

**Users**: View all users, search by name/phone/ID, message counts

**Chats**: Recent conversations, user/AI messages, timestamps

**AI Chat**: Test AI responses directly without WhatsApp

## Contributing

Contributions welcome! Fork the repository, create a feature branch, and open a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

Built with [FastAPI](https://fastapi.tiangolo.com/), [Groq](https://groq.com/), [Meta WhatsApp Business API](https://developers.facebook.com/), and [ApexCharts](https://apexcharts.com/).
