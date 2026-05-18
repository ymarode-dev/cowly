from __future__ import annotations



from sqlmodel import Session, select

from app.alerts.models import Alert, AlertSeverity, AlertType
from app.alerts.schemas import AlertCreate, TelemetryEvaluate
from app.config import settings
from app.geofences.models import Geofence
from app.geofences.service import is_inside_geofence


def _recent_duplicate(
    session: Session,
    farm_id: str,
    collar_id: str,
    alert_type: AlertType,
    window_minutes: int = 30,
) -> bool:
    from datetime import datetime, timedelta, timezone

    cutoff = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
    existing = session.exec(
        select(Alert).where(
            Alert.farm_id == farm_id,
            Alert.collar_id == collar_id,
            Alert.alert_type == alert_type,
            Alert.created_at >= cutoff,
            Alert.acknowledged == False,  # noqa: E712
        )
    ).first()
    return existing is not None


def evaluate_telemetry(
    session: Session,
    body: TelemetryEvaluate,
) -> list[AlertCreate]:
    candidates: list[AlertCreate] = []

    if body.battery_percent is not None and body.battery_percent < settings.low_battery_threshold:
        candidates.append(
            AlertCreate(
                cow_id=body.cow_id,
                collar_id=body.collar_id,
                alert_type=AlertType.LOW_BATTERY,
                severity=AlertSeverity.WARNING,
                message=f"Collar battery at {body.battery_percent:.0f}% (below {settings.low_battery_threshold:.0f}%)",
                metadata={"battery_percent": body.battery_percent, "reading_id": body.reading_id},
            )
        )

    if (
        body.temperature_c is not None
        and body.temperature_c > settings.high_temperature_threshold
    ):
        candidates.append(
            AlertCreate(
                cow_id=body.cow_id,
                collar_id=body.collar_id,
                alert_type=AlertType.HIGH_TEMPERATURE,
                severity=AlertSeverity.CRITICAL,
                message=(
                    f"Temperature {body.temperature_c:.1f}°C exceeds "
                    f"{settings.high_temperature_threshold:.1f}°C"
                ),
                metadata={"temperature_c": body.temperature_c, "reading_id": body.reading_id},
            )
        )

    if body.activity_score < settings.inactivity_threshold:
        candidates.append(
            AlertCreate(
                cow_id=body.cow_id,
                collar_id=body.collar_id,
                alert_type=AlertType.INACTIVITY,
                severity=AlertSeverity.INFO,
                message=f"Low activity score {body.activity_score:.0f}",
                metadata={"activity_score": body.activity_score, "reading_id": body.reading_id},
            )
        )

    geofences = session.exec(
        select(Geofence).where(
            Geofence.farm_id == body.farm_id,
            Geofence.active == True,  # noqa: E712
        )
    ).all()

    if geofences:
        inside_any = any(
            is_inside_geofence(body.latitude, body.longitude, g) for g in geofences
        )
        if not inside_any:
            candidates.append(
                AlertCreate(
                    cow_id=body.cow_id,
                    collar_id=body.collar_id,
                    alert_type=AlertType.GEOFENCE_EXIT,
                    severity=AlertSeverity.WARNING,
                    message="Animal left all active geofence zones",
                    metadata={
                        "latitude": body.latitude,
                        "longitude": body.longitude,
                        "reading_id": body.reading_id,
                    },
                )
            )

    deduped: list[AlertCreate] = []
    for alert in candidates:
        if not _recent_duplicate(session, body.farm_id, body.collar_id, alert.alert_type):
            deduped.append(alert)
    return deduped
