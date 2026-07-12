from uuid import uuid4

import pytest

from docbrain.identity.domain import UserId
from docbrain.organizations.domain import (
    InactiveMembershipError,
    Membership,
    OrganizationId,
    OrganizationRole,
    PermissionDeniedError,
    TenantContext,
)


def test_tenant_context_requires_active_membership() -> None:
    membership = Membership(
        user_id=UserId(uuid4()),
        organization_id=OrganizationId(uuid4()),
        role=OrganizationRole.VIEWER,
        is_active=False,
    )

    with pytest.raises(InactiveMembershipError):
        TenantContext.from_membership(membership, correlation_id="request-1")


@pytest.mark.parametrize(
    "role",
    [OrganizationRole.OWNER, OrganizationRole.ADMIN],
)
def test_owner_and_admin_can_manage_members(role: OrganizationRole) -> None:
    context = _tenant_context(role)

    context.require_member_management()


@pytest.mark.parametrize(
    "role",
    [OrganizationRole.EDITOR, OrganizationRole.VIEWER],
)
def test_editor_and_viewer_cannot_manage_members(role: OrganizationRole) -> None:
    context = _tenant_context(role)

    with pytest.raises(PermissionDeniedError) as exc_info:
        context.require_member_management()

    assert exc_info.value.permission == "member_management"


@pytest.mark.parametrize(
    "role",
    [OrganizationRole.OWNER, OrganizationRole.ADMIN, OrganizationRole.EDITOR],
)
def test_owner_admin_and_editor_can_manage_documents(role: OrganizationRole) -> None:
    context = _tenant_context(role)

    context.require_document_management()


def test_viewer_can_query_knowledge() -> None:
    context = _tenant_context(OrganizationRole.VIEWER)

    context.require_knowledge_query()


def _tenant_context(role: OrganizationRole) -> TenantContext:
    return TenantContext(
        user_id=UserId(uuid4()),
        organization_id=OrganizationId(uuid4()),
        role=role,
        correlation_id="request-1",
    )

