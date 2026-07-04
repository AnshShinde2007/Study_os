from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://studyos:studyos@localhost:5432/studyos"
    jwt_secret: str = "change-me"
    jwt_expiry_seconds: int = 3600
    refresh_expiry_days: int = 30
    cors_origins: str = "http://localhost:5173"
    public_url: str = "http://localhost:8000"
    storage_path: Path = Path("./storage")
    groq_api_key: str | None = None
    groq_api_url: str = "https://api.groq.com/openai/v1"
    groq_model: str = "llama-3.3-70b-versatile"
    supabase_jwt_secret: str | None = None  # Supabase Dashboard → Project Settings → API → JWT Secret
    resend_api_key: str | None = None        # Resend Dashboard → API Keys
    email_from: str = "StudyOS <noreply@studyos.app>"  # Verified sender in Resend
    google_client_id: str | None = None
    google_client_secret: str | None = None
    github_client_id: str | None = None
    github_client_secret: str | None = None
    session_secret: str = "change-me-too"
    cognee_enabled: bool = True
    rate_limit_per_minute: int = 100
    cognee_dataset_prefix: str = "studyos"
    db_provider: str = "postgres"
    db_name: str = "cognee"
    db_host: str = "127.0.0.1"
    db_port: int = 5432
    db_username: str = "studyos"
    db_password: str = "studyos"
    vector_db_provider: str = "pgvector"
    vector_dataset_database_handler: str = "pgvector"
    vector_db_name: str = "cognee"
    vector_db_url: str = "127.0.0.1"
    vector_db_port: int = 5432
    vector_db_username: str = "studyos"
    vector_db_password: str = "studyos"
    graph_database_provider: str = "kuzu"
    system_root_directory: str = "./.cognee_system"
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def allowed_origins(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
