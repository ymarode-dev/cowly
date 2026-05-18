from __future__ import annotations


import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlmodel import Field, SQLModel, UniqueConstraint


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class CollarStatus(str, Enum):
    UNREGISTERED = "unregistered"
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    MAINTENANCE = "maintenance"


class Collar(SQLModel, table=True):
    __tablename__ = "collars"
    __table_args__ = (
        UniqueConstraint("farm_id", "mac_address", name="uq_collars_farm_mac"),
    )

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        max_length=36,
    )
    farm_id: str = Field(index=True, max_length=36)
    mac_address: str = Field(index=True, max_length=64)
    status: CollarStatus = Field(default=CollarStatus.AVAILABLE)
    cow_id: str | None = Field(default=None, max_length=36)
    firmware_version: str | None = Field(default=None, max_length=64)
    registered_at: datetime = Field(default_factory=_utcnow)
