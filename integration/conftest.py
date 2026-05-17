import os

import httpx
import pytest

GATEWAY_URL = os.getenv("COWLY_GATEWAY_URL", "http://localhost:8000")
TIMEOUT = float(os.getenv("COWLY_TEST_TIMEOUT", "10"))


def gateway_reachable() -> bool:
    try:
        response = httpx.get(f"{GATEWAY_URL}/", timeout=2.0)
        return response.status_code == 200
    except httpx.HTTPError:
        return False


@pytest.fixture(scope="session")
def gateway() -> str:
    if not gateway_reachable():
        pytest.skip(
            f"API gateway not reachable at {GATEWAY_URL}. "
            "Start the stack: docker compose up -d"
        )
    return GATEWAY_URL


@pytest.fixture
def http_client(gateway: str) -> httpx.Client:
    with httpx.Client(base_url=gateway, timeout=TIMEOUT) as client:
        yield client
