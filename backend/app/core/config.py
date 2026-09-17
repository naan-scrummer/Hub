from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./aio_students_hub.db"

    # Authentication
    SECRET_KEY: str = "dev-secret-key-change-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Demo credentials (development only)
    DEMO_STUDENT_EMAIL: str = "student@demo.edu"
    DEMO_STUDENT_PASSWORD: str = "demo123"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    # Notification Pipeline
    NOTIFICATION_JOB_INTERVAL_MINUTES: int = 5
    NOTIFICATION_RETENTION_DAYS: int = 30
    NOTIFICATION_BATCH_SIZE: int = 100
    ENABLE_BACKGROUND_NOTIFICATIONS: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()