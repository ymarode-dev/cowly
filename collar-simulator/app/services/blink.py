from __future__ import annotations

import asyncio
from datetime import timedelta

from app.config import settings
from app.models import IdentifyStatus, LedState
from app.store import CollarRecord, _utcnow, store


async def run_identify_blink(collar_id: str, blinks: int) -> None:
    async with store._lock:
        collar = store.collars.get(collar_id)
        if collar is None:
            return

    interval = settings.identify_blink_interval_ms / 1000.0

    try:
        for n in range(1, blinks + 1):
            async with store._lock:
                collar = store.collars[collar_id]
                collar.led_state = LedState.BLINKING
                collar.identify_completed_blinks = n
            await asyncio.sleep(interval)

            async with store._lock:
                collar = store.collars[collar_id]
                collar.led_state = LedState.OFF
            if n < blinks:
                await asyncio.sleep(interval)

        async with store._lock:
            collar = store.collars[collar_id]
            collar.identify_status = IdentifyStatus.COMPLETED
            collar.led_state = LedState.OFF
            collar.identify_verified_until = _utcnow() + timedelta(
                seconds=settings.identify_session_ttl_seconds
            )
    except asyncio.CancelledError:
        async with store._lock:
            collar = store.collars.get(collar_id)
            if collar:
                collar.identify_status = IdentifyStatus.IDLE
                collar.led_state = LedState.OFF
                collar.identify_completed_blinks = 0
        raise


async def start_identify(collar_id: str, blinks: int) -> CollarRecord:
    async with store._lock:
        collar = store.collars.get(collar_id)
        if collar is None:
            raise KeyError(collar_id)
        if collar.cow_id is not None:
            raise ValueError("Collar is already assigned to a cow")

        await store.cancel_identify_task(collar)
        collar.identify_status = IdentifyStatus.BLINKING
        collar.identify_target_blinks = blinks
        collar.identify_completed_blinks = 0
        collar.identify_verified_until = None
        collar.led_state = LedState.BLINKING
        collar._identify_task = asyncio.create_task(run_identify_blink(collar_id, blinks))
        return collar
