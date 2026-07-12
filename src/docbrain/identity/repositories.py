from sqlalchemy import select
from sqlalchemy.orm import Session

from docbrain.identity.domain import User, UserId
from docbrain.identity.models import PasswordCredentialModel, UserModel
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


def _user_from_model(model: UserModel) -> User:
    return User(
        id=UserId(model.id),
        email=model.email,
        display_name=model.display_name,
        is_active=model.is_active,
    )
