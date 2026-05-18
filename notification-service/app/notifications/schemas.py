from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.notifications.models import NotificationChannel, NotificationStatus


class NotificationCreate(BaseModel):
    farm_id: Optional[str] = None
    channel: NotificationChannel
    recipient: str
    subject: str
    body: str
    metadata: dict = Field(default_factory=dict)


class NotificationResponse(BaseModel):
    id: str
    farm_id: str
    channel: NotificationChannel
    recipient: str
    subject: str
    body: str
    metadata: dict
    status: NotificationStatus
    error_message: Optional[str] = None
    created_at: datetime
