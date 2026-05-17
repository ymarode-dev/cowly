from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="COWLY_HERD_")

    host: str = "0.0.0.0"
    port: int = 8103
    database_url: str = "postgresql+psycopg2://cowly:cowly@localhost:5433/cowly_herd"
    db_echo: bool = False
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"


settings = Settings()
