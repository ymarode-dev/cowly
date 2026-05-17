from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    users_registered: int
