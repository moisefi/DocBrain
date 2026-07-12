from uuid import uuid4

import pytest

from docbrain.core.config import Settings
from docbrain.identity.domain import UserId
from docbrain.identity.tokens import JwtTokenService, TokenVerificationError


def test_jwt_token_service_issues_and_verifies_access_token() -> None:
    settings = Settings(
        jwt_secret="test-secret-with-enough-length-32b",
        jwt_issuer="docbrain-test",
    )
    service = JwtTokenService(settings)
    user_id = UserId(uuid4())

    token = service.issue_access_token(user_id)
    claims = service.verify_access_token(token.value)

    assert token.value
    assert claims.subject == user_id
    assert claims.issuer == "docbrain-test"
    assert claims.expires_at > claims.issued_at


def test_jwt_token_service_rejects_token_signed_with_another_secret() -> None:
    user_id = UserId(uuid4())
    issuer = JwtTokenService(
        Settings(jwt_secret="issuer-secret-with-enough-length-32b"),
    )
    verifier = JwtTokenService(
        Settings(jwt_secret="verifier-secret-with-enough-length-32b"),
    )

    token = issuer.issue_access_token(user_id)

    with pytest.raises(TokenVerificationError):
        verifier.verify_access_token(token.value)
