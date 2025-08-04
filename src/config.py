from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///fallback.db"  # fallback for type checker

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
