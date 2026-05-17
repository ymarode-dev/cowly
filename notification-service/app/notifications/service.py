from sqlmodel import Session, select

from app.notifications.models import Notification, NotificationStatus
from app.notifications.schemas import NotificationCreate, NotificationResponse


def to_response(record: Notification) -> NotificationResponse:
    return NotificationResponse(
        id=record.id,
        channel=record.channel,
        recipient=record.recipient,
        subject=record.subject,
        body=record.body,
        metadata=record.metadata_json,
        status=record.status,
        created_at=record.created_at,
    )


def list_notifications(session: Session) -> list[NotificationResponse]:
    records = session.exec(
        select(Notification).order_by(Notification.created_at.desc())
    ).all()
    return [to_response(n) for n in records]


def send_notification(
    session: Session,
    body: NotificationCreate,
) -> NotificationResponse:
    record = Notification(
        channel=body.channel,
        recipient=body.recipient,
        subject=body.subject,
        body=body.body,
        metadata_json=body.metadata,
        status=NotificationStatus.SENT,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return to_response(record)


def count_notifications(session: Session) -> int:
    return len(session.exec(select(Notification)).all())
