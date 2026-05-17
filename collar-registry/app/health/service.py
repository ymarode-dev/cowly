from sqlmodel import Session

from app.collars import service as collar_service
from app.health.schemas import HealthResponse
from app.simulator import service as simulator_service


async def get_health(session: Session) -> HealthResponse:
    simulator_ok = await simulator_service.check_simulator_health()
    return HealthResponse(
        status="ok",
        service="collar-registry",
        collars_registered=collar_service.count_collars(session),
        simulator_reachable=simulator_ok,
    )
