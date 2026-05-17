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


class AlertResponse(BaseModel):
    id: str
    cow_id: Optional[str] = None
    collar_id: str
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    metadata: dict
    acknowledged: bool
    created_at: datetime
