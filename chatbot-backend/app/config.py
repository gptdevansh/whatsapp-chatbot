"""Configuration management using pydantic-settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "WhatsApp AI Assistant"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Database
    # Use /home for Azure persistent storage, fallback to ./data for local development
    DATABASE_URL: str = "sqlite+aiosqlite:////home/data/chatbot.db"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Admin
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str
    
    # Meta WhatsApp Business API
    META_PHONE_NUMBER_ID: str
    META_ACCESS_TOKEN: str
    META_VERIFY_TOKEN: str
    META_BUSINESS_ACCOUNT_ID: str = ""
    META_API_VERSION: str = "v24.0"
    
    # AI API
    AI_PROVIDER: str = "groq"
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate SECRET_KEY is not default."""
        if not v or v == "your-secret-key-here-generate-a-secure-one":
            raise ValueError(
                "SECRET_KEY must be set to a secure random value. "
                "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    @field_validator("META_ACCESS_TOKEN", "META_PHONE_NUMBER_ID", "META_VERIFY_TOKEN")
    @classmethod
    def validate_meta_required(cls, v: str, info) -> str:
        """Validate required Meta WhatsApp fields."""
        field_name = info.field_name
        if not v or v.startswith("your_"):
            raise ValueError(
                f"{field_name} is required. Get it from Meta Developer Console. "
                "See META_SETUP.md for instructions."
            )
        return v
    
    @field_validator("GROQ_API_KEY")
    @classmethod
    def validate_ai_key(cls, v: str, info) -> str:
        """Validate at least one AI API key is configured."""
        values = info.data
        if values.get("AI_PROVIDER") == "groq" and (not v or v.startswith("gsk_your_")):
            raise ValueError(
                "GROQ_API_KEY is required when AI_PROVIDER=groq. "
                "Get a free key from https://console.groq.com/keys"
            )
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


settings = Settings()