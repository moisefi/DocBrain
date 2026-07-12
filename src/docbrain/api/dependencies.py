from collections.abc import Iterator

from fastapi import Request
from sqlalchemy.orm import Session, sessionmaker

from docbrain.core.config import Settings


def get_session(request: Request) -> Iterator[Session]:
    session_factory = request.app.state.session_factory
    if not isinstance(session_factory, sessionmaker):
        raise RuntimeError("Application session factory is not configured")

    with session_factory() as session:
        yield session


def get_app_settings(request: Request) -> Settings:
    settings = request.app.state.settings
    if not isinstance(settings, Settings):
        raise RuntimeError("Application settings are not configured")
    return settings
