from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.alerts.models import AlertSeverity, AlertType


class AlertCreate(BaseModel):
    cow_id: Optional[str] = None
    collar_id: str
    alert_type: AlertType
    severity: AlertSeverity = AlertSeverity.WARNING
    message: str
    metadata: dict = Field(default_factory=dict)


class TelemetryEvaluate(BaseModel):
    farm_id: str
    collar_id: str
    cow_id: Optional[str] = None
    latitude: float
    longitude: float
    activity_score: float
    temperature_c: Optional[float] = None
    battery_percent: Optional[float] = None
    reading_id: Optional[str] = None


class AlertResponse(BaseModel):
    id: str
    farm_id: str
    cow_id: Optional[str] = None
    collar_id: str
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    metadata: dict
    acknowledged: bool
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime
