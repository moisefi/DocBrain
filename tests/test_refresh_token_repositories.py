from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from docbrain.db.base import Base, import_all_models
from docbrain.identity.domain import User, UserId
from docbrain.identity.repositories import (
    SqlAlchemyRefreshTokenRepository,
    SqlAlchemyUserRepository,
)


def test_refresh_token_repository_adds_and_gets_token_by_hash() -> None:
    with _session() as session:
        user = User(UserId(uuid4()), "sergio@example.com", "Sergio")
        SqlAlchemyUserRepository(session).add(user)
        repository = SqlAlchemyRefreshTokenRepository(session)
        family_id = uuid4()
        token_id = uuid4()

        repository.add_family(family_id, user.id)
        repository.add_token(
            token_id=token_id,
            family_id=family_id,
            user_id=user.id,
            token_hash="abc123",
            expires_at=datetime.now(UTC) + timedelta(days=30),
        )
        session.commit()

        token = repository.get_by_hash("abc123")
        assert token is not None
        assert token.id == token_id
        assert token.family_id == family_id
        assert token.user_id == user.id.value


def test_refresh_token_repository_marks_token_used_and_revokes_family() -> None:
    with _session() as session:
        user = User(UserId(uuid4()), "sergio@example.com", "Sergio")
        SqlAlchemyUserRepository(session).add(user)
        repository = SqlAlchemyRefreshTokenRepository(session)
        family_id = uuid4()
        token_id = uuid4()
        replacement_id = uuid4()
        repository.add_family(family_id, user.id)
        repository.add_token(
            token_id=token_id,
            family_id=family_id,
            user_id=user.id,
            token_hash="abc123",
            expires_at=datetime.now(UTC) + timedelta(days=30),
        )
        session.commit()

        repository.mark_used(token_id, replacement_id)
        repository.revoke_family(family_id)
        session.commit()

        token = repository.get_by_hash("abc123")
        assert token is not None
        assert token.used_at is not None
        assert token.replaced_by_token_id == replacement_id


def _session() -> Session:
    import_all_models()
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Session(engine)

