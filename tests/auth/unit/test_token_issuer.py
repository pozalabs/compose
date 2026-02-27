import compose

SECRET_KEY = "test-secret-key-for-jwt-operations"
ISSUER = "test-issuer"


def test_issue_and_decode_roundtrip():
    issuer = compose.auth.JWTIssuer.default(secret_key=SECRET_KEY, issuer=ISSUER)
    decoder = compose.auth.JWTDecoder.default(secret_key=SECRET_KEY)

    token = issuer.issue(sub="user-456", expires_in=3600, role="editor")
    result = decoder.decode(token)

    assert result == compose.auth.TokenClaims(
        sub="user-456",
        iss=ISSUER,
        jti=result.jti,
        iat=result.iat,
        exp=result.exp,
        extra={"role": "editor"},
    )
