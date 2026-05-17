from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    collars_registered: int
    simulator_reachable: bool
