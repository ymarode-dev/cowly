from __future__ import annotations

from datetime import datetime, timezone

from sqlmodel import Session, select

from app.cows.models import Cow
from app.cows.schemas import CowCreate, CowResponse, CowUpdate


class DuplicateEarTagError(Exception):
    pass


class CowNotFoundError(Exception):
    pass


def to_response(cow: Cow) -> CowResponse:
    return CowResponse(
        id=cow.id,
        farm_id=cow.farm_id,
        name=cow.name,
        ear_tag=cow.ear_tag,
        breed=cow.breed,
        date_of_birth=cow.date_of_birth,
        weight_kg=cow.weight_kg,
        notes=cow.notes,
        collar_id=cow.collar_id,
        created_at=cow.created_at,
        updated_at=cow.updated_at,
    )


def list_cows(session: Session, farm_id: str) -> list[CowResponse]:
    cows = session.exec(
        select(Cow).where(Cow.farm_id == farm_id).order_by(Cow.created_at)
    ).all()
    return [to_response(c) for c in cows]


def create_cow(session: Session, farm_id: str, body: CowCreate) -> CowResponse:
    existing = session.exec(
        select(Cow).where(Cow.farm_id == farm_id, Cow.ear_tag == body.ear_tag)
    ).first()
    if existing:
        raise DuplicateEarTagError("ear tag already exists")
    cow = Cow(farm_id=farm_id, **body.model_dump())
    session.add(cow)
    session.commit()
    session.refresh(cow)
    return to_response(cow)


def get_cow(session: Session, farm_id: str, cow_id: str) -> CowResponse:
    cow = session.get(Cow, cow_id)
    if not cow or cow.farm_id != farm_id:
        raise CowNotFoundError("Cow not found")
    return to_response(cow)


def update_cow(
    session: Session,
    farm_id: str,
    cow_id: str,
    body: CowUpdate,
) -> CowResponse:
    cow = session.get(Cow, cow_id)
    if not cow or cow.farm_id != farm_id:
        raise CowNotFoundError("Cow not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(cow, key, value)
    cow.updated_at = datetime.now(timezone.utc)
    session.add(cow)
    session.commit()
    session.refresh(cow)
    return to_response(cow)


def delete_cow(session: Session, farm_id: str, cow_id: str) -> None:
    cow = session.get(Cow, cow_id)
    if not cow or cow.farm_id != farm_id:
        raise CowNotFoundError("Cow not found")
    session.delete(cow)
    session.commit()


def count_cows(session: Session, farm_id: str | None = None) -> int:
    statement = select(Cow)
    if farm_id:
        statement = statement.where(Cow.farm_id == farm_id)
    return len(session.exec(statement).all())
