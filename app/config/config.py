# Bibliotēkas
from pydantic_settings import BaseSettings, SettingsConfigDict


# Iestatījumi
class Settings(BaseSettings):

    # PostgreSQL iestatījumi
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # Tokenu iestatījumi
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


# Objekta izveide
settings = Settings()
