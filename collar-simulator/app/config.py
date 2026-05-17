from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="COWLY_COLLAR_SIM_")

    host: str = "0.0.0.0"
    port: int = 8101
    herd_size: int = 100
    identify_blink_count: int = 3
    identify_blink_interval_ms: int = 400
    identify_session_ttl_seconds: int = 120
    scan_max_results: int = 50


settings = Settings()
