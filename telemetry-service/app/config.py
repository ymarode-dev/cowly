from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="COWLY_TELEMETRY_")

    host: str = "0.0.0.0"
    port: int = 8105
    database_url: str = "postgresql+psycopg2://cowly:cowly@localhost:5433/cowly_telemetry"
    db_echo: bool = False
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"


settings = Settings()
