from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "University Social Media Generator"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Database
    DATABASE_URL: str = "sqlite:///./sql_app.db"

    
    OPENAI_API_KEY: str = ""

    # Social Media Credentials (optional)
    FB_PAGE_ACCESS_TOKEN: str = ""
    FB_PAGE_ID: str = ""
    IG_BUSINESS_ACCOUNT_ID: str = ""
    LINKEDIN_ACCESS_TOKEN: str = ""
    LINKEDIN_AUTHOR_URN: str = ""
    TIKTOK_ACCESS_TOKEN: str = ""
    WHATSAPP_API_TOKEN: str = ""
    WHATSAPP_PHONE_ID: str = ""
    WHATSAPP_RECIPIENT_PHONE: str = ""
    GREEN_API_TOKEN: str = ""
    GREEN_API_INSTANCE_ID: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields in .env
    )

settings = Settings()
