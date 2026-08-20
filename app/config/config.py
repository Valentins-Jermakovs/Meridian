# ==============================
# Bibliotēku imports
# ==============================

from pydantic_settings import BaseSettings, SettingsConfigDict


# ==============================
# Lietotnes iestatījumi
# ==============================

class Settings(BaseSettings):

    # PostgreSQL datubāzes iestatījumi
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # Redis iestatījumi
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_PASSWORD: str | None = None
    REDIS_CACHE_TTL: int = 60

    # JWT tokenu iestatījumi
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    # .env faila konfigurācija
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


# Iestatījumu objekta izveide
settings = Settings()