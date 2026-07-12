from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import jwt
from jwt import InvalidTokenError

from docbrain.core.config import Settings, get_settings
from docbrain.identity.domain import UserId


@dataclass(frozen=True, slots=True)
class AccessToken:
    value: str
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class AccessTokenClaims:
    subject: UserId
    issued_at: datetime
    expires_at: datetime
    issuer: str


class JwtTokenService:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def issue_access_token(self, user_id: UserId) -> AccessToken:
        issued_at = datetime.now(UTC)
        expires_at = issued_at + timedelta(
            seconds=self._settings.access_token_ttl_seconds,
        )
        payload = {
            "sub": str(user_id.value),
            "iat": issued_at,
            "exp": expires_at,
            "iss": self._settings.jwt_issuer,
            "typ": "access",
        }
        token = jwt.encode(
            payload,
            self._settings.jwt_secret,
            algorithm="HS256",
        )
        return AccessToken(value=token, expires_at=expires_at)

    def verify_access_token(self, token: str) -> AccessTokenClaims:
        try:
            payload = jwt.decode(
                token,
                self._settings.jwt_secret,
                algorithms=["HS256"],
                issuer=self._settings.jwt_issuer,
                options={"require": ["sub", "iat", "exp", "iss", "typ"]},
            )
        except InvalidTokenError as exc:
            raise TokenVerificationError from exc

        if payload.get("typ") != "access":
            raise TokenVerificationError

        subject = payload.get("sub")
        issued_at = _require_timestamp(payload.get("iat"))
        expires_at = _require_timestamp(payload.get("exp"))
        if not isinstance(subject, str):
            raise TokenVerificationError

        return AccessTokenClaims(
            subject=UserId(UUID(subject)),
            issued_at=datetime.fromtimestamp(issued_at, UTC),
            expires_at=datetime.fromtimestamp(expires_at, UTC),
            issuer=self._settings.jwt_issuer,
        )


class TokenVerificationError(ValueError):
    """Raised when a JWT cannot be trusted."""


def _require_timestamp(value: Any) -> float:
    if not isinstance(value, int | float):
        raise TokenVerificationError
    return float(value)
