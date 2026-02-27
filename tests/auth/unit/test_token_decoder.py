import pendulum
import pytest

import compose
from compose import exceptions

SECRET_KEY = "test-secret-key-for-jwt-operations"
ISSUER = "test-issuer"


@pytest.fixture
def issuer() -> compose.auth.JWTIssuer:
    return compose.auth.JWTIssuer.default(secret_key=SECRET_KEY, issuer=ISSUER)


@pytest.fixture
def decoder() -> compose.auth.JWTDecoder:
    return compose.auth.JWTDecoder(secret_key=SECRET_KEY, clock=pendulum.DateTime)


def test_decode_return_token_claims(
    issuer: compose.auth.JWTIssuer, decoder: compose.auth.JWTDecoder
):
    token = issuer.issue(sub="user-123", expires_in=3600)

    result = decoder.decode(token)

    assert isinstance(result, compose.auth.TokenClaims)
    assert result.sub == "user-123"
    assert result.iss == ISSUER


def test_decode_collect_extra_claims(
    issuer: compose.auth.JWTIssuer, decoder: compose.auth.JWTDecoder
):
    token = issuer.issue(sub="user-123", expires_in=3600, role="admin", org_id="org-1")

    result = decoder.decode(token)

    assert result.extra == {"role": "admin", "org_id": "org-1"}


def test_default_create_working_decoder(issuer: compose.auth.JWTIssuer):
    decoder = compose.auth.JWTDecoder.default(secret_key=SECRET_KEY)
    token = issuer.issue(sub="user-123", expires_in=3600)

    result = decoder.decode(token)

    assert result.sub == "user-123"


def test_cannot_decode_invalid_token(decoder: compose.auth.JWTDecoder):
    with pytest.raises(exceptions.AuthorizationError, match="Invalid token"):
        decoder.decode("invalid-token")


def test_cannot_decode_wrong_secret(issuer: compose.auth.JWTIssuer):
    decoder = compose.auth.JWTDecoder(secret_key="wrong-secret", clock=pendulum.DateTime)
    token = issuer.issue(sub="user-123", expires_in=3600)

    with pytest.raises(exceptions.AuthorizationError, match="Invalid token"):
        decoder.decode(token)


def test_cannot_decode_expired_token(
    issuer: compose.auth.JWTIssuer, decoder: compose.auth.JWTDecoder
):
    token = issuer.issue(sub="user-123", expires_in=-1)

    with pytest.raises(exceptions.AuthorizationError, match="Token has expired"):
        decoder.decode(token)
