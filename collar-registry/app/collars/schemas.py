from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.collars.models import CollarStatus


class CollarRegister(BaseModel):
    mac_address: str
    firmware_version: Optional[str] = None


class CollarResponse(BaseModel):
    id: str
    mac_address: str
    status: CollarStatus
    cow_id: Optional[str] = None
    firmware_version: Optional[str] = None
    registered_at: datetime
