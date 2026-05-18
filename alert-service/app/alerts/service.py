from __future__ import annotations



from datetime import datetime, timezone

import httpx
from sqlmodel import Session, select

from app.alerts.evaluate import evaluate_telemetry
from app.alerts.models import Alert
from app.alerts.schemas import AlertCreate, AlertResponse, TelemetryEvaluate
from app.config import settings


class AlertNotFoundError(Exception):
    pass


def to_response(alert: Alert) -> AlertResponse:
    return AlertResponse(
        id=alert.id,
        farm_id=alert.farm_id,
        cow_id=alert.cow_id,
        collar_id=alert.collar_id,
        alert_type=alert.alert_type,
        severity=alert.severity,
        message=alert.message,
        metadata=alert.metadata_json,
        acknowledged=alert.acknowledged,
        acknowledged_by=alert.acknowledged_by,
        acknowledged_at=alert.acknowledged_at,
        created_at=alert.created_at,
    )


def list_alerts(
    session: Session,
    farm_id: str,
    open_only: bool = False,
) -> list[AlertResponse]:
    statement = (
        select(Alert)
        .where(Alert.farm_id == farm_id)
        .order_by(Alert.created_at.desc())
    )
    alerts = session.exec(statement).all()
    if open_only:
        alerts = [a for a in alerts if not a.acknowledged]
    return [to_response(a) for a in alerts]


def create_alert(session: Session, farm_id: str, body: AlertCreate) -> AlertResponse:
    alert = Alert(
        farm_id=farm_id,
        cow_id=body.cow_id,
        collar_id=body.collar_id,
        alert_type=body.alert_type,
        severity=body.severity,
        message=body.message,
        metadata_json=body.metadata,
    )
    session.add(alert)
    session.commit()
    session.refresh(alert)
    return to_response(alert)


def acknowledge_alert(
    session: Session,
    farm_id: str,
    alert_id: str,
    user_id: str,
) -> AlertResponse:
    alert = session.get(Alert, alert_id)
    if not alert or alert.farm_id != farm_id:
        raise AlertNotFoundError("Alert not found")
    alert.acknowledged = True
    alert.acknowledged_by = user_id
    alert.acknowledged_at = datetime.now(timezone.utc)
    session.add(alert)
    session.commit()
    session.refresh(alert)
    return to_response(alert)


def count_alerts(session: Session, farm_id: str | None = None) -> tuple[int, int]:
    statement = select(Alert)
    if farm_id:
        statement = statement.where(Alert.farm_id == farm_id)
    alerts = session.exec(statement).all()
    open_count = sum(1 for a in alerts if not a.acknowledged)
    return len(alerts), open_count


async def notify_farmer(alert: AlertResponse) -> None:
    payload = {
        "farm_id": alert.farm_id,
        "channel": "email",
        "recipient": settings.default_notification_recipient,
        "subject": f"[{alert.severity.value}] {alert.alert_type.value}",
        "body": alert.message,
        "metadata": {
            "alert_id": alert.id,
            "collar_id": alert.collar_id,
            "cow_id": alert.cow_id,
        },
    }
    url = f"{settings.notification_service_url}/api/v1/notifications"
    headers = {"X-Internal-Api-Key": settings.internal_api_key}
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(url, json=payload, headers=headers)
    except httpx.HTTPError:
        pass


async def process_telemetry_evaluation(
    session: Session,
    body: TelemetryEvaluate,
) -> list[AlertResponse]:
    created: list[AlertResponse] = []
    for candidate in evaluate_telemetry(session, body):
        response = create_alert(session, body.farm_id, candidate)
        await notify_farmer(response)
        created.append(response)
    return created
