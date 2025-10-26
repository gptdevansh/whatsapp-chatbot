# Production Dockerfile for WhatsApp AI Chatbot
# Python 3.11 slim base image for minimal size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Python environment optimization
# PYTHONDONTWRITEBYTECODE: Prevents .pyc files (faster startup)
# PYTHONUNBUFFERED: Real-time logging without buffering
# PIP_NO_CACHE_DIR: Reduce image size by not caching pip downloads
# PIP_DISABLE_PIP_VERSION_CHECK: Skip version check for faster installs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
# gcc: Required for compiling some Python packages
# Clean up apt cache to reduce image size
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (better layer caching)
# Changes to code won't invalidate this layer
COPY ../chatbot-backend/requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY ../chatbot-backend/ .

# Copy frontend files to serve via FastAPI
COPY ../chatbot-frontend/ /app/frontend/

# Security: Run as non-root user
# Creates 'appuser' with UID 1000 for better security practices
# Note: Azure App Service needs write access to /home, so we keep root for Azure
# Uncomment USER line for local development
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
# USER appuser

# Expose application port
EXPOSE 8000

# Health check endpoint for container orchestration
# Checks if application is responding every 30 seconds
# Fails after 3 retries, allows 5s startup period
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# Start FastAPI application with Uvicorn
# --host 0.0.0.0: Listen on all network interfaces
# --port 8000: Default HTTP port
# --workers 1: Single worker (Azure handles scaling)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]