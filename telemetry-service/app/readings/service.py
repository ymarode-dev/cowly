from __future__ import annotations



import httpx
from sqlmodel import Session, select

from app.config import settings
from app.readings.models import TelemetryReading
from app.readings.schemas import TelemetryIngest, TelemetryReadingResponse


def to_response(reading: TelemetryReading) -> TelemetryReadingResponse:
    return TelemetryReadingResponse(
        id=reading.id,
        farm_id=reading.farm_id,
        collar_id=reading.collar_id,
        cow_id=reading.cow_id,
        latitude=reading.latitude,
        longitude=reading.longitude,
        activity_score=reading.activity_score,
        temperature_c=reading.temperature_c,
        battery_percent=reading.battery_percent,
        recorded_at=reading.recorded_at,
    )


async def trigger_alert_evaluation(
    farm_id: str,
    reading: TelemetryReadingResponse,
) -> None:
    payload = {
        "farm_id": farm_id,
        "collar_id": reading.collar_id,
        "cow_id": reading.cow_id,
        "latitude": reading.latitude,
        "longitude": reading.longitude,
        "activity_score": reading.activity_score,
        "temperature_c": reading.temperature_c,
        "battery_percent": reading.battery_percent,
        "reading_id": reading.id,
    }
    url = f"{settings.alert_service_url}/api/v1/internal/evaluate"
    headers = {"X-Internal-Api-Key": settings.internal_api_key}
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(url, json=payload, headers=headers)
    except httpx.HTTPError:
        pass


def ingest_reading(
    session: Session,
    farm_id: str,
    body: TelemetryIngest,
) -> TelemetryReadingResponse:
    reading = TelemetryReading(farm_id=farm_id, **body.model_dump())
    session.add(reading)
    session.commit()
    session.refresh(reading)
    return to_response(reading)


def latest_for_collar(
    session: Session,
    farm_id: str,
    collar_id: str,
    limit: int,
) -> list[TelemetryReadingResponse]:
    statement = (
        select(TelemetryReading)
        .where(
            TelemetryReading.farm_id == farm_id,
            TelemetryReading.collar_id == collar_id,
        )
        .order_by(TelemetryReading.recorded_at.desc())
        .limit(limit)
    )
    readings = session.exec(statement).all()
    return [to_response(r) for r in reversed(readings)]


def count_readings(session: Session, farm_id: str | None = None) -> int:
    statement = select(TelemetryReading)
    if farm_id:
        statement = statement.where(TelemetryReading.farm_id == farm_id)
    return len(session.exec(statement).all())
