from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TelemetryIngest(BaseModel):
    collar_id: str
    cow_id: Optional[str] = None
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    activity_score: float = Field(ge=0, le=100)
    temperature_c: Optional[float] = None
    battery_percent: Optional[float] = Field(default=None, ge=0, le=100)


class TelemetryReadingResponse(TelemetryIngest):
    id: str
    recorded_at: datetime
