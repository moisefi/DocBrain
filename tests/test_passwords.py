import pytest

from docbrain.identity.passwords import (
    PasswordHash,
    PasswordService,
    WeakPasswordError,
)


def test_password_service_hashes_and_verifies_password() -> None:
    service = PasswordService()

    password_hash = service.hash_password("correct horse battery staple")

    assert password_hash.value.startswith("$argon2")
    assert service.verify_password("correct horse battery staple", password_hash)


def test_password_service_rejects_wrong_password() -> None:
    service = PasswordService()
    password_hash = service.hash_password("correct horse battery staple")

    assert not service.verify_password("wrong horse battery staple", password_hash)


def test_password_service_rejects_weak_password() -> None:
    service = PasswordService()

    with pytest.raises(WeakPasswordError):
        service.hash_password("too-short")


def test_password_service_can_detect_hash_rehash_requirement() -> None:
    service = PasswordService()
    password_hash = PasswordHash(
        "$argon2id$v=19$m=8,t=1,p=1$MTIzNDU2Nzg$"
        "O9VIJMKZ1Eu56vS2kD5L8sTRPeQRi6XvE2xqis3uGzY",
    )

    assert service.needs_rehash(password_hash)

