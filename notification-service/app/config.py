from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="COWLY_NOTIFICATION_")

    host: str = "0.0.0.0"
    port: int = 8107
    database_url: str = (
        "postgresql+psycopg2://cowly:cowly@localhost:5433/cowly_notifications"
    )
    db_echo: bool = False
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    internal_api_key: str = "cowly-internal-dev-key"


settings = Settings()
