from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Настройки приложения"""

    # База данных
    database_url: str = "postgresql://guidebook_user:guidebook_password@localhost:5433/guidebook_db"

    # API ключ для аутентификации
    api_key: str = "your-secret-api-key-here"

    # Настройки приложения
    app_name: str = "Guidebook REST API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Настройки CORS
    cors_origins: list[str] = ["*"]

    # Максимальный уровень вложенности для видов деятельности
    max_activity_levels: int = 3

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
