from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    openai_api_key: str | None = None
    qdrant_api_key: str | None = None
    qdrant_url: str | None = None
    qdrant_host: str | None = None
    qdrant_port: int | None = None
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')