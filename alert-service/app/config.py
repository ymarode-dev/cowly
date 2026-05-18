from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="COWLY_ALERT_")

    host: str = "0.0.0.0"
    port: int = 8106
    database_url: str = "postgresql+psycopg2://cowly:cowly@localhost:5433/cowly_alerts"
    db_echo: bool = True
    notification_service_url: str = "http://notification-service:8107"
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    internal_api_key: str = "cowly-internal-dev-key"
    default_notification_recipient: str = "demo@cowly.local"
    low_battery_threshold: float = 20.0
    high_temperature_threshold: float = 39.5
    inactivity_threshold: float = 10.0


settings = Settings()
