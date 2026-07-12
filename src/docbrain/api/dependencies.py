from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session, sessionmaker

from docbrain.core.config import Settings
from docbrain.identity.domain import User
from docbrain.identity.repositories import SqlAlchemyUserRepository
from docbrain.identity.tokens import JwtTokenService, TokenVerificationError

bearer_scheme = HTTPBearer(auto_error=False)


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


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    session: Annotated[Session, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> User:
    if credentials is None:
        raise _unauthorized()

    try:
        claims = JwtTokenService(settings).verify_access_token(credentials.credentials)
    except TokenVerificationError as exc:
        raise _unauthorized() from exc

    user = SqlAlchemyUserRepository(session).get_by_id(claims.subject)
    if user is None or not user.is_active:
        raise _unauthorized()
    return user


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
