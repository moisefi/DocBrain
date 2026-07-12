from dataclasses import dataclass
from typing import Protocol
from uuid import uuid4

from docbrain.identity.domain import User, UserId
from docbrain.identity.passwords import PasswordHash, PasswordService
from docbrain.identity.tokens import AccessToken, JwtTokenService
from docbrain.organizations.domain import (
    Membership,
    Organization,
    OrganizationId,
    OrganizationRole,
)


class UserRepository(Protocol):
    def get_by_id(self, user_id: UserId) -> User | None: ...

    def get_by_email(self, email: str) -> User | None: ...

    def add(self, user: User) -> None: ...


class PasswordCredentialRepository(Protocol):
    def add(self, user_id: UserId, password_hash: PasswordHash) -> None: ...

    def get_by_user_id(self, user_id: UserId) -> PasswordHash | None: ...


class OrganizationRepository(Protocol):
    def add(self, organization: Organization) -> None: ...


class MembershipRepository(Protocol):
    def add(self, membership: Membership) -> None: ...


@dataclass(frozen=True, slots=True)
class RegisterUserCommand:
    email: str
    password: str
    organization_name: str
    display_name: str | None = None


@dataclass(frozen=True, slots=True)
class RegisterUserResult:
    user: User
    organization: Organization
    membership: Membership


class RegisterUserUseCase:
    def __init__(
        self,
        *,
        users: UserRepository,
        password_credentials: PasswordCredentialRepository,
        organizations: OrganizationRepository,
        memberships: MembershipRepository,
        password_service: PasswordService,
    ) -> None:
        self._users = users
        self._password_credentials = password_credentials
        self._organizations = organizations
        self._memberships = memberships
        self._password_service = password_service

    def execute(self, command: RegisterUserCommand) -> RegisterUserResult:
        email = _normalize_email(command.email)
        if self._users.get_by_email(email) is not None:
            raise EmailAlreadyRegisteredError(email)

        user = User(
            id=UserId(uuid4()),
            email=email,
            display_name=command.display_name,
        )
        organization = Organization(
            id=OrganizationId(uuid4()),
            name=command.organization_name.strip(),
            slug=_slugify(command.organization_name),
        )
        membership = Membership(
            user_id=user.id,
            organization_id=organization.id,
            role=OrganizationRole.OWNER,
        )
        password_hash = self._password_service.hash_password(command.password)

        self._users.add(user)
        self._organizations.add(organization)
        self._memberships.add(membership)
        self._password_credentials.add(user.id, password_hash)

        return RegisterUserResult(
            user=user,
            organization=organization,
            membership=membership,
        )


class EmailAlreadyRegisteredError(ValueError):
    def __init__(self, email: str) -> None:
        super().__init__(f"Email already registered: {email}")
        self.email = email


def _normalize_email(email: str) -> str:
    normalized = email.strip().lower()
    if "@" not in normalized:
        raise InvalidEmailError(email)
    return normalized


def _slugify(value: str) -> str:
    slug = "-".join(value.strip().lower().split())
    if not slug:
        raise InvalidOrganizationNameError
    return slug


class InvalidEmailError(ValueError):
    """Raised when an email address is not valid enough for registration."""


class InvalidOrganizationNameError(ValueError):
    """Raised when an organization name cannot produce a usable slug."""


@dataclass(frozen=True, slots=True)
class LoginCommand:
    email: str
    password: str


@dataclass(frozen=True, slots=True)
class LoginResult:
    user: User
    access_token: AccessToken


class LoginUseCase:
    def __init__(
        self,
        *,
        users: UserRepository,
        password_credentials: PasswordCredentialRepository,
        password_service: PasswordService,
        token_service: JwtTokenService,
    ) -> None:
        self._users = users
        self._password_credentials = password_credentials
        self._password_service = password_service
        self._token_service = token_service

    def execute(self, command: LoginCommand) -> LoginResult:
        email = _normalize_email(command.email)
        user = self._users.get_by_email(email)
        if user is None or not user.is_active:
            raise InvalidCredentialsError

        password_hash = self._password_credentials.get_by_user_id(user.id)
        if password_hash is None:
            raise InvalidCredentialsError

        if not self._password_service.verify_password(command.password, password_hash):
            raise InvalidCredentialsError

        return LoginResult(
            user=user,
            access_token=self._token_service.issue_access_token(user.id),
        )


class InvalidCredentialsError(ValueError):
    """Raised when login credentials cannot authenticate a user."""
