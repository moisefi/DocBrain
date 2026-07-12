from dataclasses import dataclass, field
from uuid import uuid4

import pytest

from docbrain.core.config import Settings
from docbrain.identity.domain import User, UserId
from docbrain.identity.passwords import PasswordHash, PasswordService
from docbrain.identity.tokens import JwtTokenService
from docbrain.identity.use_cases import (
    InvalidCredentialsError,
    LoginCommand,
    LoginUseCase,
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
        password_service=password_service,
        token_service=_token_service(),
    )

    result = use_case.execute(
        LoginCommand(
            email=" Sergio@Example.com ",
            password="correct horse battery staple",
        ),
    )

    assert result.user == user
    assert result.access_token.value


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
        password_service=password_service,
        token_service=_token_service(),
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
        password_service=password_service,
        token_service=_token_service(),
    )

    with pytest.raises(InvalidCredentialsError):
        use_case.execute(
            LoginCommand(
                email="sergio@example.com",
                password="correct horse battery staple",
            ),
        )


@dataclass
class FakeUsers:
    items: list[User] = field(default_factory=list)

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


def _use_case() -> LoginUseCase:
    return LoginUseCase(
        users=FakeUsers(),
        password_credentials=FakePasswordCredentials(),
        password_service=PasswordService(),
        token_service=_token_service(),
    )


def _token_service() -> JwtTokenService:
    return JwtTokenService(
        Settings(jwt_secret="test-secret-with-enough-length-32b"),
    )
