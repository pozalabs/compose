# 인증 가이드

authlib OAuth 클라이언트와 compose JWT를 조합한 인증 플로우 예시

## 구성 요소

- authlib: OAuth 2.0 클라이언트 (인가 코드 교환, 사용자 정보 획득)
- compose `JWTIssuer`: 내부 access/refresh 토큰 발급
- compose `JWTDecoder`: 토큰 검증 및 클레임 추출

## 1. authlib OAuth 클라이언트 설정

Google OAuth를 예시로 사용. authlib의 `AsyncOAuth2Client`로 인가 코드를 교환하고 사용자 정보를 획득

```python
from authlib.integrations.httpx_client import AsyncOAuth2Client
import httpx

GOOGLE_AUTH_URL = "https://oauth2.googleapis.com"
GOOGLE_API_URL = "https://www.googleapis.com"


async def exchange_authorization_code(
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    code: str,
) -> dict:
    """인가 코드를 교환하여 Google 토큰을 획득"""
    async with AsyncOAuth2Client(
        client_id=client_id, client_secret=client_secret
    ) as client:
        token = await client.fetch_token(
            url=f"{GOOGLE_AUTH_URL}/token",
            grant_type="authorization_code",
            redirect_uri=redirect_uri,
            code=code,
        )
    return token


def get_user_info(access_token: str) -> dict:
    """Google access token으로 사용자 정보 조회"""
    with httpx.Client(
        base_url=GOOGLE_API_URL,
        headers={"Authorization": f"Bearer {access_token}"},
    ) as client:
        response = client.get("/oauth2/v3/userinfo")
        response.raise_for_status()
        return response.json()
```

## 2. 내부 JWT 토큰 발급

사용자 확인 후 compose `JWTIssuer`로 서비스 자체 토큰 발급

```python
import compose

jwt_issuer = compose.auth.JWTIssuer.default(
    secret_key="your-secret-key",
    issuer="your-service",
)


def issue_token_pair(user_id: str) -> tuple[str, str]:
    access_token = jwt_issuer.issue(sub=user_id, expires_in=3600)
    refresh_token = jwt_issuer.issue(sub=user_id, expires_in=86400 * 7)
    return access_token, refresh_token
```

커스텀 클레임이 필요하면 `issue()`에 키워드 인자로 전달

```python
access_token = jwt_issuer.issue(sub=user_id, expires_in=3600, role="admin")
```

## 3. 토큰 검증 및 현재 사용자 조회

`JWTDecoder`로 토큰을 검증하고 `TokenClaims`에서 사용자 식별

```python
jwt_decoder = compose.auth.JWTDecoder.default(secret_key="your-secret-key")


def get_current_user(token: str) -> User:
    claims = jwt_decoder.decode(token)
    user = user_repository.find_by_id(claims.sub)
    if user is None:
        raise compose.exceptions.AuthorizationError()
    return user
```

`TokenClaims.extra`로 커스텀 클레임에 접근

```python
claims = jwt_decoder.decode(token)
role = claims.extra.get("role")
```

## 4. FastAPI 통합 예시

```python
from fastapi import Depends, Response
from fastapi.security import HTTPBearer

security = HTTPBearer()


async def login(code: str, redirect_uri: str, response: Response):
    # 1. authlib으로 인가 코드 교환
    google_token = await exchange_authorization_code(
        client_id="...", client_secret="...",
        redirect_uri=redirect_uri, code=code,
    )

    # 2. 사용자 정보 획득
    user_info = get_user_info(google_token["access_token"])

    # 3. 내부 사용자 조회/생성
    user = find_or_create_user(email=user_info["email"], name=user_info["name"])

    # 4. 내부 JWT 발급
    access_token, refresh_token = issue_token_pair(str(user.id))

    # 5. refresh token은 httpOnly 쿠키로 전달
    response.set_cookie(
        key="refresh_token", value=refresh_token,
        httponly=True, secure=True, samesite="none",
    )
    return {"access_token": access_token}


async def protected_endpoint(credentials=Depends(security)):
    user = get_current_user(credentials.credentials)
    return {"user_id": user.id}
```
