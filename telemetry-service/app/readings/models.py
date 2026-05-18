from __future__ import annotations


import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TelemetryReading(SQLModel, table=True):
    __tablename__ = "telemetry_readings"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        max_length=36,
    )
    farm_id: str = Field(index=True, max_length=36)
    collar_id: str = Field(index=True, max_length=36)
    cow_id: str | None = Field(default=None, max_length=36)
    latitude: float
    longitude: float
    activity_score: float
    temperature_c: float | None = None
    battery_percent: float | None = None
    recorded_at: datetime = Field(default_factory=_utcnow, index=True)
