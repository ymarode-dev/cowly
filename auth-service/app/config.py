from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="COWLY_AUTH_")

    host: str = "0.0.0.0"
    port: int = 8102
    database_url: str = "postgresql+psycopg2://cowly:cowly@localhost:5433/cowly_auth"
    db_echo: bool = True
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60


settings = Settings()
