# 인증 가이드

authlib Starlette OAuth 미들웨어와 compose JWT를 조합한 인증 플로우 예시

## 구성 요소

- authlib Starlette 통합: OAuth 2.0 / OpenID Connect 클라이언트 (인가 리다이렉트, 토큰 교환, 사용자 정보 획득)
- compose `JWTIssuer`: 내부 access/refresh 토큰 발급
- compose `JWTDecoder`: 토큰 검증 및 클레임 추출

## 1. authlib OAuth 클라이언트 설정

Google OAuth를 예시로 사용. authlib의 Starlette 통합 OAuth 클라이언트를 등록하고 `SessionMiddleware`를 추가

```python
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware

from fastapi import FastAPI

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="session-secret")

oauth = OAuth()
oauth.register(
    name="google",
    client_id="your-client-id",
    client_secret="your-client-secret",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)
```

`server_metadata_url`을 지정하면 authorize/token/userinfo 엔드포인트가 자동 설정됨

## 2. OAuth 인가 플로우

authlib 미들웨어가 인가 리다이렉트와 토큰 교환을 처리

```python
from fastapi import Request

@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get("/auth/callback")
async def auth_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    userinfo = token["userinfo"]  # OpenID Connect: id_token에서 자동 파싱
    # userinfo = {"sub": "...", "email": "...", "name": "...", ...}
    return userinfo
```

## 3. 내부 JWT 토큰 발급

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

## 4. 토큰 검증 및 현재 사용자 조회

`JWTDecoder`로 토큰을 검증하고 `TokenClaims`에서 사용자 식별

```python
jwt_decoder = compose.auth.JWTDecoder.default(secret_key="your-secret-key")


def get_current_user(token: str) -> User:
    claims = jwt_decoder.decode(token)
    if (user := user_repository.find_by_id(claims.sub)) is None:
        raise compose.exceptions.AuthorizationError()
    return user
```

`TokenClaims.extra`로 커스텀 클레임에 접근

```python
claims = jwt_decoder.decode(token)
role = claims.extra.get("role")
```

## 5. 전체 통합 예시

```python
from fastapi import Depends, Request, Response
from fastapi.security import HTTPBearer

security = HTTPBearer()


@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get("/auth/callback")
async def auth_callback(request: Request, response: Response):
    # 1. authlib이 인가 코드 교환 + 사용자 정보 획득을 처리
    token = await oauth.google.authorize_access_token(request)
    userinfo = token["userinfo"]

    # 2. 내부 사용자 조회/생성
    user = find_or_create_user(email=userinfo["email"], name=userinfo["name"])

    # 3. 내부 JWT 발급
    access_token, refresh_token = issue_token_pair(str(user.id))

    # 4. refresh token은 httpOnly 쿠키로 전달
    response.set_cookie(
        key="refresh_token", value=refresh_token,
        httponly=True, secure=True, samesite="none",
    )
    return {"access_token": access_token}


@app.get("/me")
async def me(credentials=Depends(security)):
    user = get_current_user(credentials.credentials)
    return {"user_id": user.id}
```
