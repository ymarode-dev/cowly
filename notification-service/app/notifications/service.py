from __future__ import annotations


from sqlmodel import Session, select

from app.delivery import DeliveryError, deliver_notification
from app.notifications.models import Notification, NotificationStatus
from app.notifications.schemas import NotificationCreate, NotificationResponse


def to_response(record: Notification) -> NotificationResponse:
    return NotificationResponse(
        id=record.id,
        farm_id=record.farm_id,
        channel=record.channel,
        recipient=record.recipient,
        subject=record.subject,
        body=record.body,
        metadata=record.metadata_json,
        status=record.status,
        error_message=record.error_message,
        created_at=record.created_at,
    )


def list_notifications(session: Session, farm_id: str) -> list[NotificationResponse]:
    records = session.exec(
        select(Notification)
        .where(Notification.farm_id == farm_id)
        .order_by(Notification.created_at.desc())
    ).all()
    return [to_response(n) for n in records]


def send_notification(
    session: Session,
    farm_id: str,
    body: NotificationCreate,
) -> NotificationResponse:
    record = Notification(
        farm_id=farm_id,
        channel=body.channel,
        recipient=body.recipient,
        subject=body.subject,
        body=body.body,
        metadata_json=body.metadata,
        status=NotificationStatus.QUEUED,
    )
    session.add(record)
    session.flush()

    try:
        deliver_notification(
            record.channel,
            record.recipient,
            record.subject,
            record.body,
        )
        record.status = NotificationStatus.SENT
    except (DeliveryError, OSError) as exc:
        record.status = NotificationStatus.FAILED
        record.error_message = str(exc)

    session.add(record)
    session.commit()
    session.refresh(record)
    return to_response(record)


def count_notifications(session: Session, farm_id: str | None = None) -> int:
    statement = select(Notification)
    if farm_id:
        statement = statement.where(Notification.farm_id == farm_id)
    return len(session.exec(statement).all())
