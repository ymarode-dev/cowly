from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.config import settings
from app.readings.models import TelemetryReading  # noqa: F401

engine = create_engine(settings.database_url, echo=settings.db_echo, pool_pre_ping=True)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
