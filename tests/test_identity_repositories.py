from uuid import uuid4

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from docbrain.db.base import Base, import_all_models
from docbrain.identity.domain import User, UserId
from docbrain.identity.models import PasswordCredentialModel
from docbrain.identity.passwords import PasswordHash
from docbrain.identity.repositories import (
    SqlAlchemyPasswordCredentialRepository,
    SqlAlchemyUserRepository,
)


def test_user_repository_adds_and_gets_user_by_email() -> None:
    with _session() as session:
        repository = SqlAlchemyUserRepository(session)
        user = User(UserId(uuid4()), "sergio@example.com", "Sergio")

        repository.add(user)
        session.commit()

        assert repository.get_by_email("sergio@example.com") == user
        assert repository.get_by_email("missing@example.com") is None


def test_password_credential_repository_adds_hash() -> None:
    with _session() as session:
        user = User(UserId(uuid4()), "sergio@example.com", "Sergio")
        SqlAlchemyUserRepository(session).add(user)
        repository = SqlAlchemyPasswordCredentialRepository(session)

        repository.add(user.id, PasswordHash("$argon2id$hash"))
        session.commit()

        credential = session.scalar(select(PasswordCredentialModel))
        assert credential is not None
        assert credential.user_id == user.id.value
        assert credential.password_hash == "$argon2id$hash"


def _session() -> Session:
    import_all_models()
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Session(engine)

