from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    alerts_total: int
    alerts_open: int
