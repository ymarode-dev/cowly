from __future__ import annotations


from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class LedState(str, Enum):
    OFF = "off"
    BLINKING = "blinking"
    SOLID = "solid"


class IdentifyStatus(str, Enum):
    IDLE = "idle"
    BLINKING = "blinking"
    COMPLETED = "completed"
    FAILED = "failed"


class CowBase(BaseModel):
    name: str
    ear_tag: str
    breed: str
    date_of_birth: Optional[date] = None
    weight_kg: Optional[float] = None
    notes: Optional[str] = None


class CowResponse(CowBase):
    id: str
    collar_id: Optional[str] = None
    created_at: datetime


class CollarResponse(BaseModel):
    id: str
    mac_address: str
    assigned: bool
    cow_id: Optional[str] = None
    led_state: LedState
    battery_percent: float
    last_seen_at: datetime


class ScannedCollar(CollarResponse):
    rssi_dbm: int = Field(description="Simulated signal strength; higher is closer.")


class ScanResponse(BaseModel):
    scanned_at: datetime
    collars: list[ScannedCollar]


class IdentifyRequest(BaseModel):
    blinks: int = Field(default=3, ge=2, le=5)


class IdentifyResponse(BaseModel):
    collar_id: str
    status: IdentifyStatus
    target_blinks: int
    completed_blinks: int
    led_state: LedState
    message: str


class IdentifyStatusResponse(BaseModel):
    collar_id: str
    status: IdentifyStatus
    target_blinks: int
    completed_blinks: int
    led_state: LedState
    verified: bool
    verified_until: Optional[datetime] = None


class AssignByCowIdRequest(BaseModel):
    collar_id: str
    cow_id: str
    require_identify: bool = True


class AssignWithCowDataRequest(BaseModel):
    collar_id: str
    cow: CowBase
    require_identify: bool = True


class AssignmentResponse(BaseModel):
    collar_id: str
    cow: CowResponse
    assigned_at: datetime
    message: str


class HealthResponse(BaseModel):
    status: str
    service: str
    herd_size: int
    collars_total: int
    collars_assigned: int
    cows_total: int
    cows_assigned: int
