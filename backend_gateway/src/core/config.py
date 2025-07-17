import os
from pydantic_settings import BaseSettings

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

    class Config:
        env_file = ".env"

# Global settings instance
settings = Settings() 