from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class CowCreate(BaseModel):
    name: str
    ear_tag: str
    breed: str
    date_of_birth: Optional[date] = None
    weight_kg: Optional[float] = Field(default=None, gt=0)
    notes: Optional[str] = None


class CowUpdate(BaseModel):
    name: Optional[str] = None
    breed: Optional[str] = None
    weight_kg: Optional[float] = Field(default=None, gt=0)
    notes: Optional[str] = None
    collar_id: Optional[str] = None


class CowResponse(CowCreate):
    id: str
    collar_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
