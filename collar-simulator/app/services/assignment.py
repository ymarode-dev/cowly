from __future__ import annotations

from app.models import CowBase
from app.store import CowRecord, _utcnow, store


class AssignmentError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


async def assign_collar_to_cow(
    collar_id: str,
    cow_id: str,
    *,
    require_identify: bool = True,
) -> tuple[CowRecord, str]:
    async with store._lock:
        collar = store.collars.get(collar_id)
        if collar is None:
            raise AssignmentError(f"Collar '{collar_id}' not found", 404)

        cow = store.cows.get(cow_id)
        if cow is None:
            raise AssignmentError(f"Cow '{cow_id}' not found", 404)

        if collar.cow_id is not None:
            raise AssignmentError(
                f"Collar '{collar_id}' is already assigned to cow '{collar.cow_id}'",
                409,
            )
        if cow.collar_id is not None:
            raise AssignmentError(
                f"Cow '{cow_id}' already has collar '{cow.collar_id}'",
                409,
            )
        if require_identify and not store.is_identify_verified(collar):
            raise AssignmentError(
                "Collar must be identified first (blink LED 2–3 times via POST /collars/{id}/identify)",
                428,
            )

        assigned_at = _utcnow()
        collar.cow_id = cow_id
        cow.collar_id = collar_id
        await store.cancel_identify_task(collar)
        collar.identify_verified_until = None

        return cow, assigned_at.isoformat()


async def assign_collar_with_cow_data(
    collar_id: str,
    cow_data: CowBase,
    *,
    require_identify: bool = True,
) -> tuple[CowRecord, str]:
    """Create a new cow record and link it to the collar."""
    async with store._lock:
        collar = store.collars.get(collar_id)
        if collar is None:
            raise AssignmentError(f"Collar '{collar_id}' not found", 404)
        if collar.cow_id is not None:
            raise AssignmentError(
                f"Collar '{collar_id}' is already assigned to cow '{collar.cow_id}'",
                409,
            )
        if require_identify and not store.is_identify_verified(collar):
            raise AssignmentError(
                "Collar must be identified first (blink LED 2–3 times via POST /collars/{id}/identify)",
                428,
            )

        next_num = len(store.cows) + 1
        cow_id = f"COW-NEW-{next_num:03d}"
        assigned_at = _utcnow()

        cow = CowRecord(
            id=cow_id,
            name=cow_data.name,
            ear_tag=cow_data.ear_tag,
            breed=cow_data.breed,
            date_of_birth=cow_data.date_of_birth,
            weight_kg=cow_data.weight_kg,
            notes=cow_data.notes,
            collar_id=collar_id,
            created_at=assigned_at,
        )
        store.cows[cow_id] = cow
        collar.cow_id = cow_id
        await store.cancel_identify_task(collar)
        collar.identify_verified_until = None

        return cow, assigned_at.isoformat()
