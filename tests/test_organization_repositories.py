from uuid import uuid4

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from docbrain.db.base import Base, import_all_models
from docbrain.identity.domain import User, UserId
from docbrain.identity.repositories import SqlAlchemyUserRepository
from docbrain.organizations.domain import (
    Membership,
    Organization,
    OrganizationId,
    OrganizationRole,
)
from docbrain.organizations.models import MembershipModel, OrganizationModel
from docbrain.organizations.repositories import (
    SqlAlchemyMembershipRepository,
    SqlAlchemyOrganizationRepository,
    membership_from_model,
)


def test_organization_repository_adds_organization() -> None:
    with _session() as session:
        organization = Organization(OrganizationId(uuid4()), "Acme", "acme")
        SqlAlchemyOrganizationRepository(session).add(organization)
        session.commit()

        model = session.scalar(select(OrganizationModel))
        assert model is not None
        assert model.id == organization.id.value
        assert model.slug == "acme"


def test_membership_repository_adds_membership() -> None:
    with _session() as session:
        user = User(UserId(uuid4()), "sergio@example.com", "Sergio")
        organization = Organization(OrganizationId(uuid4()), "Acme", "acme")
        SqlAlchemyUserRepository(session).add(user)
        SqlAlchemyOrganizationRepository(session).add(organization)
        membership = Membership(
            user_id=user.id,
            organization_id=organization.id,
            role=OrganizationRole.OWNER,
        )

        SqlAlchemyMembershipRepository(session).add(membership)
        session.commit()

        model = session.scalar(select(MembershipModel))
        assert model is not None
        assert membership_from_model(model) == membership


def _session() -> Session:
    import_all_models()
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Session(engine)

