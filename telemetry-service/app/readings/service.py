from sqlmodel import Session, select

from app.readings.models import TelemetryReading
from app.readings.schemas import TelemetryIngest, TelemetryReadingResponse


def to_response(reading: TelemetryReading) -> TelemetryReadingResponse:
    return TelemetryReadingResponse(
        id=reading.id,
        collar_id=reading.collar_id,
        cow_id=reading.cow_id,
        latitude=reading.latitude,
        longitude=reading.longitude,
        activity_score=reading.activity_score,
        temperature_c=reading.temperature_c,
        battery_percent=reading.battery_percent,
        recorded_at=reading.recorded_at,
    )


def ingest_reading(session: Session, body: TelemetryIngest) -> TelemetryReadingResponse:
    reading = TelemetryReading(**body.model_dump())
    session.add(reading)
    session.commit()
    session.refresh(reading)
    return to_response(reading)


def latest_for_collar(
    session: Session,
    collar_id: str,
    limit: int,
) -> list[TelemetryReadingResponse]:
    statement = (
        select(TelemetryReading)
        .where(TelemetryReading.collar_id == collar_id)
        .order_by(TelemetryReading.recorded_at.desc())
        .limit(limit)
    )
    readings = session.exec(statement).all()
    return [to_response(r) for r in reversed(readings)]


def count_readings(session: Session) -> int:
    return len(session.exec(select(TelemetryReading)).all())
