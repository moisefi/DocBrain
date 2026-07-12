from dataclasses import dataclass

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


@dataclass(frozen=True, slots=True)
class PasswordHash:
    value: str


class PasswordService:
    def __init__(self, hasher: PasswordHasher | None = None) -> None:
        self._hasher = hasher or PasswordHasher(
            time_cost=3,
            memory_cost=65536,
            parallelism=4,
            hash_len=32,
            salt_len=16,
        )

    def hash_password(self, plain_password: str) -> PasswordHash:
        _validate_plain_password(plain_password)
        return PasswordHash(self._hasher.hash(plain_password))

    def verify_password(
        self,
        plain_password: str,
        password_hash: PasswordHash,
    ) -> bool:
        try:
            return self._hasher.verify(password_hash.value, plain_password)
        except VerifyMismatchError:
            return False

    def needs_rehash(self, password_hash: PasswordHash) -> bool:
        return self._hasher.check_needs_rehash(password_hash.value)


def _validate_plain_password(plain_password: str) -> None:
    if len(plain_password) < 12:
        raise WeakPasswordError("Password must contain at least 12 characters")


class WeakPasswordError(ValueError):
    """Raised when a password does not satisfy local password policy."""

