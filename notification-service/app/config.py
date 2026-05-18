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
    smtp_enabled: bool = False
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_use_tls: bool = False
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from: str = "cowly@localhost"


settings = Settings()
