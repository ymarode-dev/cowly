from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    cows_total: int
