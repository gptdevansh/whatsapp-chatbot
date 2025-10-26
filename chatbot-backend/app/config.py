"""
Application configuration management.

This module handles all environment-based configuration using Pydantic Settings.
All sensitive values should be loaded from environment variables.
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List


class Settings(BaseSettings):
    """Application settings with environment variable validation."""
    
    # ==================== Application Settings ====================
    APP_NAME: str = "WhatsApp AI Assistant"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "production"  # production, development, staging
    
    # ==================== Database Settings ====================
    # MongoDB/Cosmos DB Connection
    MONGODB_URL: str = "mongodb://localhost:27017"  # Default for local Docker
    MONGODB_DATABASE: str = "whatsapp_chatbot"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"
    
    # ==================== Security Settings ====================
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ==================== Admin Credentials ====================
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str
    
    # ==================== WhatsApp Business API ====================
    META_PHONE_NUMBER_ID: str
    META_ACCESS_TOKEN: str
    META_VERIFY_TOKEN: str
    META_BUSINESS_ACCOUNT_ID: str = ""
    META_API_VERSION: str = "v24.0"
    
    # ==================== AI Configuration ====================
    AI_PROVIDER: str = "groq"  # groq, openai, anthropic
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    
    # ==================== API Configuration ====================
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # ==================== Validators ====================
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Ensure SECRET_KEY is secure and properly configured."""
        if not v or v == "your-secret-key-here-generate-a-secure-one":
            raise ValueError(
                "SECRET_KEY must be set. Generate with: "
                "python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v
    
    @field_validator("META_ACCESS_TOKEN", "META_PHONE_NUMBER_ID", "META_VERIFY_TOKEN")
    @classmethod
    def validate_meta_required(cls, v: str, info) -> str:
        """Validate required WhatsApp Business API credentials."""
        if not v or v.startswith("your_"):
            raise ValueError(
                f"{info.field_name} is required. "
                "Get credentials from Meta Developer Console."
            )
        return v
    
    @field_validator("GROQ_API_KEY")
    @classmethod
    def validate_ai_key(cls, v: str, info) -> str:
        """Validate AI API key is configured for selected provider."""
        values = info.data
        if values.get("AI_PROVIDER") == "groq" and not v:
            raise ValueError(
                "GROQ_API_KEY required when AI_PROVIDER=groq. "
                "Get free key from console.groq.com"
            )
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# Global settings instance
settings = Settings()