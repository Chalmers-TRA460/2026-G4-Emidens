from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    model: str = "gemma4:e4b"
    ollama_base_url: str = "http://localhost:11434"
    api_host: str = "127.0.0.1"
    api_port: int = 8080


settings = Settings()
