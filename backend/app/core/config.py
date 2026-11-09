from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Enterprise Data Analysis Agent"
    app_env: str = "dev"
    mock_mode: bool = True
    database_url: str = "sqlite+aiosqlite:///./data/data_agent.db"
    redis_url: str = "redis://localhost:6379/0"
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-flash"
    cors_origins: str = "http://localhost:5173"
    max_agent_steps: int = 8
    query_timeout_seconds: int = 5
    max_query_rows: int = 500
    cache_ttl_seconds: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
