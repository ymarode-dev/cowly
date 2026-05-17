from sqlmodel import Session, select

from app.collars.models import Collar, CollarStatus
from app.collars.schemas import CollarRegister, CollarResponse


class DuplicateMacError(Exception):
    pass


class CollarNotFoundError(Exception):
    pass


def to_response(collar: Collar) -> CollarResponse:
    return CollarResponse(
        id=collar.id,
        mac_address=collar.mac_address,
        status=collar.status,
        cow_id=collar.cow_id,
        firmware_version=collar.firmware_version,
        registered_at=collar.registered_at,
    )


def list_collars(session: Session) -> list[CollarResponse]:
    collars = session.exec(select(Collar).order_by(Collar.registered_at)).all()
    return [to_response(c) for c in collars]


def register_collar(session: Session, body: CollarRegister) -> CollarResponse:
    existing = session.exec(
        select(Collar).where(Collar.mac_address == body.mac_address)
    ).first()
    if existing:
        raise DuplicateMacError("collar already registered")
    collar = Collar(
        mac_address=body.mac_address,
        firmware_version=body.firmware_version,
        status=CollarStatus.AVAILABLE,
    )
    session.add(collar)
    session.commit()
    session.refresh(collar)
    return to_response(collar)


def get_collar(session: Session, collar_id: str) -> CollarResponse:
    collar = session.get(Collar, collar_id)
    if not collar:
        raise CollarNotFoundError("Collar not found")
    return to_response(collar)


def assign_collar(session: Session, collar_id: str, cow_id: str) -> CollarResponse:
    collar = session.get(Collar, collar_id)
    if not collar:
        raise CollarNotFoundError("Collar not found")
    collar.cow_id = cow_id
    collar.status = CollarStatus.ASSIGNED
    session.add(collar)
    session.commit()
    session.refresh(collar)
    return to_response(collar)


def count_collars(session: Session) -> int:
    return len(session.exec(select(Collar)).all())
