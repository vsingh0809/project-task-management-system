from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "Project Task Manager"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = "postgresql+asyncpg://fastigo:fastigo123@localhost:5432/fastigo_pm"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    OPENAI_API_KEY: str = ""
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()