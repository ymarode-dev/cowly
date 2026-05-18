from __future__ import annotations


import logging
import smtplib
from email.message import EmailMessage

from app.config import settings
from app.notifications.models import NotificationChannel

logger = logging.getLogger(__name__)


class DeliveryError(Exception):
    pass


def deliver_email(recipient: str, subject: str, body: str) -> None:
    if not settings.smtp_enabled:
        logger.info(
            "SMTP disabled — logging email to %s: %s",
            recipient,
            subject,
        )
        return

    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    if settings.smtp_use_tls:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
            smtp.starttls()
            if settings.smtp_username:
                smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(message)
    else:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
            if settings.smtp_username:
                smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(message)


def deliver_notification(
    channel: NotificationChannel,
    recipient: str,
    subject: str,
    body: str,
) -> None:
    if channel == NotificationChannel.EMAIL:
        deliver_email(recipient, subject, body)
        return
    if channel == NotificationChannel.PUSH:
        logger.info("Push delivery stub — would notify %s: %s", recipient, subject)
        return
    if channel == NotificationChannel.SMS:
        logger.info("SMS delivery stub — would text %s: %s", recipient, body[:80])
        return
    raise DeliveryError(f"Unsupported channel: {channel}")
