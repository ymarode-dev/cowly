from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="COWLY_GATEWAY_")

    host: str = "0.0.0.0"
    port: int = 8000
    auth_service_url: str = "http://auth-service:8102"
    herd_service_url: str = "http://herd-service:8103"
    collar_registry_url: str = "http://collar-registry:8104"
    collar_simulator_url: str = "http://collar-simulator:8101"
    telemetry_service_url: str = "http://telemetry-service:8105"
    alert_service_url: str = "http://alert-service:8106"
    notification_service_url: str = "http://notification-service:8107"
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"


settings = Settings()
