from __future__ import annotations


from datetime import datetime

from pydantic import BaseModel, Field


class GeofenceCreate(BaseModel):
    name: str
    center_latitude: float = Field(ge=-90, le=90)
    center_longitude: float = Field(ge=-180, le=180)
    radius_meters: float = Field(gt=0)
    active: bool = True


class GeofenceUpdate(BaseModel):
    name: str | None = None
    center_latitude: float | None = Field(default=None, ge=-90, le=90)
    center_longitude: float | None = Field(default=None, ge=-180, le=180)
    radius_meters: float | None = Field(default=None, gt=0)
    active: bool | None = None


class GeofenceResponse(BaseModel):
    id: str
    farm_id: str
    name: str
    center_latitude: float
    center_longitude: float
    radius_meters: float
    active: bool
    created_at: datetime
