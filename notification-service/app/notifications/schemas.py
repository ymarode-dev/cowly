from datetime import datetime

from pydantic import BaseModel, Field

from app.notifications.models import NotificationChannel, NotificationStatus


class NotificationCreate(BaseModel):
    channel: NotificationChannel
    recipient: str
    subject: str
    body: str
    metadata: dict = Field(default_factory=dict)


class NotificationResponse(NotificationCreate):
    id: str
    status: NotificationStatus
    created_at: datetime
