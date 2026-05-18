from __future__ import annotations


import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AlertType(str, Enum):
    GEOFENCE_EXIT = "geofence_exit"
    LOW_BATTERY = "low_battery"
    INACTIVITY = "inactivity"
    HIGH_TEMPERATURE = "high_temperature"


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class Alert(SQLModel, table=True):
    __tablename__ = "alerts"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        max_length=36,
    )
    farm_id: str = Field(index=True, max_length=36)
    cow_id: str | None = Field(default=None, max_length=36)
    collar_id: str = Field(index=True, max_length=36)
    alert_type: AlertType
    severity: AlertSeverity = AlertSeverity.WARNING
    message: str
    metadata_json: dict = Field(default_factory=dict, sa_column=Column("metadata", JSON))
    acknowledged: bool = Field(default=False)
    acknowledged_by: str | None = Field(default=None, max_length=36)
    acknowledged_at: datetime | None = None
    created_at: datetime = Field(default_factory=_utcnow, index=True)
