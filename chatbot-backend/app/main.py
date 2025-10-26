"""
Main FastAPI application.
Entry point for the WhatsApp Chatbot backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
import os

from app.config import settings
from app.database import connect_db, close_db
from app.routers import whatsapp  # type: ignore
from app.routers import admin  # type: ignore
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler."""
    # Startup
    logger.info("Starting application...")
    await connect_db()
    logger.info("MongoDB/Cosmos DB initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await close_db()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="WhatsApp Chatbot Backend API",
    version="1.0.0",
    lifespan=lifespan,
    debug=settings.DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(whatsapp.router)
app.include_router(admin.router, prefix=settings.API_V1_PREFIX)

# Serve frontend static files at /frontend
# Frontend is mounted at /app/frontend in Docker (see docker-compose.yml)
frontend_path = os.path.abspath("/app/frontend")
if not os.path.exists(frontend_path):
    # Fallback for local development
    frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'chatbot-frontend'))

if os.path.exists(frontend_path):
    app.mount("/frontend", StaticFiles(directory=frontend_path, html=True), name="frontend")
    logger.info(f"Frontend mounted from: {frontend_path}")
else:
    logger.warning(f"Frontend path not found: {frontend_path}")


# Root endpoint
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - redirects to frontend login."""
    return RedirectResponse(url="/frontend/")


@app.get("/api", tags=["Health"])
async def api_info():
    """API information endpoint."""
    return {
        "service": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "frontend": "/frontend/"
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring and load balancers."""
    return {
        "status": "healthy",
        "service": "whatsapp-ai-backend",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )