from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from docbrain.identity.domain import User, UserId
from docbrain.identity.models import (
    PasswordCredentialModel,
    RefreshTokenFamilyModel,
    RefreshTokenModel,
    UserModel,
)
from docbrain.identity.passwords import PasswordHash


class SqlAlchemyUserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_email(self, email: str) -> User | None:
        model = self._session.scalar(
            select(UserModel).where(UserModel.email == email),
        )
        if model is None:
            return None
        return _user_from_model(model)

    def get_by_id(self, user_id: UserId) -> User | None:
        model = self._session.get(UserModel, user_id.value)
        if model is None:
            return None
        return _user_from_model(model)

    def add(self, user: User) -> None:
        self._session.add(
            UserModel(
                id=user.id.value,
                email=user.email,
                display_name=user.display_name,
                is_active=user.is_active,
            ),
        )


class SqlAlchemyPasswordCredentialRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, user_id: UserId, password_hash: PasswordHash) -> None:
        self._session.add(
            PasswordCredentialModel(
                user_id=user_id.value,
                password_hash=password_hash.value,
            ),
        )

    def get_by_user_id(self, user_id: UserId) -> PasswordHash | None:
        model = self._session.get(PasswordCredentialModel, user_id.value)
        if model is None:
            return None
        return PasswordHash(model.password_hash)


class SqlAlchemyRefreshTokenRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add_family(self, family_id: UUID, user_id: UserId) -> None:
        self._session.add(
            RefreshTokenFamilyModel(
                id=family_id,
                user_id=user_id.value,
            ),
        )

    def add_token(
        self,
        *,
        token_id: UUID,
        family_id: UUID,
        user_id: UserId,
        token_hash: str,
        expires_at: datetime,
    ) -> None:
        self._session.add(
            RefreshTokenModel(
                id=token_id,
                family_id=family_id,
                user_id=user_id.value,
                token_hash=token_hash,
                expires_at=expires_at,
            ),
        )

    def get_by_hash(self, token_hash: str) -> RefreshTokenModel | None:
        return self._session.scalar(
            select(RefreshTokenModel).where(RefreshTokenModel.token_hash == token_hash),
        )

    def mark_used(self, token_id: UUID, replaced_by_token_id: UUID) -> None:
        model = self._session.get(RefreshTokenModel, token_id)
        if model is None:
            return
        model.used_at = datetime.now(UTC)
        model.replaced_by_token_id = replaced_by_token_id

    def revoke_token(self, token_id: UUID) -> None:
        model = self._session.get(RefreshTokenModel, token_id)
        if model is not None:
            model.revoked_at = datetime.now(UTC)

    def revoke_family(self, family_id: UUID) -> None:
        family = self._session.get(RefreshTokenFamilyModel, family_id)
        if family is not None:
            family.revoked_at = datetime.now(UTC)


def _user_from_model(model: UserModel) -> User:
    return User(
        id=UserId(model.id),
        email=model.email,
        display_name=model.display_name,
        is_active=model.is_active,
    )
