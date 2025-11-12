from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # Application
    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database - defaults to MySQL for development
    DATABASE_URL: str = "mysql+pymysql://root:root@localhost:3306/delivery_system"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 0
    
    # Redis
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENCRYPTION_KEY: str = "your-encryption-key-32-bytes-long"
    
    # Voice Authentication
    VOICE_SIMILARITY_THRESHOLD: float = 0.85
    MIN_VOICE_SAMPLES: int = 3
    MAX_VOICE_SAMPLES: int = 5
    VOICE_SAMPLE_DURATION: int = 5
    
    # AI Detection
    AI_DETECTION_THRESHOLD: float = 0.90
    ENABLE_AI_DETECTION: bool = True
    
    # File Storage
    AUDIO_STORAGE_PATH: str = "../storage/audio_samples"
    MAX_AUDIO_SIZE_MB: int = 10
    
    # Twilio
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
    class Config:
        env_file = "config/.env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()