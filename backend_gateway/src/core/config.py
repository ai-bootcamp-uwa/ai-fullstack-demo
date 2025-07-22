import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Server
    host: str = "localhost"
    port: int = 3003
    debug: bool = True

    # Authentication
    jwt_secret: str = "your-secret-key"
    jwt_algorithm: str = "HS256"
    token_expire_minutes: int = 30

    # Service URLs (actual ports from implemented modules)
    data_foundation_url: str = "http://localhost:8000"  # Module 1 actual port
    cortex_engine_url: str = "http://localhost:3002"    # Module 2 actual port

    # CORS settings
    allowed_origins: List[str] = ["http://localhost:3004"]

    # Chat settings
    chat_storage_path: str = "data/chats"
    max_context_messages: int = 5
    max_chat_title_length: int = 100

    class Config:
        env_file = ".env"

# Global settings instance
settings = Settings() 