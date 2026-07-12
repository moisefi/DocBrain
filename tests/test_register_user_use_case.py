from dataclasses import dataclass, field
from uuid import uuid4

import pytest

from docbrain.identity.domain import User, UserId
from docbrain.identity.passwords import PasswordHash, PasswordService
from docbrain.identity.use_cases import (
    EmailAlreadyRegisteredError,
    InvalidEmailError,
    InvalidOrganizationNameError,
    RegisterUserCommand,
    RegisterUserUseCase,
)
from docbrain.organizations.domain import Membership, Organization, OrganizationRole


def test_register_user_creates_owner_membership_and_password_credential() -> None:
    users = FakeUsers()
    password_credentials = FakePasswordCredentials()
    organizations = FakeOrganizations()
    memberships = FakeMemberships()
    use_case = RegisterUserUseCase(
        users=users,
        password_credentials=password_credentials,
        organizations=organizations,
        memberships=memberships,
        password_service=PasswordService(),
    )

    result = use_case.execute(
        RegisterUserCommand(
            email=" Sergio@example.COM ",
            password="correct horse battery staple",
            organization_name="Acme Operations",
            display_name="Sergio",
        ),
    )

    assert result.user.email == "sergio@example.com"
    assert result.organization.slug == "acme-operations"
    assert result.membership.role == OrganizationRole.OWNER
    assert users.items == [result.user]
    assert organizations.items == [result.organization]
    assert memberships.items == [result.membership]
    assert password_credentials.items[0].user_id == result.user.id
    assert password_credentials.items[0].password_hash.value.startswith("$argon2")


def test_register_user_rejects_duplicate_email() -> None:
    users = FakeUsers(items=[User(UserId(uuid4()), "a@b.com", None)])
    use_case = RegisterUserUseCase(
        users=users,
        password_credentials=FakePasswordCredentials(),
        organizations=FakeOrganizations(),
        memberships=FakeMemberships(),
        password_service=PasswordService(),
    )

    with pytest.raises(EmailAlreadyRegisteredError):
        use_case.execute(
            RegisterUserCommand(
                email="A@B.COM",
                password="correct horse battery staple",
                organization_name="Acme",
            ),
        )


def test_register_user_rejects_invalid_email() -> None:
    use_case = _use_case()

    with pytest.raises(InvalidEmailError):
        use_case.execute(
            RegisterUserCommand(
                email="not-an-email",
                password="correct horse battery staple",
                organization_name="Acme",
            ),
        )


def test_register_user_rejects_blank_organization_name() -> None:
    use_case = _use_case()

    with pytest.raises(InvalidOrganizationNameError):
        use_case.execute(
            RegisterUserCommand(
                email="a@b.com",
                password="correct horse battery staple",
                organization_name=" ",
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
class FakePasswordCredential:
    user_id: UserId
    password_hash: PasswordHash


@dataclass
class FakePasswordCredentials:
    items: list[FakePasswordCredential] = field(default_factory=list)

    def add(self, user_id: UserId, password_hash: PasswordHash) -> None:
        self.items.append(FakePasswordCredential(user_id, password_hash))


@dataclass
class FakeOrganizations:
    items: list[Organization] = field(default_factory=list)

    def add(self, organization: Organization) -> None:
        self.items.append(organization)


@dataclass
class FakeMemberships:
    items: list[Membership] = field(default_factory=list)

    def add(self, membership: Membership) -> None:
        self.items.append(membership)


def _use_case() -> RegisterUserUseCase:
    return RegisterUserUseCase(
        users=FakeUsers(),
        password_credentials=FakePasswordCredentials(),
        organizations=FakeOrganizations(),
        memberships=FakeMemberships(),
        password_service=PasswordService(),
    )
