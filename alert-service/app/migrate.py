from pathlib import Path

from alembic import command
from alembic.config import Config


def run_migrations() -> None:
    root = Path(__file__).resolve().parent.parent
    cfg = Config(str(root / "alembic.ini"))
    command.upgrade(cfg, "head")
