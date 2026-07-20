from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AptisPro"
    DEBUG: bool = False
    FRONTEND_URL: str = "http://localhost:8000"
    BACKEND_URL: str = "http://localhost:8001"

    # Database
    DATABASE_URL: str = "sqlite:///./aptispro_dev.db"

    # JWT
    SECRET_KEY: str = "dev-secret-key-CHANGE-IN-PRODUCTION-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    RESET_TOKEN_EXPIRE_MINUTES: int = 15      # 15 phút cho reset password

    # AI
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # Payment (PayOS)
    PAYOS_CLIENT_ID: str = ""
    PAYOS_API_KEY: str = ""
    PAYOS_CHECKSUM_KEY: str = ""
    VIP_DURATION_DAYS: int = 365
    VIP_PRICE_VND: int = 199000

    # Email (Resend)
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "noreply@aptispro.com"
    EMAIL_FROM_NAME: str = "AptisPro"

    # CORS
    ALLOWED_ORIGINS: str = '["http://localhost:8000", "http://localhost:5173"]'

    def get_allowed_origins(self) -> List[str]:
        return json.loads(self.ALLOWED_ORIGINS)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
