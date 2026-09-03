from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://pokedex:pokedex@localhost:5432/pokedex"
    secret_key: str = "change-me"
    google_client_id: str = ""
    google_client_secret: str = ""
    frontend_url: str = "http://localhost:5173"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days


settings = Settings()
