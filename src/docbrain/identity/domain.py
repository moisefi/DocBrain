from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class UserId:
    value: UUID


@dataclass(frozen=True, slots=True)
class User:
    id: UserId
    email: str
    display_name: str | None
    is_active: bool = True
