import os

os.environ["COWLY_COLLAR_SIM_HERD_SIZE"] = "20"

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client
