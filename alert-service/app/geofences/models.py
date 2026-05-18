import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Geofence(SQLModel, table=True):
    __tablename__ = "geofences"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        max_length=36,
    )
    farm_id: str = Field(index=True, max_length=36)
    name: str = Field(max_length=255)
    center_latitude: float
    center_longitude: float
    radius_meters: float = Field(gt=0)
    active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=_utcnow)
