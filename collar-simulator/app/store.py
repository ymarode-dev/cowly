from __future__ import annotations


import asyncio
import random
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from app.config import settings
from app.models import IdentifyStatus, LedState


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


BREEDS = (
    "Holstein",
    "Jersey",
    "Guernsey",
    "Brown Swiss",
    "Angus",
    "Hereford",
    "Sahiwal",
    "Gir",
)


@dataclass
class CowRecord:
    id: str
    name: str
    ear_tag: str
    breed: str
    date_of_birth: Optional[date]
    weight_kg: Optional[float]
    notes: Optional[str]
    collar_id: Optional[str]
    created_at: datetime


@dataclass
class CollarRecord:
    id: str
    mac_address: str
    cow_id: Optional[str]
    led_state: LedState = LedState.OFF
    battery_percent: float = 100.0
    last_seen_at: datetime = field(default_factory=_utcnow)
    identify_status: IdentifyStatus = IdentifyStatus.IDLE
    identify_target_blinks: int = 0
    identify_completed_blinks: int = 0
    identify_verified_until: Optional[datetime] = None
    _identify_task: Optional[asyncio.Task] = field(default=None, repr=False)


class HerdStore:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self.cows: dict[str, CowRecord] = {}
        self.collars: dict[str, CollarRecord] = {}

    def seed(self, herd_size: int | None = None) -> None:
        size = herd_size or settings.herd_size
        self.cows.clear()
        self.collars.clear()

        for i in range(1, size + 1):
            cow_id = f"COW-{i:03d}"
            collar_id = f"COL-{i:03d}"
            mac = f"AA:BB:CC:{i >> 8 & 0xFF:02X}:{i & 0xFF:02X}:{(i * 7) & 0xFF:02X}"

            self.cows[cow_id] = CowRecord(
                id=cow_id,
                name=f"Cow {i}",
                ear_tag=f"ET-{1000 + i}",
                breed=BREEDS[i % len(BREEDS)],
                date_of_birth=date(2020 + (i % 4), (i % 12) + 1, min((i % 28) + 1, 28)),
                weight_kg=round(400 + (i % 150) + random.random() * 20, 1),
                notes=None,
                collar_id=None,
                created_at=_utcnow(),
            )
            self.collars[collar_id] = CollarRecord(
                id=collar_id,
                mac_address=mac,
                cow_id=None,
                battery_percent=round(85 + random.random() * 15, 1),
                last_seen_at=_utcnow(),
            )

    def is_identify_verified(self, collar: CollarRecord) -> bool:
        if collar.identify_verified_until is None:
            return False
        return _utcnow() <= collar.identify_verified_until

    async def cancel_identify_task(self, collar: CollarRecord) -> None:
        if collar._identify_task and not collar._identify_task.done():
            collar._identify_task.cancel()
            try:
                await collar._identify_task
            except asyncio.CancelledError:
                pass
        collar._identify_task = None


store = HerdStore()
