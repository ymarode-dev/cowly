from __future__ import annotations


import uuid
from datetime import date, datetime, timezone

from sqlmodel import Field, SQLModel, UniqueConstraint


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Cow(SQLModel, table=True):
    __tablename__ = "cows"
    __table_args__ = (UniqueConstraint("farm_id", "ear_tag", name="uq_cows_farm_ear_tag"),)

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        max_length=36,
    )
    farm_id: str = Field(index=True, max_length=36)
    name: str = Field(max_length=255)
    ear_tag: str = Field(index=True, max_length=64)
    breed: str = Field(max_length=128)
    date_of_birth: date | None = None
    weight_kg: float | None = None
    notes: str | None = None
    collar_id: str | None = Field(default=None, max_length=36)
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)
