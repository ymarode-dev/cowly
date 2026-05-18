from __future__ import annotations



import random

from app.config import settings
from app.models import LedState, ScannedCollar
from app.store import CollarRecord, _utcnow, store


def _collar_to_scanned(collar: CollarRecord, rssi: int) -> ScannedCollar:
    return ScannedCollar(
        id=collar.id,
        mac_address=collar.mac_address,
        assigned=collar.cow_id is not None,
        cow_id=collar.cow_id,
        led_state=collar.led_state,
        battery_percent=collar.battery_percent,
        last_seen_at=collar.last_seen_at,
        rssi_dbm=rssi,
    )


def scan_unassigned_collars() -> list[ScannedCollar]:
    """Simulate a BLE scan: unassigned collars in range, sorted by signal strength."""
    now = _utcnow()
    results: list[ScannedCollar] = []

    for collar in store.collars.values():
        if collar.cow_id is not None:
            continue
        collar.last_seen_at = now
        rssi = random.randint(-85, -45)
        results.append(_collar_to_scanned(collar, rssi))

    results.sort(key=lambda c: c.rssi_dbm, reverse=True)
    return results[: settings.scan_max_results]
