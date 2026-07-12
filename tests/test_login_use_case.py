from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest

from docbrain.core.config import Settings
from docbrain.identity.domain import User, UserId
from docbrain.identity.passwords import PasswordHash, PasswordService
from docbrain.identity.refresh_tokens import RefreshTokenRecord, RefreshTokenService
from docbrain.identity.tokens import JwtTokenService
from docbrain.identity.use_cases import (
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    LoginCommand,
    LoginUseCase,
    LogoutCommand,
    LogoutUseCase,
    RefreshSessionCommand,
    RefreshSessionUseCase,
)


def test_login_returns_access_token_for_valid_credentials() -> None:
    password_service = PasswordService()
    user = User(UserId(uuid4()), "sergio@example.com", "Sergio")
    password_hash = password_service.hash_password("correct horse battery staple")
    credentials = FakePasswordCredentials(
        hashes={user.id: password_hash},
    )
    use_case = LoginUseCase(
        users=FakeUsers([user]),
        password_credentials=credentials,
        refresh_tokens=FakeRefreshTokens(),
        password_service=password_service,
        token_service=_token_service(),
        refresh_token_service=_refresh_token_service(),
    )

    result = use_case.execute(
        LoginCommand(
            email=" Sergio@Example.com ",
            password="correct horse battery staple",
        ),
    )

    assert result.user == user
    assert result.access_token.value
    assert result.refresh_token.value


def test_login_rejects_unknown_email() -> None:
    use_case = _use_case()

    with pytest.raises(InvalidCredentialsError):
        use_case.execute(
            LoginCommand(
                email="missing@example.com",
                password="correct horse battery staple",
            ),
        )


def test_login_rejects_wrong_password() -> None:
    password_service = PasswordService()
    user = User(UserId(uuid4()), "sergio@example.com", "Sergio")
    password_hash = password_service.hash_password("correct horse battery staple")
    use_case = LoginUseCase(
        users=FakeUsers([user]),
        password_credentials=FakePasswordCredentials(
            hashes={user.id: password_hash},
        ),
        refresh_tokens=FakeRefreshTokens(),
        password_service=password_service,
        token_service=_token_service(),
        refresh_token_service=_refresh_token_service(),
    )

    with pytest.raises(InvalidCredentialsError):
        use_case.execute(
            LoginCommand(
                email="sergio@example.com",
                password="wrong horse battery staple",
            ),
        )


def test_login_rejects_inactive_user() -> None:
    password_service = PasswordService()
    user = User(UserId(uuid4()), "sergio@example.com", "Sergio", is_active=False)
    password_hash = password_service.hash_password("correct horse battery staple")
    use_case = LoginUseCase(
        users=FakeUsers([user]),
        password_credentials=FakePasswordCredentials(
            hashes={user.id: password_hash},
        ),
        refresh_tokens=FakeRefreshTokens(),
        password_service=password_service,
        token_service=_token_service(),
        refresh_token_service=_refresh_token_service(),
    )

    with pytest.raises(InvalidCredentialsError):
        use_case.execute(
            LoginCommand(
                email="sergio@example.com",
                password="correct horse battery staple",
            ),
        )


def test_refresh_session_rotates_refresh_token() -> None:
    user = User(UserId(uuid4()), "sergio@example.com", "Sergio")
    refresh_token_service = _refresh_token_service()
    old_refresh_token = refresh_token_service.issue(user.id)
    refresh_tokens = FakeRefreshTokens()
    refresh_tokens.records[
        refresh_token_service.hash(old_refresh_token.value)
    ] = RefreshTokenRecord(
        token_id=old_refresh_token.token_id,
        family_id=old_refresh_token.family_id,
        user_id=user.id,
        token_hash=refresh_token_service.hash(old_refresh_token.value),
        expires_at=datetime.now(UTC) + timedelta(days=1),
        used_at=None,
        revoked_at=None,
        family_revoked_at=None,
    )
    use_case = RefreshSessionUseCase(
        users=FakeUsers([user]),
        refresh_tokens=refresh_tokens,
        token_service=_token_service(),
        refresh_token_service=refresh_token_service,
    )

    result = use_case.execute(RefreshSessionCommand(old_refresh_token.value))

    assert result.user == user
    assert result.access_token.value
    assert result.refresh_token.value != old_refresh_token.value
    assert refresh_tokens.used_tokens == [
        (old_refresh_token.token_id, result.refresh_token.token_id),
    ]


