# WhatsApp AI Chatbot

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://www.docker.com/)

A production-ready WhatsApp chatbot powered by FastAPI and Groq AI, featuring an admin dashboard for managing conversations and users.

## Features

- AI-powered responses using Groq's Llama 3.3 70B model
- Multi-user conversation support with message history
- Admin dashboard with user analytics and chat viewer
- Real-time message processing via WhatsApp webhooks
- Docker containerized for easy deployment

## Getting Started

First, grab the code from GitHub:
```bash
git clone https://github.com/yourusername/whatsapp-chatbot.git
cd whatsapp-chatbot
```

Next, set up your environment variables. Copy the example file and fill in your details:
```bash
cd chatbot-backend
cp .env.example .env
```

Open the `.env` file and add your API keys (don't worry, I'll show you where to get them):
```env
# Get these from Meta for Developers (developers.facebook.com)
META_PHONE_NUMBER_ID=your_phone_number_id
META_ACCESS_TOKEN=your_access_token
META_VERIFY_TOKEN=your_verify_token

# Free API key from console.groq.com (no credit card needed)
GROQ_API_KEY=your_groq_api_key

# Create your own admin credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=choose_a_strong_password
SECRET_KEY=any_random_32_character_string
```

Now start everything with Docker:
```bash
cd ..
docker-compose up -d
```

That's it! Open your browser and go to `http://localhost:8000/frontend/` to access the admin dashboard.

## Where to Get API Keys

**Groq AI (Free)**: Head over to [console.groq.com](https://console.groq.com), sign up, and grab your free API key. No credit card required.

**WhatsApp Business API**: Go to [Meta for Developers](https://developers.facebook.com/), create an app, and set up WhatsApp Business. You'll get your phone number ID and access token from there.

## Project Structure

```
whatsapp-chatbot/
├── chatbot-backend/     # FastAPI application
├── chatbot-frontend/    # Admin dashboard
└── docker/              # Docker configuration
```

## Technologies

- **Backend**: FastAPI, SQLModel, SQLite
- **Frontend**: Vanilla JavaScript, CSS3
- **AI**: Groq API (Llama 3.3 70B)
- **Integration**: Meta WhatsApp Business API
- **Container**: Docker

## Common Commands

Want to see what's happening? Check the logs:
```bash
docker-compose logs -f
```

Need to restart? Simple:
```bash
docker-compose restart
```

All done for the day? Shut it down:
```bash
docker-compose down
```

## Deployment

Deploy on any Docker-compatible platform (Azure, AWS, Google Cloud, DigitalOcean, Railway, Render, Fly.io).

Requirements for production:
- HTTPS endpoint for WhatsApp webhooks
- Persistent storage for SQLite database
- Properly configured environment variables

## License
