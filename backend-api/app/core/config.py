from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "local"
    app_name: str = "AI Resume Platform"
    api_prefix: str = "/api"

    database_url: str
    redis_url: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    upload_dir: str = "/app/uploads"
    max_upload_size_mb: int = 10

    ai_provider: str = "mock"
    ai_model: str = "mock-v1"
    ollama_base_url: str = "http://ollama:11434"
    ollama_model: str = "llama3.1"
    ai_timeout_seconds: int = 30

    admin_email: str = "admin@example.com"
    admin_password: str = "AdminPassword123"
    admin_full_name: str = "Local Admin"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
