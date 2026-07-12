from uuid import uuid4

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from docbrain.db.base import Base, import_all_models
from docbrain.identity.models import UserModel
from docbrain.identity.passwords import PasswordService
from docbrain.identity.unit_of_work import SqlAlchemyIdentityUnitOfWork
from docbrain.identity.use_cases import RegisterUserCommand, RegisterUserUseCase


def test_identity_unit_of_work_commits_registration() -> None:
    session_factory = _session_factory()

    with SqlAlchemyIdentityUnitOfWork(session_factory) as uow:
        use_case = RegisterUserUseCase(
            users=uow.users,
            password_credentials=uow.password_credentials,
            organizations=uow.organizations,
            memberships=uow.memberships,
            password_service=PasswordService(),
        )
        use_case.execute(
            RegisterUserCommand(
                email="sergio@example.com",
                password="correct horse battery staple",
                organization_name="Acme",
            ),
        )

    with session_factory() as session:
        assert session.scalar(select(UserModel.email)) == "sergio@example.com"


def test_identity_unit_of_work_rolls_back_on_error() -> None:
    session_factory = _session_factory()

    try:
        with SqlAlchemyIdentityUnitOfWork(session_factory) as uow:
            uow.session.add(
                UserModel(
                    id=uuid4(),
                    email="sergio@example.com",
                    display_name=None,
                    is_active=True,
                ),
            )
            raise RuntimeError
    except RuntimeError:
        pass

    with session_factory() as session:
        assert session.scalar(select(UserModel.email)) is None


def _session_factory() -> sessionmaker[Session]:
    import_all_models()
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
