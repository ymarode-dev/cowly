from app.models import CollarResponse, CowResponse
from app.store import CollarRecord, CowRecord


def cow_to_response(cow: CowRecord) -> CowResponse:
    return CowResponse(
        id=cow.id,
        name=cow.name,
        ear_tag=cow.ear_tag,
        breed=cow.breed,
        date_of_birth=cow.date_of_birth,
        weight_kg=cow.weight_kg,
        notes=cow.notes,
        collar_id=cow.collar_id,
        created_at=cow.created_at,
    )


def collar_to_response(collar: CollarRecord) -> CollarResponse:
    return CollarResponse(
        id=collar.id,
        mac_address=collar.mac_address,
        assigned=collar.cow_id is not None,
        cow_id=collar.cow_id,
        led_state=collar.led_state,
        battery_percent=collar.battery_percent,
        last_seen_at=collar.last_seen_at,
    )