def test_refresh_session_revokes_family_when_used_token_is_reused() -> None:
    user = User(UserId(uuid4()), "sergio@example.com", "Sergio")
    refresh_token_service = _refresh_token_service()
    refresh_token = refresh_token_service.issue(user.id)
    refresh_tokens = FakeRefreshTokens()
    refresh_tokens.records[refresh_token_service.hash(refresh_token.value)] = (
        RefreshTokenRecord(
            token_id=refresh_token.token_id,
            family_id=refresh_token.family_id,
            user_id=user.id,
            token_hash=refresh_token_service.hash(refresh_token.value),
            expires_at=datetime.now(UTC) + timedelta(days=1),
            used_at=datetime.now(UTC),
            revoked_at=None,
            family_revoked_at=None,
        )
    )
    use_case = RefreshSessionUseCase(
        users=FakeUsers([user]),
        refresh_tokens=refresh_tokens,
        token_service=_token_service(),
        refresh_token_service=refresh_token_service,
    )

    with pytest.raises(InvalidRefreshTokenError):
        use_case.execute(RefreshSessionCommand(refresh_token.value))

    assert refresh_tokens.revoked_families == [refresh_token.family_id]


def test_logout_revokes_refresh_token_family() -> None:
    user = User(UserId(uuid4()), "sergio@example.com", "Sergio")
    refresh_token_service = _refresh_token_service()
    refresh_token = refresh_token_service.issue(user.id)
    refresh_tokens = FakeRefreshTokens()
    refresh_tokens.records[refresh_token_service.hash(refresh_token.value)] = (
        RefreshTokenRecord(
            token_id=refresh_token.token_id,
            family_id=refresh_token.family_id,
            user_id=user.id,
            token_hash=refresh_token_service.hash(refresh_token.value),
            expires_at=datetime.now(UTC) + timedelta(days=1),
            used_at=None,
            revoked_at=None,
            family_revoked_at=None,
        )
    )
    use_case = LogoutUseCase(
        refresh_tokens=refresh_tokens,
        refresh_token_service=refresh_token_service,
    )

    use_case.execute(LogoutCommand(refresh_token.value))

    assert refresh_tokens.revoked_families == [refresh_token.family_id]


@dataclass
class FakeUsers:
    items: list[User] = field(default_factory=list)

    def get_by_id(self, user_id: UserId) -> User | None:
        return next((user for user in self.items if user.id == user_id), None)

    def get_by_email(self, email: str) -> User | None:
        return next((user for user in self.items if user.email == email), None)

    def add(self, user: User) -> None:
        self.items.append(user)


@dataclass
class FakePasswordCredentials:
    hashes: dict[UserId, PasswordHash] = field(default_factory=dict)

    def add(self, user_id: UserId, password_hash: PasswordHash) -> None:
        self.hashes[user_id] = password_hash

    def get_by_user_id(self, user_id: UserId) -> PasswordHash | None:
        return self.hashes.get(user_id)


@dataclass
class FakeRefreshTokens:
    families: list[object] = field(default_factory=list)
    tokens: list[str] = field(default_factory=list)
    records: dict[str, RefreshTokenRecord] = field(default_factory=dict)
    used_tokens: list[tuple[UUID, UUID]] = field(default_factory=list)
    revoked_tokens: list[UUID] = field(default_factory=list)
    revoked_families: list[UUID] = field(default_factory=list)

    def add_family(self, family_id: object, user_id: UserId) -> None:
        self.families.append((family_id, user_id))

    def add_token(
        self,
        *,
        token_id: object,
        family_id: object,
        user_id: UserId,
        token_hash: str,
        expires_at: object,
    ) -> None:
        self.tokens.append(token_hash)

    def get_record_by_hash(self, token_hash: str) -> RefreshTokenRecord | None:
        return self.records.get(token_hash)

    def mark_used(self, token_id: UUID, replaced_by_token_id: UUID) -> None:
        self.used_tokens.append((token_id, replaced_by_token_id))

    def revoke_token(self, token_id: UUID) -> None:
        self.revoked_tokens.append(token_id)

    def revoke_family(self, family_id: UUID) -> None:
        self.revoked_families.append(family_id)


def _use_case() -> LoginUseCase:
    return LoginUseCase(
        users=FakeUsers(),
        password_credentials=FakePasswordCredentials(),
        refresh_tokens=FakeRefreshTokens(),
        password_service=PasswordService(),
        token_service=_token_service(),
        refresh_token_service=_refresh_token_service(),
    )


def _token_service() -> JwtTokenService:
    return JwtTokenService(
        Settings(jwt_secret="test-secret-with-enough-length-32b"),
    )


def _refresh_token_service() -> RefreshTokenService:
    return RefreshTokenService(
        Settings(jwt_secret="test-secret-with-enough-length-32b"),
    )
