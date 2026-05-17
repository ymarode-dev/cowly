from typing import Any, Optional

from pydantic import BaseModel


class ServiceHealth(BaseModel):
    name: str
    url: str
    status: str
    detail: Optional[dict[str, Any]] = None


class GatewayHealthResponse(BaseModel):
    status: str
    service: str
    services: list[ServiceHealth]
