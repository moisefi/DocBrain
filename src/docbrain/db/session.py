from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from docbrain.core.config import Settings, get_settings


def create_database_engine(settings: Settings | None = None) -> Engine:
    resolved_settings = settings or get_settings()
    return create_engine(resolved_settings.database_url, pool_pre_ping=True)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

