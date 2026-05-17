from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="COWLY_COLLAR_REGISTRY_")

    host: str = "0.0.0.0"
    port: int = 8104
    database_url: str = "postgresql+psycopg2://cowly:cowly@localhost:5433/cowly_collar"
    db_echo: bool = True
    collar_simulator_url: str = "http://collar-simulator:8101"
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"


settings = Settings()
