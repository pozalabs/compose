# 인증 가이드

SPA + 백엔드 아키텍처에서 compose auth 모듈을 사용한 인증 플로우 예시

## 플로우 개요

1. 프론트엔드가 OAuth provider(Google 등)로 리다이렉트
2. 사용자 인증 후 프론트엔드가 인가 코드를 수신
3. 프론트엔드가 인가 코드를 백엔드 API로 전달
4. 백엔드가 코드를 교환하여 provider 토큰을 획득 (`AuthorizationServer`)
5. 백엔드가 provider 토큰으로 사용자 정보를 조회 (`ResourceServer`)
6. 백엔드가 내부 JWT를 발급하여 프론트엔드에 반환 (`JWTIssuer`)
7. 이후 요청에서 JWT를 검증하여 사용자 식별 (`JWTDecoder`)

## 1. OAuth 토큰 교환 (AuthorizationServer)

`AuthorizationServer`는 OAuth2 인가 서버에 코드를 교환하는 클라이언트 역할

```python
import compose
from authlib.integrations.httpx_client import AsyncOAuth2Client


class GoogleAuthorizationServer(compose.auth.AuthorizationServer):
    async def revoke_token(self, token: str) -> None:
        async with self.auth_client_factory() as client:
            await client.revoke_token(
                url="https://oauth2.googleapis.com/revoke",
                headers=self.headers,
                token=token,
                token_type_hint="refresh_token",
            )


auth_server = GoogleAuthorizationServer(
    auth_client_factory=lambda: AsyncOAuth2Client(
        client_id="your-client-id",
        client_secret="your-client-secret",
    ),
    access_token_url="https://oauth2.googleapis.com/token",
)

# 인가 코드 → provider 토큰
grant = await auth_server.grant_authorization(redirect_uri="...", code="...")
# grant.access_token, grant.refresh_token
```

## 2. 사용자 정보 조회 (ResourceServer)

`ResourceServer`는 OAuth2 리소스 서버에서 보호된 자원을 가져오는 클라이언트 역할

```python
import httpx


class GoogleResourceServer(compose.auth.ResourceServer):
    def __init__(self, base_url: str, http_client_factory):
        self.base_url = base_url
        self.http_client_factory = http_client_factory

    def get_resource(self, access_token: str) -> compose.auth.UserResource:
        with self.http_client_factory(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {access_token}"},
        ) as client:
            response = client.get("/oauth2/v3/userinfo")
            response.raise_for_status()
            data = response.json()
            return compose.auth.UserResource(email=data["email"], name=data["name"])


resource_server = GoogleResourceServer(
    base_url="https://www.googleapis.com",
    http_client_factory=httpx.Client,
)

user_info = resource_server.get_resource(grant.access_token)
```

## 3. 내부 JWT 발급 (JWTIssuer)

사용자 확인 후 `JWTIssuer`로 서비스 자체 토큰 발급

```python
jwt_issuer = compose.auth.JWTIssuer.default(
    secret_key="your-secret-key",
    issuer="your-service",
)

access_token = jwt_issuer.issue(sub=str(user.id), expires_in=3600)
refresh_token = jwt_issuer.issue(sub=str(user.id), expires_in=86400 * 7)
```

커스텀 클레임이 필요하면 키워드 인자로 전달

```python
access_token = jwt_issuer.issue(sub=str(user.id), expires_in=3600, role="admin")
```

## 4. 토큰 검증 (JWTDecoder)

`JWTDecoder`로 토큰을 검증하고 `TokenClaims`에서 사용자 식별

```python
jwt_decoder = compose.auth.JWTDecoder.default(secret_key="your-secret-key")


def get_current_user(token: str) -> User:
    claims = jwt_decoder.decode(token)
    user = user_repository.find_by_id(claims.sub)
    if user is None:
        raise compose.exceptions.AuthorizationError()
    return user

# 커스텀 클레임 접근
role = claims.extra.get("role")
```

## 5. FastAPI 통합 예시

```python
from fastapi import Depends, Response
from fastapi.security import HTTPBearer

security = HTTPBearer()


@app.post("/auth/google/login")
async def login(code: str, redirect_uri: str, response: Response):
    # 1. 인가 코드 → provider 토큰
    grant = await auth_server.grant_authorization(redirect_uri=redirect_uri, code=code)

    # 2. provider 토큰 → 사용자 정보
    user_info = resource_server.get_resource(grant.access_token)

    # 3. 내부 사용자 조회/생성
    user = find_or_create_user(email=user_info.email, name=user_info.name)

    # 4. 내부 JWT 발급
    access_token = jwt_issuer.issue(sub=str(user.id), expires_in=3600)
    refresh_token = jwt_issuer.issue(sub=str(user.id), expires_in=86400 * 7)

    # 5. refresh token은 httpOnly 쿠키로 전달
    response.set_cookie(
        key="refresh_token", value=refresh_token,
        httponly=True, secure=True, samesite="none",
    )
    return {"access_token": access_token}


@app.get("/me")
async def me(credentials=Depends(security)):
    user = get_current_user(credentials.credentials)
    return {"user_id": str(user.id)}
```
