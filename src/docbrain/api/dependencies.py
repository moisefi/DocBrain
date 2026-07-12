from collections.abc import Iterator

from fastapi import Request
from sqlalchemy.orm import Session, sessionmaker


def get_session(request: Request) -> Iterator[Session]:
    session_factory = request.app.state.session_factory
    if not isinstance(session_factory, sessionmaker):
        raise RuntimeError("Application session factory is not configured")

    with session_factory() as session:
        yield session

