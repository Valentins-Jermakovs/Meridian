# ==============================
# Library imports
# ==============================

from pydantic_settings import (
    BaseSettings, 
    SettingsConfigDict
)


# ==============================
# Application settings
# ==============================

class Settings(BaseSettings):
    """
    This class represents the application settings.
    
    It uses Pydantic's `BaseSettings` to define the structure of the settings,
    and `SettingsConfigDict` to configure the .env file.
    """
    
    # PostgreSQL database settings
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    
    # Redis settings
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_PASSWORD: str | None = None
    REDIS_CACHE_TTL: int = 60
    
    # JWT token settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    
    # .env file configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


# Create an instance of the settings class
settings = Settings()