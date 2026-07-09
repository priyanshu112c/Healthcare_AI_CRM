from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="CRM_",
        extra="ignore",
    )

    app_name: str = "Healthcare CRM Interaction Logger"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/healthcare_crm"

    groq_api_key: str = ""
    model: str = "gemma2-9b-it"
    model_fallback: str = "llama-3.3-70b-versatile"
    max_tokens: int = 4096
    temperature: float = 0.1

    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
