from uuid import uuid4

from sqlalchemy.orm import Session

from docbrain.identity.domain import UserId
from docbrain.organizations.domain import (
    Membership,
    Organization,
    OrganizationId,
    OrganizationRole,
)
from docbrain.organizations.models import MembershipModel, OrganizationModel


class SqlAlchemyOrganizationRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, organization: Organization) -> None:
        self._session.add(
            OrganizationModel(
                id=organization.id.value,
                name=organization.name,
                slug=organization.slug,
                is_active=organization.is_active,
            ),
        )


class SqlAlchemyMembershipRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, membership: Membership) -> None:
        self._session.add(
            MembershipModel(
                id=uuid4(),
                user_id=membership.user_id.value,
                organization_id=membership.organization_id.value,
                role=membership.role.value,
                is_active=membership.is_active,
            ),
        )


def membership_from_model(model: MembershipModel) -> Membership:
    return Membership(
        user_id=UserId(model.user_id),
        organization_id=OrganizationId(model.organization_id),
        role=OrganizationRole(model.role),
        is_active=model.is_active,
    )
