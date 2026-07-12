from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from secrets import token_urlsafe
from uuid import UUID, uuid4

from docbrain.core.config import Settings, get_settings
from docbrain.identity.domain import UserId


@dataclass(frozen=True, slots=True)
class RefreshToken:
    value: str
    token_id: UUID
    family_id: UUID
    user_id: UserId
    expires_at: datetime


class RefreshTokenService:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def issue(self, user_id: UserId, family_id: UUID | None = None) -> RefreshToken:
        expires_at = datetime.now(UTC) + timedelta(
            seconds=self._settings.refresh_token_ttl_seconds,
        )
        return RefreshToken(
            value=token_urlsafe(48),
            token_id=uuid4(),
            family_id=family_id or uuid4(),
            user_id=user_id,
            expires_at=expires_at,
        )

    def hash(self, token: str) -> str:
        return sha256(token.encode("utf-8")).hexdigest()

