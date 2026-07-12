from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from docbrain.identity.domain import UserId


class OrganizationRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

    def can_manage_members(self) -> bool:
        return self in {self.OWNER, self.ADMIN}

    def can_manage_documents(self) -> bool:
        return self in {self.OWNER, self.ADMIN, self.EDITOR}

    def can_query_knowledge(self) -> bool:
        return self in {self.OWNER, self.ADMIN, self.EDITOR, self.VIEWER}


@dataclass(frozen=True, slots=True)
class OrganizationId:
    value: UUID


@dataclass(frozen=True, slots=True)
class Organization:
    id: OrganizationId
    name: str
    slug: str
    is_active: bool = True


@dataclass(frozen=True, slots=True)
class Membership:
    user_id: UserId
    organization_id: OrganizationId
    role: OrganizationRole
    is_active: bool = True

    def require_active(self) -> None:
        if not self.is_active:
            raise InactiveMembershipError


@dataclass(frozen=True, slots=True)
class TenantContext:
    user_id: UserId
    organization_id: OrganizationId
    role: OrganizationRole
    correlation_id: str

    @classmethod
    def from_membership(
        cls,
        membership: Membership,
        *,
        correlation_id: str,
    ) -> "TenantContext":
        membership.require_active()
        return cls(
            user_id=membership.user_id,
            organization_id=membership.organization_id,
            role=membership.role,
            correlation_id=correlation_id,
        )

    def require_member_management(self) -> None:
        if not self.role.can_manage_members():
            raise PermissionDeniedError("member_management")

    def require_document_management(self) -> None:
        if not self.role.can_manage_documents():
            raise PermissionDeniedError("document_management")

    def require_knowledge_query(self) -> None:
        if not self.role.can_query_knowledge():
            raise PermissionDeniedError("knowledge_query")


class TenancyError(Exception):
    """Base error for tenancy domain rules."""


class InactiveMembershipError(TenancyError):
    """Raised when a membership exists but cannot be used."""


class PermissionDeniedError(TenancyError):
    def __init__(self, permission: str) -> None:
        super().__init__(f"Permission denied: {permission}")
        self.permission = permission
