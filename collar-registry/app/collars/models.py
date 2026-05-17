import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class CollarStatus(str, Enum):
    UNREGISTERED = "unregistered"
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    MAINTENANCE = "maintenance"


class Collar(SQLModel, table=True):
    __tablename__ = "collars"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        max_length=36,
    )
    mac_address: str = Field(index=True, unique=True, max_length=64)
    status: CollarStatus = Field(default=CollarStatus.AVAILABLE)
    cow_id: str | None = Field(default=None, max_length=36)
    firmware_version: str | None = Field(default=None, max_length=64)
    registered_at: datetime = Field(default_factory=_utcnow)
