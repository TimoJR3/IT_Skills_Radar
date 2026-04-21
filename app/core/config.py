from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "IT Skills Radar"
    app_env: str = "local"
    database_url: str = "postgresql+psycopg://postgres:postgres@db:5432/it_skills_radar"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

