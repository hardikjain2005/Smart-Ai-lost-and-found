from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


_url = get_settings().database_url
if _url.startswith("sqlite"):  # used by the test-suite only
    engine = create_engine(
        _url, connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
else:
    engine = create_engine(_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
