from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    database_url: str
    debug: bool = False

    class Config:
        env_file = ".env"

# Create a single instance to use across the project (temporary)
from functools import lru_cache

@lru_cache()
def get_settings() -> Settings:
    return Settings()
