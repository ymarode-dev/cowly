import os

os.environ["COWLY_GATEWAY_AUTH_SERVICE_URL"] = "http://auth.test"
os.environ["COWLY_GATEWAY_HERD_SERVICE_URL"] = "http://herd.test"
os.environ["COWLY_GATEWAY_COLLAR_REGISTRY_URL"] = "http://registry.test"
os.environ["COWLY_GATEWAY_COLLAR_SIMULATOR_URL"] = "http://simulator.test"
os.environ["COWLY_GATEWAY_TELEMETRY_SERVICE_URL"] = "http://telemetry.test"
os.environ["COWLY_GATEWAY_ALERT_SERVICE_URL"] = "http://alert.test"
os.environ["COWLY_GATEWAY_NOTIFICATION_SERVICE_URL"] = "http://notification.test"
os.environ["COWLY_GATEWAY_REDIS_ENABLED"] = "false"

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client
