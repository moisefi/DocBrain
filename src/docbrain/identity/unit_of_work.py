from collections.abc import Callable
from types import TracebackType

from sqlalchemy.orm import Session

from docbrain.identity.repositories import (
    SqlAlchemyPasswordCredentialRepository,
    SqlAlchemyUserRepository,
)
from docbrain.organizations.repositories import (
    SqlAlchemyMembershipRepository,
    SqlAlchemyOrganizationRepository,
)


class SqlAlchemyIdentityUnitOfWork:
    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    def __enter__(self) -> "SqlAlchemyIdentityUnitOfWork":
        self.session = self._session_factory()
        self.users = SqlAlchemyUserRepository(self.session)
        self.password_credentials = SqlAlchemyPasswordCredentialRepository(
            self.session,
        )
        self.organizations = SqlAlchemyOrganizationRepository(self.session)
        self.memberships = SqlAlchemyMembershipRepository(self.session)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type is None:
            self.session.commit()
        else:
            self.session.rollback()
        self.session.close()

