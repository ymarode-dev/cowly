from __future__ import annotations


import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class NotificationChannel(str, Enum):
    PUSH = "push"
    EMAIL = "email"
    SMS = "sms"


class NotificationStatus(str, Enum):
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"


class Notification(SQLModel, table=True):
    __tablename__ = "notifications"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        max_length=36,
    )
    farm_id: str = Field(index=True, max_length=36)
    channel: NotificationChannel
    recipient: str = Field(max_length=255)
    subject: str = Field(max_length=512)
    body: str
    metadata_json: dict = Field(default_factory=dict, sa_column=Column("metadata", JSON))
    status: NotificationStatus = NotificationStatus.QUEUED
    error_message: str | None = None
    created_at: datetime = Field(default_factory=_utcnow, index=True)
