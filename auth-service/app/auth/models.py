import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Farm(SQLModel, table=True):
    __tablename__ = "farms"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        max_length=36,
    )
    name: str = Field(max_length=255, index=True)
    created_at: datetime = Field(default_factory=_utcnow)


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        max_length=36,
    )
    email: str = Field(index=True, unique=True, max_length=255)
    farm_id: str = Field(foreign_key="farms.id", index=True, max_length=36)
    farm_name: str = Field(max_length=255)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=_utcnow)
