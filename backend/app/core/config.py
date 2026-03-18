from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "MoneyMind"
    database_url: str
    redis_url: str = "redis://localhost:6379"
    anthropic_api_key: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7
    brave_api_key: str = ""
    memory_mcp_path: str = "./memory/moneymind.json"
    frontend_url: str = "http://localhost:3000"

    class Config:
        env_file = ".env"

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
